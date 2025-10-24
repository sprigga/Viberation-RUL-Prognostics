# PHM 2012 數據整合到前端系統

## ✅ 完成項目總結

### 第二個任務：將訓練和測試數據整合到 Frontend

已成功將 PHM IEEE 2012 Challenge 的訓練數據和測試數據整合到現有的振動分析系統前端，實現了完整的數據上傳、視覺化和分析功能。

---

## 📁 新增檔案結構

```
vibration_signals/
├── backend/
│   ├── phm_models.py           # PHM 數據庫模型
│   ├── phm_processor.py        # PHM 數據處理器
│   └── database.py             # 更新：包含 PHM 模型初始化
├── frontend/src/views/
│   ├── PHMTraining.vue         # 訓練數據視覺化頁面
│   └── PHMTesting.vue          # 測試數據上傳與分析頁面
├── frontend/src/router/
│   └── index.js                # 更新：新增 PHM 路由
├── frontend/src/
│   └── App.vue                 # 更新：新增 PHM 菜單
├── phm_analysis_results/       # 訓練數據分析結果
│   ├── summary.json
│   ├── training_data_summary.csv
│   ├── vibration_statistics.csv
│   ├── data_overview.png
│   ├── vibration_trends.png
│   ├── kurtosis_trends.png
│   └── TRAINING_DATA_ANALYSIS_REPORT.md
├── run_backend.py              # 簡化的 Backend 啟動腳本
└── analyze_training_data.py    # 訓練數據分析腳本
```

---

## 🚀 啟動系統

### 1. 啟動 Backend API

```bash
cd /home/ubuntu/vibration_signals
uv run python run_backend.py
```

Backend 將運行在 `http://localhost:8000`

**測試 API:**
```bash
# 健康檢查
curl http://localhost:8000/

# 獲取訓練數據摘要
curl http://localhost:8000/api/phm/training-summary

# 獲取分析數據
curl http://localhost:8000/api/phm/analysis-data
```

### 2. 啟動 Frontend

```bash
cd frontend
npm install  # 首次運行
npm run dev
```

Frontend 將運行在 `http://localhost:5173`

---

## 🎯 功能特性

### 一、訓練數據視覺化頁面 (`/phm-training`)

**功能：**
- ✅ 顯示 6 個訓練軸承的完整摘要表格
- ✅ 操作條件分類（Condition 1/2/3）
- ✅ 互動式振動趨勢圖表（水平/垂直 RMS）
- ✅ 峰度趨勢分析（故障預警指標）
- ✅ 軸承選擇器（動態切換查看不同軸承）
- ✅ 關鍵發現和數據說明

**數據來源：**
- 從 `phm_analysis_results/` 讀取預處理的分析結果
- 包含 300 個採樣點的時間序列數據

**圖表特性：**
- 使用 Chart.js 繪製
- RMS 趨勢線（水平 vs 垂直）
- 峰度趨勢（含正常閾值線 ≈3）
- RUL 標記線

### 二、測試數據上傳與分析頁面 (`/phm-testing`)

**功能：**
- ✅ CSV 文件上傳（支持 PHM 格式）
- ✅ 實時特徵提取（RMS, 峰值, 峰度）
- ✅ RUL 預測（基線模型）
- ✅ 健康狀態評估
- ✅ 已上傳數據歷史記錄

**操作流程：**
1. 輸入軸承名稱（例如：Bearing1_3）
2. 上傳 CSV 文件（PHM 格式）
3. 系統自動分析並顯示特徵
4. 點擊「預測 RUL」獲取壽命預測
5. 查看信心度和健康狀態

**RUL 預測邏輯：**
- 基於峰度的簡單基線模型
- 峰度 > 10 → RUL = 500 分鐘（嚴重異常）
- 峰度 > 5 → RUL = 2000 分鐘（中度異常）
- 峰度 ≤ 5 → RUL = 5000 分鐘（正常）

### 三、數據庫模型

**PHMBearing** - 訓練集軸承信息
- bearing_name, condition, load_N, speed_rpm
- actual_RUL_min, num_files

