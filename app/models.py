from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from .db import Base

class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(64), unique=True, index=True, nullable=False)
    original_filename = Column(String(512), nullable=False)
    original_file_path = Column(String(1024), nullable=False)
    result_json_path = Column(String(1024), nullable=False)
    text_file_path = Column(String(1024), nullable=False)
    page_count = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="completed")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
