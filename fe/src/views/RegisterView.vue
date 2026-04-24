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
  displayName: '',
  password: '',
  confirmPassword: '',
})

const errorMessage = ref('')
const isSubmitting = ref(false)

function validateForm() {
  if (!/^[A-Za-z0-9_]{3,20}$/.test(form.username)) {
    return '用户名需为 3-20 位，并且只能包含字母、数字、下划线'
  }

  if (!form.displayName.trim()) {
    return '显示名称不能为空'
  }

  if (form.displayName.trim().length > 50) {
    return '显示名称不能超过 50 个字符'
  }

  if (form.password.length < 8) {
    return '密码至少需要 8 位'
  }

  if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
    return '密码必须同时包含字母和数字'
  }

  if (form.password !== form.confirmPassword) {
    return '两次输入的密码不一致'
  }

  return ''
}

async function handleSubmit() {
  errorMessage.value = validateForm()
  if (errorMessage.value) {
    return
  }

  isSubmitting.value = true

  try {
    await authStore.register(form)
    await router.push(resolveRedirectPath(route.query.redirect))
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : 'Register failed, please try again'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-layout">
    <section class="auth-card">
      <div class="auth-card__header">
        <p class="auth-card__eyebrow">Create Account</p>
        <h1>注册账号</h1>
        <p class="auth-card__description">
          创建新用户后会直接完成登录，并跳转回你刚才想访问的页面。
        </p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="auth-field">
          <span>用户名</span>
          <input
            v-model.trim="form.username"
            type="text"
            autocomplete="username"
            placeholder="仅支持字母、数字、下划线"
          />
        </label>

        <label class="auth-field">
          <span>显示名称</span>
          <input
            v-model.trim="form.displayName"
            type="text"
            autocomplete="nickname"
            placeholder="用于页面展示"
          />
        </label>

        <label class="auth-field">
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            placeholder="至少 8 位，包含字母和数字"
          />
        </label>

        <label class="auth-field">
          <span>确认密码</span>
          <input
            v-model="form.confirmPassword"
            type="password"
            autocomplete="new-password"
          />
        </label>

        <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

        <button class="auth-submit" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '注册中...' : '注册并登录' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>已经有账号了？</p>
        <RouterLink
          class="auth-link"
          :to="{ name: 'login', query: { redirect: route.query.redirect } }"
        >
          去登录
        </RouterLink>
      </div>
    </section>
  </main>
</template>
