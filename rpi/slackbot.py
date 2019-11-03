import json
import time
import subprocess
from slackclient import SlackClient

# Slack API Token
slack_client = SlackClient("SLACK_API_TOKEN")

user_list = slack_client.api_call("users.list")
allowed_user_ids = []
for user in user_list.get('members'):
    print 'user:', user.get('name'), 'with id:', user.get('id')
    if user.get('name') in ['user1', 'user2']:
        allowed_user_ids.append(user.get('id'))
        print '    Added allowed user id:', user.get('id')

if not slack_client.rtm_connect():
    print 'Cannot connect to slack'
    exit(0)

print ("Connected!")
while True:
    for msg in slack_client.rtm_read():
        if msg['type'] != 'message'  and not "subtype" in msg:
            break
        if msg['user'] not in allowed_user_ids:
            break

        txt = msg['text']
        print txt
        if txt.lower() == 'ping':
            print msg
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='pong', as_user=True)
        elif txt == 'status':
            ret = subprocess.Popen(['route', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = ret.communicate()
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='```%s```' % stdout, as_user=True)
            if stderr:
                slack_client.api_call("chat.postMessage",channel=msg['channel'],
                    text='ERROR\n```%s```' % stderr, as_user=True)
        if txt.lower() == 'child inet on':
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='turning on child inet....', as_user=True)
            time.sleep(1)
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='turning on child inet....DONE', as_user=True)
        if txt.lower() == 'child inet off':
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='turning off child inet....', as_user=True)
            time.sleep(1)
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='turning off child inet....DONE', as_user=True)
        elif txt.lower() == 'help':
            slack_client.api_call("chat.postMessage",channel=msg['channel'],
                text='Available commands:\n\tping\n\tstatus\n\tchild inet on\n\tchild inet off\n\thelp',
                as_user=True)

    time.sleep(1)
