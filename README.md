# Streamlink WebUI 

This Repository currently contains the API for an application which simplifies the download of Twitch Streams.

In the future a nice web-ui will be added.

This project is in early-early alpha, so any reviews, bug reports or feature request are highly desirable.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [API Endpoints](#api-endpoints)
4. [Usage](#usage)
5. [Logging](#logging)
6. [Database Management](#database-management)
7. [Troubleshooting](#troubleshooting)
8. [License](#license)

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



## Configuration

- The application uses Streamlink to handle the streams.
- The database is initialized with SQLAlchemy.
- Logs are stored in the `./logs` directory, and the database schema is managed in `db_schema.py`.

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

## Usage

To interact with the API, you can use `curl` commands as shown below:

### Start a Stream
```bash
curl --request POST \
  --url http://127.0.0.1:8000/start/ \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.2.0' \
  --data '{
    "name": "Twitch_Channel"
}'
```

### Stop All Streams
```bash
curl --request POST \
  --url http://127.0.0.1:8000/stop_all/ \
  --header 'User-Agent: insomnia/9.2.0'
```

### Stop a Specific Stream
```bash
curl --request POST \
  --url 'http://127.0.0.1:8000/stop/?stream_id=fd2c40a9-7754-48d9-a74a-5c2235fbd92d' \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.2.0'
```

### Start a Stream with All Parameters
```bash
curl --request POST \
  --url http://127.0.0.1:8000/start/ \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.2.0' \
  --data '{
    "name": "Twitch_Channel",
    "block_ads": true,
    "append_time": true,
    "quality": "best",
    "time_format": "%Y-%m-%d-%H-%M",
    "output_dir": "/mnt/downloads",
    "base_dl_url": "https://twitch.tv"
}'
```

### List All Running Streams
```bash
curl --request GET \
  --url http://127.0.0.1:8000/stream_list/ \
  --header 'User-Agent: insomnia/9.2.0'
```

### Cleanup Database
```bash
curl --request GET \
  --url http://127.0.0.1:8000/cleanup/ \
  --header 'User-Agent: insomnia/9.2.0'
```

### Get Stream Information
```bash
curl --request GET \
  --url 'http://127.0.0.1:8000/stream_info/?stream_id=52fb1923-96a1-4ae9-a08d-b390c85c0eeb' \
  --header 'User-Agent: insomnia/9.2.0'
```

## Logging

- Logs are created for each download task with detailed information about the streaming and recording process.
- Global logs are stored in `./logs/application-<date>.log`.
- Each download task gets its own log file named based on the stream's filename, stored in the `./logs` directory.

## Database Management

- The database schema is managed using SQLAlchemy.
- The database is initialized with `init_db` and can be cleaned up with the `/cleanup/` endpoint.
- Stream information is stored in the database and can be queried using the `/stream_info/` endpoint.

## Troubleshooting

- Ensure that all necessary packages are installed using `pip install -r requirements.txt`.
- Make sure to initialize the database before starting the application.
- Check the logs for detailed error messages and tracebacks.

## License 

This project is licensed under the BSD 2-Clause License.

---

Developed by CrazyWolf13 with ❤️
