from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class BGGElementScraper:
    def __init__(self, username, password):
        self.baseUrl = "https://www.boardgamegeek.com" 
        self.browser = webdriver.Firefox()
        self.logIn(username, password)

    def logIn(self, username, password):
        try:
            self.browser.get(self.baseUrl + "/login")
            timeout = 5 # seconds
            myElem = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, "username")))
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

    def question(self, questionNumber):
        questionUrl = "/question/" + str(questionNumber)
        questionSelector = "a[href='" + questionUrl + "']"
        timeout = 5 # seconds

        try:
            self.browser.get(self.baseUrl + questionUrl)
            # wait for question to load
            questionElement = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, questionSelector)))
        except TimeoutException:
            print("could not load page for question " + str(questionNumber))
            raise

        return questionElement.text