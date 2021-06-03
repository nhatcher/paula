import json
import toml
import os
import re

from subprocess import run, PIPE
from tempfile import mkstemp


config = toml.load("config.toml")['tradfri']

ip = config["ip"]
identity = config["identity"]
shared_key = config["shared_key"]
uri = f"coaps://{ip}:5684"
bulb_living_id = "65537"
bulb_bedroom_id = "65538"

print("config", config)


def get_bulb_status(bulb_id):
    (fd, filename) = mkstemp()
    command = ["coap-client", "-m", "get", "-u", identity, "-k", shared_key,  f"{uri}/15001/{bulb_id}", "-o", filename]
    print("Executing:", command)
    run(command, stdout=PIPE)
    with open(filename, "rb") as f:
        result = f.read()
    os.close(fd)
    os.remove(filename)
    return json.loads(result)

def switch_on(bulb_id):
    payload = '{ "3311": [{ "5850": 1 }] }'
    command = ["coap-client", "-m", "put", "-u", identity, "-k", shared_key,  "-e", payload, f"{uri}/15001/{bulb_id}"]
    print("Executing:", command)
    run(command, stdout=PIPE)


def switch_off(bulb_id):
    payload = '{ "3311": [{ "5850": 0 }] }'
    command = ["coap-client", "-m", "put", "-u", identity, "-k", shared_key,  "-e", payload, f"{uri}/15001/{bulb_id}"]
    print("Executing:", command)
    run(command, stdout=PIPE)


def change_bulb(room, dimmer, color=None, transition=None):
    """
    https://github.com/glenndehaan/ikea-tradfri-coap-docs#bulbs
    {
        "3311": [
            {
            "5850": 1, // on / off
            "5851": 254, // dimmer (1 to 254)
            "5706": "f1e0b5", // color in HEX (Don't use in combination with: color X and/or color Y)
            "5709": 65535, // color X (Only use in combination with color Y)
            "5710": 65535, // color Y (Only use in combination with color X)
            "5712": 10 // transition time (fade time)
            }
        ]
    }
    """
    if room == "bedroom":
        bulb_id = bulb_bedroom_id
    else:
        bulb_id = bulb_living_id
    dimmer = int(dimmer)
    if dimmer < 1:
        dimmer = 1
    elif dimmer > 254:
        dimmer = 254
    options = {
        "5850": 1,
        "5851": dimmer,
    }
    if color != None:
        color = color.lower()
        if color.startswith('#'):
            color = color[1:]
        if len(color) == 3:
            color = f"{color}{color}"
        match = re.search(r'^[0-9a-f]{6}$', color)
        if match:
            options["5706"] = color
    if transition != None:
        transition = int(transition)
        if transition < 0:
            transition = 0
        options["5712"] = transition
    payload = json.dumps({ "3311": [options] })
    command = ["coap-client", "-m", "put", "-u", identity, "-k", shared_key,  "-e", payload, f"{uri}/15001/{bulb_id}"]
    print("Executing:", command)
    run(command, stdout=PIPE)

def toggle(room):
    if room == "bedroom":
        bulb_id = bulb_bedroom_id
    else:
        bulb_id = bulb_living_id
    status = get_bulb_status(bulb_id)
    if status["3311"][0]["5850"]:
        switch_off(bulb_id)
    else:
        switch_on(bulb_id)

