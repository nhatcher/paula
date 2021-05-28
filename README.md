A simple Telegram bot to control your lights and your camera
============================================================


What if I told you you can use your Raspberry Pi, Python and Telegram to control your Ikea lights?



What hardware do you need?
--------------------------

1. A Raspberry Pi Zero W
2. A Camera module for the RP
3. Ikea TRÅDFRI lights and the [Ikea Gateaway](https://www.ikea.com/gb/en/p/tradfri-gateway-white-20337807/)


How do I install all this?
--------------------------

1. Install Raspian on the RP. Make sure to add ssh access.
2. Add the camera.
3. Create a Telegram Bot (that's extremely easy!)

At the time of writing the RP is still using python2 as default. We will use python3

* Clone this repository
* Create a virtual environment and activate it

     `$ python3 -m venv venv`

     `$ source venv/bin/activate`
* Install the requirements:

     `$ pip install -r requirements.txt`
* Create simple file `config.toml` with the following configuration:

```
[telegram]
token = "<the token you got for BotFather>"
```

You ned to find your `user_id`. Run the command:

`$ python simple_bot.py`

And send a message to your bot. Any message will do. If you do things right you should get a response of the type:

`Hello *****!`

Where the `*****` is the `admin_id`

## Communicating with the IKEA Gateway

Slightly more complex is the IKEA side of things. You need to find the ip of the Gateway. There are many ways of doing that. If you know how to access your router webpage that will show you all the connected devices.

An easy way to inspect the result of running this on the Rapberry Pi:

`$ arp -a`

This will (hopefully) show you a list of connected MAC addresses and IP addresses. You ned the IP of your Gateway (The hostname should be something like GW-)

If none of these two work you will need to do some research yourself.


The IKEA Gateway is a constrained computer and does not use HTTPS (or TCP for that matter). It uses a protocol called [CoAP](https://datatracker.ietf.org/doc/html/rfc7252) (Constrained Application Protocol). There are many python libraries out there that talk that protocol for instance. Of all of them [aiocoap](https://aiocoap.readthedocs.io/en/latest/index.html) seems to be pretty good, and it is used by the home assistant library [pytradfri](https://github.com/home-assistant-libs/pytradfri). This might be a better choise than what we are using here but for now I just have installed the default C implementation [libcoap](https://libcoap.net/install.html)

```bash
sudo apt install build-essential autoconf automake libtool
git clone --recursive https://github.com/obgm/libcoap.git
cd libcoap
git checkout dtls
git submodule update --init --recursive
./autogen.sh
./configure --disable-documentation --disable-shared
make
sudo make install
```

Once done this you need to get the 'Security Code' of your Trådfri Gateway. You will find that bellow the Gateway. For security reasons we cannot use the security code to talk to the Gateway.
Instead we use the security code one to ge a 'shared key' that we can use all around (still need to keep secret, but we can change it if compromised).

Choose an IDENTITY, any word you like, like Ikea or ChuckNorris. With that, the IP address we found and the above mentioned security code run

```
$ coap-client -m post -u "Client_identity" -k "SECURITY_CODE" -e '{"9090":"IDENTITY"}' "coaps://IP_ADDRESS:5684/15011/9063"
```

If successesfull, this will return something like:


```
{"9091":"<pre-shared-key>","9029":"<you-couldn't-care-less-about-this>"}
```

Get that pre-shared key and save it in the `config.toml`