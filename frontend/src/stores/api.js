import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Guide specifications
  getGuideSpecs() {
    return api.get('/api/guide-specs')
  },

  getGuideSpec(id) {
    return api.get(`/api/guide-specs/${id}`)
  },

  createGuideSpec(data) {
    return api.post('/api/guide-specs', data)
  },

  // Frequency calculation
  calculateFrequencies(params) {
    return api.post('/api/calculate-frequencies', params)
  },

  // Analysis
  analyzeVibration(data) {
    return api.post('/api/analyze', data)
  },

  uploadCSV(file, guideSpecId, fs, velocity) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/upload-csv?guide_spec_id=${guideSpecId}&fs=${fs}&velocity=${velocity}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Results
  getResults(guideSpecId = null, limit = 50) {
    const params = new URLSearchParams()
    if (guideSpecId) params.append('guide_spec_id', guideSpecId)
    params.append('limit', limit)
    return api.get(`/api/results?${params.toString()}`)
  },

  getResult(id) {
    return api.get(`/api/results/${id}`)
  },

  getHealthTrend(guideSpecId, days = 30) {
    return api.get(`/api/health-trend/${guideSpecId}?days=${days}`)
  },

  // PHM 2012 Challenge APIs
  getPHMTrainingSummary() {
    return api.get('/api/phm/training-summary')
  },

  getPHMAnalysisData() {
    return api.get('/api/phm/analysis-data')
  },

  uploadBearingData(file, bearingName) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/phm/upload-bearing-data?bearing_name=${bearingName}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getBearingTestData(bearingName) {
    return api.get(`/api/phm/test-data/${bearingName}`)
  },

  predictRUL(bearingName, modelType = 'baseline') {
    return api.post('/api/phm/predict-rul', null, {
      params: { bearing_name: bearingName, model_type: modelType }
    })
  }
}
