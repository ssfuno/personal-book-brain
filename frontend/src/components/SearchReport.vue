<script setup lang="ts">
import { ref } from 'vue'
import {
  NCard,
  NInput,
  NButton,
  NSpace,
  NText,
  NTag,
  useMessage,
  NGrid,
  NGridItem
} from 'naive-ui'
import { useApiClient } from '../composables/useApiClient'
import type { SearchResult } from '../types'

const message = useMessage()
const { loading, error, fetchWithAuth } = useApiClient()

const query = ref('')
const result = ref<SearchResult | null>(null)

const searchAndReport = async () => {
  if (!query.value.trim()) return
  result.value = null

  try {
    const data = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/search?q=${encodeURIComponent(query.value.trim())}&limit=10`)
    result.value = data
    if (data.results_count > 0) {
      message.success('レポートを生成しました')
    }
  } catch (e: any) {
    message.error(e.message)
  }
}

const getGoogleBooksUrl = (isbn: string) => `https://books.google.co.jp/books?vid=ISBN${isbn}`
const getAmazonUrl = (isbn: string) => `https://www.amazon.co.jp/s?k=${isbn}`
</script>

<template>
  <n-space vertical :size="32">
    <!-- Search Section -->
    <n-card bordered :segmented="{ content: true }">
      <template #header>
        <n-space vertical :size="4">
          <n-text strong style="font-size: 1.1rem">AI再読ガイド & 蔵書検索</n-text>
          <n-text depth="3" style="font-size: 0.85rem">読み返したいテーマを入力してください。蔵書から最適な箇所をAIが特定し、再読ガイドを生成します。</n-text>
        </n-space>
      </template>

      <n-space vertical :size="20">
        <n-input v-model:value="query" type="text" placeholder="例: 分散システムの基礎、SQLチューニング、Go言語の並行処理" size="large" round
          :disabled="loading" @keyup.enter="searchAndReport" />
        <n-button type="primary" block size="large" round :loading="loading" :disabled="!query.trim()"
          @click="searchAndReport">
          {{ loading ? 'AIがガイドを作成中...' : '検索して再読ガイドを作成' }}
        </n-button>
      </n-space>
    </n-card>

    <!-- Error Alert -->
    <n-alert v-if="error" type="error" closable @close="error = ''">
      {{ error }}
    </n-alert>

    <!-- Result Display -->
    <n-space v-if="result" vertical :size="24" class="animate-fadeIn">
      <n-space align="center">
        <n-tag :bordered="false" :type="result.results_count > 0 ? 'info' : 'warning'">検索ヒット: {{ result.results_count }}
          冊</n-tag>
        <n-text depth="3" style="font-size: 0.85rem">対象クエリ: "{{ result.query }}"</n-text>
      </n-space>

      <!-- No results message -->
      <n-alert v-if="result.results_count === 0" type="info" title="該当する蔵書が見つかりませんでした">
        別のキーワードで検索してみてください。蔵書に登録されている本の目次が検索対象になります。
      </n-alert>

      <!-- AI Report -->
      <template v-else>
        <!-- Recommendations Grid -->
        <n-text strong style="font-size: 1.1rem; margin-top: 16px; display: block;">📚 おすすめの蔵書リスト</n-text>

        <n-grid :cols="1" :y-gap="16">
          <n-grid-item v-for="(book, idx) in result.report.recommendations" :key="idx">
            <n-card bordered size="medium" :title="`${idx + 1}. ${book.title}`">
              <template #header-extra>
                <n-space>
                  <n-button tag="a" :href="getGoogleBooksUrl(book.isbn)" target="_blank" size="small" secondary
                    type="tertiary">
                    Google Books
                  </n-button>
                  <n-button tag="a" :href="getAmazonUrl(book.isbn)" target="_blank" size="small" secondary
                    type="warning">
                    Amazon
                  </n-button>
                </n-space>
              </template>

              <n-space vertical :size="16">
                <!-- Book Summary -->
                <n-text>{{ book.summary }}</n-text>

                <!-- Relevant Chapters (Simple Tags) -->
                <n-space :size="[8, 8]" wrap>
                  <n-tag v-for="(chapter, cIdx) in book.relevant_chapters" :key="cIdx" :bordered="false" size="small"
                    type="info" secondary>
                    {{ chapter.chapter_title }}
                  </n-tag>
                </n-space>
              </n-space>
            </n-card>
          </n-grid-item>
        </n-grid>
      </template>
    </n-space>
  </n-space>
</template>

<style scoped>
.animate-fadeIn {
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

:deep(.markdown-body) {
  font-size: 1rem;
  line-height: 1.8;
  color: #333;
}

:deep(.markdown-body p) {
  margin-bottom: 1em;
}
</style>
