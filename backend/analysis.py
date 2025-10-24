"""
Vibration analysis core module
Integrates all analysis algorithms from the original codebase
"""
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import butter, filtfilt, hilbert
import pywt
from typing import Dict, Any, Tuple

# Import original modules
import sys
sys.path.append('..')
from timedomain import TimeDomain as td
from frequencydomain import FrequencyDomain as fd
from filterprocess import FilterProcess as fp
from waveletprocess import WaveLetProcess as wp
from hilbertransfer import HilberTransfer as ht
from harmonic_sildband_table import HarmonicSildband as hs


class VibrationAnalyzer:
    """
    Main vibration analyzer for linear guides
    Integrates all analysis methods
    """

    def __init__(self, guide_spec):
        """
        Initialize analyzer with guide specification

        Args:
            guide_spec: GuideSpec model instance
        """
        self.guide_spec = guide_spec
        self.baseline = None
        self.history = []

    def calculate_theoretical_frequencies(self, velocity: float) -> Dict[str, float]:
        """
        Calculate theoretical fault frequencies based on guide specs and velocity

        Args:
            velocity: Operating velocity in m/s

        Returns:
            Dictionary of theoretical frequencies
        """
        # Default parameters based on guide series
        params = self._get_guide_parameters(self.guide_spec.series)

        D = params['D'] / 1000  # convert to meters
        ball_spacing = params['L'] / params['n_balls'] / 1000

        # Ball Pass Frequency
        BPF = velocity / ball_spacing if ball_spacing > 0 else 0

        # Ball Spin Frequency
        BSF = velocity / (np.pi * D) if D > 0 else 0

        # Cage Frequency
        cage_freq = velocity / (params['L'] / 1000) if params['L'] > 0 else 0

        return {
            'BPF（滾動體通過頻率）': BPF,
            'BSF（滾動體自轉頻率）': BSF,
            'Cage_Freq（保持鏈頻率）': cage_freq,
            '2×BPF': 2 * BPF,
            '3×BPF': 3 * BPF
        }

    def _get_guide_parameters(self, series: str) -> Dict:
        """Get default parameters for guide series"""
        # Database of guide parameters
        params_db = {
            'HRC15': {'D': 3.175, 'L': 50, 'n_balls': 20, 'contact_angle': 45},
            'HRC20': {'D': 4.763, 'L': 60, 'n_balls': 22, 'contact_angle': 45},
            'HRC25': {'D': 6.35, 'L': 70, 'n_balls': 26, 'contact_angle': 45},
            'HRC30': {'D': 7.938, 'L': 80, 'n_balls': 28, 'contact_angle': 45},
            'HRC35': {'D': 9.525, 'L': 100, 'n_balls': 32, 'contact_angle': 45},
            'HRC45': {'D': 12.7, 'L': 120, 'n_balls': 36, 'contact_angle': 45},
        }

        return params_db.get(series, {'D': 6.35, 'L': 70, 'n_balls': 26, 'contact_angle': 45})

    def analyze(self, signal_data: np.ndarray, fs: int, velocity: float) -> Dict[str, Any]:
        """
        Complete vibration analysis

        Args:
            signal_data: Vibration signal array
            fs: Sampling frequency
            velocity: Operating velocity (m/s)

        Returns:
            Complete diagnosis dictionary
        """
        diagnosis = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'velocity': velocity,
            'health_score': 100,
            'findings': [],
            'recommendations': []
        }

        # Step 1: Time domain features
        time_features = self._extract_time_domain_features(signal_data)
        diagnosis['time_features'] = time_features

        # Step 2: Assess preload status
        preload_status = self._assess_preload_status(time_features, self.guide_spec.preload)
        diagnosis['preload_status'] = preload_status

        # Step 3: Frequency domain features
        theoretical_freqs = self.calculate_theoretical_frequencies(velocity)
        freq_features = self._extract_frequency_features(signal_data, fs, theoretical_freqs)
        diagnosis['frequency_features'] = freq_features

        # Step 4: Envelope analysis
        envelope_features = self._envelope_analysis(signal_data, fs, theoretical_freqs)
        diagnosis['envelope_features'] = envelope_features

        # Step 5: Higher order statistics
        higher_order_features = self._higher_order_statistics(signal_data, fs)
        diagnosis['higher_order_features'] = higher_order_features

        # Step 6: Wavelet analysis
        wavelet_features = self._wavelet_analysis(signal_data, fs)
        diagnosis['wavelet_features'] = wavelet_features

        # Step 7: Integrated diagnosis
        diagnosis = self._integrated_diagnosis(diagnosis)

        return diagnosis

    def _extract_time_domain_features(self, signal: np.ndarray) -> Dict[str, float]:
        """Extract time domain features"""
        pdata = pd.Series(signal)

        return {
            'Peak': float(td.peak(pdata)),
            'Avg': float(td.avg(pdata)),
            'RMS': float(td.rms(pdata)),
            'Kurtosis': float(td.kurt(pdata)),
            'Crest_Factor': float(td.cf(pdata))
        }

    def _assess_preload_status(self, time_features: Dict, preload_level: str) -> Dict:
        """
        Assess preload status based on time domain features

        Args:
            time_features: Time domain features
            preload_level: Preload level (VC, V0, V1, V2)

        Returns:
            Preload status assessment
        """
        rms = time_features['RMS']
        kurt = time_features['Kurtosis']

        status = {
            'level': preload_level,
            'condition': '正常',
            'warnings': []
        }

        # Thresholds based on preload level
        preload_thresholds = {
            'VC': {'rms_min': 0.05, 'kurt_max': 4.0},
            'V0': {'rms_min': 0.08, 'kurt_max': 4.5},
            'V1': {'rms_min': 0.12, 'kurt_max': 5.0},
            'V2': {'rms_min': 0.15, 'kurt_max': 5.5}
        }

        threshold = preload_thresholds.get(preload_level, preload_thresholds['V1'])

        if rms < threshold['rms_min'] * 0.7:
            status['condition'] = '預壓可能失效（振動過低）'
            status['warnings'].append('建議檢查預壓設定')

        if kurt > threshold['kurt_max']:
            status['condition'] = '預壓可能不足（衝擊明顯）'
            status['warnings'].append('可能存在間隙')

        return status

    def _extract_frequency_features(self, signal: np.ndarray, fs: int, theoretical_freqs: Dict) -> Dict:
        """Extract frequency domain features"""
        pdata = pd.Series(signal)

        try:
            # Use original frequency domain module
            fftoutput, total_fft_mgs, total_fft_bi, low_fm0 = fd.fft_fm0_si(pdata, fs)

            # Extract features around theoretical frequencies
            BPF = theoretical_freqs['BPF（滾動體通過頻率）']

            features = {
                'FM0': float(low_fm0),
                'Motor_Gear_Energy': float(total_fft_mgs) if not np.isnan(total_fft_mgs) else 0.0,
                'Belt_Energy': float(total_fft_bi) if not np.isnan(total_fft_bi) else 0.0,
                'BPF_Detected': False,
                'BPF_Amplitude': 0.0
            }

            # Check for BPF in spectrum
            if BPF > 0:
                tolerance = BPF * 0.05
                mask = (fftoutput['freqs'] >= BPF - tolerance) & (fftoutput['freqs'] <= BPF + tolerance)
                if mask.any():
                    bpf_amp = fftoutput.loc[mask, 'abs_fft'].max()
                    features['BPF_Detected'] = True
                    features['BPF_Amplitude'] = float(bpf_amp)

            return features
        except Exception as e:
            return {
                'FM0': 0.0,
                'Motor_Gear_Energy': 0.0,
                'Belt_Energy': 0.0,
                'BPF_Detected': False,
                'BPF_Amplitude': 0.0,
                'error': str(e)
            }

    def _envelope_analysis(self, signal: np.ndarray, fs: int, theoretical_freqs: Dict) -> Dict:
        """
        Envelope analysis for detecting rolling element defects
        """
        try:
            # Determine resonance band based on guide series
            resonance_band = self._determine_resonance_band(self.guide_spec.series)

            # Bandpass filter
            nyq = fs / 2
            low = resonance_band[0] / nyq
            high = resonance_band[1] / nyq

            # Ensure valid frequency range
            low = max(0.01, min(low, 0.99))
            high = max(0.01, min(high, 0.99))

            if low >= high:
                low, high = 0.1, 0.9

            b, a = butter(4, [low, high], btype='band')
            filtered = filtfilt(b, a, signal)

            # Hilbert transform
            analytic_signal = hilbert(filtered)
            envelope = np.abs(analytic_signal)

            # FFT of envelope
            envelope_fft = np.fft.fft(envelope - np.mean(envelope))
            envelope_freqs = np.fft.fftfreq(len(envelope), 1/fs)
            envelope_spectrum = np.abs(envelope_fft)

            positive = envelope_freqs >= 0
            envelope_freqs = envelope_freqs[positive]
            envelope_spectrum = envelope_spectrum[positive]

            # Detect BPF in envelope spectrum
            bpf = theoretical_freqs['BPF（滾動體通過頻率）']
            envelope_detections = {}

            for n in range(1, 5):
                target_freq = n * bpf
                tolerance = target_freq * 0.05

                mask = (envelope_freqs >= target_freq - tolerance) & \
                       (envelope_freqs <= target_freq + tolerance)

                if np.any(mask):
                    peak_amp = np.max(envelope_spectrum[mask])
                    noise = np.median(envelope_spectrum)
                    snr = float(peak_amp / noise) if noise > 0 else 0.0

                    envelope_detections[f'{n}×BPF'] = {
                        'frequency': float(target_freq),
                        'amplitude': float(peak_amp),
                        'snr': snr
                    }

            return {
                'resonance_band': resonance_band,
                'detections': envelope_detections,
                'defect_detected': len(envelope_detections) > 0
            }
        except Exception as e:
            return {
                'resonance_band': [0, 0],
                'detections': {},
                'defect_detected': False,
                'error': str(e)
            }

    def _determine_resonance_band(self, series: str) -> Tuple[float, float]:
        """Determine resonance band based on guide series"""
        size = int(''.join(filter(str.isdigit, series))) if any(c.isdigit() for c in series) else 25

        if 'MR' in series:
            return (8000, 15000)
        elif size <= 25:
            return (4000, 10000)
        elif size <= 45:
            return (2000, 8000)
        else:
            return (1000, 6000)

    def _higher_order_statistics(self, signal: np.ndarray, fs: int) -> Dict:
        """Calculate higher order statistics"""
        try:
            pdata = pd.DataFrame({'Degree': np.arange(len(signal)), 'Acc': signal})

            # NA4 calculation
            na4, _, _ = fp.NA4(pdata, 2)

            # FM4, M6A, M8A
            fm4 = fp.FM4(pd.Series(signal))
            m6a = fp.M6A(pd.Series(signal))
            m8a = fp.M8A(pd.Series(signal))

            return {
                'NA4': float(na4) if not np.isnan(na4) else 0.0,
                'FM4': float(fm4) if not np.isnan(fm4) else 0.0,
                'M6A': float(m6a) if not np.isnan(m6a) else 0.0,
                'M8A': float(m8a) if not np.isnan(m8a) else 0.0
            }
        except Exception as e:
            return {
                'NA4': 0.0,
                'FM4': 0.0,
                'M6A': 0.0,
                'M8A': 0.0,
                'error': str(e)
            }

    def _wavelet_analysis(self, signal: np.ndarray, fs: int) -> Dict:
        """Wavelet analysis for transient detection"""
        try:
            # STFT
            flat_np4, hann_np4 = wp.StftProcess(signal, fs)

            # CWT
            cwt_scale_max = 64
            ts = 1.0 / fs
            coef, freqs = pywt.cwt(signal, np.arange(1, cwt_scale_max), 'db8', ts)
            cwt_np4 = wp.CWTProcess(coef, freqs)

            return {
                'STFT_Flat_NP4': float(flat_np4) if not np.isnan(flat_np4) else 0.0,
                'STFT_Hann_NP4': float(hann_np4) if not np.isnan(hann_np4) else 0.0,
                'CWT_NP4': float(cwt_np4) if not np.isnan(cwt_np4) else 0.0
            }
        except Exception as e:
            return {
                'STFT_Flat_NP4': 0.0,
                'STFT_Hann_NP4': 0.0,
                'CWT_NP4': 0.0,
                'error': str(e)
            }

    def _integrated_diagnosis(self, diagnosis: Dict) -> Dict:
        """
        Integrated diagnosis combining all features
        """
        health_score = 100
        findings = []
        recommendations = []

        # Check time domain features
        time_features = diagnosis['time_features']
        if time_features['Kurtosis'] > 8:
            health_score -= 30
            findings.append('峰度異常升高，可能存在滾動體或軌道缺陷')
            recommendations.append('建議安排更換')
        elif time_features['Kurtosis'] > 5:
            health_score -= 15
            findings.append('峰度略高，顯示輕微衝擊')
            recommendations.append('加密監測頻率')

        # Check preload status
        preload_status = diagnosis.get('preload_status', {})
        if preload_status.get('condition') != '正常':
            health_score -= 20
            findings.append(f'預壓狀態: {preload_status.get("condition")}')
            recommendations.extend(preload_status.get('warnings', []))

        # Check envelope analysis
        envelope_features = diagnosis.get('envelope_features', {})
        if envelope_features.get('defect_detected'):
            health_score -= 25
            findings.append('包絡譜顯示滾動體或軌道缺陷')
            recommendations.append('建議進行詳細檢查')

        # Check higher order statistics
        higher_order = diagnosis.get('higher_order_features', {})
        if higher_order.get('NA4', 0) > 3:
            health_score -= 15
            findings.append('高階統計異常，疑似早期故障')
            recommendations.append('持續監測，準備備件')

        # Check wavelet features
        wavelet = diagnosis.get('wavelet_features', {})
        if wavelet.get('CWT_NP4', 0) > 4:
            health_score -= 10
            findings.append('瞬態衝擊檢測到異常')
            recommendations.append('檢查是否有異物或局部缺陷')

        # Ensure health score is in valid range
        health_score = max(0, min(100, health_score))

        # Determine severity
        if health_score >= 90:
            severity = '健康'
        elif health_score >= 75:
            severity = '輕微異常'
        elif health_score >= 60:
            severity = '中等異常'
        else:
            severity = '嚴重異常'

        diagnosis['health_score'] = health_score
        diagnosis['severity'] = severity
        diagnosis['findings'] = findings if findings else ['無明顯異常']
        diagnosis['recommendations'] = recommendations if recommendations else ['繼續例行監測']

        return diagnosis
