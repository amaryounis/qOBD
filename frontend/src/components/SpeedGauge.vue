<template>
  <div class="speed-gauge-container">
    <UniversalGauge 
      :value="speed" 
      :maxValue="200" 
      type="speed" 
      :decimals="1"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import UniversalGauge from "./UniversalGauge.vue";

const props = defineProps({
  speed: {
    type: Number,
    required: true,
    default: 0
  }
});
</script>

<style scoped>
.speed-gauge-container {
  width: 100%;
  height: 100%;
}
</style>