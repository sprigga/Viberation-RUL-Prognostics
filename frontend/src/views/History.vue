<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2>歷史分析記錄</h2>
          <el-space>
            <el-select v-model="filterGuideId" placeholder="篩選滑軌" clearable @change="loadResults">
              <el-option
                v-for="spec in guideSpecs"
                :key="spec.id"
                :label="`${spec.series}-${spec.type}`"
                :value="spec.id"
              />
            </el-select>
            <el-button @click="loadResults">
              <el-icon><Refresh /></el-icon>
              重新整理
            </el-button>
          </el-space>
        </div>
      </template>

      <el-table :data="results" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="分析時間" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column label="健康分數" width="150">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.health_score"
              :color="getHealthColor(scope.row.health_score)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="velocity" label="速度 (m/s)" width="110" />
        <el-table-column label="RMS" width="100">
          <template #default="scope">
            {{ scope.row.time_features?.RMS?.toFixed(4) }}
          </template>
        </el-table-column>
        <el-table-column label="峰度" width="100">
          <template #default="scope">
            {{ scope.row.time_features?.Kurtosis?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="診斷發現">
          <template #default="scope">
            <el-tag
              v-for="(finding, index) in scope.row.findings?.slice(0, 2)"
              :key="index"
              size="small"
              style="margin: 2px;"
            >
              {{ finding }}
            </el-tag>
            <span v-if="scope.row.findings?.length > 2">...</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewDetail(scope.row.id)">
              查看詳情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px; justify-content: center;"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="分析詳情" width="800px">
      <div v-if="selectedResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分析ID">{{ selectedResult.id }}</el-descriptions-item>
          <el-descriptions-item label="時間">
            {{ formatDate(selectedResult.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="健康分數">
            <el-tag :type="getHealthTagType(selectedResult.health_score)" size="large">
              {{ selectedResult.health_score }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="速度">{{ selectedResult.velocity }} m/s</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px;">時域特徵</h3>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item
            v-for="(value, key) in selectedResult.time_features"
            :key="key"
            :label="key"
          >
            {{ value?.toFixed(4) }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px;">診斷發現</h3>
        <el-alert
          v-for="(finding, index) in selectedResult.findings"
          :key="index"
          :title="finding"
          type="info"
          style="margin-bottom: 10px;"
          :closable="false"
        />

        <h3 style="margin-top: 20px;">維護建議</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(rec, index) in selectedResult.recommendations"
            :key="index"
          >
            {{ rec }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '../stores/api'

const results = ref([])
const guideSpecs = ref([])
const filterGuideId = ref(null)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailDialogVisible = ref(false)
const selectedResult = ref(null)

const loadResults = async () => {
  loading.value = true
  try {
    const data = await api.getResults(filterGuideId.value, 100)
    results.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('載入失敗')
  } finally {
    loading.value = false
  }
}

const loadGuideSpecs = async () => {
  try {
    guideSpecs.value = await api.getGuideSpecs()
  } catch (error) {
    console.error('Failed to load guide specs')
  }
}

const viewDetail = async (id) => {
  try {
    selectedResult.value = await api.getResult(id)
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('載入詳情失敗')
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const getHealthColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  return '#f56c6c'
}

const getHealthTagType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 75) return 'warning'
  return 'danger'
}

onMounted(() => {
  loadGuideSpecs()
  loadResults()
})
</script>

<style scoped>
.history-page {
  padding: 20px;
}

h3 {
  color: #303133;
  margin-bottom: 10px;
}
</style>
