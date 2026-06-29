<template>
  <div class="home">
    <header class="hero">
      <h1>法务小秘</h1>
      <p class="subtitle">AI 智能体合同起草与谈判辅助系统</p>
      <p class="desc">面向中小企业的智能化合同管理工具，让合同工作更高效、更安全</p>
    </header>

    <main class="cards">
      <el-card shadow="hover" class="feature-card" @click="router.push('/draft')">
        <div class="card-icon">📝</div>
        <h3>合同起草</h3>
        <p>选择合同类型，通过多轮智能对话引导，快速生成规范的合同初稿</p>
        <el-tag size="small">技术服务 · 采购 · 劳动 · 合作 · 保密</el-tag>
      </el-card>

      <el-card shadow="hover" class="feature-card" @click="router.push('/negotiate')">
        <div class="card-icon">🔍</div>
        <h3>谈判辅助</h3>
        <p>上传对方修改的合同，自动比对差异，识别风险条款并提供建议话术</p>
        <el-tag size="small">差异比对 · 风险识别 · 话术建议</el-tag>
      </el-card>
    </main>

    <footer class="footer">
      <span>实训 Demo · 仅供学习参考</span>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}
.hero {
  text-align: center;
  padding: 80px 20px 40px;
}
.hero h1 {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: 4px;
}
.subtitle {
  font-size: 20px;
  opacity: 0.95;
  margin-bottom: 8px;
}
.desc {
  font-size: 14px;
  opacity: 0.7;
}
.cards {
  display: flex;
  gap: 24px;
  padding: 20px;
  flex-wrap: wrap;
  justify-content: center;
  flex: 1;
}
.feature-card {
  width: 340px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  color: #333;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
.card-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.feature-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
}
.feature-card p {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  line-height: 1.6;
}
.footer {
  padding: 24px;
  font-size: 12px;
  opacity: 0.5;
}
</style>
