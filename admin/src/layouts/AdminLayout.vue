<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="brand">🍌 黄蕉管理后台</div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/banners">
          <el-icon><Picture /></el-icon>
          <span>首页焦点图</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Menu /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/videos">
          <el-icon><VideoCamera /></el-icon>
          <span>短剧管理</span>
        </el-menu-item>
        <el-menu-item index="/vip-plans">
          <el-icon><Star /></el-icon>
          <span>会员套餐</span>
        </el-menu-item>
        <el-menu-item index="/ad-free-plans">
          <el-icon><Mute /></el-icon>
          <span>免广告套餐</span>
        </el-menu-item>
        <el-menu-item index="/signin-rules">
          <el-icon><Calendar /></el-icon>
          <span>签到配置</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>积分任务</span>
        </el-menu-item>
        <el-menu-item index="/card-codes">
          <el-icon><Ticket /></el-icon>
          <span>卡密管理</span>
        </el-menu-item>
        <el-menu-item index="/distribution-config">
          <el-icon><Share /></el-icon>
          <span>分销配置</span>
        </el-menu-item>
        <el-menu-item index="/withdraw-applies">
          <el-icon><Money /></el-icon>
          <span>提现审核</span>
        </el-menu-item>
        <el-menu-item index="/static-pages">
          <el-icon><Document /></el-icon>
          <span>静态页面</span>
        </el-menu-item>
        <el-menu-item index="/feedbacks">
          <el-icon><ChatDotRound /></el-icon>
          <span>意见反馈</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><Tickets /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/interactions">
          <el-icon><Star /></el-icon>
          <span>收藏/追剧记录</span>
        </el-menu-item>
        <el-menu-item index="/admin-accounts">
          <el-icon><UserFilled /></el-icon>
          <span>管理员账号</span>
        </el-menu-item>
        <el-menu-item index="/banned-words">
          <el-icon><WarningFilled /></el-icon>
          <span>违禁词管理</span>
        </el-menu-item>
        <el-menu-item index="/action-logs">
          <el-icon><Notebook /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ store.info?.nickname }}（{{ store.info?.phone }}）</span>
        <el-button link @click="logout">退出登录</el-button>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import {
  Calendar,
  ChatDotRound,
  Document,
  List,
  Menu,
  Money,
  Mute,
  Notebook,
  Odometer,
  Picture,
  Share,
  Star,
  Ticket,
  Tickets,
  User,
  UserFilled,
  VideoCamera,
  WarningFilled,
} from "@element-plus/icons-vue";
import { useAdminStore } from "../stores/admin";

const route = useRoute();
const router = useRouter();
const store = useAdminStore();

function logout() {
  store.logout();
  router.replace("/login");
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.aside {
  background: #1f2430;
  color: #fff;
}
.brand {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.menu {
  border-right: none;
  background: transparent;
}
.menu :deep(.el-menu-item) {
  color: #c9cdd4;
}
.menu :deep(.el-menu-item.is-active) {
  color: #ffb020;
  background: rgba(255, 176, 32, 0.12);
}
.header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  border-bottom: 1px solid #eee;
  background: #fff;
}
.main {
  background: #f5f6f8;
}
</style>
