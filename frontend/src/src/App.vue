<template>
  <div id="app">
    <header class="hero">
      <div class="hero-inner">
        <h1 class="hero-title">Streamlink Web UI</h1>
        <p class="hero-sub">Clean, modern dark interface</p>
      </div>
    </header>
    <main class="app-shell">
      <StreamlinkUi />
    </main>
  </div>
</template>

<script>
import StreamlinkUi from './components/StreamlinkUi.vue';
import '@fortawesome/fontawesome-free/css/all.css';

export default {
  name: 'App',
  components: { StreamlinkUi }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

:root{
  --bg-1: #0f0c29;
  --bg-2: #302b63;
  --bg-3: #24243e;
  --card: rgba(255,255,255,0.04);
  --muted: #9aa0a6;
  --accent: #6441a5; /* twitch-like */
}

*{box-sizing:border-box}
html,body,#app{height:100%;margin:0}
body{
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  background: linear-gradient(135deg,var(--bg-1),var(--bg-2),var(--bg-3));
  color: var(--muted);
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
}

.hero{
  padding: 28px 24px;
  background: linear-gradient(90deg, rgba(255,255,255,0.02), transparent);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.hero-inner{max-width:1200px;margin:0 auto;display:flex;flex-direction:column;align-items:flex-start;gap:6px}
.hero-title{
  margin:0;color:#fff;font-size:28px;font-weight:700;letter-spacing:0.4px;text-shadow:0 6px 24px rgba(100,65,165,0.12)
}
.hero-sub{margin:0;color:var(--muted);font-size:13px}

.app-shell{max-width:1200px;margin:24px auto;padding:20px}

/* Make StreamlinkUi content appear as elevated card */
.content{background:var(--card);backdrop-filter:blur(6px);border-radius:12px;padding:22px;color:inherit}

/* Stronger default card shadows for inner items */
.stream-box{box-shadow:0 10px 30px rgba(2,6,23,0.6)}

/* Accent links */
a{color:var(--accent)}

/* Ensure smaller UI elements look crisp */
button{font-family:inherit}
</style>
