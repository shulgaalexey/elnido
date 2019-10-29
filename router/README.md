# Router

## Configuring router

### Huawei HG659 with Vodafone firmware

Configure phishing protection

Set up Cisco OpenDNS as DNS, which allows to use its phishing protection

1. Login as admin in http://192.168.1.1/html/advance.html#internet

2. Edit Internet_vdsl properties

- IPv4 primary DNS server: 208.67.222.222
- IPv4 secondary DNS server: 208.67.220.220


3. Test settings by novigating to the page http://www.internetbadguys.com/

Refer to OpenDNS guide for more details: https://support.opendns.com/hc/en-us/articles/228006047-Generalized-Router-Configuration-Instructions


Configure Parental control

1. Login as admin in http://192.168.1.1/html/advance.html#parent_control

2. Add new rule in Time rules:
 - Give a rule a name
 - Assign allowed time window
 - Check affected devices
