<template>
  <div class="analysis-page">
    <el-card>
      <template #header>
        <h2>振動信號分析</h2>
      </template>

      <el-form :model="analysisForm" label-width="120px">
        <el-form-item label="滑軌規格">
          <el-select v-model="analysisForm.guideSpecId" placeholder="選擇滑軌規格">
            <el-option
              v-for="spec in guideSpecs"
              :key="spec.id"
              :label="`${spec.series}-${spec.type} (預壓: ${spec.preload})`"
              :value="spec.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="採樣頻率">
          <el-input-number v-model="analysisForm.fs" :min="1000" :max="100000" :step="100" />
          <span style="margin-left: 10px;">Hz</span>
        </el-form-item>

        <el-form-item label="運行速度">
          <el-input-number v-model="analysisForm.velocity" :min="0.1" :max="10" :step="0.1" :precision="2" />
          <span style="margin-left: 10px;">m/s</span>
        </el-form-item>

        <el-form-item label="上傳CSV檔案">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".csv"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖曳檔案至此或 <em>點擊上傳</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支援CSV格式，檔案格式: time, x, y, z, ...
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="analyzeData" :loading="analyzing">
            <el-icon><DataAnalysis /></el-icon>
            開始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="analysisResult" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2>分析結果</h2>
          <el-tag :type="getHealthTagType(analysisResult.diagnosis.health_score)" size="large">
            健康分數: {{ analysisResult.diagnosis.health_score }}
          </el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="綜合診斷" name="summary">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="分析時間">
              {{ formatDate(analysisResult.diagnosis.timestamp) }}
            </el-descriptions-item>
            <el-descriptions-item label="運行速度">
              {{ analysisResult.diagnosis.velocity }} m/s
            </el-descriptions-item>
            <el-descriptions-item label="健康分數">
              <el-progress
                :percentage="analysisResult.diagnosis.health_score"
                :color="getHealthColor(analysisResult.diagnosis.health_score)"
              />
            </el-descriptions-item>
            <el-descriptions-item label="嚴重程度">
              <el-tag :type="getSeverityTagType(analysisResult.diagnosis.severity)">
                {{ analysisResult.diagnosis.severity }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <h3>診斷發現</h3>
          <el-alert
            v-for="(finding, index) in analysisResult.diagnosis.findings"
            :key="index"
            :title="finding"
            type="warning"
            style="margin-bottom: 10px;"
            show-icon
          />

          <h3 style="margin-top: 20px;">維護建議</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(rec, index) in analysisResult.diagnosis.recommendations"
              :key="index"
              :timestamp="rec"
              placement="top"
            >
              {{ rec }}
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <el-tab-pane label="時域特徵" name="time">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(value, key) in analysisResult.diagnosis.time_features" :key="key">
              <el-card shadow="hover" class="feature-card">
                <div class="feature-label">{{ key }}</div>
                <div class="feature-value">{{ value.toFixed(4) }}</div>
              </el-card>
            </el-col>
          </el-row>

          <h3 style="margin-top: 20px;">預壓狀態評估</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="預壓等級">
              {{ analysisResult.diagnosis.preload_status?.level }}
            </el-descriptions-item>
            <el-descriptions-item label="狀態">
              <el-tag :type="analysisResult.diagnosis.preload_status?.condition === '正常' ? 'success' : 'warning'">
                {{ analysisResult.diagnosis.preload_status?.condition }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="警告">
              <div v-for="(warning, index) in analysisResult.diagnosis.preload_status?.warnings" :key="index">
                {{ warning }}
              </div>
              <span v-if="!analysisResult.diagnosis.preload_status?.warnings?.length">無</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="頻域特徵" name="frequency">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(value, key) in analysisResult.diagnosis.frequency_features" :key="key">
              <el-card shadow="hover" class="feature-card">
                <div class="feature-label">{{ key }}</div>
                <div class="feature-value">
                  {{ typeof value === 'boolean' ? (value ? '是' : '否') : value.toFixed(4) }}
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="包絡分析" name="envelope">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="共振頻帶">
              {{ analysisResult.diagnosis.envelope_features?.resonance_band?.join(' - ') }} Hz
            </el-descriptions-item>
            <el-descriptions-item label="缺陷檢測">
              <el-tag :type="analysisResult.diagnosis.envelope_features?.defect_detected ? 'danger' : 'success'">
                {{ analysisResult.diagnosis.envelope_features?.defect_detected ? '檢測到缺陷' : '未檢測到缺陷' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <h3 style="margin-top: 20px;">檢測結果</h3>
          <el-table :data="getEnvelopeDetections()" border>
            <el-table-column prop="harmonic" label="諧波" />
            <el-table-column prop="frequency" label="頻率 (Hz)" />
            <el-table-column prop="amplitude" label="振幅" />
            <el-table-column prop="snr" label="信噪比" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="高階統計" name="higher-order">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(value, key) in analysisResult.diagnosis.higher_order_features" :key="key">
              <el-card shadow="hover" class="feature-card">
                <div class="feature-label">{{ key }}</div>
                <div class="feature-value">{{ value.toFixed(4) }}</div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="小波分析" name="wavelet">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(value, key) in analysisResult.diagnosis.wavelet_features" :key="key">
              <el-card shadow="hover" class="feature-card">
                <div class="feature-label">{{ key }}</div>
                <div class="feature-value">{{ value.toFixed(4) }}</div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, DataAnalysis } from '@element-plus/icons-vue'
import api from '../stores/api'

const guideSpecs = ref([])
const analysisForm = ref({
  guideSpecId: null,
  fs: 25600,
  velocity: 0.5
})
const uploadRef = ref()
const selectedFile = ref(null)
const analyzing = ref(false)
const analysisResult = ref(null)
const activeTab = ref('summary')

const loadGuideSpecs = async () => {
  try {
    guideSpecs.value = await api.getGuideSpecs()
    if (guideSpecs.value.length > 0) {
      analysisForm.value.guideSpecId = guideSpecs.value[0].id
    }
  } catch (error) {
    ElMessage.error('載入滑軌規格失敗')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const analyzeData = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('請先上傳CSV檔案')
    return
  }

  if (!analysisForm.value.guideSpecId) {
    ElMessage.warning('請選擇滑軌規格')
    return
  }

  analyzing.value = true
  try {
    const result = await api.uploadCSV(
      selectedFile.value,
      analysisForm.value.guideSpecId,
      analysisForm.value.fs,
      analysisForm.value.velocity
    )

    analysisResult.value = result
    ElMessage.success('分析完成!')
    activeTab.value = 'summary'
  } catch (error) {
    ElMessage.error('分析失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    analyzing.value = false
  }
}

const getHealthTagType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 75) return 'warning'
  return 'danger'
}

const getSeverityTagType = (severity) => {
  if (severity === '健康') return 'success'
  if (severity === '輕微異常') return 'info'
  if (severity === '中等異常') return 'warning'
  return 'danger'
}

const getHealthColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const getEnvelopeDetections = () => {
  if (!analysisResult.value?.diagnosis?.envelope_features?.detections) return []

  return Object.entries(analysisResult.value.diagnosis.envelope_features.detections).map(([key, value]) => ({
    harmonic: key,
    frequency: value.frequency.toFixed(2),
    amplitude: value.amplitude.toFixed(4),
    snr: value.snr.toFixed(2)
  }))
}

onMounted(() => {
  loadGuideSpecs()
})
</script>

<style scoped>
.analysis-page {
  padding: 20px;
}

.feature-card {
  margin-bottom: 15px;
  text-align: center;
}

.feature-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.feature-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
</style>
