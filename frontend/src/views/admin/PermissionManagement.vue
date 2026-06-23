<template>
  <div class="permission-management">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <h2>权限管理</h2>
          <span class="subtitle">管理系统权限和访问控制</span>
        </div>
        <el-button type="primary" @click="handleAdd" v-if="hasPermission('admin:role:add')">
          <el-icon><Plus /></el-icon>
          添加权限
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table :data="permissions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="permissionCode" label="权限编码" min-width="180" />
        <el-table-column prop="permissionName" label="权限名称" min-width="120" />
        <el-table-column prop="module" label="所属模块" width="100">
          <template #default="{ row }">
            <el-tag :type="getModuleTagType(row.module)">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resourceType" label="资源类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.resourceType)" size="small">
              {{ row.resourceType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="apiPath" label="API路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="apiMethod" label="方法" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.apiMethod" :type="getMethodTagType(row.apiMethod)" size="small">
              {{ row.apiMethod }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleEdit(row)"
              v-if="hasPermission('admin:role:edit')"
            >
              编辑
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
              v-if="hasPermission('admin:role:delete')"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchPermissions"
          @current-change="fetchPermissions"
        />
      </div>
    </el-card>

    <!-- 添加/编辑权限对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="权限编码" prop="permissionCode">
          <el-input v-model="form.permissionCode" placeholder="如: site:add" />
        </el-form-item>
        <el-form-item label="权限名称" prop="permissionName">
          <el-input v-model="form.permissionName" placeholder="如: 添加网点" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-select v-model="form.module" placeholder="选择模块" style="width: 100%">
            <el-option label="仪表盘" value="dashboard" />
            <el-option label="网点管理" value="site" />
            <el-option label="数据导入" value="data" />
            <el-option label="需求预测" value="forecast" />
            <el-option label="模型管理" value="model" />
            <el-option label="系统管理" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型" prop="resourceType">
          <el-select v-model="form.resourceType" placeholder="选择资源类型" style="width: 100%">
            <el-option label="菜单" value="menu" />
            <el-option label="按钮" value="button" />
            <el-option label="API" value="api" />
          </el-select>
        </el-form-item>
        <el-form-item label="API路径" prop="apiPath">
          <el-input v-model="form.apiPath" placeholder="/api/logistics/site" />
        </el-form-item>
        <el-form-item label="HTTP方法" prop="apiMethod">
          <el-select v-model="form.apiMethod" placeholder="选择HTTP方法" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="form.sortOrder" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { permissionApi } from '@/api/permission'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const permissions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('添加权限')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  permissionCode: '',
  permissionName: '',
  module: '',
  resourceType: '',
  apiPath: '',
  apiMethod: '',
  sortOrder: 0
})

const rules = {
  permissionCode: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  permissionName: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  module: [{ required: true, message: '请选择所属模块', trigger: 'change' }],
  resourceType: [{ required: true, message: '请选择资源类型', trigger: 'change' }]
}

// 获取权限列表
const fetchPermissions = async () => {
  loading.value = true
  try {
    const { data } = await permissionApi.list()
    permissions.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

// 检查用户权限
const hasPermission = (code) => {
  return userStore.hasPermission(code)
}

// 模块标签颜色
const getModuleTagType = (module) => {
  const types = {
    dashboard: 'success',
    site: 'primary',
    data: 'warning',
    forecast: 'danger',
    model: 'info',
    admin: ''
  }
  return types[module] || ''
}

// 资源类型标签颜色
const getTypeTagType = (type) => {
  const types = {
    menu: 'primary',
    button: 'success',
    api: 'info'
  }
  return types[type] || ''
}

// HTTP方法标签颜色
const getMethodTagType = (method) => {
  const types = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger'
  }
  return types[method] || ''
}

// 添加权限
const handleAdd = () => {
  dialogTitle.value = '添加权限'
  resetForm()
  dialogVisible.value = true
}

// 编辑权限
const handleEdit = (row) => {
  dialogTitle.value = '编辑权限'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 删除权限
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限 "${row.permissionName}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await permissionApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (form.id) {
      await permissionApi.update(form)
      ElMessage.success('更新成功')
    } else {
      await permissionApi.create(form)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchPermissions()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
}

// 重置表单
const resetForm = () => {
  form.id = null
  form.permissionCode = ''
  form.permissionName = ''
  form.module = ''
  form.resourceType = ''
  form.apiPath = ''
  form.apiMethod = ''
  form.sortOrder = 0
  formRef.value?.clearValidate()
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped lang="scss">
.permission-management {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .title-section {
    h2 {
      margin: 0 0 8px 0;
      font-size: 20px;
      font-weight: 500;
    }

    .subtitle {
      color: #909399;
      font-size: 14px;
    }
  }

  .table-card {
    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
