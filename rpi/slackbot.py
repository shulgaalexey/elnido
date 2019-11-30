import json
import time
import subprocess
import threading
import datetime
import socket
from timeit import Timer
#from r7insight import R7InsightHandler
#import logging
from slackclient import SlackClient
from slackclient.server import SlackConnectionError


SLACK_API_TOKEN = None
ALLOWED_USER_NAMES = []
CONTROLLED_IPS = []
CUR_CHANNEL = None
R7_LOG_TOKEN = None
DNS_SERVICE = 'pihole-FTL'


def _get_cur_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _log(msg):
    timed_msg = '%s: %s' % (_get_cur_time(),  msg)
    print timed_msg
    echo_file_cmd = 'echo "%s" >> /home/pi/slackbot.log' % timed_msg
    subprocess.Popen(echo_file_cmd, shell=True)
    log_cmd = 'echo %s %s | nc eu.data.logs.insight.rapid7.com 10000' % (R7_LOG_TOKEN, msg)
    subprocess.Popen(log_cmd, shell=True)


def load_config():
    global SLACK_API_TOKEN
    global ALLOWED_USER_NAMES
    global R7_LOG_TOKEN
    global CONTROLLED_IPS
    _log('Load config from config.json file')
    with open('/home/pi/.bot.config.json') as config_file:
        config_loaded = json.load(config_file)
        SLACK_API_TOKEN = config_loaded['slack_api_token']
        ALLOWED_USER_NAMES = config_loaded['allowed_user_names']
        CONTROLLED_IPS = config_loaded['controlled_ips']
        print 'Controlled IPs', CONTROLLED_IPS
        R7_LOG_TOKEN = config_loaded['r7_log_token']


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
        _log('user: %s with id: %s' %  (user.get('name'), user.get('id')))
        if user.get('name') in ALLOWED_USER_NAMES:
            allowed_user_ids.append(user.get('id'))
            _log('    Added allowed user id: %s' % user.get('id'))
    return allowed_user_ids


def post_message(slack_client, text, channel):
    if not channel or not text:
        _log('Did not send message: "%s" to channel: "%s"' % (text, channel))
        return
    slack_client.api_call("chat.postMessage",channel=channel,
        text=text, as_user=True)


class Command(object):
    def __init__(self, cmd, timeout):
        self.cmd = cmd
        self.process = None
        self.timeout = timeout
        self.stdout = None
        self.stderr = None

    def run(self):
        print 'Run command: %s' % self.cmd
        print 'Timeout: %s' % self.timeout
        def target():
            self.process = subprocess.Popen(self.cmd.split(),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.stdout, self.stderr = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()


def run_command(cmd_str, channel):
    command = Command(cmd_str, timeout=15)
    command.run()
    if command.stdout:
        post_message(slack_client, '```%s```' % command.stdout, channel)
    if command.stderr:
        post_message(slack_client, 'ERROR\n```%s```' % command.stderr, channel)


def check_ip_reachable(ip):
    command = Command('ping %s' % ip, timeout=5)
    command.run()
    return command.stdout and 'bytes from' in command.stdout


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
        for ip in  CONTROLLED_IPS:
            post_message(slack_client, 'checking %s....' % ip['alias'], channel)
            check = check_ip_reachable(ip['ip'])
            reachable = 'reachable' if check else 'not reachable'
            post_message(slack_client, '%s' % reachable, channel)
    elif txt.lower() == 'child inet on':
        for ip in  CONTROLLED_IPS:
            post_message(slack_client, 'turning on child inet for %s....' % ip['alias'], channel)
            run_command('sudo iptables -D INPUT -s %s -j DROP' % ip['ip'], channel)
            post_message(slack_client, 'turning on child inet for %s....DONE' % ip['alias'], channel)
    elif txt.lower() == 'child inet off':
        for ip in  CONTROLLED_IPS:
            post_message(slack_client, 'turning off child inet for %s....' % ip['alias'], channel)
            run_command('sudo iptables -A INPUT -s %s -j DROP' % ip['ip'], channel)
            post_message(slack_client, 'turning off child inet for %s....DONE' % ip['alias'], channel)
    elif txt.lower() == 'stop':
        post_message(slack_client, 'Bye bye master', channel)
        _log('Stop command')
        exit(0)
    elif txt.lower() == 'help':
        post_message(slack_client,
                'Available commands:\n\tping\n\tstatus\n\tchild inet on\n\tchild inet off\n\tstop\n\thelp',
                channel)
    else:
        _log(msg)
        post_message(slack_client, '```%s```\nU mad?' % msg, channel)



slack_client = None
iter = 0
try:
    load_config()

    #LOG = logging.getLogger('r7insight')
    #LOG.setLevel(logging.INFO)
    #LOG_HANDLER = R7InsightHandler(R7_LOG_TOKEN, 'eu')
    #LOG.addHandler(LOG_HANDLER)


    slack_client = connect()
    allowed_user_ids = get_allowed_user_ids(slack_client)
    while True:
        iter += 1
        if iter > (5 * 60):
            iter = 0
            _log("Heartbeat")
        try:
            for msg in slack_client.rtm_read():
                if msg['type'] != 'message'  and not "subtype" in msg:
                    continue
                if msg['user'] not in allowed_user_ids:
                    continue
                process_message(slack_client, msg)
        except SlackConnectionError as sce:
            _log('Slack connect socket error, reconnect in 15 sec, reason: "%s"' % sce)
            time.sleep(15)
            slack_client = connect()
            if slack_client:
                post_message(slack_client, 'Reconnect after exception\n```%s```' % sce, CUR_CHANNEL)
                time.sleep(2)
            else:
                _log('Unable to connect to slack')
        except socket.error as se:
            _log('Socket error, reconnect in 15 sec, reason: "%s"' % se)
            time.sleep(15)
            slack_client = connect()
            if slack_client:
                post_message(slack_client, 'Reconnect after exception\n```%s```' % se, CUR_CHANNEL)
                time.sleep(2)
            else:
                _log('Unable to connect to slack')
        except IOError as ex:
            _log('Cannot fetch messages: %s' % ex)
            post_message(slack_client, 'Exception\n```%s```' % ex, CUR_CHANNEL)
            time.sleep(2)
        time.sleep(1)
except KeyboardInterrupt:
    _log('Terminated by operator. Sending farewell message to channel %s...' % CUR_CHANNEL)
    post_message(slack_client, 'Interrupted by the Operator', CUR_CHANNEL)
    time.sleep(2)
_log("Finished")
