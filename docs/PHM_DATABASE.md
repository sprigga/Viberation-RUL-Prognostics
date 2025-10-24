# PHM IEEE 2012 資料庫說明

## 概述

本專案已將 PHM IEEE 2012 Data Challenge Dataset 的 Learning_set 訓練資料匯入 SQLite 資料庫,方便進行分析與查詢。

## 資料庫位置

```
backend/phm_data.db
```

資料庫大小: 約 1.4 GB

## 資料庫架構

### 表格結構

#### 1. bearings (軸承表)
儲存軸承的基本資訊

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| bearing_id | INTEGER | 主鍵 |
| bearing_name | TEXT | 軸承名稱 (如 Bearing1_1) |
| condition_id | INTEGER | 狀態 ID (可選) |
| description | TEXT | 描述 (可選) |

#### 2. measurement_files (測量檔案表)
儲存每個 CSV 檔案的資訊

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| file_id | INTEGER | 主鍵 |
| bearing_id | INTEGER | 外鍵,關聯到 bearings 表 |
| file_name | TEXT | 檔案名稱 (如 acc_00001.csv) |
| file_number | INTEGER | 檔案編號 |
| record_count | INTEGER | 記錄數量 |

#### 3. measurements (測量資料表)
儲存實際的振動測量資料

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| measurement_id | INTEGER | 主鍵 |
| file_id | INTEGER | 外鍵,關聯到 measurement_files 表 |
| hour | INTEGER | 小時 |
| minute | INTEGER | 分鐘 |
| second | INTEGER | 秒 |
| microsecond | INTEGER | 微秒 |
| horizontal_acceleration | REAL | 水平加速度 |
| vertical_acceleration | REAL | 垂直加速度 |

### 索引

- `idx_measurements_file_id`: 加速測量資料的檔案查詢
- `idx_measurements_time`: 加速時間範圍查詢
- `idx_files_bearing_id`: 加速軸承檔案查詢

## 資料統計

### 總體統計
- 軸承數量: 6
- 檔案總數: 7,534
- 測量記錄總數: 19,287,040

### 各軸承統計

| 軸承名稱 | 檔案數 | 測量記錄數 |
|---------|--------|-----------|
| Bearing1_1 | 2,803 | 7,175,680 |
| Bearing1_2 | 871 | 2,229,760 |
| Bearing2_1 | 911 | 2,332,160 |
| Bearing2_2 | 797 | 2,040,320 |
| Bearing3_1 | 515 | 1,318,400 |
| Bearing3_2 | 1,637 | 4,190,720 |

## 使用方法

### 1. 重新匯入資料

如需重新匯入資料:

```bash
uv run python scripts/import_phm_data.py
```

### 2. 查詢資料

使用查詢工具:

```bash
uv run python scripts/query_phm_data.py
```

### 3. Python 程式碼範例

```python
from scripts.query_phm_data import PHMDataQuery
from pathlib import Path

# 連接資料庫
db_path = Path("backend/phm_data.db")
with PHMDataQuery(str(db_path)) as query:
    # 獲取所有軸承
    bearings = query.get_bearings()

    # 獲取特定軸承的統計資料
    stats = query.get_bearing_stats('Bearing1_1')
    print(f"Files: {stats['file_count']}")
    print(f"Measurements: {stats['measurement_count']}")

    # 獲取測量資料
    df = query.get_measurements('Bearing1_1', file_number=1, limit=100)
    print(df.head())

    # 獲取加速度統計
    acc_stats = query.get_acceleration_stats('Bearing1_1')
    print(acc_stats)

    # 獲取檔案摘要
    file_summary = query.get_file_summary('Bearing1_1')
    print(file_summary.head())
```

### 4. 直接 SQL 查詢

```python
import sqlite3

conn = sqlite3.connect('backend/phm_data.db')
cursor = conn.cursor()

# 查詢特定軸承的所有測量資料
cursor.execute("""
    SELECT m.*, mf.file_name
    FROM measurements m
    JOIN measurement_files mf ON m.file_id = mf.file_id
    JOIN bearings b ON mf.bearing_id = b.bearing_id
    WHERE b.bearing_name = 'Bearing1_1'
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

## 常用查詢範例

### 查詢特定時間範圍的資料

```sql
SELECT *
FROM measurements m
JOIN measurement_files mf ON m.file_id = mf.file_id
JOIN bearings b ON mf.bearing_id = b.bearing_id
WHERE b.bearing_name = 'Bearing1_1'
  AND m.hour = 9
  AND m.minute BETWEEN 40 AND 50
LIMIT 100;
```

### 計算每個檔案的統計值

```sql
SELECT
    mf.file_number,
    COUNT(*) as record_count,
    AVG(m.horizontal_acceleration) as avg_h_acc,
    AVG(m.vertical_acceleration) as avg_v_acc,
    MAX(ABS(m.horizontal_acceleration)) as max_h_acc,
    MAX(ABS(m.vertical_acceleration)) as max_v_acc
FROM measurements m
JOIN measurement_files mf ON m.file_id = mf.file_id
JOIN bearings b ON mf.bearing_id = b.bearing_id
WHERE b.bearing_name = 'Bearing1_1'
GROUP BY mf.file_number
ORDER BY mf.file_number;
```

### 找出異常振動值

```sql
SELECT
    b.bearing_name,
    mf.file_number,
    m.*
FROM measurements m
JOIN measurement_files mf ON m.file_id = mf.file_id
JOIN bearings b ON mf.bearing_id = b.bearing_id
WHERE ABS(m.horizontal_acceleration) > 10
   OR ABS(m.vertical_acceleration) > 10
ORDER BY b.bearing_name, mf.file_number;
```

## 注意事項

1. 資料庫檔案較大 (1.4 GB),查詢時建議:
   - 使用 LIMIT 限制結果數量
   - 利用索引進行查詢優化
   - 針對特定軸承或時間範圍進行查詢

2. 時間格式:
   - 時間資訊分為 hour, minute, second, microsecond 四個欄位
   - 需要組合使用才能獲得完整時間戳記

3. 加速度單位:
   - horizontal_acceleration: 水平方向加速度
   - vertical_acceleration: 垂直方向加速度
   - 單位請參考原始資料集說明文件

## 相關檔案

- 資料匯入腳本: [scripts/import_phm_data.py](../scripts/import_phm_data.py)
- 查詢工具: [scripts/query_phm_data.py](../scripts/query_phm_data.py)
- 原始資料集: `phm-ieee-2012-data-challenge-dataset/Learning_set/`
