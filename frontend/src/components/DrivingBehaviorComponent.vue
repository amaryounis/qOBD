<template>
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <h2 class="card-title">Driving Behavior Analysis</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
          <!-- Acceleration Behavior -->
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-semibold">Acceleration Behavior</h3>
              <div class="mt-2">
                <div class="flex justify-between">
                  <span>Score:</span>
                  <div class="rating">
                    <input type="radio" disabled :checked="accelerationScore < 2" class="mask mask-star-2 bg-red-400" />
                    <input type="radio" disabled :checked="accelerationScore >= 2 && accelerationScore < 3" class="mask mask-star-2 bg-orange-400" />
                    <input type="radio" disabled :checked="accelerationScore >= 3 && accelerationScore < 4" class="mask mask-star-2 bg-yellow-400" />
                    <input type="radio" disabled :checked="accelerationScore >= 4 && accelerationScore < 5" class="mask mask-star-2 bg-lime-400" />
                    <input type="radio" disabled :checked="accelerationScore >= 5" class="mask mask-star-2 bg-green-400" />
                  </div>
                </div>
                <progress 
                  class="progress mt-2" 
                  :class="accelerationColorClass" 
                  :value="accelerationScore" 
                  max="5"
                ></progress>
                
                <div class="alert mt-4 text-sm" :class="accelerationAlertClass">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>{{ accelerationFeedback }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Braking Behavior -->
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-semibold">Braking Behavior</h3>
              <div class="mt-2">
                <div class="flex justify-between">
                  <span>Score:</span>
                  <div class="rating">
                    <input type="radio" disabled :checked="brakingScore < 2" class="mask mask-star-2 bg-red-400" />
                    <input type="radio" disabled :checked="brakingScore >= 2 && brakingScore < 3" class="mask mask-star-2 bg-orange-400" />
                    <input type="radio" disabled :checked="brakingScore >= 3 && brakingScore < 4" class="mask mask-star-2 bg-yellow-400" />
                    <input type="radio" disabled :checked="brakingScore >= 4 && brakingScore < 5" class="mask mask-star-2 bg-lime-400" />
                    <input type="radio" disabled :checked="brakingScore >= 5" class="mask mask-star-2 bg-green-400" />
                  </div>
                </div>
                <progress 
                  class="progress mt-2" 
                  :class="brakingColorClass" 
                  :value="brakingScore" 
                  max="5"
                ></progress>
                
                <div class="alert mt-4 text-sm" :class="brakingAlertClass">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>{{ brakingFeedback }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Driving History Analysis -->
        <div class="mt-4">
          <h3 class="text-lg font-semibold mb-2">Recent Driving Patterns</h3>
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Current Trip</th>
                  <th>Last 7 Days</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Avg. Efficiency</td>
                  <td>{{ drivingData.currentEfficiency.toFixed(1) }} km/L</td>
                  <td>{{ drivingData.weekEfficiency.toFixed(1) }} km/L</td>
                  <td>
                    <span :class="efficiencyTrendClass">
                      {{ efficiencyTrendIcon }} {{ Math.abs(efficiencyDiff).toFixed(1) }} km/L
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>Harsh Accelerations</td>
                  <td>{{ drivingData.currentHarshAccel }}</td>
                  <td>{{ (drivingData.weekHarshAccel / 7).toFixed(1) }}/day</td>
                  <td>
                    <span :class="accelTrendClass">
                      {{ accelTrendIcon }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>Harsh Braking</td>
                  <td>{{ drivingData.currentHarshBraking }}</td>
                  <td>{{ (drivingData.weekHarshBraking / 7).toFixed(1) }}/day</td>
                  <td>
                    <span :class="brakingTrendClass">
                      {{ brakingTrendIcon }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const props = defineProps({
    drivingData: {
      type: Object,
      required: true,
      default: () => ({
        accelerationScore: 3.5,
        brakingScore: 4.2,
        currentEfficiency: 8.5,
        weekEfficiency: 9.2,
        currentHarshAccel: 2,
        weekHarshAccel: 12,
        currentHarshBraking: 1,
        weekHarshBraking: 10
      })
    }
  });
  
  // Derived values from props
  const accelerationScore = computed(() => props.drivingData.accelerationScore);
  const brakingScore = computed(() => props.drivingData.brakingScore);
  
  // Efficiency difference
  const efficiencyDiff = computed(() => {
    return props.drivingData.currentEfficiency - props.drivingData.weekEfficiency;
  });
  
  // Color classes based on scores
  const accelerationColorClass = computed(() => {
    if (accelerationScore.value >= 4) return 'progress-success';
    if (accelerationScore.value >= 3) return 'progress-warning';
    return 'progress-error';
  });
  
  const brakingColorClass = computed(() => {
    if (brakingScore.value >= 4) return 'progress-success';
    if (brakingScore.value >= 3) return 'progress-warning';
    return 'progress-error';
  });
  
  // Alert classes based on scores
  const accelerationAlertClass = computed(() => {
    if (accelerationScore.value >= 4) return 'alert-success';
    if (accelerationScore.value >= 3) return 'alert-warning';
    return 'alert-error';
  });
  
  const brakingAlertClass = computed(() => {
    if (brakingScore.value >= 4) return 'alert-success';
    if (brakingScore.value >= 3) return 'alert-warning';
    return 'alert-error';
  });
  
  // Feedback messages
  const accelerationFeedback = computed(() => {
    if (accelerationScore.value >= 4) {
      return 'You have smooth acceleration patterns. Keep up the good work!';
    } else if (accelerationScore.value >= 3) {
      return 'Your acceleration is generally smooth, but has room for improvement.';
    } else {
      return 'Try to accelerate more gradually to improve fuel efficiency.';
    }
  });
  
  const brakingFeedback = computed(() => {
    if (brakingScore.value >= 4) {
      return 'Your braking is gentle and anticipatory. Excellent!';
    } else if (brakingScore.value >= 3) {
      return 'Your braking is good, but try to anticipate stops earlier.';
    } else {
      return 'Avoid hard braking by maintaining more distance from vehicles ahead.';
    }
  });
  
  // Trend formatting for efficiency
  const efficiencyTrendIcon = computed(() => {
    if (Math.abs(efficiencyDiff.value) < 0.5) return '→';
    return efficiencyDiff.value > 0 ? '↗' : '↘';
  });
  
  const efficiencyTrendClass = computed(() => {
    if (Math.abs(efficiencyDiff.value) < 0.5) return 'text-base-content';
    return efficiencyDiff.value > 0 ? 'text-success' : 'text-error';
  });
  
  // Trend formatting for harsh acceleration
  const accelTrendIcon = computed(() => {
    const current = props.drivingData.currentHarshAccel;
    const avg = props.drivingData.weekHarshAccel / 7;
    
    if (Math.abs(current - avg) < 0.5) return '→ No change';
    return current > avg ? '↗ Increased' : '↘ Decreased';
  });
  
  const accelTrendClass = computed(() => {
    const current = props.drivingData.currentHarshAccel;
    const avg = props.drivingData.weekHarshAccel / 7;
    
    if (Math.abs(current - avg) < 0.5) return 'text-base-content';
    return current > avg ? 'text-error' : 'text-success';
  });
  
  // Trend formatting for harsh braking
  const brakingTrendIcon = computed(() => {
    const current = props.drivingData.currentHarshBraking;
    const avg = props.drivingData.weekHarshBraking / 7;
    
    if (Math.abs(current - avg) < 0.5) return '→ No change';
    return current > avg ? '↗ Increased' : '↘ Decreased';
  });
  
  const brakingTrendClass = computed(() => {
    const current = props.drivingData.currentHarshBraking;
    const avg = props.drivingData.weekHarshBraking / 7;
    
    if (Math.abs(current - avg) < 0.5) return 'text-base-content';
    return current > avg ? 'text-error' : 'text-success';
  });
  </script>