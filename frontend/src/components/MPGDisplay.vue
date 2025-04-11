<template>
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <h2 class="card-title text-center w-full">MPG</h2>
        <div class="flex flex-col items-center justify-center h-full">
          <div class="text-4xl font-bold">{{ mpg.toFixed(1) }}</div>
          <div class="text-lg mt-2">mpg</div>
          <div class="mt-4">
            <span class="badge" :class="efficiencyBadgeClass">{{ efficiencyStatus }}</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  const props = defineProps({
    mpg: {
      type: Number,
      required: true,
      default: 0
    }
  });
  
  // Determine efficiency status based on MPG
  const efficiencyStatus = computed(() => {
    if (props.mpg < 20) return "Poor";
    if (props.mpg < 35) return "Average";
    return "Good";
  });
  
  // Determine badge class for efficiency status
  const efficiencyBadgeClass = computed(() => {
    if (efficiencyStatus.value === "Poor") return "badge-error";
    if (efficiencyStatus.value === "Average") return "badge-warning";
    return "badge-success";
  });
  </script>