<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>IdiotsMS</h1>
        <p>Welcome Back</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            maxlength="12"
            placeholder="Enter username"
            :class="{ 'error': errors.username }"
            @blur="validateUsername"
          />
          <span class="char-count">{{ formData.username.length }}/12</span>
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            maxlength="12"
            placeholder="Enter password"
            :class="{ 'error': errors.password }"
            @blur="validatePassword"
          />
          <span class="char-count">{{ formData.password.length }}/12</span>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div v-if="authStore.error" class="error-message global-error">
          {{ authStore.error }}
        </div>

        <button
          type="submit"
          class="auth-button"
          :disabled="!isFormValid || authStore.loading"
        >
          <span v-if="authStore.loading" class="loading-spinner"></span>
          {{ authStore.loading ? 'Signing In...' : 'Sign In' }}
        </button>

        <div class="auth-footer">
          <p>Don't have an account? <router-link to="/register">Create Account</router-link></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const formData = ref({
      username: '',
      password: ''
    })

    const errors = ref({
      username: '',
      password: ''
    })

    const validateUsername = () => {
      const username = formData.value.username.trim()

      if (!username) {
        errors.value.username = 'Username is required'
        return false
      }

      if (username.length < 3 || username.length > 12) {
        errors.value.username = 'Username must be 3-12 characters'
        return false
      }

      if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        errors.value.username = 'Username can only contain letters, numbers, and underscores'
        return false
      }

      errors.value.username = ''
      return true
    }

    const validatePassword = () => {
      const password = formData.value.password

      if (!password) {
        errors.value.password = 'Password is required'
        return false
      }

      if (password.length < 8 || password.length > 12) {
        errors.value.password = 'Password must be 8-12 characters'
        return false
      }

      errors.value.password = ''
      return true
    }

    const isFormValid = computed(() => {
      return formData.value.username.trim() &&
             formData.value.password &&
             !errors.value.username &&
             !errors.value.password
    })

    const handleLogin = async () => {
      validateUsername()
      validatePassword()

      if (!isFormValid.value) return

      const result = await authStore.login({
        username: formData.value.username.trim(),
        password: formData.value.password
      })

      if (result.success) {
        router.push('/dashboard')
      }
    }

    return {
      formData,
      errors,
      authStore,
      isFormValid,
      validateUsername,
      validatePassword,
      handleLogin
    }
  }
}
</script>

<style scoped>
.auth-container {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: 20px;
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-2xl);
  padding: 40px 32px;
  box-shadow: var(--shadow-xl);
  transition: all 0.3s ease;
}

.auth-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15), 0 15px 15px -5px rgba(0, 0, 0, 0.08);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header h1 {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.auth-header p {
  color: var(--text-secondary);
  font-size: 1.125rem;
  font-weight: 500;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
}

.form-group input {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: 1rem;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
  background: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), var(--shadow-md);
  transform: translateY(-1px);
}

.form-group input.error {
  border-color: var(--error-color);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-group input::placeholder {
  color: var(--text-tertiary);
  font-weight: 400;
}

.char-count {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: 0.75rem;
  font-weight: 500;
  pointer-events: none;
  margin-top: 12px;
  background: var(--bg-primary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.error-message {
  color: var(--error-color);
  font-size: 0.813rem;
  font-weight: 500;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-message::before {
  content: "⚠";
  font-size: 0.875rem;
}

.global-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
  font-weight: 500;
}

.auth-button {
  background: var(--primary-gradient);
  color: white;
  border: none;
  padding: 18px 24px;
  border-radius: var(--radius-lg);
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.auth-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.auth-button:hover:not(:disabled)::before {
  left: 100%;
}

.auth-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-md);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-sm);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.auth-footer p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

.auth-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.auth-footer a:hover {
  color: #5a67d8;
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 640px) {
  .auth-container {
    padding: 16px;
  }

  .auth-card {
    padding: 32px 24px;
    border-radius: var(--radius-xl);
  }

  .auth-header h1 {
    font-size: 2.25rem;
  }

  .auth-header p {
    font-size: 1rem;
  }

  .form-group input {
    padding: 14px 16px;
    font-size: 0.938rem;
  }

  .auth-button {
    padding: 16px 20px;
    font-size: 0.938rem;
  }
}

@media (max-width: 480px) {
  .auth-container {
    padding: 12px;
  }

  .auth-card {
    padding: 24px 20px;
    border-radius: var(--radius-lg);
  }

  .auth-header h1 {
    font-size: 2rem;
  }

  .auth-header p {
    font-size: 0.938rem;
  }

  .auth-form {
    gap: 20px;
  }

  .form-group input {
    padding: 12px 16px;
    font-size: 0.875rem;
  }

  .auth-button {
    padding: 14px 18px;
    font-size: 0.875rem;
  }

  .char-count {
    font-size: 0.688rem;
    padding: 1px 4px;
  }
}

@media (max-width: 360px) {
  .auth-card {
    padding: 20px 16px;
  }

  .auth-header h1 {
    font-size: 1.875rem;
  }

  .form-group input {
    padding: 12px 14px;
  }

  .auth-button {
    padding: 12px 16px;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .auth-card {
    background: rgba(31, 41, 55, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .form-group input {
    background: var(--bg-secondary);
    border-color: var(--border-color);
  }

  .char-count {
    background: var(--bg-secondary);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .auth-card {
    border: 2px solid var(--text-primary);
  }

  .form-group input {
    border: 2px solid var(--text-primary);
  }

  .auth-button {
    border: 2px solid var(--text-primary);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
