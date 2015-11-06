from flask import Flask, render_template
from flask.helpers import send_from_directory
import subprocess, re, glob, os
from flask.wrappers import Response

app = Flask(__name__)

NFCAP_DIR = "../nfcapd/" # dir where collector collects data
REFRESH_INTERVAL = 1 # if REFRESH_INTERVAL > do refresh; unit is s


@app.route('/static/<path:path>')  # for loading all static files (antipatent, but it is necessary because app is not deployed on webserver )
def send_static(path):
    return send_from_directory('static', path)

@app.route("/clear", methods=['POST'])
def clear():
    for f in glob.glob(NFCAP_DIR +"nfcapd.*"):
        if not re.match(".*nfcapd\.current\.", f):
            os.remove(f) 
    return Response()

@app.route('/')
def index():
    def splitColumns(s):
        return re.split("  +", s)
    data = subprocess.Popen(["nfdump", "-R", NFCAP_DIR], stdout=subprocess.PIPE).stdout.read().decode(encoding='utf_8', errors='strict')
    splited = data.splitlines()
    head =  re.match("(Date first seen) +(Duration) +(Proto) +(Src IP Addr:Port) +(Dst IP Addr:Port) +(Packets) +(Bytes) +(Flows)", splited[0]).groups()
    flows = []
    for d in splited[1:]:
        rowMatch = re.match("(\S+ \S+) +(\S+) +(\S+) +(\S+) +-> +(\S+) +(\d+) +(\d+) +(\d+)", d)
        if rowMatch:
            flows.append(rowMatch.groups())
        else:
            break 
    
    info = splited[1+len(flows):]  
    return render_template('index.html', head=head, flows= flows, info=info, REFRESH_INTERVAL=REFRESH_INTERVAL)

if __name__ == '__main__':
    app.debug = True
    app.run()
