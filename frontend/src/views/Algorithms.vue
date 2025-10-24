<template>
  <div class="algorithms-page">
    <el-card>
      <template #header>
        <h2>演算法原理與應用展示</h2>
      </template>

      <el-collapse v-model="activeAlgorithms" accordion>
        <!-- Time Domain -->
        <el-collapse-item title="時域特徵分析" name="time-domain">
          <h3>原理說明</h3>
          <p>時域特徵直接從原始振動信號中提取統計特徵，用於整體健康評估。</p>

          <h4>主要特徵:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Peak（峰值）">
              <code>Peak = max(|signal|)</code>
              <p>反映最大振動幅度，用於檢測衝擊</p>
            </el-descriptions-item>
            <el-descriptions-item label="RMS（均方根值）">
              <code>RMS = sqrt(mean(signal²))</code>
              <p>反映整體振動能量，最常用的健康指標</p>
            </el-descriptions-item>
            <el-descriptions-item label="Kurtosis（峰度）">
              <code>Kurt = E[(X-μ)⁴] / σ⁴</code>
              <p>反映信號尖銳程度，異常升高表示衝擊</p>
            </el-descriptions-item>
            <el-descriptions-item label="Crest Factor（波峰因數）">
              <code>CF = Peak / RMS</code>
              <p>反映峰值與平均值的比值</p>
            </el-descriptions-item>
          </el-descriptions>

          <h4 style="margin-top: 20px;">應用場景:</h4>
          <el-tag type="success" style="margin: 5px;">磨損程度監測</el-tag>
          <el-tag type="info" style="margin: 5px;">預壓狀態評估</el-tag>
          <el-tag type="warning" style="margin: 5px;">異常檢測</el-tag>

          <el-alert
            title="診斷準則"
            type="info"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>RMS 緩慢上升 → 磨損加劇</li>
              <li>Kurtosis > 8 → 嚴重衝擊，可能存在缺陷</li>
              <li>RMS 突然下降 → 預壓可能失效</li>
            </ul>
          </el-alert>
        </el-collapse-item>

        <!-- Frequency Domain -->
        <el-collapse-item title="頻域特徵分析" name="frequency-domain">
          <h3>原理說明</h3>
          <p>透過快速傅立葉轉換（FFT）將時域信號轉換為頻域，識別故障特徵頻率。</p>

          <h4>關鍵概念:</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <h4>FFT（快速傅立葉轉換）</h4>
                <code>X(f) = ∫ x(t)e^(-j2πft) dt</code>
                <p>將時域信號轉為頻域</p>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <h4>FM0（正規化峰值）</h4>
                <code>FM0 = Peak / ΣE_harmonics</code>
                <p>峰值與諧波能量比值</p>
              </el-card>
            </el-col>
          </el-row>

          <h4 style="margin-top: 20px;">故障頻率:</h4>
          <el-table :data="faultFrequencies" border>
            <el-table-column prop="type" label="故障類型" />
            <el-table-column prop="frequency" label="特徵頻率" />
            <el-table-column prop="description" label="說明" />
          </el-table>

          <h4 style="margin-top: 20px;">應用場景:</h4>
          <el-tag type="danger" style="margin: 5px;">滾動體缺陷檢測</el-tag>
          <el-tag type="warning" style="margin: 5px;">軌道損傷檢測</el-tag>
          <el-tag type="info" style="margin: 5px;">安裝問題診斷</el-tag>
        </el-collapse-item>

        <!-- Envelope Analysis -->
        <el-collapse-item title="包絡分析（Envelope Analysis）" name="envelope">
          <h3>原理說明</h3>
          <p>包絡分析透過希爾伯特轉換提取信號包絡，特別適合檢測週期性衝擊。</p>

          <h4>處理流程:</h4>
          <el-steps direction="vertical" :active="4">
            <el-step title="帶通濾波" description="選擇共振頻帶（如 4-10 kHz）" />
            <el-step title="希爾伯特轉換" description="計算解析信號" />
            <el-step title="提取包絡" description="取振幅包絡" />
            <el-step title="FFT 分析" description="對包絡做頻譜分析" />
            <el-step title="特徵識別" description="尋找 BPF 及諧波" />
          </el-steps>

          <h4 style="margin-top: 20px;">共振頻帶選擇:</h4>
          <el-table :data="resonanceBands" border>
            <el-table-column prop="series" label="滑軌系列" />
            <el-table-column prop="band" label="共振頻帶 (Hz)" />
            <el-table-column prop="reason" label="說明" />
          </el-table>

          <el-alert
            title="診斷準則"
            type="warning"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>包絡譜出現 BPF → 滾動體或軌道缺陷</li>
              <li>SNR > 3 → 缺陷顯著</li>
              <li>多個諧波 → 缺陷嚴重</li>
            </ul>
          </el-alert>
        </el-collapse-item>

        <!-- Wavelet Analysis -->
        <el-collapse-item title="小波分析（Wavelet Analysis）" name="wavelet">
          <h3>原理說明</h3>
          <p>小波分析提供時頻域聯合分析，適合檢測瞬態衝擊和非穩態信號。</p>

          <h4>方法對比:</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <h4>STFT（短時傅立葉轉換）</h4>
                <p>使用 Hann 和 Flattop 窗</p>
                <p>窗長: 128 / 256 點</p>
                <p>重疊: 95%</p>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <h4>CWT（連續小波轉換）</h4>
                <p>小波基: db8</p>
                <p>尺度: 1-64</p>
                <p>對應頻率: 800-2500 Hz</p>
              </el-card>
            </el-col>
          </el-row>

          <h4 style="margin-top: 20px;">NP4 特徵:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="定義">
              <code>NP4 = N·Σ(Z-μ)⁴ / [Σ(Z-μ)²]²</code>
            </el-descriptions-item>
            <el-descriptions-item label="物理意義">
              類似峰度，反映時頻能量分佈的集中程度
            </el-descriptions-item>
            <el-descriptions-item label="應用">
              檢測瞬態衝擊、局部缺陷
            </el-descriptions-item>
          </el-descriptions>

          <h4 style="margin-top: 20px;">應用場景:</h4>
          <el-tag type="danger" style="margin: 5px;">瞬態衝擊檢測</el-tag>
          <el-tag type="warning" style="margin: 5px;">異物進入檢測</el-tag>
          <el-tag type="info" style="margin: 5px;">早期微裂紋</el-tag>
        </el-collapse-item>

        <!-- Higher Order Statistics -->
        <el-collapse-item title="高階統計（Higher Order Statistics）" name="higher-order">
          <h3>原理說明</h3>
          <p>高階統計特徵對早期故障敏感，可檢測傳統方法難以發現的微小缺陷。</p>

          <h4>關鍵指標:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="NA4">
              <p>正規化四次矩（帶分段）</p>
              <code>NA4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²/M]²</code>
              <p>檢測諧波能量異常</p>
            </el-descriptions-item>
            <el-descriptions-item label="NA4S">
              <p>NA4 對比健康基線</p>
              <code>NA4S = NA4_defect / NA4_baseline</code>
              <p>更敏感的早期故障指標</p>
            </el-descriptions-item>
            <el-descriptions-item label="FM4">
              <p>四次矩比值</p>
              <code>FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²</code>
              <p>檢測邊帶能量</p>
            </el-descriptions-item>
            <el-descriptions-item label="M6A / M8A">
              <p>六次矩 / 八次矩</p>
              <p>對極早期故障敏感</p>
            </el-descriptions-item>
            <el-descriptions-item label="ER">
              <p>能量比</p>
              <code>ER = RMS_sideband / RMS_total</code>
              <p>邊帶能量占比</p>
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="診斷準則"
            type="success"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>NA4 > 3 → 早期微裂紋</li>
              <li>FM4 異常 → 邊帶能量增加</li>
              <li>M6A / M8A 上升 → 潤滑不良或極早期故障</li>
            </ul>
          </el-alert>
        </el-collapse-item>

        <!-- Preload Assessment -->
        <el-collapse-item title="預壓狀態評估" name="preload">
          <h3>原理說明</h3>
          <p>基於時域特徵評估線性滑軌的預壓狀態，確保設計預壓與實際相符。</p>

          <h4>CPC 預壓等級:</h4>
          <el-table :data="preloadLevels" border>
            <el-table-column prop="level" label="預壓等級" />
            <el-table-column prop="value" label="預壓值" />
            <el-table-column prop="rms_threshold" label="RMS 閾值" />
            <el-table-column prop="kurt_threshold" label="峰度閾值" />
          </el-table>

          <h4 style="margin-top: 20px;">診斷邏輯:</h4>
          <el-steps direction="vertical" :active="3">
            <el-step title="RMS 過低" description="振動 < 閾值 × 0.7 → 預壓失效（鬆動）" status="error" />
            <el-step title="峰度過高" description="Kurtosis > 閾值 → 預壓不足（產生間隙衝擊）" status="warning" />
            <el-step title="正常狀態" description="兩項指標均在範圍內" status="success" />
          </el-steps>

          <h4 style="margin-top: 20px;">維護建議:</h4>
          <el-tag type="danger" style="margin: 5px;">檢查預壓設定</el-tag>
          <el-tag type="warning" style="margin: 5px;">檢查安裝精度</el-tag>
          <el-tag type="info" style="margin: 5px;">重新預壓</el-tag>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <h2>演算法應用對應表</h2>
      </template>

      <el-table :data="algorithmMapping" border stripe>
        <el-table-column prop="module" label="專案模組" width="180" />
        <el-table-column prop="application" label="應用於線性滑軌" width="180" />
        <el-table-column prop="fault_type" label="檢測故障類型" />
        <el-table-column prop="cpc_params" label="CPC 參數關聯" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeAlgorithms = ref('time-domain')

