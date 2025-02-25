<template>
    <div>
        <canvas ref="chartCanvas"></canvas>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart } from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels"; // Ensure plugin is imported

const props = defineProps({
    speed: {
        type: Number,
        required: true,
    },
});

const chartCanvas = ref(null);
let chartInstance = null;

const updateChart = () => {
    if (!chartCanvas.value) return;

    const ctx = chartCanvas.value.getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Speed (km/h)"],
            datasets: [
                {
                    label: "Speed",
                    data: [props.speed || 0], // Prevent undefined error
                    backgroundColor: "red",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 200, // Max speed limit
                    ticks: {
                        stepSize: 50,
                        color: "white", // Ensure readability
                    },
                },
                x: {
                    ticks: {
                        color: "white", // Ensure readability
                    },
                },
            },
            plugins: {
                legend: { display: false },
                datalabels: {
                    color: "white",
                    font: { size: 20, weight: "bold" },
                    formatter: (value) => value.toFixed(2), // Show proper decimal places
                    anchor: "center",
                    align: "center",
                },
            },
        },
        plugins: [ChartDataLabels], // Enable plugin
    });
};

watch(() => props.speed, updateChart);
onMounted(updateChart);
</script>

<style scoped>
canvas {
    max-width: 400px;
    margin-top: 20px;
}
</style>
