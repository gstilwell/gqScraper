import os
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class DeletedQuestion(Exception):
    pass

class BGGElementScraper:
    def __init__(self, username, password):
        self.baseUrl = "https://www.boardgamegeek.com" 
        self.recentQuestionsPage = "https://www.boardgamegeek.com/questions/recent"
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
        # we never want to hammer the server too quickly. if we sleep here, we don't have to keep track
        # elsewhere of how long it has been since we loaded a page
        sleep(5)
        try:
            self.browser.get(url)
        except TimeoutException:
            print("could not load page " + url)
            raise

        self.loadedPage = url
    
    # gets the first match for the indicated element from the presently loaded page
    def element(self, selector):
        try:
            element = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            print("could not find element " + selector + " on page " + self.loadedPage)
            raise

        return element
    
    def subElement(self, element, subselector):
        try:
            subElement = WebDriverWait(element, self.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, subselector)))
        except TimeoutException:
            print("could not find element " + subselector + " on page " + self.loadedPage)
            raise

        return subElement

    # gets all matches for the indicated element from the presently loaded page
    def elements(self, selector):
        try:
            elements = self.browser.find_elements_by_css_selector(selector)
        except:
            print("could not find elements " + selector + " on page " + self.loadedPage)
            raise

        return elements
    
    def validPath(self, path):
        return path.replace(":", "@@@COLON@@@").replace("*", "@@@ASTERISK@@@")

    def latestPostedQuestionId(self):
        self.loadPage(self.recentQuestionsPage)
        questionTableSelector = "table.forum_table"
        questionSelector = "a[href*='/question/']"
        table = self.element(questionTableSelector)
        question = self.subElement(table, questionSelector)
        question_url = question.get_attribute("href")
        question_id = question_url.split("/")[-1]
        return question_id

    # loads the recent questions page and pulls the timestamp from the indicated question
    # this assumes the question is on the recent questions page still
    # this shouldn't be a problem as long as this is only used while probing the recent questions page for new questions
    # and as long as there aren't more than 50 questions asked within the span of a few seconds. I find this unlikely
    # (and it's far from catastrophic if the situation does pop up)
    #
    # the traversal up and down the parent/children in the table is inane, but it's the most straightforward way to find the date
    # given that there are no labels on most elements on the GQ pages
    def timestampOfRecentQuestion(self, id):
        if self.loadedPage != self.recentQuestionsPage:
            self.loadPage(self.recentQuestionsPage)
        questionSelector = "a[href='/question/{id}']".format(id = id)
        try:
            question = self.element(questionSelector)
        except TimeoutException:
            return None
        parentRow = question.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')
        dateCell = self.subElement(parentRow, "td:nth-of-type(4)")
        dateDiv = self.subElement(dateCell, "div:nth-of-type(2)")
        return dateDiv.text

    def recentAnswers(self):
        self.loadPage("https://www.boardgamegeek.com/answers/recent")
        answerBlockSelector = ".forum_table"
        answerBlocks = self.elements(answerBlockSelector)
        answers = []

        for block in answerBlocks:
            answers.append(self.answerBlockToAnswerDict(block))

        return answers

    def answerBlockToAnswerDict(self, block):
        avatarBlock = self.subElement(block, ".avatarblock")
        questionLink = self.subElement(block, "a[href*='/question/']")
        answerElement = self.subElement(questionLink.find_element_by_xpath('..'), "div")
        dateContainer = self.subElement(block, ".sf")
        thumbElement = self.subElement(block, "a[aria-label='Recommendations and tip info']")

        username = self.subElement(avatarBlock, "a[href*='/user/']").get_attribute("href").split("/")[-1]
        text = answerElement.text.split("A: ")[-1]
        qid = int(questionLink.get_attribute("href").split("/")[-1])
        thumbs = None if thumbElement.text == '' else int(thumbElement.text)
        date = dateContainer.text.split("Answered on ")[-1]
        # gg answer tip display is broken. just force None
        gold = None

        return {
            "username": username,
            "text": text,
            "question_id": qid,
            "thumbs": thumbs,
            "date": date,
            "gold": gold,
        }

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

    def question_text(self, questionUrl):
        questionSelector = "a[href='" + questionUrl + "']"
        try:
            questionElement = self.element(questionSelector)
            return questionElement.text
        except TimeoutException:
            # question was deleted
            raise DeletedQuestion

    def question_asker(self):
        askerSelector = ".username > a"
        askerElement = self.element(askerSelector)
        return askerElement.text

    def question_thumbs(self):
        thumbsSelector = ".recsbig > a[aria-label=\"Recommendations and tip info\"]"
        thumbsElement = self.element(thumbsSelector)
        thumbs = thumbsElement.text

        # it's a little annoying to have to do this, but the "no thumbs" case is an empty string.
        # it's easier to pass this around as a "none" rather than an empty string
        if thumbs == "":
            return None
        else:
            return thumbs

    def question_geekgold(self):
        ggSelector = ".tippersbig > a[aria-label=\"Tips and Recommendations\"]"
        ggElement = self.element(ggSelector)
        gold = ggElement.text

        # it's a little annoying to have to do this, but the "no gold" case is an empty string.
        # it's easier to pass this around as a "none" rather than an empty string
        if gold == "":
            return None
        else:
            return gold

    def question(self, questionNumber):
        questionUrl = "/question/" + str(questionNumber)
        self.loadPage(self.baseUrl + questionUrl)

        try:
            question_text = self.question_text(questionUrl)
        except DeletedQuestion:
            return {
                "id": questionNumber,
                "text": None,
                "thumbs": None,
                "gold": None,
                "username": None,
                "date": None,
            }

        return {
            "id": questionNumber,
            "text": question_text,
            "thumbs": self.question_thumbs(),
            "gold": self.question_geekgold(),
            "username": self.question_asker(),
            "date": None,
        }