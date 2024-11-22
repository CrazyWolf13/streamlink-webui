from pydantic import BaseModel, validator
import os
import re
import tempfile
from uuid import uuid4
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# Check if there is a DOWNLOAD_PATH env in the .env file, if not, use the current directory
if os.getenv("DOWNLOAD_PATH") is not None:
    # Make sure the path is a real path
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
    if not os.path.isdir(DOWNLOAD_PATH):
        raise ValueError('Invalid DOWNLOAD_PATH. The DOWNLOAD_PATH must be a valid directory.')
else:    
    DOWNLOAD_PATH = str(os.getcwd()) + "/downloads"

class download_task(BaseModel):
    name: str
    base_dl_url: str = "https://www.twitch.tv/"
    block_ads: bool = False
    append_time: bool = True
    time_format: str = "%Y-%m-%d-%H-%M"
    quality: str = "best"
    output_dir: str = str(DOWNLOAD_PATH)
    stream_id: str = 0
    schedule: bool = False
    schedule_interval: int = 5
    schedule_end: int = 12

    @validator('name')
    def validate_username(cls, v):
        if not re.match(r'^\w{3,24}$', v):
            raise ValueError('Invalid username. The username must be 3 to 24 characters long and may only contain letters, numbers and underlines.')
        return v
    
    @validator('base_dl_url')
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
        try:
            temp_file = tempfile.TemporaryFile(dir=v)
            temp_file.close()  
        except (PermissionError, OSError) as e:
            raise ValueError(f'Cannot write to output_dir: {e}')
        return v

    @validator('schedule')
    def validate_schedule(cls, v):
        if not isinstance(v, bool):
            raise ValueError('Invalid schedule. The schedule must be a boolean value.')
        return v

    @validator('schedule_interval')
    def validate_schedule_interval(cls, v):
        if v <= 0:
            raise ValueError('Invalid schedule_interval. The schedule_interval must be a positive integer.')
        return v

    @validator('schedule_end')
    def validate_schedule_end(cls, v):
        if v <= 0:
            raise ValueError('Invalid schedule_end. The schedule_end must be a positive integer.')
        return v