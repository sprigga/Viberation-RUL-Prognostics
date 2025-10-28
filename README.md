# 🔧 Vibration Signal Analysis System

Modern web application integrating Vue 3 frontend with FastAPI backend, designed for vibration signal analysis and fault diagnosis in rotating machinery. The system integrates IEEE PHM 2012 dataset for bearing health monitoring research.

## 🎯 Project Overview

This system provides an integrated platform for:
- **Vibration Signal Analysis**: Advanced signal processing for rotating machinery
- **Advanced Signal Processing**: Time, frequency, and time-frequency domain feature extraction
- **PHM Database Integration**: Complete IEEE PHM 2012 bearing dataset analysis capabilities
- **Real-time Health Monitoring**: Interactive dashboard with live analysis and visualization
- **Predictive Maintenance**: Health assessment and remaining useful life (RUL) prediction
- **Modern Web Interface**: Vue 3 + Element Plus frontend with ECharts visualization

## 🏗️ System Architecture

### Backend (FastAPI + Python)
- **API Server**: `backend/main.py` - Comprehensive RESTful API (1300+ lines)
- **Signal Processing Modules**: Integrated time domain, frequency domain, and envelope analysis
- **Database Layer**: SQLite databases for PHM data and temperature monitoring
- **Advanced Algorithms**: Hilbert transform, STFT, CWT, and filter-based features

### Frontend (Vue 3 + Element Plus)
- **Dashboard**: IEEE PHM 2012 experiment overview and real-time time-domain analysis
- **PHM Database**: Complete bearing dataset browser with statistical analysis
- **Algorithms**: Interactive algorithm demonstration and parameter tuning
- **Analysis Tools**: Interactive vibration analysis and RUL prediction

### Core Analysis Modules
- `timedomain.py`: Time domain features (RMS, kurtosis, crest factor, etc.)
- `frequencydomain.py`: FFT analysis and spectral features
- `timefrequency.py`: Time-frequency analysis (STFT, CWT, spectrogram)
- `filterprocess.py`: Advanced filtering and higher-order statistics (NA4, FM4, M6A, M8A, ER)
- `hilberttransform.py`: Hilbert transform and envelope analysis
- `harmonic_sildband_table.py`: Harmonic and sideband energy analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- UV package manager (recommended)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd vibration_signals
```

### 2. Start Backend
The main backend application is `backend/main.py`.

```bash
# Using UV (recommended)
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload

# Or using traditional Python
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
Open your browser and navigate to: `http://localhost:5173`

