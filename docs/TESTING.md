# PHM IEEE 2012 Data Challenge - Test Set Structure Analysis

## Test Dataset Structure

### Directory Structure
```
phm-ieee-2012-data-challenge-dataset/
├── Test_set/
│   ├── Bearing1_3/
│   ├── Bearing1_4/
│   ├── Bearing1_5/
│   ├── Bearing1_6/
│   ├── Bearing1_7/
│   ├── Bearing2_3/
│   ├── Bearing2_4/
│   ├── Bearing2_5/
│   ├── Bearing2_6/
│   ├── Bearing2_7/
│   └── Bearing3_3/
├── Full_Test_Set/
│   ├── Bearing1_3/
│   ├── Bearing1_4/
│   ├── Bearing1_5/
│   ├── Bearing1_6/
│   ├── Bearing1_7/
│   ├── Bearing2_3/
│   ├── Bearing2_4/
│   ├── Bearing2_5/
│   ├── Bearing2_6/
│   ├── Bearing2_7/
│   └── Bearing3_3/
```

### Test Bearing Naming Convention
- **BearingX_Y**: Where X represents the test condition (1, 2, or 3) and Y is the bearing instance for testing
- Each bearing directory contains sequential accelerometer data files with the naming convention: `acc_XXXXX.csv`
- The test bearings continue the numbering from where the Learning_set ended

### Test Data File Characteristics
- **File Format**: CSV files containing accelerometer measurements (same format as training data)
- **Naming Convention**: `acc_XXXXX.csv` (e.g., `acc_00001.csv`, `acc_00002.csv`, etc.)
- **Data Content**: Each CSV file contains 2,560 data points with the format:
  - 6 columns: likely timestamp, x-coordinate, y-coordinate, time-related values, and two accelerometer readings
  - Example data structure: `8,33,1,3.7816e+05,0.092,0.044`
- **File Size**: Approximately 75-81KB per file
- **Sequential Order**: Files are numbered sequentially representing continuous monitoring

### Number of Files per Test Bearing
- Each test bearing directory contains hundreds to thousands of files:
  - Test_set: Number of files varies per bearing (e.g., Bearing1_3: 1,802 files, Bearing2_5: 2,337 files)
  - Full_Test_Set: More complete data sets (e.g., Bearing1_3: 2,375 files)
- The different file counts suggest different monitoring periods or conditions for each bearing

### Data Format in Test Set
Based on the sample data from `acc_00001.csv` in the Test_set:
- The data format is consistent with the training set (Learning_set), maintaining the same 6-column structure
- The values represent accelerometer measurements along different axes
- Time-related information is preserved in the first columns

### Test Set Characteristics
- Contains 11 additional bearings beyond the training set
- Used for evaluating algorithms developed using the training set
- Each bearing was operated under the same three conditions as the training set (Bearing1, Bearing2, Bearing3)
- The naming convention suggests that bearings 3-7 are test bearings (BearingX_3 to BearingX_7) while the training set had bearings 1-2 (BearingX_1 to BearingX_2)
- The Full_Test_Set is likely a more complete version of the Test_set with additional data points

### Relationship to Current Project
In the context of your vibration_signals project:
- The test set can be used to validate models trained on the Learning_set
- Provides independent data for evaluating bearing fault detection algorithms
- Can be used to test the robustness of your diagnostic algorithms
- Enables objective comparison of different analysis approaches
- The Full_Test_Set provides a more comprehensive evaluation with potentially more complete bearing degradation data

The test dataset serves as the evaluation component for developing and validating predictive maintenance algorithms for linear guide systems, ensuring that models generalize well to unseen bearing data.