const faultFrequencies = [
  { type: '滾動體缺陷', frequency: 'BPF（Ball Pass Frequency）', description: '滾動體通過頻率及諧波' },
  { type: '滾動體自轉', frequency: 'BSF（Ball Spin Frequency）', description: '滾動體自身旋轉頻率' },
  { type: '保持鏈', frequency: 'Cage Frequency', description: '保持鏈旋轉頻率' }
]

const resonanceBands = [
  { series: '微型 (MR)', band: '8,000 - 15,000', reason: '尺寸小，共振頻率高' },
  { series: '小型 (15/20/25)', band: '4,000 - 10,000', reason: '標準共振範圍' },
  { series: '中型 (30/35/45)', band: '2,000 - 8,000', reason: '尺寸增大，頻率降低' },
  { series: '大型 (55/65)', band: '1,000 - 6,000', reason: '大尺寸，低頻共振' }
]

const preloadLevels = [
  { level: 'VC', value: '微間隙', rms_threshold: '0.05', kurt_threshold: '4.0' },
  { level: 'V0', value: '0.02C（標準）', rms_threshold: '0.08', kurt_threshold: '4.5' },
  { level: 'V1', value: '0.05C（中預壓）', rms_threshold: '0.12', kurt_threshold: '5.0' },
  { level: 'V2', value: '0.08C（高預壓）', rms_threshold: '0.15', kurt_threshold: '5.5' }
]

