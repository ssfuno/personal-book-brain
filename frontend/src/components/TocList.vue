<script setup lang="ts">
import { ref, computed } from 'vue'
import {
    NList,
    NListItem,
    NSpace,
    NText,
    NButton
} from 'naive-ui'
import type { TocItem } from '../types'

const props = defineProps<{
    toc: TocItem[]
    limit?: number
}>()

const showAll = ref(false)

const displayedToc = computed(() => {
    if (!props.limit || showAll.value) {
        return props.toc
    }
    return props.toc.slice(0, props.limit)
})

const remainingCount = computed(() => {
    if (!props.limit || !props.toc) return 0
    return props.toc.length - props.limit
})
</script>

<template>
    <n-list bordered clickable hoverable>
        <n-list-item v-for="(item, idx) in displayedToc" :key="idx"
            :style="{ paddingLeft: (12 + (Number(item.level || 1) - 1) * 24) + 'px' }">
            <n-text :style="{ fontWeight: item.level === 1 ? '600' : '400', fontSize: '0.9rem' }">
                {{ item.title }}
            </n-text>
        </n-list-item>

        <n-list-item v-if="limit && toc.length > limit" @click="showAll = !showAll" style="cursor: pointer">
            <n-space justify="center">
                <n-button text type="primary">
                    {{ showAll ? '閉じる' : `他 ${remainingCount} 項目を表示...` }}
                </n-button>
            </n-space>
        </n-list-item>
    </n-list>
</template>

<style scoped></style>
