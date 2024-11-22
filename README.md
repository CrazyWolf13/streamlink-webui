# Streamlink WebUI 

This Repository currently contains the API for an application which simplifies the download of Twitch Streams.

I used a FastAPI backend and a Vue.js frontend.

This project is in early-early alpha, so any reviews, bug reports or feature request are highly appreciated.

## Table of Contents

- [Streamlink WebUI](#streamlink-webui)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Showcase](#showcase)
    - [Start job section](#start-job-section)
    - [Running jobs section](#running-jobs-section)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [API Endpoints](#api-endpoints)
    - [Start a Stream](#start-a-stream)
    - [Stop All Streams](#stop-all-streams)
    - [Stop a Specific Stream](#stop-a-specific-stream)
    - [List All Running Streams](#list-all-running-streams)
    - [Get Stream Information](#get-stream-information)
    - [Cleanup Database](#cleanup-database)
    - [Get Avatar](#get-avatar)
    - [Get Live Status](#get-live-status)
  - [Usage](#usage)
  - [Logging](#logging)
  - [Docker Image](#docker-image)
  - [License](#license)
  - [License for Included Software](#license-for-included-software)
      - [Streamlink](#streamlink)
  - [Acknowledgements](#acknowledgements)


## Features

- Use a frontend to record Twitch streams.
- Schedule recordings to start automatically when a channel goes live.
- View all currently running or scheduled recordings.
- Display Twitch avatars.

## Showcase

### Start job section

![Showcase Start Recoring Section](./assets/showcase_1.png)

### Running jobs section

![Showcase Running Streams Section](./assets/showcase_2.png)


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/CrazyWolf13/streamlink-webui.git
    cd streamlink-webui
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Run FastAPI:
    ```bash
    fastapi dev main.py
    ```

4. Start the frontend
    ```bash
    cd streamlink-webui/frontend
    npm install
    yarn serve
    ```

5. Create a Twitch API Key to fetch live status and user avatars:

  1. Go to the [Twitch Developer Portal](https://dev.twitch.tv/console/apps).
  2. Sign in if prompted.
  3. Click on "Register Your Application".
  4. Provide a name for your app and select "Application Integration".
  5. Enter `https://localhost` as the OAuth Redirect URL.
  6. You will receive a Client ID and Client Secret.
  7. In the root directory of the project, create a `.env` file and add the following:
    ```
    CLIENT_ID='your_client_id'
    CLIENT_SECRET='your_client_secret'
    DOWNLOAD_PATH='/home/<your_username>/Download'
    ```



## Configuration

- The application uses Streamlink to handle the streams.
- The database is initialized with SQLAlchemy.
- Logs are stored in the `./logs` directory, and the database schema is configured in `db_schema.py`.

## API Endpoints

### Start a Stream
- **POST** `/start/`
  - Starts a new stream and saves it to the specified output directory.
  - Request body: JSON
  - Example Request:
    ```json
    {
      "name": "Twitch_Channel",
      "block_ads": true,
      "append_time": true,
      "quality": "best",
      "time_format": "%Y-%m-%d-%H-%M",
      "output_dir": "/mnt/downloads",
      "base_dl_url": "https://twitch.tv"
    }
    ```

### Stop All Streams
- **POST** `/stop_all/`
  - Stops all currently running streams.
  
### Stop a Specific Stream
- **POST** `/stop/`
  - Stops a specific stream by `stream_id`.
  - Query parameter: `stream_id` (UUID)

### List All Running Streams
- **GET** `/stream_list/`
  - Returns a list of all running streams.

### Get Stream Information
- **GET** `/stream_info/`
  - Retrieves information for a specific stream.
  - Query parameter: `stream_id` (UUID)

### Cleanup Database
- **GET** `/cleanup/`
  - Deletes the database and all its contents.

### Get Avatar
- **GET** `/get_avatar/`
  - Gets the avatar for a twitch account, uses `username: <twitch_login_name>` as parameter.

### Get Live Status
- **GET** `/get_live_status/`
  - Gets the live status of a twitch user, uses `username: <twitch_login_name>` as parameter.

## Usage

To interact with the API, you can use `curl` commands or even better Insomnia.

## Logging

- Logs are created for each download task with detailed information about the streaming and recording process.
- Global logs are stored in `./logs/application-<date>.log`.
- Each download task gets its own log file named based on the stream's filename, stored in the `./logs` directory.


## Docker Image

Currently there is no docker image as the installation is quite simple and I personally don't user docker if possible, however if there is desire, I may create a Docker Image, just file an Issue with this as a feature Request.


## License 

This project is licensed under the BSD 2-Clause License.

[License](./LICENSE)

## License for Included Software

#### Streamlink

This project is built upon software from the Streamlink project, which is licensed under the BSD 2-Clause License. See below for the full license text:
[Third-Party-Licenses](./third-party-licenses)

## Acknowledgements

We would like to thank the authors and maintainers of [Streamlink](https://github.com/streamlink/streamlink) for their excellent work at maintaining streamlink. Streamlink is invaluable to our project, and we appreciate your dedication to the open-source community.

Thank you!

---

Developed by CrazyWolf13 with ❤️
