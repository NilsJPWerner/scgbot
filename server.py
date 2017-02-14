# import os
# import time
from datetime import datetime
# import atexit

from flask import Flask, request, Response, render_template
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger

from modules import sheets, excel

app = Flask(__name__)

POST_UPDATE_MESSAGE = False
UPDATE_MESSAGE_START_DATE = datetime(2017, 2, 5, 17, 0)
UPDATE_MESSAGE_UPDATE_INTERVAL = 1


def create_update_message():
    gs = sheets.OutreachSheet()
    return gs.create_daily_update_message()

# def post_update_message():
#     """Need to run tests on gs and bot before sending message"""
#     bot = slack.SlackBot(slack.SLACK_TOKEN)
#     message = create_update_message()
#     sent = bot.send_message(slack.GENERAL_CHANNEL_ID, message)
#     if sent:
#         print "message sent succesfully at: %s" % datetime.now()
#     else:
#         print "message failed to send at: %s" % datetime.now()

# def send_user_update_message():
#     bot = slack.SlackBot(slack.SLACK_TOKEN)
#     gs = sheets.OutreachSheet()
#     message = gs.get_individual_update_message(slack.PERSONAL_USER_ID)
#     bot.send_message(slack.EXECUTIVE_CHANNEL_ID, message)

# if POST_UPDATE_MESSAGE:
#     scheduler = BackgroundScheduler()
#     scheduler.start()
#     scheduler.add_job(
#         func=post_update_message,
#         trigger=IntervalTrigger(
#             start_date=UPDATE_MESSAGE_START_DATE,
#             days=UPDATE_MESSAGE_UPDATE_INTERVAL),
#         id='printing_job',
#         name='Posts the daily giving stats to the general channel',
#         replace_existing=True)
#     # Shut down the scheduler when exiting the app
#     atexit.register(lambda: scheduler.shutdown())

@app.route('/', methods=['GET'])
def test():
    return Response('It works!')

@app.route('/test/update-message/', methods=['GET'])
def test_giving_update():
    return Response(create_update_message())


@app.route('/upload', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        start_time = datetime.now()

        f = request.files['file']
        doc = excel.giving_document(f)
        if doc.check_sheet_type() == 'OTHER':
            return Response("That is not a supported file")
        donors = doc.get_donors()
        print "Time to get donors from excel: %s" % str(datetime.now() - start_time)
        start_time = datetime.now()
        gs = sheets.SignUpSheet()
        print "Time to initialize sign-up sheet: %s" % str(datetime.now() - start_time)
        start_time = datetime.now()
        worked, failed = [], []
        for donor in donors:
            success = gs.mark_person_as_donated(donor['fname'], donor['lname'], donor['email'])
            if success:
                worked.append(donor)
            else:
                failed.append(donor)

        print "Time to fetch and update cells: %s" % str(datetime.now() - start_time)
        return render_template('excel_upload.html', worked=worked, failed=failed)
    else:
        return render_template('excel_upload.html')


if __name__ == "__main__":
    app.run(debug=True)
