<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../features/auth/store/auth'
import { resolveRedirectPath } from '../features/auth/lib/navigation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
})

const errorMessage = ref('')
const isSubmitting = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    await authStore.login(form)
    await router.push(resolveRedirectPath(route.query.redirect))
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : 'Login failed, please try again'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-layout">
    <section class="auth-card">
      <div class="auth-card__header">
        <p class="auth-card__eyebrow">Vue + Flask</p>
        <h1>登录系统</h1>
        <p class="auth-card__description">
          输入已注册的账号密码完成登录。若你是第一次使用，可以先创建一个新账号。
        </p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="auth-field">
          <span>用户名</span>
          <input v-model.trim="form.username" type="text" autocomplete="username" />
        </label>

        <label class="auth-field">
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
          />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button class="auth-submit" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>还没有账号？</p>
        <RouterLink
          class="auth-link"
          :to="{ name: 'register', query: { redirect: route.query.redirect } }"
        >
          立即注册
        </RouterLink>
      </div>
    </section>
  </main>
</template>
