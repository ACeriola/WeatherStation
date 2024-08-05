import socket, json, csv
import threading, time
from datetime import datetime

# Create socket and other initial values
admin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
PORT = 5678
SIZE = 1024
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
ADMIN_MSG = "ADMIN"

admin_conn = ""
admin_addr = ""

date_format = '%m/%d/%Y %H:%M:%S'


def refresh_csv():
  file = open("results.csv", "w")
  file.close()


def write_data_to_csv(data, filename):

  #open the CSV file in append mode
  with open(filename, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(data)


def print_info(heat_idx, h_temp, l_temp, h_humidity, l_humidity):
  print("===================================\n")
  print(f"Heat Index\t\t: {heat_idx}")
  print(f"Highest Temperature\t: {h_temp}°C")
  print(f"Lowest Temperature\t: {l_temp}°C")
  print(f"Highest Humidity\t: {h_humidity}%")
  print(f"Lowest Humidity\t\t: {l_humidity}%\n")


def process_admin():
  print("\n\n[CONNECTED TO SERVER]\n\n")

  while True:
    admin.send(ADMIN_MSG.encode(FORMAT))
    msg = admin.recv(SIZE).decode(FORMAT)
    # parse the data received
    data = json.loads(msg)
    # convert the time string back to datetime
    data["time"] = datetime.strptime(data["time"], date_format)

    # prepare data for writing to csv
    store_data = [
      data["time"], data["temp_celsius"], data["humidity"], data["heat_idx"], data["rain"], data["atm"]
    ]
    write_data_to_csv(store_data, 'results.csv')

    # update the highest and lowest temp/humidity values
    heat_idx = data["heat_idx"]
    h_temp, l_temp = data["hi_temp"], data["lo_temp"]
    h_humidity, l_humidity = data["hi_humid"], data["lo_humid"]
    print_info(heat_idx, h_temp, l_temp, h_humidity, l_humidity)

def main():
  print("WEATHER STATION\n")

  curr_date = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
  print(f"Date: {curr_date}\n")

  # set up csv file
  header = ['date_time', 'temp_celsius', 'humdity', 'heat_index', 'rain', 'atm']
  refresh_csv()
  write_data_to_csv(header, 'results.csv')

  # Connect to the server
  admin.connect(ADDR)
  thread = threading.Thread(target=process_admin)
  thread.start() 

if __name__ == "__main__":
  main()
