<template>
  <div class="gauge-container">
    <canvas ref="gaugeCanvas"></canvas>
    <div class="rpm-label">{{ formatNumber(rpm) }} RPM</div>
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

const formatNumber = (num) => {
  return num ? parseFloat(num).toFixed(2) : "0.00";
};

const updateGauge = () => {
  if (!gaugeCanvas.value) return;

  const ctx = gaugeCanvas.value.getContext("2d");

  if (!gaugeChart) {
    gaugeChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [props.rpm, 8000 - props.rpm],
            backgroundColor: ["blue", "lightgray"],
            borderWidth: 0,
            rotation: 270,
            circumference: 180,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: {
          legend: { display: false },
        },
      },
    });
  } else {
    gaugeChart.data.datasets[0].data = [props.rpm, 8000 - props.rpm];
    gaugeChart.update();
  }
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
  bottom: 10px;
  font-size: 24px;
  font-weight: bold;
  color: white;
}
</style>