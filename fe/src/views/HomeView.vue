<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getHealth } from '../api/health'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const healthMessage = ref('同步中')
const loadError = ref('')
const activeSlideIndex = ref(0)

const heroSlides = [
  {
    title: '极速狂飙',
    subtitle: '体验最刺激的竞速快感',
    tag: '竞速',
    theme: 'velocity',
  },
  {
    title: '幻境传说',
    subtitle: '踏入魔法与巨龙交织的奇幻世界',
    tag: '角色扮演',
    theme: 'fantasy',
  },
  {
    title: '银河前线',
    subtitle: '集结舰队，在星际战场赢下战略对决',
    tag: '策略',
    theme: 'galaxy',
  },
]

const featuredGames = [
  {
    title: '恐怖森林',
    category: '恐怖',
    rating: '4.4',
    players: '5.4万',
    theme: 'forest',
  },
  {
    title: '足球经理',
    category: '体育',
    rating: '4.3',
    players: '4.9万',
    theme: 'stadium',
  },
  {
    title: '魔法方块',
    category: '休闲',
    rating: '4.6',
    players: '4.2万',
    theme: 'puzzle',
  },
  {
    title: '战场前线',
    category: '射击',
    rating: '4.7',
    players: '9.2万',
    theme: 'battle',
  },
]

const categories = [
  { name: '动作', count: '1250 款游戏' },
  { name: '角色扮演', count: '980 款游戏' },
  { name: '策略', count: '760 款游戏' },
  { name: '射击', count: '650 款游戏' },
]

const platformStats = computed(() => [
  { label: '收录游戏总数', value: '12,580', trend: '+125' },
  { label: '活跃用户数', value: '1,250,000', trend: '+8.5%' },
  { label: '今日更新数', value: '48', trend: '+12' },
  { label: '后端状态', value: healthMessage.value, trend: '实时' },
])

const newsList = [
  {
    title: '年度最佳游戏评选结果公布',
    date: '2025-01-15 14:30',
    views: '12.5万',
  },
  {
    title: 'TGA 游戏大奖颁奖典礼圆满落幕',
    date: '2025-01-14 10:20',
    views: '8.9万',
  },
  {
    title: '《幻想骑士传说》3.0 版本更新说明',
    date: '2025-01-13 16:45',
    views: '6.2万',
  },
]

const rankingList = [
  { rank: '01', name: '极速狂飙', hot: '96.8' },
  { rank: '02', name: '幻境传说', hot: '95.2' },
  { rank: '03', name: '战场前线', hot: '93.7' },
  { rank: '04', name: '足球经理', hot: '90.4' },
  { rank: '05', name: '魔法方块', hot: '88.9' },
]

const currentSlide = computed(() => heroSlides[activeSlideIndex.value])

const displayName = computed(
  () => authStore.user?.name || authStore.user?.username || 'User',
)

let slideTimer: number | undefined

function nextSlide() {
  activeSlideIndex.value = (activeSlideIndex.value + 1) % heroSlides.length
}

function selectSlide(index: number) {
  activeSlideIndex.value = index
}

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

  slideTimer = window.setInterval(nextSlide, 4000)
})

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

onUnmounted(() => {
  if (slideTimer) {
    window.clearInterval(slideTimer)
  }
})
</script>

