# PHM 2012 系統快速啟動指南

## 🚀 3 分鐘快速啟動

### 步驟 1：啟動 Backend（終端 1）

```bash
cd /home/ubuntu/vibration_signals
uv run python run_backend.py
```

看到以下輸出表示成功：
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步驟 2：啟動 Frontend（終端 2）

```bash
cd /home/ubuntu/vibration_signals/frontend
npm run dev
```

看到以下輸出：
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### 步驟 3：訪問網頁

打開瀏覽器訪問：`http://localhost:5173`

---

## 📊 查看訓練數據

1. 點擊左側菜單 **"PHM 2012"** → **"訓練數據"**
2. 查看 6 個訓練軸承的摘要表格
3. 點擊「查看詳情」查看振動趨勢圖表
4. 使用下拉菜單切換不同軸承

---

## 🔬 測試數據分析

1. 點擊左側菜單 **"PHM 2012"** → **"測試分析"**
2. 輸入軸承名稱（如 "Bearing1_3"）
3. 上傳 CSV 文件（從 `phm-ieee-2012-data-challenge-dataset/Test_set/` 目錄）
4. 查看分析結果
5. 點擊「預測 RUL」

---

## 🧪 測試 API（可選）

```bash
# 健康檢查
curl http://localhost:8000/

# 獲取訓練摘要
curl http://localhost:8000/api/phm/training-summary

# 獲取分析數據
curl http://localhost:8000/api/phm/analysis-data
```

---

## 📁 測試數據位置

PHM 測試數據 CSV 文件位於：
```
phm-ieee-2012-data-challenge-dataset/Test_set/Bearing1_3/acc_00001.csv
phm-ieee-2012-data-challenge-dataset/Test_set/Bearing1_4/acc_00001.csv
...
```

選擇任意 CSV 文件上傳到系統進行測試！

---

## ❓ 常見問題

**Q: Backend 啟動失敗？**
A: 確保在專案根目錄執行，並檢查 8000 端口是否被佔用

**Q: Frontend 無法連接 Backend？**
A: 確認 Backend 運行在 http://localhost:8000

**Q: 圖表不顯示？**
A: 檢查 `phm_analysis_results/` 目錄是否存在分析結果文件

**Q: 上傳文件格式錯誤？**
A: 確保使用 PHM 格式的 CSV 文件（6 列：時間戳 + 水平/垂直振動）

---

## 📚 完整文檔

詳細說明請查看：[PHM_INTEGRATION_README.md](PHM_INTEGRATION_README.md)

訓練數據分析報告：[phm_analysis_results/TRAINING_DATA_ANALYSIS_REPORT.md](phm_analysis_results/TRAINING_DATA_ANALYSIS_REPORT.md)
