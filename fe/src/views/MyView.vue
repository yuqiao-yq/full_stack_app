<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  searchGames,
  type GameSearchResult,
} from '../features/games/api/games'
import {
  createReview,
  getMyReviews,
  type GameReview,
  type ReviewStatus,
} from '../features/reviews/api/reviews'
import { useAuthStore } from '../features/auth/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navLinks = [
  { label: '首页', to: { name: 'home' } },
  { label: '游戏库', to: { name: 'home' } },
  { label: '排行榜', to: { name: 'home' } },
  { label: '资讯', to: { name: 'home' } },
  { label: '我的', to: { name: 'my' } },
]

const staticMenuItems = [
  {
    key: 'wishlist',
    label: '心愿单',
    count: '12',
    title: '近期最想入手',
    description: '这里放着你准备下一个周末开坑的游戏。',
    cards: [
      { name: '星际拓荒：远征版', meta: '期待值 9.8 / 开放宇宙探索' },
      { name: '幻境传说 DLC', meta: '期待值 9.4 / 新职业与地图' },
      { name: '极速狂飙 2026', meta: '期待值 9.2 / 次世代赛道体验' },
    ],
  },
  {
    key: 'played',
    label: '我玩过的',
    count: '38',
    title: '最近游玩记录',
    description: '记录你近期体验过的作品与投入时长。',
    cards: [
      { name: '战场前线', meta: '累计 82 小时 / 最近一次游玩 2 小时前' },
      { name: '足球经理', meta: '累计 116 小时 / 正在经营冠军赛季' },
      { name: '魔法方块', meta: '累计 24 小时 / 适合碎片时间放松' },
    ],
  },
  {
    key: 'completed',
    label: '完美通关',
    count: '7',
    title: '100% 达成清单',
    description: '那些你已经全收集、全成就、无遗憾毕业的作品。',
    cards: [
      { name: '恐怖森林', meta: '全结局解锁 / 收集率 100%' },
      { name: '苍穹守望者', meta: '全支线完成 / 成就 58/58' },
      { name: '深海奇旅', meta: '困难模式通关 / 图鉴 100%' },
    ],
  },
  {
    key: 'achievements',
    label: '成就与徽章',
    count: '48',
    title: '个人徽章陈列',
    description: '平台给你的标签与高光时刻，方便随时回顾。',
    cards: [
      { name: '白金猎人', meta: '连续 5 款游戏达成白金成就' },
      { name: '竞速王者', meta: '竞速类排行榜前 1%' },
      { name: '评论达人', meta: '累计发布 20+ 高质量评价' },
    ],
  },
]

const activeMenuKey = ref('wishlist')
const searchQuery = ref('')
const searchResults = ref<GameSearchResult[]>([])
const selectedGame = ref<GameSearchResult | null>(null)
const myReviews = ref<GameReview[]>([])
const reviewError = ref('')
const reviewSuccess = ref('')
const isSearching = ref(false)
const isLoadingReviews = ref(false)
const isSubmittingReview = ref(false)

const reviewStatusOptions: Array<{ value: ReviewStatus; label: string }> = [
  { value: 'reviewed', label: '我的评价' },
  { value: 'wishlist', label: '加入心愿单' },
  { value: 'played', label: '我玩过的' },
  { value: 'completed', label: '完美通关' },
]

const reviewForm = reactive({
  userScore: 4.5,
  reviewText: '',
  status: 'reviewed' as ReviewStatus,
})

const menuItems = computed(() => [
  ...staticMenuItems.slice(0, 3),
  {
    key: 'reviews',
    label: '我的评价',
    count: String(myReviews.value.length),
    title: '最新发布的点评',
    description: '搜索真实游戏资料，补全封面和平台信息后，再发布你的个人评价。',
    cards: [],
  },
  ...staticMenuItems.slice(3),
])

const currentSection = computed(
  () =>
    menuItems.value.find((item) => item.key === activeMenuKey.value) ??
    menuItems.value[0],
)

