<template>
  <div class="page">
    <div class="nav-bar">剧照/壁纸</div>
    <div v-if="!images.length" class="empty-tip">暂无壁纸</div>
    <div class="gallery-grid" v-else>
      <div class="gallery-item" v-for="img in images" :key="img.id">
        <div class="thumb">{{ img.name || "壁纸" }}</div>
        <div class="meta">
          <span>{{ img.name }}</span>
          <button class="download-btn" @click="download(img)">下载（{{ img.downloads }}）</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { videoApi } from "../api";

const props = defineProps({ id: String });
const route = useRoute();
const images = ref([]);

async function load() {
  images.value = await videoApi.images(props.id || route.params.id);
}

async function download(img) {
  const result = await videoApi.downloadImage(props.id || route.params.id, img.id);
  img.downloads = result.downloads;
  if (img.image_url) {
    const a = document.createElement("a");
    a.href = img.image_url;
    a.download = img.name || "wallpaper";
    a.click();
  }
}

onMounted(load);
</script>

<style scoped>
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px;
}
.thumb {
  aspect-ratio: 3 / 4;
  background: var(--brand-gradient);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  font-size: 12px;
}
.download-btn {
  border: 1px solid var(--brand);
  color: var(--brand-dark);
  background: #fff;
  border-radius: 12px;
  padding: 3px 8px;
  font-size: 11px;
}
</style>
