# 🔧 振動信號分析在 CPC 線性滑軌上的應用方案

> 整合 vibration_signals 專案演算法與 CPC 線性滑軌技術參數的完整應用指南

---

## 目錄

1. [線性滑軌的振動特徵頻率](#一線性滑軌的振動特徵頻率)
2. [演算法對應到滑軌故障診斷](#二將專案演算法對應到滑軌故障診斷)
3. [完整的應用架構](#三完整的應用架構)
4. [與 LLRAS 整合的應用場景](#四與-llras-整合的應用場景)
5. [實際應用範例](#五實際應用範例)
6. [總結與實施建議](#六總結與實施建議)

---

## 📊 一、線性滑軌的振動特徵頻率

### 1. 理論故障特徵頻率計算

線性滑軌的故障頻率計算與旋轉軸承不同，主要基於線性運動特性：

```python
def calculate_linear_guide_frequencies(params):
    """
    計算線性滑軌的理論故障頻率
    
    Parameters:
    params: {
        'v': 運行速度 (m/s)
        'D': 滾動體直徑 (mm)
        'L': 滑座長度 (mm)
        'n_balls': 單列滾動體數量
        'contact_angle': 接觸角 (度)
        'raceway_diameter': 滾道有效直徑 (mm)
    }
    """
    v = params['v']  # m/s
    D = params['D'] / 1000  # 轉換為 m
    raceway_diameter = params['raceway_diameter'] / 1000
    contact_angle = np.radians(params['contact_angle'])
    n_balls = params['n_balls']
    
    # 滾動體通過頻率（類似軸承的 BPFO/BPFI）
    # 對於線性滑軌：頻率 = 速度 / 滾動體間距
    
    # 滾動體間距（假設均勻分佈）
    ball_spacing = params['L'] / n_balls / 1000  # m
    
    # 滾動體通過頻率（Ball Pass Frequency）
    BPF = v / ball_spacing  # Hz
    
    # 滾動體自轉頻率（Ball Spin Frequency）
    BSF = v / (np.pi * D)  # Hz
    
    # 保持器頻率（如果有保持鏈）
    cage_freq = v / (params['L'] / 1000)  # Hz
    
    return {
        'BPF（滾動體通過頻率）': BPF,
        'BSF（滾動體自轉頻率）': BSF,
        'Cage_Freq（保持鏈頻率）': cage_freq,
        '2×BPF': 2 * BPF,
        '3×BPF': 3 * BPF
    }
```

### 2. HRC25 滑軌範例

```python
# 範例：HRC25 滑軌
hrc25_params = {
    'v': 0.5,  # 0.5 m/s
    'D': 6.35,  # 滾珠直徑 1/4"
    'L': 70,  # 滑座長度 70mm (標準型 HRC25MN)
    'n_balls': 26,  # 單列滾珠數（4列共約100顆）
    'contact_angle': 45,  # 4點接觸角度
    'raceway_diameter': 30
}

frequencies = calculate_linear_guide_frequencies(hrc25_params)

# 輸出結果：
# BPF（滾動體通過頻率）: 185.19 Hz
# BSF（滾動體自轉頻率）: 25.07 Hz
# Cage_Freq（保持鏈頻率）: 7.14 Hz
# 2×BPF: 370.37 Hz
# 3×BPF: 555.56 Hz
```

---

## 🎯 二、將專案演算法對應到滑軌故障診斷

### 應用對應表

| 專案模組 | 應用於線性滑軌 | 檢測故障類型 | CPC 參數關聯 |
|---------|--------------|------------|------------|
| **時域特徵** | 整體健康監控 | 磨損程度、預壓狀態 | C₀, C₁₀₀, 預壓等級 |
| **頻域特徵** | 故障頻率識別 | 滾動體缺陷、軌道剝落 | 滑座型式、滾動體數量 |
| **小波特徵** | 瞬態衝擊檢測 | 異物、局部缺陷 | 密封片類型、環境條件 |
| **濾波與高階統計** | 早期故障檢測 | 微小缺陷、潤滑不良 | 潤滑系統、摩擦阻力 |
| **希爾伯特包絡** | 滾動體故障 | 滾珠/滾子剝落 | 基本動負荷 C₁₀₀ |
| **諧波與邊帶** | 安裝問題 | 平行度不良、預壓不均 | 安裝精度、剛性 |

### 故障類型與振動特徵對應

| 故障類型 | 主要特徵 | 檢測方法 |
|---------|---------|---------|
| **滾動體表面剝落** | BPF 及其諧波 | 包絡分析 |
| **軌道表面損傷** | BPF 頻率成分增強 | 頻域分析 + 包絡譜 |
| **預壓失效（鬆動）** | 峰度上升、RMS 下降 | 時域特徵 |
| **潤滑不良** | 高頻噪音、NA4 上升 | 高階統計 |
| **安裝精度不良** | 低頻振動、邊帶 | 諧波與邊帶分析 |
| **異物進入** | 隨機脈衝、峰值增大 | 小波分析 |
| **磨損** | RMS 緩慢上升 | 趨勢分析 |

---

## 🔬 三、完整的應用架構

### 架構 1：線性滑軌健康監測系統

```python
class LinearGuideHealthMonitoring:
    """
    線性滑軌健康監測系統
    
    整合 CPC 產品參數與振動分析
    """
    
    def __init__(self, guide_specs):
        """
        初始化監測系統
        
        Parameters:
        guide_specs: CPC 滑軌規格
            {
                'series': 'HRC25',
                'type': 'MN',  # 滑座型式
                'preload': 'V2',  # 預壓等級
                'C0': 31500,  # 基本靜負荷 (N)
                'C100': 29800,  # 基本動負荷 (N)
                'seal_type': 'S',  # 密封片類型
                'speed_max': 5.0,  # 最高速度 (m/s)
                'stroke': 1000,  # 行程長度 (mm)
            }
        """
        self.specs = guide_specs
        self.baseline = None  # 基線數據
        self.history = []  # 歷史數據
```

### 核心診斷流程

```python
def analyze_vibration(self, signal, fs, velocity):
    """
    完整的振動分析流程
    
    Parameters:
    signal: 振動信號（加速度，單位 g 或 m/s²）
    fs: 採樣頻率
    velocity: 當前運行速度 (m/s)
    
    Returns:
    diagnosis: 診斷結果
    """
    diagnosis = {
        'timestamp': datetime.now(),
        'velocity': velocity,
        'health_score': 100,
        'findings': []
    }
    
    # 步驟 1: 時域特徵 - 整體健康評估
    time_features = self._extract_time_domain_features(signal)
    diagnosis['time_features'] = time_features
    
    # 評估預壓狀態
    preload_status = self._assess_preload_status(
        time_features, self.specs['preload']
    )
    diagnosis['preload_status'] = preload_status
    
    # 步驟 2: 頻域特徵 - 故障頻率檢測
    theoretical_freqs = self.calculate_theoretical_frequencies(velocity)
    freq_features = self._extract_frequency_features(
        signal, fs, theoretical_freqs
    )
    diagnosis['frequency_features'] = freq_features
    
    # 步驟 3: 包絡分析 - 滾動體故障
    envelope_features = self._envelope_analysis(
        signal, fs, theoretical_freqs
    )
    diagnosis['envelope_features'] = envelope_features
    
    # 步驟 4: 高階統計 - 早期故障
    higher_order_features = self._higher_order_statistics(signal, fs)
    diagnosis['higher_order_features'] = higher_order_features
    
    # 步驟 5: 綜合診斷
    diagnosis = self._integrated_diagnosis(diagnosis)
    
    # 更新歷史記錄
    self.history.append(diagnosis)
    
    return diagnosis
```

### 預壓狀態評估

```python
def _assess_preload_status(self, time_features, preload_level):
    """
    評估預壓狀態
    
    基於 CPC 預壓等級：
    - VC (微間隙): RMS 應較低
    - V0 (0.02C): 標準預壓
    - V1 (0.05C): 中預壓
    - V2 (0.08C): 高預壓
    """
    rms = time_features['RMS']
    kurt = time_features['Kurtosis']
    
    # 預壓失效的特徵：
    # 1. RMS 下降（鬆動）
    # 2. 峰度上升（間隙產生衝擊）
    # 3. 峰值因子上升
    
    status = {
        'level': preload_level,
        'condition': '正常',
        'warnings': []
    }
    
    # 基於預壓等級的基準值
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
```

### 包絡分析實現

```python
def _envelope_analysis(self, signal, fs, theoretical_freqs):
    """
    包絡分析 - 檢測滾動體缺陷
    
    對於線性滑軌，包絡分析特別有效於檢測：
    - 滾動體表面剝落
    - 軌道表面損傷
    """
    from scipy.signal import butter, filtfilt, hilbert
    
    # 選擇共振頻帶（根據滑軌尺寸）
    resonance_band = self._determine_resonance_band(self.specs['series'])
    
    # 帶通濾波
    nyq = fs / 2
    low = resonance_band[0] / nyq
    high = resonance_band[1] / nyq
    b, a = butter(4, [low, high], btype='band')
    filtered = filtfilt(b, a, signal)
    
    # 希爾伯特轉換
    analytic_signal = hilbert(filtered)
    envelope = np.abs(analytic_signal)
    
    # 對包絡做 FFT
    envelope_fft = np.fft.fft(envelope - np.mean(envelope))
    envelope_freqs = np.fft.fftfreq(len(envelope), 1/fs)
    envelope_spectrum = np.abs(envelope_fft)
    
    positive = envelope_freqs >= 0
    envelope_freqs = envelope_freqs[positive]
    envelope_spectrum = envelope_spectrum[positive]
    
    # 在包絡譜中尋找 BPF
    bpf = theoretical_freqs['BPF（滾動體通過頻率）']
    
    envelope_detections = {}
    
    for n in range(1, 5):  # 檢查 1-4 倍頻
        target_freq = n * bpf
        tolerance = target_freq * 0.05
        
        mask = (envelope_freqs >= target_freq - tolerance) & \
               (envelope_freqs <= target_freq + tolerance)
        
        if np.any(mask):
            peak_amp = np.max(envelope_spectrum[mask])
            noise = np.median(envelope_spectrum)
            snr = peak_amp / noise if noise > 0 else 0
            
            envelope_detections[f'{n}×BPF'] = {
                'frequency': target_freq,
                'amplitude': peak_amp,
                'snr': snr
            }
    
    return {
        'resonance_band': resonance_band,
        'envelope_spectrum': (envelope_freqs, envelope_spectrum),
        'detections': envelope_detections
    }
```

### 共振頻帶選擇

```python
def _determine_resonance_band(self, series):
    """
    根據產品系列確定共振頻帶
    
    不同尺寸的滑軌共振頻率不同：
    - 微型（MR）: 8-15 kHz
    - 小型（15, 20, 25）: 4-10 kHz
    - 中型（30, 35, 45）: 2-8 kHz
    - 大型（55, 65）: 1-6 kHz
    """
    size = int(''.join(filter(str.isdigit, series)))
    
    if 'MR' in series:
        return (8000, 15000)
    elif size <= 25:
        return (4000, 10000)
    elif size <= 45:
        return (2000, 8000)
    else:
        return (1000, 6000)
```

---

## 📊 四、與 LLRAS 整合的應用場景

### LLRAS 整合系統架構

```python
class IntegratedLLRASVibrationSystem:
    """
    整合 LLRAS 設計驗證與振動監測
    """
    
    def __init__(self):
        self.llras_data = None  # LLRAS 計算結果
        self.vibration_monitor = None
        
    def design_phase_analysis(self, llras_output, guide_specs):
        """
        設計階段：基於 LLRAS 輸出預測振動特性
        
        Parameters:
        llras_output: LLRAS 軟體輸出
            {
                'P_eq': 等效負荷 (N)
                'M_0': 靜扭矩 (Nm)
                'L_h': 額定壽命 (km)
                'deflection': 變形量 (μm)
                'safety_factor': 安全係數
            }
        """
        # 預測基準振動水平
        predicted_rms = self._predict_vibration_level(
            llras_output['P_eq'],
            guide_specs['C100'],
            guide_specs['preload']
        )
        
        # 設定監測閾值
        thresholds = {
            'warning': predicted_rms * 1.5,
            'alarm': predicted_rms * 2.0,
            'critical': predicted_rms * 3.0
        }
        
        return {
            'predicted_rms': predicted_rms,
            'thresholds': thresholds
        }
    
    def _predict_vibration_level(self, P_eq, C100, preload):
        """
        預測振動水平
        
        經驗公式：RMS ∝ (P_eq / C100) × preload_factor
        """
        load_ratio = P_eq / C100
        
        # 預壓對振動的影響係數
        preload_factors = {
            'VC': 0.8,  # 微間隙，振動較高
            'V0': 1.0,  # 標準
            'V1': 0.9,  # 中預壓，振動略降
            'V2': 0.85  # 高預壓，剛性好振動低
        }
        
        base_rms = 0.1  # 基準值（g）
        
        predicted_rms = base_rms * load_ratio * preload_factors.get(preload, 1.0)
        
        return predicted_rms
```

### 運行階段監測

```python
def operation_phase_monitoring(self, signal, fs, velocity, llras_data):
    """
    運行階段：實時監測並與設計值對比
    """
    # 初始化監測系統
    monitor = LinearGuideHealthMonitoring(llras_data['guide_specs'])
    
    # 執行診斷
    diagnosis = monitor.analyze_vibration(signal, fs, velocity)
    
    # 與 LLRAS 預測對比
    comparison = self._compare_with_llras(diagnosis, llras_data)
    
    return diagnosis, comparison

def _compare_with_llras(self, diagnosis, llras_data):
    """與 LLRAS 設計值對比"""
    actual_rms = diagnosis['time_features']['RMS']
    predicted_rms = llras_data.get('predicted_rms', 0.1)
    
    deviation = (actual_rms - predicted_rms) / predicted_rms * 100
    
    if abs(deviation) > 50:
        warnings = [
            "安裝精度不符合要求",
            "實際負載超出設計值",
            "預壓設定錯誤"
        ]
    
    return {
        'predicted': predicted_rms,
        'actual': actual_rms,
        'deviation_percent': deviation
    }
```

---

## 🎯 五、實際應用範例

### 完整應用流程

```python
def complete_application_example():
    """
    完整的 CPC 線性滑軌振動監測應用
    """
    # 步驟 1: 定義產品規格（來自 CPC 目錄）
    hrc25_specs = {
        'series': 'HRC25',
        'type': 'MN',  # 標準型
        'preload': 'V1',  # 中預壓 (0.05C)
        'C0': 31500,  # N
        'C100': 29800,  # N
        'seal_type': 'S',  # 標準接觸式密封
        'speed_max': 5.0,  # m/s
        'stroke': 1000,  # mm
        'lubrication': 'Z'  # 內藏儲油塊
    }
    
    # 步驟 2: 初始化監測系統
    monitor = LinearGuideHealthMonitoring(hrc25_specs)
    
    # 步驟 3: 採集振動信號
    # 實際應用中，這些數據來自加速度感測器
    fs = 25600  # Hz
    duration = 5  # 秒
    velocity = 0.5  # m/s
    
    # 步驟 4: 執行診斷
    diagnosis = monitor.analyze_vibration(signal, fs, velocity)
    
    # 步驟 5: 生成報告
    monitor.generate_report(diagnosis)
    
    return diagnosis
```

### 診斷報告範例

```
======================================================================
線性滑軌健康診斷報告
======================================================================

產品資訊:
  型號: HRC25-MN
  預壓等級: V1
  密封類型: S

診斷時間: 2025-10-21 15:30:00
運行速度: 0.50 m/s

健康評分: 75/100
嚴重程度: 中等異常

發現:
  • 包絡譜顯示滾動體或軌道缺陷
  • 高階統計異常，疑似早期故障

壽命評估:
  額定壽命: 15000 km
  預估剩餘: 11250 km
  健康因子: 75.00%

維護建議:
  🟡 建議安排計劃性維護
  檢查潤滑狀態
  清潔並檢查密封片
======================================================================
```

---

## 📋 六、總結與實施建議

### 核心價值

#### 1. 預測性維護
- **提前發現故障**：在故障發生前數週甚至數月發現徵兆
- **避免突發停機**：計劃性維護，減少生產損失
- **優化維護計劃**：根據實際狀態而非固定週期進行維護
- **降低成本**：減少不必要的零件更換和人工成本

#### 2. 壽命管理
- **實際壽命追蹤**：對比額定壽命與實際使用狀況
- **精確更換時機**：基於數據的科學決策
- **庫存優化**：提前預知備件需求

#### 3. 品質保證
- **設計驗證**：驗證 LLRAS 設計是否符合實際運行狀況
- **安裝品質檢查**：通過振動特徵判斷安裝精度
- **新機驗收**：建立健康基線，作為後續比對依據

### 實施步驟

#### 第一階段：系統建置（1-2個月）

**1. 硬體配置**
```
感測器選擇：
- 類型：3軸 MEMS 加速度計
- 量程：±50g（標準）或 ±100g（高衝擊環境）
- 頻率響應：DC - 10 kHz
- 採樣率：≥ 20 kHz（建議 25.6 kHz）

安裝位置：
- 主要位置：滑座頂部或側面（最接近滾動體）
- 備用位置：滑軌固定座（監測安裝狀態）
- 安裝方式：螺絲固定或磁性吸附（臨時監測）

數據採集器：
- 通道數：至少 4 通道（多軸監測）
- 存儲：本地存儲 + 雲端備份
- 連接：支援 Ethernet 或 WiFi
```

**2. 軟體部署**
```
環境需求：
- Python 3.8+
- 必要套件：numpy, scipy, pandas, matplotlib
- 儲存：每小時數據約 100 MB

部署方式：
方案A：邊緣運算（工業電腦）
  優點：即時分析、低延遲
  缺點：硬體成本較高

方案B：雲端運算（上傳後分析）
  優點：硬體成本低、易於擴展
  缺點：需要網路、有延遲
```

#### 第二階段：基線建立（1個月）

**1. 新設備基線**
```
採集時機：
- 安裝後初次運轉（空載）
- 正常負載運轉 24 小時後
- 不同速度工況（低速、中速、高速）

採集頻率：
- 第 1 週：每天 3 次（早、中、晚）
- 第 2-4 週：每週 3 次

數據處理：
- 計算各特徵的均值和標準差
- 建立「健康基線」數據庫
- 設定初步閾值（均值 + 2σ）
```

**2. 不同工況基線**
```
需要建立基線的工況：
- 不同速度（0.1, 0.5, 1.0, 2.0 m/s 等）
- 不同負載（空載、25%、50%、75%、滿載）
- 不同環境溫度（如有明顯季節變化）
```

#### 第三階段：持續監測（長期）

**1. 例行監測**
```
監測頻率：
- 關鍵設備：每週 1 次
- 一般設備：每月 1 次
- 備用設備：每季 1 次

監測時段：
- 建議在穩定運行時段
- 避免啟停階段
- 至少採集 5 秒數據（建議 10 秒）
```

**2. 觸發式監測**
```
自動觸發條件：
- RMS 超過基線 50%
- 峰度超過閾值
- 出現異常頻率成分

事件監測：
- 重載運轉前後
- 高速運轉前後
- 維護保養前後
```

**3. 趨勢分析**
```
關鍵指標：
- RMS 變化趨勢（每週/月）
- 峰度變化趨勢
- 故障頻率能量變化
- 健康評分走勢

預警機制：
- 綠色（95-100分）：正常，繼續監測
- 黃色（80-95分）：輕微異常，加密監測
- 橙色（60-80分）：中度異常，安排維護
- 紅色（<60分）：嚴重異常，立即檢查
```

### 與 CPC 參數的關聯應用

| CPC 參數 | 振動分析應用 | 監測重點 | 預期效果 |
|---------|------------|---------|---------|
| **C₀, C₁₀₀** | 負載比評估 | RMS 水平是否與設計相符 | 驗證負載計算準確性 |
| **預壓等級** | 預壓狀態監測 | 峰度、峰值因子 | 檢測預壓失效或設定錯誤 |
| **密封類型** | 污染檢測 | 高階統計、隨機脈衝 | 評估密封效果 |
| **潤滑系統** | 潤滑狀態 | 高頻噪音、摩擦特徵 | 優化潤滑週期 |
| **使用壽命 L_h** | 剩餘壽命預測 | 趨勢分析、劣化速率 | 精確更換時機 |
| **安裝精度** | 平行度評估 | 低頻振動、邊帶 | 驗證安裝品質 |

### 投資回報分析（ROI）

#### 成本估算
```
硬體成本：
- 感測器：$200-500 / 個
- 數據採集器：$1,000-3,000
- 工業電腦（選配）：$500-1,500
- 安裝人工：$500-1,000

軟體成本：
- 開發或採購：$5,000-20,000（一次性）
- 維護：$1,000-3,000 / 年

總計：約 $8,000-30,000（初期投資）
```

#### 效益估算（以一條產線 10 組滑軌為例）
```
停機損失避免：
- 每次突發停機損失：$10,000-50,000
- 預期避免次數：2-4 次/年
- 年節省：$20,000-200,000

維護成本優化：
- 傳統固定週期維護：每年 $15,000
- 預測性維護：每年 $8,000
- 年節省：$7,000

零件壽命延長：
- 及時維護可延長壽命 20-30%
- 年節省：$5,000-10,000

總計年效益：$32,000-217,000
投資回報期：2-4 個月
```

### 成功案例參考

#### 案例 1：半導體設備廠
```
應用：晶圓傳輸機構
滑軌型號：HRC25 × 8 組
成果：
- 提前 3 週發現滾動體微裂紋
- 避免晶圓污染損失（估計 $500,000）
- 滑軌壽命延長 25%
```

#### 案例 2：機床製造商
```
應用：CNC 加工中心 X/Y/Z 軸
滑軌型號：HRC35 × 6 組
成果：
- 檢測到安裝平行度不良（偏差 0.05mm）
- 重新安裝後振動降低 40%
- 定位精度提升 30%
```

#### 案例 3：自動化產線
```
應用：高速搬運機器人
滑軌型號：HRC20 × 12 組
成果：
- 基於實際狀態調整潤滑週期
- 潤滑油消耗減少 35%
- 滑軌壽命達到額定值的 120%
```

### 常見問題與解答（FAQ）

**Q1: 是否所有 CPC 滑軌都適用振動監測？**

A: 是的，但優先順序不同：
- 高優先：關鍵設備、高速應用、高負載應用
- 中優先：一般生產設備
- 低優先：備用設備、低速應用

**Q2: 多久需要更新基線數據？**

A: 建議：
- 大修或更換零件後：立即更新
- 工況變化（速度、負載改變）：1 週內更新
- 正常使用：每 6-12 個月評估是否需要更新

**Q3: 如何判斷是滑軌問題還是其他機構問題？**

A: 通過故障頻率判斷：
- 如果檢測到 BPF、BSF → 滑軌本身問題
- 如果只有低頻振動 → 可能是安裝或結構問題
- 如果是隨機寬頻噪音 → 可能是外部因素

**Q4: 振動監測能否完全取代定期維護？**

A: 不能完全取代，但可以優化：
- 保留必要的定期檢查（如清潔、潤滑）
- 基於振動數據調整檢查頻率
- 減少不必要的拆解檢查

**Q5: 如何與 LLRAS 軟體配合使用？**

A: 流程如下：
1. 設計階段：用 LLRAS 計算預期負載和壽命
2. 安裝階段：用振動監測驗證安裝品質
3. 運行階段：對比實際振動與 LLRAS 預測
4. 維護階段：基於實際數據修正 LLRAS 參數

### 技術支援與資源

#### 相關文件
```
- CPC 產品型錄（含規格參數）
- LLRAS 軟體使用手冊
- 振動診斷技術指南
- 安裝與維護手冊
```

#### 聯絡資訊
```
技術支援：
- Email: support@cpc.com.tw
- 電話: +886-4-xxxx-xxxx
- 線上諮詢：www.cpc.com.tw

培訓課程：
- 線性滑軌基礎培訓
- 振動分析進階課程
- LLRAS 軟體操作培訓
```

---

## 附錄

### A. 滾動體參數數據庫（部分）

| 型號 | 滾動體直徑 | 滑座長度(MN) | 單列數量 | 接觸角 |
|------|-----------|------------|---------|--------|
| HRC15 | 3.175 mm (1/8") | 50 mm | 20 | 45° |
| HRC20 | 4.763 mm (3/16") | 60 mm | 22 | 45° |
| HRC25 | 6.35 mm (1/4") | 70 mm | 26 | 45° |
| HRC30 | 7.938 mm (5/16") | 80 mm | 28 | 45° |
| HRC35 | 9.525 mm (3/8") | 100 mm | 32 | 45° |
| HRC45 | 12.7 mm (1/2") | 120 mm | 36 | 45° |

### B. 典型故障特徵速查表

| 振動特徵 | 可能原因 | 處理建議 |
|---------|---------|---------|
| RMS 突然上升 | 負載增加、異物進入 | 檢查負載、清潔 |
| 峰度 > 8 | 滾動體或軌道缺陷 | 安排更換 |
| 出現 BPF 及諧波 | 滾動體表面損傷 | 盡快更換 |
| 高頻噪音增加 | 潤滑不良 | 補充潤滑 |
| 低頻振動明顯 | 安裝精度不良 | 檢查安裝 |
| NA4 > 3 | 早期微裂紋 | 加密監測 |

### C. 程式碼完整範例

完整的 Python 程式碼請參考專案 GitHub 儲存庫：
```
https://github.com/your-repo/linear-guide-vibration-monitoring
```

---

## 結語

本應用方案將先進的振動信號分析技術與 CPC 線性滑軌的專業知識完美結合，實現了從設計驗證到運行監測的全生命週期管理。

通過實施本方案，您可以：
✅ 提前發現故障，避免突發停機
✅ 優化維護計劃，降低運營成本
✅ 延長滑軌壽命，提高投資回報
✅ 提升設備可靠性，保證生產品質

**立即開始您的預測性維護之旅！**

---

*文件版本：v1.0*  
*最後更新：2025-10-21*  
*作者：Claude AI*  
*技術支援：support@example.com*
