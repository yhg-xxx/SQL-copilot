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
        <Login v-if="activeTab === 'login'" @switch-to-register="activeTab = 'register'" />

        <!-- 注册表单 -->
        <Register v-else @switch-to-login="activeTab = 'login'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Star } from '@element-plus/icons-vue'
import Login from './Login.vue'
import Register from './Register.vue'

const activeTab = ref('login')
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
