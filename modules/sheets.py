import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds']

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_CREDENTIALS = os.path.join(THIS_FOLDER, 'scgbot-5baffeec478c.json')
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(JSON_CREDENTIALS, SCOPE)

TEST_CELL = 'B3'
TOTAL_DONATIONS_CELL = 'B5'
TOTAL_DONATION_GOAL_CELL = 'B6'
LAUREN_MESSAGE_CELL = 'B18'

FIRST_PLACE_ROW = 10
LEADERBOARD_NAME_COL = 'B'
LEADERBOARD_COUNT_COL = 'C'

NEXT_CHALLENGE_NAME = 'B14'
NEXT_CHALLENGE_COUNT = 'B15'
NEXT_CHALLENGE_DATE = 'B16'

# Personal infos
USER_INFO_RANGE = 'E4:I39'
USER_INFO_ROW_LEN = 5  # From E to I

# Sign-up constants
GIFT_COL = 'H'

class OutreachSheet(object):
    """Object containing worksheets from outreach document"""
    def __init__(self):
        GC = gspread.authorize(CREDENTIALS)
        self.bot_sheet = GC.open("2017 Committee Outreach").worksheet("bot_sheet")

    def get_daily_update_message(self):
        donations = int(self.bot_sheet.acell(TOTAL_DONATIONS_CELL).value)
        total_goal = int(self.bot_sheet.acell(TOTAL_DONATION_GOAL_CELL).value)
        percentage = round((float(donations) / total_goal) * 100, 2)

        message = ":moneybag: *This is your daily giving update* :moneybag:\n\n\n"
        message += ":bar_chart: Total Current Donations: %d\n" % donations
        message += ":chart_with_upwards_trend: "
        message += "At %0.2f%% of %d donor goal\n" % (percentage, total_goal)

        try:
            challenge = self.get_next_challenge()
            message += ":calendar: Next Challenge: %s - " % challenge['name']
            message += "%d donations\n" % challenge['count']
            message += ":squirrel: %s days & " % (challenge['date'] - datetime.now()).days
            message += "%d donations left to go\n\n\n" % (challenge['count'] - donations)
        except ValueError:
            message += '\n\n'

        leaderboard = self.get_leaderboard()
        message += ":sports_medal: Current Leaderboard :sports_medal:\n"
        for p in zip(leaderboard, [':one:', ':two:', ':three:']):
            message += "%s %s - %s\n" % (p[1], p[0][0], p[0][1])
        return message

    def get_personal_update_messages(self):
        members = self.get_all_members()
        messages = []
        lauren_message = self.bot_sheet.acell(LAUREN_MESSAGE_CELL).value
        self.bot_sheet.update_acell(LAUREN_MESSAGE_CELL, '')
        for member in members:
            text = ":moneybag: *%s here is your personal update* :moneybag:\n\n" % member['name']
            text += ":bar_chart: Your donations this fortnight: %s\n" % member['fortnight']
            text += ":chart_with_upwards_trend: Your total donations: %s\n\n" % member['total']
            if lauren_message:
                text += ":spiral_note_pad: %s" % lauren_message
            messages.append({'slack_id': member['slack_id'], 'text': text})
        return messages

    def get_next_challenge(self):
        challenge = {}
        challenge['name'] = self.bot_sheet.acell(NEXT_CHALLENGE_NAME).value
        date = self.bot_sheet.acell(NEXT_CHALLENGE_DATE).value
        challenge['date'] = datetime.strptime(date, "%Y-%m-%d")
        challenge['count'] = int(self.bot_sheet.acell(NEXT_CHALLENGE_COUNT).value)

        if challenge['date'] < datetime.now():
            raise ValueError
        return challenge

    def get_leaderboard(self):
        leaderboard = []
        for i in [0, 1, 2]:
            name = self.bot_sheet.acell(LEADERBOARD_NAME_COL + str(FIRST_PLACE_ROW + i)).value
            count = self.bot_sheet.acell(LEADERBOARD_COUNT_COL + str(FIRST_PLACE_ROW + i)).value
            leaderboard.append((name, count))
        return leaderboard

    def get_all_members(self):
        members = []
        cells = self.bot_sheet.range("E4:I39")
        rows = [cells[i:i+USER_INFO_ROW_LEN] for i in range(0, len(cells), USER_INFO_ROW_LEN)]
        for row in rows:
            member = {
                'name': row[0].value,
                'slack_id': row[1].value,
                'total': row[2].value,
                'fortnight': row[4].value
            }
            if member['slack_id']:
                members.append(member)
        return members



class SignUpSheet(object):

    def __init__(self):
        GC = gspread.authorize(CREDENTIALS)
        self.sign_up_sheet = GC.open("2017 Committee Outreach").worksheet("Sign-Up Sheet")
        self.cells = self.sign_up_sheet._fetch_cells()  # Force call on private method

    def local_find_row(self, string):
        try:
            match = next(cell for cell in self.cells if cell.value == string)
            return match.row
        except StopIteration:
            raise gspread.exceptions.CellNotFound(string)

    def local_findall_rows(self, string):
        return [cell.row for cell in self.cells if cell.value == string]

    def find_gift_cell(self, first_name, last_name, email):
        try:
            if not email:
                raise gspread.exceptions.CellNotFound
            row = self.local_find_row(email)

        except gspread.exceptions.CellNotFound:
            lname_rows = self.local_findall_rows(last_name)
            if len(lname_rows) == 1:  # check if unique last name is found
                row = lname_rows[0]
            else:
                fname_rows = self.local_findall_rows(first_name)
                if len(fname_rows) == 1:  # check if unique first name is found
                    row = fname_rows[0]
                else:
                    matched_rows = set(fname_rows) & set(lname_rows)
                    if len(matched_rows) == 1:  # check if unique combination is found
                        row = matched_rows.pop()
                    else:
                        raise gspread.exceptions.CellNotFound  # raise exception if no unique match

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
        try:
            gift_cell_name = self.find_gift_cell(first_name, last_name, email)
            if self.sign_up_sheet.acell(gift_cell_name).value != 'Gave':
                self.sign_up_sheet.update_acell(gift_cell_name, 'Gave')
            return True
        except gspread.exceptions.CellNotFound:
            return False
        except gspread.exceptions.UpdateCellError:
            return False


if __name__ == "__main__":
    outreach = OutreachSheet()
    print outreach.get_personal_update_messages()[0]['text']
    # print outreach.get_daily_update_message()
    # signup = SignUpSheet()
    # print 'signup initialized'
