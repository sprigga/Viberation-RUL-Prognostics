# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **modern web application** for CPC Linear Guide vibration analysis and fault diagnosis. The system combines:
- **Legacy Python modules**: Original vibration signal processing algorithms (time domain, frequency domain, wavelet, filtering, Hilbert transform)
- **FastAPI backend**: RESTful API for analysis services with SQLite database
- **Vue 3 frontend**: Interactive web interface with real-time visualization
- **Integrated analysis**: Automated health assessment and predictive maintenance

The application enables predictive maintenance by analyzing vibration signals to detect rolling element defects, track wear, preload failures, and installation issues in CPC linear guide systems.

## Running the Application

### Modern Web Application (Recommended)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`

**Docker Compose (Full Stack):**
```bash
docker-compose up
```
Brings up both frontend and backend services.

### Legacy Batch Processing

```bash
python main_code.py
```
- Reads from `root_inputdir` (line 8 of [main_code.py](main_code.py#L8))
- Outputs CSV files to `./excel/` directory
- Use this for batch processing existing data files

### Main Dependencies

**Backend:**
- fastapi==0.104.1, uvicorn==0.24.0
- sqlalchemy==2.0.23
- pandas, numpy, scipy, PyWavelets

**Frontend:**
- Vue 3, Vue Router, Pinia
- Element Plus (UI components)
- Chart.js + vue-chartjs
- Axios (HTTP client)

## Architecture

### Modern Web Application Structure

```
vibration_signals/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints & server
│   ├── database.py         # SQLite configuration
│   ├── models.py           # SQLAlchemy models (GuideSpec, AnalysisResult)
│   ├── analysis.py         # VibrationAnalyzer (integrates legacy modules)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── views/         # Page components
│   │   │   ├── Dashboard.vue          # Health overview & trends
│   │   │   ├── Analysis.vue           # Upload & analyze signals
│   │   │   ├── FrequencyCalculator.vue # BPF/BSF calculator
│   │   │   ├── Algorithms.vue         # Algorithm documentation
│   │   │   ├── GuideSpecs.vue         # Manage guide specs
│   │   │   └── History.vue            # Analysis history
│   │   ├── router/        # Vue Router configuration
│   │   ├── stores/        # API client (api.js)
│   │   ├── App.vue        # Main app component
│   │   └── main.js        # App entry point
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── [legacy modules]        # Original Python analysis modules
│   ├── timedomain.py      # Peak, RMS, Kurtosis, CF
│   ├── frequencydomain.py # FFT, FM0, frequency features
│   ├── filterprocess.py   # NA4, FM4, M6A, M8A, ER
│   ├── waveletprocess.py  # STFT, CWT, NP4
│   ├── hilbertransfer.py  # Hilbert transform, envelope
│   ├── harmonic_sildband_table.py # Harmonic/sideband analysis
│   ├── x_parameter.py, y_parameter.py, z_parameter.py
│   └── initialization.py  # Legacy configuration
├── docker-compose.yml     # Full stack deployment
├── vibration_analysis.db  # SQLite database
└── README_NEW.md          # Complete documentation
```

### Data Flow (Web Application)

1. **User uploads CSV** → Frontend [Analysis.vue](frontend/src/views/Analysis.vue)
2. **API receives file** → Backend [main.py](backend/main.py#L156) `/api/upload-csv`
3. **Parse & extract signal** → NumPy array from CSV
4. **Vibration analysis** → [analysis.py](backend/analysis.py) `VibrationAnalyzer.analyze()`
   - Calls legacy modules in sequence:
     - Time domain features (Peak, RMS, Kurtosis, CF)
     - Frequency domain (FFT, BPF detection, FM0)
     - Envelope analysis (Hilbert transform, resonance band filtering)
     - Higher-order statistics (NA4, FM4, M6A, M8A)
     - Wavelet analysis (STFT, CWT, NP4)
     - Preload status assessment
   - Integrates all features into comprehensive diagnosis
   - Calculates health score (0-100) and severity level
5. **Store results** → SQLite [models.py](backend/models.py) `AnalysisResult` table
6. **Return diagnosis** → JSON response to frontend
7. **Display visualizations** → Charts, tables, and alerts in Vue components

### Database Schema

**GuideSpec** (滑軌規格):
- `id`, `series`, `type`, `preload`
- `C0` (static load), `C100` (dynamic load)
- `seal_type`, `speed_max`, `stroke`, `lubrication`

**AnalysisResult** (分析結果):
- `id`, `guide_spec_id`, `timestamp`, `velocity`
- `health_score` (0-100)
- `time_features`, `frequency_features`, `envelope_features` (JSON)
- `higher_order_features`, `findings`, `recommendations` (JSON)

### Feature Calculation Modules (Legacy)

All modules still functional for batch processing:

- **TimeDomain** [timedomain.py](timedomain.py): peak, avg, rms, kurt, cf, eo
- **FrequencyDomain** [frequencydomain.py](frequencydomain.py): FFT, FM0, gear/bearing energy
- **HarmonicSildband** [harmonic_sildband_table.py](harmonic_sildband_table.py): Harmonic (0.25x-2.75x), Sideband (2.75x-14.25x)
- **FilterProcess** [filterprocess.py](filterprocess.py): NA4, NA4S, FM4, M6A, M8A, ER
- **WaveLetProcess** [waveletprocess.py](waveletprocess.py): STFT (Hann/Flattop), CWT (db8), NP4
- **HilberTransfer** [hilbertransfer.py](hilbertransfer.py): Hilbert transform, envelope, NB4

## API Endpoints

### Guide Specifications
- `POST /api/guide-specs` - Create new guide spec
- `GET /api/guide-specs` - List all specs
- `GET /api/guide-specs/{id}` - Get specific spec

### Frequency Calculation
- `POST /api/calculate-frequencies` - Calculate BPF, BSF, Cage frequency
  - Params: `v` (velocity), `D` (ball diameter), `L` (slider length), `n_balls`, `contact_angle`, `raceway_diameter`

### Analysis
- `POST /api/analyze` - Analyze vibration signal data
  - Body: `signal_data` (array), `fs`, `velocity`, `guide_spec_id`
- `POST /api/upload-csv` - Upload and analyze CSV file
  - Params: `file`, `guide_spec_id`, `fs`, `velocity`

### Results
- `GET /api/results?guide_spec_id={id}&limit={n}` - List analysis results
- `GET /api/results/{id}` - Get specific result
- `GET /api/health-trend/{guide_spec_id}?days={n}` - Get health trend

## Common Development Tasks

### Adding a New API Endpoint

1. Define Pydantic model (if needed) in [backend/main.py](backend/main.py)
2. Add route:
```python
@app.post("/api/your-endpoint")
async def your_function(data: YourModel):
    # Implementation
    return result
```
3. Add to [frontend/src/stores/api.js](frontend/src/stores/api.js):
```javascript
yourFunction(data) {
  return api.post('/api/your-endpoint', data)
}
```

### Adding a New Vue Page

1. Create `frontend/src/views/YourPage.vue`
2. Add route in [frontend/src/router/index.js](frontend/src/router/index.js)
3. Add menu item in [frontend/src/App.vue](frontend/src/App.vue) sidebar

### Modifying Analysis Parameters

**Web app**: Edit [backend/analysis.py](backend/analysis.py):
- `_get_guide_parameters()`: Guide specs (D, L, n_balls) for different models
- `_assess_preload_status()`: Preload thresholds (VC/V0/V1/V2)
- `_determine_resonance_band()`: Resonance frequency bands by guide size
- `_integrated_diagnosis()`: Health score calculation logic and thresholds

**Legacy**: Edit [initialization.py](initialization.py)

### Adding New Linear Guide Models

1. In [backend/analysis.py](backend/analysis.py) `_get_guide_parameters()`:
```python
params_db = {
    'HRC25': {'D': 6.35, 'L': 70, 'n_balls': 26, 'contact_angle': 45},
    'YOUR_MODEL': {'D': x, 'L': y, 'n_balls': z, 'contact_angle': 45},
}
```

2. In [frontend/src/views/FrequencyCalculator.vue](frontend/src/views/FrequencyCalculator.vue) add to `modelParams`

3. In [frontend/src/views/GuideSpecs.vue](frontend/src/views/GuideSpecs.vue) add to series dropdown

### Database Changes

1. Modify models in [backend/models.py](backend/models.py)
2. Delete `vibration_analysis.db` file
3. Restart backend (database recreated automatically via `init_db()`)

### Adjusting Diagnosis Thresholds

Edit [backend/analysis.py](backend/analysis.py) `_integrated_diagnosis()`:
```python
if time_features['Kurtosis'] > 8:  # Threshold
    health_score -= 30  # Penalty
    findings.append('峰度異常升高...')
```

Current thresholds:
- Kurtosis > 8: -30 points (嚴重缺陷)
- Kurtosis > 5: -15 points (輕微衝擊)
- Preload abnormal: -20 points
- Envelope defect detected: -25 points
- NA4 > 3: -15 points (早期故障)
- CWT NP4 > 4: -10 points (瞬態衝擊)

## Code Conventions

### CSV File Format
Expected columns: `time, x, y, z, label, 12m, 60m`
- System extracts X-axis data (column 2) for analysis
- Can be modified in [backend/main.py](backend/main.py#L156) `upload_csv()`

### API Response Format
All endpoints return JSON:
```json
{
  "id": 1,
  "diagnosis": {
    "health_score": 85,
    "severity": "輕微異常",
    "time_features": {...},
    "findings": [...],
    "recommendations": [...]
  }
}
```

### Vue Component Structure
- Use `<script setup>` (Composition API)
- Import Element Plus components as needed
- Use Pinia stores for shared state (if needed)
- API calls via `import api from '@/stores/api'`

## Key Features for CPC Linear Guides

### 1. Theoretical Frequency Calculation
For linear guides (vs rotating bearings):
- **BPF** (Ball Pass Frequency) = v / ball_spacing
- **BSF** (Ball Spin Frequency) = v / (π × D)
- **Cage Frequency** = v / slider_length

### 2. Preload Status Assessment
Based on CPC preload levels (VC, V0, V1, V2):
- RMS too low (< threshold × 0.7) → Preload失效
- Kurtosis too high (> threshold) → 預壓不足

### 3. Resonance Band Selection
Guide size determines resonance frequency:
- MR (微型): 8-15 kHz
- 15/20/25 (小型): 4-10 kHz
- 30/35/45 (中型): 2-8 kHz
- 55/65 (大型): 1-6 kHz

Used for envelope analysis bandpass filtering.

### 4. Integrated Health Scoring
Combines multiple indicators:
- Time domain (RMS, Kurtosis, CF)
- Frequency domain (BPF detection)
- Envelope analysis (defect detection)
- Higher-order statistics (NA4, FM4)
- Wavelet (NP4)

Final score 0-100, with severity levels:
- 90-100: 健康 (green)
- 75-90: 輕微異常 (yellow)
- 60-75: 中等異常 (orange)
- 0-60: 嚴重異常 (red)

## Troubleshooting

### Backend fails to start
- Check Python version (3.8+)
- Install dependencies: `pip install -r backend/requirements.txt`
- Ensure legacy modules are in Python path

### Frontend build errors
- Check Node version (16+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check vite.config.js proxy settings

### Database errors
- Delete vibration_analysis.db and restart
- Check SQLAlchemy models are properly defined
- Verify database path in database.py

### Analysis errors
- Ensure signal data is numeric array
- Check sampling frequency is reasonable (> 1000 Hz)
- Verify CSV format matches expected columns
- Check guide_spec exists in database

For detailed usage examples, see [README_NEW.md](README_NEW.md).
