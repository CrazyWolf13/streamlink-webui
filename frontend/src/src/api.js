import axios from 'axios';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useApiStore = defineStore('api', () => {
  const baseURL = ref(window.config.baseURL || '');
  console.log('Initial baseURL:', baseURL.value);

  const client = computed(() => {
    console.log('Creating axios client with baseURL:', baseURL.value);
    return axios.create({
      baseURL: baseURL.value, 
    });
  });

  const setBaseURL = (url) => {
    console.log('Setting new baseURL:', url); 
    baseURL.value = url;
  };

  return { baseURL, client, setBaseURL };
});