from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from .db import Base


class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, unique=True, index=True)

    filename = Column(String)
    page_count = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)


class OCRTextBlock(Base):
    __tablename__ = "ocr_text_blocks"

    id = Column(Integer, primary_key=True)

    job_id = Column(String, index=True)
    page = Column(Integer)

    text = Column(String)
    confidence = Column(Float)

    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)
    x3 = Column(Float)
    y3 = Column(Float)
    x4 = Column(Float)
    y4 = Column(Float)
