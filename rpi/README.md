# Configuring RPi

## Raspberry Pi 3

1. Flash Raspbian on SD card

 - Create an empty file `ssh` in boot partition

2. [Headless wired LAN] Log in to RPi

 - ip can be taken from the router GUI
 - defaul password: raspberry
 - run `ssh pi@rpi-ip-addr`

https://dev.to/wiaio/set-up-a-raspberry-pi-without-an-external-monitor-or-keyboard--c88

## RPi Parental Control

sudo apt install iptables iptables-persistent hostapd dnsmasq squid3


nmap -sn 192.168.1.0/24

https://beebom.com/how-to-use-raspberry-pi-as-router-and-content-filter/


### Nullroute IP using route command

Suppose that bad IP is 65.21.34.4, type the following command at shell:
route add 65.21.34.4 gw 127.0.0.1 lo
or
route add -host IP-ADDRESS reject

UNDO

route delete IP-ADDRESS
or
route del -host IP-ADDRESS reject

Testing
-------
route -n
or
netstat -nr


pi@elnido:~ $ netstat -nr
Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
0.0.0.0         192.168.1.1     0.0.0.0         UG        0 0          0 eth0
192.168.1.0     0.0.0.0         255.255.255.0   U         0 0          0 eth0

https://www.cyberciti.biz/tips/how-do-i-drop-or-block-attackers-ip-with-null-routes.html



### Slack Bot

- Install virtualenv

```virtualenv .venv```

- Install pip dependencies

```pip install -r requirements.pip```

- Run slackbot.py in virtualenv

```python ./slackbot.py```

- Type `ping` in slack

https://github.com/vitorverasm/slackbot-iot

### Config

```
{
    "slack_api_token": "xxxx-111111111111-222222222222-YYYYYYYYYYYYYYYYYYYYYYYY",
    "allowed_user_names": ["user1", "user2"],
    "r7_log_token": "11111111-2222-3333-4444-555555555555",
}
```

# Pi-Hole

Installation instructions: https://blog.cryptoaustralia.org.au/instructions-for-setting-up-pi-hole/

## Installation
```
curl -sSL https://install.pi-hole.net | bash
```

## Check version
executable: `/etc/.pihole/pihole -v`

## Black lists
https://gist.github.com/nkavadias/a039fde5722c4a775142dc6fe8c43391
