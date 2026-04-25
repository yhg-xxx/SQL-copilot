<template>
  <div class="auth-form glass-card">
    <h2 class="form-title">欢迎使用数据灵犀</h2>

    <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
      <el-form-item prop="username">
        <el-input
          v-model="loginForm.username"
          placeholder="请输入账号名"
          size="large"
          class="custom-input"
        >
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="请输入密码"
          size="large"
          class="custom-input"
          show-password
        >
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <div class="form-options">
        <el-checkbox v-model="loginForm.remember" class="remember-check"> 记住密码 </el-checkbox>
      </div>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleLogin"
          :loading="loading"
          size="large"
          class="submit-btn"
          >登录</el-button
        >
      </el-form-item>
      <div class="form-links">
        <a href="#" class="link-text">忘记账号</a>
        <a href="#" class="link-text">忘记密码</a>
        <a href="#" class="link-text primary" @click.prevent="$emit('switch-to-register')">
          立即注册
        </a>
      </div>
    </el-form>

    <!-- 其他登录方式 -->
    <div class="other-login">
      <div class="divider">
        <span>其他登录方式</span>
      </div>
      <div class="social-icons">
        <button class="social-btn">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"
            />
          </svg>
        </button>
        <button class="social-btn">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"
            />
          </svg>
        </button>
        <button class="social-btn">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

// 定义事件
const emit = defineEmits(['switch-to-register'])

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  const valid = await loginFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const response = await axios.post(`/user/login`, {
      username: loginForm.username,
      password: loginForm.password
    })
    const { access_token, user } = response.data

    localStorage.setItem('token', access_token)
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      const userInfo = {
        username: loginForm.username
      }
      localStorage.setItem('user', JSON.stringify(userInfo))
    }
    ElMessage.success('登录成功')
    await router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 标题样式 */
.form-title {
  text-align: center;
  margin-bottom: 32px;
  margin-top: -10px;
  font-size: 24px;
  font-weight: 600;
  color: #1a2639;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

/* 自定义输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.3) inset;
  padding: 0 16px;
  height: 48px;
  background: rgba(255, 255, 255, 0.5);
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.5) inset;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4a89dc inset;
}

.custom-input :deep(.el-input__prefix) {
  color: #4a89dc;
  margin-right: 12px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.remember-check :deep(.el-checkbox__label) {
  color: #6b7280;
  font-size: 14px;
}

.remember-check :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #4a89dc;
  border-color: #4a89dc;
}

/* 提交按钮样式 */
.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  background: #4a89dc;
  border: none;
  box-shadow: 0 4px 15px rgba(74, 137, 220, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #3b7dd8;
  box-shadow: 0 6px 20px rgba(74, 137, 220, 0.4);
  transform: translateY(-2px);
}

.form-links {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.form-links.center {
  justify-content: center;
  gap: 8px;
}

.link-text {
  color: #6b7280;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s;
}

.link-text:hover {
  color: #4a89dc;
}

.link-text.primary {
  color: #4a89dc;
  font-weight: 500;
}

.text-muted {
  color: #9ca3af;
  font-size: 14px;
}

/* 其他登录方式 */
.other-login {
  margin-top: 32px;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(74, 137, 220, 0.2);
}

.divider span {
  padding: 0 16px;
  color: #9ca3af;
  font-size: 13px;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(74, 137, 220, 0.3);
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.social-btn:hover {
  border-color: #4a89dc;
  background: rgba(74, 137, 220, 0.1);
  box-shadow: 0 0 15px rgba(74, 137, 220, 0.2);
}

.social-btn svg {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.social-btn:hover svg {
  color: #4a89dc;
}
</style>
