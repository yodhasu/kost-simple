<template>
  <Teleport to="body">
    <Transition name="base-modal-fade" appear>
      <div v-if="visible" class="base-modal-overlay" @click.self="onBackdropClick">
        <div class="base-modal-panel" :class="panelSizeClass" role="dialog" aria-modal="true">
          <button
            v-if="showClose"
            class="base-modal-close"
            type="button"
            @click="$emit('close')"
            aria-label="Close modal"
          >
            <span class="material-symbols-outlined">close</span>
          </button>

          <div class="base-modal-content">
            <slot />
          </div>

          <div v-if="showFooter" class="base-modal-footer">
            <slot name="footer">
              <button type="button" class="base-modal-btn base-modal-btn-cancel" @click="$emit('close')">
                {{ cancelText }}
              </button>
              <button type="button" class="base-modal-btn base-modal-btn-ok" @click="$emit('submit')">
                {{ submitText }}
              </button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    visible?: boolean
    size?: 'sm' | 'md' | 'lg' | 'xl'
    showClose?: boolean
    showFooter?: boolean
    closeOnBackdrop?: boolean
    cancelText?: string
    submitText?: string
  }>(),
  {
    visible: true,
    size: 'md',
    showClose: true,
    showFooter: false,
    closeOnBackdrop: true,
    cancelText: 'Batal',
    submitText: 'OK',
  }
)

const emit = defineEmits<{
  close: []
  submit: []
}>()

const panelSizeClass = computed(() => {
  const map = {
    sm: 'base-modal-sm',
    md: 'base-modal-md',
    lg: 'base-modal-lg',
    xl: 'base-modal-xl',
  }
  return map[props.size]
})

function onBackdropClick() {
  if (props.closeOnBackdrop) {
    emit('close')
  }
}
</script>

<style scoped>
.base-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 1000;
}

.base-modal-panel {
  position: relative;
  width: 100%;
  background: #ffffff;
  border: 1px solid rgba(31, 41, 55, 0.45);
  border-radius: 56px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.base-modal-sm {
  max-width: 560px;
}

.base-modal-md {
  max-width: 760px;
}

.base-modal-lg {
  max-width: 980px;
}

.base-modal-xl {
  max-width: 1180px;
}

.base-modal-close {
  position: absolute;
  left: 1.4rem;
  top: 1.2rem;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #111827;
  cursor: pointer;
}

.base-modal-close:hover {
  background: #eef2f7;
}

.base-modal-content {
  padding: 3.6rem 1.6rem 1.2rem;
  overflow-y: auto;
}

.base-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0.9rem 1.6rem 1.5rem;
}

.base-modal-btn {
  min-width: 104px;
  padding: 0.6rem 1.15rem;
  border: 1px solid #1f2937;
  border-radius: 10px;
  background: #fff;
  color: #111827;
  font-weight: 500;
  cursor: pointer;
}

.base-modal-btn-ok {
  background: #f3f4f6;
}

.base-modal-fade-enter-active,
.base-modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.base-modal-fade-enter-from,
.base-modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .base-modal-overlay {
    padding: 0.9rem;
  }

  .base-modal-panel {
    border-radius: 34px;
  }

  .base-modal-content {
    padding: 3.2rem 1rem 0.9rem;
  }

  .base-modal-footer {
    padding: 0.75rem 1rem 1rem;
  }
}
</style>
