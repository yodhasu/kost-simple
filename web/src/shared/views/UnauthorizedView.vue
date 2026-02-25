<template>
  <div class="page">
    <div class="card">
      <h1>401</h1>
      <h2>Belum Login</h2>
      <p>Silakan login untuk melanjutkan.</p>
      <div class="actions">
        <button class="btn" @click="goLogin">Ke Login</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

function goLogin() {
  const redirect = (route.query.redirect as string) || '/'
  router.replace({ name: 'login', query: { redirect } })
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
}

.btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 10px;
  background: #0d9488;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.btn:hover {
  background: #0f766e;
}
</style>

