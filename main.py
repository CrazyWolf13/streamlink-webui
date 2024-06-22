import asyncio
from typing import Union
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator
import tempfile
from uuid import uuid4
import re
import os
import streamlink
from pathlib import Path
from download_task_model import download_task

# pip install streamlink fastapi uvicorn pydantic starlette alive-progress

# Global dictionary for tracking the current streams
running_streams = {}

async def run_streamlink_session_in_thread(download_task, filename, url):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        try:
            # Use run_in_executor to execute the coroutine in a separate thread
            await loop.run_in_executor(executor, lambda: asyncio.run(streamlink_session(download_task.name, url, download_task.quality, download_task.output_dir, download_task.block_ads, filename, download_task.stream_id)))
        except KeyError as e:
            # Log the error or execute an alternative logic
            print(f"KeyError beim Zugriff auf running_streams: {e}")

async def streamlink_session(name, url, quality, output_dir, block_ads, filename, stream_id):
    session = streamlink.Streamlink()
    try:
        plugin_name, plugin_class, _ = session.resolve_url(url)
    except streamlink.NoPluginError:
        raise HTTPException(status_code=404, detail="No plugin found for the given URL.")

    streams = session.streams(url)
    if not streams:
        raise HTTPException(status_code=404, detail="No streams found.")

    stream = streams.get(quality)
    if not stream:
        raise HTTPException(status_code=400, detail="Desired stream quality not found.")
    
    output_dir = Path(output_dir)
    output_file = output_dir / filename
    print(f"Saving stream to {output_file}")

    with open(output_file, "wb") as f:
        stream_fd = stream.open()
        # Add stream to index
        running_streams[stream_id] = stream_fd 
        try:
            while True:
                data = stream_fd.read(1024)
                if not data:
                    break
                f.write(data)
        finally:
            stream_fd.close()
            # remove stream from index
            if stream_id in running_streams:
                print(f"Stream ended, or network error {stream_id}")
                del running_streams[stream_id]
            else:
                print(f"Stream-ID {stream_id} nicht in running_streams gefunden.")
    return session
















    # Datenbankverbindung herstellen und Daten einfügen
    conn = sqlite3.connect('stream_info.db')
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO streams (stream_id, name, quality, extension, block_ads, append_time, time_format, time, output_dir, full_url, filename)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (download_task.stream_id, download_task.name, download_task.quality, extension, download_task.block_ads, download_task.append_time, download_task.time_format, time, download_task.output_dir, url, filename))
    
    conn.commit()
    conn.close()












app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/start/")
async def create_stream(download_task: download_task):
    # Check if time needs to be appended to the filename.
    if download_task.append_time == True: time = f"_{datetime.now().strftime(download_task.time_format)}"
    else: time = ""

    # Set the appropriate file extension.
    if download_task.quality == "audio_only": extension = ".mp3"  
    else: extension = ".mp4"

    filename = f"{download_task.name}{time}{extension}"
    url = f"{download_task.url}{download_task.name}"

    # start the streamlink session
    asyncio.create_task(run_streamlink_session_in_thread(download_task, filename, url))
    
    return {"stream_id": download_task.stream_id,
            "message": "Stream created with the following parameters:",
            "name": download_task.name,
            "quality": download_task.quality,
            "extension": extension,
            "block_ads": download_task.block_ads,
            "append_time": download_task.append_time,
            "time_format": download_task.time_format,
            "time": time,
            "output_dir": download_task.output_dir,
            "full_url": f"{download_task.url}{download_task.name}",
            "filename": f"{download_task.name}{time}{extension}"}



@app.post("/stop_all/")
async def stop_all_streams():
    print("Stopping all streams...")
    # List for collecting the stopped stream IDs
    stopped_streams = []  
    for stream_id in list(running_streams.keys()):
        print(f"Stopping stream {stream_id}")
        stream_fd = running_streams.get(stream_id)
        if stream_fd:
            stream_fd.close()
            stopped_streams.append(stream_id)  # Füge die gestoppte Stream-ID zur Liste hinzu
    return {"message": "All streams have been stopped.", "stopped_streams": stopped_streams}



@app.post("/stop/")
async def stop_stream(stream_id: str):
    print(f"Stopping stream {stream_id}")
    stream_fd = running_streams.get(stream_id)
    if stream_fd:
        stream_fd.close()
        return {"message": f"Stream {stream_id} has been stopped."}
    else:
        return {"message": f"Stream {stream_id} not found."}



@app.get("/stream_list/")
async def get_stream_list():
    return {"running_streams": list(running_streams.keys())}



@app.get("/stream_info/{stream_id}")
async def get_stream_info(stream_id: str):
    stream_info = running_streams.get(stream_id)
    if not stream_info:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Berechne die Laufzeit des Streams
    start_time = datetime.fromisoformat(stream_info["start_time"])
    running_since = datetime.now() - start_time

    return {
        "stream_id": stream_id,
        "start_time": stream_info["start_time"],
        "running_since": str(running_since),
        "download_task_terms": stream_info["download_task_terms"],
        "other_info": stream_info.get("other_info", "Keine weiteren Informationen verfügbar")
    }