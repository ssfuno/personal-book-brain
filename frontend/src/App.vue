<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NConfigProvider,
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NButton,
  NTabs,
  NTab,
  NSpace,
  NText,
  NH1,
  type GlobalThemeOverrides,
  NMessageProvider
} from 'naive-ui'
import BookIngest from './components/BookIngest.vue'
import SearchReport from './components/SearchReport.vue'
import BookList from './components/BookList.vue'
import { auth, signIn, logout } from './firebase'
import { onAuthStateChanged, type User } from 'firebase/auth'

// Fonts
import 'vfonts/Inter.css'

const user = ref<User | null>(null)
const loading = ref(true)
const activeTab = ref<'ingest' | 'list' | 'search'>('ingest')

// Theme overrides for a warm, professional feel
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#e67e22',
    primaryColorHover: '#d35400',
    primaryColorPressed: '#a04000',
    primaryColorSuppl: '#f39c12',
    borderRadius: '12px',
  },
  Button: {
    borderRadiusMedium: '8px'
  },
  Card: {
    borderRadius: '16px'
  }
}

onMounted(() => {
  onAuthStateChanged(auth, (u) => {
    user.value = u
    loading.value = false
  })
})
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-layout style="min-height: 100vh">
        <!-- Header -->
        <n-layout-header bordered
          style="padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 10; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(8px)">
          <n-space align="center">
            <n-h1 style="margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em;">
              Personal Book Brain
            </n-h1>
          </n-space>

          <n-space align="center" :size="24">
            <template v-if="!loading">
              <template v-if="user">
                <n-text depth="3" style="font-size: 0.85rem">{{ user.displayName }}</n-text>
                <n-button quaternary size="small" @click="logout" type="error">
                  ログアウト
                </n-button>
              </template>
              <n-button v-else type="primary" @click="signIn">
                Googleでログイン
              </n-button>
            </template>
          </n-space>
        </n-layout-header>

        <!-- Content -->
        <n-layout-content content-style="max-width: 800px; margin: 0 auto; padding: 40px 24px;">
          <template v-if="user">
            <!-- Navigation Tabs -->
            <n-tabs v-model:value="activeTab" type="line" animated justify-content="space-around"
              style="margin-bottom: 32px">
              <n-tab name="ingest">本を登録</n-tab>
              <n-tab name="list">蔵書一覧</n-tab>
              <n-tab name="search">AI検索</n-tab>
            </n-tabs>

            <!-- Views -->
            <div class="view-container">
              <book-ingest v-if="activeTab === 'ingest'" />
              <book-list v-if="activeTab === 'list'" />
              <search-report v-if="activeTab === 'search'" />
            </div>
          </template>

          <!-- Login Hero -->
          <div v-else-if="!loading" style="text-align: center; padding-top: 100px;">
            <n-space vertical :size="32" align="center">
              <n-text depth="3" style="font-size: 4rem">📖</n-text>
              <n-h1 style="font-weight: 800; font-size: 2.5rem; margin: 0">あなたの蔵書を、もっと活用しよう</n-h1>
              <n-text depth="3" style="font-size: 1.1rem; max-width: 480px; margin: 0 auto">
                本の目次を登録して、いつでも検索。読んだ本を思い出せます。
              </n-text>
              <n-button type="primary" size="large" @click="signIn"
                style="padding: 0 40px; height: 52px; font-size: 1.1rem; font-weight: 600">
                無料ではじめる
              </n-button>
            </n-space>
          </div>
        </n-layout-content>

        <!-- Footer -->
        <div class="app-footer">
          書籍情報の一部は<a href="https://ndlsearch.ndl.go.jp/" target="_blank"
            rel="noopener noreferrer">国立国会図書館サーチ</a>のAPIから取得しています。
        </div>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
.view-container {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.app-footer {
  text-align: center;
  padding: 24px 16px;
  font-size: 0.75rem;
  color: #999;
  border-top: 1px solid #f0f0f0;
}

.app-footer a {
  color: #999;
  text-decoration: underline;
}

.app-footer a:hover {
  color: #666;
}
</style>
