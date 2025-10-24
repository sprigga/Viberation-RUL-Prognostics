"""
SQLAlchemy models for database
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class GuideSpec(Base):
    """Linear guide specification model"""
    __tablename__ = "guide_specs"

    id = Column(Integer, primary_key=True, index=True)
    series = Column(String, nullable=False)  # e.g., "HRC25"
    type = Column(String, nullable=False)  # e.g., "MN"
    preload = Column(String, nullable=False)  # e.g., "V1"
    C0 = Column(Float, nullable=False)  # Static load rating (N)
    C100 = Column(Float, nullable=False)  # Dynamic load rating (N)
    seal_type = Column(String)  # e.g., "S"
    speed_max = Column(Float)  # m/s
    stroke = Column(Float)  # mm
    lubrication = Column(String, nullable=True)  # e.g., "Z"
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="guide_spec")


class AnalysisResult(Base):
    """Vibration analysis result model"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    guide_spec_id = Column(Integer, ForeignKey("guide_specs.id"))
    timestamp = Column(DateTime, default=datetime.now, index=True)
    velocity = Column(Float)  # Operating velocity (m/s)

    # Analysis results
    health_score = Column(Float)  # 0-100
    time_features = Column(JSON)  # Time domain features
    frequency_features = Column(JSON)  # Frequency domain features
    envelope_features = Column(JSON, nullable=True)  # Envelope analysis features
    higher_order_features = Column(JSON, nullable=True)  # Higher order statistics

    # Diagnosis
    findings = Column(JSON)  # List of findings
    recommendations = Column(JSON)  # List of recommendations

    # Relationships
    guide_spec = relationship("GuideSpec", back_populates="analysis_results")


class DiagnosisHistory(Base):
    """Historical diagnosis records for trend analysis"""
    __tablename__ = "diagnosis_history"

    id = Column(Integer, primary_key=True, index=True)
    guide_spec_id = Column(Integer, ForeignKey("guide_specs.id"))
    timestamp = Column(DateTime, default=datetime.now, index=True)

    # Key metrics
    rms = Column(Float)
    peak = Column(Float)
    kurtosis = Column(Float)
    crest_factor = Column(Float)
    health_score = Column(Float)

    # Operating conditions
    velocity = Column(Float)
    temperature = Column(Float, nullable=True)
    load = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
