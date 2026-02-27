<template>
  <div class="toast" :class="`toast-${type}`" role="status" aria-live="polite">
    <span class="toast-msg">{{ message }}</span>
    <button class="toast-close" type="button" @click="$emit('close')" aria-label="Tutup">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
}>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 0.875rem;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: white;
}

.toast-success {
  border-color: rgba(5, 150, 105, 0.25);
}

.toast-error {
  border-color: rgba(220, 38, 38, 0.25);
}

.toast-info {
  border-color: rgba(59, 130, 246, 0.25);
}

.toast-warning {
  border-color: rgba(245, 158, 11, 0.35);
}

.toast-msg {
  font-size: 0.875rem;
  color: #111827;
  line-height: 1.3;
  flex: 1;
}

.toast-close {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: #9ca3af;
  cursor: pointer;
}

.toast-close:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.toast-close .material-symbols-outlined {
  font-size: 1.125rem;
}
</style>
