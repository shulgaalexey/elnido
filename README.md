# elnido
Secure home network

![High level view](elnido.svg)

## Bot commands

| Command       | Response      | Description |
| ------------- | ------------- | ----------- |
| ping          | pong          | Techno check |
| status        | pihole status; nmap report, network device ping | Get current network status |
| child inet on | confirmation for each of controlled device | Turn on the inernet on controlled devies |
| child inet off | confirmation for each of controlled device | Turn off the inernet on controlled devies |
| net           | list of device IPs | Get the list of all registered network devices, both controlled on viewed |
| admin         | URL          | Get admin page link |
| stop          |              | Kill the bot |
| help          | list of command names | Get the list of available commands |

## Feature request

1. [ ] Turn inet on/off on schedule
