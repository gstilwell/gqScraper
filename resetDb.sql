DROP TABLE IF EXISTS gqscrape.answer;
DROP TABLE IF EXISTS gqscrape.question;
DROP TABLE IF EXISTS gqscrape.user;



CREATE TABLE gqscrape.user (
    id   int NOT NULL,
    name VARCHAR,
    url  VARCHAR,
    PRIMARY KEY (
        id
    )
);

CREATE TABLE gqscrape.question (
    id          int NOT NULL,
    text        VARCHAR,
    thumbs      int,
    gold        VARCHAR,
    user_id     int,
    date        VARCHAR,
    scrape_time VARCHAR,
    num_answers int,
    PRIMARY KEY (
        id
    ),
    FOREIGN KEY (
        user_id
    )
    REFERENCES gqscrape.user (id) 
);

CREATE TABLE gqscrape.answer (
    id          int NOT NULL,
    text        VARCHAR,
    thumbs      int,
    gold        VARCHAR,
    date        VARCHAR,
    scrape_time VARCHAR,
    user_id     int,
    question_id int,
    PRIMARY KEY (
        id
    ),
    FOREIGN KEY (
        user_id
    )
    REFERENCES gqscrape.user (id),
    FOREIGN KEY (
        question_id
    )
    REFERENCES gqscrape.question (id) 
);