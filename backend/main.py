"""
FastAPI backend for Linear Guide Vibration Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import pandas as pd
from datetime import datetime
import os

try:
    from backend.database import init_db, get_db
    from backend.models import AnalysisResult, GuideSpec
    from backend.phm_models import PHMBearing, PHMTestData, PHMPrediction
    from backend.phm_processor import PHMDataProcessor
    from backend.phm_query import PHMDatabaseQuery
except ModuleNotFoundError:
    from database import init_db, get_db
    from models import AnalysisResult, GuideSpec
    from phm_models import PHMBearing, PHMTestData, PHMPrediction
    from phm_processor import PHMDataProcessor
    from phm_query import PHMDatabaseQuery
import json
import tempfile

app = FastAPI(
    title="Linear Guide Vibration Analysis API",
    description="API for CPC Linear Guide health monitoring and fault diagnosis",
    version="1.0.0"
)

# CORS middleware for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class GuideSpecRequest(BaseModel):
    series: str
    type: str
    preload: str
    C0: float
    C100: float
    seal_type: str
    speed_max: float
    stroke: float
    lubrication: Optional[str] = None


class AnalysisRequest(BaseModel):
    signal_data: List[float]
    fs: int
    velocity: float
    guide_spec_id: int


class FrequencyCalculationRequest(BaseModel):
    v: float  # velocity m/s
    D: float  # ball diameter mm
    L: float  # slider length mm
    n_balls: int
    contact_angle: float
    raceway_diameter: float


# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check
@app.get("/")
async def root():
    return {
        "message": "Linear Guide Vibration Analysis API",
        "version": "1.0.0",
        "status": "running"
    }


# Guide specifications endpoints
@app.post("/api/guide-specs", response_model=Dict)
async def create_guide_spec(spec: GuideSpecRequest):
    """Create a new guide specification"""
    db = next(get_db())
    try:
        guide_spec = GuideSpec(**spec.dict())
        db.add(guide_spec)
        db.commit()
        db.refresh(guide_spec)
        return {"id": guide_spec.id, "message": "Guide specification created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@app.get("/api/guide-specs", response_model=List[Dict])
async def get_guide_specs():
    """Get all guide specifications"""
    db = next(get_db())
    try:
        specs = db.query(GuideSpec).all()
        return [
            {
                "id": s.id,
                "series": s.series,
                "type": s.type,
                "preload": s.preload,
                "C0": s.C0,
                "C100": s.C100,
                "seal_type": s.seal_type,
                "speed_max": s.speed_max,
                "stroke": s.stroke,
                "lubrication": s.lubrication
            }
            for s in specs
        ]
    finally:
        db.close()


@app.get("/api/guide-specs/{spec_id}", response_model=Dict)
async def get_guide_spec(spec_id: int):
    """Get a specific guide specification"""
    db = next(get_db())
    try:
        spec = db.query(GuideSpec).filter(GuideSpec.id == spec_id).first()
        if not spec:
            raise HTTPException(status_code=404, detail="Guide specification not found")
        return {
            "id": spec.id,
            "series": spec.series,
            "type": spec.type,
            "preload": spec.preload,
            "C0": spec.C0,
            "C100": spec.C100,
            "seal_type": spec.seal_type,
            "speed_max": spec.speed_max,
            "stroke": spec.stroke,
            "lubrication": spec.lubrication
        }
    finally:
        db.close()


# Frequency calculation endpoint
@app.post("/api/calculate-frequencies", response_model=Dict)
async def calculate_frequencies(params: FrequencyCalculationRequest):
    """Calculate theoretical fault frequencies for linear guide"""
    try:
        v = params.v
        D = params.D / 1000  # convert to meters
        ball_spacing = params.L / params.n_balls / 1000  # meters

        # Ball Pass Frequency
        BPF = v / ball_spacing if ball_spacing > 0 else 0

        # Ball Spin Frequency
        BSF = v / (np.pi * D) if D > 0 else 0

        # Cage Frequency
        cage_freq = v / (params.L / 1000) if params.L > 0 else 0

        return {
            "BPF": round(BPF, 2),
            "BSF": round(BSF, 2),
            "Cage_Freq": round(cage_freq, 2),
            "2xBPF": round(2 * BPF, 2),
            "3xBPF": round(3 * BPF, 2),
            "harmonics": [
                {"order": i, "frequency": round(i * BPF, 2)}
                for i in range(1, 6)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")


# Analysis endpoints (commented out - requires VibrationAnalyzer)
# @app.post("/api/analyze", response_model=Dict)
# async def analyze_vibration(request: AnalysisRequest):
#     """Perform vibration analysis on signal data"""
#     pass


# @app.post("/api/upload-csv", response_model=Dict)
# async def upload_csv(...):
#     """Upload and analyze CSV file - requires VibrationAnalyzer"""
#     pass


@app.get("/api/results", response_model=List[Dict])
async def get_results(guide_spec_id: Optional[int] = None, limit: int = 50):
    """Get analysis results"""
    db = next(get_db())
    try:
        query = db.query(AnalysisResult)
        if guide_spec_id:
            query = query.filter(AnalysisResult.guide_spec_id == guide_spec_id)

        results = query.order_by(AnalysisResult.timestamp.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "velocity": r.velocity,
                "health_score": r.health_score,
                "time_features": r.time_features,
                "frequency_features": r.frequency_features,
                "findings": r.findings
            }
            for r in results
        ]
    finally:
        db.close()


@app.get("/api/results/{result_id}", response_model=Dict)
async def get_result(result_id: int):
    """Get a specific analysis result"""
    db = next(get_db())
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        return {
            "id": result.id,
            "guide_spec_id": result.guide_spec_id,
            "timestamp": result.timestamp.isoformat(),
            "velocity": result.velocity,
            "health_score": result.health_score,
            "time_features": result.time_features,
            "frequency_features": result.frequency_features,
            "envelope_features": result.envelope_features,
            "higher_order_features": result.higher_order_features,
            "findings": result.findings,
            "recommendations": result.recommendations
        }
    finally:
        db.close()


@app.get("/api/health-trend/{guide_spec_id}", response_model=Dict)
async def get_health_trend(guide_spec_id: int, days: int = 30):
    """Get health score trend for a guide"""
    db = next(get_db())
    try:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        results = db.query(AnalysisResult).filter(
            AnalysisResult.guide_spec_id == guide_spec_id,
            AnalysisResult.timestamp >= cutoff
        ).order_by(AnalysisResult.timestamp).all()

        return {
            "guide_spec_id": guide_spec_id,
            "days": days,
            "data_points": len(results),
            "trend": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "health_score": r.health_score,
                    "velocity": r.velocity
                }
                for r in results
            ]
        }
    finally:
        db.close()


# ========================================
# PHM 2012 Challenge Endpoints
# ========================================

@app.get("/api/phm/training-summary", response_model=Dict)
async def get_phm_training_summary():
    """獲取 PHM 訓練集摘要"""
    try:
        processor = PHMDataProcessor()
        summary = processor.get_training_summary()
        return {
            "total_bearings": len(summary),
            "bearings": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phm/upload-bearing-data", response_model=Dict)
async def upload_bearing_data(
    file: UploadFile = File(...),
    bearing_name: str = "Unknown"
):
    """上傳單個 PHM CSV 文件並分析"""
    try:
        processor = PHMDataProcessor()

        # 創建臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # 分析文件
        result = processor.analyze_bearing_file(tmp_path)

        # 清理臨時文件
        os.remove(tmp_path)

        # 保存到數據庫
        db = next(get_db())
        try:
            test_data = PHMTestData(
                bearing_name=bearing_name,
                file_index=0,
                time_min=0,
                horiz_rms=result['horiz_rms'],
                vert_rms=result['vert_rms'],
                horiz_peak=result['horiz_peak'],
                vert_peak=result['vert_peak'],
                horiz_kurtosis=result['horiz_kurtosis'],
                vert_kurtosis=result['vert_kurtosis']
            )
            db.add(test_data)
            db.commit()
            db.refresh(test_data)

            return {
                "id": test_data.id,
                "bearing_name": bearing_name,
                "analysis": result,
                "message": "File analyzed successfully"
            }
        finally:
            db.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/test-data/{bearing_name}", response_model=Dict)
async def get_bearing_test_data(bearing_name: str):
    """獲取特定軸承的測試數據"""
    db = next(get_db())
    try:
        data = db.query(PHMTestData).filter(
            PHMTestData.bearing_name == bearing_name
        ).order_by(PHMTestData.time_min).all()

        return {
            "bearing_name": bearing_name,
            "data_points": len(data),
            "time_series": [
                {
                    "time_min": d.time_min,
                    "horiz_rms": d.horiz_rms,
                    "vert_rms": d.vert_rms,
                    "horiz_kurtosis": d.horiz_kurtosis,
                    "vert_kurtosis": d.vert_kurtosis
                }
                for d in data
            ]
        }
    finally:
        db.close()


@app.get("/api/phm/analysis-data", response_model=Dict)
async def get_phm_analysis_data():
    """獲取預處理的 PHM 分析數據（從 JSON 文件）"""
    try:
        # 讀取生成的分析結果
        summary_path = "phm_analysis_results/summary.json"
        stats_path = "phm_analysis_results/vibration_statistics.csv"

        if not os.path.exists(summary_path):
            raise HTTPException(
                status_code=404,
                detail="Analysis results not found"
            )

        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)

        # 讀取統計數據
        stats_data = []
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
            stats_data = df.to_dict('records')

        return {
            "summary": summary,
            "statistics": stats_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phm/predict-rul", response_model=Dict)
async def predict_rul(
    bearing_name: str,
    model_type: str = "baseline"
):
    """預測軸承 RUL（簡單基線模型）"""
    db = next(get_db())
    try:
        # 獲取測試數據
        data = db.query(PHMTestData).filter(
            PHMTestData.bearing_name == bearing_name
        ).order_by(PHMTestData.time_min).all()

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {bearing_name}"
            )

        # 簡單基線預測：基於峰度趨勢
        kurtosis_values = [d.horiz_kurtosis for d in data]
        latest_kurtosis = kurtosis_values[-1] if kurtosis_values else 3

        # 簡化的 RUL 估計（基於峰度閾值）
        if latest_kurtosis > 10:
            predicted_rul = 500  # 嚴重異常，接近故障
        elif latest_kurtosis > 5:
            predicted_rul = 2000  # 中度異常
        else:
            predicted_rul = 5000  # 正常

        # 保存預測結果
        prediction = PHMPrediction(
            bearing_name=bearing_name,
            predicted_RUL_min=predicted_rul,
            model_type=model_type,
            confidence=0.7,
            features={
                "latest_kurtosis": latest_kurtosis,
                "data_points": len(data)
            }
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return {
            "id": prediction.id,
            "bearing_name": bearing_name,
            "predicted_RUL_min": predicted_rul,
            "model_type": model_type,
            "confidence": 0.7,
            "features": prediction.features
        }
    finally:
        db.close()


# ========================================
# PHM Database Query Endpoints
# ========================================

@app.get("/api/phm/database/bearings", response_model=Dict)
async def get_phm_database_bearings():
    """獲取 PHM 資料庫中所有軸承列表及統計"""
    try:
        query = PHMDatabaseQuery()
        bearings = query.get_bearings()
        return {
            "total_bearings": len(bearings),
            "bearings": bearings
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}", response_model=Dict)
async def get_phm_bearing_info(bearing_name: str):
    """獲取特定軸承的詳細資訊"""
    try:
        query = PHMDatabaseQuery()
        bearing = query.get_bearing_info(bearing_name)

        if bearing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Bearing {bearing_name} not found"
            )

        return bearing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/files", response_model=Dict)
async def get_phm_bearing_files(
    bearing_name: str,
    offset: int = 0,
    limit: int = 100
):
    """獲取軸承的檔案列表（分頁）"""
    try:
        query = PHMDatabaseQuery()
        result = query.get_file_list(bearing_name, offset, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/measurements",
         response_model=Dict)
async def get_phm_bearing_measurements(
    bearing_name: str,
    file_number: Optional[int] = None,
    offset: int = 0,
    limit: int = 1000
):
    """獲取軸承的測量資料（分頁）"""
    try:
        query = PHMDatabaseQuery()
        result = query.get_measurements(
            bearing_name,
            file_number,
            offset,
            limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/file/{file_number}/data",
         response_model=Dict)
async def get_phm_file_data(bearing_name: str, file_number: int):
    """獲取完整的檔案資料用於分析"""
    try:
        query = PHMDatabaseQuery()
        data = query.get_file_data_for_analysis(bearing_name, file_number)

        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"File {file_number} not found for {bearing_name}"
            )

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/statistics",
         response_model=Dict)
async def get_phm_bearing_statistics(bearing_name: str):
    """獲取軸承的統計資訊"""
    try:
        query = PHMDatabaseQuery()
        stats = query.get_bearing_file_statistics(bearing_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/anomalies",
         response_model=Dict)
async def search_phm_anomalies(
    bearing_name: str,
    threshold_h: float = 10.0,
    threshold_v: float = 10.0,
    limit: int = 100
):
    """搜尋異常振動資料"""
    try:
        query = PHMDatabaseQuery()
        anomalies = query.search_anomalies(
            bearing_name,
            threshold_h,
            threshold_v,
            limit
        )
        return {
            "bearing_name": bearing_name,
            "threshold_horizontal": threshold_h,
            "threshold_vertical": threshold_v,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
