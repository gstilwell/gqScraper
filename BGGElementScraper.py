import os
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class BGGElementScraper:
    def __init__(self, username, password):
        self.baseUrl = "https://www.boardgamegeek.com" 
        self.timeout = 5 # seconds
        self.browser = webdriver.Firefox()
        self.loadedPage = None

        self.logIn(username, password)

    def logIn(self, username, password):
        try:
            self.browser.get(self.baseUrl + "/login")
            myElem = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.ID, "username")))
        except TimeoutException:
            print("Could not load login page")
            raise

        try:
            usernameField = self.browser.find_element(By.ID, "username")
            passwordField = self.browser.find_element(By.ID, "password")
            submitButton = self.browser.find_element(By.CSS_SELECTOR, "input[name='B1']")
        except NoSuchElementException as e:
            print("Could not find login element")
            raise

        usernameField.send_keys(username)
        passwordField.send_keys(password)
        submitButton.click()

    def loadPage(self, url):
        try:
            self.browser.get(url)
        except TimeoutException:
            print("could not load page " + url)
            raise

        self.loadedPage = url
    
    # gets the indicated element(s) from the presently loaded page
    def element(self, selector):
        try:
            element = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            print("could not find element " + selector + " on page " + self.loadedPage)
            raise

        return element

    def validPath(self, path):
        return path.replace(":", "@@@COLON@@@").replace("*", "@@@ASTERISK@@@")

    def saveAvatar(self, username, avatarDir):
        profileUrl = "/user/" + username
        avatarSelector = 'img[alt="Avatar"]'

        self.loadPage(self.baseUrl + profileUrl)
        try:
            avatarElement = self.element(avatarSelector)
        except TimeoutException:
            noAvatarFilename = os.path.join(avatarDir, self.validPath(username) + ".noavatar")
            print(username + " doesn't have an avatar. creating empty file " + noAvatarFilename)
            open(noAvatarFilename, 'w').close()
            return

        avatarUrl = avatarElement.get_attribute("src")

        img_data = requests.get(avatarUrl).content
        filename = self.validPath(username) + ".jpg"
        avatarPath = os.path.join(avatarDir, filename)
        with open(avatarPath, 'wb') as outFile:
            outFile.write(img_data)
            outFile.close()
            print("saved " + username + "'s avatar to " + avatarPath)

    def question(self, questionNumber):
        questionUrl = "/question/" + str(questionNumber)
        questionSelector = "a[href='" + questionUrl + "']"

        self.loadPage(self.baseUrl + questionUrl)
        questionElement = self.element(questionSelector)

        return questionElement.text