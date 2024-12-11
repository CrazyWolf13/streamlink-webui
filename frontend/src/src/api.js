import axios from 'axios';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useApiStore = defineStore('api', () => {
  const baseURL = ref('');
  const client = computed(() => axios.create({
    baseURL: baseURL.value, // now a new client will be created reacting to the baseURL change
  }));

  const setBaseURL = (url) => {
    baseURL.value = url;
  };

  return { baseURL, client, setBaseURL };
});