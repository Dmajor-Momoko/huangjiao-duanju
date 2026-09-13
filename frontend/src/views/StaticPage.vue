<template>
  <div class="page">
    <div class="nav-bar">{{ content?.title || "加载中..." }}</div>
    <div class="content" v-if="content">{{ content.content }}</div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { pageApi } from "../api";

const route = useRoute();
const content = ref(null);

async function load() {
  content.value = await pageApi.get(route.params.slug);
}

watch(() => route.params.slug, load);
onMounted(load);
</script>

<style scoped>
.content {
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
  color: #444;
  white-space: pre-wrap;
}
</style>
