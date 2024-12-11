<template>
  <div id="app">
    <div class="container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <ul>
          <li :class="{ active: currentView === 'start' }" @click="currentView = 'start'">Start Stream</li>
          <li :class="{ active: currentView === 'list' }" @click="handleRunningStreamsClick">Running Streams</li>
          <li :class="{ active: currentView === 'cleanup' }" @click="currentView = 'cleanup'">Cleanup</li>
        </ul>
      </aside>

      <!-- Main Content -->
      <main class="content">
        <!-- Start Stream -->
        <div v-if="currentView === 'start'">
          <h2>Start a Stream</h2>
          <div class="form-group channel-name-container">
            <label>Channel Name:</label>
            <div class="channel-input-avatar">
              <input v-model="startData.name" placeholder="Enter Channel Name" />
              <StyledButton :clickHandler="fetchLiveStatus" class="small-button">Check Live Status</StyledButton>
              <div class="avatar-container">
                <div v-if="!avatarUrl">
                  <!-- SVG fallback-->
                  <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" fill="#4d4d4d" />
                  </svg>
                </div>
              <div v-else>
                <!-- profile image  -->
                <img :src="avatarUrl" alt="Profile Image" class="profile-image-small" />
                <div class="status-indicator" :class="{ 'status-online': isUserLive, 'status-offline': !isUserLive }"></div>
              </div>
            </div>
          </div>
            <div class="form-group">
              <label>Quality:</label>
              <select v-model="startData.quality">
                <option value="audio_only">Audio Only</option>
                <option value="best">Best</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
                <option value="160p">160p</option>
              </select>
            </div>
            <div class="form-group">
              <label>Filename:</label>
              <input type="checkbox" v-model="startData.append_time" />
              Append datetime to filename
            </div>
            <div class="form-group">
              <input type="checkbox" v-model="startData.block_ads" />
              Block ads
            </div>
            <div class="form-group">
              <input type="checkbox" v-model="startData.schedule" />
              Schedule
            </div>
            <StyledButton :clickHandler="startStream">Start</StyledButton>
          </div>
        </div>


        <!-- Running Streams -->
        <div v-if="currentView === 'list'">
          <h2>Running Streams</h2>
          <StyledButton :clickHandler="fetchRunningStreams" class="refresh-btn">Refresh</StyledButton>
          <div v-if="streamsLoading">Loading streams...</div>
          <div v-else>
            <div class="streams-container">
              <div v-for="stream in detailedStreams" :key="stream.stream_id" class="stream-box">
                <div class="scheduled-icon-container invisible">
                  <i class="fas fa-hourglass-half scheduled-icon"></i>
                </div>
                <div class="stream-info">
                  <h3>
                    <a :href="stream.url" target="_blank">{{ stream.name }}</a>
                  </h3>
                  <p><strong>Stream ID:</strong> {{ stream.stream_id }}</p>
                  <p><strong>Quality:</strong> {{ stream.quality }}</p>
                  <p><strong>Running Since:</strong> {{ formatRunningTime(stream.running_since) }}</p>
                  <p><strong>Filename:</strong> {{ stream.filename }}</p>
                  <p><strong>Output Directory:</strong> {{ stream.output_dir }}</p>
                  <p><strong>Block Ads:</strong> {{ stream.block_ads ? "Yes" : "No" }}</p>
                  <p><strong>Status:</strong> {{ stream.running ? "Running" : "Stopped" }}</p>
                </div>
                <div class="profile-image-container">
                  <a :href="stream.url" target="_blank">
                    <img :src="stream.profile_image_url" alt="Profile Image" class="profile-image" />
                  </a>
                </div>
                <button @click="terminateStream(stream.stream_id)" class="terminate-btn" title="Terminate">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
              <div v-for="stream in scheduledStreams" :key="stream.stream_id" class="stream-box">
                <div class="scheduled-icon-container">
                  <i class="fas fa-hourglass-half scheduled-icon"></i>
                </div>
                <div class="stream-info">
                  <h3>
                    <a :href="stream.url" target="_blank">{{ stream.name }}</a>
                  </h3>
                  <p><strong>Stream ID:</strong> {{ stream.stream_id }}</p>
                  <p><strong>Quality:</strong> {{ stream.quality }}</p>
                  <p><strong>Scheduled:</strong> Yes</p>
                  <p><strong>Filename:</strong> {{ stream.filename }}</p>
                  <p><strong>Output Directory:</strong> {{ stream.output_dir }}</p>
                  <p><strong>Block Ads:</strong> {{ stream.block_ads ? "Yes" : "No" }}</p>
                  <p><strong>Status:</strong> {{ stream.running ? "Running" : "Stopped" }}</p>
                </div>
                <div class="profile-image-container">
                  <a :href="stream.url" target="_blank">
                    <img :src="stream.profile_image_url" alt="Profile Image" class="profile-image" />
                  </a>
                </div>
                <button @click="terminateStream(stream.stream_id)" class="terminate-btn" title="Terminate">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
          <button @click="confirmTerminateAllStreams" class="terminate-all-btn" title="Terminate All">
            <i class="fas fa-trash"></i>
          </button>
        </div>

        <!-- Cleanup -->
        <div v-if="currentView === 'cleanup'">
          <h2>Cleanup</h2>
          <StyledButton :clickHandler="cleanup">Cleanup DB and Logs</StyledButton>
        </div>
      </main>
    </div>
  </div>
