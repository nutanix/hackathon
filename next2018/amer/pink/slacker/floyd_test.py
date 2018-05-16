import os
import time
import re
import paramiko
from slackclient import SlackClient
from contextlib import contextmanager


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
bricks = 0
# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
host = '10.21.47.107'
user = 'centos'
key = paramiko.RSAKey.from_private_key_file("/home/slacker/key.pem")
c = paramiko.SSHClient()
scale_out = "add"
scale_in = "tear"
reset = "rebuild"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Have you tried turning it off and back on again?"

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(scale_out):
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect( hostname = host, username = user, pkey = key )
	stdin , stdout, stderr = c.exec_command("kubectl get pods -l app=anotherbrick | grep -v NAME | wc -l")
	bricks = stdout.read()
        response = "There are currently *{}* bricks. How many bricks do you want?".format(bricks)
    elif command.startswith(scale_in):
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect( hostname = host, username = user, pkey = key )
	stdin , stdout, stderr = c.exec_command("kubectl get pods -l app=anotherbrick | grep -v NAME | wc -l")
	bricks = stdout.read()
        response = "There are currently *{}* bricks. How many bricks do you want?".format(bricks)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

