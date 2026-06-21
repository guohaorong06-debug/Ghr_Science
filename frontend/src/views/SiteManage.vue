<template>
  <div class="site-manage">
    <el-card>
      <template #header>
        <div class="header">
          <span>网点管理</span>
          <el-button type="primary" @click="showAddDialog">新增网点</el-button>
        </div>
      </template>

      <el-form :inline="true" @submit.prevent="handleSearch">
        <el-form-item>
          <el-input v-model="keyword" placeholder="搜索网点名称/网格ID" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="网点名称" />
        <el-table-column prop="gridId" label="网格ID" width="100" />
        <el-table-column label="经纬度" width="200">
          <template #default="{ row }">
            {{ row.longitude }}, {{ row.latitude }}
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="日处理能力" width="120" />
        <el-table-column prop="description" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            <el-button link @click="locateOnMap(row)">地图定位</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="网点名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="经度" prop="longitude">
          <el-input-number v-model="form.longitude" :precision="6" :min="-180" :max="180" style="width: 100%" />
        </el-form-item>
        <el-form-item label="纬度" prop="latitude">
          <el-input-number v-model="form.latitude" :precision="6" :min="-90" :max="90" style="width: 100%" />
        </el-form-item>
        <el-form-item label="网格ID" prop="gridId">
          <el-input-number v-model="form.gridId" :min="0" :max="59" style="width: 100%" />
        </el-form-item>
        <el-form-item label="日处理能力" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { siteApi, type LogisticsSite } from '@/api/site'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitLoading = ref(false)
const keyword = ref('')
const tableData = ref<LogisticsSite[]>([])
const pagination = reactive({ current: 1, size: 10, total: 0 })

const dialogVisible = ref(false)
const dialogTitle = ref('新增网点')
const formRef = ref()
const form = reactive<LogisticsSite>({
  name: '',
  longitude: 0,
  latitude: 0,
  capacity: 1000,
})

const rules = {
  name: [{ required: true, message: '请输入网点名称', trigger: 'blur' }],
  longitude: [{ required: true, message: '请输入经度', trigger: 'blur' }],
  latitude: [{ required: true, message: '请输入纬度', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入日处理能力', trigger: 'blur' }],
}

const loadData = async () => {
  loading.value = true
  try {
    const res: any = await siteApi.page({
      current: pagination.current,
      size: pagination.size,
      keyword: keyword.value,
    })
    tableData.value = res.records
    pagination.total = res.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  keyword.value = ''
  handleSearch()
}

const showAddDialog = () => {
  dialogTitle.value = '新增网点'
  Object.assign(form, { name: '', longitude: 0, latitude: 0, capacity: 1000, gridId: undefined, description: '' })
  dialogVisible.value = true
}

const handleEdit = (row: LogisticsSite) => {
  dialogTitle.value = '编辑网点'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (form.id) {
      await siteApi.update(form)
      ElMessage.success('更新成功')
    } else {
      await siteApi.add(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: LogisticsSite) => {
  await ElMessageBox.confirm('确认删除该网点？', '提示', { type: 'warning' })
  await siteApi.delete(row.id!)
  ElMessage.success('删除成功')
  loadData()
}

const locateOnMap = (row: LogisticsSite) => {
  ElMessage.info('地图功能开发中')
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.site-manage {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
