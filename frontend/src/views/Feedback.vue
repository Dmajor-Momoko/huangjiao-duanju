<template>
  <div class="page">
    <div class="nav-bar">意见反馈</div>

    <div class="form">
      <textarea class="field textarea" v-model="content" placeholder="遇到了什么问题？说说你的建议..." rows="5"></textarea>
      <input class="field" v-model="contact" placeholder="联系方式（选填，方便我们回复你）" />
      <div class="upload-row">
        <input type="file" accept="image/*" multiple @change="onUploadImages" />
      </div>
      <div class="preview-row" v-if="images.length">
        <img v-for="(url, i) in images" :key="i" :src="url" class="preview" />
      </div>
      <button class="btn-primary" :disabled="!content.trim() || submitting" @click="submit">
        {{ submitting ? "提交中..." : "提交反馈" }}
      </button>
    </div>

    <div class="section-title">我的反馈</div>
    <div v-if="!list.length" class="empty-tip">还没有提交过反馈</div>
    <div v-else class="list">
      <div class="item" v-for="fb in list" :key="fb.id">
        <div class="item-content">{{ fb.content }}</div>
        <div class="item-meta">{{ fb.created_at.slice(0, 16).replace("T", " ") }} · {{ statusText(fb.status) }}</div>
        <div class="item-reply" v-if="fb.admin_reply">官方回复：{{ fb.admin_reply }}</div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { feedbackApi, uploadApi } from "../api";
import TabBar from "../components/TabBar.vue";

const content = ref("");
const contact = ref("");
const images = ref([]);
const submitting = ref(false);
const list = ref([]);

async function load() {
  list.value = await feedbackApi.mine();
}

async function onUploadImages(e) {
  const files = Array.from(e.target.files || []);
  for (const file of files) {
    const res = await uploadApi.upload(file);
    images.value.push(res.url);
  }
}

async function submit() {
  submitting.value = true;
  try {
    await feedbackApi.submit({ content: content.value.trim(), contact: contact.value.trim(), images: images.value });
    content.value = "";
    contact.value = "";
    images.value = [];
    await load();
    alert("提交成功，感谢反馈！");
  } catch (e) {
    alert(e.message);
  } finally {
    submitting.value = false;
  }
}

function statusText(status) {
  return status === "replied" ? "已回复" : "待处理";
}

onMounted(load);
</script>

<style scoped>
.form {
  padding: 16px;
}
.textarea {
  resize: none;
  font-family: inherit;
}
.upload-row {
  margin-bottom: 12px;
}
.preview-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.preview {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.section-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  font-weight: 700;
  border-top: 8px solid var(--bg);
}
.list {
  padding: 0 16px;
}
.item {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.item-meta {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}
.item-reply {
  margin-top: 8px;
  background: var(--brand-soft);
  color: var(--brand-dark);
  padding: 8px 10px;
  border-radius: var(--radius-md);
  font-size: 12px;
}
</style>
