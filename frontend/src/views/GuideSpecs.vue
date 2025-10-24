<template>
  <div class="guide-specs-page">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2>滑軌規格管理</h2>
          <el-button type="primary" @click="dialogVisible = true">
            <el-icon><Plus /></el-icon>
            新增規格
          </el-button>
        </div>
      </template>

      <el-table :data="guideSpecs" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="series" label="系列" width="100" />
        <el-table-column prop="type" label="型式" width="80" />
        <el-table-column prop="preload" label="預壓" width="80" />
        <el-table-column prop="C0" label="C₀ (N)" width="100" />
        <el-table-column prop="C100" label="C₁₀₀ (N)" width="100" />
        <el-table-column prop="seal_type" label="密封" width="80" />
        <el-table-column prop="speed_max" label="最高速度 (m/s)" width="130" />
        <el-table-column prop="stroke" label="行程 (mm)" width="110" />
        <el-table-column prop="lubrication" label="潤滑" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewDetails(scope.row)">
              詳情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Guide Spec Dialog -->
    <el-dialog v-model="dialogVisible" title="新增滑軌規格" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="系列">
          <el-select v-model="form.series" placeholder="選擇系列">
            <el-option label="HRC15" value="HRC15" />
            <el-option label="HRC20" value="HRC20" />
            <el-option label="HRC25" value="HRC25" />
            <el-option label="HRC30" value="HRC30" />
            <el-option label="HRC35" value="HRC35" />
            <el-option label="HRC45" value="HRC45" />
          </el-select>
        </el-form-item>

        <el-form-item label="滑座型式">
          <el-select v-model="form.type" placeholder="選擇型式">
            <el-option label="MN（標準型）" value="MN" />
            <el-option label="ML（長型）" value="ML" />
            <el-option label="MS（短型）" value="MS" />
          </el-select>
        </el-form-item>

        <el-form-item label="預壓等級">
          <el-select v-model="form.preload" placeholder="選擇預壓">
            <el-option label="VC（微間隙）" value="VC" />
            <el-option label="V0（標準預壓 0.02C）" value="V0" />
            <el-option label="V1（中預壓 0.05C）" value="V1" />
            <el-option label="V2（高預壓 0.08C）" value="V2" />
          </el-select>
        </el-form-item>

        <el-form-item label="基本靜負荷 C₀">
          <el-input-number v-model="form.C0" :min="0" :step="100" />
          <span style="margin-left: 10px;">N</span>
        </el-form-item>

        <el-form-item label="基本動負荷 C₁₀₀">
          <el-input-number v-model="form.C100" :min="0" :step="100" />
          <span style="margin-left: 10px;">N</span>
        </el-form-item>

        <el-form-item label="密封片類型">
          <el-select v-model="form.seal_type" placeholder="選擇密封">
            <el-option label="S（標準接觸式）" value="S" />
            <el-option label="N（非接觸式）" value="N" />
            <el-option label="SL（低摩擦）" value="SL" />
          </el-select>
        </el-form-item>

        <el-form-item label="最高速度">
          <el-input-number v-model="form.speed_max" :min="0.1" :max="10" :step="0.1" :precision="1" />
          <span style="margin-left: 10px;">m/s</span>
        </el-form-item>

        <el-form-item label="行程長度">
          <el-input-number v-model="form.stroke" :min="100" :max="10000" :step="100" />
          <span style="margin-left: 10px;">mm</span>
        </el-form-item>

        <el-form-item label="潤滑系統">
          <el-select v-model="form.lubrication" placeholder="選擇潤滑" clearable>
            <el-option label="Z（內藏儲油塊）" value="Z" />
            <el-option label="G（潤滑脂）" value="G" />
            <el-option label="O（潤滑油）" value="O" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addGuideSpec" :loading="saving">
          確定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '../stores/api'

const guideSpecs = ref([])
const dialogVisible = ref(false)
const saving = ref(false)

const form = ref({
  series: 'HRC25',
  type: 'MN',
  preload: 'V1',
  C0: 31500,
  C100: 29800,
  seal_type: 'S',
  speed_max: 5.0,
  stroke: 1000,
  lubrication: 'Z'
})

const loadGuideSpecs = async () => {
  try {
    guideSpecs.value = await api.getGuideSpecs()
  } catch (error) {
    ElMessage.error('載入失敗')
  }
}

const addGuideSpec = async () => {
  saving.value = true
  try {
    await api.createGuideSpec(form.value)
    ElMessage.success('新增成功!')
    dialogVisible.value = false
    await loadGuideSpecs()
  } catch (error) {
    ElMessage.error('新增失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const viewDetails = (row) => {
  ElMessage.info('詳情功能開發中...')
}

onMounted(() => {
  loadGuideSpecs()
})
</script>

<style scoped>
.guide-specs-page {
  padding: 20px;
}
</style>
