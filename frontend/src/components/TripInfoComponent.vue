<template>
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <h2 class="card-title">Trip Information</h2>
        <div class="stats stats-vertical lg:stats-horizontal shadow">
          <div class="stat">
            <div class="stat-title">Distance</div>
            <div class="stat-value">{{ formatDistance(tripData.distance) }}</div>
            <div class="stat-desc">Current Trip</div>
          </div>
          
          <div class="stat">
            <div class="stat-title">Average Speed</div>
            <div class="stat-value text-secondary">{{ formatSpeed(tripData.avgSpeed) }}</div>
            <div class="stat-desc">{{ avgSpeedTrend }}</div>
          </div>
          
          <div class="stat">
            <div class="stat-title">Trip Duration</div>
            <div class="stat-value">{{ formatDuration(tripData.duration) }}</div>
            <div class="stat-desc">Started {{ formatTime(tripData.startTime) }}</div>
          </div>
        </div>
        
        <div class="mt-4">
          <div class="flex justify-between mb-2">
            <span>Avg. Fuel Consumption:</span>
            <span class="font-medium">{{ formatConsumption(tripData.avgConsumption) }}</span>
          </div>
          <div class="flex justify-between mb-2">
            <span>Est. Fuel Remaining:</span>
            <span class="font-medium">{{ formatFuel(tripData.fuelRemaining) }}</span>
          </div>
          <div class="flex justify-between">
            <span>Est. Range:</span>
            <span class="font-medium">{{ formatDistance(tripData.estimatedRange) }}</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const props = defineProps({
    tripData: {
      type: Object,
      required: true,
      default: () => ({
        distance: 0,
        avgSpeed: 0,
        duration: 0,
        startTime: new Date(),
        avgConsumption: 0,
        fuelRemaining: 0,
        estimatedRange: 0,
        prevAvgSpeed: 0
      })
    }
  });
  
  // Format distance in km
  const formatDistance = (km) => {
    return km.toFixed(1) + ' km';
  };
  
  // Format speed in km/h
  const formatSpeed = (speed) => {
    return speed.toFixed(1) + ' km/h';
  };
  
  // Format duration in hours and minutes
  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    } else {
      return `${mins}m`;
    }
  };
  
  // Format time
  const formatTime = (date) => {
    const now = new Date();
    const time = new Date(date);
    
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Format fuel consumption
  const formatConsumption = (consumption) => {
    return consumption.toFixed(1) + ' L/100km';
  };
  
  // Format fuel remaining
  const formatFuel = (liters) => {
    return liters.toFixed(1) + ' L';
  };
  
  // Compute trend text for average speed
  const avgSpeedTrend = computed(() => {
    const diff = props.tripData.avgSpeed - props.tripData.prevAvgSpeed;
    
    if (Math.abs(diff) < 1) {
      return 'Steady';
    }
    
    if (diff > 0) {
      return `↗ ${Math.abs(diff).toFixed(1)} km/h higher`;
    } else {
      return `↘ ${Math.abs(diff).toFixed(1)} km/h lower`;
    }
  });
  </script>