# DNS_Server
Execute the below commands to run on docker and visual studio.

Make files and folders accessible:
sudo chmod 777 /var/run/docker.sock

Create a network:
docker network create dns_app

Build and run:

Run the commands for the Fibonacci Server(FS):
docker build -t fs .
docker run -p 9090:9090 --net=dns_app fs

Run the commands for the User Server(US):
docker build -t us .
docker run -p 8080:8080 --net=dns_app us

Run the commands for the Authoritative Server(AS):
docker build -t as .
docker run --network dns_app --name dns_server -p 53533:53533/udp -it as


After building and running the 3 servers, send a PUT request:
https://reqbin.com/post-online with url as : http://localhost:9090/register
with method : PUT
with content as:

{
  "hostname": "fibonacci.com",
  "fs_ip": "172.18.0.2",
  "as_ip": "172.18.0.4",
  "as_port": 53533,
  "ttl": 100
}

header as : Content-Type: application/json

Note : fs_ip, as_ip shall be in accordance with VStudio window

After sending the PUT request , verify the servers are running by :
http://localhost:8080/fibonacci?hostname=%22fibonacci.com%22&fs_port=9090&number=11&as_ip=%22172.18.0.4%22&as_port=53533