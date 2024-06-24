import streamlink

url = "https://twitch.tv/sintica"
quality = "160p"

session = streamlink.Streamlink()

streamlink_options = Options()
streamlink_options.set("disable_ads", True) 
streamlink_options.set("quality", quality)

try:
    session.streamlink(url, options=streamlink_options)
    
    with open("./video.mp4", "wb") as f:
        stream_fd = stream.open()
        try:
            while True:
                data = stream_fd.read(1024)
                if not data:
                    break
                f.write(data)
        finally:
            stream_fd.close()

except streamlink.exceptions.NoStreamsError:
    print("Could not find the desired quality.")
except streamlink.exceptions.NoPluginError:
    print("Could not find a plugin for the given URL.")
except streamlink.exceptions.PluginError as e:
    print(f"Plugin error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")