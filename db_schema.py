from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from uuid import uuid4
from datetime import datetime

DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()

class DownloadTask(Base):
    __tablename__ = 'download_tasks'

    stream_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String)
    base_dl_url = Column(String, default="https://www.twitch.tv/")
    block_ads = Column(Boolean, default=False)
    append_time = Column(Boolean, default=True)
    time_format = Column(String, default="%Y.%m.%d.%H.%M")
    quality = Column(String, default="best")
    output_dir = Column(String, default=os.getcwd())
    # Berechnete Felder
    url = Column(String)
    filename = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = f"{self.base_dl_url}{self.name}"
        if self.append_time:
            time = f"_{datetime.now().strftime(self.time_format)}"
        else:
            time = ""
        self.filename = f"{self.name}{time}.mp4" if self.quality != "audio_only" else f"{self.name}{time}.mp3"