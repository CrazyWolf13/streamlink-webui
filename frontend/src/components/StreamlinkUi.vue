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
            <div class="form-group">
              <label>Channel Name:</label>
              <input v-model="startData.name" placeholder="Enter Channel Name" />
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
              <input type="checkbox" v-model="useDefaultFilename" />
              Use default filename
              <div v-if="!useDefaultFilename" class="conditional-options">
                <input type="checkbox" v-model="includeDate" />
                Include date in filename
                <input v-model="startData.customPath" placeholder="Enter custom filename or path" />
              </div>
            </div>
            <div class="form-group">
              <input type="checkbox" v-model="startData.blockAds" />
              Block ads
            </div>
            <button @click="startStream">Start</button>
          </div>
  
          <!-- Running Streams -->
          <div v-if="currentView === 'list'">
            <h2>Running Streams</h2>
            <button @click="confirmTerminateAllStreams" class="terminate-all-btn">Terminate All Streams</button>
            <button @click="fetchRunningStreams" class="refresh-btn">Refresh</button>
            <div v-if="streamsLoading">Loading streams...</div>
            <div v-else>
              <div class="streams-container">
                <div v-for="stream in detailedStreams" :key="stream.stream_id" class="stream-box">
                  <h3>{{ stream.name }}</h3>
                  <p><strong>Stream ID:</strong> {{ stream.stream_id }}</p>
                  <p>
                    <strong>URL:</strong>
                    <a :href="stream.url" target="_blank">{{ stream.url }}</a>
                  </p>
                  <p><strong>Quality:</strong> {{ stream.quality }}</p>
                  <p><strong>Running Since:</strong> {{ formatRunningTime(stream.running_since) }}</p>
                  <p><strong>Filename:</strong> {{ stream.filename }}</p>
                  <p><strong>Output Directory:</strong> {{ stream.output_dir }}</p>
                  <p><strong>Block Ads:</strong> {{ stream.block_ads ? "Yes" : "No" }}</p>
                  <p><strong>Status:</strong> {{ stream.running ? "Running" : "Stopped" }}</p>
                  <button @click="terminateStream(stream.stream_id)" class="terminate-btn">
                    <i class="fa fa-trash"></i> Stop
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Cleanup -->
          <div v-if="currentView === 'cleanup'">
            <h2>Cleanup</h2>
            <button @click="cleanup">Cleanup DB and Logs</button>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        currentView: "start", // Default view
        startData: {
          name: "",
          quality: "audio_only",
          customPath: "",
          blockAds: false,
        },
        useDefaultFilename: true,
        includeDate: false,
        runningStreams: [], // Raw stream IDs from /api/stream_list
        detailedStreams: [], // Detailed data from /api/stream_info
        streamsLoading: false, // Loading state for the Running Streams view
      };
    },
    methods: {
      async startStream() {
        const payload = {
          ...this.startData,
          customPath: this.useDefaultFilename
            ? null
            : this.includeDate
            ? `${this.startData.customPath}_DATE`
            : this.startData.customPath,
        };
        try {
          const response = await axios.post("/api/start", payload);
          alert(`Stream started: ${response.data.message}`);
        } catch (error) {
          console.error(error);
          alert("Failed to start the stream.");
        }
      },
      async terminateStream(stream_id) {
        const confirmation = window.confirm("Are you sure you want to terminate this stream?");
        if (confirmation) {
          try {
            const response = await axios.post(`/api/stop?stream_id=${stream_id}`);
            alert(`Stream terminated: ${response.data.message}`);
            this.fetchRunningStreams(); // Refresh the list after termination
          } catch (error) {
            console.error(error);
            alert("Failed to terminate the stream.");
          }
        }
      },
      async confirmTerminateAllStreams() {
        const confirmation = window.confirm("Are you sure you want to terminate all streams?");
        if (confirmation) {
          this.terminateAllStreams();
        }
      },
      async terminateAllStreams() {
        try {
          const response = await axios.post("/api/stop_all");
          alert(`All streams terminated: ${response.data.message}`);
          this.fetchRunningStreams(); // Refresh the list after termination
        } catch (error) {
          console.error(error);
          alert("Failed to terminate all streams.");
        }
      },
      async fetchRunningStreams() {
        this.streamsLoading = true; // Show loading state
        try {
          // Fetch the list of running streams
          const listResponse = await axios.get("/api/stream_list");
          const streamIds = listResponse.data.running_streams;
  
          // Fetch details for each stream ID
          const detailsPromises = streamIds.map((id) =>
            axios.get(`/api/stream_info?stream_id=${id}`)
          );
  
          const detailsResponses = await Promise.all(detailsPromises);
  
          // Extract detailed stream information
          this.detailedStreams = detailsResponses.map((res) => res.data);
        } catch (error) {
          console.error(error);
          alert("Failed to fetch running streams.");
        } finally {
          this.streamsLoading = false; // Hide loading state
        }
      },
        handleRunningStreamsClick() {
        this.currentView = 'list';
        this.fetchRunningStreams();
        },
      async cleanup() {
        try {
          const response = await axios.get("/api/cleanup");
          alert(response.data.result);
        } catch (error) {
          console.error(error);
          alert("Cleanup failed.");
        }
      },
      formatRunningTime(minutes) {
        const totalSeconds = minutes * 60;
        const wholeMinutes = Math.floor(totalSeconds / 60);
        const remainingSeconds = Math.round(totalSeconds % 60);
        return `${wholeMinutes}m ${remainingSeconds}s`;
      },
    },
  };
  </script>
  
  <style scoped>
  /* Colors */
  :root {
    --twitch-purple: #9146ff;
    --dark-grey: #2d2d2d;
    --light-grey: #393939;
    --white: #ffffff;
    --hover-grey: #4d4d4d;
  }
  
  /* Overall Layout */
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
    color: var(--white);
    flex-grow: 1;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
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
    color: #fff;
    border-radius: 5px;
  }
  
  /* Stream Boxes */
  .stream-box {
    background-color: var(--dark-grey);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .stream-box h3 {
    margin-top: 0;
  }
  
  .stream-box p {
    margin: 5px 0;
  }
  
  .streams-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  button {
    width: auto;
    padding: 8px 16px;
    margin-top: 10px;
  }
  
  button i {
    font-size: 18px;
  }
  
  /* Action Buttons */
  .refresh-btn,
  .terminate-all-btn {
    background-color: var(--twitch-purple);
    color: var(--white);
    padding: 10px;
    margin-top: 10px;
    border-radius: 5px;
    cursor: pointer;
    width: 100%;
    transition: background-color 0.3s ease;
  }
  
  .refresh-btn:hover,
  .terminate-all-btn:hover {
    background-color: #772ce8;
  }
  
  .terminate-btn {
    background-color: transparent;
    color: #d9534f;
    border: none;
    cursor: pointer;
    font-size: 20px;
    margin-left: auto;
    transition: color 0.3s ease;
  }
  
  .terminate-btn:hover {
    color: #c9302c;
  }
  </style>