from flask import Flask, render_template, request, jsonify, flash
import subprocess
import threading
from datetime import datetime
import re

app = Flask(__name__)

 
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('website.html')
    

def validate_username(name):
    # Regular expression pattern for the username validation
    pattern = r'^\w{3,24}'

        # Check if the username matches the pattern
    if re.match(pattern, name):
        return True
    else:
        return False


def run_subprocess(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output and output.strip():
            print(output.strip())


    process.wait()
    return process.pid

@app.route('/start', methods=['POST'])
def start_streamlink():

    #Import the Data from the JSON request.
    data = request.json
    ads = data.get('ads')
    name = data.get('name')
    if validate_username(name):
        print(f"{name}: Valid username")
    else:
        return jsonify({'message': 'Name contains unallowed characters'}), 400

    
    #Fetch the time to be included in the file name if choosen.
    time = data.get('time')
    time_value = datetime.now().strftime("%Y.%m.%d.%H.%M")
    time_value = f"_{time}"

    acceptable_qualities = ["audio_only", "160p", "worst", "360p", "480p", "720p", "720p60", "1080p60", "best"]
    quality = data.get('quality')
    if quality not in acceptable_qualities:
        return jsonify({'message': 'Invalid quality parameter. Acceptable values are: audio_only, 160p, worst, 360p, 480p, 720p, 1080p60, best'}), 400
    if quality == "audio_only":
        extension = ".mp3"
    else:
        extension = ".mp4"

    
    # Code to build the command
    command = ["streamlink"]
    if ads == "true":
        command.append(" --twitch-disable-ads")
    command.append(" --output")
    command.append(" O:\\Test\\")
    if time == "true":
        command.append(time_value)
    command.append(name)
    command.append(extension)
    command.append(" https://www.twitch.tv/")
    command.append(name)
    command.append(f" {quality}")
    
    full_command = "".join(command)
    
    pid = run_subprocess(full_command)
    

    print("Other code is running now.....")
    #TODO: Log Process ID and other data to DB file.
    #print(f"The Command was: {full_command}")
    #print(f"PID is: {pid}")
    #print(f"Name is: {name}")
    #print(f"Starting Time is: {time_value}") 


    
    
    #Deploy a watcher to the process.
    return jsonify({"message": "Stream started successfully."})


if __name__ == '__main__':
   app.run()

#TODO: Porcess started successfully not launching correctly
#TODO: Add Twitch API
#TODO: Implement streamlink native Metadata
#TODO: Implement Process Watcher and Data extractor
#TODO: Implement Task lis, Stopper and Relauncher