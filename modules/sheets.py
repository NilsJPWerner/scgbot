import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds']

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_CREDENTIALS = os.path.join(THIS_FOLDER, 'scgbot-5baffeec478c.json')
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(JSON_CREDENTIALS, SCOPE)

TEST_CELL = 'B3'
TOTAL_DONATIONS_CELL = 'B5'
TOTAL_DONATION_GOAL_CELL = 'B6'

FIRST_PLACE_ROW = 10
LEADERBOARD_NAME_COL = 'B'
LEADERBOARD_COUNT_COL = 'C'

NEXT_CHALLENGE_NAME = 'B14'
NEXT_CHALLENGE_COUNT = 'B15'
NEXT_CHALLENGE_DATE = 'B16'

GIFT_COL = 'H'

class OutreachSheet(object):
    """Object containing worksheets from outreach document"""
    def __init__(self):
        GC = gspread.authorize(CREDENTIALS)
        self.bot_sheet = GC.open("2017 Committee Outreach").worksheet("bot_sheet")

    def test_bot_sheet(self):
        test_cell = self.bot_sheet.acell(TEST_CELL)
        if test_cell.value == 'test':
            print 'bot_sheet is working'
        else:
            print 'Something is wrong with bot_sheet'
            print 'B3 contained: %s' % test_cell.value

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

    def get_individual_update_message(self, user_id):
        total_donations = self.get_user_donations_this_weeks(user_id)
        weeks_donations = self.get_user_donations_this_weeks(user_id)
        real_name = self.get_user_real_name(user_id)

        message = ":moneybag: *%s here is your personal update* :moneybag:\n\n" % real_name
        message += ":bar_chart: Your donations this week: %s\n" % weeks_donations
        message += ":chart_with_upwards_trend: Your total donations: %s\n" % total_donations
        return message

    def get_total_donations(self):
        return int(self.bot_sheet.acell(TOTAL_DONATIONS_CELL).value)

    def get_total_donations_goal(self):
        return int(self.bot_sheet.acell(TOTAL_DONATION_GOAL_CELL).value)

    def user_id_to_name(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        user_name_cell = self.bot_sheet.cell(user_id_cell.row, user_id_cell.col - 1)
        return user_name_cell.value

    def get_user_total_donations(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        user_total_donation_cell = self.bot_sheet.cell(user_id_cell.row, user_id_cell.col + 1)
        return int(user_total_donation_cell.value)

    def get_user_donations_this_weeks(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        return self.bot_sheet.cell(user_id_cell.row, user_id_cell.col + 3).value

    def get_user_real_name(self, user_id):
        user_id_cell = self.bot_sheet.find(user_id)
        return self.bot_sheet.cell(user_id_cell.row, user_id_cell.col - 1).value

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


class SignUpSheet(object):

    def __init__(self):
        GC = gspread.authorize(CREDENTIALS)
        self.sign_up_sheet = GC.open("2017 Committee Outreach").worksheet("Sign-Up Sheet")

    def find_gift_cell(self, first_name, last_name, email):
        try:
            email_cell = self.sign_up_sheet.find(email)
            row = email_cell.row

        except gspread.exceptions.CellNotFound:
            fname_rows = [cell.row for cell in self.sign_up_sheet.findall(first_name)]
            lname_rows = [cell.row for cell in self.sign_up_sheet.findall(last_name)]
            matched_rows = set(fname_rows) & set(lname_rows)
            if len(matched_rows) != 1:
                return False
            row = matched_rows.pop()

        return GIFT_COL + str(row)

    def mark_person_as_donated(self, first_name, last_name, email):
        """Marks person as donated on signup sheet

        First tries to find the person through the email given. If not
        found, will try to find person through first and last name

        Args:
            first_name  (str): The first name of the person
            last_name   (str): The last name of the person
            email       (str): The email of the person

        Returns:
            (bool): Whether the cell was succesfully updated
        """
        gift_cell_name = self.find_gift_cell(first_name, last_name, email)

        try:
            if self.sign_up_sheet.acell(gift_cell_name).value != 'Gave':
                self.sign_up_sheet.update_acell(gift_cell_name, 'Gave')
            return True
        except gspread.exceptions.UpdateCellError:
            return False


    # def mark_people_as_donated(self, people):
    #     """Marks list of people as donated on sign up sheet

    #     Batch version of mark_person_as_donated that bundles updates as one
    #     api request for speed purposes. Will first attempt to use email key,
    #     then first and last name

    #     Args:
    #         people (list): A list of dicts of people's info with keys:
    #             first_name  (str): The first name of the person
    #             last_name   (str): The last name of the person
    #             email       (str): The email of the person

    #     Returns:
    #         A dict with list of people that were succesfully marked as donated,
    #         and another list for those who could not be found in the sheet.

    #         {
    #             'success': [{'email': (str), 'first_name': (str),'last_name': (str)}],
    #             'failed': [{'email': (str), 'first_name': (str),'last_name': (str)}]
    #         }

    #     Raises:
    #     """
    #     cell_list = []
    #     for person in people:
    #         pass






if __name__ == "__main__":
    # outreach = OutreachSheet()
    # print outreach.get_individual_update_message("U3QD2RBN1")
    signup = SignUpSheet()
    print "SignUpSheet initialized"
    # print signup.mark_person_as_donated("Nils", "Werner", "")
    print signup.find_gift_cell("", "", "acevedoj@uchicago.edu")

