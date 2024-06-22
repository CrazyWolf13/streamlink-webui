from pydantic import BaseModel, validator
import os
import re
import tempfile
from uuid import uuid4

class download_task(BaseModel):
    name: str
    base_dl_url: str = "https://www.twitch.tv/"
    block_ads: bool = False
    append_time: bool = True
    time_format: str = "%Y.%m.%d.%H.%M"
    quality: str = "best"
    output_dir: str = os.getcwd()
    stream_id: str = str(uuid4()) 

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