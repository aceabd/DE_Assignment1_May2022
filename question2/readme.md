## Step 1>> bash create_docker.sh

## docker-compose up -d
In the container run this command:
################
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
##################
## execute the sql query
## enable the dag data_transformation
## access the airflow from http://localhost:8080 username:airflow password:airflow

## to access postgresql
## connection string jdbc:postgresql://localhost:5432/posgres
## username:postgres password:postgres

## to access mongoDB
## connection string mongodb://mongoadmin:mongo@localhost:27017
