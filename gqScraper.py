import argparse
import json
from time import sleep
import os.path

from BGGElementScraper import BGGElementScraper

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('username', type=str, help='BGG username')
parser.add_argument('password', type=str, help='BGG user password')
args = parser.parse_args()

scraper = BGGElementScraper(args.username, args.password)

usersFile = open('users.json', 'r')
usersObj = json.load(usersFile)
usersFile.close()

avatarDir = "avatars"
usernames = usersObj['rows']
usernames = [user[0] for user in usernames]

for username in usernames:
    validUsername = username.replace(":", "@@@COLON@@@").replace("*", "@@@ASTERISK@@@")
    noAvatarPath = os.path.join(avatarDir, validUsername + ".noavatar")
    avatarPath = os.path.join(avatarDir, validUsername + ".jpg")
    if os.path.exists(noAvatarPath) or os.path.exists(avatarPath):
        continue

    scraper.saveAvatar(username, avatarDir)
    sleep(5)