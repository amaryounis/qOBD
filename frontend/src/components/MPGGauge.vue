<template>
    <div class="mpg-gauge-container">
      <UniversalGauge 
        :value="mpg" 
        :maxValue="50" 
        type="mpg" 
        :decimals="1"
      />
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import UniversalGauge from "./UniversalGauge.vue";
  
  const props = defineProps({
    mpg: {
      type: Number,
      required: true,
      default: 0
    }
  });
  </script>
  
  <style scoped>
  .mpg-gauge-container {
    width: 100%;
    height: 100%;
  }
  </style>