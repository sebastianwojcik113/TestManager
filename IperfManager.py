import iperf3

client = iperf3.Client()
client.server_hostname = '192.168.1.24'
client.port = 5201
client.json_output = False

# Simple main for testing purpose
if __name__ == '__main__':
   result = client.run()