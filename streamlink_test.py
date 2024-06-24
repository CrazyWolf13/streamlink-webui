import streamlink

url = "https://twitch.tv/LetsHugoTV"
stream_quality = "160p"

session = streamlink.Streamlink()

try:
    plugin = session.resolve_url(url)
    plugin.options.set("disable_ads", True) 
    streamlink.stream(url, stream_quality)
    
    streams = streamlink.streams()
    
    with open("./video.mp4", "wb") as f:
        stream_fd = streamlink.open()
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
