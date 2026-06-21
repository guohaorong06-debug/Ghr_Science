<template>
  <div class="register-container">
    <div class="register-card">
      <h2>用户注册</h2>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="realName">
          <el-input v-model="form.realName" placeholder="真实姓名（可选）" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（可选）" />
        </el-form-item>
        <el-form-item prop="phone">
          <el-input v-model="form.phone" placeholder="手机号（可选）" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="handleRegister" class="register-btn">注册</el-button>
        <div class="footer">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  realName: '',
  email: '',
  phone: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await authApi.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

  h2 {
    text-align: center;
    margin-bottom: 30px;
    font-size: 24px;
    color: #333;
  }

  .register-btn {
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
  .register-card {
    width: 90%;
    padding: 30px 20px;
  }
}
</style>
