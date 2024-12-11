import axios from 'axios';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// Define the store
export const useApiStore = defineStore('api', () => {
  const baseURL = ref(window.config.baseURL || '');
  console.log('Initial baseURL:', baseURL.value); // Print the initial baseURL

  const client = computed(() => {
    console.log('Creating axios client with baseURL:', baseURL.value); // Print the baseURL when creating the axios client
    return axios.create({
      baseURL: baseURL.value, // now a new client will be created reacting to the baseURL change
    });
  });

  const setBaseURL = (url) => {
    console.log('Setting new baseURL:', url); // Print the new baseURL when it is set
    baseURL.value = url;
  };

  return { baseURL, client, setBaseURL };
});

// Export a default axios instance with the initial baseURL
const api = axios.create({
  baseURL: window.config.baseURL || '',
});
console.log('Default axios instance baseURL:', api.defaults.baseURL); // Print the baseURL of the default axios instance

export default api;