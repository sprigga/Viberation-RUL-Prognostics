# IEEE PHM 2012 Data Challenge - Algorithm Computation Purposes and Goals

## Primary Objective
The main goal of the IEEE PHM 2012 Data Challenge was the **estimation of the Remaining Useful Life (RUL) of bearings**. This is a critical problem since most failures of rotating machines are related to bearings, strongly affecting availability, security, and cost-effectiveness of mechanical systems and equipment in industries such as power and transportation.

## Main Purposes of the Challenge
1. **Prognostics of bearings' life duration**: Develop algorithms to accurately estimate how much operational life remains in a bearing before failure

2. **Bearing fault detection and diagnostic**: Identify and diagnose faults in bearings during their operational life

3. **Development of robust prognostic models**: Create models that can work across different operating conditions and bearing degradation patterns

## Specific Goals for Algorithm Development

### 1. RUL Estimation Task
- Participants were provided with 6 run-to-failure datasets (Learning Set) to build their prognostics models
- Required to estimate accurately the RUL of 11 remaining bearings (Test Set)
- Monitoring data was truncated so participants had to predict the remaining life based on incomplete data
- No assumption was given about the type of failure that would occur

### 2. Data Processing Goals
- Process vibration and temperature signals gathered at specific sampling rates:
  - Vibration signals: 25.6 kHz sampling frequency, with 2560 samples recorded every 10 seconds
  - Temperature signals: 10 Hz sampling frequency, with 600 samples recorded every minute

### 3. Cross-Condition Performance
- Handle data from 3 different operating conditions:
  - Condition 1: 1800 rpm and 4000 N
  - Condition 2: 1650 rpm and 4200 N
  - Condition 3: 1500 rpm and 5000 N

## Algorithm Performance Requirements

### Scoring Criteria
The algorithms were evaluated based on:

1. **RUL Estimation Accuracy**: Converting RUL results into percentage errors of predictions
   - Formula: %Eri = 100 × (ActRULi - RULi) / ActRULi
   - Where ActRULi is the actual remaining useful life and RULi is the estimated remaining useful life

2. **Asymmetric Error Penalty**: Underestimates and overestimates were not considered equally:
   - Underestimation (RUL estimate < actual RUL) carries more severe penalties (early removal of equipment, safety risks)
   - Overestimation (RUL estimate > actual RUL) has less severe but still significant penalties (potential equipment failure, safety issues)

3. **Scoring Function**:
   - For underestimation: Ai = exp(-ln(0.5) × (Eri/5))
   - For overestimation: Ai = exp(-ln(0.5) × (Eri/20))
   - Final score: Average of all experiment scores

### Performance Targets
The actual RUL values to be estimated for the test bearings were:
- Bearing1_3: 5730 s
- Bearing1_4: 339 s
- Bearing1_5: 1610 s
- Bearing1_6: 1460 s
- Bearing1_7: 7570 s
- Bearing2_3: 7530 s
- Bearing2_4: 1390 s
- Bearing2_5: 3090 s
- Bearing2_6: 1290 s
- Bearing2_7: 580 s
- Bearing3_3: 820 s

## Technical Challenges for Algorithm Development

1. **Small Training Dataset**: The challenge datasets were characterized by a small amount of training data
2. **High Variability**: Wide spread of life duration of bearings (from 1h to 7h)
3. **Complex Degradation Patterns**: Bearings showed very different behaviors leading to different experiment durations
4. **Multi-component Failure**: Each bearing could contain almost all types of defects (balls, rings, and cage), making frequency signature-based detection difficult
5. **Real-world Conditions**: Theoretical models (L10, BPFI, BPFE, etc.) did not match experimental observations

## Data Structure Requirements
- Process ASCII files named "acc_xxxxx.csv" for vibration data
- Process ASCII files named "temp_xxxxx.csv" for temperature data
- Handle multi-column data arrangement: Hour, Minute, Second, Microsecond, Horizontal Accelerometer, Vertical Accelerometer for vibration data
- Handle temperature data with time stamps and RTD sensor measurements

The challenge aimed to develop robust prognostic algorithms that could accurately predict bearing failure times across varying operating conditions, handling the inherent uncertainty and variability in bearing degradation patterns while optimizing for both safety and operational efficiency.