<template>
  <div class="page">
    <div class="nav-bar">追剧</div>
    <div class="section-title">观看记录</div>
    <div v-if="history.length === 0" class="empty-tip">还没有观看记录</div>
    <div v-else class="video-grid">
      <VideoCard v-for="v in history" :key="v.id" :video="v" />
    </div>

    <div class="section-title">我的收藏</div>
    <div v-if="favorites.length === 0" class="empty-tip">还没有收藏的短剧</div>
    <div v-else class="video-grid">
      <VideoCard v-for="v in favorites" :key="v.id" :video="v" />
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { userApi } from "../api";
import TabBar from "../components/TabBar.vue";
import VideoCard from "../components/VideoCard.vue";

const history = ref([]);
const favorites = ref([]);

onMounted(async () => {
  history.value = await userApi.history();
  favorites.value = await userApi.favorites();
});
</script>

<style scoped>
.section-title {
  padding: 16px 12px 8px;
  font-size: 14px;
  font-weight: 700;
  border-top: 8px solid var(--bg);
}
</style>
