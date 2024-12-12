import axios from 'axios';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useApiStore = defineStore('api', () => {
  const baseURL = ref(window.config.baseURL || '');

  const client = computed(() => {
    return axios.create({
      baseURL: baseURL.value, 
    });
  });

  const setBaseURL = (url) => {
    baseURL.value = url;
  };

  return { baseURL, client, setBaseURL };
});