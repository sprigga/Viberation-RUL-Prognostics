"""
PHM 2012 數據模型
用於軸承 RUL 預測的數據結構
"""
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class PHMBearing(Base):
    """PHM 軸承數據表"""
    __tablename__ = "phm_bearings"

    id = Column(Integer, primary_key=True, index=True)
    bearing_name = Column(String, unique=True, index=True)  # e.g., "Bearing1_1"
    condition = Column(Integer)  # 操作條件 1-3
    load_N = Column(Float)  # 負載 (N)
    speed_rpm = Column(Float)  # 轉速 (RPM)
    actual_RUL_min = Column(Float)  # 實際 RUL (分鐘)
    num_files = Column(Integer)  # 數據文件數
    total_duration_min = Column(Float)  # 總時長
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PHMTestData(Base):
    """PHM 測試數據表"""
    __tablename__ = "phm_test_data"

    id = Column(Integer, primary_key=True, index=True)
    bearing_name = Column(String, index=True)  # e.g., "Bearing1_3"
    file_index = Column(Integer)  # 文件索引
    time_min = Column(Float)  # 時間 (分鐘)
    horiz_rms = Column(Float)  # 水平振動 RMS
    vert_rms = Column(Float)  # 垂直振動 RMS
    horiz_peak = Column(Float)  # 水平振動峰值
    vert_peak = Column(Float)  # 垂直振動峰值
    horiz_kurtosis = Column(Float)  # 水平振動峰度
    vert_kurtosis = Column(Float)  # 垂直振動峰度
    signal_data = Column(JSON)  # 原始信號數據 (可選)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PHMPrediction(Base):
    """PHM RUL 預測結果表"""
    __tablename__ = "phm_predictions"

    id = Column(Integer, primary_key=True, index=True)
    bearing_name = Column(String, index=True)
    predicted_RUL_min = Column(Float)  # 預測 RUL (分鐘)
    actual_RUL_min = Column(Float, nullable=True)  # 實際 RUL (如果已知)
    prediction_error = Column(Float, nullable=True)  # 預測誤差
    score = Column(Float, nullable=True)  # 評分函數結果
    features = Column(JSON)  # 使用的特徵
    model_type = Column(String)  # 模型類型
    confidence = Column(Float)  # 預測信心度
    created_at = Column(DateTime(timezone=True), server_default=func.now())
