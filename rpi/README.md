# Configuring RPi

## Raspberry Pi 3

1. Flash Raspbian on SD card

 - Create an empty file `ssh` in boot partition

2. [Headless wired LAN] Log in to RPi

 - ip can be taken from the router GUI
 - defaul password: raspberry
 - run `ssh pi@rpi-ip-addr`

https://dev.to/wiaio/set-up-a-raspberry-pi-without-an-external-monitor-or-keyboard--c88


## RPI as a router - RaspAP

Install raspbian, upgrade it:

```
sudo apt-get update
sudo apt-mark hold wpasupplicant
sudo apt dist-upgrade
sudo reboot
```

Install RaspAP
https://github.com/billz/raspap-webgui

Patch: https://github.com/billz/raspap-webgui/issues/141#issuecomment-353804194

```
sudo apt-get install iptables-persistent

sudo vim /etc/hostapd/hostapd.conf

Comment out the driver if you are using rpi3 with wireless

#driver=nl80211
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
beacon_int=100
auth_algs=1
wpa_key_mgmt=WPA-PSK
ssid=raspi-webgui
channel=1
hw_mode=g
wpa_passphrase=ChangeMe
interface=wlan0
wpa=1
wpa_pairwise=TKIP
country_code=AF


sudo vim /etc/default/hostapd
DAEMON_CONF="/etc/hostapd/hostapd.conf"

sudo vim /etc/sysctl.conf
uncomment the line
net.ipv4.ip_forward=1

run this command to activate immediately
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

Run the following commands to create the network translation between the ethernet port eth0 and the wifi port wlan0
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

To make this happen on reboot (so you don't have to type it every time) run 
sudo sh -c "iptables-save > /etc/iptables/rules.v4"
```



-------------------------------------------------------------------


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
    "controlled_ips": [
		{"ip": "xx.xx.xx.xx", "alias": "notebook"},
		{"ip": "yy.yy.yy.yy", "alias": "iPad"}
	],
    "other_ips": [
		{"ip": "zz.zz.zz.zz", "alias": "computer"}
	]
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


# Turn on and off traffic from devices
OFF
```
sudo iptables -D INPUT -s 192.168.1.9 -j DROP
```
ON
```
sudo iptables -D INPUT -s 192.168.1.9 -j DROP
```

# Reboot to restart the bot

Cron task is used:

```
sudo crontab -e
@reboot /home/pi/elnido/rpi/start.sh
```

https://kvz.io/schedule-tasks-on-linux-using-crontab.html
