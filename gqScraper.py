import argparse
import json
from time import sleep
import os.path

from BGGElementScraper import BGGElementScraper
from GQDB import GQDB

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('bgg_username', type=str, help='BGG username')
parser.add_argument('bgg_password', type=str, help='BGG user password')
parser.add_argument('db_name', type=str, help='db name')
parser.add_argument('db_host', type=str, help='db hostname')
parser.add_argument('db_port', type=str, help='db port')
parser.add_argument('db_username', type=str, help='db username')
parser.add_argument('db_password', type=str, help='db password')
args = parser.parse_args()

scraper = BGGElementScraper(args.bgg_username, args.bgg_password)
db = GQDB(args.db_name, args.db_host, args.db_port, args.db_username, args.db_password)

#question = {
#    "id": 211919,
#    "text": "test question?",
#    "thumbs": 6,
#    "gold": "100.0",
#    "user_id": 103374,
#    "date": "2005-04-28 15:06:26"
#}
#db.write_question(question)
#quit()

#question = scraper.question(213258)
#db.write_question(question)

while True:
    lastSavedId = int(db.most_recent_question_id_saved())
    lastPostedId = int(scraper.latestPostedQuestionId())

    while lastPostedId > lastSavedId:
        nextQuestionToSave = lastSavedId + 1

        # timestamp is not on the question's page, so we have to scrape it explicitly and stick it in our qDict
        timestamp = scraper.timestampOfRecentQuestion(nextQuestionToSave)
        question = scraper.question(nextQuestionToSave)
        question["date"] = timestamp
        db.write_question(question)
        print(question)

        lastSavedId = nextQuestionToSave
        sleep(5)

    sleep(5)

#usersFile = open('users.json', 'r')
#usersObj = json.load(usersFile)
#usersFile.close()
#
#avatarDir = "avatars"
#usernames = usersObj['rows']
#usernames = [user[0] for user in usernames]
#
#while True:


#for username in usernames:
#    validUsername = username.replace(":", "@@@COLON@@@").replace("*", "@@@ASTERISK@@@")
#    noAvatarPath = os.path.join(avatarDir, validUsername + ".noavatar")
#    avatarPath = os.path.join(avatarDir, validUsername + ".jpg")
#    if os.path.exists(noAvatarPath) or os.path.exists(avatarPath):
#        continue
#
#    scraper.saveAvatar(username, avatarDir)
#    sleep(5)