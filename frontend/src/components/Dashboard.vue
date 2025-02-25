<template>
    <div>
      <h2>Simulated OBD-II Data</h2>
      <p>Speed: {{ obdData.speed }} km/h</p>
      <p>RPM: {{ obdData.rpm }}</p>
      <p>Fuel Efficiency: {{ obdData.fuel_efficiency }} km/L</p>
  
      <button @click="calculateEfficiency">Calculate Efficiency Score</button>
      <p v-if="efficiencyScore !== null">Efficiency Score: {{ efficiencyScore }}</p>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  
      <div class="chart-container">
        <RPMGauge :rpm="obdData.rpm" />
        <SpeedChart :speed="obdData.speed" />
        <EfficiencyChart v-if="efficiencyScore !== null" :efficiency="efficiencyScore" />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import RPMGauge from "@/components/RPMGauge.vue";
  import SpeedChart from "@/components/SpeedChart.vue";
  import EfficiencyChart from "@/components/FuelEfficiencyChart.vue";
  
  const obdData = ref({});
  const efficiencyScore = ref(null);
  const errorMessage = ref("");
  
  const fetchOBDData = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/obd-data");
      if (!response.ok) throw new Error("Failed to fetch OBD data");
      obdData.value = await response.json();
    } catch (error) {
      console.error("Error fetching OBD data:", error);
      errorMessage.value = "Failed to fetch OBD data. Please try again.";
    }
  };
  
  const calculateEfficiency = async () => {
    if (!obdData.value || Object.keys(obdData.value).length === 0) {
      errorMessage.value = "OBD Data is empty. Please fetch data first.";
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
  
  onMounted(fetchOBDData);
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
  