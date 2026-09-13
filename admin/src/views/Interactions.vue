<template>
  <div>
    <h2 class="title">收藏/追剧记录</h2>
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="收藏记录" name="favorites">
        <el-table :data="favorites" border>
          <el-table-column prop="user_phone" label="用户手机号" width="140" />
          <el-table-column prop="video_title" label="短剧" />
          <el-table-column prop="created_at" label="收藏时间" width="180">
            <template #default="{ row }">{{ row.created_at.slice(0, 16).replace("T", " ") }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="观看记录" name="watch-history">
        <el-table :data="watchHistory" border>
          <el-table-column prop="user_phone" label="用户手机号" width="140" />
          <el-table-column prop="video_title" label="短剧" />
          <el-table-column prop="episode_no" label="观看到第几集" width="110" />
          <el-table-column prop="progress_seconds" label="进度(秒)" width="90" />
          <el-table-column prop="updated_at" label="最后更新" width="180">
            <template #default="{ row }">{{ row.updated_at.slice(0, 16).replace("T", " ") }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { interactionApi } from "../api";

const activeTab = ref("favorites");
const favorites = ref([]);
const watchHistory = ref([]);

async function loadFavorites() {
  favorites.value = await interactionApi.favorites();
}
async function loadWatchHistory() {
  watchHistory.value = await interactionApi.watchHistory();
}

function onTabChange(name) {
  if (name === "favorites") loadFavorites();
  else loadWatchHistory();
}

onMounted(loadFavorites);
</script>

<style scoped>
.title {
  margin-bottom: 16px;
}
</style>
