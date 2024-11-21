from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Time, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import logging


Base = declarative_base()

class DownloadTask(Base):
    __tablename__ = 'download_tasks'
    stream_id = Column(String, primary_key=True)
    name = Column(String)
    base_dl_url = Column(String)
    block_ads = Column(Boolean)
    append_time = Column(Boolean)
    time_format = Column(String)
    time = Column(DateTime)
    quality = Column(String)
    output_dir = Column(String)
    url = Column(String)
    filename = Column(String)
    running = Column(Boolean)
    schedule = Column(Boolean)
    schedule_interval = Column(Integer)
    schedule_end = Column(Integer)    

def remove_db():
    if os.path.exists("./application.db"):
        os.remove("./application.db")
        logging.info("Successfully cleaned up the database.")
        return {"Successfully cleaned up the database."}
    else:
        logging.info("No database file found.")
        return {"No database file found."}

def init_db():
    engine = create_engine('sqlite:///./application.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    logging.info("Database initialized.")
    return engine, Base, Session

async def get_running_stream_ids():
    engine, _, Session = init_db()
    session = Session()
    try:
        running_tasks = session.query(DownloadTask).filter(DownloadTask.running == True).all()
        running_stream_ids = [task.stream_id for task in running_tasks]
        logging.info(f"Running stream IDs: {running_stream_ids}")
        return running_stream_ids
    finally:
        session.close()


