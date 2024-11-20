<template>
  <div id="app">
    <h1>Streamlink-UI</h1>
    <StreamlinkUi />
  </div>
</template>

<script>
import StreamlinkUi from './components/StreamlinkUi.vue';

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
  color: #2c3e50;
  margin-top: 60px;
}
</style>