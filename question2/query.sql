create table tweets
(
    type      text,
    id        text,
    timestamp text,
    query     text,
    user_name text,
    message   text
);

COPY tweets(type, id, timestamp, query, user_name ,message)
    FROM '/file.csv'
    DELIMITER ','
    CSV HEADER;