**PHMTestData** - 測試數據記錄
- bearing_name, file_index, time_min
- horiz_rms, vert_rms
- horiz_peak, vert_peak
- horiz_kurtosis, vert_kurtosis

**PHMPrediction** - RUL 預測結果
- bearing_name, predicted_RUL_min
- actual_RUL_min, prediction_error
- model_type, confidence, features

---

## 📊 API 端點

### PHM 訓練數據

**GET `/api/phm/training-summary`**
- 返回 6 個訓練軸承的摘要信息
- 包含操作條件、RUL、文件數等

**GET `/api/phm/analysis-data`**
- 返回完整的分析數據
- 包含 summary.json 和 vibration_statistics.csv

### PHM 測試數據

**POST `/api/phm/upload-bearing-data`**
- 上傳並分析單個 CSV 文件
- 參數：`file` (CSV), `bearing_name` (字符串)
- 返回：分析結果（RMS, 峰度等）

**GET `/api/phm/test-data/{bearing_name}`**
- 獲取特定軸承的所有測試數據
- 返回：時間序列數據

### RUL 預測

**POST `/api/phm/predict-rul`**
- 預測軸承剩餘使用壽命
- 參數：`bearing_name`, `model_type` (默認 "baseline")
- 返回：predicted_RUL_min, confidence, features

---

## 🎨 前端頁面展示

### 訓練數據頁面特性：

1. **摘要表格**
   - 軸承編號、操作條件（顏色標籤）
   - 負載、轉速、RUL
   - 數據文件數、總時長
   - 「查看詳情」按鈕

2. **振動趨勢圖**
   - 軸承選擇下拉菜單
   - 雙線圖：水平 RMS vs 垂直 RMS
   - X軸：時間（分鐘）
   - Y軸：RMS 值

3. **峰度趨勢圖**
   - 雙線圖：水平峰度 vs 垂直峰度
   - 正常閾值參考線（≈3）
   - 清晰顯示異常峰值

4. **數據說明卡片**
   - 數據集信息
   - 關鍵發現（4 條重點）
   - 峰度正常值/異常值說明

### 測試數據頁面特性：

1. **上傳區域**
   - 軸承名稱輸入框
   - 拖放式文件上傳
   - 只接受 CSV 格式

2. **分析結果卡片**
   - 統計數據顯示（RMS, 峰度）
   - 健康狀態標籤（正常/輕微異常/嚴重異常）
   - 「預測 RUL」按鈕

3. **RUL 預測結果卡片**
   - 預測 RUL（大數字顯示）
   - 信心度進度條
   - 狀態標籤（綠/黃/紅）
   - 特徵數據（JSON 格式）

4. **已上傳數據表格**
   - 歷史記錄列表
   - 快速預測按鈕

---

## 📈 數據分析結果

### 訓練集統計：

| 軸承 | 操作條件 | 負載 (N) | 轉速 (RPM) | RUL (分鐘) | 文件數 |
|------|---------|---------|-----------|-----------|--------|
| Bearing1_1 | Cond 1 | 4000 | 1800 | **28020** | 2803 |
| Bearing1_2 | Cond 1 | 4200 | 1650 | 8700 | 871 |
| Bearing2_1 | Cond 2 | 4200 | 1650 | 9100 | 911 |
| Bearing2_2 | Cond 2 | 4000 | 1800 | 7960 | 797 |
| Bearing3_1 | Cond 3 | **5000** | 1500 | **5730** | 515 |
| Bearing3_2 | Cond 3 | 4200 | 1650 | 16430 | 1637 |

### 關鍵發現：

1. **峰度是最可靠的早期故障指標**
   - 在多數案例中提供 1000-3000 分鐘預警時間

2. **垂直振動更早顯示退化**
   - 垂直方向通常比水平方向更敏感

3. **高負載縮短壽命**
   - Bearing3_1 (5000N) 僅 5730 分鐘 RUL

4. **數據豐富性**
   - Bearing1_1 最多數據 (2803 files)
   - 適合作為主要訓練樣本

---

## 🔧 技術細節

