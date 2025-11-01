import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import { useApiStore } from './api';

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);

const apiStore = useApiStore(pinia);
apiStore.setBaseURL(window.config.baseURL); 

app.mount('#app')
