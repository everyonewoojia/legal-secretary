<template>
  <div class="home">
    <div class="bg-decoration">
      <div class="bg-circle" />
      <div class="bg-square" />
    </div>

    <section class="hero">
      <h1 class="hero-title">让合同管理更智能、更安全</h1>
      <div class="hero-dot-line">
        <span class="hero-dot" />
        <span class="hero-line" />
      </div>
      <p class="hero-subtitle">面向中小企业的 AI 智能体合同起草与谈判辅助系统</p>
    </section>

    <div class="section-divider" />

    <main class="cards">
      <div class="card-dot" />

      <el-card shadow="never" class="feature-card" @click="router.push('/draft')">
        <div class="card-icon-wrap">
          <span class="card-icon">📝</span>
        </div>
        <h3 class="card-title">合同起草</h3>
        <p class="card-desc">选择合同类型，通过多轮智能对话引导，快速生成规范的合同初稿</p>
        <div class="card-tags">技术服务 · 采购 · 劳动 · 合作 · 保密</div>
        <el-button type="primary" class="card-btn">开始起草</el-button>
        <div class="card-bottom-line" />
      </el-card>

      <el-card shadow="never" class="feature-card" @click="router.push('/negotiate')">
        <div class="card-icon-wrap">
          <span class="card-icon">🔍</span>
        </div>
        <h3 class="card-title">谈判辅助</h3>
        <p class="card-desc">上传对方修改的合同，自动比对差异，识别风险条款并提供建议话术</p>
        <div class="card-tags">差异比对 · 风险识别 · 话术建议</div>
        <el-button type="primary" class="card-btn">开始分析</el-button>
        <div class="card-bottom-line" />
      </el-card>
    </main>

    <footer class="footer">
      <p>© 2026 法务小秘 · 华中科技大学软件学院实训项目</p>
      <p>本系统为教学实训 Demo，仅供参考，不替代律师意见</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.home {
  min-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(180deg, #F0F5FF 0%, #FFFFFF 400px);
  padding: 0 20px;
  position: relative;
  overflow: hidden;
}

/* ===== Geometric Decorations ===== */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  top: -120px;
  right: -180px;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: #2563EB;
  opacity: 0.03;
}

.bg-square {
  position: absolute;
  bottom: 120px;
  left: -60px;
  width: 120px;
  height: 120px;
  background: #2563EB;
  opacity: 0.02;
  transform: rotate(45deg);
}

/* ===== Hero ===== */
.hero {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 64px 20px 20px;
  animation: fadeDown 0.6s ease;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 16px;
}

.hero-dot-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 16px;
}

.hero-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2563EB;
  flex-shrink: 0;
}

.hero-line {
  width: 36px;
  height: 2px;
  background: #2563EB;
  border-radius: 1px;
}

.hero-subtitle {
  font-size: 15px;
  color: #64748B;
  margin: 0;
  font-weight: 400;
}

/* ===== Divider ===== */
.section-divider {
  position: relative;
  z-index: 1;
  width: 80%;
  max-width: 480px;
  height: 1px;
  background: #E5E7EB;
  opacity: 0.5;
  margin: 20px auto 0;
}

/* ===== Cards ===== */
.cards {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 32px;
  padding: 36px 0 20px;
  flex-wrap: wrap;
  justify-content: center;
  flex: 1;
  align-content: flex-start;
}

.card-dot {
  position: absolute;
  bottom: 60px;
  left: 50%;
  margin-left: -3px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2563EB;
  opacity: 0.3;
}

.feature-card {
  width: 440px;
  max-width: 100%;
  border-radius: 16px;
  background: #FFFFFF;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  border: none;
  position: relative;
  overflow: hidden;
}

.feature-card:nth-child(2) {
  animation-delay: 0s;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.15);
}

.feature-card :deep(.el-card__body) {
  padding: 36px;
}

.card-icon-wrap {
  width: 44px;
  height: 44px;
  background: #EFF6FF;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.card-icon {
  font-size: 22px;
  line-height: 1;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 12px;
}

.card-desc {
  font-size: 14px;
  color: #64748B;
  margin: 0 0 20px;
  line-height: 1.8;
}

.card-tags {
  font-size: 12px;
  font-weight: 500;
  color: #2563EB;
  margin-bottom: 24px;
  letter-spacing: 0.3px;
}

.card-btn {
  width: 100%;
  border-radius: 8px;
  background: #2563EB;
  border-color: #2563EB;
  transition: background 0.2s;
  height: 40px;
}

.card-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.card-bottom-line {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #2563EB, transparent);
  border-radius: 1px;
}

/* ===== Footer ===== */
.footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 24px 20px 32px;
  margin-top: 48px;
}

.footer p {
  font-size: 12px;
  color: #94A3B8;
  margin: 4px 0;
}

/* ===== Animations ===== */
@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .feature-card {
    width: 100%;
  }

  .hero {
    padding-top: 40px;
  }

  .hero-title {
    font-size: 22px;
  }

  .bg-circle {
    width: 300px;
    height: 300px;
    top: -80px;
    right: -100px;
  }

  .bg-square {
    display: none;
  }
}
</style>
