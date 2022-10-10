import socket
import pickle
from flask import Flask, request

app = Flask(__name__)
BUFFER_SIZE = 1024

@app.route('/')
def fs_log():
    return "This is Fibonacci Server (FS)"

def fib(n):
    if n < 0:
        raise ValueError(f"Enter n > 0")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


@app.route('/fibonacci')
def fibonacci():
    n = int(request.args.get('number'))
    return str(fib(n))


def register_with_as(as_ip, as_port, hostname, value, type, ttl):
    msg = ((hostname, value, type, ttl))
    msg_bytes = pickle.dumps(msg)
    as_addr = (as_ip, as_port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(msg_bytes, as_addr)


@app.route('/register', methods=['PUT'])
def register():
    body = request.json
    if not body:
        raise ValueError("body is None")
    hostname = body["hostname"]
    fs_ip    = body["fs_ip"]
    as_ip    = body["as_ip"]
    as_port  = body["as_port"]
    ttl      = body["ttl"]
    register_with_as(as_port=as_port,
                     as_ip=as_ip,
                     hostname=hostname,
                     value=fs_ip,
                     type="A",
                     ttl=ttl)
    return "Registration Done!"


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9090,
            debug=True)
