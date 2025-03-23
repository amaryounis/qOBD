<template>
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body p-4">
        <h2 class="card-title flex justify-between">
          <span>Predictive Analysis</span>
          <div class="badge badge-primary">AI Powered</div>
        </h2>
        
        <div v-if="loading" class="flex justify-center items-center py-8">
          <div class="loading loading-spinner loading-lg"></div>
        </div>
        
        <div v-else>
          <!-- Main predictions container -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <!-- Maintenance Predictions -->
            <div class="card bg-base-200">
              <div class="card-body p-4">
                <h3 class="text-lg font-semibold flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Maintenance Predictions
                </h3>
                
                <div class="mt-2 space-y-3">
                  <div v-for="(item, index) in predictions.maintenance" :key="index" 
                       class="flex justify-between items-center p-2 rounded-lg"
                       :class="getMaintenanceUrgencyClass(item.urgency)">
                    <div>
                      <div class="font-medium">{{ item.component }}</div>
                      <div class="text-sm opacity-80">{{ item.detail }}</div>
                    </div>
                    <div class="text-right">
                      <div class="font-medium">{{ item.timeframe }}</div>
                      <div class="badge mt-1" :class="getMaintenanceBadgeClass(item.urgency)">
                        {{ item.urgency }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Efficiency Predictions -->
            <div class="card bg-base-200">
              <div class="card-body p-4">
                <h3 class="text-lg font-semibold flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Efficiency Forecasts
                </h3>
                
                <div class="mt-4">
                  <div class="flex justify-between mb-2">
                    <span>Current Fuel Efficiency:</span>
                    <span class="font-medium">{{ formatNumber(predictions.efficiency.current, 1) }} km/L</span>
                  </div>
                  <div class="flex justify-between mb-2">
                    <span>Predicted Next Trip:</span>
                    <span class="font-medium">
                      {{ formatNumber(predictions.efficiency.nextTrip, 1) }} km/L
                      <span 
                        :class="predictions.efficiency.nextTrip > predictions.efficiency.current ? 'text-success' : 'text-error'"
                      >
                        {{ predictions.efficiency.nextTrip > predictions.efficiency.current ? '↗' : '↘' }}
                      </span>
                    </span>
                  </div>
                  <div class="flex justify-between mb-4">
                    <span>Predicted Monthly Avg:</span>
                    <span class="font-medium">
                      {{ formatNumber(predictions.efficiency.monthly, 1) }} km/L
                      <span 
                        :class="predictions.efficiency.monthly > predictions.efficiency.current ? 'text-success' : 'text-error'"
                      >
                        {{ predictions.efficiency.monthly > predictions.efficiency.current ? '↗' : '↘' }}
                      </span>
                    </span>
                  </div>
                  
                  <div class="alert" :class="getEfficiencyAlertClass(predictions.efficiency)">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span>{{ predictions.efficiency.improvement }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Cost Predictions -->
          <div class="card bg-base-200 mb-4">
            <div class="card-body p-4">
              <h3 class="text-lg font-semibold flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Cost Predictions
              </h3>
              
              <div class="overflow-x-auto mt-2">
                <table class="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>Period</th>
                      <th>Fuel Cost</th>
                      <th>Maintenance</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Next Month</td>
                      <td>${{ formatNumber(predictions.costs.month.fuel, 2) }}</td>
                      <td>${{ formatNumber(predictions.costs.month.maintenance, 2) }}</td>
                      <td class="font-medium">${{ formatNumber(predictions.costs.month.total, 2) }}</td>
                    </tr>
                    <tr>
                      <td>Next 3 Months</td>
                      <td>${{ formatNumber(predictions.costs.quarter.fuel, 2) }}</td>
                      <td>${{ formatNumber(predictions.costs.quarter.maintenance, 2) }}</td>
                      <td class="font-medium">${{ formatNumber(predictions.costs.quarter.total, 2) }}</td>
                    </tr>
                    <tr>
                      <td>Next Year</td>
                      <td>${{ formatNumber(predictions.costs.year.fuel, 2) }}</td>
                      <td>${{ formatNumber(predictions.costs.year.maintenance, 2) }}</td>
                      <td class="font-medium">${{ formatNumber(predictions.costs.year.total, 2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="alert alert-info mt-4 text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-4 h-4">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>
                  Predictions based on your driving patterns, current fuel prices, and vehicle condition. 
                  Accuracy improves with more driving data.
                </span>
              </div>
            </div>
          </div>
          
          <!-- Potential Optimizations -->
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-semibold">Optimization Suggestions</h3>
              
              <div class="mt-2 space-y-2">
                <div v-for="(item, index) in predictions.optimizations" :key="index" 
                     class="p-3 bg-base-100 rounded-lg">
                  <div class="flex items-start">
                    <div class="badge badge-accent mt-1 mr-3">{{ item.category }}</div>
                    <div>
                      <div class="font-medium">{{ item.title }}</div>
                      <div class="text-sm mt-1">{{ item.description }}</div>
                      <div class="text-sm font-medium text-success mt-1">
                        Potential Savings: {{ item.saving }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
  
  const props = defineProps({
    obdData: {
      type: Object,
      required: true
    },
    tripData: {
      type: Object,
      required: true
    }
  });
  
  const loading = ref(true);
  const predictions = ref({
    maintenance: [
      { 
        component: 'Oil Change', 
        detail: 'Based on mileage and engine conditions',
        timeframe: 'In 2,500 km', 
        urgency: 'Medium' 
      },
      { 
        component: 'Brake Pads (Front)', 
        detail: '35% remaining, wear pattern detected',
        timeframe: 'In 5,000 km', 
        urgency: 'Low' 
      },
      { 
        component: 'Air Filter', 
        detail: 'Reduced airflow detected',
        timeframe: 'In 1,000 km', 
        urgency: 'High' 
      }
    ],
    efficiency: {
      current: 8.5,
      nextTrip: 8.7,
      monthly: 9.1,
      improvement: 'Try maintaining a more consistent speed on highways to improve fuel economy.'
    },
    costs: {
      month: {
        fuel: 120.50,
        maintenance: 0,
        total: 120.50
      },
      quarter: {
        fuel: 361.50,
        maintenance: 150.00,
        total: 511.50
      },
      year: {
        fuel: 1446.00,
        maintenance: 850.00,
        total: 2296.00
      }
    },
    optimizations: [
      {
        category: 'Driving',
        title: 'Reduce Hard Accelerations',
        description: 'Your acceleration rate is higher than optimal. Gradually accelerating could improve fuel economy.',
        saving: '5-8% fuel economy improvement'
      },
      {
        category: 'Maintenance',
        title: 'Tire Pressure Adjustment',
        description: 'Current tire pressure appears slightly low. Optimal pressure would improve efficiency and tire life.',
        saving: '3% fuel economy improvement'
      },
      {
        category: 'Route',
        title: 'Alternative Routes',
        description: 'Your common routes have high congestion. Alternative routes may reduce idle time.',
        saving: 'Up to 20 minutes per day'
      }
    ]
  });
  
  // Formatting helpers
  const formatNumber = (num, decimals = 2) => {
    return num !== undefined && num !== null ? parseFloat(num).toFixed(decimals) : "0.00";
  };
  
  // Styling helpers for maintenance items
  const getMaintenanceUrgencyClass = (urgency) => {
    switch (urgency.toLowerCase()) {
      case 'high':
        return 'bg-error bg-opacity-10';
      case 'medium':
        return 'bg-warning bg-opacity-10';
      case 'low':
        return 'bg-info bg-opacity-10';
      default:
        return '';
    }
  };
  
  const getMaintenanceBadgeClass = (urgency) => {
    switch (urgency.toLowerCase()) {
      case 'high':
        return 'badge-error';
      case 'medium':
        return 'badge-warning';
      case 'low':
        return 'badge-info';
      default:
        return 'badge-neutral';
    }
  };
  
  // Style helper for efficiency alert
  const getEfficiencyAlertClass = (efficiency) => {
    const trend = efficiency.monthly - efficiency.current;
    
    if (trend > 0.5) return 'alert-success';
    if (trend > 0) return 'alert-info';
    if (trend > -0.5) return 'alert-warning';
    return 'alert-error';
  };
  
  // Fetch predictions from API (simulated)
  const fetchPredictions = () => {
    loading.value = true;
    
    // Simulate API delay
    setTimeout(() => {
      // In a real implementation, this would call your ML model API
      // For simulation, we'll just update with some calculated values based on current data
      
      // Update efficiency predictions based on current data
      predictions.value.efficiency.current = props.tripData.avgConsumption || 8.5;
      predictions.value.efficiency.nextTrip = props.tripData.avgConsumption * (1 + (Math.random() * 0.1 - 0.05));
      predictions.value.efficiency.monthly = predictions.value.efficiency.nextTrip * (1 + (Math.random() * 0.15 - 0.05));
      
      // Update cost predictions
      const monthlyKm = 1200; // Assumed monthly distance
      const fuelPrice = 1.50; // Assumed price per liter
      const fuelConsumption = monthlyKm / predictions.value.efficiency.monthly;
      
      predictions.value.costs.month.fuel = fuelConsumption * fuelPrice;
      predictions.value.costs.quarter.fuel = predictions.value.costs.month.fuel * 3;
      predictions.value.costs.year.fuel = predictions.value.costs.month.fuel * 12;
      
      predictions.value.costs.month.total = predictions.value.costs.month.fuel + predictions.value.costs.month.maintenance;
      predictions.value.costs.quarter.total = predictions.value.costs.quarter.fuel + predictions.value.costs.quarter.maintenance;
      predictions.value.costs.year.total = predictions.value.costs.year.fuel + predictions.value.costs.year.maintenance;
      
      loading.value = false;
    }, 1500);
  };
  
  let predictionInterval = null;
  
  onMounted(() => {
    fetchPredictions();
    // Update predictions periodically
    predictionInterval = setInterval(fetchPredictions, 30000); // Every 30 seconds
  });
  
  onBeforeUnmount(() => {
    if (predictionInterval) clearInterval(predictionInterval);
  });
  </script>