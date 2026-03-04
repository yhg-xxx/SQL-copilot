<template>
  <div class="register-page">
    <!-- 背景装饰元素 -->
    <div class="bg-glow"></div>
    <div class="bg-grid"></div>

    <div class="register-container glass-card">
      <h2 class="register-title">用户注册</h2>
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="80px" class="register-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" class="custom-input">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" class="custom-input" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" class="custom-input" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" class="submit-btn">注册</el-button>
          <el-button @click="goToLogin" class="secondary-btn">去登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

const router = useRouter();
const registerFormRef = ref(null);
const loading = ref(false);

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (value, callback) => {
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
    await router.push('/login');
  } catch (error) {
    console.error('注册失败:', error);
    ElMessage.error('注册失败，用户名可能已存在');
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: radial-gradient(ellipse at top, #e6f0ff, #d6e6ff);
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

/* 玻璃卡片效果 */
.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(74, 137, 220, 0.2);
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(74, 137, 220, 0.15);
}

.register-container {
  width: 100%;
  max-width: 450px;
  padding: 48px;
  position: relative;
  z-index: 1;
}

.register-title {
  text-align: center;
  margin-bottom: 32px;
  font-size: 28px;
  font-weight: 600;
  background: linear-gradient(135deg, #1a2639, #2b4b7a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.register-form :deep(.el-form-item__label) {
  color: #1a2639;
  font-weight: 500;
}

/* 自定义输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(74, 137, 220, 0.3) inset;
  padding: 0 16px;
  height: 44px;
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
  margin-right: 8px;
}

/* 提交按钮样式 */
.submit-btn {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  background: #4a89dc;
  border: none;
  box-shadow: 0 4px 15px rgba(74, 137, 220, 0.3);
  transition: all 0.3s ease;
  margin-bottom: 12px;
}

.submit-btn:hover {
  background: #3b7dd8;
  box-shadow: 0 6px 20px rgba(74, 137, 220, 0.4);
  transform: translateY(-2px);
}

/* 次要按钮样式 */
.secondary-btn {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  background: transparent;
  border: 1px solid rgba(74, 137, 220, 0.5);
  color: #4a89dc;
  transition: all 0.3s ease;
}

.secondary-btn:hover {
  background: rgba(74, 137, 220, 0.1);
  border-color: #4a89dc;
  box-shadow: 0 4px 15px rgba(74, 137, 220, 0.2);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-container {
    padding: 32px 24px;
    margin: 20px;
    border-radius: 16px;
  }

  .register-title {
    font-size: 24px;
  }
}
</style>
