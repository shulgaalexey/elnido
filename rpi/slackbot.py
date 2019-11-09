import json
import time
import subprocess
import datetime
import socket
from slackclient import SlackClient

SLACK_API_TOKEN = None
ALLOWED_USER_NAMES = None
CUR_CHANNEL = None


def _get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _log(msg):
    print '%s: %s' % (_get_cur_time(),  msg)


def load_config():
    global SLACK_API_TOKEN
    global ALLOWED_USER_NAMES
    _log('Load config from config.json file')
    with open('config.json') as config_file:
        config_loaded = json.load(config_file)
        SLACK_API_TOKEN = config_loaded['slack_api_token']
        ALLOWED_USER_NAMES = config_loaded['allowed_user_names']
        _log('Successfully loaded config')


def connect():
    slack_client = SlackClient(SLACK_API_TOKEN)
    if not slack_client.rtm_connect():
        _log('Cannot connect to slack')
        exit(0)
    _log("Connected!")
    return slack_client


def get_allowed_user_ids(slack_client):
    user_list = slack_client.api_call("users.list")
    allowed_user_ids = []
    for user in user_list.get('members'):
        _log('user: ' +  user.get('name') + ' with id: ' + user.get('id'))
        if user.get('name') in ALLOWED_USER_NAMES:
            allowed_user_ids.append(user.get('id'))
            _log('    Added allowed user id: ' + user.get('id'))
    return allowed_user_ids


def post_message(slack_client, text, channel):
    if not channel or not text:
        _log('Did not send message: "%s" to channel: "%s"' % (text, channel))
        return
    slack_client.api_call("chat.postMessage",channel=channel,
        text=text, as_user=True)


def process_message(slack_client, msg):
    global CUR_CHANNEL
    if 'text' not in msg:
        return
    txt = msg['text']
    _log(txt)
    if 'channel' not in msg:
        return
    channel = msg['channel']
    CUR_CHANNEL = channel
    if txt.lower() == 'ping':
        _log(msg)
        post_message(slack_client, 'pong', channel)
    elif txt == 'status':
        ret = subprocess.Popen(['route', '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = ret.communicate()
        post_message(slack_client, '```%s```' % stdout, channel)
        if stderr:
            post_message(slack_client, 'ERROR\n```%s```' % stderr, channel)
    if txt.lower() == 'child inet on':
        post_message(slack_client, 'turning on child inet....', channel)
        time.sleep(1)
        post_message(slack_client, 'turning on child inet....DONE', channel)
    if txt.lower() == 'child inet off':
        post_message(slack_client, 'turning off child inet....', channel)
        time.sleep(1)
        post_message(slack_client, 'turning off child inet....DONE', channel)
    elif txt.lower() == 'help':
        post_message(slack_client,
                'Available commands:\n\tping\n\tstatus\n\tchild inet on\n\tchild inet off\n\thelp',
                channel)


try:
    load_config()
    slack_client = connect()
    allowed_user_ids = get_allowed_user_ids(slack_client)
    while True:
        try:
            for msg in slack_client.rtm_read():
                if msg['type'] != 'message'  and not "subtype" in msg:
                    continue
                if msg['user'] not in allowed_user_ids:
                    continue
                process_message(slack_client, msg)
        except socket.error as se:
            _log('Socket error, reconnect in 5 sec: ' + se)
            time.sleep(1)
            connect()
        except IOError as ex:
            _log('Cannot fetch messages: ' + ex)
        time.sleep(1)
except KeyboardInterrupt:
    _log('Terminated by operator. Sending farewell message to channel %s...' % CUR_CHANNEL)
    post_message(slack_client, 'Interrupted by the Operator', CUR_CHANNEL)
    time.sleep(2)
_log("Finished")