The backend API will be running on: `http://localhost:8081`

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d
```
For development, you can use `docker-compose.dev.yml`:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Individual Services
```bash
# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend
```

## 📊 IEEE PHM 2012 Integration

### Dataset Overview
- **Training Data**: 6 complete run-to-failure experiments
- **Test Data**: 11 truncated monitoring datasets
- **Sampling**: 25.6 kHz vibration, 0.1 Hz temperature
- **Sensors**: Dual accelerometers (horizontal/vertical), RTD temperature sensor

### Operating Conditions
| Condition | Speed (RPM) | Load (N) | Bearings |
|-----------|-------------|----------|----------|
| 1 | 1800 | 4000 | Bearing1_1, Bearing1_2 |
| 2 | 1650 | 4200 | Bearing2_1, Bearing2_2 |
| 3 | 1500 | 5000 | Bearing3_1, Bearing3_2 |

### Key Features
- **Real Degradation**: Natural bearing deterioration without artificial defects
- **Multiple Failure Modes**: Ball, inner race, outer race, and cage failures
- **High Variability**: Bearing lifetimes range from 1 to 7.47 hours
- **Challenge Scoring**: Asymmetric scoring function for early/late predictions

## 🔧 API Endpoints

### System Health
- `GET /` - System health check and API information

### PHM Database Integration
- `GET /api/phm/training-summary` - PHM training data summary
- `GET /api/phm/analysis-data` - PHM analysis results from preprocessed data
- `GET /api/phm/database/bearings` - List all bearings in PHM database
- `GET /api/phm/database/bearing/{bearing_name}` - Get specific bearing information
- `GET /api/phm/database/bearing/{bearing_name}/files` - Get bearing file list (paginated)
- `GET /api/phm/database/bearing/{bearing_name}/measurements` - Get bearing measurements
- `GET /api/phm/database/bearing/{bearing_name}/file/{file_number}/data` - Get complete data for a specific file
- `GET /api/phm/database/bearing/{bearing_name}/statistics` - Get bearing statistics
- `GET /api/phm/database/bearing/{bearing_name}/anomalies` - Search for anomalous vibration data
- `POST /api/phm/predict-rul` - Predict remaining useful life

### Algorithm Analysis Endpoints
- `GET /api/algorithms/time-domain/{bearing_name}/{file_number}` - Time domain features
- `GET /api/algorithms/time-domain-trend/{bearing_name}` - Time domain trend analysis
- `GET /api/algorithms/frequency-domain/{bearing_name}/{file_number}` - Frequency domain analysis
- `GET /api/algorithms/frequency-fft/{bearing_name}/{file_number}` - Low-frequency FFT features
- `GET /api/algorithms/frequency-tsa/{bearing_name}/{file_number}` - TSA high-frequency FFT
- `GET /api/algorithms/envelope/{bearing_name}/{file_number}` - Envelope spectrum analysis
- `GET /api/algorithms/hilbert/{bearing_name}/{file_number}` - Hilbert transform features
- `GET /api/algorithms/filter-features/{bearing_name}/{file_number}` - Advanced filter features (NA4, FM4, M6A, M8A, ER)
- `GET /api/algorithms/filter-trend/{bearing_name}` - Filter features trend analysis
- `GET /api/algorithms/higher-order/{bearing_name}/{file_number}` - Higher-order statistics

### Time-Frequency Analysis
- `GET /api/algorithms/stft/{bearing_name}/{file_number}` - Short-Time Fourier Transform
- `GET /api/algorithms/cwt/{bearing_name}/{file_number}` - Continuous Wavelet Transform
- `GET /api/algorithms/spectrogram/{bearing_name}/{file_number}` - Spectrogram analysis



## 📁 Project Structure

```
vibration_signals/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── models.py           # Database models
│   ├── phm_*.py           # PHM-specific processors
│   └── Dockerfile         # Backend container
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── views/         # Vue components
│   │   ├── stores/        # Pinia state management
│   │   └── router/        # Vue router
│   └── Dockerfile         # Frontend container
├── docs/                   # Documentation
├── phm_analysis_results/   # PHM analysis outputs
├── scripts/                # Utility scripts
├── *.py                   # Legacy analysis modules
├── docker-compose.yml     # Multi-service deployment
└── pyproject.toml         # Python dependencies
```

## 🧪 Testing and Development

### Backend Testing
```bash
# Run API tests
python test_timefrequency_api.py

# Test configuration
python backend/test_config.py
```

### Frontend Development
```bash
cd frontend
npm run dev    # Development server
npm run build  # Production build
npm run preview # Preview build
```

### Data Import
```bash
# Import PHM training data
python scripts/import_phm_data.py

