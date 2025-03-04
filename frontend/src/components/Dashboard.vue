<template>
  <div>
    <h2>Simulated OBD-II Data</h2>
    <p>Speed: {{ formatNumber(obdData.speed) }} km/h</p>
    <p>RPM: {{ formatNumber(obdData.rpm) }}</p>
    <p>Fuel Efficiency: {{ formatNumber(obdData.fuel_efficiency) }} km/L</p>
    <p>Engine Temperature: {{ formatNumber(obdData.engine_temp) }} °C</p>
    <p>Throttle: {{ formatNumber(obdData.throttle) }}%</p>
    <p>Fault Code: <span :class="{ error: obdData.fault_code !== 'None' }">{{ obdData.fault_code }}</span></p>

    <p v-if="efficiencyScore !== null">Efficiency Score: {{ formatNumber(efficiencyScore) }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <div class="chart-container">
      <RPMGauge :rpm="formatNumber(obdData.rpm)" />
      <SpeedChart :speed="obdData.speed" />
      <EfficiencyChart v-if="efficiencyScore !== null && efficiencyScore !== undefined" :efficiency="efficiencyScore" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import RPMGauge from "@/components/RPMGauge.vue";
import SpeedChart from "@/components/SpeedChart.vue";
import EfficiencyChart from "@/components/FuelEfficiencyChart.vue";

const obdData = ref({});
const efficiencyScore = ref(null);
const errorMessage = ref("");
let obdFetchInterval = null;
let efficiencyFetchInterval = null;

// Function to round numbers safely
const formatNumber = (num) => {
  return num ? parseFloat(num).toFixed(2) : "0.00";
};

const fetchOBDData = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/real-time-obd-data");
    if (!response.ok) throw new Error("Failed to fetch OBD data");
    obdData.value = await response.json();
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
        fault_code: obdData.value.fault_code || "None"
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to calculate efficiency: ${errorText}`);
    }

    const result = await response.json();
    efficiencyScore.value = result.efficiency_score;
    errorMessage.value = "";
  } catch (error) {
    console.error("Error calculating efficiency:", error);
    errorMessage.value = error.message;
  }
};

// Start fetching data every second and update efficiency every 2 seconds
onMounted(() => {
  fetchOBDData(); // Initial fetch
  calculateEfficiency(); // Initial efficiency calc
  obdFetchInterval = setInterval(fetchOBDData, 1000);
  efficiencyFetchInterval = setInterval(calculateEfficiency, 1000);
});

// Clear intervals when the component is unmounted
onBeforeUnmount(() => {
  if (obdFetchInterval) clearInterval(obdFetchInterval);
  if (efficiencyFetchInterval) clearInterval(efficiencyFetchInterval);
});
</script>

<style scoped>
.chart-container {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.error {
  color: red;
}
</style>
