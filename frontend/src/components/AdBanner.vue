<template>
  <router-link v-if="showAd" class="ad-banner" to="/ad-free">
    <span class="ad-tag">广告</span>
    <span class="ad-text">开通免广告会员，享受纯净追剧体验</span>
    <span class="ad-cta">立即开通 ›</span>
  </router-link>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
const showAd = computed(() => !userStore.info?.is_vip && !userStore.info?.is_ad_free);
</script>

<style scoped>
.ad-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px 16px;
  padding: 10px 12px;
  background: #f5f5f5;
  border-radius: var(--radius-md);
  font-size: 12px;
  color: var(--text-muted);
}
.ad-tag {
  flex: 0 0 auto;
  font-size: 10px;
  color: #fff;
  background: #bbb;
  padding: 1px 5px;
  border-radius: 4px;
}
.ad-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ad-cta {
  flex: 0 0 auto;
  color: var(--brand-dark);
  font-weight: 600;
}
</style>
