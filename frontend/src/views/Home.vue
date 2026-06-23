<template>
  <el-container class="home-container">
    <el-header>
      <div class="header-left">
        <h3>智能物流决策系统</h3>
      </div>
      <div class="header-right">
        <el-tag :type="roleTagType">{{ roleName }}</el-tag>
        <span>{{ userStore.userInfo?.realName || userStore.userInfo?.username }}</span>
        <el-button @click="handleLogout" type="danger" size="small">退出</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" v-if="userStore.token">
        <el-menu :default-active="$route.path" router>
          <!-- 仪表盘 - 所有角色可见 -->
          <el-menu-item index="/dashboard" v-if="!userStore.permissions || userStore.permissions.length === 0 || hasPermission('dashboard:view')">
            <el-icon><DataLine /></el-icon>
            <span>决策仪表盘</span>
          </el-menu-item>

          <!-- 网点管理 - 所有角色可见 -->
          <el-menu-item index="/site" v-if="!userStore.permissions || userStore.permissions.length === 0 || hasPermission('site:view')">
            <el-icon><Location /></el-icon>
            <span>网点管理</span>
          </el-menu-item>

          <!-- 数据导入 - 运营员和管理员可见 -->
          <el-menu-item index="/data-import" v-if="hasPermission('data:view')">
            <el-icon><Upload /></el-icon>
            <span>数据导入</span>
          </el-menu-item>

          <!-- 需求预测 - 所有角色可见 -->
          <el-menu-item index="/forecast" v-if="!userStore.permissions || userStore.permissions.length === 0 || hasPermission('forecast:view')">
            <el-icon><TrendCharts /></el-icon>
            <span>需求预测</span>
          </el-menu-item>

          <!-- 模型管理 - 所有角色可见 -->
          <el-menu-item index="/model" v-if="!userStore.permissions || userStore.permissions.length === 0 || hasPermission('model:view')">
            <el-icon><Setting /></el-icon>
            <span>模型管理</span>
          </el-menu-item>

          <!-- 管理员菜单 -->
          <el-sub-menu index="/admin" v-if="userStore.isAdmin">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/admin/users" v-if="hasPermission('admin:user:view')">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/roles" v-if="hasPermission('admin:role:view')">
              <el-icon><Avatar /></el-icon>
              <span>角色管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/permissions" v-if="hasPermission('admin:role:view')">
              <el-icon><Key /></el-icon>
              <span>权限管理</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  DataLine,
  Location,
  Upload,
  TrendCharts,
  Setting,
  Tools,
  User,
  Avatar,
  Key
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const hasPermission = (code: string) => {
  // 添加调试日志
  const result = userStore.hasPermission(code)
  console.log(`[权限检查] ${code}:`, result, '所有权限:', userStore.permissions)
  return result
}

const roleName = computed(() => {
  if (userStore.isAdmin) return '管理员'
  if (userStore.isOperator) return '运营员'
  if (userStore.isGuest) return '游客'
  return '未知'
})

const roleTagType = computed(() => {
  if (userStore.isAdmin) return 'danger'
  if (userStore.isOperator) return 'warning'
  if (userStore.isGuest) return 'info'
  return ''
})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped lang="scss">
.home-container {
  height: 100vh;

  .el-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #409eff;
    color: white;

    .header-left h3 {
      margin: 0;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;

      .el-tag {
        font-weight: bold;
      }
    }
  }

  .el-aside {
    background: #f5f7fa;
    overflow-y: auto;

    .el-menu {
      border-right: none;
    }

    .el-icon {
      margin-right: 8px;
    }
  }

  .el-main {
    background: #fff;
    overflow-y: auto;
  }
}
</style>
