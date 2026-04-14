<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getHealth } from '../api/health'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const healthMessage = ref('Loading...')
const loadError = ref('')

const displayName = computed(
  () => authStore.user?.name || authStore.user?.username || 'User',
)

onMounted(async () => {
  try {
    if (!authStore.user) {
      await authStore.fetchMe()
    }

    const health = await getHealth()
    healthMessage.value = health.message
  } catch (error) {
    loadError.value =
      error instanceof Error ? error.message : 'Failed to load data'
  }
})

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <main class="dashboard">
    <section class="dashboard-card">
      <div class="dashboard-card__header">
        <div>
          <p class="dashboard-card__eyebrow">Authenticated</p>
          <h1>欢迎回来，{{ displayName }}</h1>
          <p class="dashboard-card__description">
            你已经完成登录，当前页面是一个受保护页面，只能在携带有效 JWT 时访问。
          </p>
        </div>

        <button class="secondary-button" type="button" @click="handleLogout">
          退出登录
        </button>
      </div>

      <div class="dashboard-grid">
        <article class="info-panel">
          <p class="info-panel__label">当前用户</p>
          <p class="info-panel__value">{{ authStore.user?.username || '--' }}</p>
        </article>

        <article class="info-panel">
          <p class="info-panel__label">显示名称</p>
          <p class="info-panel__value">{{ authStore.user?.name || '--' }}</p>
        </article>

        <article class="info-panel">
          <p class="info-panel__label">后端状态</p>
          <p class="info-panel__value">{{ healthMessage }}</p>
        </article>
      </div>

      <p v-if="loadError" class="auth-error">{{ loadError }}</p>
    </section>
  </main>
</template>
