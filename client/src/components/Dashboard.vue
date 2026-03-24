<template>
  <div class="dashboard-container">
    <div class="dashboard-card">
      <div class="dashboard-header">
        <h1>Account Dashboard</h1>
        <button @click="handleLogout" class="logout-button">Logout</button>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>Loading account information...</p>
      </div>

      <div v-else-if="user" class="account-info">
        <div class="info-card">
          <h2>Account Information</h2>
          <div class="info-item">
            <span class="label">Username:</span>
            <span class="value">{{ user.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">Account ID:</span>
            <span class="value">#{{ user.id }}</span>
          </div>
          <div class="info-item">
            <span class="label">Created:</span>
            <span class="value">{{ formatDate(user.createdat) }}</span>
          </div>
        </div>

        <div class="password-section">
          <h2>Change Password</h2>
          <form @submit.prevent="handlePasswordChange" class="password-form">
            <div class="form-group">
              <label for="currentPassword">Current Password</label>
              <input
                id="currentPassword"
                v-model="passwordForm.currentPassword"
                type="password"
                maxlength="12"
                placeholder="Enter current password"
                :class="{ 'error': errors.currentPassword }"
                @blur="validateCurrentPassword"
              />
              <span class="char-count">{{ passwordForm.currentPassword.length }}/12</span>
              <span v-if="errors.currentPassword" class="error-message">{{ errors.currentPassword }}</span>
            </div>

            <div class="form-group">
              <label for="newPassword">New Password</label>
              <input
                id="newPassword"
                v-model="passwordForm.newPassword"
                type="password"
                maxlength="12"
                placeholder="Enter new password"
                :class="{ 'error': errors.newPassword }"
                @blur="validateNewPassword"
              />
              <span class="char-count">{{ passwordForm.newPassword.length }}/12</span>
              <span v-if="errors.newPassword" class="error-message">{{ errors.newPassword }}</span>

              <!-- Password strength indicator -->
              <div class="password-strength">
                <div class="strength-bar">
                  <div
                    class="strength-fill"
                    :class="passwordStrength.class"
                    :style="{ width: passwordStrength.percentage + '%' }"
                  ></div>
                </div>
                <span class="strength-text" :class="passwordStrength.class">
                  {{ passwordStrength.text }}
                </span>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmNewPassword">Confirm New Password</label>
              <input
                id="confirmNewPassword"
                v-model="passwordForm.confirmNewPassword"
                type="password"
                maxlength="12"
                placeholder="Confirm new password"
                :class="{ 'error': errors.confirmNewPassword }"
                @blur="validateConfirmNewPassword"
              />
              <span v-if="errors.confirmNewPassword" class="error-message">{{ errors.confirmNewPassword }}</span>
            </div>

            <div v-if="successMessage" class="success-message">
              {{ successMessage }}
            </div>

            <div v-if="authStore.error" class="error-message global-error">
              {{ authStore.error }}
            </div>

            <button
              type="submit"
              class="change-password-button"
              :disabled="!isPasswordFormValid || authStore.loading"
            >
              <span v-if="authStore.loading" class="loading-spinner"></span>
              {{ authStore.loading ? 'Updating Password...' : 'Update Password' }}
            </button>
          </form>
        </div>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="fetchUserData" class="retry-button">Retry</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const loading = ref(true)
    const error = ref(null)
    const successMessage = ref('')
    const user = ref(null)

    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    })

    const errors = ref({
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    })

    const passwordStrength = computed(() => {
      const password = passwordForm.value.newPassword
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

    const fetchUserData = async () => {
      loading.value = true
      error.value = null

      const result = await authStore.fetchProfile()
      if (result.success) {
        user.value = result.data.user
      } else {
        error.value = result.error
      }

      loading.value = false
    }

    const validateCurrentPassword = () => {
      const password = passwordForm.value.currentPassword

      if (!password) {
        errors.value.currentPassword = 'Current password is required'
        return false
      }

      if (password.length < 5 || password.length > 12) {
        errors.value.currentPassword = 'Password must be 5-12 characters'
        return false
      }

      errors.value.currentPassword = ''
      return true
    }

    const validateNewPassword = () => {
      const password = passwordForm.value.newPassword

      if (!password) {
        errors.value.newPassword = 'New password is required'
        return false
      }

      if (password.length < 5 || password.length > 12) {
        errors.value.newPassword = 'Password must be 5-12 characters'
        return false
      }

      if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
        errors.value.newPassword = 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
        return false
      }

      if (password === passwordForm.value.currentPassword) {
        errors.value.newPassword = 'New password must be different from current password'
        return false
      }

      errors.value.newPassword = ''
      return true
    }

    const validateConfirmNewPassword = () => {
      if (!passwordForm.value.confirmNewPassword) {
        errors.value.confirmNewPassword = 'Please confirm your new password'
        return false
      }

      if (passwordForm.value.newPassword !== passwordForm.value.confirmNewPassword) {
        errors.value.confirmNewPassword = 'Passwords do not match'
        return false
      }

      errors.value.confirmNewPassword = ''
      return true
    }

    const isPasswordFormValid = computed(() => {
      return passwordForm.value.currentPassword &&
             passwordForm.value.newPassword &&
             passwordForm.value.confirmNewPassword &&
             !errors.value.currentPassword &&
             !errors.value.newPassword &&
             !errors.value.confirmNewPassword &&
             passwordForm.value.newPassword === passwordForm.value.confirmNewPassword
    })

    const handlePasswordChange = async () => {
      successMessage.value = ''
      validateCurrentPassword()
      validateNewPassword()
      validateConfirmNewPassword()

      if (!isPasswordFormValid.value) return

      const result = await authStore.changePassword({
        currentPassword: passwordForm.value.currentPassword,
        newPassword: passwordForm.value.newPassword,
        confirmNewPassword: passwordForm.value.confirmNewPassword
      })

      if (result.success) {
        successMessage.value = 'Password updated successfully!'
        // Reset form
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmNewPassword: ''
        }
        errors.value = {
          currentPassword: '',
          newPassword: '',
          confirmNewPassword: ''
        }
      }
    }

    const handleLogout = () => {
      authStore.logout()
      router.push('/login')
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Watch new password changes to re-validate confirm password
    watch(() => passwordForm.value.newPassword, () => {
      if (passwordForm.value.confirmNewPassword) {
        validateConfirmNewPassword()
      }
    })

    onMounted(() => {
      fetchUserData()
    })

    return {
      loading,
      error,
      successMessage,
      user,
      passwordForm,
      errors,
      authStore,
      passwordStrength,
      isPasswordFormValid,
      validateCurrentPassword,
      validateNewPassword,
      validateConfirmNewPassword,
      handlePasswordChange,
      handleLogout,
      formatDate,
      fetchUserData
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-2xl);
  padding: 40px 32px;
  box-shadow: var(--shadow-xl);
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15), 0 15px 15px -5px rgba(0, 0, 0, 0.08);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid var(--border-color);
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-header h1 {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
}

