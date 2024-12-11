import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import { useApiStore } from './api';

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);

const apiStore = useApiStore();
apiStore.setBaseURL(window.config.baseURL); // Set the baseURL dynamically from config.js

createApp(App).mount('#app')
