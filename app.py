from flask import Flask, render_template, request, jsonify, flash
import subprocess
import threading
from datetime import datetime
import re
import os
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)


def validate_username(name):
    # Regex to check and validate twitch name
    pattern = r'^\w{3,24}$'
    if re.match(pattern, name):
        return True
    else:
        return False


def read_output(stream, logfile):
    with open(logfile, "a") as log_file:
        for line in stream:
            log_file.write(line)
            log_file.flush()  # Ensure output is immediately written to the file
            print(line, end='')  # Print the updated line to the terminal

def run_subprocess(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        with open(log_file, "w") as logfile:  # Open log file in write mode to clear its contents
            logfile.write("started cmd\n")

        # Create separate threads to continuously read from stdout and stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, log_file))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, log_file))
        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        # Handle the error gracefully here, if needed

def execute_command(command):
    thread = threading.Thread(target=run_subprocess, args=(command,))
    thread.start()
    print("starting Thread")


log_file = "output.log"

if os.path.exists(log_file):
        os.remove(log_file)

 
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('website.html')


@app.route('/start', methods=['POST'])
def start_streamlink():

    #Import the Data from the JSON request.
    data = request.json
    ads = data.get('ads')
    name = data.get('name')
    if not validate_username(name):
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



    execute_command(full_command)
    

    print("Other code is running now.....")
    #print(f"The Command was: {full_command}")
    #print(f"PID is: {pid}")
    #print(f"Name is: {name}")
    #print(f"Starting Time is: {time_value}") 


    
    
    #Deploy a watcher to the process.
    return jsonify({"message": "Stream started successfully."})


if __name__ == '__main__':
   app.run()

#TODO: Implement DB
#TODO: Implement PID and Process Watcher
#TODO: Porcess started successfully not launching correctly
#TODO: Add Twitch API or requests to get the streamer avatar
#TODO: Implement streamlink native Metadata
#TODO: Implement Process Watcher and Data extractor
#TODO: Implement Task lis, Stopper and Relauncher