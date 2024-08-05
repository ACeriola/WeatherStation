import signal
import sys
import socket, random, time
from datetime import datetime

# Create socket and other initial values
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
PORT = 5678
SIZE = 1024
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
data = ''

# Connect to the server
sock.connect(ADDR)
print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

# This method exits the server program gracefully.
def handler(signal_received, frame):
    data = DISCONNECT_MSG
    sock.send(data.encode(FORMAT))
    sock.close() # Disconnect from the server
    sys.exit(0)

# handler is ran when SIGINT (ctrl-C) is encountered
signal.signal(signal.SIGINT, handler)

connected = True
while connected:
    # Generate the data
    while True:
        time1 = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        temp = str(round(random.uniform(24, 32), 2))
        humid = str(round(random.uniform(73, 97), 2))
        atm = str(round(random.uniform(950, 1050), 2))

        # Format: {"time": string, "temp_celsius": float, "humidity": float}
        data = '{"time": "' + time1 + '", "temp_celsius": ' + temp + ', "humidity": ' + humid + ', "atmospheric pressure": ' + atm +'}'

        # Send to server
        time.sleep(5)
        sock.send(data.encode(FORMAT))

        print(f"{data}")

    connected = False