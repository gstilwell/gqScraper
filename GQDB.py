import psycopg2
from datetime import datetime

class GQDB:
    def __init__(self, name, host, port, username, password):
        dbConnectString = "dbname='{dbname}' host='{host}' port='{port}' user='{user}' password='{password}'"\
            .format(dbname = name, host = host, port = port, user = username, password = password)
        try:
            self.db = psycopg2.connect(dbConnectString)
            self.cursor = self.db.cursor()
        except Exception as e:
            print("couldn't connect to db")
            print(e)

        self.classicSchema = "main"
        self.scrapeSchema = "gqscrape"

    def queryWriteOnly(self, query):
        self.cursor.execute(query)
        self.db.commit()

    def queryOne(self, query):
        self.cursor.execute(query)
        self.db.commit()
        row = self.cursor.fetchone()
        return row

    def query(self, query):
        self.cursor.execute(query)
        self.db.commit()
        row = self.cursor.fetchall()
        return row

    def mostRecentQuestionIdSaved(self):
        query = """SELECT id FROM {schema}.question ORDER BY id DESC LIMIT 1""".format(schema = self.scrapeSchema)
        row = self.queryOne(query)
        return row[0]

    def mostRecentUserId(self):
        base_query = "SELECT id FROM {schema}.user ORDER BY id DESC LIMIT 1"
        new_query = base_query.format(schema = self.scrapeSchema)
        classic_query = base_query.format(schema = self.classicSchema)

        latestNewId = self.queryOne(new_query)[0]
        latestClassicId = self.queryOne(classic_query)[0]
        if latestNewId > latestClassicId:
            return latestNewId
        else:
            return latestClassicId

    def mostRecentAnswerId(self):
        query = "SELECT id FROM {schema}.answer ORDER BY id DESC LIMIT 1".format(schema = self.scrapeSchema)
        row = self.queryOne(query)
        return row[0] if row else 0

    def assigned_userId(self, username):
        return self.mostRecentUserId() + 1

    def getUserId(self, schema, username):
        query = """SELECT * FROM {schema}.user WHERE name = '{username}'""".format(schema = schema, username = username)
        row = self.queryOne(query)
        return row[0] if row else None

    def isClassicUser(self, username):
        if self.getUserId(self.classicSchema, username):
            return True
        else:
            return False

    def isNewUser(self, username):
        if self.getUserId(self.scrapeSchema, username):
            return True
        else:
            return False

    def userId(self, username):
        if self.isClassicUser(username):
            return self.getUserId(self.classicSchema, username)
        if self.isNewUser(username):
            return self.getUserId(self.scrapeSchema, username)
        else:
            return self.assigned_userId(username)

    def addUser(self, username):
        # if we're scraping a deleted question, username will be None
        # do nothing in this case
        if not username:
            return
        print("adding user " + username)
        # need to wrap string in single quotes for the query
        quotedUsername = "'{name}'".format(name = username)
        self.queryWriteOnly("INSERT INTO {schema}.user(id, name, url) VALUES ({id},{name},{url})"\
            .format(schema = self.scrapeSchema, id = self.userId(username), name = quotedUsername, url = quotedUsername))

    def dbifyDict(self, theDict):
        for trait in theDict.keys():
            if theDict[trait] == None:
                # postgres doesn't understand None so well
                theDict[trait] = "NULL"
            elif isinstance(theDict[trait], str):
                # strings need to be wrapped in quotes and their apostrophes escaped for postgres
                theDict[trait] = "'{0}'".format(str(theDict[trait]).replace("'", "''"))
            else:
                # pass everything else through as-is
                pass

        return theDict

    def addUserIfUnknown(self, username):
        if not self.isNewUser(username):
            self.addUser(username)

    def addQuestionIfUnknown(self, question):
        if not self.questionIsInScrapeDatabase(question["id"]):
            self.writeQuestion(question)

    def writeQuestion(self, qDict):
        askedByUser = qDict["username"]
        # the dummy user in the database used for deleted questions is id 0
        # force 0 id if we get a "None" deleted user
        if not askedByUser:
            askedByUserId = 0
        else:
            askedByUserId = self.userId(askedByUser)
        qDict = self.dbifyDict(qDict)
        self.addUserIfUnknown(askedByUser)

        print("writing question " + qDict["text"])
        query = "INSERT INTO {schema}.question(id, text, thumbs, gold, user_id, date, scrape_time, num_answers)\
            VALUES ({id}, {text}, {thumbs}, {gold}, {userId}, {date}, '{scrape_time}', NULL)"\
            .format(schema = self.scrapeSchema, id = qDict["id"], text = qDict["text"],\
            thumbs = qDict["thumbs"], gold = qDict["gold"], userId = askedByUserId,\
            date = qDict["date"], scrape_time = datetime.now().isoformat())
        self.queryWriteOnly(query)

    # we need the question passed in because we have to save it if it's not already in the database,
    # and we don't have access to the scraper. So it's up to the calling code to get the question associated
    # with this answer and give it to us
    def writeAnswer(self, question, aDict):
        answeredByUser = aDict["username"]
        answeredByUserId = self.userId(answeredByUser)
        aDict = self.dbifyDict(aDict)
        self.addUserIfUnknown(answeredByUser)
        self.addQuestionIfUnknown(question)

        print("writing answer " + aDict["text"])
        query = "INSERT INTO {schema}.answer(id, text, thumbs, gold, date, scrape_time, user_id, question_id)\
            VALUES ({id}, {text}, {thumbs}, {gold}, {date}, '{scrape_time}', {userId}, {qid})"\
            .format(schema = self.scrapeSchema, id = self.mostRecentAnswerId() + 1, text = aDict["text"],\
            thumbs = aDict["thumbs"], gold = aDict["gold"], date = aDict["date"],\
            scrape_time = datetime.now().isoformat(), userId = answeredByUserId, qid = aDict["question_id"])
        self.queryWriteOnly(query)

    def questionIsInScrapeDatabase(self, qid):
        query = "SELECT id FROM {schema}.question WHERE id = {qid}".format(schema = self.scrapeSchema, qid = qid)
        row = self.queryOne(query)
        return True if row else False

    def answerIsInScrapeDatabase(self, answer):
        # I wanted to use the username and date here to verify the answer exists, but that requires
        # the user to be in the database already. I don't want to have that burden placed on this method.
        # Searching by text and date is good enough. If two people post the exact same answer at the exact same
        # second, somebody's answer will be counted as already scraped and will be flagged as such.
        # I think the odds are very much against that happening in the next two weeks
        # (after which point this method won't matter much at all anyway)
        answer = self.dbifyDict(answer.copy())
        query = "SELECT id FROM {schema}.answer WHERE text = {text} AND date = {date}"\
            .format(schema = self.scrapeSchema, text = answer["text"], date = answer["date"])
        row = self.queryOne(query)
        return True if row else False

    def __del__(self):
        self.cursor.close()
        self.db.close()