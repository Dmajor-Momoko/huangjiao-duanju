<template>
  <div>
    <div class="toolbar">
      <h2 class="title">意见反馈</h2>
    </div>

    <el-radio-group v-model="statusFilter" class="filter" @change="load">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="pending">待处理</el-radio-button>
      <el-radio-button value="replied">已回复</el-radio-button>
    </el-radio-group>

    <el-table :data="feedbacks" border>
      <el-table-column prop="user_phone" label="用户手机号" width="130" />
      <el-table-column prop="content" label="反馈内容" min-width="240" show-overflow-tooltip />
      <el-table-column prop="contact" label="联系方式" width="130" />
      <el-table-column label="图片" width="120">
        <template #default="{ row }">
          <el-image
            v-for="(img, i) in row.images"
            :key="i"
            :src="img"
            style="width: 32px; height: 32px; margin-right: 4px"
            preview-teleported
            :preview-src-list="row.images"
          />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'replied' ? 'success' : 'warning'">
            {{ row.status === "replied" ? "已回复" : "待处理" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="admin_reply" label="回复内容" show-overflow-tooltip />
      <el-table-column prop="created_at" label="提交时间" width="180">
        <template #default="{ row }">{{ row.created_at.slice(0, 16).replace("T", " ") }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="primary" @click="openReply(row)">回复</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="replyVisible" title="回复反馈" width="440">
      <p class="target">{{ replyTarget?.content }}</p>
      <el-input v-model="replyText" type="textarea" :rows="4" placeholder="输入回复内容" />
      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="warning" @click="confirmReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { feedbackApi } from "../api";

const feedbacks = ref([]);
const statusFilter = ref("");
const replyVisible = ref(false);
const replyTarget = ref(null);
const replyText = ref("");

async function load() {
  feedbacks.value = await feedbackApi.list(statusFilter.value);
}

function openReply(row) {
  replyTarget.value = row;
  replyText.value = row.admin_reply || "";
  replyVisible.value = true;
}

async function confirmReply() {
  await feedbackApi.reply(replyTarget.value.id, replyText.value);
  ElMessage.success("已回复");
  replyVisible.value = false;
  await load();
}

onMounted(load);
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter {
  margin-bottom: 16px;
}
.target {
  margin-bottom: 12px;
  color: #666;
  font-size: 13px;
}
</style>
