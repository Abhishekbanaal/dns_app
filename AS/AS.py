import socket
import pickle
import json
import time
import os

HOST_IP = "0.0.0.0"
SERVER_PORT = 53533
BUFFER_SIZE = 1024
# Map /tmp/ on localhost to /tmp/ in the docker container
AUTH_SERVER_DB_FILE = "/tmp/auth_db.json"
TYPE = "A"


def save_dns_record(name, value, type, ttl):
    """
    - value is the IP adddress
    - type is always A
    """
    # Create the DB file if it doesn't exist
    if not os.path.exists(AUTH_SERVER_DB_FILE):
        with open(AUTH_SERVER_DB_FILE, "w") as f:
            json.dump({}, f, indent=4)

    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    # Timestamp at which this record will expire
    ttl_ts = time.time() + ttl

    existing_records[name] = (value, ttl_ts, ttl)

    with open(AUTH_SERVER_DB_FILE, "w") as f:
        json.dump(existing_records, f, indent=4)

def get_dns_record(name):
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    value, ttl_ts, ttl = existing_records[name]

    if time.time() > ttl_ts:
        return None
    return (TYPE, name, value, ttl_ts, ttl)


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST_IP, SERVER_PORT))

    while (True):
        msg_bytes, client_addr = udp_socket.recvfrom(BUFFER_SIZE)
        msg = pickle.loads(msg_bytes)
        if len(msg) == 4:
            name, value, type, ttl = pickle.loads(msg_bytes)
            save_dns_record(name=name, type=type, value=value, ttl=ttl)
        elif len(msg) == 2:
            type, name = msg
            dns_record = get_dns_record(name)
            if dns_record:
                (_, name, value, _, ttl) = dns_record
                response = (type, name, value, ttl)
            else:
                # Return an empty string if there is no record or the TTL expired
                response = ""
            response_bytes = pickle.dumps(response)
            udp_socket.sendto(response_bytes, client_addr)
        else:
            msg = f"Expected msg of len 4 or 2, got :{msg!r}"
            udp_socket.sendto(msg, client_addr)


if __name__ == '__main__':
    main()