const algorithmMapping = [
  { module: '時域特徵', application: '整體健康監控', fault_type: '磨損程度、預壓狀態', cpc_params: 'C₀, C₁₀₀, 預壓等級' },
  { module: '頻域特徵', application: '故障頻率識別', fault_type: '滾動體缺陷、軌道剝落', cpc_params: '滑座型式、滾動體數量' },
  { module: '小波特徵', application: '瞬態衝擊檢測', fault_type: '異物、局部缺陷', cpc_params: '密封片類型、環境條件' },
  { module: '濾波與高階統計', application: '早期故障檢測', fault_type: '微小缺陷、潤滑不良', cpc_params: '潤滑系統、摩擦阻力' },
  { module: '希爾伯特包絡', application: '滾動體故障', fault_type: '滾珠/滾子剝落', cpc_params: '基本動負荷 C₁₀₀' },
  { module: '諧波與邊帶', application: '安裝問題', fault_type: '平行度不良、預壓不均', cpc_params: '安裝精度、剛性' }
]
</script>

<style scoped>
.algorithms-page {
  padding: 20px;
}

h3 {
  color: #303133;
  margin-top: 15px;
  margin-bottom: 10px;
}

h4 {
  color: #606266;
  margin-top: 15px;
  margin-bottom: 10px;
}

code {
  background-color: #f5f7fa;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e6a23c;
}

p {
  color: #606266;
  line-height: 1.6;
  margin: 8px 0;
}
</style>
