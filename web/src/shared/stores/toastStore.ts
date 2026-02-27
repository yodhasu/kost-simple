import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface ToastItem {
  id: string
  type: ToastType
  message: string
  createdAt: number
  timeoutMs: number
}

function uid(): string {
  return `${Date.now()}_${Math.random().toString(16).slice(2)}`
}

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [] as ToastItem[],
  }),
  actions: {
    push(type: ToastType, message: string, timeoutMs = 2500) {
      const id = uid()
      const toast: ToastItem = { id, type, message, createdAt: Date.now(), timeoutMs }
      this.items.push(toast)

      window.setTimeout(() => {
        this.remove(id)
      }, timeoutMs)
    },
    remove(id: string) {
      this.items = this.items.filter((t) => t.id !== id)
    },
    clear() {
      this.items = []
    },
  },
})
