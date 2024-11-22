<template>
  <div id="app">
    <h1>Streamlink-Web-UI</h1>
    <StreamlinkUi />
  </div>
</template>

<script>
import StreamlinkUi from './components/StreamlinkUi.vue';
import '@fortawesome/fontawesome-free/css/all.css';

export default {
  name: 'App',
  components: {
    StreamlinkUi
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #ababab;
  margin-top: 30px;
}

body {
  background-color: #212121;  ;
}
</style>