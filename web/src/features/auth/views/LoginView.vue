<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo -->
      <div class="login-header">
        <h1 class="logo">Kostan</h1>
        <p class="subtitle">Sistem Manajemen Kost</p>
      </div>

      <!-- Login Card -->
      <div class="login-card">
        <h2 class="card-title">Masuk ke Akun Anda</h2>
        
        <!-- Error Alert -->
        <div v-if="error" class="error-alert">
          <span class="material-symbols-outlined">error</span>
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input 
              v-model="email" 
              type="email" 
              class="form-input"
              placeholder="Masukkan email Anda"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <div class="password-input-wrapper">
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Masukkan password"
                required
                :disabled="loading"
              />
              <button 
                type="button" 
                class="toggle-password"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined">
                  {{ showPassword ? 'visibility_off' : 'visibility' }}
                </span>
              </button>
            </div>
          </div>

          <button type="submit" class="btn-login" :disabled="loading">
            <span v-if="loading" class="spinner-small"></span>
            {{ loading ? 'Memproses...' : 'Masuk' }}
          </button>
        </form>
      </div>

      <p class="footer-text">
        &copy; 2026 Kostan. All rights reserved.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../../shared/composables/useAuth'

const router = useRouter()
const { signIn, error: authError } = useAuth()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  
  try {
    await signIn(email.value, password.value)
    router.push('/')
  } catch (err: any) {
    error.value = authError.value || 'Login gagal'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 2.5rem;
  font-weight: 700;
  color: #00897B;
  margin: 0;
}

.subtitle {
  font-size: 0.875rem;
  color: #607D8B;
  margin-top: 0.25rem;
}

/* Card */
.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1F2937;
  text-align: center;
  margin-bottom: 1.5rem;
}

/* Form */
.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #4B5563;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #E5E7EB;
  border-radius: 0.5rem;
  background: #F9FAFB;
  color: #1F2937;
  transition: all 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: #00897B;
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 137, 123, 0.1);
}

.form-input::placeholder {
  color: #9CA3AF;
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Password Input */
.password-input-wrapper {
  position: relative;
}

.password-input-wrapper .form-input {
  padding-right: 3rem;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #9CA3AF;
  display: flex;
  align-items: center;
  padding: 0.25rem;
}

.toggle-password:hover {
  color: #6B7280;
}

/* Error Alert */
.error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 0.5rem;
  color: #DC2626;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.error-alert .material-symbols-outlined {
  font-size: 1.25rem;
}

/* Button */
.btn-login {
  width: 100%;
  padding: 0.875rem;
  font-size: 1rem;
  font-weight: 600;
  background: #00897B;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-login:hover:not(:disabled) {
  background: #00796B;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Spinner */
.spinner-small {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Footer */
.footer-text {
  text-align: center;
  font-size: 0.75rem;
  color: #607D8B;
  margin-top: 1.5rem;
}
</style>
