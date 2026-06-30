<template>
  <div class="brand-panel">
    <div class="particles">
      <span v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)" />
    </div>

    <div class="brand-top">
      <div class="logo-wrap">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="19" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" />
          <path d="M13 20l5 5 9-9" stroke="rgba(255,255,255,0.95)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
          <rect x="14" y="26" width="12" height="2" rx="1" fill="rgba(255,255,255,0.5)" />
        </svg>
      </div>
      <h1 class="brand-name">法务小秘</h1>
      <p class="brand-sub">AI 智能体合同起草与谈判辅助系统</p>
    </div>

    <div class="pain-points">
      <div class="bubble" style="animation-delay:0.2s">
        <p>中小企业缺乏专职法务？</p>
      </div>
      <div class="bubble" style="animation-delay:0.7s">
        <p>合同起草总是不规范？</p>
      </div>
      <div class="bubble" style="animation-delay:1.2s">
        <p>谈判时总是处于劣势？</p>
      </div>
    </div>

    <div class="capabilities">
      <span class="cap-badge">🎯 智能引导</span>
      <span class="cap-badge">🔍 风险识别</span>
      <span class="cap-badge">💬 谈判辅助</span>
      <span class="cap-badge">⚡ 一键生成</span>
    </div>

    <div class="brand-bottom">
      <p class="slogan-text">让每个中小企业都拥有自己的AI法务助手</p>
      <div class="mascot">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <circle cx="28" cy="28" r="27" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)" stroke-width="1" />
          <circle cx="28" cy="28" r="22" fill="rgba(255,255,255,0.08)" />
          <circle cx="20" cy="24" r="2.5" fill="rgba(255,255,255,0.9)" />
          <circle cx="36" cy="24" r="2.5" fill="rgba(255,255,255,0.9)" />
          <path d="M20 34c0 0 3 5 8 5s8-5 8-5" stroke="rgba(255,255,255,0.8)" stroke-width="2" stroke-linecap="round" />
          <path d="M6 28c0 0 6-8 12-8s12 8 12 8" stroke="rgba(255,255,255,0.2)" stroke-width="1" stroke-linecap="round" />
          <path d="M38 28c0 0 6-8 12-8s12 8 12 8" stroke="rgba(255,255,255,0.2)" stroke-width="1" stroke-linecap="round" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
function particleStyle(i) {
  const size = 2 + (i % 4) * 1.5
  const x = (i * 17 + 3) % 100
  const y = (i * 23 + 7) % 100
  const delay = (i * 0.7) % 4
  const dur = 6 + (i % 3) * 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}%`,
    top: `${y}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${dur}s`,
  }
}
</script>

<style scoped>
.brand-panel {
  flex: 0 0 55%;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 48px 44px;
  background: linear-gradient(135deg, #7C3AED, #2563EB);
  color: #fff;
  overflow: hidden;
}

.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  animation: floatUp linear infinite;
}

@keyframes floatUp {
  0% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { opacity: 1; }
  100% { transform: translateY(-120px) scale(0.4); opacity: 0; }
}

.brand-top {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.logo-wrap {
  margin-bottom: 4px;
  animation: fadeInUp 0.6s ease;
}

.brand-name {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 2px;
  margin: 0;
}

.brand-sub {
  font-size: 13px;
  opacity: 0.75;
  margin: 2px 0 0;
  font-weight: 400;
}

.pain-points {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 20px;
}

.bubble {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 12px 18px;
  max-width: 90%;
  opacity: 0;
  transform: translateY(12px);
  animation: bubbleIn 0.5s ease forwards;
}

.bubble:nth-child(2) { align-self: center; }
.bubble:nth-child(3) { align-self: flex-end; }

.bubble p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.92;
  line-height: 1.4;
}

@keyframes bubbleIn {
  to { opacity: 1; transform: translateY(0); }
}

.capabilities {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.cap-badge {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.3px;
  backdrop-filter: blur(4px);
}

.brand-bottom {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 28px;
}

.slogan-text {
  font-size: 13px;
  opacity: 0.7;
  margin: 0;
  max-width: 70%;
  line-height: 1.5;
}

.mascot {
  flex-shrink: 0;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .brand-panel {
    display: none;
  }
}
</style>
