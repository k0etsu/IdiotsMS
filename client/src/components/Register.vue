<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>IdiotsMS</h1>
        <p>Create Account</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            maxlength="12"
            placeholder="Enter username (4-12 chars)"
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
            placeholder="Enter password (5-12 characters)"
            :class="{ 'error': errors.password }"
            @blur="validatePassword"
          />
          <span class="char-count">{{ formData.password.length }}/12</span>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="formData.confirmPassword"
            type="password"
            maxlength="12"
            placeholder="Confirm password"
            :class="{ 'error': errors.confirmPassword }"
            @blur="validateConfirmPassword"
          />
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
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
          {{ authStore.loading ? 'Creating Account...' : 'Create Account' }}
        </button>

        <div class="auth-footer">
          <p>Already have an account? <router-link to="/login">Sign In</router-link></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const formData = ref({
      username: '',
      password: '',
      confirmPassword: ''
    })

    const errors = ref({
      username: '',
      password: '',
      confirmPassword: ''
    })

    const passwordStrength = computed(() => {
      const password = formData.value.password
      if (!password) return { percentage: 0, class: '', text: '' }

      let score = 0
      const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        numbers: /\d/.test(password),
        special: /[@$!%*?&]/.test(password)
      }

      score = Object.values(checks).filter(Boolean).length

      const strengthLevels = [
        { percentage: 20, class: 'weak', text: 'Weak' },
        { percentage: 40, class: 'fair', text: 'Fair' },
        { percentage: 60, class: 'good', text: 'Good' },
        { percentage: 80, class: 'strong', text: 'Strong' },
        { percentage: 100, class: 'very-strong', text: 'Very Strong' }
      ]

      return strengthLevels[score - 1] || strengthLevels[0]
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

      if (!/^[a-zA-Z0-9]+$/.test(username)) {
        errors.value.username = 'Username can only contain letters and numbers'
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

      if (password.length < 5 || password.length > 12) {
        errors.value.password = 'Password must be 5-12 characters'
        return false
      }

      errors.value.password = ''
      return true
    }

    const validateConfirmPassword = () => {
      if (!formData.value.confirmPassword) {
        errors.value.confirmPassword = 'Please confirm your password'
        return false
      }

      if (formData.value.password !== formData.value.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
        return false
      }

      errors.value.confirmPassword = ''
      return true
    }

    const isFormValid = computed(() => {
      return formData.value.username.trim() &&
             formData.value.password &&
             formData.value.confirmPassword &&
             !errors.value.username &&
             !errors.value.password &&
             !errors.value.confirmPassword &&
             formData.value.password === formData.value.confirmPassword
    })

    const handleRegister = async () => {
      validateUsername()
      validatePassword()
      validateConfirmPassword()

      if (!isFormValid.value) return

      const result = await authStore.register({
        username: formData.value.username.trim(),
        password: formData.value.password,
        confirmPassword: formData.value.confirmPassword
      })

      if (result.success) {
        router.push('/dashboard')
      }
    }

    // Watch password changes to re-validate confirm password
    watch(() => formData.value.password, () => {
      if (formData.value.confirmPassword) {
        validateConfirmPassword()
      }
    })

    return {
      formData,
      errors,
      authStore,
      passwordStrength,
      isFormValid,
      validateUsername,
      validatePassword,
      validateConfirmPassword,
      handleRegister
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

.password-strength {
  margin-top: 12px;
}

.strength-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 8px;
  position: relative;
}

.strength-fill {
  height: 100%;
  transition: width 0.4s ease, background-color 0.4s ease;
  border-radius: var(--radius-sm);
  position: relative;
}

.strength-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.3) 100%);
  animation: shimmer 2s infinite;
}

.strength-fill.weak { background: linear-gradient(90deg, #ef4444, #dc2626); }
.strength-fill.fair { background: linear-gradient(90deg, #f59e0b, #d97706); }
.strength-fill.good { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.strength-fill.strong { background: linear-gradient(90deg, #10b981, #059669); }
.strength-fill.very-strong { background: linear-gradient(90deg, #059669, #047857); }

.strength-text {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.strength-text.weak { color: #ef4444; }
.strength-text.fair { color: #f59e0b; }
.strength-text.good { color: #3b82f6; }
.strength-text.strong { color: #10b981; }
.strength-text.very-strong { color: #059669; }

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
