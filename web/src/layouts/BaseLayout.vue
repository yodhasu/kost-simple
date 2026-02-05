<template>
  <div class="base-layout">
    <slot />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.base-layout {
  min-height: 100vh;
  background: var(--bg-main);
}
</style>
