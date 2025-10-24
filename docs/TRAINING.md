# PHM IEEE 2012 Data Challenge - Training Set Structure Analysis

## Dataset Overview
The PHM IEEE 2012 Data Challenge dataset contains vibration data from rolling bearings under different operating conditions. It includes:
- **Learning_set** (Training Set): 6 bearings operated under three different conditions
- **Test_set**: 11 additional bearings
- **Full_Test_Set**: Complete test set

## Training Dataset Structure

### Directory Structure
```
phm-ieee-2012-data-challenge-dataset/
├── Learning_set/
│   ├── Bearing1_1/
│   ├── Bearing1_2/
│   ├── Bearing2_1/
│   ├── Bearing2_2/
│   ├── Bearing3_1/
│   └── Bearing3_2/
├── Test_set/
└── Full_Test_Set/
```

### Bearing Naming Convention
- **BearingX_Y**: Where X represents the test condition (1, 2, or 3) and Y is the bearing instance
- Each bearing directory contains sequential accelerometer data files with the naming convention: `acc_XXXXX.csv`

### Data File Characteristics
- **File Format**: CSV files containing accelerometer measurements
- **Naming Convention**: `acc_XXXXX.csv` (e.g., `acc_00001.csv`, `acc_00002.csv`, etc.)
- **Data Content**: Each CSV file contains 2,560 data points with the format:
  - 6 columns: likely timestamp, x-coordinate, y-coordinate, time-related values, and two accelerometer readings
  - Example data structure: `9,39,39,65664,0.552,-0.146`
- **File Size**: Approximately 75-81KB per file
- **Sequential Order**: Files are numbered sequentially (00001.csv to the final measurement file) representing continuous monitoring over the bearing's operational lifetime

### Number of Files per Bearing
- Each bearing directory contains hundreds of files representing continuous vibration data collection over time
- Example: Bearing1_1 has 2,803 files, indicating long-term monitoring
- The sequential numbering represents the chronological order of data collection

### Data Format Analysis
Based on the sample data from `acc_00001.csv`:
- The data appears to be timestamped vibration measurements from accelerometers
- Likely contains both X-axis and Y-axis accelerometer readings
- Each file represents a snapshot of vibration data from the bearing at a specific time
- The first few columns likely represent time/synchronization data
- The last two columns represent accelerometer measurements along two axes

### Test Conditions
The dataset includes three different test conditions (Bearing1, Bearing2, Bearing3), each with multiple bearing instances:
- Different operating conditions to simulate various real-world scenarios
- Allows for robust model training across diverse operational conditions
- Each bearing was run until failure, providing degradation data

### Relationship to Current Project
In the context of your vibration_signals project:
- The dataset can be used to train models for bearing health condition assessment
- Provides real-world degradation patterns from actual bearing failures
- The analysis.py file in your project shows sophisticated analysis methods that would benefit from this training data
- The bearing fault frequency calculations in your code can be validated against this dataset
- Provides baseline data for creating health score algorithms and fault detection

This dataset is ideal for developing and testing predictive maintenance algorithms, bearing fault detection systems, and degradation modeling approaches for linear guide systems.