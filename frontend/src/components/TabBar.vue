<template>
  <nav class="tab-bar">
    <router-link
      v-for="tab in tabs"
      :key="tab.name"
      :to="tab.path"
      class="tab-bar-item"
      :class="{ active: route.name === tab.name }"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span>{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
const tabs = [
  { name: "home", path: "/home", label: "首页", icon: "🏠" },
  { name: "watch", path: "/watch", label: "追剧", icon: "🎬" },
  { name: "user", path: "/user", label: "我的", icon: "👤" },
];
</script>
