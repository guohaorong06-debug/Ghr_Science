<template>
  <div class="login-container">
    <div class="login-card">
      <h2>智能物流决策系统</h2>
      <p class="subtitle">欢迎使用</p>

      <!-- 角色选择模式 -->
      <div class="role-selector" v-if="!selectedRole">
        <div class="role-intro">
          <p>请选择您的角色</p>
        </div>
        <div class="role-cards">
          <div
            v-for="role in roles"
            :key="role.code"
            :class="['role-card', role.code]"
            @click="selectRole(role)"
          >
            <el-icon :size="40">
              <component :is="role.icon" />
            </el-icon>
            <h3>{{ role.name }}</h3>
            <p>{{ role.desc }}</p>
            <div class="role-badge">{{ role.permissions }}个权限</div>
            <div class="role-action">{{ role.action }}</div>
          </div>
        </div>
      </div>

      <!-- 登录表单 -->
      <el-form
        v-else
        :model="form"
        :rules="rules"
        ref="formRef"
        @submit.prevent="handleLogin"
      >
        <div class="form-header">
          <h3>{{ currentRole?.name }}登录</h3>
          <el-button link @click="backToRoleSelection">切换角色</el-button>
        </div>

        <!-- 游客：无需表单，直接进入 -->
        <template v-if="selectedRole === 'guest'">
          <div class="guest-info">
            <el-icon :size="60" color="#409eff"><User /></el-icon>
            <p>游客模式</p>
            <p class="desc">无需登录，一键体验系统</p>
            <p class="permission-hint">只读权限 · 7个权限</p>
          </div>
          <el-button
            type="primary"
            @click="handleGuestLogin"
            :loading="loading"
            class="login-btn"
            size="large"
          >
            <el-icon><Right /></el-icon>
            立即进入
          </el-button>
        </template>

        <!-- 运营员：注册或登录 -->
        <template v-else-if="selectedRole === 'operator'">
          <el-tabs v-model="activeTab" class="login-tabs">
            <el-tab-pane label="登录" name="login">
              <el-form-item prop="username">
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  clearable
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  show-password
                />
              </el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                class="login-btn"
                size="large"
              >
                登录
              </el-button>
            </el-tab-pane>

            <el-tab-pane label="注册" name="register">
              <el-form-item prop="username">
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  clearable
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码（6位以上）"
                  prefix-icon="Lock"
                  show-password
                />
              </el-form-item>
              <el-form-item prop="realName">
                <el-input
                  v-model="form.realName"
                  placeholder="请输入真实姓名（可选）"
                  prefix-icon="Avatar"
                  clearable
                />
              </el-form-item>
              <el-button
                type="success"
                @click="handleRegister"
                :loading="loading"
                class="login-btn"
                size="large"
              >
                注册
              </el-button>
            </el-tab-pane>
          </el-tabs>
        </template>

        <!-- 管理员：固定账号登录 -->
        <template v-else-if="selectedRole === 'admin'">
          <div class="admin-notice">
            <el-alert
              title="管理员账号唯一"
              type="warning"
              :closable="false"
              show-icon
            >
              <p>账号：admin</p>
              <p>请输入管理员密码</p>
            </el-alert>
          </div>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入管理员密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleAdminLogin"
            />
          </el-form-item>
          <el-button
            type="danger"
            @click="handleAdminLogin"
            :loading="loading"
            class="login-btn"
            size="large"
          >
            管理员登录
          </el-button>
        </template>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Avatar, Setting, Right } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const selectedRole = ref('')
const activeTab = ref('login')

const roles = [
  {
    code: 'guest',
    name: '游客',
    desc: '一键体验，无需登录',
    icon: User,
    permissions: 7,
    action: '立即体验'
  },
  {
    code: 'operator',
    name: '运营员',
    desc: '注册账号，业务操作',
    icon: Avatar,
    permissions: 15,
    action: '登录/注册'
  },
  {
    code: 'admin',
    name: '管理员',
    desc: '系统管理，完整权限',
    icon: Setting,
    permissions: 27,
    action: '管理员登录'
  }
]

