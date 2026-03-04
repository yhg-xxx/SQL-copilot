<template>
  <div class="auth-page">
    <!-- 背景装饰元素 -->
    <div class="bg-glow"></div>
    <div class="bg-grid"></div>

    <!-- 左侧品牌展示区域 -->
    <div class="brand-section">
      <div class="brand-header">
        <div class="brand-logo">
          <img src="../assets/logo.png" alt="Logo" class="logo-img" />
          <span class="logo-text">数据灵犀</span>
        </div>
      </div>

      <div class="brand-content">
        <h1 class="brand-title">多智能体协作，让数据查询更智能</h1>
        <div class="brand-badge">
          <el-icon><Star /></el-icon>
          <span>自然语言对话，复杂SQL一键生成</span>
        </div>

        <!-- 产品展示卡片 -->
        <div class="product-showcase">
          <div class="showcase-window glass-card">
            <div class="window-header">
              <div class="window-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <div class="window-content">
              <div class="chat-interface">
                <div class="chat-message">
                  <div class="avatar"></div>
                  <div class="message-content">
                    <div class="message-line"></div>
                    <div class="message-line short"></div>
                  </div>
                </div>
                <div class="chat-input">
                  <div class="input-box"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="brand-footer">
        <p>© 2026 多智能体数据库查询系统</p>
      </div>
    </div>

    <!-- 右侧登录注册表单区域 -->
    <div class="form-section">
      <div class="form-container">
        <!-- 登录表单 -->
        <div v-if="activeTab === 'login'" class="auth-form glass-card">
          <h2 class="form-title">欢迎使用多智能体数据库查询系统</h2>

          <!-- 登录方式切换 -->
          <div class="login-tabs">
            <button
              :class="['tab-btn', { active: loginType === 'phone' }]"
              @click="loginType = 'phone'"
            >
              手机号登录
            </button>
            <button
              :class="['tab-btn', { active: loginType === 'account' }]"
              @click="loginType = 'account'"
            >
              账号登录
            </button>
          </div>

          <!-- 登录表单 -->
          <el-form
            :model="loginForm"
            :rules="loginRules"
            ref="loginFormRef"
            class="login-form"
          >
            <el-form-item v-if="loginType === 'phone'" prop="phone">
              <el-input
                v-model="loginForm.phone"
                placeholder="请输入手机号码"
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item v-else prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入账号名/账号ID"
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
                placeholder="请输入登录密码"
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
              <el-checkbox v-model="loginForm.remember" class="remember-check">
                记住密码
              </el-checkbox>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                size="large"
                class="submit-btn"
              >
                登录
              </el-button>
            </el-form-item>

            <div class="form-links">
              <a href="#" class="link-text">忘记账号</a>
              <a href="#" class="link-text">忘记密码</a>
              <a href="#" class="link-text primary" @click.prevent="activeTab = 'register'">
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
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </button>
              <button class="social-btn">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
                </svg>
              </button>
              <button class="social-btn">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-else class="auth-form glass-card">
          <h2 class="form-title">欢迎注册</h2>

          <el-form
            :model="registerForm"
            :rules="registerRules"
            ref="registerFormRef"
            class="register-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
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
                v-model="registerForm.password"
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

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请确认密码"
                size="large"
                class="custom-input"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleRegister"
                :loading="loading"
                size="large"
                class="submit-btn"
              >
                注册
              </el-button>
            </el-form-item>

            <div class="form-links center">
              <span class="text-muted">已有账号？</span>
              <a href="#" class="link-text primary" @click.prevent="activeTab = 'login'">
                立即登录
              </a>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Star, User, Lock, Phone } from '@element-plus/icons-vue';

const router = useRouter();
const activeTab = ref('login');
const loginType = ref('account');
const loginFormRef = ref(null);
const registerFormRef = ref(null);
const loading = ref(false);

// 登录表单
const loginForm = reactive({
  username: '',
  phone: '',
  password: '',
  remember: false
});

// 注册表单
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

// 登录验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
};

