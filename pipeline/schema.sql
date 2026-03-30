-- This file should contain all code required to create & seed database tables.



DROP DATABASE IF EXISTS lmnh_museum;
CREATE DATABASE lmnh_museum;

ALTER DATABASE lmnh_museum
SET DateStyle = 'European'
;

\c lmnh_museum

CREATE TABLE department (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE floor (
    floor_id INT PRIMARY KEY,
    floor_name VARCHAR(100) NOT NULL
);

CREATE TABLE request (
    request_id INT PRIMARY KEY,
    request_value INT NOT NULL,
    request_description VARCHAR(100)
);

CREATE TABLE rating (
    rating_id INT PRIMARY KEY,
    rating_value INT NOT NULL,
    rating_description VARCHAR(100)
);

CREATE TABLE exhibition (
    exhibition_id INT PRIMARY KEY,
    exhibition_name VARCHAR(100) NOT NULL,
    exhibition_description TEXT,
    department_id INT REFERENCES department(department_id),
    floor_id INT REFERENCES floor(floor_id),
    exhibition_start_date TIMESTAMP NOT NULL,
    public_id VARCHAR(30)
);

CREATE TABLE request_interaction (
    request_interaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_id INT REFERENCES exhibition(exhibition_id),
    request_id INT REFERENCES request(request_id),
    event_at TIMESTAMP NOT NULL
);

CREATE TABLE rating_interaction (
    rating_interaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_id INT REFERENCES exhibition(exhibition_id),
    rating_id INT REFERENCES rating(rating_id),
    event_at TIMESTAMP NOT NULL

);

INSERT INTO department 
    (department_id, department_name)
VALUES
    (0, 'Entomology'),
    (1, 'Geology'),
    (2, 'Paleontology'),
    (3, 'Zoology'),
    (4, 'Ecology')
;

INSERT INTO floor
    (floor_id, floor_name)
VALUES
    (0, 'Vault'),
    (1, 'First'),
    (2, 'Second'),
    (3, 'Three')
;

INSERT INTO request
    (request_id, request_value, request_description)
VALUES 
    (0, 0, 'Assistance'),
    (1, 1, 'Emergency')
;

INSERT INTO rating
    (rating_id, rating_value, rating_description)
VALUES
    (0, 0, 'Terrible'),
    (1, 1, 'Bad'),
    (2, 2, 'Neutral'),
    (3, 3, 'Good'),
    (4, 4, 'Amazing')
;


INSERT INTO exhibition
    (exhibition_id, exhibition_name, 
    exhibition_description, 
    department_id, 
    floor_id, 
    exhibition_start_date, public_id)
VALUES
    (1, 'Adaptation',
    'How insect evolution has kept pace with an industrialised world',
    2,
    0,
    '01/07/19',
    'EXH_01'),
    (0, 'Measureless to Man',
    'How insect evolution has kept pace with an industrialised world',
    1,
    1,
    '23/08/21',
    'EXH_00'),
    (5, 'Thunder Lizards',
    'How new research is making scientists rethink what dinosaurs really looked like.',
    2,
    1,
    '01/02/23',
    'EXH_05'),
    (2, 'The Crenshaw Collector',
    'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.',
    3,
    2,
    '03/03/21',
    'EXH_02'),
    (4, 'Our Polluted World',
    'A hard-hitting exploration of humanity''s impact on the environment.',
    4,
    3,
    '12/05/21',
    'EXH_04'),
    (3, 'Cetacean Sensations',
    'Whales: from ancient myth to critically endangered.',
    3,
    1,
    '01/07/19',
    'EXH_03')
;