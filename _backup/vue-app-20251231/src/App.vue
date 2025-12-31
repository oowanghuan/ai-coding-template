<template>
  <MainLayout v-if="showLayout">
    <router-view />
  </MainLayout>
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/MainLayout.vue'

const route = useRoute()

// Don't show main layout on auth pages
const showLayout = computed(() => {
  return !route.meta.isAuthPage
})
</script>

<style>
/* 全局样式已移至 theme.css */
#app {
  height: 100vh;
  overflow: hidden;
}
</style>
