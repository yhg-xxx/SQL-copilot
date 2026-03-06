<template>
  <div class="auth-form glass-card">
    <h2 class="form-title">欢迎注册</h2>

    <el-form :model="registerForm" :rules="rules" ref="registerFormRef" class="register-form">
      <el-form-item prop="username">
        <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" class="custom-input">
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" size="large" class="custom-input" show-password>
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" size="large" class="custom-input" show-password>
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleRegister" :loading="loading" size="large" class="submit-btn">注册</el-button>
      </el-form-item>
      <div class="form-links center">
        <span class="text-muted">已有账号？</span>
        <a href="#" class="link-text primary" @click.prevent="$emit('switch-to-login')">
          立即登录
        </a>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

// 定义事件
const emit = defineEmits(['switch-to-login']);

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
    emit('switch-to-login');
  } catch (error) {
    console.error('注册失败:', error);
    ElMessage.error('注册失败，用户名可能已存在');
  } finally {
    loading.value = false;
  }
};
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

.register-form :deep(.el-form-item) {
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
</style>
