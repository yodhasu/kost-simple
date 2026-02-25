<template>
  <div class="toast-wrap" aria-live="polite" aria-relevant="additions">
    <div v-for="t in toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">
      <span class="toast-msg">{{ t.message }}</span>
      <button class="toast-close" type="button" @click="toastStore.remove(t.id)" aria-label="Tutup">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToastStore } from '../../stores/toastStore'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.items)
</script>

<style scoped>
.toast-wrap {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: min(360px, calc(100vw - 2rem));
}

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

