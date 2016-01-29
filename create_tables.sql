
CREATE TABLE questions(
question_id INT PRIMARY KEY NOT NULL,
month_ INT NOT NULL,
day_ INT NOT NULL,
question VARCHAR(1000) NOT NULL
);

CREATE TABLE users(
email VARCHAR(100) PRIMARY KEY NOT NULL,
first_name VARCHAR(100) NOT NULL,
last_name VARCHAR(100) NOT NULL,
pwd VARCHAR(150) NOT NULL
);

CREATE TABLE user_answers(
email VARCHAR(100) NOT NULL,
question_id INT NOT NULL,
year_ INT NOT NULL,
answer text,
PRIMARY KEY(email, question_id)
);
