<template>
  <div class="gauge-container w-full h-64">
    <div class="relative w-full h-full flex items-center justify-center">
      <!-- Gauge Background -->
      <svg class="w-full" viewBox="0 0 200 120">
        <!-- Gauge Ticks -->
        <g v-for="tick in ticks" :key="tick.value">
          <!-- Tick Mark -->
          <line 
            :x1="tick.x1" 
            :y1="tick.y1" 
            :x2="tick.x2" 
            :y2="tick.y2"
            :stroke="tick.color" 
            :stroke-width="tick.major ? 2 : 1"
          />
          <!-- Tick Label -->
          <text 
            v-if="tick.major" 
            :x="tick.labelX" 
            :y="tick.labelY" 
            :fill="tick.color" 
            font-size="8" 
            text-anchor="middle"
          >
            {{ tick.label }}
          </text>
        </g>
        
        <!-- Current Value -->
        <text 
          x="100" 
          y="85" 
          fill="currentColor" 
          font-size="20" 
          font-weight="bold" 
          text-anchor="middle"
        >
          {{ displayValue }} {{ unit }}
        </text>
        
        <!-- Gauge Needle -->
        <g :transform="`rotate(${needleRotation}, 100, 90)`">
          <line 
            x1="100" 
            y1="100" 
            x2="100" 
            y2="50"
            stroke="#ef4444" 
            stroke-width="2"
          />
          <circle cx="100" cy="90" r="5" fill="#ef4444" />
        </g>
      </svg>
      
      <!-- Status badge -->
      <div class="absolute bottom-0 mb-2">
        <span class="badge" :class="statusBadgeClass">{{ status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  value: {
    type: Number,
    required: true,
    default: 0
  },
  maxValue: {
    type: Number,
    default: 8000 
  },
  type: {
    type: String,
    default: 'rpm',
    validator: (value) => ['rpm', 'speed', 'mpg', 'fuel'].includes(value)
  },
  decimals: {
    type: Number,
    default: 0
  }
});

// Add gauge-specific configurations
const gaugeConfig = computed(() => {
  switch(props.type) {
    case 'fuel':
      return {
        colors: {
          low: '#ef4444',  // Red for low fuel
          medium: '#f59e0b', // Amber for medium fuel
          high: '#10b981'  // Green for high fuel
        },
        thresholds: {
          low: 20,  // Below 20% is low
          medium: 50 // Below 50% is medium, above is high
        }
      };
    case 'mpg':
      return {
        colors: {
          low: '#ef4444',  // Red for low MPG
          medium: '#f59e0b', // Amber for medium MPG
          high: '#10b981'  // Green for high MPG
        },
        thresholds: {
          low: 20,  // Below 20 mpg is low
          medium: 35 // Below 35 mpg is medium, above is high
        }
      };
    case 'rpm':
      return {
        colors: {
          normal: "#374151",
          high: "#ef4444"
        },
        thresholds: {
          high: props.maxValue * 0.75
        }
      };
    case 'speed':
    default:
      return {
        colors: {
          normal: "#374151"
        },
        thresholds: {}
      };
  }
});

// Unit based on gauge type
const unit = computed(() => {
  switch(props.type) {
    case 'speed': return 'km/h';
    case 'mpg': return 'mpg';
    case 'fuel': return '%';
    default: return '';
  }
});

// Format value display with proper decimal places
const displayValue = computed(() => {
  return props.value.toFixed(props.decimals);
});

// Calculate needle rotation angle based on value
const needleRotation = computed(() => {
  // Map value from 0-maxValue to -165 to -15 degrees for proper needle positioning
  // This keeps the needle within the visible arc
  const percentage = Math.min(props.value / props.maxValue, 1);
  
  // When value is 0, make sure needle is at the leftmost position
  if (props.value === 0) {
    return -92;
  }
  
  return -92 + (percentage * 150); // -165 = far left, -15 = far right
});

