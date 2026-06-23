<template>
  <div class="login-container">
    <div class="login-card">
      <h2>智能物流决策系统</h2>
      <p class="subtitle">请选择登录角色</p>

      <!-- 角色选择 -->
      <div class="role-selector">
        <div
          v-for="role in roles"
          :key="role.code"
          :class="['role-card', { active: selectedRole === role.code }]"
          @click="selectRole(role)"
        >
          <el-icon :size="32">
            <component :is="role.icon" />
          </el-icon>
          <h3>{{ role.name }}</h3>
          <p>{{ role.desc }}</p>
          <div class="role-badge">{{ role.permissions }}个权限</div>
        </div>
      </div>

      <!-- 登录表单 -->
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        @submit.prevent="handleLogin"
        v-if="selectedRole"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            :disabled="isQuickLogin"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            :disabled="isQuickLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleLogin"
          class="login-btn"
        >
          {{ isQuickLogin ? '快速登录' : '登录' }}
        </el-button>
        <div class="footer">
          <a @click="clearSelection" style="cursor: pointer">切换角色</a>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Avatar, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const selectedRole = ref('')

const roles = [
  {
    code: 'guest',
    name: '游客',
    desc: '只读权限，查看数据',
    icon: User,
    permissions: 7,
    username: 'guest',
    password: '123456'
  },
  {
    code: 'operator',
    name: '运营员',
    desc: '业务操作，管理网点和数据',
    icon: Avatar,
    permissions: 15,
    username: 'operator',
    password: '123456'
  },
  {
    code: 'admin',
    name: '管理员',
    desc: '完整权限，系统管理',
    icon: Setting,
    permissions: 27,
    username: 'admin',
    password: '123456'
  }
]

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const isQuickLogin = computed(() => {
  return form.username && form.password && selectedRole.value
})

const selectRole = (role: typeof roles[0]) => {
  selectedRole.value = role.code
  form.username = role.username
  form.password = role.password
}

const clearSelection = () => {
  selectedRole.value = ''
  form.username = ''
  form.password = ''
}

const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success(`欢迎，${roles.find(r => r.code === selectedRole.value)?.name}`)
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 900px;
  max-width: 95vw;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

  h2 {
    text-align: center;
    margin-bottom: 10px;
    font-size: 28px;
    color: #333;
  }

  .subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
  }

  .role-selector {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 30px;

    .role-card {
      padding: 24px;
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      background: #fafafa;

      &:hover {
        border-color: #409eff;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
      }

      &.active {
        border-color: #409eff;
        background: #ecf5ff;
        box-shadow: 0 8px 24px rgba(64, 158, 255, 0.3);
      }

      .el-icon {
        color: #409eff;
        margin-bottom: 12px;
      }

      h3 {
        margin: 8px 0;
        font-size: 18px;
        color: #333;
      }

      p {
        margin: 8px 0;
        font-size: 13px;
        color: #666;
        min-height: 40px;
      }

      .role-badge {
        display: inline-block;
        margin-top: 8px;
        padding: 4px 12px;
        background: #409eff;
        color: white;
        border-radius: 12px;
        font-size: 12px;
      }
    }
  }

  .el-form {
    max-width: 400px;
    margin: 0 auto;
  }

  .login-btn {
    width: 100%;
    margin-top: 10px;
  }

  .footer {
    text-align: center;
    margin-top: 20px;
    a {
      color: #409eff;
      text-decoration: none;
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

@media (max-width: 768px) {
  .login-card {
    width: 95%;
    padding: 20px;

    .role-selector {
      grid-template-columns: 1fr;
    }
  }
}
</style>
