import argparse
from time import sleep

from BGGElementScraper import BGGElementScraper

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('username', type=str, help='BGG username')
parser.add_argument('password', type=str, help='BGG user password')
args = parser.parse_args()

scraper = BGGElementScraper(args.username, args.password)

for username in ["imyourskribe", "Chris Sjoholm", "xman@pcisys.net"]:
    scraper.saveAvatar(username, "avatars")
    sleep(5)

question = scraper.question(1)
print(question)