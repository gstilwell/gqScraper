from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from time import sleep

import argparse

parser = argparse.ArgumentParser(description='Scrub GQ')
parser.add_argument('username', type=str, help='BGG username')
parser.add_argument('password', type=str, help='BGG user password')
args = parser.parse_args()

browser = webdriver.Firefox()
browser.get("https://www.boardgamegeek.com/login")
delay = 3 # seconds
try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "username")))

    usernameField = browser.find_element(By.ID, "username")
    passwordField = browser.find_element(By.ID, "password")
    submitButton = browser.find_element(By.CSS_SELECTOR, "input[name='B1']")

    usernameField.send_keys(args.username)
    passwordField.send_keys(args.password)
    submitButton.click()
except TimeoutException:
    print("Could not load login page")

for qNum in range(1,10):
    browser.get("https://www.boardgamegeek.com/question/" + str(qNum))
    try:
        questionSelector = "a[href='/question/" + str(qNum) + "']"
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, questionSelector)))

        questionElement = browser.find_element(By.CSS_SELECTOR, questionSelector)
        questionText = questionElement.text
    except TimeoutException:
        print("could not load page for question " + str(qNum))