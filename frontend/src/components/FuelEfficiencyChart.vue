<template>
    <div v-if="efficiency > 0">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from "vue";
  import { Chart } from "chart.js/auto";
  import ChartDataLabels from "chartjs-plugin-datalabels";
  
  const props = defineProps({
    efficiency: {
      type: Number,
      required: true,
    },
  });
  
  const chartCanvas = ref(null);
  let chartInstance = null;
  
  const updateChart = () => {
    if (!chartCanvas.value) return;
  
    const ctx = chartCanvas.value.getContext("2d");
  
    if (!chartInstance) {
      chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Fuel Efficiency"],
          datasets: [
            {
              label: "Fuel Efficiency",
              data: [props.efficiency || 0],
              backgroundColor: "green",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              min: 0,
              max: 100,
              ticks: {
                stepSize: 20,
                color: "white",
              },
            },
            x: {
              ticks: {
                color: "white",
              },
            },
          },
          plugins: {
            legend: { display: false },
            datalabels: {
              color: "white",
              font: { size: 16, weight: "bold" },
              align: "center",
              anchor: "center",
              formatter: (value) => value.toFixed(2),
            },
          },
        },
        plugins: [ChartDataLabels],
      });
    } else {
      chartInstance.data.datasets[0].data = [props.efficiency || 0];
      chartInstance.update();
    }
  };
  
  watch(() => props.efficiency, updateChart);
  onMounted(updateChart);
  </script>
  
  <style scoped>
  canvas {
    max-width: 400px;
    margin-top: 20px;
  }
  </style>