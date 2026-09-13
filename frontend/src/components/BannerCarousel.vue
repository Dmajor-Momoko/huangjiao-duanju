<template>
  <div class="banner-carousel" v-if="banners.length">
    <div class="banner-track" :style="{ transform: `translateX(-${active * 100}%)` }">
      <div class="banner-slide" v-for="b in banners" :key="b.id" @click="go(b)">
        <img v-if="b.image_url" :src="b.image_url" class="banner-img" />
        <div v-else class="banner-fallback">{{ b.title }}</div>
      </div>
    </div>
    <div class="banner-dots" v-if="banners.length > 1">
      <span v-for="(b, i) in banners" :key="b.id" class="dot" :class="{ active: i === active }"></span>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { bannerApi } from "../api";

const banners = ref([]);
const active = ref(0);
const router = useRouter();
let timer = null;

async function load() {
  banners.value = await bannerApi.list();
  if (banners.value.length > 1) {
    timer = setInterval(() => {
      active.value = (active.value + 1) % banners.value.length;
    }, 4000);
  }
}

function go(banner) {
  if (!banner.link_url) return;
  if (banner.link_url.startsWith("/")) {
    router.push(banner.link_url);
  } else {
    window.open(banner.link_url, "_blank");
  }
}

onMounted(load);
onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.banner-carousel {
  position: relative;
  margin: 12px 12px 0;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.banner-track {
  display: flex;
  transition: transform 0.4s ease;
}
.banner-slide {
  flex: 0 0 100%;
  aspect-ratio: 16 / 7;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.banner-fallback {
  width: 100%;
  height: 100%;
  background: var(--brand-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  padding: 12px;
  text-align: center;
}
.banner-dots {
  position: absolute;
  bottom: 8px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 5px;
}
.dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
}
.dot.active {
  background: #fff;
  width: 12px;
  border-radius: 3px;
}
</style>
