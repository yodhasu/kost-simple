<template>
  <div class="page">
    <div class="card">
      <h1>403</h1>
      <h2>Akses Ditolak</h2>
      <p>Anda tidak memiliki izin untuk membuka halaman ini.</p>
      <div class="actions">
        <button class="btn-secondary" @click="goHome">Ke Beranda</button>
        <button class="btn" @click="goSettings">Ke Pengaturan</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.replace('/')
}

function goSettings() {
  router.replace('/settings')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f9fafb;
  padding: 1.5rem;
}

.card {
  width: min(560px, 100%);
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  text-align: center;
}

h1 {
  margin: 0;
  font-size: 3rem;
  color: #111827;
}

h2 {
  margin: 0.25rem 0 0.75rem;
  font-size: 1.25rem;
  color: #111827;
}

p {
  margin: 0;
  color: #6b7280;
}

.actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn,
.btn-secondary {
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.btn {
  border: none;
  background: #0d9488;
  color: white;
}

.btn:hover {
  background: #0f766e;
}

.btn-secondary {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-secondary:hover {
  background: #f9fafb;
}
</style>

