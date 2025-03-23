<template>
  <div v-if="efficiency > 0" class="chart-container w-full h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
  <div v-else class="w-full h-64 flex items-center justify-center text-gray-400">
    No efficiency data available
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from "vue";
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, BarController } from "chart.js";

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, BarController);

const props = defineProps({
  efficiency: {
    type: Number,
    required: true,
  },
});

const chartCanvas = ref(null);
let chartInstance = null;

// Get efficiency color based on score
const getEfficiencyColor = (score) => {
  if (score > 75) return '#34D399'; // emerald-400 
  if (score > 50) return '#60A5FA'; // blue-400
  if (score > 25) return '#FBBF24'; // amber-400
  return '#F87171'; // red-400
};

// Get classification for efficiency score
const getEfficiencyClass = (score) => {
  if (score > 75) return "Excellent";
  if (score > 50) return "Good";
  if (score > 25) return "Average";
  return "Poor";
};

const updateChart = () => {
  if (!chartCanvas.value) return;

  const ctx = chartCanvas.value.getContext("2d");
  
  // Round the efficiency value to 1 decimal place
  const roundedEfficiency = Math.round(props.efficiency * 10) / 10;
  
  if (!chartInstance) {
    chartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Efficiency"],
        datasets: [
          {
            label: "Driver Efficiency",
            data: [roundedEfficiency],
            backgroundColor: getEfficiencyColor(roundedEfficiency),
            borderRadius: 6,
            borderWidth: 0,
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
              stepSize: 25,
              callback: function(value) {
                return value + '%';
              }
            },
            grid: {
              color: 'rgba(200, 200, 200, 0.2)',
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            callbacks: {
              label: (context) => {
                const value = context.raw;
                return `Score: ${value.toFixed(1)}% (${getEfficiencyClass(value)})`;
              }
            }
          },
        },
        animation: {
          duration: 300,
        },
      },
    });
  } else {
    // Update data and color
    chartInstance.data.datasets[0].data = [roundedEfficiency];
    chartInstance.data.datasets[0].backgroundColor = getEfficiencyColor(roundedEfficiency);
    chartInstance.update('none'); // No animation for updates
  }
};

// Watch for efficiency changes
watch(() => props.efficiency, (newValue) => {
  if (typeof newValue === 'number' && !isNaN(newValue)) {
    setTimeout(() => updateChart(), 100);
  }
}, { immediate: false });

onMounted(() => {
  if (props.efficiency > 0) {
    setTimeout(() => updateChart(), 100);
  }
});

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
}
</style>