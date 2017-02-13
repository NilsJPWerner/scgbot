from modules import slack, sheets

def create_update_message():
    gs = sheets.OutreachSheet()
    return gs.create_daily_update_message()

def post_update_message():
    """Need to run tests on gs and bot before sending message"""
    bot = slack.SlackBot(slack.SLACK_TOKEN)
    message = create_update_message()
    bot.send_message(slack.GENERAL_CHANNEL_ID, message)

if __name__ == "__main__":
    post_update_message()