// 注册验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return;

  const valid = await loginFormRef.value.validate();
  if (!valid) return;

  loading.value = true;
  try {
    const loginData = loginType.value === 'phone'
      ? { username: loginForm.phone, password: loginForm.password }
      : { username: loginForm.username, password: loginForm.password };

    const response = await axios.post('http://localhost:8000/user/login', loginData);
    const { access_token, user } = response.data;

    localStorage.setItem('token', access_token);
    // 存储用户信息到本地存储
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      // 如果响应中没有用户信息，使用登录表单中的用户名
      const userInfo = {
        username: loginType.value === 'phone' ? loginForm.phone : loginForm.username
      };
      localStorage.setItem('user', JSON.stringify(userInfo));
    }
    ElMessage.success('登录成功');
    await router.push('/');
  } catch (error) {
    console.error('登录失败:', error);
    ElMessage.error('登录失败，请检查用户名和密码');
  } finally {
    loading.value = false;
  }
};

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return;

  const valid = await registerFormRef.value.validate();
  if (!valid) return;

  loading.value = true;
  try {
    await axios.post('http://localhost:8000/user/register', {
      username: registerForm.username,
      password: registerForm.password
    });
    ElMessage.success('注册成功，请登录');
    activeTab.value = 'login';
  } catch (error) {
    console.error('注册失败:', error);
    ElMessage.error('注册失败，用户名可能已存在');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* CSS变量定义 - 与HomeView保持一致 */
:root {
  --primary-glow: #4a89dc;
  --secondary-glow: #6b9fde;
  --bg-deep: #f8f9fa;
  --bg-card: rgba(255, 255, 255, 0.8);
  --border-glow: rgba(74, 137, 220, 0.3);
  --text-primary: #1a2639;
  --text-secondary: #2c3e50;
  --accent-blue: #4a89dc;
}

.auth-page {
  display: flex;
  min-height: 100vh;
  position: relative;
  background: radial-gradient(ellipse at top, #e6f0ff, #d6e6ff);
  color: var(--text-primary);
  overflow-x: hidden;
}

/* 网格背景（蓝色） */
.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(74, 137, 220, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(74, 137, 220, 0.08) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* 大光晕（蓝色） */
.bg-glow {
  position: absolute;
  top: -20%;
  left: -10%;
  width: 120%;
  height: 60%;
  background: radial-gradient(circle, rgba(74, 137, 220, 0.2) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 60px;
  position: relative;
  z-index: 1;
}

.brand-header {
  margin-bottom: 60px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 8px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #4a89dc, #6b9fde);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}

.brand-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  color: #1a2639;
  margin-bottom: 20px;
  line-height: 1.2;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(74, 137, 220, 0.1);
  color: #4a89dc;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  width: fit-content;
  margin-bottom: 60px;
}

.product-showcase {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.showcase-window {
  width: 520px;
  height: 360px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
  overflow: hidden;
  border: 1px solid rgba(74, 137, 220, 0.2);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
}

.window-header {
  height: 40px;
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(74, 137, 220, 0.2);
}

.window-dots {
  display: flex;
  gap: 6px;
}

.window-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e1;
}

.window-content {
  padding: 24px;
  height: calc(100% - 40px);
}

.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4a89dc 0%, #6b9fde 100%);
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-line {
  height: 16px;
  background: rgba(74, 137, 220, 0.1);
  border-radius: 8px;
  width: 80%;
}

.message-line.short {
  width: 50%;
}

.chat-input {
  margin-top: auto;
}

.input-box {
  height: 48px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(74, 137, 220, 0.2);
}

.brand-footer {
  margin-top: auto;
  padding-top: 40px;
  text-align: center;
}

.brand-footer p {
  color: #6b7280;
  font-size: 12px;
}

/* 右侧表单区域 */
.form-section {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  z-index: 1;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

/* 玻璃卡片效果 - 与HomeView一致 */
.glass-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
}

.auth-form {
  padding: 48px;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a2639;
  margin-bottom: 32px;
  text-align: center;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.login-tabs {
  display: flex;
  gap: 32px;
  margin-bottom: 28px;
  border-bottom: 1px solid rgba(74, 137, 220, 0.2);
}

.tab-btn {
  background: none;
  border: none;
  padding: 12px 0;
  font-size: 15px;
  color: #6b7280;
  cursor: pointer;
  position: relative;
  transition: color 0.3s;
}

.tab-btn:hover {
  color: #4a89dc;
}

.tab-btn.active {
  color: #4a89dc;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #4a89dc;
  border-radius: 2px;
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .brand-section {
    display: none;
  }

  .form-section {
    width: 100%;
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .auth-form {
    padding: 32px 24px;
    border-radius: 16px;
  }

  .form-title {
    font-size: 20px;
  }
}
</style>
