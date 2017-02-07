import os
import time
from datetime import datetime
import atexit

from flask import Flask, request, Response
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import slack
import sheets

app = Flask(__name__)

POST_UPDATE_MESSAGE = False
UPDATE_MESSAGE_START_DATE = datetime(2017, 2, 5, 17, 0)
UPDATE_MESSAGE_UPDATE_INTERVAL = 1

# SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')


# @app.route('/slack', methods=['POST'])
# def inbound():
#     if request.form.get('token') == SLACK_WEBHOOK_SECRET:
#         channel = request.form.get('channel_name')
#         username = request.form.get('user_name')
#         text = request.form.get('text')
#         inbound_message = username + " in " + channel + " says: " + text
#         print inbound_message
#     return Response(), 200

def create_update_message():
    gs = sheets.OutreachSheet()
    return gs.create_daily_update_message()

def post_update_message():
    """Need to run tests on gs and bot before sending message"""
    bot = slack.SlackBot(slack.SLACK_TOKEN)
    message = create_update_message()
    sent = bot.send_channel_message(slack.GENERAL_CHANNEL_ID, message)
    if sent:
        print "message sent succesfully at: %s" % datetime.now()
    else:
        print "message failed to send at: %s" % datetime.now()

def send_user_update_message():
    bot = slack.SlackBot(slack.SLACK_TOKEN)
    gs = sheets.OutreachSheet()
    message = gs.get_individual_update_message(slack.PERSONAL_USER_ID)
    bot.send_channel_message(slack.EXECUTIVE_CHANNEL_ID, message)

if POST_UPDATE_MESSAGE:
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=post_update_message,
        trigger=IntervalTrigger(
            start_date=UPDATE_MESSAGE_START_DATE,
            days=UPDATE_MESSAGE_UPDATE_INTERVAL),
        id='printing_job',
        name='Posts the daily giving stats to the general channel',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

@app.route('/', methods=['GET'])
def test():
    return Response('It works!')

@app.route('/test/update-message/', methods=['GET'])
def test_giving_update():
    return Response(create_update_message())


if __name__ == "__main__":
    # app.run(debug=False)
    send_user_update_message()