// Generate tick marks for the gauge
const ticks = computed(() => {
  const result = [];
  const numMajorTicks = props.type === 'rpm' ? 8 : 10; // Number of major ticks
  const tickStep = props.maxValue / numMajorTicks;
  
  // Use smaller radius and adjusted angles to keep ticks inside the container
  const outerRadius = 85;
  const innerRadius = 78;
  const labelRadius = 70;
  
  // Adjust the angle range to match the needle rotation
  const startAngle = -Math.PI * 0.92; // About -165 degrees
  const endAngle = -Math.PI * 0.08;   // About -15 degrees
  const angleRange = endAngle - startAngle;
  
  for (let i = 0; i <= numMajorTicks; i++) {
    const value = i * tickStep;
    // Angle formula adjusted to match the needle rotation range
    const angle = startAngle + (i / numMajorTicks) * angleRange;
    
    // Format label based on gauge type
    let label;
    if (props.type === 'rpm') {
      label = (value / 1000).toFixed(0) + 'k';
    } else {
      label = Math.round(value).toString();
    }
    
    // Determine tick color based on value and type
    let tickColor = "#374151"; // Default color
    
    if (props.type === 'rpm' && value >= gaugeConfig.value.thresholds.high) {
      tickColor = gaugeConfig.value.colors.high;
    } else if (props.type === 'fuel') {
      if (value < gaugeConfig.value.thresholds.low) {
        tickColor = gaugeConfig.value.colors.low;
      } else if (value < gaugeConfig.value.thresholds.medium) {
        tickColor = gaugeConfig.value.colors.medium;
      } else {
        tickColor = gaugeConfig.value.colors.high;
      }
    } else if (props.type === 'mpg') {
      if (value < gaugeConfig.value.thresholds.low) {
        tickColor = gaugeConfig.value.colors.low;
      } else if (value < gaugeConfig.value.thresholds.medium) {
        tickColor = gaugeConfig.value.colors.medium;
      } else {
        tickColor = gaugeConfig.value.colors.high;
      }
    }
    
    // Major tick - adjust positions to keep within view
    result.push({
      value: value,
      label: label,
      major: true,
      color: tickColor,
      x1: 100 + outerRadius * Math.cos(angle),
      y1: 110 + outerRadius * Math.sin(angle),
      x2: 100 + innerRadius * Math.cos(angle),
      y2: 110 + innerRadius * Math.sin(angle),
      labelX: 100 + labelRadius * Math.cos(angle),
      labelY: 110 + labelRadius * Math.sin(angle) + 3,
    });
    
    // Minor ticks (if not the last major tick)
    if (i < numMajorTicks) {
      for (let j = 1; j < 5; j++) {
        const minorAngle = angle + (j / 5) * (angleRange / numMajorTicks);
        const minorValue = value + (j / 5) * tickStep;
        
        // Determine minor tick color
        let minorTickColor = "#374151";
        
        if (props.type === 'rpm' && minorValue >= gaugeConfig.value.thresholds.high) {
          minorTickColor = gaugeConfig.value.colors.high;
        } else if (props.type === 'fuel') {
          if (minorValue < gaugeConfig.value.thresholds.low) {
            minorTickColor = gaugeConfig.value.colors.low;
          } else if (minorValue < gaugeConfig.value.thresholds.medium) {
            minorTickColor = gaugeConfig.value.colors.medium;
          } else {
            minorTickColor = gaugeConfig.value.colors.high;
          }
        } else if (props.type === 'mpg') {
          if (minorValue < gaugeConfig.value.thresholds.low) {
            minorTickColor = gaugeConfig.value.colors.low;
          } else if (minorValue < gaugeConfig.value.thresholds.medium) {
            minorTickColor = gaugeConfig.value.colors.medium;
          } else {
            minorTickColor = gaugeConfig.value.colors.high;
          }
        }
        
        result.push({
          value: null,
          major: false,
          color: minorTickColor,
          x1: 100 + outerRadius * Math.cos(minorAngle),
          y1: 110 + outerRadius * Math.sin(minorAngle),
          x2: 100 + (innerRadius + 3) * Math.cos(minorAngle),
          y2: 110 + (innerRadius + 3) * Math.sin(minorAngle),
        });
      }
    }
  }
  
  return result;
});

// Determine status based on value and type
const status = computed(() => {
  if (props.type === 'rpm') {
    if (props.value > props.maxValue * 0.8) return "High";
    if (props.value > props.maxValue * 0.5) return "Moderate";
    return "Normal";
  } else if (props.type === 'speed') {
    if (props.value > 120) return "High";
    if (props.value > 80) return "Moderate";
    return "Normal";
  } else if (props.type === 'fuel') {
    if (props.value < gaugeConfig.value.thresholds.low) return "Low";
    if (props.value < gaugeConfig.value.thresholds.medium) return "Medium";
    return "Good";
  } else if (props.type === 'mpg') {
    if (props.value < gaugeConfig.value.thresholds.low) return "Poor";
    if (props.value < gaugeConfig.value.thresholds.medium) return "Average";
    return "Good";
  }
  return "Normal";
});

// Badge class based on status
const statusBadgeClass = computed(() => {
  if (status.value === "High" || status.value === "Low" || status.value === "Poor") return "badge-error";
  if (status.value === "Moderate" || status.value === "Medium" || status.value === "Average") return "badge-warning";
  return "badge-success";
});
</script>

<style scoped>
.gauge-container {
  position: relative;
}
</style>