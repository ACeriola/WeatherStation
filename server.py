'''
NOTE: this includes computation for heat index and highest/lowest humidity/temp
'''
import socket
import threading
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 5678
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
ADMIN_MSG = "ADMIN"
data_store = []

admin_conn = ""
admin_addr = ""

date_format = '%m/%d/%Y %H:%M:%S'

highest_temp = float("-inf")
lowest_temp = float("inf")
highest_humidity = float("-inf")
lowest_humidity = float("inf")

#constants for heat index calculation
c = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-3, -5.481717e-2, 1.22874e-3, 8.5282e-4, -1.99e-6]

def calculate_heat_index(temp_celsius, humidity):
    temp_fahrenheit = (temp_celsius * 9/5) + 32
    heat_index = c[0] + c[1] * temp_fahrenheit + c[2] * humidity + c[3] * temp_fahrenheit * humidity + c[4] * temp_fahrenheit ** 2 + c[5] * humidity ** 2 + c[6] * temp_fahrenheit ** 2 * humidity + c[7] * temp_fahrenheit * humidity ** 2 + c[8] * temp_fahrenheit ** 2 * humidity ** 2
    return heat_index

def track_high_low(temp_celsius, humidity):
  global highest_temp, lowest_temp, highest_humidity, lowest_humidity
  # track the highest and lowest temperature and humidity
  if highest_temp is None or temp_celsius > highest_temp:
    highest_temp = temp_celsius

  if lowest_temp is None or temp_celsius < lowest_temp:
    lowest_temp = temp_celsius

  if highest_humidity is None or humidity > highest_humidity:
    highest_humidity = humidity

  if lowest_humidity is None or humidity < lowest_humidity:
    lowest_humidity = humidity

def handle_connection(conn, addr):
  global highest_temp, lowest_temp, highest_humidity, lowest_humidity
  global admin_conn, admin_addr
  print(f"[NEW CONNECTION] {addr} connected.")

  connected = True
  while connected:
    msg = conn.recv(SIZE).decode(FORMAT)
    if msg == DISCONNECT_MSG:
      connected = False
      print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
      print(f"[CLOSED CONNECTION] {addr} disconnected.")
    
    elif msg == ADMIN_MSG:
      #conn.send(msg.encode(FORMAT))
      admin_conn = conn
      admin_addr = addr
      
    else:
      print(f"[{addr}] {msg}")
      # parse the JSON data received from the client
      data = json.loads(msg)

      # calculate the heat index
      heat_index = round(calculate_heat_index(data["temp_celsius"], data["humidity"]), 3)

      # track the highest and lowest temperature and humidity
      track_high_low(data["temp_celsius"], data["humidity"])

      # update the message dictionary
      data["heat_idx"] = heat_index
      data["hi_temp"] = highest_temp
      data["lo_temp"] = lowest_temp
      data["hi_humid"] = highest_humidity
      data["lo_humid"] = lowest_humidity
    
      # send the updated dictionary to admin
      if admin_conn != "":
        data = json.dumps(data)
        admin_conn.send(data.encode(FORMAT))

      #Add the received JSON data to the data_store list
      data_store.append(data)
  conn.close()

def main():
  print("[STARTING] Server is starting...")
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind(ADDR)
  server.listen()
  print(f"[LISTENING] Server is listening on {IP}:{PORT}")

  while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_connection, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
  main()



