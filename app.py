from flask import Flask, render_template
from flask import request
from flask_toastr import Toastr
import subprocess

app = Flask(__name__)

 
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('website.html')
    

@app.route('/launch', methods=['POST'])
def checker():
    if request.form.get('match-with-pairs'):
        print("pairs")
    if request.form.get('match-with-bears'):
        print("bears")
    argument1 = request.form.get('arg1')
    argument2 = request.form.get('arg2')
    if argument1 is None:
        Toastr.info("Here's a message to briefly show to your user")
        print ("Field argument1 cannot be empty")
    whitelist = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-1234567890"
    whitelist_set = set(whitelist)
    if any(c not in whitelist_set for c in argument1):
        print("blocked")
    else:
        print("allowed")
        if any(c not in whitelist_set for c in argument2):
            print("blocked")
        else:
            print("allowed")
            cmd = f'cmd /c "{argument1}" "{argument2}"'
            print(cmd)

    return render_template('website.html')


if __name__ == '__main__':
   app.run()