### Backend 技術棧：
- **FastAPI** - RESTful API 框架
- **SQLAlchemy** - ORM 數據庫操作
- **Pandas** - 數據處理
- **NumPy** - 數值計算
- **SciPy** - 統計分析

### Frontend 技術棧：
- **Vue 3** - 前端框架（Composition API）
- **Element Plus** - UI 組件庫
- **Chart.js** - 圖表繪製
- **Axios** - HTTP 請求

### 數據格式：

**PHM CSV 格式：**
```
hour, minute, second, microsecond, horiz_vibration, vert_vibration
9, 39, 39, 65664, 0.552, -0.146
9, 39, 39, 65703, 0.501, -0.48
...
```

**API Response Example:**
```json
{
  "id": 1,
  "bearing_name": "Bearing1_3",
  "analysis": {
    "horiz_rms": 0.452,
    "vert_rms": 0.381,
    "horiz_kurtosis": 3.21,
    "vert_kurtosis": 2.98
  }
}
```

---

## 🎯 使用案例

### 案例 1：查看訓練數據趨勢

1. 訪問 `http://localhost:5173/phm-training`
2. 查看摘要表格，了解各軸承基本信息
3. 點擊「查看詳情」或使用下拉菜單選擇軸承
4. 觀察 RMS 和峰度趨勢圖
5. 識別故障模式（漸進式 vs 突發式）

### 案例 2：上傳測試數據並預測 RUL

1. 訪問 `http://localhost:5173/phm-testing`
2. 輸入軸承名稱（如 "Test_Bearing_1"）
3. 上傳 PHM 格式的 CSV 文件
4. 查看分析結果（RMS, 峰度）
5. 點擊「預測 RUL」
6. 查看預測壽命和健康狀態

### 案例 3：批量分析多個測試文件

1. 依次上傳多個 CSV 文件（不同軸承）
2. 在「已上傳數據」表格中查看所有記錄
3. 使用「快速預測」按鈕批量預測
4. 比較不同軸承的健康狀態

---

## 📝 下一步改進建議

### 1. 模型優化
- [ ] 實現更複雜的 RUL 預測模型（機器學習）
- [ ] 增加特徵工程（頻域、小波特徵）
- [ ] 訓練基於歷史數據的迴歸模型

### 2. 功能擴展
- [ ] 批量上傳多個文件
- [ ] 導出分析報告（PDF）
- [ ] 實時監控儀表板
- [ ] 警報和通知系統

### 3. UI/UX 改進
- [ ] 添加更多圖表類型（散點圖、熱力圖）
- [ ] 響應式設計優化
- [ ] 深色模式支持
- [ ] 多語言支持

### 4. 性能優化
- [ ] 大文件上傳進度條
- [ ] 數據緩存機制
- [ ] 異步處理長時間任務
- [ ] WebSocket 實時更新

---

## ✅ 任務完成檢查表

- [x] 訓練數據整理、分類並生成表格
- [x] 繪製訓練數據分布和趨勢圖表
- [x] 創建 PHM 數據庫模型
- [x] 實現 PHM 數據處理器
- [x] 開發 PHM API 端點
- [x] 創建訓練數據視覺化頁面
- [x] 創建測試數據上傳頁面
- [x] 整合圖表組件顯示振動趨勢
- [x] 實現 RUL 預測功能
- [x] 測試完整功能流程
- [x] 生成完整文檔

---

## 🎉 總結

成功完成了 PHM 2012 數據到前端系統的完整整合！

**關鍵成果：**
1. **完整的數據分析** - 6 個訓練軸承的深度分析
2. **互動式視覺化** - 振動趨勢和峰度圖表
3. **測試數據上傳** - 支持 PHM CSV 格式
4. **RUL 預測** - 基線模型實現
5. **友好的用戶界面** - 使用 Element Plus 組件

**技術亮點：**
- RESTful API 設計
- Vue 3 Composition API
- Chart.js 動態圖表
- SQLAlchemy ORM
- 完整的錯誤處理

**文檔齊全：**
- API 文檔
- 使用指南
- 分析報告
- 技術細節

系統已經可以用於 PHM 數據的上傳、分析和視覺化！
