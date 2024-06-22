from typing import Union
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel, validator
import tempfile
import re
import os

# Define Pydantic base model for the stream object.
class Stream(BaseModel):
    name: str
    url: str = "https://www.twitch.tv/"
    block_ads: bool = False
    append_time: bool = True
    time_format: str = "%Y.%m.%d.%H.%M"
    quality: str = "best"
    output_dir: str = os.getcwd()

    @validator('name')
    def validate_username(cls, v):
        if not re.match(r'^\w{3,24}$', v):
            raise ValueError('Invalid username. The username must be 3 to 24 characters long and may only contain letters, numbers and underlines.')
        return v
    
    @validator('url')
    def validate_url(cls, v):
        if not re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/.*)?$', v):
            raise ValueError('Invalid URL. The URL must be a valid URL.')
        return v
    
    @validator('time_format')
    def validate_time_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9\.\-;:_\s%]+$', v):
            raise ValueError('Invalid time_format. Only alphanumeric characters, "., -, ;, :, _, %" are allowed.')
        return v
    
    @validator('quality')
    def validate_quality(cls, v):
        acceptable_qualities = ["audio_only", "160p", "worst", "360p", "480p", "720p", "720p60", "1080p60", "best"]
        if v not in acceptable_qualities:
            raise ValueError('Invalid quality parameter. Acceptable values are: audio_only, 160p, worst, 360p, 480p, 720p, 720p60, 1080p60, best')
        return v
    
    @validator('output_dir')
    def validate_output_dir(cls, v):
        if not os.path.isdir(v):
            raise ValueError('Invalid output_dir. The output_dir must be a valid directory.')
        # Try to create a temporary file in the directory
        try:
            temp_file = tempfile.TemporaryFile(dir=v)
            temp_file.close()  # Close and remove the temporary file immediately
        except (PermissionError, OSError) as e:
            raise ValueError(f'Cannot write to output_dir: {e}')
        return v

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/start/")
async def create_stream(stream: Stream):
    # Check if time needs to be appended to the filename.
    if stream.append_time == True: time = f"_{datetime.now().strftime(stream.time_format)}"
    else: time = ""

    # Set the appropriate file extension.
    if stream.quality == "audio_only": extension = ".mp3"  
    else: extension = ".mp4"
    
    # Returning the data that was passed to the API.
    return {
        "message": "Stream created with the following parameters:",
        "name": stream.name,
        "quality": stream.quality,
        "extension": extension,
        "block_ads": stream.block_ads,
        "append_time": stream.append_time,
        "time_format": stream.time_format,
        "time": time,
        "output_dir": stream.output_dir,
        "full_url": f"{stream.url}{stream.name}",
        "filename": f"{stream.name}{time}{extension}"
    }
