import usb_setup as usbhid
import time
import json
from datetime import datetime
import os

version = "v0"

steer = [0, 0]

engines = [0, 0, 0, 0]

def dumpLogToFile(log):
    now = datetime.now()
    with open("logs/" + str(now.strftime("%Y-%m-%d")) + "-logdump.log", "a") as file:
        nowFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{nowFormatted}] {log}\n")
dumpLogToFile("START")
def sendStatus():
    dataPacket = {
        "name": "lazik",
        "version": version,
        "time": time.time(),
        "engines": {
            "fl": engines[0],
            "fr": engines[1],
            "rl": engines[2],
            "rr": engines[3]
        },
        "steer": {
            "fl" : steer[0],
            "fr" : steer[1]
        }
    }

    json_str = json.dumps(dataPacket)
    print(json_str)
    usbhid.send_data(json_str)

def usbcmdrun():
    global engines
    global steer
    global version

    with open('/dev/hidg0', 'rb') as fd:
        request_bytes = fd.read(64)
    
    command = request_bytes.decode('utf-8').replace('\0', '').strip()
    print(command)
    if command == "DUMPDIR":
        with os.scandir("logs/") as d:
            files = []
            for e in d:
                if(not e.is_dir()):
                    fsize = e.stat().st_size
                    fname = e.name
                    files.append({"name": fname, "size": fsize})
            print(files)
            usbhid.send_data(json.dumps({"action" : "dumpdir", "files": files}))
    if "DUMPLOG" in command:
        requested_fname = command.split()[1]
        with open("logs/" + str(requested_fname), "r") as f:
            logs = f.read()
            usbhid.send_data(json.dumps({"action" : "dumplog", "name" : requested_fname, "log": logs}))
    if command == "KILLENGINES":
        engines = [0, 0, 0, 0]
        sendStatus()
    if "SETENGINE" in command:
        
        print("ENGINE " + command.split()[1] + " = " + str(command.split()[2]))
        engines[int(command.split()[1])] = int(command.split()[2])
        sendStatus()
    if "SETSTEER" in command:
        cmdsplit = command.split()
        print("STEER = " + str(cmdsplit[1]))
        steer[0], steer[1] = cmdsplit[1], cmdsplit[1]
        sendStatus()
    # sendStatus()
    if command == "GET_DATA":
        sendStatus()

if __name__ == "__main__":
    print(" ")
    print(" ")
    print("----------")
    print(" ")
    print(" ")
    print("LAZIK SOFT LOADING")
    print(version)
    usbhid.create_custom_hid_gadget()
    print("LAZIK SOFT READY")
    while True:
        # print(f"VEL: {engines}\nINFO: {lastmsg}", end="\n\r\r")
        try:
            usbcmdrun()
        except KeyboardInterrupt:
            dumpLogToFile("STOP")
            exit()
        except Exception as e:
            dumpLogToFile(f"Error {e}")
            print(f"Error {e}")
    # usbhid.handle_requests()
dumpLogToFile("STOP")