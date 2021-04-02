import argparse
from time import sleep

from BGGElementScraper import BGGElementScraper

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('username', type=str, help='BGG username')
parser.add_argument('password', type=str, help='BGG user password')
args = parser.parse_args()

scraper = BGGElementScraper(args.username, args.password)

for username in ["imyourskribe", "Chris Sjoholm", "xman@pcisys.net"]:
    avatar = scraper.saveAvatar(username)
    print(avatar)
    sleep(5)