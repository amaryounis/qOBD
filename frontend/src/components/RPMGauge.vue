<template>
  <div class="rpm-gauge-container">
    <UniversalGauge 
      :value="rpm" 
      :maxValue="8000" 
      type="rpm" 
      :decimals="0"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import UniversalGauge from "./UniversalGauge.vue";

const props = defineProps({
  rpm: {
    type: Number,
    required: true,
    default: 0
  }
});
</script>

<style scoped>
.rpm-gauge-container {
  width: 100%;
  height: 100%;
}
</style>