.logout-button {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.logout-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.logout-button:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.logout-button:hover::before {
  left: 100%;
}

.logout-button:active {
  transform: translateY(0);
  box-shadow: var(--shadow-md);
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--bg-tertiary);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 24px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 60px 20px;
}

.retry-button {
  background: var(--primary-gradient);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: var(--radius-lg);
  font-size: 0.938rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 24px;
  box-shadow: var(--shadow-md);
}

.retry-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.info-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 32px 24px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.info-card h2 {
  color: var(--text-primary);
  font-size: 1.5rem;
  margin-bottom: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item:hover {
  background: var(--bg-tertiary);
  margin: 0 -24px;
  padding: 16px 24px;
  border-radius: var(--radius-md);
}

.info-item .label {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.938rem;
}

.info-item .value {
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1rem;
  font-family: 'Inter', sans-serif;
}

.password-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  padding: 32px 24px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.password-section:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.password-section h2 {
  color: var(--text-primary);
  font-size: 1.5rem;
  margin-bottom: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.password-form {
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

.success-message {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
  color: var(--success-color);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.success-message::before {
  content: "✓";
  font-size: 1.125rem;
  font-weight: 700;
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

.change-password-button {
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

.change-password-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.change-password-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.change-password-button:hover:not(:disabled)::before {
  left: 100%;
}

.change-password-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-md);
}

.change-password-button:disabled {
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

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .dashboard-card {
    padding: 32px 24px;
    border-radius: var(--radius-xl);
  }

  .dashboard-header h1 {
    font-size: 2rem;
  }

  .info-card,
  .password-section {
    padding: 24px 20px;
  }
}

@media (max-width: 640px) {
  .dashboard-container {
    padding: 12px;
  }

  .dashboard-card {
    padding: 24px 20px;
    border-radius: var(--radius-lg);
  }

  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .dashboard-header h1 {
    font-size: 1.875rem;
    text-align: center;
  }

  .logout-button {
    align-self: center;
    max-width: 200px;
  }

  .info-card h2,
  .password-section h2 {
    font-size: 1.25rem;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 0;
  }

  .info-item .value {
    font-size: 0.938rem;
  }

  .form-group input {
    padding: 14px 16px;
    font-size: 0.938rem;
  }

  .change-password-button {
    padding: 16px 20px;
    font-size: 0.938rem;
  }
}

@media (max-width: 480px) {
  .dashboard-container {
    padding: 8px;
  }

  .dashboard-card {
    padding: 20px 16px;
  }

  .dashboard-header h1 {
    font-size: 1.75rem;
  }

  .info-card,
  .password-section {
    padding: 20px 16px;
  }

  .account-info {
    gap: 24px;
  }

  .password-form {
    gap: 20px;
  }

  .form-group input {
    padding: 12px 16px;
    font-size: 0.875rem;
  }

  .change-password-button {
    padding: 14px 18px;
    font-size: 0.875rem;
  }

  .char-count {
    font-size: 0.688rem;
    padding: 1px 4px;
  }
}

@media (max-width: 360px) {
  .dashboard-card {
    padding: 16px 12px;
  }

  .dashboard-header h1 {
    font-size: 1.5rem;
  }

  .info-card,
  .password-section {
    padding: 16px 12px;
  }

  .logout-button {
    padding: 10px 16px;
    font-size: 0.813rem;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .dashboard-card {
    background: rgba(31, 41, 55, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .info-card,
  .password-section {
    background: var(--bg-secondary);
    border-color: var(--border-color);
  }

  .form-group input {
    background: var(--bg-primary);
    border-color: var(--border-color);
  }

  .char-count {
    background: var(--bg-primary);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .dashboard-card {
    border: 2px solid var(--text-primary);
  }

  .form-group input {
    border: 2px solid var(--text-primary);
  }

  .change-password-button {
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
