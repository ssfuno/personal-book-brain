<script setup lang="ts">
import { ref } from 'vue'
import {
  NCard,
  NInput,
  NButton,
  NAlert,
  NSpace,
  NText,
  useMessage,
  NModal,
  NInputGroup
} from 'naive-ui'
import { useApiClient } from '../composables/useApiClient'
import TocList from './TocList.vue'
import type { BookPreview } from '../types'

const message = useMessage()
const { loading, error, fetchWithAuth } = useApiClient()

const query = ref('')
const result = ref<BookPreview | null>(null)
const showAllToc = ref(false)

// State for Preview Flow
const isPreview = ref(false)
const showEditor = ref(false)
const editedTocJson = ref('')
const editorError = ref('')

const fetchPreview = async () => {
  if (!query.value.trim()) return
  result.value = null
  showAllToc.value = false
  isPreview.value = false

  try {
    const normalizedIsbn = query.value.trim().replace(/[-\s]/g, '')

    // Call Preview Endpoint
    const data = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/books/preview`, {
      method: 'POST',
      body: JSON.stringify({ isbn: normalizedIsbn })
    })

    result.value = data
    isPreview.value = true // Enter Preview Mode

  } catch (e: any) {
    message.error(e.message)
    result.value = null
  }
}

const confirmRegistration = async () => {
  if (!result.value) return

  try {
    await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/books`, {
      method: 'POST',
      body: JSON.stringify({
        isbn: result.value.isbn,
        title: result.value.title,
        toc: result.value.toc // Send the current (possibly edited) TOC
      })
    })

    message.success('書籍を登録しました')

    // Reset State independent of verification
    query.value = ''
    result.value = null
    isPreview.value = false

  } catch (e: any) {
    message.error(e.message)
  }
}

const startEditing = () => {
  if (!result.value) return
  editedTocJson.value = JSON.stringify(result.value.toc, null, 2)
  showEditor.value = true
}

const saveEditing = () => {
  if (!result.value) return
  try {
    const parsed = JSON.parse(editedTocJson.value)
    if (!Array.isArray(parsed)) throw new Error("TOC must be an array")
    // Simple validation (can be expanded)
    result.value.toc = parsed
    showEditor.value = false
    editorError.value = ''
    message.success('目次を更新しました（登録するまで確定しません）')
  } catch (e: any) {
    editorError.value = 'JSON形式が正しくありません: ' + e.message
  }
}

const cancelPreview = () => {
  result.value = null
  isPreview.value = false
  query.value = ''
  message.info('登録をキャンセルしました')
}
</script>

<template>
  <n-space vertical :size="32">
    <!-- Input Section -->
    <n-card bordered :segmented="{ content: true }">
      <template #header>
        <n-space vertical :size="4">
          <n-text strong style="font-size: 1.1rem">新しい本を追加</n-text>
          <n-text depth="3" style="font-size: 0.85rem">ISBN（10桁または13桁）を入力してください。AIがタイトルと目次を自動取得します。</n-text>
        </n-space>
      </template>

      <n-space vertical :size="20">
        <n-input-group>
          <n-input v-model:value="query" type="text" placeholder="例: 9784798150727" size="large" round
            :disabled="loading || isPreview" @keyup.enter="fetchPreview" />
          <n-button type="primary" size="large" round :loading="loading" :disabled="!query.trim() || isPreview"
            @click="fetchPreview">
            検索
          </n-button>
        </n-input-group>
      </n-space>
    </n-card>

    <!-- Error Alert -->
    <n-alert v-if="error" type="error" closable @close="error = ''">
      {{ error }}
    </n-alert>

    <!-- Preview / Result Display -->
    <n-card v-if="result" bordered :title="isPreview ? '登録プレビュー' : '登録完了'" class="animate-fadeIn">
      <template #header-extra v-if="isPreview">
        <n-space>
          <n-button size="small" @click="startEditing">目次を編集</n-button>
          <n-button size="small" type="error" ghost @click="cancelPreview">キャンセル</n-button>
        </n-space>
      </template>

      <n-space vertical :size="16">
        <template v-if="result.title !== 'Unknown Title'">
          <div>
            <n-text strong style="font-size: 1.2rem">{{ result.title }}</n-text>
            <div style="margin-top: 4px">
              <n-text depth="3" style="font-size: 0.85rem">
                {{ result.toc?.length || 0 }} 項目
              </n-text>
            </div>
          </div>

          <toc-list v-if="result.toc?.length" :toc="result.toc" :limit="showAllToc ? undefined : 10" />

          <n-space justify="center" v-if="isPreview" style="margin-top: 16px;">
            <n-button type="primary" size="large" @click="confirmRegistration" :loading="loading">
              この内容で登録する
            </n-button>
          </n-space>

        </template>

        <template v-else>
          <n-alert type="warning" title="書籍情報を取得できませんでした">
            このISBNの書籍情報が見つかりませんでした。
          </n-alert>
          <n-text depth="3" style="font-size: 0.85rem">
            入力されたISBN: {{ result.isbn }}
          </n-text>
          <n-space justify="end" v-if="isPreview">
            <n-button @click="cancelPreview">キャンセル</n-button>
          </n-space>
        </template>
      </n-space>
    </n-card>

    <!-- JSON Editor Modal -->
    <n-modal v-model:show="showEditor" preset="card" title="目次の編集 (JSON)" style="width: 800px; max-width: 90%">
      <n-space vertical>
        <n-alert type="info" :show-icon="false">
          JSON形式で目次を直接編集できます。構造（title, levelなど）を崩さないように注意してください。
        </n-alert>
        <n-input v-model:value="editedTocJson" type="textarea" :rows="20" placeholder="JSON Format"
          style="font-family: monospace;" />
        <n-alert v-if="editorError" type="error">
          {{ editorError }}
        </n-alert>
        <n-space justify="end">
          <n-button @click="showEditor = false">キャンセル</n-button>
          <n-button type="primary" @click="saveEditing">反映する</n-button>
        </n-space>
      </n-space>
    </n-modal>
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
</style>