# Query PHM database
python scripts/query_phm_data.py
```

## 📈 Analysis Workflow

1. **Data Upload**: Upload CSV files through web interface
2. **Preprocessing**: Automatic signal conditioning and validation
3. **Feature Extraction**: Multi-domain feature computation
4. **Health Assessment**: ML-based health score calculation
5. **RUL Prediction**: Prognostics algorithm application
6. **Visualization**: Interactive charts and trend analysis

## 🔍 Feature Extraction

### Time Domain Features
- Statistical moments (mean, std, skewness, kurtosis)
- Amplitude features (peak, RMS, crest factor)
- Energy-based indicators

### Frequency Domain Features
- FFT-based spectral analysis
- Characteristic frequency detection
- Frequency band energy ratios

### Advanced Features
- Wavelet coefficients and energy distribution
- Hilbert envelope analysis
- Higher-order spectral moments
- Harmonic and sideband energy tracking

## 🛠️ Configuration

### Environment Variables
The application is configured using environment variables. See `docker-compose.yml` for examples.

- `DATABASE_URL`: Path to the main SQLite database.
- `PHM_DATABASE_PATH`: Path to the PHM data SQLite database.
- `PHM_TEMPERATURE_DATABASE_PATH`: Path to the PHM temperature data SQLite database.
- `VITE_API_URL`: The URL of the backend API for the frontend to connect to.

Default values are set in the `docker-compose.yml` and `backend/config.py`.

### Backend Configuration
See `backend/CONFIG_README.md` for detailed configuration options.

## 📚 Algorithm Documentation

### Time Domain Analysis
Time domain features are directly extracted from the raw vibration signal without conversion to other domains. These features provide overall health assessment:

- **Peak**: Maximum amplitude value in the signal
- **RMS (Root Mean Square)**: Represents the overall vibration energy
- **Kurtosis**: Measures the peakedness of the signal distribution
- **Crest Factor**: Ratio of peak value to RMS value
- **Average**: Mean value of the signal

### Frequency Domain Analysis
Frequency domain analysis transforms the time-domain signal into frequency components using FFT:

- **Low-Frequency FM0**: Normalized peak value in low-frequency range
- **High-Frequency FM0**: Normalized peak value in high-frequency range (using TSA)
- **TSA (Time Synchronous Averaging)**: Averages signal over synchronous periods to improve signal-to-noise ratio

### Time-Frequency Analysis
Time-frequency analysis provides joint time-frequency representation:

- **STFT (Short-Time Fourier Transform)**: Localized frequency analysis in time windows
- **CWT (Continuous Wavelet Transform)**: Multi-scale analysis using wavelet functions
- **Spectrogram**: Time-frequency energy distribution
- **NP4**: Normalized fourth-order moment of time-frequency coefficients

### Envelope Analysis & Hilbert Transform
Envelope analysis extracts amplitude modulation information:

- **Hilbert Transform**: Computes analytical signal to extract envelope and instantaneous frequency
- **Envelope Spectrum**: FFT of the envelope signal, useful for detecting periodic impulses
- **NB4**: Normalized bispectrum fourth-order statistic
- **ER (Energy Ratio)**: Ratio of specific frequency band energy to total energy

### Advanced Filter Features
Higher-order statistics for early fault detection:

- **NA4**: Normalized fourth-order moment with segment-based normalization
- **FM4**: Fourth-order moment statistic
- **M6A**: Sixth-order moment statistic
- **M8A**: Eighth-order moment statistic
- **ER**: Energy ratio between filtered and original signals

## 📊 System Architecture Diagrams

### UML Class Diagram
```
+----------------------------------------+
|              VibrationSystem           |
+----------------------------------------+
| - timedomain: TimeDomain               |
| - frequencydomain: FrequencyDomain     |
| - filterprocess: FilterProcess         |
| - hilberttransform: HilbertTransform   |
+----------------------------------------+
| + analyze_vibration()                  |
| + extract_time_features()              |
| + extract_frequency_features()         |
| + extract_envelope_features()          |
| + calculate_advanced_stats()           |
+----------------------------------------+

+------------------+       +------------------------+
|   TimeDomain     |       |   FrequencyDomain      |
+------------------+       +------------------------+
| - peak()         |       | - fft_process()        |
| - avg()          |       | - ifft_process()       |
| - rms()          |       | - fft_fm0_si()         |
| - cf()           |       | - tsa_fft_fm0_slf()    |
| - kurt()         |       +------------------------+
| - eo()           |
+------------------+

+------------------+       +------------------------+
| FilterProcess    |       |   HilbertTransform     |
+------------------+       +------------------------+
| - NA4()          |       | - calculate_nb4()      |
| - NA4S()         |       | - hilbert_transform()  |
| - FM4()          |       | - analyze_signal()     |
| - M6A()          |       +------------------------+
| - M8A()          |
| - ER()           |
| - FilterHarmonic()|
| - FilterSideband()|
+------------------+
```

### UML Sequence Diagram
```
User -> Frontend: Select Bearing & File
Frontend -> Backend: API Request for Analysis
Backend -> Database: Query Vibration Data
Database -> Backend: Return Data
Backend -> TimeDomain: Calculate Time Features
TimeDomain -> Backend: Return Time Results
Backend -> FrequencyDomain: Calculate Frequency Features
FrequencyDomain -> Backend: Return Frequency Results
Backend -> FilterProcess: Calculate Advanced Features
FilterProcess -> Backend: Return Advanced Results
Backend -> Frontend: Return Analysis Results
Frontend -> User: Display Analysis Results
```

### Data Flow Diagram
```
+----------------+     +----------------+     +----------------+
| Vibration Data |---->| Preprocessing  |---->| Feature        |
| (Accel. H/V)   |     | (Filtering,    |     | Extraction     |
+----------------+     | Detrending)    |     | Algorithms     |
                       +----------------+     +----------------+
                                                      |
                                                      v
                        +----------------+    +------------------+
                        | Visualization  |<---| Trend Analysis   |
                        | & Dashboard    |    | & RUL Prediction |
                        +----------------+    +------------------+
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Lin Hung Chuan
- Development Team

## 🙏 Acknowledgments

- IEEE PHM Society for the 2012 Data Challenge dataset
- FEMTO-ST Institute for the PRONOSTIA experimental platform
- Industrial partners for real-world validation datasets

---

**Note**: This system is designed for research and industrial applications. Ensure proper validation and testing before deployment in critical systems.