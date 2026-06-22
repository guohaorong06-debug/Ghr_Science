<template>
  <div class="model-manage">
    <el-card>
      <template #header>
        <div class="header">
          <span>模型版本管理</span>
          <el-button type="primary" @click="showUploadDialog">上传新模型</el-button>
        </div>
      </template>

      <el-alert title="活跃模型用于预测服务，同时只能有一个活跃模型" type="info" :closable="false" style="margin-bottom: 20px" />

      <el-table :data="modelList" v-loading="loading" border stripe>
        <el-table-column prop="version" label="版本号" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.isActive" type="success" size="small">活跃</el-tag>
            {{ row.version }}
          </template>
        </el-table-column>
        <el-table-column prop="filePath" label="文件路径" show-overflow-tooltip />
        <el-table-column prop="fileSize" label="文件大小" width="120">
          <template #default="{ row }">{{ formatFileSize(row.fileSize) }}</template>
        </el-table-column>
        <el-table-column label="评估指标" width="200">
          <template #default="{ row }">
            <div v-if="row.metricsJson">
              <el-popover trigger="hover" placement="top" width="300">
                <template #reference>
                  <el-link type="primary">查看详情</el-link>
                </template>
                <pre style="font-size: 12px">{{ formatMetrics(row.metricsJson) }}</pre>
              </el-popover>
            </div>
            <span v-else style="color: #909399">--</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
        <el-table-column prop="createTime" label="上传时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.isActive" link type="primary" @click="handleActivate(row)">激活</el-button>
            <el-button v-else link disabled>当前活跃</el-button>
            <el-button v-if="!row.isActive" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadVisible" title="上传模型" width="500px">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="版本号" prop="version">
          <el-input v-model="uploadForm.version" placeholder="如: v1.0.0" />
        </el-form-item>
        <el-form-item label="模型文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pt,.pth"
            drag
          >
            <div style="padding: 20px">
              <el-icon size="50"><Upload /></el-icon>
              <div>点击或拖拽 .pt 或 .pth 文件</div>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="评估指标">
          <el-input v-model="uploadForm.metricsJson" type="textarea" :rows="4" placeholder='{"MAE": 45.23, "RMSE": 67.89}' />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { modelApi, type ModelVersion } from '@/api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const loading = ref(false)
const uploading = ref(false)
const uploadVisible = ref(false)
const modelList = ref<ModelVersion[]>([])
const uploadFormRef = ref()
const uploadRef = ref()

const uploadForm = reactive({
  version: '',
  file: null as File | null,
  metricsJson: '',
  description: '',
})

const uploadRules = {
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  file: [{ required: true, message: '请选择模型文件', trigger: 'change' }],
}

const loadModels = async () => {
  loading.value = true
  try {
    modelList.value = await modelApi.list()
  } finally {
    loading.value = false
  }
}

const showUploadDialog = () => {
  Object.assign(uploadForm, { version: '', file: null, metricsJson: '', description: '' })
  uploadVisible.value = true
}

const handleFileChange = (uploadFile: any) => {
  uploadForm.file = uploadFile.raw
}

const handleUpload = async () => {
  await uploadFormRef.value.validate()
  if (!uploadForm.file) {
    ElMessage.error('请选择文件')
    return
  }

  uploading.value = true
  try {
    await modelApi.upload(uploadForm.file, uploadForm.version, uploadForm.description, uploadForm.metricsJson)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    loadModels()
  } finally {
    uploading.value = false
  }
}

const handleActivate = async (row: ModelVersion) => {
  await ElMessageBox.confirm(`确认激活模型 ${row.version}？当前活跃模型将被替换`, '提示', { type: 'warning' })
  await modelApi.activate(row.id!)
  ElMessage.success('激活成功')
  loadModels()
}

const handleDelete = async (row: ModelVersion) => {
  await ElMessageBox.confirm(`确认删除模型 ${row.version}？文件将被永久删除`, '提示', { type: 'warning' })
  await modelApi.delete(row.id!)
  ElMessage.success('删除成功')
  loadModels()
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatMetrics = (json: string) => {
  try {
    return JSON.stringify(JSON.parse(json), null, 2)
  } catch {
    return json
  }
}

onMounted(loadModels)
</script>

<style scoped lang="scss">
.model-manage {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