const form = reactive({
  username: '',
  password: '',
  realName: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const currentRole = computed(() => {
  return roles.find(r => r.code === selectedRole.value)
})

const selectRole = (role: typeof roles[0]) => {
  selectedRole.value = role.code
  form.username = ''
  form.password = ''
  form.realName = ''
  activeTab.value = 'login'
}

const backToRoleSelection = () => {
  selectedRole.value = ''
  form.username = ''
  form.password = ''
  form.realName = ''
}

// 游客登录（无需账号密码）
const handleGuestLogin = async () => {
  loading.value = true
  try {
    await userStore.login('guest', '123456')
    ElMessage.success('欢迎，游客')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}

// 运营员登录
const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success(`欢迎，${form.username}`)
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 运营员注册
const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    // 调用注册API
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.username,
        password: form.password,
        realName: form.realName || form.username
      })
    })

    if (response.ok) {
      ElMessage.success('注册成功，请登录')
      activeTab.value = 'login'
    } else {
      const data = await response.json()
      ElMessage.error(data.message || '注册失败')
    }
  } catch (error) {
    ElMessage.error('注册失败')
  } finally {
    loading.value = false
  }
}

// 管理员登录
const handleAdminLogin = async () => {
  if (!form.password) {
    ElMessage.warning('请输入管理员密码')
    return
  }
  loading.value = true
  try {
    await userStore.login('admin', form.password)
    ElMessage.success('欢迎，管理员')
    router.push('/')
  } catch (error) {
    ElMessage.error('密码错误')
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

  .role-intro {
    text-align: center;
    margin-bottom: 20px;

    p {
      font-size: 16px;
      color: #666;
    }
  }

  .role-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 20px;

    .role-card {
      padding: 30px 20px;
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      background: #fafafa;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      }

      &.guest:hover {
        border-color: #409eff;
        box-shadow: 0 8px 24px rgba(64, 158, 255, 0.3);
      }

      &.operator:hover {
        border-color: #67c23a;
        box-shadow: 0 8px 24px rgba(103, 194, 58, 0.3);
      }

      &.admin:hover {
        border-color: #f56c6c;
        box-shadow: 0 8px 24px rgba(245, 108, 108, 0.3);
      }

      .el-icon {
        color: #409eff;
        margin-bottom: 16px;
      }

      h3 {
        margin: 12px 0;
        font-size: 20px;
        color: #333;
      }

      p {
        margin: 8px 0;
        font-size: 14px;
        color: #666;
        min-height: 40px;
      }

      .role-badge {
        display: inline-block;
        margin: 12px 0;
        padding: 6px 16px;
        background: #409eff;
        color: white;
        border-radius: 16px;
        font-size: 13px;
      }

      .role-action {
        margin-top: 8px;
        font-size: 14px;
        color: #409eff;
        font-weight: 500;
      }
    }
  }

  .el-form {
    max-width: 450px;
    margin: 0 auto;

    .form-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;

      h3 {
        margin: 0;
        font-size: 20px;
        color: #333;
      }
    }

    .guest-info {
      text-align: center;
      padding: 30px 0;

      p {
        margin: 12px 0;
        font-size: 18px;
        font-weight: 500;
        color: #333;
      }

      .desc {
        font-size: 14px;
        color: #666;
        font-weight: normal;
      }

      .permission-hint {
        font-size: 13px;
        color: #409eff;
        font-weight: normal;
      }
    }

    .admin-notice {
      margin-bottom: 20px;

      p {
        margin: 8px 0;
        font-size: 14px;
      }
    }

    .login-tabs {
      margin-bottom: 20px;
    }
  }

  .login-btn {
    width: 100%;
    margin-top: 10px;
  }
}

@media (max-width: 768px) {
  .login-card {
    width: 95%;
    padding: 20px;

    .role-cards {
      grid-template-columns: 1fr;
    }
  }
}
</style>
