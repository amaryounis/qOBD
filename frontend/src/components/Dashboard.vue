<template>
  <div :data-theme="theme" class="min-h-screen bg-base-200 w-full" :class="{ 'high-contrast': highContrastMode }">
    <!-- Navbar - make it less prominent -->
    <div class="navbar bg-base-300 shadow-lg h-12">
      <div class="flex-1">
        <a class="btn btn-ghost normal-case text-xl">qOBD Dashboard</a>
      </div>
      <div class="flex-none">
        <div class="dropdown dropdown-end">
          <label tabindex="0" class="btn btn-ghost btn-circle">
            <div class="indicator">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span v-if="hasFaultCode" class="badge badge-xs badge-error indicator-item"></span>
            </div>
          </label>
          <div tabindex="0" class="mt-3 z-[1] card card-compact dropdown-content w-52 bg-base-100 shadow">
            <div class="card-body">
              <span class="font-bold text-lg">Notifications</span>
              <div v-if="hasFaultCode" class="text-error">
                Fault Code: {{ obdData.fault_code }}
              </div>
              <div v-else class="text-success">
                No active alerts
              </div>
            </div>
          </div>
        </div>
        <div class="dropdown dropdown-end">
          <label tabindex="0" class="btn btn-ghost btn-circle avatar">
            <div class="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center">
              <span class="text-xl font-bold">S</span>
            </div>
          </label>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><a @click="openSettings = true">Settings</a></li>
            <li><a @click="toggleTheme">Toggle Theme</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Content with Tab Navigation -->
    <div class="w-full relative">
      <!-- Tab Navigation -->
      <div class="tabs tabs-boxed bg-base-300 justify-center sticky top-0 z-10">
        <a 
          @click="currentSlide = 0" 
          :class="{'tab-active': currentSlide === 0, 'tab': true}"
        >Main Dashboard</a>
        <a 
          @click="currentSlide = 1" 
          :class="{'tab-active': currentSlide === 1, 'tab': true}"
        >Details</a>
      </div>

      <!-- Content Container -->
      <div class="w-full">
        <!-- Slide 1: Main Dashboard -->
        <SlideTransition transitionName="fade">
          <div v-show="currentSlide === 0" class="p-4 overflow-y-auto min-h-[calc(100vh-6rem)]">
            <div class="container mx-auto">
              <!-- Primary Gauges (Always shown on main slide) -->
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title text-center w-full">RPM Gauge</h2>
                    <div class="flex justify-center h-64">
                      <RPMGauge :rpm="obdData.rpm" />
                    </div>
                  </div>
                </div>
                
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title text-center w-full">Speed Gauge</h2>
                    <div class="flex justify-center h-64">
                      <SpeedGauge :speed="obdData.speed" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Customizable components for Slide 1 -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4" v-if="displayInSlide(0, 'statsCards')">
                <!-- Speed, RPM, and Gear Stats Cards -->
                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Speed</div>
                    <div class="stat-value">{{ formatNumber(obdData.speed, 1) }} km/h</div>
                    <div class="stat-desc">Current Vehicle Speed</div>
                  </div>
                </div>

                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Engine RPM</div>
                    <div class="stat-value">{{ formatNumber(obdData.rpm, 0) }}</div>
                    <div class="stat-desc">
                      <div class="badge" :class="getRPMBadgeClass(obdData.rpm)">
                        {{ getRPMStatus(obdData.rpm) }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Gear Position</div>
                    <div class="stat-value text-secondary">{{ formatGear(obdData.gear, obdData.speed) }}</div>
                    <div class="stat-desc">Fuel Efficiency: {{ formatNumber(obdData.fuel_efficiency, 2) }} km/L</div>
                  </div>
                </div>
              </div>

              <!-- Engine Status Card -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4" v-if="displayInSlide(0, 'engineStatus')">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Engine Status</h2>
                    <div class="overflow-x-auto">
                      <table class="table table-zebra w-full">
                        <tbody>
                          <tr>
                            <td>Temperature</td>
                            <td>
                              <div class="flex items-center gap-2">
                                {{ formatNumber(obdData.engine_temp, 1) }} °C
                                <span class="badge" :class="getTempBadgeClass(obdData.engine_temp)">
                                  {{ getTempStatus(obdData.engine_temp) }}
                                </span>
                              </div>
                            </td>
                          </tr>
                          <tr>
                            <td>Throttle Position</td>
                            <td>
                              <div class="flex items-center gap-2">
                                <progress 
                                  class="progress progress-primary w-full" 
                                  :value="obdData.throttle" 
                                  max="100"
                                ></progress>
                                <span>{{ formatNumber(obdData.throttle, 1) }}%</span>
                              </div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                <!-- Diagnostic Status Card -->
                <div class="card bg-base-100 shadow-xl" v-if="displayInSlide(0, 'diagnosticStatus')">
                  <div class="card-body p-4">
                    <h2 class="card-title">
                      Diagnostic Status
                      <div v-if="hasFaultCode" class="badge badge-error gap-2">
                        Error
                      </div>
                      <div v-else class="badge badge-success gap-2">
                        Normal
                      </div>
                    </h2>
                    
                    <div v-if="hasFaultCode" class="alert alert-error">
                      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <div class="font-bold">Fault Code: {{ obdData.fault_code }}</div>
                        <div class="text-xs">{{ getFaultDescription(obdData.fault_code) }}</div>
                      </div>
                    </div>
                    
                    <div v-else class="alert alert-success">
                      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>No fault codes detected</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Efficiency Score on Slide 1 (if configured) -->
              <div v-if="displayInSlide(0, 'efficiencyScore') && efficiencyScore !== null" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Driver Efficiency Score</h2>
                    <div class="flex flex-col md:flex-row gap-4 items-center">
                      <div class="radial-progress text-accent" :style="`--value:${efficiencyScore}; --size:8rem;`">
                        {{ formatNumber(efficiencyScore, 1) }}%
                      </div>
                      <div class="flex-1">
                        <h3 class="text-xl font-bold">{{ getEfficiencyRating(efficiencyScore) }}</h3>
                        <div class="mt-2">
                          <div class="alert" :class="getEfficiencyAlertClass(efficiencyScore)">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span>{{ getEfficiencyTip(efficiencyScore, obdData) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Efficiency Chart on Slide 1 (if configured) -->
              <div v-if="displayInSlide(0, 'efficiencyChart') && showEfficiencyChart && efficiencyScore !== null" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Efficiency Chart</h2>
                    <div class="flex justify-center">
                      <EfficiencyChart :efficiency="efficiencyScore" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </SlideTransition>

        <!-- Slide 2: Additional Information -->
        <SlideTransition transitionName="fade">
          <div v-show="currentSlide === 1" class="p-4 overflow-y-auto min-h-[calc(100vh-6rem)]">
            <div class="container mx-auto">
              <!-- Trip Information Component -->
              <div class="mb-4">
                <TripInfoComponent :tripData="tripData" />
              </div>
              
              <!-- Driving Behavior Analysis Component -->
              <div class="mb-4">
                <DrivingBehaviorComponent :drivingData="drivingData" />
              </div>
              
              <!-- Predictive Model Component -->
              <div class="mb-4">
                <PredictiveModel :obdData="obdData" :tripData="tripData" />
              </div>
              
              <!-- Efficiency Score - if configured for Slide 2 -->
              <div v-if="displayInSlide(1, 'efficiencyScore') && efficiencyScore !== null" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Driver Efficiency Score</h2>
                    <div class="flex flex-col md:flex-row gap-4 items-center">
                      <div class="radial-progress text-accent" :style="`--value:${efficiencyScore}; --size:8rem;`">
                        {{ formatNumber(efficiencyScore, 1) }}%
                      </div>
                      <div class="flex-1">
                        <h3 class="text-xl font-bold">{{ getEfficiencyRating(efficiencyScore) }}</h3>
                        <div class="mt-2">
                          <div class="alert" :class="getEfficiencyAlertClass(efficiencyScore)">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <span>{{ getEfficiencyTip(efficiencyScore, obdData) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Efficiency Chart - if configured for Slide 2 -->
              <div v-if="displayInSlide(1, 'efficiencyChart') && showEfficiencyChart && efficiencyScore !== null" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Efficiency Chart</h2>
                    <div class="flex justify-center">
                      <EfficiencyChart :efficiency="efficiencyScore" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Engine Status - if configured for Slide 2 -->
              <div v-if="displayInSlide(1, 'engineStatus')" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">Engine Status</h2>
                    <div class="overflow-x-auto">
                      <table class="table table-zebra w-full">
                        <tbody>
                          <tr>
                            <td>Temperature</td>
                            <td>
                              <div class="flex items-center gap-2">
                                {{ formatNumber(obdData.engine_temp, 1) }} °C
                                <span class="badge" :class="getTempBadgeClass(obdData.engine_temp)">
                                  {{ getTempStatus(obdData.engine_temp) }}
                                </span>
                              </div>
                            </td>
                          </tr>
                          <tr>
                            <td>Throttle Position</td>
                            <td>
                              <div class="flex items-center gap-2">
                                <progress 
                                  class="progress progress-primary w-full" 
                                  :value="obdData.throttle" 
                                  max="100"
                                ></progress>
                                <span>{{ formatNumber(obdData.throttle, 1) }}%</span>
                              </div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Diagnostic Status - if configured for Slide 2 -->
              <div v-if="displayInSlide(1, 'diagnosticStatus')" class="mb-4">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body p-4">
                    <h2 class="card-title">
                      Diagnostic Status
                      <div v-if="hasFaultCode" class="badge badge-error gap-2">
                        Error
                      </div>
                      <div v-else class="badge badge-success gap-2">
                        Normal
                      </div>
                    </h2>
                    
                    <div v-if="hasFaultCode" class="alert alert-error">
                      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <div class="font-bold">Fault Code: {{ obdData.fault_code }}</div>
                        <div class="text-xs">{{ getFaultDescription(obdData.fault_code) }}</div>
                      </div>
                    </div>
                    
                    <div v-else class="alert alert-success">
                      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>No fault codes detected</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Stats cards on Slide 2 (if configured) -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4" v-if="displayInSlide(1, 'statsCards')">
                <!-- Speed, RPM, and Gear Stats Cards -->
                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Speed</div>
                    <div class="stat-value">{{ formatNumber(obdData.speed, 1) }} km/h</div>
                    <div class="stat-desc">Current Vehicle Speed</div>
                  </div>
                </div>

                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Engine RPM</div>
                    <div class="stat-value">{{ formatNumber(obdData.rpm, 0) }}</div>
                    <div class="stat-desc">
                      <div class="badge" :class="getRPMBadgeClass(obdData.rpm)">
                        {{ getRPMStatus(obdData.rpm) }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="stats shadow bg-base-100">
                  <div class="stat">
                    <div class="stat-title">Gear Position</div>
                    <div class="stat-value text-secondary">{{ formatGear(obdData.gear, obdData.speed) }}</div>
                    <div class="stat-desc">Fuel Efficiency: {{ formatNumber(obdData.fuel_efficiency, 2) }} km/L</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </SlideTransition>
      </div>
    </div>

    <!-- Settings Modal with component placement options -->
    <div v-if="openSettings" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="font-bold text-xl mb-4">Dashboard Settings</h3>
        
        <div class="divider">Display Options</div>
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="label-text">Show RPM Gauge</span> 
            <input type="checkbox" v-model="showRPMGauge" class="toggle toggle-primary" />
          </label>
          <label class="label cursor-pointer">
            <span class="label-text">Show Speed Gauge</span> 
            <input type="checkbox" v-model="showSpeedChart" class="toggle toggle-primary" />
          </label>
          <label class="label cursor-pointer">
            <span class="label-text">Show Efficiency Chart</span> 
            <input type="checkbox" v-model="showEfficiencyChart" class="toggle toggle-primary" />
          </label>
        </div>
        
        <div class="divider">Component Placement</div>
        <div class="grid grid-cols-2 gap-4">
          <div class="card bg-base-200 p-4">
            <h3 class="font-bold mb-2">Main Screen (Slide 1)</h3>
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Status Cards</span> 
                <input type="checkbox" v-model="componentLayout.statsCards.slide1" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Engine Status</span> 
                <input type="checkbox" v-model="componentLayout.engineStatus.slide1" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Diagnostic Status</span> 
                <input type="checkbox" v-model="componentLayout.diagnosticStatus.slide1" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Efficiency Score</span> 
                <input type="checkbox" v-model="componentLayout.efficiencyScore.slide1" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Efficiency Chart</span> 
                <input type="checkbox" v-model="componentLayout.efficiencyChart.slide1" class="checkbox checkbox-primary" />
              </label>
            </div>
          </div>
          
          <div class="card bg-base-200 p-4">
            <h3 class="font-bold mb-2">Details Screen (Slide 2)</h3>
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Status Cards</span> 
                <input type="checkbox" v-model="componentLayout.statsCards.slide2" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Engine Status</span> 
                <input type="checkbox" v-model="componentLayout.engineStatus.slide2" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Diagnostic Status</span> 
                <input type="checkbox" v-model="componentLayout.diagnosticStatus.slide2" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Efficiency Score</span> 
                <input type="checkbox" v-model="componentLayout.efficiencyScore.slide2" class="checkbox checkbox-primary" />
              </label>
              <label class="label cursor-pointer">
                <span class="label-text">Efficiency Chart</span> 
                <input type="checkbox" v-model="componentLayout.efficiencyChart.slide2" class="checkbox checkbox-primary" />
              </label>
            </div>
          </div>
        </div>
        
        <div class="divider">Appearance</div>
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="label-text">High Contrast Mode</span> 
            <input type="checkbox" v-model="highContrastMode" class="toggle toggle-accent" />
          </label>
          <label class="label cursor-pointer">
            <span class="label-text">Dark Theme</span> 
            <input type="checkbox" v-model="isDarkTheme" class="toggle toggle-primary" />
          </label>
        </div>
        
        <div class="modal-action">
          <button @click="openSettings = false" class="btn btn-ghost">Cancel</button>
          <button @click="saveSettings" class="btn btn-primary">Save Settings</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="openSettings = false"></div>
    </div>

    <!-- Toasts for Errors -->
    <div v-if="errorMessage" class="toast toast-end">
      <div class="alert alert-error">
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = ''" class="btn btn-sm">Dismiss</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import RPMGauge from "./RPMGauge.vue";
import SpeedGauge from "./SpeedGauge.vue";
import EfficiencyChart from "./FuelEfficiencyChart.vue";
import TripInfoComponent from "./TripInfoComponent.vue";
import DrivingBehaviorComponent from "./DrivingBehaviorComponent.vue";
import SlideTransition from "./SlideTransition.vue";
import PredictiveModel from "./PredictiveModel.vue";

// State variables
const obdData = ref({
  speed: 0,
  rpm: 0,
  gear: 0,
  fuel_efficiency: 0,
  engine_temp: 0,
  throttle: 0,
  fault_code: "None"
});
const tripData = ref({
  distance: 0,
  avgSpeed: 0,
  duration: 0,
  startTime: new Date(),
  avgConsumption: 0,
  fuelRemaining: 0,
  estimatedRange: 0,
  prevAvgSpeed: 0
});
const drivingData = ref({
  accelerationScore: 3.5,
  brakingScore: 4.2,
  currentEfficiency: 8.5,
  weekEfficiency: 9.2,
  currentHarshAccel: 2,
  weekHarshAccel: 12,
  currentHarshBraking: 1,
  weekHarshBraking: 10
});
const efficiencyScore = ref(null);
const errorMessage = ref("");
const theme = ref("dark");
const openSettings = ref(false);
const showRPMGauge = ref(true);
const showSpeedChart = ref(true);
const showEfficiencyChart = ref(true);
const highContrastMode = ref(false);
const isDarkTheme = ref(true);

// Sliding functionality
const currentSlide = ref(0);
const prevSlide = () => {
  currentSlide.value = currentSlide.value === 0 ? 1 : 0;
};
const nextSlide = () => {
  currentSlide.value = currentSlide.value === 0 ? 1 : 0;
};

// Component layout configuration
const componentLayout = ref({
  statsCards: { slide1: true, slide2: false },
  engineStatus: { slide1: true, slide2: false },
  diagnosticStatus: { slide1: true, slide2: false },
  efficiencyScore: { slide1: false, slide2: true },
  efficiencyChart: { slide1: false, slide2: true }
});

// Helper to determine if a component should be displayed on a specific slide
const displayInSlide = (slideIndex, componentName) => {
  if (slideIndex === 0) {
    return componentLayout.value[componentName]?.slide1 || false;
  } else {
    return componentLayout.value[componentName]?.slide2 || false;
  }
};

// Intervals
let obdFetchInterval = null;
let efficiencyFetchInterval = null;
let tripDataInterval = null;
let drivingDataInterval = null;

// Computed properties
const hasFaultCode = computed(() => {
  return obdData.value.fault_code && obdData.value.fault_code !== "None";
});

// Formatter functions
const formatNumber = (num, decimals = 2) => {
  return num !== undefined && num !== null ? parseFloat(num).toFixed(decimals) : "0.00";
};

const formatGear = (gear, speed) => {
  if (speed === 0) return "N"; // Show "N" for Neutral if car is stopped
  return gear !== undefined && gear !== null ? gear.toString() : "N";
};

// Status and classification functions
const getRPMStatus = (rpm) => {
  if (rpm > 5000) return "High";
  if (rpm > 3000) return "Moderate";
  return "Normal";
};

const getRPMBadgeClass = (rpm) => {
  if (rpm > 5000) return "badge-error";
  if (rpm > 3000) return "badge-warning";
  return "badge-success";
};

const getTempStatus = (temp) => {
  if (temp > 95) return "Critical";
  if (temp > 85) return "Warning";
  return "Normal";
};

const getTempBadgeClass = (temp) => {
  if (temp > 95) return "badge-error";
  if (temp > 85) return "badge-warning";
  return "badge-success";
};

const getEfficiencyRating = (score) => {
  if (score > 75) return "Excellent";
  if (score > 50) return "Good";
  if (score > 25) return "Average";
  return "Poor";
};

const getEfficiencyAlertClass = (score) => {
  if (score > 75) return "alert-success";
  if (score > 50) return "alert-info";
  if (score > 25) return "alert-warning";
  return "alert-error";
};

const getEfficiencyTip = (score, data) => {
  if (data.rpm > 3000) {
    return "Try shifting to a higher gear to reduce RPM.";
  } else if (data.throttle > 70) {
    return "Ease up on the throttle for better fuel economy.";
  } else if (score < 40) {
    return "Maintain a steady speed and avoid rapid acceleration.";
  }
  return "Continue with your current driving pattern.";
};

const getFaultDescription = (code) => {
  const faultCodes = {
    "P0300": "Random/Multiple Cylinder Misfire Detected",
    "P0171": "System Too Lean (Bank 1)",
    "P0420": "Catalyst System Efficiency Below Threshold",
    // Add more codes as needed
  };
  
  return faultCodes[code] || "Unknown error code - consult a mechanic";
};

// Theme toggle function
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value;
  theme.value = isDarkTheme.value ? "dark" : "light";
  document.documentElement.setAttribute('data-theme', theme.value);
  localStorage.setItem('dashboardTheme', theme.value);
};

// API functions with faster update rate for real-time feel
const fetchOBDData = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/real-time-obd-data");
    if (!response.ok) throw new Error("Failed to fetch OBD data");
    
    const data = await response.json();
    if (data.error) {
      throw new Error(data.error);
    }
    
    // Apply a small amount of smoothing/interpolation for a more fluid feel
    if (obdData.value.speed !== 0) {
      const smoothFactor = 0.3;  // Lower = smoother but slower transitions
      obdData.value = {
        speed: obdData.value.speed + (data.speed - obdData.value.speed) * smoothFactor,
        rpm: obdData.value.rpm + (data.rpm - obdData.value.rpm) * smoothFactor,
        gear: data.gear, // Don't interpolate discrete values
        fuel_efficiency: obdData.value.fuel_efficiency + (data.fuel_efficiency - obdData.value.fuel_efficiency) * smoothFactor,
        engine_temp: obdData.value.engine_temp + (data.engine_temp - obdData.value.engine_temp) * smoothFactor,
        throttle: obdData.value.throttle + (data.throttle - obdData.value.throttle) * smoothFactor,
        fault_code: data.fault_code // Don't interpolate fault codes
      };
    } else {
      // Initial load or after a stop - no interpolation
      obdData.value = data;
    }
    
    errorMessage.value = "";
  } catch (error) {
    console.error("Error fetching OBD data:", error);
    errorMessage.value = "Temporary issue fetching OBD data. Retrying...";
  }
};

const calculateEfficiency = async () => {
  if (!obdData.value || Object.keys(obdData.value).length === 0) {
    errorMessage.value = "OBD Data is empty.";
    return;
  }

  // Skip efficiency calculation if speed is zero
  if (obdData.value.speed === 0) {
    efficiencyScore.value = 0;
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/api/efficiency-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        speed: obdData.value.speed || 0,
        rpm: obdData.value.rpm || 0,
        fuel_efficiency: obdData.value.fuel_efficiency || 0,
        engine_temp: obdData.value.engine_temp || 0,
        throttle: obdData.value.throttle || 0,
        fault_code: obdData.value.fault_code || "None",
        gear: obdData.value.gear || 0
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to calculate efficiency: ${errorText}`);
    }

    const result = await response.json();
    if (result.error) {
      throw new Error(result.error);
    }
    
    // Apply smoothing to efficiency score as well
    if (efficiencyScore.value !== null) {
      const smoothFactor = 0.2;
      efficiencyScore.value = efficiencyScore.value + (result.efficiency_score - efficiencyScore.value) * smoothFactor;
    } else {
      efficiencyScore.value = result.efficiency_score;
    }
    
    errorMessage.value = "";
  } catch (error) {
    console.error("Error calculating efficiency:", error);
    // Only show error if it's not the speed=0 error
    if (!error.message.includes("Speed cannot be zero")) {
      errorMessage.value = error.message;
    }
  }
};

// Fetch trip information
const fetchTripData = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/trip-info");
    if (!response.ok) throw new Error("Failed to fetch trip data");
    
    const data = await response.json();
    
    // Apply smoothing for transitions
    const smoothFactor = 0.2;
    
    // Update trip data with smoothing
    tripData.value = {
      distance: tripData.value.distance + (data.distance - tripData.value.distance) * smoothFactor,
      avgSpeed: tripData.value.avgSpeed + (data.avgSpeed - tripData.value.avgSpeed) * smoothFactor,
      duration: data.duration, // Don't smooth time
      startTime: new Date(data.startTime),
      avgConsumption: tripData.value.avgConsumption + (data.avgConsumption - tripData.value.avgConsumption) * smoothFactor,
      fuelRemaining: tripData.value.fuelRemaining + (data.fuelRemaining - tripData.value.fuelRemaining) * smoothFactor,
      estimatedRange: tripData.value.estimatedRange + (data.estimatedRange - tripData.value.estimatedRange) * smoothFactor,
      prevAvgSpeed: data.prevAvgSpeed
    };
    
  } catch (error) {
    console.error("Error fetching trip data:", error);
  }
};

// Fetch driving behavior data
const fetchDrivingBehavior = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/driving-behavior");
    if (!response.ok) throw new Error("Failed to fetch driving behavior data");
    
    const data = await response.json();
    
    // Apply smoothing for transitions
    const smoothFactor = 0.1;
    
    // Update driving data with smoothing
    drivingData.value = {
      accelerationScore: drivingData.value.accelerationScore + (data.accelerationScore - drivingData.value.accelerationScore) * smoothFactor,
      brakingScore: drivingData.value.brakingScore + (data.brakingScore - drivingData.value.brakingScore) * smoothFactor,
      currentEfficiency: drivingData.value.currentEfficiency + (data.currentEfficiency - drivingData.value.currentEfficiency) * smoothFactor,
      weekEfficiency: data.weekEfficiency,
      currentHarshAccel: data.currentHarshAccel,
      weekHarshAccel: data.weekHarshAccel,
      currentHarshBraking: data.currentHarshBraking,
      weekHarshBraking: data.weekHarshBraking
    };
    
  } catch (error) {
    console.error("Error fetching driving behavior data:", error);
  }
};

// Settings functions
const saveSettings = () => {
  openSettings.value = false;
  
  // Apply theme settings
  theme.value = isDarkTheme.value ? "dark" : "light";
  document.documentElement.setAttribute('data-theme', theme.value);
  
  // Apply high contrast mode
  if (highContrastMode.value) {
    document.documentElement.classList.add('high-contrast');
  } else {
    document.documentElement.classList.remove('high-contrast');
  }
  
  // Save all settings to localStorage
  localStorage.setItem('dashboardSettings', JSON.stringify({
    theme: theme.value,
    showRPMGauge: showRPMGauge.value,
    showSpeedChart: showSpeedChart.value,
    showEfficiencyChart: showEfficiencyChart.value,
    highContrastMode: highContrastMode.value,
    componentLayout: componentLayout.value
  }));
};

// Lifecycle hooks
onMounted(() => {
  // Ensure DaisyUI theme is set correctly
  document.documentElement.setAttribute('data-theme', theme.value);

  // Load user settings from localStorage
  const savedSettings = localStorage.getItem('dashboardSettings');
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings);
      theme.value = settings.theme || theme.value;
      isDarkTheme.value = theme.value === 'dark';
      showRPMGauge.value = settings.showRPMGauge ?? showRPMGauge.value;
      showSpeedChart.value = settings.showSpeedChart ?? showSpeedChart.value;
      showEfficiencyChart.value = settings.showEfficiencyChart ?? showEfficiencyChart.value;
      highContrastMode.value = settings.highContrastMode || highContrastMode.value;
      
      // Load component layout if available
      if (settings.componentLayout) {
        componentLayout.value = settings.componentLayout;
      }
    } catch (e) {
      console.error("Error parsing saved settings:", e);
    }
  }

  // Apply high contrast if needed
  if (highContrastMode.value) {
    document.documentElement.classList.add('high-contrast');
  }

  // Initial data fetch
  fetchOBDData();
  calculateEfficiency();
  fetchTripData();
  fetchDrivingBehavior();
  
  // Set intervals for real-time updates
  obdFetchInterval = setInterval(fetchOBDData, 100); // Update every 100ms for smoother display
  efficiencyFetchInterval = setInterval(calculateEfficiency, 500); // Update efficiency less frequently
  tripDataInterval = setInterval(fetchTripData, 1000); // Update trip data every second
  drivingDataInterval = setInterval(fetchDrivingBehavior, 2000); // Update driving behavior every 2 seconds
});

// Clear intervals when the component is unmounted
onBeforeUnmount(() => {
  if (obdFetchInterval) clearInterval(obdFetchInterval);
  if (efficiencyFetchInterval) clearInterval(efficiencyFetchInterval);
  if (tripDataInterval) clearInterval(tripDataInterval);
  if (drivingDataInterval) clearInterval(drivingDataInterval);
  
  // Save settings on unmount
  localStorage.setItem('dashboardSettings', JSON.stringify({
    theme: theme.value,
    showRPMGauge: showRPMGauge.value,
    showSpeedChart: showSpeedChart.value,
    showEfficiencyChart: showEfficiencyChart.value,
    highContrastMode: highContrastMode.value,
    componentLayout: componentLayout.value
  }));
});
</script>

<style scoped>
/* Sliding functionality */
.slider-container {
  height: calc(100vh - 3rem);
  position: relative;
}

.slides {
  width: 200%;
  display: flex;
}

.slide {
  width: 50%;
}

/* High contrast mode styles */
:global(.high-contrast) {
  --contrast-text: white;
  --contrast-bg: black;
  --contrast-highlight: yellow;
}

:global(.high-contrast) .card {
  border: 2px solid var(--contrast-highlight);
}

:global(.high-contrast) .stat-title, 
:global(.high-contrast) .card-title {
  color: var(--contrast-highlight) !important;
}

:global(.high-contrast) .stat-value {
  color: var(--contrast-text) !important;
  font-weight: 800;
}

/* Card animation effects */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Mobile responsiveness adjustments */
@media (max-width: 768px) {
  .grid.grid-cols-2, 
  .grid.grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
</style>