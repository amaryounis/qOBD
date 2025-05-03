<template>
  <div class="flex flex-col items-center">
        <!-- Fuel percentage display -->
        <div class="text-3xl font-bold mb-2">
          {{ fuelPercentage.toFixed(1) }}%
        </div>
        
        <!-- Fuel bar -->
        <div class="w-full h-8 bg-base-300 rounded-full mb-2">
          <div 
            class="h-full rounded-full" 
            :class="fuelBarColorClass"
            :style="`width: ${fuelPercentage}%;`"
          ></div>
        </div>
        
        <!-- Fuel status -->
        <div class="mt-2">
          <span class="badge" :class="fuelStatusBadgeClass">{{ fuelStatus }}</span>
        </div>
        
        
      </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  fuelRemaining: {
    type: Number,
    required: true,
    default: 0
  },
  fuelCapacity: {
    type: Number,
    default: 50.0
  },
  fuelEfficiency: {
    type: Number,
    default: 10.0  // km/L
  }
});

// Calculate fuel percentage
const fuelPercentage = computed(() => {
  return Math.min(100, Math.max(0, (props.fuelRemaining / props.fuelCapacity) * 100));
});

// Determine color class based on fuel level
const fuelBarColorClass = computed(() => {
  if (fuelPercentage.value < 20) return 'bg-error';
  if (fuelPercentage.value < 50) return 'bg-warning';
  return 'bg-success';
});

// Determine fuel status
const fuelStatus = computed(() => {
  if (fuelPercentage.value < 20) return 'Low';
  if (fuelPercentage.value < 50) return 'Medium';
  return 'Good';
});

// Determine badge class for fuel status
const fuelStatusBadgeClass = computed(() => {
  if (fuelStatus.value === 'Low') return 'badge-error';
  if (fuelStatus.value === 'Medium') return 'badge-warning';
  return 'badge-success';
});

// Calculate estimated range
const estimatedRange = computed(() => {
  return props.fuelRemaining * props.fuelEfficiency;
});
</script>