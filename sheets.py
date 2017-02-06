import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds']

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_CREDENTIALS = os.path.join(THIS_FOLDER, 'scgbot-5baffeec478c.json')
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(JSON_CREDENTIALS, SCOPE)

GC = gspread.authorize(CREDENTIALS)

TEST_CELL = 'B3'
TOTAL_DONATIONS_CELL = 'B5'
TOTAL_DONATION_GOAL_CELL = 'B6'

FIRST_PLACE_ROW = 10
LEADERBOARD_NAME_COL = 'B'
LEADERBOARD_COUNT_COL = 'C'

NEXT_CHALLENGE_NAME = 'B14'
NEXT_CHALLENGE_COUNT = 'B15'
NEXT_CHALLENGE_DATE = 'B16'

class OutreachSheet(object):
    """Object containing worksheets from outreach document"""
    def __init__(self):
        self.bot_sheet = GC.open("2017 Committee Outreach").worksheet("bot_sheet")

    def test_bot_sheet(self):
        test_cell = self.bot_sheet.acell(TEST_CELL)
        if test_cell.value == 'test':
            print 'bot_sheet is working'
        else:
            print 'Something is wrong with bot_sheet'
            print 'B3 contained: %s' % test_cell.value

    def get_total_donations(self):
        return int(self.bot_sheet.acell(TOTAL_DONATIONS_CELL).value)

    def get_total_donations_goal(self):
        return int(self.bot_sheet.acell(TOTAL_DONATION_GOAL_CELL).value)

    def create_daily_update_message(self):
        donations = self.get_total_donations()
        total_goal = self.get_total_donations_goal()
        percentage = round((float(donations) / total_goal) * 100, 2)

        message = ":moneybag: *This is your daily giving update* :moneybag:\n\n\n"
        message += ":bar_chart: Total Current Donations: %d\n" % donations
        message += ":chart_with_upwards_trend: At %0.2f%% of %d donor goal\n" % (percentage, total_goal)

        challenge = self.get_next_challenge()
        message += ":calendar: Next Challenge: %s - %s\n" % (challenge['name'], challenge['date'])
        message += ":squirrel: %d donations left to go\n\n\n" % (challenge['count'] - donations)

        leaderboard = self.get_leaderboard()
        message += ":sports_medal: Current Leaderboard :sports_medal:\n"
        for p in zip(leaderboard, [':one:', ':two:', ':three:']):
            message += "%s %s - %s\n" % (p[1], p[0][0], p[0][1])
        return message

    def user_id_to_name(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        user_name_cell = self.bot_sheet.cell(user_id_cell.row, user_id_cell.col - 1)
        return user_name_cell.value

    def get_user_total_donations(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        user_total_donation_cell = self.bot_sheet.cell(user_id_cell.row, user_id_cell.col + 1)
        return int(user_total_donation_cell.value)

    def get_user_weeks_donations(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        user_week_donation_cell = self.bot_sheet.cell(user_id_cell.row, user_id_cell.col + 3)

    def get_next_challenge(self):
        challenge = {}
        challenge['name'] = self.bot_sheet.acell(NEXT_CHALLENGE_NAME).value
        challenge['date'] = self.bot_sheet.acell(NEXT_CHALLENGE_DATE).value
        challenge['count'] = int(self.bot_sheet.acell(NEXT_CHALLENGE_COUNT).value)
        return challenge

    def get_leaderboard(self):
        leaderboard = []
        for i in [0, 1, 2]:
            name = self.bot_sheet.acell(LEADERBOARD_NAME_COL + str(FIRST_PLACE_ROW + i)).value
            count = self.bot_sheet.acell(LEADERBOARD_COUNT_COL + str(FIRST_PLACE_ROW + i)).value
            leaderboard.append((name, count))
        return leaderboard


    # def report_error(self, message):


    # def get_user_donations_this_week(self, user):





if __name__ == "__main__":
    outreach = OutreachSheet()
    print outreach.create_daily_update_message()
