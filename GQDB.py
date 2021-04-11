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

    def most_recent_user_id(self):
        base_query = "SELECT id FROM {schema}.user ORDER BY id DESC LIMIT 1"
        new_query = base_query.format(schema = self.scrapeSchema)
        classic_query = base_query.format(schema = self.classicSchema)

        latest_new_id = self.query_one(new_query)[0]
        latest_classic_id = self.query_one(classic_query)[0]
        if latest_new_id > latest_classic_id:
            return latest_new_id
        else:
            return latest_classic_id

    def assigned_user_id(self, username):
        return self.most_recent_user_id() + 1

    def get_user_id(self, schema, username):
        query = """SELECT * FROM {schema}.user WHERE name = '{username}'""".format(schema = schema, username = username)
        row = self.query_one(query)
        return row[0] if row else None

    def is_classic_user(self, username):
        if self.get_user_id(self.classicSchema, username):
            return True
        else:
            return False

    def is_new_user(self, username):
        if self.get_user_id(self.scrapeSchema, username):
            return True
        else:
            return False

    def user_id(self, username):
        if self.is_classic_user(username):
            return self.get_user_id(self.classicSchema, username)
        if self.is_new_user(username):
            return self.get_user_id(self.scrapeSchema, username)
        else:
            return self.assigned_user_id(username)

    def add_user(self, username):
        # need to wrap string in single quotes for the query
        quoted_username = "'{name}'".format(name = username)
        self.query_write_only("INSERT INTO {schema}.user(id, name, url) VALUES ({id},{name},{url})"\
            .format(schema = self.scrapeSchema, id = self.user_id(username), name = quoted_username, url = quoted_username))

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
        asked_by_user = qDict["user_id"]
        asked_by_user_id = self.user_id(asked_by_user)
        qDict = self.dbify_question_dict(qDict)

        if not self.is_new_user(asked_by_user):
            self.add_user(asked_by_user)

        query = "INSERT INTO {schema}.question(id, text, thumbs, gold, user_id, date, scrape_time, num_answers)\
            VALUES ({id}, {text}, {thumbs}, {gold}, {user_id}, {date}, '{scrape_time}', NULL)"\
            .format(schema = self.scrapeSchema, id = qDict["id"], text = qDict["text"],\
            thumbs = qDict["thumbs"], gold = qDict["gold"], user_id = asked_by_user_id,\
            date = qDict["date"], scrape_time = datetime.now().isoformat())
        self.query_write_only(query)

    def __del__(self):
        self.cursor.close()
        self.db.close()