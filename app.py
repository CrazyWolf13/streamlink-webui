from flask import Flask, render_template, request, jsonify, flash
import subprocess
from datetime import datetime

app = Flask(__name__)

 
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('website.html')
    

whitelist = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-1234567890"

def check_name(name):
    for char in name:
        if char not in whitelist:
            return False
    return True




@app.route('/start', methods=['POST'])
def start_streamlink():

    data = request.json
    

    name = data.get('name')
    if not check_name(name):
        return jsonify({'message': 'Name contains unallowed characters'}), 400
    

    acceptable_qualities = ["audio_only", "160p", "worst", "360p", "480p", "720p", "720p60", "1080p60", "best"]
    quality = data.get('quality')
    if quality not in acceptable_qualities:
        return jsonify({'message': 'Invalid quality parameter. Acceptable values are: audio_only, 160p, worst, 360p, 480p, 720p, 720p60, 1080p60, best'}), 400


    ads = data.get('ads')
    if ads == "true":
        ads = "--twitch-disable-ads"
    else:
        ads = ""

    time = data.get('time')
    if time == "true":
        time = datetime.now().strftime("%Y.%m.%d.%H.%M")
        time = f"_{time}"
    else:
        time = ""


    command = [
        "streamlink",
        ads,
        "--output",
        f"O:\\Test\\{name}{time}.mp4",
        f"https://www.twitch.tv/{name}",
        quality
        ]


    print(command)
    subprocess.run(command, shell=True)
    return jsonify({'message': 'Process started successfully'})

if __name__ == '__main__':
   app.run()

#TODO: Porcess started successfully not launching correctly
#TODO: Add Twitch API
#TODO: Implement streamlink native Metadata
#TODO: Implement Process Watcher and Data extractor
#TODO: Implement Task lis, Stopper and Relauncher
#TODO: Implement Custom File Name