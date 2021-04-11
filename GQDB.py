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

    def query_write_only(self, query):
        self.cursor.execute(query)
        self.db.commit()

    def query_one(self, query):
        self.cursor.execute(query)
        self.db.commit()
        row = self.cursor.fetchone()
        return row

    def query(self, query):
        self.cursor.execute(query)
        self.db.commit()
        row = self.cursor.fetchall()
        return row

    def most_recent_question_id(self):
        query = """SELECT id FROM {schema}.question ORDER BY id DESC LIMIT 1""".format(schema = self.scrapeSchema)
        row = self.query_one(query)
        return row[0]

    def is_user(self, schema, username):
        query = """SELECT * FROM {schema}.user WHERE user = '{username}'""".format(schema = schema, user = username)
        row = self.query_one(query)
        return true if row else false

    def is_classic_user(self, username):
        self.is_user(self.classicSchema, username)

    def is_new_user(self, username):
        self.is_user(self.scrapeSchema, username)

    def dbify_question_dict(self, qDict):
        for trait in qDict.keys():
            if qDict[trait] == None:
                # postgres doesn't understand None so well
                qDict[trait] = "NULL"
            elif isinstance(qDict[trait], str):
                # strings need to be wrapped in quotes
                qDict[trait] = "'{0}'".format(str(qDict[trait]))
            else:
                # pass everything else through as-is
                pass

        return qDict

    def write_question(self, qDict):
        qDict = self.dbify_question_dict(qDict)

        query = "INSERT INTO {schema}.question(id, text, thumbs, gold, user_id, date, scrape_time, num_answers)\
            VALUES ({id}, {text}, {thumbs}, {gold}, {user_id}, {date}, '{scrape_time}', NULL)"\
            .format(schema = self.scrapeSchema, id = qDict["id"], text = qDict["text"],\
            thumbs = qDict["thumbs"], gold = qDict["gold"], user_id = qDict["user_id"],\
            date = qDict["date"], scrape_time = datetime.now().isoformat())
        self.query_write_only(query)

    def __del__(self):
        self.cursor.close()
        self.db.close()