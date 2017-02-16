from modules import slack, sheets


def post_update_message():
    """Need to run tests on gs and bot before sending message"""
    bot = slack.SlackBot(slack.SLACK_TOKEN)

    gs = sheets.OutreachSheet()
    # update = gs.get_daily_update_message()
    # bot.send_message(slack.GENERAL_CHANNEL_ID, update)

    for message in gs.get_personal_update_messages():
        bot.send_message(message['slack_id'], message['text'])

if __name__ == "__main__":
    post_update_message()
