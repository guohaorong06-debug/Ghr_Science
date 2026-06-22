<template>
  <el-container class="home-container">
    <el-header>
      <div class="header-left">
        <h3>智能物流决策系统</h3>
      </div>
      <div class="header-right">
        <span>{{ userStore.userInfo?.realName || userStore.userInfo?.username }}</span>
        <el-button @click="handleLogout" type="danger" size="small">退出</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/dashboard">
            <span>决策仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/site">
            <span>网点管理</span>
          </el-menu-item>
          <el-menu-item index="/data-import">
            <span>数据导入</span>
          </el-menu-item>
          <el-menu-item index="/forecast">
            <span>需求预测</span>
          </el-menu-item>
          <el-menu-item index="/model">
            <span>模型管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

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
    }
  }

  .el-aside {
    background: #f5f7fa;
  }

  .el-main {
    background: #fff;
  }
}
</style>
