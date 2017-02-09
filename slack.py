import os
from slackclient import SlackClient
from datetime import datetime

SLACK_TOKEN = os.environ.get('SLACK_TEST_API_KEY')
GENERAL_CHANNEL_ID = "C3QD2RG93"
MARKETING_CHANNEL_ID = "C3Q80T00Z"
OUTREACH_CHANNEL_ID = "C3Q7ZKRED"
EXECUTIVE_CHANNEL_ID = "G3PL0TMA5"
PERSONAL_USER_ID = "U3QD2RBN1"

class SlackBot(object):
    def __init__(self, slack_token):
        self.slack_client = SlackClient(slack_token)
        # write a test function

    def test_auth(self):
        test = self.slack_client.api_call("api.test")
        if test and test['ok']:
            return True
        return False

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call.get('ok'):
            return channels_call['channels']
        return None

    def send_message(self, channel_id, message):
        """Takes user ids or channel ids, and then sends the given message
        throught the bot user. Will print to say if message succeeded"""
        if channel_id[0] == 'U':
            channel = self.slack_client.api_call("im.open", user=channel_id)['channel']['id']
        else:
            channel = channel_id
        ret = self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
            username='scg_bot',
            icon_emoji=':robot_face:')

        if ret['ok']:
            print "message sent succesfully at: %s" % datetime.now()
        else:
            print "message failed to send at: %s" % datetime.now()
            print "reason: %s" % ret['error']


if __name__ == '__main__':
    bot = SlackBot(SLACK_TOKEN)
    bot.send_message('D121', 'testing')
