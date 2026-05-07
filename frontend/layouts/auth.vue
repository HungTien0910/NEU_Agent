<template>
  <div class="auth-layout">
    <video
      class="auth-layout__video"
      autoplay
      muted
      loop
      playsinline
      preload="auto"
    >
      <source src="/media/neu-header.mp4" type="video/mp4" />
    </video>
    <main class="auth-layout__content">
      <slot />
    </main>
    <AdmissionChatWidget />
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  position: relative;
  display: grid;
  place-items: center;
  overflow: hidden;
}

.auth-layout__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(1.15) contrast(1.05) brightness(0.98);
}

.auth-layout__content {
  display: grid;
  place-items: center;
  padding: 48px 24px;
  position: relative;
  z-index: 1;
}

@media (max-width: 960px) {
  .auth-layout__content {
    padding: 32px 18px;
  }
}
</style>
