from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import sessionmaker
import streamlink
from streamlink.session import Streamlink
from streamlink.options import Options
from streamlink.exceptions import (StreamlinkError, PluginError, FatalPluginError, NoPluginError, NoStreamsError, StreamError)
from uuid import uuid4
import re
import os
from pathlib import Path
from datetime import datetime
import logging
import shutil
from dotenv import load_dotenv
from datetime import timedelta


# Import my functions
from download_task_model import download_task
from db_schema import init_db, DownloadTask, remove_db, get_running_stream_ids
from get_twitch_api import get_access_token, get_user


# Arrays to store jobs
running_streams = {}
scheduled_streams = []
scheduled_tasks = {} 

# Load environment variables from .env file
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# Logging configuration
Path('./logs').mkdir(exist_ok=True)
logging_filename=f'./logs/application-{datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.log'
logging.basicConfig(
    filename=logging_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def calculate_running_since(start_time):
    now = datetime.now()
    running_since = now - start_time
    total_minutes = running_since.total_seconds() / 60
    return total_minutes


async def run_streamlink_session_in_thread(download_task, filename, url, time):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        try:
            logging.info(f"Starting streamlink session for {download_task.name} in a separate thread.")
            # Execute in a separate thread
            await loop.run_in_executor(executor, lambda: asyncio.run(streamlink_session(download_task.name, url, download_task.quality, time, download_task.output_dir, download_task.block_ads, filename, download_task.stream_id)))
            logging.info(f"Streamlink session for {download_task.name} completed successfully.")
        except KeyError as e:
            logging.error(f"KeyError when accessing running_streams: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during streamlink session for {download_task.name}: {e}")

async def streamlink_session(name, url, quality, time, output_dir, block_ads, filename, stream_id):    
    try: 
        session = Streamlink()
        if "twitch.tv" in url:
        # Define Options if a Twitch URL is provided.
            options = Options()
            options.set("disable_ads", block_ads)
            streams = session.streams(url, options)
            session.set_option("stream-timeout", 30)
        else:
            session.set_option("stream-timeout", 30)
            streams = session.streams(url)

        output_dir = Path(output_dir)
        Path(output_dir).mkdir(exist_ok=True)
        filename = filename.replace(":", "-")
        output_file = output_dir / filename

        # Create individual logger for each download task
        task_logger = logging.getLogger(f"download_{stream_id}")
        task_log_file = f"./logs/{filename.replace('.mp4', '.txt').replace('.mp3', '.txt').replace(':', '-')}"
        task_handler = logging.FileHandler(task_log_file)
        task_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        task_handler.setFormatter(task_formatter)
        task_logger.addHandler(task_handler)
        task_logger.setLevel(logging.DEBUG)

        task_logger.info(f"Starting download for {name}")
        task_logger.info(f"Saving stream to {output_file}")

        # Start download
        with open(output_file, "wb") as f:
            fd = streams[quality].open()
            running_streams[stream_id] = fd 
            try:
                while True:
                    data = fd.read(1024)
                    if not data:
                        break
                    f.write(data)
            finally:
                fd.close()

                # Update task in DB 
                engine, _, Session = init_db()
                session = Session()
                try:
                    # Search task in db
                    download_task = session.query(DownloadTask).filter_by(stream_id=stream_id).first()
                    if download_task:
                        # Update the task in DB with total_time and running=false
                        download_task.running = False
                        download_task.total_time = (datetime.now() - download_task.time).total_seconds()
                        session.commit()
                        task_logger.info(f"Stream ended or network error {stream_id}")
                    else:
                        task_logger.error(f"Stream-ID {stream_id} not found in running_streams.")
                finally:
                    session.close()
                    if stream_id in running_streams:
                        del running_streams[stream_id]
                    else:
                        task_logger.error(f"Stream-ID {stream_id} not found in running_streams.")
    except NoPluginError:
        print("No suitable plugin found for the provided URL.")
    except NoStreamsError:
        print("No streams available for this URL.")
    except PluginError as e:
        print(f"Plugin error: {e}")
    except FatalPluginError as e:
        print(f"Fatal plugin error: {e}")
    except StreamError as e:
        print(f"Stream error: {e}")
    except StreamlinkError as e:
        print(f"General Streamlink error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return session

async def check_live_status_periodically(username, schedule_interval, schedule_end, download_task, filename, url, time):
    if isinstance(schedule_end, str):
        schedule_end = datetime.fromisoformat(schedule_end)

    while datetime.now() < schedule_end:
        logging.info(f"Checking live status for username: {username}")
        live_status = await get_live_status(username)
        if live_status["live_status"] == "live":
            logging.info(f"User {username} is live with stream data: {live_status['stream_data']}")
            # Remove the task from scheduled_streams list
            if download_task.stream_id in scheduled_streams:
                scheduled_streams.remove(download_task.stream_id)
            # Start streamlink session in separate thread
            asyncio.create_task(run_streamlink_session_in_thread(download_task, filename, url, time))
            return
        await asyncio.sleep(schedule_interval * 60) 
    logging.info(f"Schedule end time reached for username: {username}. Stopping live status checks.")
    # Remove the stream_id from the scheduled_streams list
    if download_task.stream_id in scheduled_streams:
        scheduled_streams.remove(download_task.stream_id)

app = FastAPI()

# Mount static frontend files
app.mount("/dist", StaticFiles(directory="../../frontend/src/dist", html=True), name="static")

# CORS-Configuration
origins = ["http://localhost:8080/", "http://localhost:8080", "http://localhost/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Route / to /dist
@app.get("/")
async def root():
    return RedirectResponse(url="/dist")


@app.post("/api/v1/start/")
async def create_stream(download_task: download_task):
    logging.info(f"Start creating stream for {download_task.name}")

    if download_task.append_time:
        time_str = datetime.now().strftime(download_task.time_format)
        time = datetime.strptime(time_str, download_task.time_format)
        logging.info(f"Appending time to filename using format {download_task.time_format}: {time_str}")
    else:
        time = ""
        logging.info("No time appending requested.")

    extension = ".mp3" if download_task.quality == "audio_only" else ".mp4"
    logging.info(f"Selected file extension based on quality {download_task.quality}: {extension}")

    filename = f"{download_task.name}__{time}{extension}"
    url = f"{download_task.base_dl_url}{download_task.name}"
    logging.info(f"Constructed filename: {filename} and URL: {url}")

    download_task.stream_id = str(uuid4())
    logging.info(f"Generated stream ID: {download_task.stream_id}")

    # Create DB session
    engine, Base, Session = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    logging.info("Database session initialized.")

    # Add task to DB
    schedule_end_time = datetime.now() + timedelta(hours=download_task.schedule_end)
    download_task_instance = DownloadTask(
        stream_id=f"{download_task.stream_id}",
        name=f"{download_task.name}",
        base_dl_url=f"{download_task.base_dl_url}",
        block_ads=download_task.block_ads,
        append_time=download_task.append_time,
        time_format=f"{download_task.time_format}",
        time=time,
        quality=f"{download_task.quality}",
        output_dir=f"{download_task.output_dir}",
        url=f"{url}",
        filename=f"{filename}",
        running=True,
        schedule=download_task.schedule,
        schedule_interval=download_task.schedule_interval,
        schedule_end=schedule_end_time  
    )
    session.add(download_task_instance)
    session.commit()

    # extract neccessary information from the download_task_instance
    schedule_interval = download_task_instance.schedule_interval
    schedule_end = download_task_instance.schedule_end

    session.close()
    logging.info(f"Download task for {download_task.name} added to database.")

    if download_task.schedule:
        logging.info(f"Stream {download_task.name} scheduled with interval {schedule_interval} minutes and end time {schedule_end}.")
        # Add the stream_id to the scheduled_streams list
        scheduled_streams.append(download_task.stream_id)
        # Start background process and check live status periodically
        task = asyncio.create_task(check_live_status_periodically(download_task.name, schedule_interval, schedule_end, download_task, filename, url, time))
        scheduled_tasks[download_task.stream_id] = task
    else:
        # Start streamlink session in separate thread
        asyncio.create_task(run_streamlink_session_in_thread(download_task, filename, url, time))
        logging.info(f"Streamlink session initiated for {download_task.name}.")

    logging.info(f"Stream creation completed for {download_task.name} with ID {download_task.stream_id}.")
    return {
        "stream_id": download_task.stream_id,
        "message": "Stream request created with the following parameters:",
        "name": download_task.name,
        "quality": download_task.quality,
        "block_ads": download_task.block_ads,
        "time": time,
        "full_url": f"{download_task.base_dl_url}{download_task.name}",
        "path": f"{download_task.output_dir}/{filename}",
        "schedule": download_task.schedule,
    }


@app.post("/api/v1/stop_all/")
async def stop_all_streams():
    # Stop all running streams
    logging.info("Stopping all streams...")
    stopped_streams = []
    running_stream_ids = await get_running_stream_ids()
    # Stop all running streams
    for stream_id in running_stream_ids:
        try:
            await stop_stream(stream_id)
            stopped_streams.append(stream_id)
        except HTTPException as e:
            logging.error(f"Error stopping stream {stream_id}: {e.detail}")
    logging.info("All streams have been successfully stopped.")
    return {"message": "All streams have been stopped.", "stopped_streams": stopped_streams}



@app.post("/api/v1/stop/")
async def stop_stream(stream_id: str):
    # Check and stop a scheduled stream
    if stream_id in scheduled_streams:
        logging.info(f"Stopping scheduled stream {stream_id}")
        scheduled_streams.remove(stream_id)
        # Cancel the scheduled task
        task = scheduled_tasks.pop(stream_id, None)
        if task:
            task.cancel()
            logging.info(f"Scheduled stream {stream_id} successfully stopped.")
        return {"message": f"Scheduled stream {stream_id} has been stopped."}

    # Stop a running job
    logging.info(f"Stopping stream {stream_id}")
    stream_fd = running_streams.get(stream_id)
    if stream_fd:
        stream_fd.close()
        logging.info(f"Stream {stream_id} successfully stopped.")
        del running_streams[stream_id]
        return {"message": f"Stream {stream_id} has been stopped."}
    else:
        logging.error(f"Stream {stream_id} not found.")
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found.")


@app.get("/api/v1/cleanup/")
async def cleanup_db():
    logging.info("Cleaning up...")
    try:
        # Attempt to remove the database
        result = remove_db()
        logging.info("Database successfully cleaned up.")
    except Exception as e:
        logging.error(f"Error when deleting the database: {e}")
        result = False
    try:
        # Try to remove old log files
        for log_file in Path("./logs/").glob("*"):
            if log_file.name != Path(logging_filename).name:
                try:
                    log_file.unlink()
                except Exception as e:
                    logging.error(f"Error when removing log file {log_file}: {e}")
        logging.info("Old log files successfully removed.")
    except Exception as e:
        logging.error(f"Error when removing old log files: {e}")
        result = False
    if result:
        logging.info("Database clean-up completely successful.")
    else:
        logging.error("Some errors occurred during the database clean-up.")
    if result != False: return {"result": f"Cleanup completed successfully."} 
    if result == False: return {"result": "Cleaned up files, but could not remove everything."}



@app.get("/api/v1/stream_list/")
async def get_stream_list():
    # List all running streams
    running_streams_list = list(running_streams.keys())
    logging.info(f"Total running streams: {len(running_streams_list)}")
    logging.info(f"Total scheduled streams: {len(scheduled_streams)}")
    return {"running_streams": running_streams_list, "scheduled_streams": scheduled_streams}


@app.get("/api/v1/stream_info/")
async def get_stream_info(stream_id: str):
    # Get information for a specific stream
    logging.info(f"Retrieving information for stream ID {stream_id}")
    engine, _, Session = init_db()
    session = Session()
    try:
        download = session.query(DownloadTask).filter_by(stream_id=stream_id).first()
        if download is None:
            logging.error(f"Stream ID {stream_id} not found.")
            return {"error": "Stream ID not found."}

        running_since = calculate_running_since(download.time)

        download_info = {
            "stream_id": download.stream_id,
            "name": download.name,
            "block_ads": download.block_ads,
            "time": download.time,
            "running_since": running_since,
            "quality": download.quality,
            "output_dir": download.output_dir,
            "url": download.url,
            "filename": download.filename,
            "running": download.running,
            "total_time": running_since
        }
        logging.info(f"Information for stream ID {stream_id} retrieved successfully.")
        return download_info
    finally:
        session.close()


@app.get("/api/v1/get_live_status/")
# get live status for a specific twitch account
async def get_live_status(username: str):
    logging.info(f"Checking live status for username: {username}")

    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        logging.error("Failed to get access token")
        raise HTTPException(status_code=500, detail="Failed to get access token")

    user_data = get_user(username, access_token, client_id, endpoint="streams", param="user_login")
    if user_data and 'data' in user_data and len(user_data['data']) > 0:
        stream_data = user_data['data'][0]
        logging.info(f"User {username} is live with stream data: {stream_data}")
        return {"live_status": "live", "stream_data": stream_data}
    else:
        logging.info(f"User {username} is not live")
        return {"live_status": "offline"}


@app.get("/api/v1/get_avatar/")
# get avatar for a specific twitch account
async def get_avatar(username: str):
    logging.info(f"Fetching avatar for username: {username}")

    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        logging.error("Failed to get access token")
        raise HTTPException(status_code=500, detail="Failed to get access token")

    user_data = get_user(username, access_token, client_id, endpoint="users", param="login")
    if user_data and 'data' in user_data and len(user_data['data']) > 0:
        profile_image_url = user_data['data'][0].get('profile_image_url')
        logging.info(f"Successfully fetched avatar for username: {username}")
        return {"profile_image_url": profile_image_url}
    else:
        logging.error(f"User not found or no profile image URL available for username: {username}")
        raise HTTPException(status_code=404, detail="User not found or no profile image URL available")