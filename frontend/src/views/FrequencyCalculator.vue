<template>
  <div class="frequency-calculator">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h2>線性滑軌故障頻率計算器</h2>
          </template>

          <el-form :model="params" label-width="150px">
            <el-form-item label="運行速度 (v)">
              <el-input-number v-model="params.v" :min="0.01" :max="10" :step="0.1" :precision="2" />
              <span style="margin-left: 10px;">m/s</span>
            </el-form-item>

            <el-form-item label="滾動體直徑 (D)">
              <el-input-number v-model="params.D" :min="1" :max="20" :step="0.1" :precision="3" />
              <span style="margin-left: 10px;">mm</span>
            </el-form-item>

            <el-form-item label="滑座長度 (L)">
              <el-input-number v-model="params.L" :min="10" :max="200" :step="1" />
              <span style="margin-left: 10px;">mm</span>
            </el-form-item>

            <el-form-item label="單列滾動體數量">
              <el-input-number v-model="params.n_balls" :min="1" :max="100" :step="1" />
              <span style="margin-left: 10px;">個</span>
            </el-form-item>

            <el-form-item label="接觸角">
              <el-input-number v-model="params.contact_angle" :min="0" :max="90" :step="1" />
              <span style="margin-left: 10px;">度</span>
            </el-form-item>

            <el-form-item label="滾道有效直徑">
              <el-input-number v-model="params.raceway_diameter" :min="10" :max="100" :step="1" />
              <span style="margin-left: 10px;">mm</span>
            </el-form-item>

            <el-divider />

            <el-form-item label="快速選擇型號">
              <el-select v-model="selectedModel" @change="applyModel" placeholder="選擇型號">
                <el-option label="HRC15" value="HRC15" />
                <el-option label="HRC20" value="HRC20" />
                <el-option label="HRC25" value="HRC25" />
                <el-option label="HRC30" value="HRC30" />
                <el-option label="HRC35" value="HRC35" />
                <el-option label="HRC45" value="HRC45" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="calculate">
                <el-icon><Connection /></el-icon>
                計算頻率
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card v-if="result">
          <template #header>
            <h2>計算結果</h2>
          </template>

          <el-descriptions :column="1" border size="large">
            <el-descriptions-item label="BPF（滾動體通過頻率）">
              <span class="freq-value">{{ result.BPF }} Hz</span>
            </el-descriptions-item>
            <el-descriptions-item label="BSF（滾動體自轉頻率）">
              <span class="freq-value">{{ result.BSF }} Hz</span>
            </el-descriptions-item>
            <el-descriptions-item label="Cage Freq（保持鏈頻率）">
              <span class="freq-value">{{ result.Cage_Freq }} Hz</span>
            </el-descriptions-item>
            <el-descriptions-item label="2×BPF">
              <span class="freq-value">{{ result['2xBPF'] }} Hz</span>
            </el-descriptions-item>
            <el-descriptions-item label="3×BPF">
              <span class="freq-value">{{ result['3xBPF'] }} Hz</span>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <h3>BPF 諧波頻率</h3>
          <el-table :data="result.harmonics" border stripe>
            <el-table-column prop="order" label="倍數" width="100" />
            <el-table-column prop="frequency" label="頻率 (Hz)" />
          </el-table>

          <el-alert
            title="說明"
            type="info"
            style="margin-top: 20px;"
            :closable="false"
          >
            <template #default>
              <ul style="margin: 5px 0; padding-left: 20px;">
                <li>BPF: 用於檢測滾動體表面或軌道缺陷</li>
                <li>BSF: 用於檢測滾動體本身缺陷</li>
                <li>Cage Freq: 用於檢測保持鏈問題</li>
                <li>監測時應關注 BPF 及其諧波（2×, 3×, ...）</li>
              </ul>
            </template>
          </el-alert>
        </el-card>

        <el-card v-else>
          <el-empty description="輸入參數並點擊計算以查看結果" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import api from '../stores/api'

const params = ref({
  v: 0.5,
  D: 6.35,
  L: 70,
  n_balls: 26,
  contact_angle: 45,
  raceway_diameter: 30
})

const selectedModel = ref('')
const result = ref(null)

const modelParams = {
  'HRC15': { D: 3.175, L: 50, n_balls: 20, raceway_diameter: 20 },
  'HRC20': { D: 4.763, L: 60, n_balls: 22, raceway_diameter: 25 },
  'HRC25': { D: 6.35, L: 70, n_balls: 26, raceway_diameter: 30 },
  'HRC30': { D: 7.938, L: 80, n_balls: 28, raceway_diameter: 35 },
  'HRC35': { D: 9.525, L: 100, n_balls: 32, raceway_diameter: 42 },
  'HRC45': { D: 12.7, L: 120, n_balls: 36, raceway_diameter: 55 }
}

const applyModel = () => {
  if (selectedModel.value && modelParams[selectedModel.value]) {
    Object.assign(params.value, modelParams[selectedModel.value])
  }
}

const calculate = async () => {
  try {
    result.value = await api.calculateFrequencies(params.value)
    ElMessage.success('計算完成!')
  } catch (error) {
    ElMessage.error('計算失敗: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.frequency-calculator {
  padding: 20px;
}

.freq-value {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}
</style>