</template>


<script>
import StyledButton from './StyledButton.vue';
import { useApiStore } from '../api.js'; // Import the store

export default {
  components: { StyledButton },
  data() {
    return {
      currentView: 'start',
      startData: {
        name: '',
        quality: 'best',
        block_ads: true,
        append_time: true,
        schedule: false,
      },
      liveStatusUsername: '', 
      avatarUrl: null, 
      isUserLive: false, 
      runningStreams: [], 
      detailedStreams: [], 
      scheduledStreams: [], 
      streamsLoading: false, 
    };
  },
  methods: {
    async startStream() {
      const payload = {
        name: this.startData.name || '',
        quality: this.startData.quality || 'best',
        block_ads: !!this.startData.block_ads,
        append_time: !!this.startData.append_time, 
        schedule: !!this.startData.schedule,
      };

      try {
        const apiStore = useApiStore();
        const response = await apiStore.client.post('/api/v1/start', payload);
        alert(`Stream started: ${response.data.message}`);
      } catch (error) {
        console.error(error);
        alert('Failed to start the stream.');
      }
    },

    async fetchLiveStatus() {
      if (!this.startData.name.trim()) {
        alert('Please enter a username.');
        return;
      }

      try {
        const apiStore = useApiStore();
        const response = await apiStore.client.get(`/api/v1/get_live_status?username=${this.startData.name}`);
        const liveStatus = response.data.live_status;

        if (liveStatus === 'live') {
          this.isUserLive = true;
        } else if (liveStatus === 'offline') {
          this.isUserLive = false;
        } else {
          throw new Error('Unexpected response format.');
        }

        // Fetch avatar image
        const avatarResponse = await apiStore.client.get(`/api/v1/get_avatar?username=${this.startData.name}`);
        this.avatarUrl = avatarResponse.data.profile_image_url;

      } catch (error) {
        console.error('Error fetching live status:', error);
        alert('Failed to fetch live status or avatar.');
      }
    },

    async terminateStream(stream_id) {
      const confirmation = window.confirm('Are you sure you want to terminate this stream?');
      if (confirmation) {
        try {
          const apiStore = useApiStore();
          const response = await apiStore.client.post(`/api/v1/stop?stream_id=${stream_id}`);
          alert(`Stream terminated: ${response.data.message}`);
          this.fetchRunningStreams(); // reload
        } catch (error) {
          console.error(error);
          alert('Failed to terminate the stream.');
        }
      }
    },
    async confirmTerminateAllStreams() {
      const confirmation = window.confirm('Are you sure you want to terminate all streams?');
      if (confirmation) {
        this.terminateAllStreams(); // terminate all streams
      }
    },
    async terminateAllStreams() {
      try {
        const apiStore = useApiStore();
        const response = await apiStore.client.post('/api/v1/stop_all');
        alert(`All streams terminated: ${response.data.message}`);
        this.fetchRunningStreams(); //reload
      } catch (error) {
        console.error(error);
        alert('Failed to terminate all streams.');
      }
    },
    async fetchRunningStreams() {
      this.streamsLoading = true; // Show loading screen
      try {
        const apiStore = useApiStore();
        // Fetch all running and scheduled stream IDs
        const listResponse = await apiStore.client.get('/api/v1/stream_list');
        const runningStreamIds = listResponse.data.running_streams;
        const scheduledStreamIds = listResponse.data.scheduled_streams;

        // Fetch details for each running stream ID
        const runningDetailsPromises = runningStreamIds.map((id) =>
          apiStore.client.get(`/api/v1/stream_info?stream_id=${id}`)
        );

        const runningDetailsResponses = await Promise.all(runningDetailsPromises);

        // Extract data from each response
        this.detailedStreams = await Promise.all(
          runningDetailsResponses.map(async (res) => {
            const stream = res.data;
            const avatarResponse = await apiStore.client.get(`/api/v1/get_avatar?username=${stream.name}`);
            stream.profile_image_url = avatarResponse.data.profile_image_url;
            return stream;
          })
        );

        // Fetch details for each scheduled stream ID
        const scheduledDetailsPromises = scheduledStreamIds.map((id) =>
          apiStore.client.get(`/api/v1/stream_info?stream_id=${id}`)
        );

        const scheduledDetailsResponses = await Promise.all(scheduledDetailsPromises);

        // Extract detailed stream info
        this.scheduledStreams = await Promise.all(
          scheduledDetailsResponses.map(async (res) => {
            const stream = res.data;
            const avatarResponse = await apiStore.client.get(`/api/v1/get_avatar?username=${stream.name}`);
            stream.profile_image_url = avatarResponse.data.profile_image_url;
            return stream;
          })
        );
      } catch (error) {
        console.error(error);
        alert('Failed to fetch running streams.');
      } finally {
        this.streamsLoading = false;
      }
    },
    handleRunningStreamsClick() {
      this.currentView = 'list';
      this.fetchRunningStreams();
    },
    async cleanup() {
      try {
        const apiStore = useApiStore();
        const response = await apiStore.client.get('/api/v1/cleanup');
        alert(response.data.result);
      } catch (error) {
        console.error(error);
        alert('Cleanup failed.');
      }
    },
    formatRunningTime(minutes) {
      const totalSeconds = minutes * 60;
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = Math.floor(minutes % 60);
      const remainingSeconds = Math.round(totalSeconds % 60);

      if (hours > 0) {
        return `${hours}h ${remainingMinutes}m ${remainingSeconds}s`;
      } else {
        return `${remainingMinutes}m ${remainingSeconds}s`;
      }
    },
  },
};
</script>

