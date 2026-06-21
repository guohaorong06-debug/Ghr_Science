<template>
  <div class="data-import">
    <el-card>
      <template #header>数据导入</template>

      <el-steps :active="step" finish-status="success" align-center>
        <el-step title="上传文件" />
        <el-step title="预览数据" />
        <el-step title="导入完成" />
      </el-steps>

      <!-- Step 1: 上传 -->
      <div v-if="step === 0" class="upload-section">
        <el-upload
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept=".csv"
        >
          <div class="upload-content">
            <el-icon size="80"><Upload /></el-icon>
            <div>点击或拖拽CSV文件到此处</div>
            <div class="tip">仅支持CSV格式，格式：网点ID,日期,包裹量,是否节假日,天气,温度,降水,风速</div>
          </div>
        </el-upload>
        <el-button type="primary" @click="handlePreview" :disabled="!file" :loading="loading" style="margin-top: 20px">
          预览数据
        </el-button>
      </div>

      <!-- Step 2: 预览 -->
      <div v-if="step === 1" class="preview-section">
        <el-alert title="预览前100条记录，确认无误后点击导入" type="info" :closable="false" style="margin: 20px 0" />
        <el-table :data="previewData" border stripe max-height="400">
          <el-table-column prop="siteId" label="网点ID" width="100" />
          <el-table-column prop="recordDate" label="日期" width="120" />
          <el-table-column prop="volume" label="包裹量" width="100" />
          <el-table-column prop="isHoliday" label="节假日" width="80">
            <template #default="{ row }">{{ row.isHoliday ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column prop="weather" label="天气" width="80" />
          <el-table-column prop="temperature" label="温度(℃)" width="100" />
          <el-table-column prop="precipitation" label="降水(mm)" width="100" />
          <el-table-column prop="windSpeed" label="风速(km/h)" width="100" />
        </el-table>
        <div style="margin-top: 20px; display: flex; gap: 10px">
          <el-button @click="step = 0">返回</el-button>
          <el-button type="primary" @click="handleImport" :loading="loading">确认导入</el-button>
        </div>
      </div>

      <!-- Step 3: 完成 -->
      <div v-if="step === 2" class="result-section">
        <el-result icon="success" title="导入成功" :sub-title="resultMessage">
          <template #extra>
            <el-button type="primary" @click="resetUpload">继续导入</el-button>
            <el-button @click="viewRecords">查看记录</el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 历史记录 -->
    <el-card style="margin-top: 20px">
      <template #header>历史记录</template>
      <el-form :inline="true">
        <el-form-item label="网点ID">
          <el-input-number v-model="queryForm.siteId" :min="1" clearable />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRecords">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="records" v-loading="recordLoading" border stripe>
        <el-table-column prop="siteId" label="网点ID" width="100" />
        <el-table-column prop="recordDate" label="日期" width="120" />
        <el-table-column prop="volume" label="包裹量" width="100" />
        <el-table-column prop="isHoliday" label="节假日" width="80">
          <template #default="{ row }">{{ row.isHoliday ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column prop="weather" label="天气" />
        <el-table-column prop="temperature" label="温度(℃)" />
      </el-table>
      <el-pagination
        v-model:current-page="recordPagination.current"
        v-model:page-size="recordPagination.size"
        :total="recordPagination.total"
        layout="total, prev, pager, next"
        @current-change="loadRecords"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { dataApi, type DemandRecord } from '@/api/data'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const step = ref(0)
const loading = ref(false)
const file = ref<File | null>(null)
const previewData = ref<DemandRecord[]>([])
const resultMessage = ref('')

const handleFileChange = (uploadFile: any) => {
  file.value = uploadFile.raw
}

const handlePreview = async () => {
  if (!file.value) return
  loading.value = true
  try {
    previewData.value = await dataApi.preview(file.value)
    step.value = 1
  } catch (error) {
    // 拦截器已处理
  } finally {
    loading.value = false
  }
}

const handleImport = async () => {
  if (!file.value) return
  loading.value = true
  try {
    const msg = await dataApi.import(file.value)
    resultMessage.value = msg
    step.value = 2
  } finally {
    loading.value = false
  }
}

const resetUpload = () => {
  step.value = 0
  file.value = null
  previewData.value = []
}

const viewRecords = () => {
  loadRecords()
}

// 历史记录
const recordLoading = ref(false)
const records = ref<DemandRecord[]>([])
const dateRange = ref<string[]>([])
const queryForm = reactive({ siteId: undefined as number | undefined })
const recordPagination = reactive({ current: 1, size: 20, total: 0 })

const loadRecords = async () => {
  recordLoading.value = true
  try {
    const res: any = await dataApi.records({
      current: recordPagination.current,
      size: recordPagination.size,
      siteId: queryForm.siteId,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1],
    })
    records.value = res.records
    recordPagination.total = res.total
  } finally {
    recordLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.data-import {
  .upload-section,
  .preview-section,
  .result-section {
    padding: 40px 20px;
  }

  .upload-content {
    text-align: center;
    padding: 40px;

    .tip {
      margin-top: 10px;
      font-size: 12px;
      color: #999;
    }
  }
}
</style>
