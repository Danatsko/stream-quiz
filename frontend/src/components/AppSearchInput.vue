<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import AppButton from '@/components/AppButton.vue'
import AppInput from '@/components/AppInput.vue'

const emit = defineEmits<{
  (e: 'search', query: string): void
}>()

const searchQuery = ref('')

const handleSearch = (): void => {
  emit('search', searchQuery.value.trim())
}

const MAX_SEARCH_LENGTH = 100
</script>

<template>
  <div class="search-container">
    <AppInput
      id="global-search"
      type="text"
      placeholder="Search"
      v-model="searchQuery"
      @keyup.enter="handleSearch"
      :maxlength="MAX_SEARCH_LENGTH"
    >
      <template v-slot:icon>
        <Icon icon="mdi:search" />
      </template>
    </AppInput>
    <AppButton @click="handleSearch" title="Search" aria-label="Search">
      <Icon icon="mdi:search" />
    </AppButton>
  </div>
</template>

<style scoped>
.search-container {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 0.5rem;
}

.search-container :deep(.form-group) {
  padding-bottom: 0;
}
</style>