<style scoped>
:root {
  --twitch-purple: #9146ff;
  --dark-grey: #2d2d2d;
  --light-grey: #393939;
  --white: #ffffff;
  --hover-grey: #4d4d4d;
  --dark-background: #212121;
  --font-color: #ababab;
}

body {
  background-color: var(--dark-background);
}

/* Layout */
.container {
  display: flex;
  height: 100vh;
}

.sidebar {
  background-color: var(--dark-grey);
  color: var(--white);
  padding: 15px;
  width: 200px;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  cursor: pointer;
  margin: 10px 0;
  padding: 10px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.sidebar li:hover {
  background-color: var(--hover-grey);
}

.sidebar li.active {
  background-color: var(--twitch-purple);
  color: var(--white);
}

.content {
  background-color: var(--light-grey);
  color: var(--font-color);
  flex-grow: 1;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px); 
}

/* Form Styles */
.form-group {
  margin-bottom: 20px;
}

input,
select {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  background-color: #333;
  border: none;
  color: var(--font-color);
  border-radius: 5px;
}

/* Stream Boxes */
.stream-box {
  background-color: var(--dark-grey);
  padding: 20px;
  border-radius: 10px;
  margin-top: 10px;
  display: flex;
  align-items: center; 
  gap: 20px;
  background-color: #333;
  position: relative;
}

.stream-box .stream-info {
  flex-grow: 1;
}

.stream-box h3 {
  margin-top: 0;
}

.stream-box p {
  margin: 5px 0;
}

.stream-box .profile-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 150px;
}

.stream-box img.profile-image {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  margin-right: 10vw;
  transition: transform 0.2s ease-in-out; 
}

.stream-box img.profile-image:hover {
  transform: scale(1.1); 
}

.stream-box .scheduled-icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 10vw;
}

.stream-box .scheduled-icon {
  font-size: 2.5vw;
  color: var(--twitch-purple);
  transition: transform 0.2s ease-in-out;
}

.stream-box .scheduled-icon:hover {
  transform: scale(1.1); 
}

.stream-box .scheduled-icon-container.invisible {
  visibility: hidden;
}

.streams-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  gap: 20px;
  flex-grow: 1; 
  overflow-y: auto; 
  max-height: calc(100vh - 140px); 
}

button {
  width: auto;
  padding: 8px 16px;
  margin-top: 10px;
}

button i {
  font-size: 18px;
}

/* Button Styles */
.terminate-btn {
  background-color: transparent;
  color: #d9534f;
  border: none;
  cursor: pointer;
  font-size: 20px;
  position: absolute;
  top: 10px;
  right: 10px;
  transition: color 0.3s ease;
}

.terminate-btn:hover {
  color: red;
}

.terminate-btn:hover::after {
  position: absolute;
  top: -25px;
  right: 0;
  background-color: var(--dark-grey);
  color: var(--white);
  padding: 5px;
  border-radius: 5px;
  font-size: 12px;
  white-space: nowrap;
}
/* Terminate All Button */
.terminate-all-btn {
  background-color: #d9534f;
  color: var(--white);
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
  width: auto;
  transition: background-color 0.3s ease;
  position: fixed;
  bottom: 10px;
  right: 10px;
}

.terminate-all-btn:hover {
  background-color: red;
}

/* Smaller version of styled button */
.small-button {
  width: 10vw;
}

/* Avatar Container */
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-container svg {
  width: 10vw;
  height: 10vw;
}

.profile-image-small {
  width: 10vw; 
  height: 10vw;
  border-radius: 50%;
  border: 2px solid var(--white);
}

/* Status Indicator */
.status-indicator {
  width: 1vw;
  height: 1vw;
  position: absolute;
  bottom: 5px;
  right: 5px;
  border: 2px solid var(--dark-grey);
  border-radius: 50%;
}

.status-online {
  background-color: #4caf50;
}

.status-offline {
  background-color: #d9534f;
}

.channel-name-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.channel-input-avatar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.channel-input-avatar input {
  flex: 1;
  width: auto;
  max-width: 60vw; 
}
  </style>
