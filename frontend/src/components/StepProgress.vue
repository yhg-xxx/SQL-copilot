<template>
  <div class="step-progress-container">
    <StarSpinner />
    <span class="step-text" :key="currentStep">{{ currentStep || '处理中...' }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StarSpinner from './StarSpinner.vue'

const props = defineProps({
  step: {
    type: String,
    default: ''
  }
})

const currentStep = computed(() => props.step)
</script>

<style scoped>
.step-progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-text {
  color: #606266;
  font-size: 14px;
  transition: opacity 0.3s ease;
}
</style>
