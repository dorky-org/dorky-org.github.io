<script setup>
import { onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'

// 只在"英语"板块生效，其它板块不挂载朗读逻辑
// route.path 是 URL-encoded 的（浏览器里中文路径会被编码），先解码再比较
const route = useRoute()
const isEnglishSection = () => {
  try {
    return decodeURIComponent(route.path).startsWith('/英语/')
  } catch {
    return false
  }
}

const READ_SELECTOR = 'p, li, blockquote, td, th'

let currentEl = null

function isMostlyLatin(text) {
  const latin = (text.match(/[a-zA-Z]/g) || []).length
  const cjk = (text.match(/[一-龥]/g) || []).length
  return latin >= cjk
}

function stopSpeaking() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  window.speechSynthesis.cancel()
  if (currentEl) currentEl.classList.remove('read-aloud-active')
  currentEl = null
}

function speak(el) {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  const text = el.innerText.trim()
  if (!text) return

  // 再次点击同一段：停止朗读
  if (currentEl === el) {
    stopSpeaking()
    return
  }

  stopSpeaking()

  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = isMostlyLatin(text) ? 'en-US' : 'zh-CN'
  utter.rate = 0.95
  utter.onend = () => {
    if (currentEl === el) {
      el.classList.remove('read-aloud-active')
      currentEl = null
    }
  }
  utter.onerror = utter.onend

  el.classList.add('read-aloud-active')
  currentEl = el
  window.speechSynthesis.speak(utter)
}

function onClick(e) {
  if (e.target.closest('a')) return // 不打断正常的链接点击
  speak(e.currentTarget)
}

function attach() {
  if (!isEnglishSection()) return
  const container = document.querySelector('.vp-doc')
  if (!container) return
  container.querySelectorAll(READ_SELECTOR).forEach((el) => {
    if (el.dataset.readAloudBound) return
    el.dataset.readAloudBound = '1'
    el.classList.add('read-aloud-target')
    el.addEventListener('click', onClick)
  })
}

onMounted(() => {
  nextTick(() => setTimeout(attach, 100))
})

watch(
  () => route.path,
  () => {
    stopSpeaking()
    nextTick(() => setTimeout(attach, 150))
  }
)

onUnmounted(stopSpeaking)
</script>

<template></template>
