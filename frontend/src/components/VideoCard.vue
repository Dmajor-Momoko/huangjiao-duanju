<template>
  <router-link :to="`/video/${video.id}`" class="video-card">
    <div class="cover">{{ video.title }}</div>
    <div class="title">{{ video.title }}</div>
    <div class="sub" v-if="video.total_episodes">共{{ video.total_episodes }}集</div>
  </router-link>
</template>

<script setup>
defineProps({
  video: { type: Object, required: true },
});
</script>

<style scoped>
.video-card {
  display: block;
}
.sub {
  font-size: 11px;
  color: #999;
}
</style>