<template>
  <main class="portal-page">
    <div class="portal-shell">
      <header class="portal-header">
        <div class="portal-brand">
          <div class="portal-brand__logo">G</div>
          <div>
            <p class="portal-brand__title">游戏数据中心</p>
            <p class="portal-brand__subtitle">欢迎回来，{{ displayName }}</p>
          </div>
        </div>

        <nav class="portal-nav" aria-label="Primary">
          <a class="portal-nav__link portal-nav__link--active" href="/">首页</a>
          <a class="portal-nav__link" href="/">游戏库</a>
          <a class="portal-nav__link" href="/">排行榜</a>
          <a class="portal-nav__link" href="/">资讯</a>
          <a class="portal-nav__link" href="/">关于</a>
        </nav>

        <div class="portal-actions">
          <input class="portal-search" type="text" placeholder="搜索游戏名称..." />
          <button class="portal-account" type="button" @click="handleLogout">
            退出登录
          </button>
        </div>
      </header>

      <section class="hero-section">
        <div class="hero-banner" :class="`hero-banner--${currentSlide.theme}`">
          <div class="hero-banner__overlay">
            <p class="hero-banner__tag">{{ currentSlide.tag }}</p>
            <h1>{{ currentSlide.title }}</h1>
            <p class="hero-banner__subtitle">{{ currentSlide.subtitle }}</p>
            <button class="hero-banner__button" type="button">查看详情</button>
          </div>

          <button class="hero-banner__arrow" type="button" @click="nextSlide">
            →
          </button>

          <div class="hero-banner__dots">
            <button
              v-for="(slide, index) in heroSlides"
              :key="slide.title"
              class="hero-banner__dot"
              :class="{ 'hero-banner__dot--active': index === activeSlideIndex }"
              type="button"
              @click="selectSlide(index)"
            ></button>
          </div>
        </div>
      </section>

      <section class="content-section">
        <div class="section-heading">
          <h2>热门游戏</h2>
          <a href="/">查看更多</a>
        </div>

        <div class="game-grid">
          <article
            v-for="game in featuredGames"
            :key="game.title"
            class="game-card"
          >
            <div class="game-card__cover" :class="`game-card__cover--${game.theme}`"></div>
            <div class="game-card__body">
              <h3>{{ game.title }}</h3>
              <p class="game-card__category">{{ game.category }}</p>
              <div class="game-card__meta">
                <span>★ {{ game.rating }}</span>
                <span>{{ game.players }}</span>
              </div>
              <button class="game-card__button" type="button">查看详情</button>
            </div>
          </article>
        </div>
      </section>

      <section class="content-section">
        <div class="section-heading">
          <h2>游戏分类</h2>
        </div>

        <div class="category-grid">
          <article
            v-for="category in categories"
            :key="category.name"
            class="category-card"
          >
            <div class="category-card__icon">{{ category.name.slice(0, 1) }}</div>
            <h3>{{ category.name }}</h3>
            <p>{{ category.count }}</p>
          </article>
        </div>
      </section>

      <section class="content-section">
        <div class="section-heading">
          <h2>平台数据</h2>
        </div>

        <div class="stats-grid">
          <article
            v-for="stat in platformStats"
            :key="stat.label"
            class="stats-card"
          >
            <div class="stats-card__trend">{{ stat.trend }}</div>
            <p class="stats-card__value">{{ stat.value }}</p>
            <p class="stats-card__label">{{ stat.label }}</p>
          </article>
        </div>
      </section>

      <section class="content-section content-section--split">
        <div class="news-panel">
          <div class="section-heading">
            <h2>最新资讯</h2>
            <a href="/">更多资讯</a>
          </div>

          <article
            v-for="news in newsList"
            :key="news.title"
            class="news-item"
          >
            <div class="news-item__cover"></div>
            <div class="news-item__body">
              <h3>{{ news.title }}</h3>
              <p>{{ news.date }} · {{ news.views }}</p>
            </div>
            <a class="news-item__link" href="/">阅读全文</a>
          </article>
        </div>

        <aside class="ranking-panel">
          <div class="section-heading">
            <h2>游戏排行榜</h2>
          </div>

          <article
            v-for="item in rankingList"
            :key="item.rank"
            class="ranking-item"
          >
            <span class="ranking-item__rank">{{ item.rank }}</span>
            <div class="ranking-item__body">
              <h3>{{ item.name }}</h3>
              <p>热度值 {{ item.hot }}</p>
            </div>
          </article>
        </aside>
      </section>

      <footer class="portal-footer">
        <span>当前登录用户：{{ authStore.user?.username || '--' }}</span>
        <span>服务状态：{{ healthMessage }}</span>
      </footer>

      <p v-if="loadError" class="auth-error portal-error">{{ loadError }}</p>
    </div>
  </main>
</template>
