CREATE TABLE matchStats (
id INT AUTO_INCREMENT PRIMARY KEY,
match_id INT,
batting_team_id iNT,
bowling_team_id INT,
innings_number INT,
innings_total INT,
innings_wickets INT,
innings_overs FLOAT,
innings_extras INT,
innings_declared TINYINT,
CONSTRAINT fk_match_stats
FOREIGN KEY (match_id) REFERENCES matches (match_id)
);

CREATE TABLE bowling (
id INT AUTO_INCREMENT PRIMARY KEY,
match_id INT,
team_id INT,
player_id INT,
player_name VARCHAR(100),
overs FLOAT,
maidens INT,
runs INT,
wickets INT,
economy FLOAT,
dots INT,
fours INT,
sixes INT,
wides INT,
no_balls INT,
innings INT,
CONSTRAINT fk_match_bowling
FOREIGN KEY (match_id) REFERENCES matches (match_id)
);

CREATE TABLE batting (
id INT AUTO_INCREMENT PRIMARY KEY,
match_id INT,
team_id INT,
player_id INT,
player_name VARCHAR(100),
description VARCHAR(100),
runs INT,
balls INT,
fours INT,
sixes INT,
strike_rate FLOAT,
innings INT,
CONSTRAINT fk_match
FOREIGN KEY (match_id) REFERENCES matches (match_id)
);

CREATE TABLE matches (
id INT AUTO_INCREMENT PRIMARY KEY,
series_id INT,
match_id INT,
format VARCHAR(100),
match_date DATE,
venue_id INT,
team1 INT,
team2 INT,
toss_winner_id INT,
toss_decision VARCHAR(100),
match_winner_id INT,
player_of_the_match VARCHAR(100),
winning_margin VARCHAR(200),
INDEX idx_match_id (match_id)
);
