<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NCollapse,
  NCollapseItem,
  NTag,
  NSpace,
  NText,
  NEmpty,

  NSpin,
  useMessage
} from 'naive-ui'
import { useApiClient } from '../composables/useApiClient'
import TocList from './TocList.vue'
import type { Book } from '../types'

const message = useMessage()
const { loading, error, fetchWithAuth } = useApiClient()
const books = ref<Book[]>([])

const fetchBooks = async () => {
  try {
    const data = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/books`)
    books.value = data
  } catch (e: any) {
    message.error(e.message)
  }
}

onMounted(() => fetchBooks())
</script>

<template>
  <n-space vertical :size="24">
    <n-space vertical :size="4">
      <n-text strong style="font-size: 1.1rem">蔵書一覧</n-text>
      <n-text depth="3" style="font-size: 0.85rem">{{ books.length }} 冊の書籍を管理中</n-text>
    </n-space>

    <!-- Loading -->
    <n-spin v-if="loading && !books.length" style="padding: 60px 0; width: 100%">
      <template #description>読み込み中...</template>
    </n-spin>

    <!-- Error -->
    <n-alert v-else-if="error" type="error">{{ error }}</n-alert>

    <!-- Empty -->
    <n-empty v-else-if="!books.length" description="まだ本が登録されていません" style="padding: 60px 0">
      <template #extra>
        <n-text depth="3">「本を登録」から追加してみましょう</n-text>
      </template>
    </n-empty>

    <!-- List -->
    <div v-else class="list-container">
      <n-collapse arrow-placement="right" accordion>
        <n-collapse-item v-for="book in books" :key="book.id" :name="book.id" class="book-item">
          <template #header>
            <n-space :size="12" align="center">
              <n-text strong>{{ book.title }}</n-text>
            </n-space>
          </template>
          <template #header-extra>
            <n-space :size="8">
              <n-tag :bordered="false" type="info" size="small" round>
                {{book.toc?.filter((i) => Number(i.level || 1) === 1).length || 0}} 章
              </n-tag>
            </n-space>
          </template>

          <div style="margin-top: 12px; border-radius: 8px">
            <toc-list v-if="book.toc?.length" :toc="book.toc" :limit="15" />
          </div>
        </n-collapse-item>
      </n-collapse>
    </div>
  </n-space>
</template>

<style scoped>
.list-container {
  animation: fadeIn 0.4s ease-out;
}

.book-item {
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.book-item:hover {
  background: #fafaf9;
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
</style>
