<template>
  <el-header class="page-header" height="56px">
    <div class="header-left">
      <span class="brand">法务小秘</span>
      <el-tag :type="tagType" size="small">{{ tag }}</el-tag>
    </div>
    <div class="header-nav">
      <slot />
    </div>
  </el-header>
</template>

<script setup>
defineProps({
  tag: { type: String, required: true },
  tagType: { type: String, default: 'success' },
})
</script>

<style scoped>
.page-header {
  display: flex !important;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px !important;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: 1px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
