<template>
    <transition
      :name="transitionName"
      :mode="mode"
      :duration="duration"
      @before-enter="beforeEnter"
      @enter="enter"
      @after-enter="afterEnter"
      @before-leave="beforeLeave"
      @leave="leave"
      @after-leave="afterLeave"
    >
      <slot></slot>
    </transition>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  
  const props = defineProps({
    transitionName: {
      type: String,
      default: 'fade'
    },
    mode: {
      type: String,
      default: 'out-in'
    },
    duration: {
      type: [Number, Object],
      default: 300
    }
  });
  
  const emit = defineEmits([
    'before-enter',
    'enter',
    'after-enter',
    'before-leave',
    'leave',
    'after-leave'
  ]);
  
  // Event handlers
  const beforeEnter = (el) => {
    emit('before-enter', el);
  };
  
  const enter = (el, done) => {
    emit('enter', el, done);
  };
  
  const afterEnter = (el) => {
    emit('after-enter', el);
  };
  
  const beforeLeave = (el) => {
    emit('before-leave', el);
  };
  
  const leave = (el, done) => {
    emit('leave', el, done);
  };
  
  const afterLeave = (el) => {
    emit('after-leave', el);
  };
  </script>
  
  <style scoped>
  /* Fade Transition */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  
  /* Slide Left/Right Transitions */
  .slide-left-enter-active,
  .slide-left-leave-active,
  .slide-right-enter-active,
  .slide-right-leave-active {
    transition: all 0.3s ease-out;
  }
  
  .slide-left-enter-from {
    opacity: 0;
    transform: translateX(20px);
  }
  
  .slide-left-leave-to {
    opacity: 0;
    transform: translateX(-20px);
  }
  
  .slide-right-enter-from {
    opacity: 0;
    transform: translateX(-20px);
  }
  
  .slide-right-leave-to {
    opacity: 0;
    transform: translateX(20px);
  }
  
  /* Slide Up/Down Transitions */
  .slide-up-enter-active,
  .slide-up-leave-active,
  .slide-down-enter-active,
  .slide-down-leave-active {
    transition: all 0.3s ease-out;
  }
  
  .slide-up-enter-from {
    opacity: 0;
    transform: translateY(20px);
  }
  
  .slide-up-leave-to {
    opacity: 0;
    transform: translateY(-20px);
  }
  
  .slide-down-enter-from {
    opacity: 0;
    transform: translateY(-20px);
  }
  
  .slide-down-leave-to {
    opacity: 0;
    transform: translateY(20px);
  }
  
  /* Scale Transition */
  .scale-enter-active,
  .scale-leave-active {
    transition: all 0.3s ease;
  }
  
  .scale-enter-from,
  .scale-leave-to {
    opacity: 0;
    transform: scale(0.95);
  }
  </style>