<template>
    <div class="gauge-container">
      <canvas ref="gaugeCanvas"></canvas>
      <div class="rpm-label">{{ rpm }} RPM</div> <!-- Label correctly placed under the arc -->
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from "vue";
  import { Chart, ArcElement } from "chart.js";
  
  Chart.register(ArcElement);
  
  const props = defineProps({
    rpm: {
      type: Number,
      required: true,
    },
  });
  
  const gaugeCanvas = ref(null);
  let gaugeChart = null;
  
  const updateGauge = () => {
    if (!gaugeCanvas.value) return;
  
    const ctx = gaugeCanvas.value.getContext("2d");
  
    if (gaugeChart) {
      gaugeChart.destroy();
    }
  
    gaugeChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [props.rpm, 8000 - props.rpm], // Max RPM = 6000
            backgroundColor: ["blue", "lightgray"],
            borderWidth: 0,
            rotation: 270, // Start at bottom (counterclockwise)
            circumference: 180, // Moves from left to right
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%", // Creates a speedometer effect
        plugins: {
          legend: { display: false },
        },
      },
    });
  };
  
  watch(() => props.rpm, updateGauge);
  onMounted(updateGauge);
  </script>
  
  <style scoped>
  .gauge-container {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .rpm-label {
    position: absolute;
    bottom: 10px; /* Adjust placement under the arc */
    font-size: 24px;
    font-weight: bold;
    color: white;
  }
  </style>
  