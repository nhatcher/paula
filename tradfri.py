import json
import toml
import os

from subprocess import run, PIPE
from tempfile import mkstemp


config = toml.load("config.toml")['tradfri']

ip = config["ip"]
identity = config["identity"]
shared_key = config["shared_key"]
uri = f"coaps://{ip}:5684"
bulb1_id = "65537" 

print("config", config)


def _get_bulb_status(bulb_id):
    (fd, filename) = mkstemp()
    command = ["coap-client", "-m", "get", "-u", identity, "-k", shared_key,  f"{uri}/15001/{bulb_id}", "-o", filename]
    print("Executing:", command)
    run(command, stdout=PIPE)
    with open(filename, "rb") as f:
        result = f.read()
    os.close(fd)
    os.remove(filename)
    return json.loads(result)

def get_bulb_status():
    return _get_bulb_status(bulb1_id)

def switch_on():
    payload = '{ "3311": [{ "5850": 1 }] }'
    command = ["coap-client", "-m", "put", "-u", identity, "-k", shared_key,  "-e", payload, f"{uri}/15001/{bulb1_id}"]
    print("Executing:", command)
    run(command, stdout=PIPE)


def switch_off():
    payload = '{ "3311": [{ "5850": 0 }] }'
    command = ["coap-client", "-m", "put", "-u", identity, "-k", shared_key,  "-e", payload, f"{uri}/15001/{bulb1_id}"]
    print("Executing:", command)
    run(command, stdout=PIPE)

def toggle():
    status = get_bulb_status()
    if status["3311"][0]["5850"]:
        switch_off()
    else:
        switch_on()

