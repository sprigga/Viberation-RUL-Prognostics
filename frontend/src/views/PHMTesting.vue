<template>
  <div class="phm-testing">
    <el-card class="header-card">
      <h2>🔬 PHM 測試數據分析</h2>
      <p>上傳測試數據並預測剩餘使用壽命 (RUL)</p>
    </el-card>

    <!-- 上傳區域 -->
    <el-card class="upload-card">
      <template #header>
        <span>📤 上傳 PHM 測試數據</span>
      </template>

      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="軸承名稱">
          <el-input
            v-model="uploadForm.bearing_name"
            placeholder="例如: Bearing1_3"
            style="width: 300px"
          />
        </el-form-item>

        <el-form-item label="上傳文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".csv"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖曳文件到此處或 <em>點擊上傳</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上傳 PHM 格式的 CSV 文件
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="uploading"
            @click="uploadAndAnalyze"
            :disabled="!selectedFile"
          >
            上傳並分析
          </el-button>
          <el-button @click="resetUpload">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分析結果 -->
    <el-card v-if="analysisResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>📊 分析結果</span>
          <el-tag type="success">{{ analysisResult.bearing_name }}</el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="水平振動 RMS" :value="analysisResult.analysis.horiz_rms">
            <template #suffix>
              <span style="font-size: 14px"></span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic title="垂直振動 RMS" :value="analysisResult.analysis.vert_rms">
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider />

      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic
            title="水平振動峰度"
            :value="analysisResult.analysis.horiz_kurtosis"
          >
            <template #suffix>
              <el-tag
                :type="getKurtosisType(analysisResult.analysis.horiz_kurtosis)"
                size="small"
              >
                {{ getKurtosisStatus(analysisResult.analysis.horiz_kurtosis) }}
              </el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-statistic
            title="垂直振動峰度"
            :value="analysisResult.analysis.vert_kurtosis"
          >
            <template #suffix>
              <el-tag
                :type="getKurtosisType(analysisResult.analysis.vert_kurtosis)"
                size="small"
              >
                {{ getKurtosisStatus(analysisResult.analysis.vert_kurtosis) }}
              </el-tag>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider />

      <el-button type="primary" @click="predictRUL">
        預測 RUL
      </el-button>
    </el-card>

    <!-- RUL 預測結果 -->
    <el-card v-if="prediction" class="prediction-card">
      <template #header>
        <div class="card-header">
          <span>🎯 RUL 預測結果</span>
          <el-tag :type="getRULType(prediction.predicted_RUL_min)">
            {{ getRULStatus(prediction.predicted_RUL_min) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="軸承名稱">
          <strong>{{ prediction.bearing_name }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="模型類型">
          {{ prediction.model_type }}
        </el-descriptions-item>
        <el-descriptions-item label="預測 RUL">
          <el-statistic
            :value="prediction.predicted_RUL_min"
            suffix="分鐘"
          />
        </el-descriptions-item>
        <el-descriptions-item label="信心度">
          <el-progress
            :percentage="prediction.confidence * 100"
            :color="customColors"
          />
        </el-descriptions-item>
        <el-descriptions-item label="預測時間">
          {{ new Date().toLocaleString('zh-TW') }}
        </el-descriptions-item>
        <el-descriptions-item label="狀態">
          <el-tag :type="getRULType(prediction.predicted_RUL_min)" size="large">
            {{ getRULStatus(prediction.predicted_RUL_min) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h4>📈 特徵數據：</h4>
      <pre>{{ JSON.stringify(prediction.features, null, 2) }}</pre>
    </el-card>

    <!-- 已上傳數據列表 -->
    <el-card v-if="uploadedData.length > 0" class="history-card">
      <template #header>
        <span>📋 已上傳數據</span>
      </template>

      <el-table :data="uploadedData" stripe>
        <el-table-column prop="bearing_name" label="軸承名稱" width="150" />
        <el-table-column prop="horiz_rms" label="水平 RMS" width="120" />
        <el-table-column prop="vert_rms" label="垂直 RMS" width="120" />
        <el-table-column prop="horiz_kurtosis" label="水平峰度" width="120" />
        <el-table-column prop="vert_kurtosis" label="垂直峰度" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="quickPredict(scope.row.bearing_name)"
            >
              快速預測
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/stores/api'

const uploadForm = ref({
  bearing_name: ''
})

const selectedFile = ref(null)
const uploading = ref(false)
const analysisResult = ref(null)
const prediction = ref(null)
const uploadedData = ref([])
const uploadRef = ref(null)

const customColors = [
  { color: '#f56c6c', percentage: 30 },
  { color: '#e6a23c', percentage: 60 },
  { color: '#5cb87a', percentage: 100 }
]

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const uploadAndAnalyze = async () => {
  if (!uploadForm.value.bearing_name) {
    ElMessage.warning('請輸入軸承名稱')
    return
  }

  if (!selectedFile.value) {
    ElMessage.warning('請選擇文件')
    return
  }

  try {
    uploading.value = true

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('bearing_name', uploadForm.value.bearing_name)

    const response = await api.post('/api/phm/upload-bearing-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      params: {
        bearing_name: uploadForm.value.bearing_name
      }
    })

    analysisResult.value = response.data
    uploadedData.value.unshift({
      bearing_name: response.data.bearing_name,
      horiz_rms: response.data.analysis.horiz_rms.toFixed(3),
      vert_rms: response.data.analysis.vert_rms.toFixed(3),
      horiz_kurtosis: response.data.analysis.horiz_kurtosis.toFixed(2),
      vert_kurtosis: response.data.analysis.vert_kurtosis.toFixed(2)
    })

    ElMessage.success('文件上傳並分析成功！')
  } catch (error) {
    ElMessage.error('上傳失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const predictRUL = async () => {
  if (!analysisResult.value) {
    ElMessage.warning('請先上傳並分析數據')
    return
  }

  try {
    const response = await api.post('/api/phm/predict-rul', null, {
      params: {
        bearing_name: analysisResult.value.bearing_name,
        model_type: 'baseline'
      }
    })

    prediction.value = response.data
    ElMessage.success('RUL 預測完成！')
  } catch (error) {
    ElMessage.error('預測失敗: ' + (error.response?.data?.detail || error.message))
  }
}

const quickPredict = async (bearingName) => {
  try {
    const response = await api.post('/api/phm/predict-rul', null, {
      params: {
        bearing_name: bearingName,
        model_type: 'baseline'
      }
    })

    prediction.value = response.data
    ElMessage.success('RUL 預測完成！')
  } catch (error) {
    ElMessage.error('預測失敗: ' + (error.response?.data?.detail || error.message))
  }
}

const resetUpload = () => {
  uploadForm.value.bearing_name = ''
  selectedFile.value = null
  analysisResult.value = null
  prediction.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const getKurtosisType = (kurtosis) => {
  if (kurtosis > 10) return 'danger'
  if (kurtosis > 5) return 'warning'
  return 'success'
}

const getKurtosisStatus = (kurtosis) => {
  if (kurtosis > 10) return '嚴重異常'
  if (kurtosis > 5) return '輕微異常'
  return '正常'
}

const getRULType = (rul) => {
  if (rul < 1000) return 'danger'
  if (rul < 3000) return 'warning'
  return 'success'
}

const getRULStatus = (rul) => {
  if (rul < 1000) return '緊急 - 接近故障'
  if (rul < 3000) return '注意 - 需要監控'
  return '良好 - 健康狀態'
}
</script>

<style scoped>
.phm-testing {
  max-width: 1200px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-card h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.header-card p {
  margin: 0;
  opacity: 0.9;
}

.upload-card,
.result-card,
.prediction-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-icon--upload {
  font-size: 67px;
  color: #409EFF;
  margin-bottom: 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
}

.prediction-card h4 {
  margin: 16px 0 8px 0;
  color: #409EFF;
}

.prediction-card pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.el-statistic {
  margin: 16px 0;
}
</style>
