import os
from slackclient import SlackClient

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

    def send_channel_message(self, channel_id, message):
        ret = self.slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username='scg_bot',
            icon_emoji=':robot_face:'
        )
        return ret['ok']

    def send_direct_message(self, user_id, message):
        channel = self.slack_client.api_call("im.open", user=user_id)
        if channel['ok']:
            ret = self.slack_client.api_call(
                "chat.postMessage",
                as_user=True,
                channel=channel['channel']['id'],
                text=message,
                username='scg_bot',
                icon_emoji=':robot_face:'
            )
        return ret['ok']

if __name__ == '__main__':
    bot = SlackBot(SLACK_TOKEN)
    bot.send_direct_message('U3QD2RBN1', 'testing')
