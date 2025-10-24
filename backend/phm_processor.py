"""
PHM 2012 數據處理器
處理上傳的 PHM 數據並提取特徵
"""
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from pathlib import Path


class PHMDataProcessor:
    """PHM 數據處理器"""

    # 操作條件映射
    OPERATING_CONDITIONS = {
        'Bearing1_1': {'condition': 1, 'load': 4000, 'speed': 1800},
        'Bearing1_2': {'condition': 1, 'load': 4200, 'speed': 1650},
        'Bearing1_3': {'condition': 1, 'load': 4200, 'speed': 1650},
        'Bearing1_4': {'condition': 1, 'load': 4000, 'speed': 1800},
        'Bearing1_5': {'condition': 1, 'load': 4200, 'speed': 1650},
        'Bearing1_6': {'condition': 1, 'load': 4000, 'speed': 1800},
        'Bearing1_7': {'condition': 1, 'load': 4000, 'speed': 1800},
        'Bearing2_1': {'condition': 2, 'load': 4200, 'speed': 1650},
        'Bearing2_2': {'condition': 2, 'load': 4000, 'speed': 1800},
        'Bearing2_3': {'condition': 2, 'load': 4200, 'speed': 1650},
        'Bearing2_4': {'condition': 2, 'load': 4200, 'speed': 1650},
        'Bearing2_5': {'condition': 2, 'load': 4200, 'speed': 1650},
        'Bearing2_6': {'condition': 2, 'load': 4000, 'speed': 1800},
        'Bearing2_7': {'condition': 2, 'load': 4000, 'speed': 1800},
        'Bearing3_1': {'condition': 3, 'load': 5000, 'speed': 1500},
        'Bearing3_2': {'condition': 3, 'load': 4200, 'speed': 1650},
        'Bearing3_3': {'condition': 3, 'load': 4200, 'speed': 1650},
    }

    # 訓練集 RUL 值
    TRAINING_RUL = {
        'Bearing1_1': 28020,
        'Bearing1_2': 8700,
        'Bearing2_1': 9100,
        'Bearing2_2': 7960,
        'Bearing3_1': 5730,
        'Bearing3_2': 16430,
    }

    def __init__(self, sampling_rate: int = 25600):
        self.sampling_rate = sampling_rate

    def parse_csv_file(self, file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        解析 PHM CSV 文件

        Returns:
            (horiz_vibration, vert_vibration)
        """
        df = pd.read_csv(file_path, header=None)

        # 格式: hour, minute, second, microsecond, horiz_vibration, vert_vibration
        horiz_vib = df.iloc[:, 4].values
        vert_vib = df.iloc[:, 5].values

        return horiz_vib, vert_vib

    def extract_features(self, signal: np.ndarray) -> Dict:
        """
        從振動信號提取特徵

        Args:
            signal: 振動信號數組

        Returns:
            特徵字典
        """
        features = {}

        # 時域特徵
        features['mean'] = float(np.mean(signal))
        features['std'] = float(np.std(signal))
        features['rms'] = float(np.sqrt(np.mean(signal**2)))
        features['peak'] = float(np.max(np.abs(signal)))
        features['peak_to_peak'] = float(np.ptp(signal))
        features['crest_factor'] = features['peak'] / features['rms'] if features['rms'] > 0 else 0

        # 峰度和偏度
        features['kurtosis'] = float(pd.Series(signal).kurtosis())
        features['skewness'] = float(pd.Series(signal).skew())

        # 頻域特徵（簡化版）
        fft_vals = np.fft.fft(signal)
        fft_mag = np.abs(fft_vals[:len(fft_vals)//2])
        freqs = np.fft.fftfreq(len(signal), 1/self.sampling_rate)[:len(fft_vals)//2]

        features['spectral_energy'] = float(np.sum(fft_mag**2))
        features['dominant_freq'] = float(freqs[np.argmax(fft_mag)])

        return features

    def analyze_bearing_file(self, file_path: str) -> Dict:
        """
        分析單個 CSV 文件

        Returns:
            分析結果字典
        """
        horiz_vib, vert_vib = self.parse_csv_file(file_path)

        horiz_features = self.extract_features(horiz_vib)
        vert_features = self.extract_features(vert_vib)

        result = {
            'horiz_rms': horiz_features['rms'],
            'vert_rms': vert_features['rms'],
            'horiz_peak': horiz_features['peak'],
            'vert_peak': vert_features['peak'],
            'horiz_kurtosis': horiz_features['kurtosis'],
            'vert_kurtosis': vert_features['kurtosis'],
            'horiz_features': horiz_features,
            'vert_features': vert_features,
        }

        return result

    def analyze_bearing_directory(self, bearing_path: str, bearing_name: str,
                                   sample_rate: int = 10) -> Dict:
        """
        分析整個軸承目錄

        Args:
            bearing_path: 軸承數據目錄路徑
            bearing_name: 軸承名稱
            sample_rate: 採樣率（每 N 個文件採樣一次）

        Returns:
            分析結果
        """
        csv_files = sorted([f for f in os.listdir(bearing_path) if f.endswith('.csv')])

        if not csv_files:
            raise ValueError(f"No CSV files found in {bearing_path}")

        # 獲取操作條件
        op_condition = self.OPERATING_CONDITIONS.get(bearing_name, {})

        # 分析結果
        analysis = {
            'bearing_name': bearing_name,
            'condition': op_condition.get('condition', 0),
            'load_N': op_condition.get('load', 0),
            'speed_rpm': op_condition.get('speed', 0),
            'actual_RUL_min': self.TRAINING_RUL.get(bearing_name, None),
            'num_files': len(csv_files),
            'sampling_rate_hz': self.sampling_rate,
            'time_series': []
        }

        # 採樣分析
        sample_indices = range(0, len(csv_files), sample_rate)

        for idx in sample_indices:
            file_path = os.path.join(bearing_path, csv_files[idx])

            try:
                file_result = self.analyze_bearing_file(file_path)
                file_result['file_index'] = idx
                file_result['time_min'] = idx * 10  # 假設每 10 分鐘一個文件

                analysis['time_series'].append(file_result)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue

        return analysis

    def get_training_summary(self) -> List[Dict]:
        """
        獲取訓練集摘要

        Returns:
            訓練集軸承列表
        """
        summary = []

        for bearing_name, rul in self.TRAINING_RUL.items():
            op_cond = self.OPERATING_CONDITIONS.get(bearing_name, {})
            summary.append({
                'name': bearing_name,  # 使用 'name' 以匹配前端
                'condition': op_cond.get('condition', 0),
                'load_N': op_cond.get('load', 0),
                'speed_rpm': op_cond.get('speed', 0),
                'actual_RUL_min': rul,
            })

        return summary

    def calculate_score(self, predicted_RUL: float, actual_RUL: float) -> float:
        """
        計算評分函數（根據 EXPERIMENT.md）

        A_i = RUL_predicted - RUL_actual
        Score = sum(exp(-A_i/13) - 1) if A_i < 0 (低估)
                sum(exp(A_i/10) - 1) if A_i >= 0 (高估)
        """
        error = predicted_RUL - actual_RUL

        if error < 0:  # 低估（更嚴重懲罰）
            score = np.exp(-error / 13) - 1
        else:  # 高估
            score = np.exp(error / 10) - 1

        return float(score)
