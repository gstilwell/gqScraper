import argparse
import json
from time import sleep

from BGGElementScraper import BGGElementScraper

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('username', type=str, help='BGG username')
parser.add_argument('password', type=str, help='BGG user password')
args = parser.parse_args()

scraper = BGGElementScraper(args.username, args.password)

usersFile = open('users.json', 'r')
usersObj = json.load(usersFile)
usersFile.close()

usernames = usersObj['rows']
usernames = [user[0] for user in usernames]

for username in usernames:
    scraper.saveAvatar(username, "avatars")
    sleep(5)