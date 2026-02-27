<template>
  <div class="toast-wrap" aria-live="polite" aria-relevant="additions">
    <BaseToast
      v-for="t in toasts"
      :key="t.id"
      :type="t.type"
      :message="t.message"
      @close="toastStore.remove(t.id)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToastStore } from '../../stores/toastStore'
import BaseToast from './BaseToast.vue'

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
</style>
