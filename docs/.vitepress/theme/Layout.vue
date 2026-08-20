<script setup>
import DefaultTheme from 'vitepress/theme'
import ReadAloud from './ReadAloud.vue'

const { Layout } = DefaultTheme
</script>

<template>
  <Layout>
    <template #layout-top>
      <ReadAloud />
    </template>
  </Layout>
</template>