const displayName = computed(
  () => authStore.user?.name || authStore.user?.username || 'User',
)

const profileStats = computed(() => [
  { label: '已收藏游戏', value: '64' },
  { label: '已通关作品', value: '19' },
  { label: '累计游戏时长', value: '486h' },
  { label: '发布评价', value: String(myReviews.value.length || 0) },
])

function isActiveNav(name: string) {
  return route.name === name
}

function formatReviewDate(value: string) {
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function fetchMyReviews() {
  isLoadingReviews.value = true

  try {
    const data = await getMyReviews()
    myReviews.value = data.reviews
  } catch (error) {
    reviewError.value =
      error instanceof Error ? error.message : '获取评价列表失败'
  } finally {
    isLoadingReviews.value = false
  }
}

async function handleSearch() {
  reviewError.value = ''
  reviewSuccess.value = ''

  if (searchQuery.value.trim().length < 2) {
    reviewError.value = '请输入至少 2 个字符的游戏名称'
    return
  }

  isSearching.value = true

  try {
    const data = await searchGames(searchQuery.value.trim())
    searchResults.value = data.results

    if (!data.results.length) {
      reviewError.value = '没有找到匹配的游戏，请换一个关键词试试'
    }
  } catch (error) {
    reviewError.value =
      error instanceof Error ? error.message : '搜索游戏数据失败'
  } finally {
    isSearching.value = false
  }
}

function selectGame(game: GameSearchResult) {
  selectedGame.value = game
  reviewError.value = ''
  reviewSuccess.value = ''
}

async function handleSubmitReview() {
  reviewError.value = ''
  reviewSuccess.value = ''

  if (!selectedGame.value) {
    reviewError.value = '请先从搜索结果中选择一个游戏'
    return
  }

  if (!reviewForm.reviewText.trim()) {
    reviewError.value = '请填写你的评价内容'
    return
  }

  if (reviewForm.userScore < 0 || reviewForm.userScore > 5) {
    reviewError.value = '评分范围需在 0 到 5 分之间'
    return
  }

  isSubmittingReview.value = true

  try {
    await createReview({
      externalGameId: selectedGame.value.externalGameId,
      gameName: selectedGame.value.name,
      coverUrl: selectedGame.value.coverUrl,
      platforms: selectedGame.value.platforms,
      genres: selectedGame.value.genres,
      released: selectedGame.value.released,
      externalRating: selectedGame.value.rating,
      userScore: reviewForm.userScore,
      reviewText: reviewForm.reviewText.trim(),
      status: reviewForm.status,
    })

    reviewSuccess.value = '评价提交成功，已保存到本地后端'
    reviewForm.reviewText = ''
    await fetchMyReviews()
  } catch (error) {
    reviewError.value =
      error instanceof Error ? error.message : '提交评价失败'
  } finally {
    isSubmittingReview.value = false
  }
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe()
  }

  await fetchMyReviews()
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
          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            class="portal-nav__link"
            :class="{ 'portal-nav__link--active': isActiveNav(String(link.to.name)) }"
            :to="link.to"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <div class="portal-actions">
          <input class="portal-search" type="text" placeholder="搜索我的游戏记录..." />
          <button class="portal-account" type="button" @click="handleLogout">
            退出登录
          </button>
        </div>
      </header>

      <section class="profile-hero">
        <div class="profile-hero__main">
          <div class="profile-hero__avatar">{{ displayName.slice(0, 1) }}</div>
          <div>
            <p class="profile-hero__eyebrow">个人中心</p>
            <h1>{{ displayName }} 的游戏档案</h1>
            <p class="profile-hero__desc">
              统一管理你的心愿单、游玩记录、完美通关作品和平台评价，打造专属的玩家主页。
            </p>
          </div>
        </div>

        <div class="profile-stats">
          <article
            v-for="stat in profileStats"
            :key="stat.label"
            class="profile-stat"
          >
            <p class="profile-stat__value">{{ stat.value }}</p>
            <p class="profile-stat__label">{{ stat.label }}</p>
          </article>
        </div>
      </section>

      <section class="profile-layout">
        <aside class="profile-sidebar">
          <div class="profile-sidebar__header">
            <h2>我的空间</h2>
            <p>用不同菜单管理你的游戏生活。</p>
          </div>

          <button
            v-for="item in menuItems"
            :key="item.key"
            class="profile-menu__item"
            :class="{ 'profile-menu__item--active': item.key === activeMenuKey }"
            type="button"
            @click="activeMenuKey = item.key"
          >
            <span>{{ item.label }}</span>
            <strong>{{ item.count }}</strong>
          </button>

          <div class="profile-sidebar__tip">
            <p class="profile-sidebar__tip-label">本周玩家状态</p>
            <p>已连续登录 5 天，建议优先完成心愿单中的新作试玩。</p>
          </div>
        </aside>

        <section class="profile-content">
          <div class="section-heading section-heading--profile">
            <div>
              <h2>{{ currentSection.title }}</h2>
              <p class="profile-content__description">
                {{ currentSection.description }}
              </p>
            </div>
            <button class="profile-content__action" type="button">
              管理{{ currentSection.label }}
            </button>
          </div>

          <template v-if="activeMenuKey !== 'reviews'">
            <div class="profile-card-grid">
              <article
                v-for="card in currentSection.cards"
                :key="card.name"
                class="profile-card"
              >
                <div class="profile-card__badge">{{ currentSection.label }}</div>
                <h3>{{ card.name }}</h3>
                <p>{{ card.meta }}</p>
              </article>
            </div>

            <div class="profile-notes">
              <article class="profile-note">
                <h3>最近目标</h3>
                <p>完成《极速狂飙 2026》预购前的试玩体验，并整理心愿单优先级。</p>
              </article>
              <article class="profile-note">
                <h3>社区互动</h3>
                <p>本月已收到 86 个评价点赞，你的深度评测正在帮助更多玩家做选择。</p>
              </article>
            </div>
          </template>

          <template v-else>
            <section class="review-workspace">
              <div class="review-search-bar">
                <input
                  v-model="searchQuery"
                  class="review-search-input"
                  type="text"
                  placeholder="搜索游戏名称，如 Elden Ring、Cyberpunk 2077..."
                  @keyup.enter="handleSearch"
                />
                <button
                  class="profile-content__action"
                  type="button"
                  :disabled="isSearching"
                  @click="handleSearch"
                >
                  {{ isSearching ? '搜索中...' : '搜索游戏' }}
                </button>
              </div>

              <div class="review-layout">
                <div class="review-search-results">
                  <div class="review-panel__title">搜索结果</div>
                  <article
                    v-for="game in searchResults"
                    :key="game.externalGameId"
                    class="search-result-card"
                    :class="{
                      'search-result-card--active':
                        selectedGame?.externalGameId === game.externalGameId,
                    }"
                    @click="selectGame(game)"
                  >
                    <div
                      class="search-result-card__cover"
                      :style="
                        game.coverUrl
                          ? { backgroundImage: `url(${game.coverUrl})` }
                          : undefined
                      "
                    ></div>
                    <div class="search-result-card__body">
                      <h3>{{ game.name }}</h3>
                      <p>
                        {{ game.platforms.join(' / ') || '平台信息待补充' }}
                      </p>
                      <p>
                        评分 {{ game.rating ?? '--' }} · 上线
                        {{ game.released || '未知' }}
                      </p>
                      <p>{{ game.summary || '暂无游戏简介' }}</p>
                    </div>
                  </article>

                  <p
                    v-if="!searchResults.length && !isSearching"
                    class="review-empty-state"
                  >
                    输入关键词后，这里会展示来自 IGDB 的游戏搜索结果。
                  </p>
                </div>

                <div class="review-editor">
                  <div class="review-panel__title">评价编辑器</div>

                  <div v-if="selectedGame" class="selected-game-card">
                    <div
                      class="selected-game-card__cover"
                      :style="
                        selectedGame.coverUrl
                          ? { backgroundImage: `url(${selectedGame.coverUrl})` }
                          : undefined
                      "
                    ></div>
                    <div class="selected-game-card__body">
                      <h3>{{ selectedGame.name }}</h3>
                      <p>平台：{{ selectedGame.platforms.join(' / ') || '未知' }}</p>
                      <p>类型：{{ selectedGame.genres.join(' / ') || '未知' }}</p>
                      <p class="selected-game-card__summary">
                        {{ selectedGame.summary || '暂无游戏简介' }}
                      </p>
                      <p>
                        IGDB 评分：{{ selectedGame.rating ?? '--' }} · 发售：
                        {{ selectedGame.released || '未知' }}
                      </p>
                    </div>
                  </div>

                  <p v-else class="review-empty-state">
                    请先从左侧搜索结果中选择一个游戏，再填写评价内容。
                  </p>

                  <div class="review-form">
                    <label class="review-form__field">
                      <span>归类</span>
                      <select v-model="reviewForm.status">
                        <option
                          v-for="status in reviewStatusOptions"
                          :key="status.value"
                          :value="status.value"
                        >
                          {{ status.label }}
                        </option>
                      </select>
                    </label>

                    <label class="review-form__field">
                      <span>我的评分（0 - 5）</span>
                      <input
                        v-model.number="reviewForm.userScore"
                        type="number"
                        min="0"
                        max="5"
                        step="0.1"
                      />
                    </label>

                    <label class="review-form__field review-form__field--full">
                      <span>评价内容</span>
                      <textarea
                        v-model="reviewForm.reviewText"
                        rows="5"
                        placeholder="写下你对这款游戏的感受、推荐理由或避坑提醒..."
                      ></textarea>
                    </label>

                    <button
                      class="profile-content__action"
                      type="button"
                      :disabled="isSubmittingReview"
                      @click="handleSubmitReview"
                    >
                      {{ isSubmittingReview ? '提交中...' : '提交评价' }}
                    </button>
                  </div>

                  <p v-if="reviewError" class="auth-error">{{ reviewError }}</p>
                  <p v-if="reviewSuccess" class="review-success">{{ reviewSuccess }}</p>
                </div>
              </div>
            </section>

            <section class="review-history">
              <div class="review-panel__title">我发布过的评价</div>

              <div v-if="isLoadingReviews" class="review-empty-state">
                正在加载你的评价列表...
              </div>

              <div v-else-if="myReviews.length" class="review-history__list">
                <article
                  v-for="review in myReviews"
                  :key="review.id"
                  class="review-history-card"
                >
                  <div
                    class="review-history-card__cover"
                    :style="
                      review.coverUrl
                        ? { backgroundImage: `url(${review.coverUrl})` }
                        : undefined
                    "
                  ></div>
                  <div class="review-history-card__body">
                    <div class="review-history-card__header">
                      <div>
                        <h3>{{ review.gameName }}</h3>
                        <p>
                          {{ review.platforms.join(' / ') || '平台未知' }} ·
                          {{ formatReviewDate(review.createdAt) }}
                        </p>
                      </div>
                      <span class="review-history-card__score">
                        {{ review.userScore.toFixed(1) }}
                      </span>
                    </div>
                    <p class="review-history-card__tags">
                      {{ review.status }} · {{ review.genres.join(' / ') || '类型未知' }}
                    </p>
                    <p class="review-history-card__text">{{ review.reviewText }}</p>
                  </div>
                </article>
              </div>

              <div v-else class="review-empty-state">
                你还没有发布过任何评价，先从上方搜索一款游戏试试。
              </div>
            </section>
          </template>
        </section>
      </section>
    </div>
  </main>
</template>
