<template>
  <div class="dashboard">
    <el-row :gutter="20" class="header-stats">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon size="30"><Check /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ healthyCount }}</h3>
            <p>健康設備</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon size="30"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ warningCount }}</h3>
            <p>警告</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon size="30"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ criticalCount }}</h3>
            <p>嚴重異常</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #909399;">
            <el-icon size="30"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ totalAnalyses }}</h3>
            <p>總分析次數</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>健康趨勢</span>
              <el-select v-model="selectedGuide" placeholder="選擇滑軌" style="width: 200px;" @change="loadTrendData">
                <el-option
                  v-for="spec in guideSpecs"
                  :key="spec.id"
                  :label="`${spec.series}-${spec.type}`"
                  :value="spec.id"
                />
              </el-select>
            </div>
          </template>
          <div style="height: 300px;">
            <Line v-if="chartData" :data="chartData" :options="chartOptions" />
            <el-empty v-else description="選擇滑軌以查看趨勢" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最近分析</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="result in recentResults"
              :key="result.id"
              :timestamp="formatDate(result.timestamp)"
              :color="getHealthColor(result.health_score)"
            >
              <div>
                <strong>健康分數: {{ result.health_score }}</strong>
                <p style="font-size: 12px; color: #909399;">速度: {{ result.velocity }} m/s</p>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="recentResults.length === 0" description="暫無記錄" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/analysis')">
              <el-icon><DataAnalysis /></el-icon>
              開始分析
            </el-button>
            <el-button type="success" @click="$router.push('/frequency')">
              <el-icon><Connection /></el-icon>
              頻率計算
            </el-button>
            <el-button type="info" @click="$router.push('/algorithms')">
              <el-icon><Operation /></el-icon>
              演算法展示
            </el-button>
            <el-button @click="$router.push('/guide-specs')">
              <el-icon><Setting /></el-icon>
              管理滑軌規格
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Check, Warning, CircleClose, DataLine, DataAnalysis, Connection, Operation, Setting } from '@element-plus/icons-vue'
import api from '../stores/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const healthyCount = ref(0)
const warningCount = ref(0)
const criticalCount = ref(0)
const totalAnalyses = ref(0)
const recentResults = ref([])
const guideSpecs = ref([])
const selectedGuide = ref(null)
const chartData = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      title: {
        display: true,
        text: '健康分數'
      }
    }
  }
}

const loadDashboardData = async () => {
  try {
    const results = await api.getResults(null, 100)
    totalAnalyses.value = results.length

    healthyCount.value = results.filter(r => r.health_score >= 90).length
    warningCount.value = results.filter(r => r.health_score >= 60 && r.health_score < 90).length
    criticalCount.value = results.filter(r => r.health_score < 60).length

    recentResults.value = results.slice(0, 10)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const loadGuideSpecs = async () => {
  try {
    guideSpecs.value = await api.getGuideSpecs()
    if (guideSpecs.value.length > 0) {
      selectedGuide.value = guideSpecs.value[0].id
      await loadTrendData()
    }
  } catch (error) {
    console.error('Failed to load guide specs:', error)
  }
}

const loadTrendData = async () => {
  if (!selectedGuide.value) return

  try {
    const trend = await api.getHealthTrend(selectedGuide.value, 30)

    chartData.value = {
      labels: trend.trend.map(t => new Date(t.timestamp).toLocaleDateString()),
      datasets: [
        {
          label: '健康分數',
          data: trend.trend.map(t => t.health_score),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4
        }
      ]
    }
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const getHealthColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  if (score >= 60) return '#f56c6c'
  return '#909399'
}

onMounted(() => {
  loadDashboardData()
  loadGuideSpecs()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.header-stats {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.stat-info h3 {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 5px;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
