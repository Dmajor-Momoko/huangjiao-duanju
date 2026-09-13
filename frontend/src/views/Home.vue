<template>
  <div class="page">
    <div class="nav-bar"><span class="brand-logo">🍌</span>黄蕉</div>
    <BannerCarousel />
    <div class="search-bar">
      <input class="field" v-model="keyword" placeholder="搜索短剧名称" @keyup.enter="load" />
    </div>
    <div class="categories">
      <span
        class="cate"
        :class="{ active: activeCategory === null }"
        @click="selectCategory(null)"
      >全部</span>
      <span
        v-for="c in categories"
        :key="c.id"
        class="cate"
        :class="{ active: activeCategory === c.id }"
        @click="selectCategory(c.id)"
      >{{ c.name }}</span>
    </div>

    <div v-if="loading" class="empty-tip">加载中...</div>
    <div v-else-if="videos.length === 0" class="empty-tip">暂无短剧</div>
    <div v-else class="video-grid">
      <VideoCard v-for="v in videos" :key="v.id" :video="v" />
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { videoApi } from "../api";
import BannerCarousel from "../components/BannerCarousel.vue";
import TabBar from "../components/TabBar.vue";
import VideoCard from "../components/VideoCard.vue";

const videos = ref([]);
const categories = ref([]);
const activeCategory = ref(null);
const keyword = ref("");
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    videos.value = await videoApi.list({
      category_id: activeCategory.value || undefined,
      keyword: keyword.value || undefined,
    });
  } finally {
    loading.value = false;
  }
}

function selectCategory(id) {
  activeCategory.value = id;
  load();
}

onMounted(async () => {
  categories.value = await videoApi.categories();
  await load();
});
</script>

<style scoped>
.search-bar {
  padding: 12px 12px 0;
}
.categories {
  display: flex;
  gap: 8px;
  padding: 12px;
  overflow-x: auto;
}
.cate {
  padding: 7px 16px;
  border-radius: 16px;
  background: var(--bg);
  font-size: 13px;
  white-space: nowrap;
  color: #666;
  transition: background 0.15s ease, color 0.15s ease;
}
.cate.active {
  background: var(--brand-gradient);
  color: #fff;
  font-weight: 600;
}
</style>
