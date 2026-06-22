<template>
  <div class="forecast-page">
    <el-row :gutter="20">
      <!-- 左侧：预测参数 -->
      <el-col :span="6">
        <el-card>
          <template #header>预测参数</template>
          <el-form :model="form" label-width="100px">
            <el-form-item label="选择网点">
              <el-select v-model="form.siteId" placeholder="请选择" filterable style="width: 100%">
                <el-option v-for="site in siteList" :key="site.id" :label="site.name" :value="site.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="起始日期">
              <el-date-picker v-model="form.startDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="天气条件">
              <el-select v-model="form.weather" placeholder="可选">
                <el-option label="晴" value="sunny" />
                <el-option label="雨" value="rainy" />
                <el-option label="雪" value="snowy" />
              </el-select>
            </el-form-item>
            <el-form-item label="促销活动">
              <el-switch v-model="form.promotion" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handlePredict" :loading="predicting" :disabled="!form.siteId || !form.startDate" style="width: 100%">
                开始预测
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 预警列表 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>预警通知</span>
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" />
            </div>
          </template>
          <el-empty v-if="alerts.length === 0" description="暂无预警" :image-size="60" />
          <div v-else class="alert-list">
            <div v-for="item in alerts" :key="item.alert.id" class="alert-item" :class="{ unread: !item.alert.isRead }" @click="handleAlertClick(item)">
              <el-tag :type="alertTypeMap[item.alert.alertLevel]" size="small">{{ alertLevelMap[item.alert.alertLevel] }}</el-tag>
              <div class="alert-content">
                <div class="alert-title">{{ item.siteName }}</div>
                <div class="alert-desc">{{ item.alert.alertDate }} 预计超载 {{ item.alert.overflowRatio.toFixed(1) }}%</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：预测结果 -->
      <el-col :span="18">
        <el-card v-loading="loading">
          <template #header>预测结果</template>
          <div v-if="forecastData.length === 0" style="text-align: center; padding: 60px">
            <el-empty description="请选择网点并开始预测" />
          </div>
          <div v-else>
            <div ref="chartRef" style="width: 100%; height: 400px"></div>
            <el-table :data="forecastData" border stripe style="margin-top: 20px">
              <el-table-column prop="forecastDate" label="日期" width="120" />
              <el-table-column prop="p10" label="10%分位数" width="120" />
              <el-table-column prop="median" label="中位数预测" width="120">
                <template #default="{ row }">
                  <span style="font-weight: bold; color: #409eff">{{ row.median }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="p90" label="90%分位数" width="120" />
              <el-table-column label="预警状态">
                <template #default="{ row }">
                  <el-tag v-if="row.alert" :type="alertTypeMap[row.alert.alertLevel]">
                    {{ alertLevelMap[row.alert.alertLevel] }}
                  </el-tag>
                  <span v-else style="color: #67c23a">正常</span>
                </template>
              </el-table-column>
              <el-table-column prop="modelVersion" label="模型版本" width="150" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { siteApi, type LogisticsSite } from '@/api/site'
import { forecastApi, type ForecastResult, type AlertRecord } from '@/api/forecast'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const siteList = ref<LogisticsSite[]>([])
const loading = ref(false)
const predicting = ref(false)
const forecastData = ref<ForecastResult[]>([])
const alerts = ref<Array<{ alert: AlertRecord; siteName: string }>>([])
const chartRef = ref()
let chartInstance: echarts.ECharts | null = null

const form = reactive({
  siteId: undefined as number | undefined,
  startDate: new Date().toISOString().split('T')[0],
  weather: '',
  promotion: false,
})

const alertLevelMap: Record<string, string> = {
  RED: '红色预警',
  YELLOW: '黄色预警',
  GREEN: '绿色预警',
}

const alertTypeMap: Record<string, any> = {
  RED: 'danger',
  YELLOW: 'warning',
  GREEN: 'success',
}

const unreadCount = computed(() => alerts.value.filter(a => !a.alert.isRead).length)

const loadSites = async () => {
  siteList.value = await siteApi.list()
}

const handlePredict = async () => {
  predicting.value = true
  try {
    const conditions = {
      weather: form.weather,
      promotion: form.promotion,
    }
    forecastData.value = await forecastApi.predict({
      siteId: form.siteId!,
      startDate: form.startDate,
      conditions,
    })
    ElMessage.success('预测完成')
    await nextTick()
    renderChart()
    loadAlerts()
  } finally {
    predicting.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = forecastData.value.map(d => d.forecastDate)
  const p10 = forecastData.value.map(d => d.p10)
  const median = forecastData.value.map(d => d.median)
  const p90 = forecastData.value.map(d => d.p90)

  const option = {
    title: { text: '预测区间瀑布图', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['10%分位数', '中位数', '90%分位数', '预测区间'], bottom: 10 },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value', name: '包裹量' },
    series: [
      {
        name: '预测区间',
        type: 'line',
        data: p90.map((val, idx) => [dates[idx], p10[idx], val]),
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
        stack: 'confidence',
        symbol: 'none',
      },
      {
        name: '10%分位数',
        type: 'line',
        data: p10,
        lineStyle: { type: 'dashed', color: '#909399' },
        symbol: 'none',
      },
      {
        name: '中位数',
        type: 'line',
        data: median,
        lineStyle: { width: 3, color: '#409eff' },
        symbol: 'circle',
      },
      {
        name: '90%分位数',
        type: 'line',
        data: p90,
        lineStyle: { type: 'dashed', color: '#909399' },
        symbol: 'none',
      },
    ],
  }

  chartInstance.setOption(option)
}

const loadAlerts = async () => {
  alerts.value = await forecastApi.getAlerts({ isRead: false })
}

const handleAlertClick = async (item: any) => {
  if (!item.alert.isRead) {
    await forecastApi.markRead(item.alert.id)
    item.alert.isRead = true
  }
}

onMounted(() => {
  loadSites()
  loadAlerts()
})
</script>

<style scoped lang="scss">
.forecast-page {
  .alert-list {
    max-height: 300px;
    overflow-y: auto;

    .alert-item {
      display: flex;
      gap: 10px;
      padding: 12px;
      border-bottom: 1px solid #eee;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #f5f7fa;
      }

      &.unread {
        background: #ecf5ff;
      }

      .alert-content {
        flex: 1;

        .alert-title {
          font-weight: bold;
          margin-bottom: 4px;
        }

        .alert-desc {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}
</style>
