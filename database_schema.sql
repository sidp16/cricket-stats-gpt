CREATE TABLE players (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(100),
    date_of_birth DATE,
    batting_style VARCHAR(100),
    bowling_style VARCHAR(100)
);

CREATE TABLE teams (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(100)
);

CREATE TABLE series (
    series_id INT PRIMARY KEY,
    series_name VARCHAR(200),
    is_tournament BOOLEAN
);

CREATE TABLE venues (
    venue_id INT PRIMARY KEY,
    venue_name VARCHAR(200)
);

CREATE TABLE matches (
    series_id INT,
    match_id INT PRIMARY KEY,
    format VARCHAR(100),
    match_date DATE,
    venue_id INT,
    team1_id INT,
    team2_id INT,
    toss_winner_id INT,
    toss_decision VARCHAR(100),
    match_winner_name VARCHAR(100),
    player_of_the_match VARCHAR(100),
    winning_margin VARCHAR(200),
    INDEX idx_match_id (match_id)
);

CREATE TABLE bowling (
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
    PRIMARY KEY (match_id, player_id, innings)
);

CREATE TABLE batting (
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
    batting_position INT,
    innings INT,
    PRIMARY KEY (match_id, player_id, innings)
);

CREATE TABLE matchStats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    batting_team_id INT,
    bowling_team_id INT,
    innings_number INT,
    innings_total INT,
    innings_wickets INT,
    innings_overs FLOAT,
    innings_extras INT,
    innings_declared TINYINT
);

ALTER TABLE matches
    ADD CONSTRAINT fk_team1
    FOREIGN KEY (team1_id) REFERENCES teams (team_id),
    ADD CONSTRAINT fk_team2
    FOREIGN KEY (team2_id) REFERENCES teams (team_id),
    ADD CONSTRAINT fk_toss_winner
    FOREIGN KEY (toss_winner_id) REFERENCES teams (team_id),
    -- ADD CONSTRAINT fk_match_winner
    -- FOREIGN KEY (match_winner_name) REFERENCES teams (team_name),
    -- ADD CONSTRAINT fk_player_of_the_match
    -- FOREIGN KEY (player_of_the_match) REFERENCES players (player_id),
    ADD CONSTRAINT fk_series_matches
    FOREIGN KEY (series_id) REFERENCES series (series_id),
    ADD CONSTRAINT fk_venue_id
    FOREIGN KEY (venue_id) REFERENCES venues (venue_id);

ALTER TABLE bowling
    ADD CONSTRAINT fk_match_bowling
    FOREIGN KEY (match_id) REFERENCES matches (match_id),
    ADD CONSTRAINT fk_team_bowling
    FOREIGN KEY (team_id) REFERENCES teams (team_id),
    ADD CONSTRAINT fk_player_bowling
    FOREIGN KEY (player_id) REFERENCES players (player_id);

ALTER TABLE batting
    ADD CONSTRAINT fk_match_batting
    FOREIGN KEY (match_id) REFERENCES matches (match_id),
    ADD CONSTRAINT fk_team_batting
    FOREIGN KEY (team_id) REFERENCES teams (team_id),
    ADD CONSTRAINT fk_player_batting
    FOREIGN KEY (player_id) REFERENCES players (player_id);

ALTER TABLE matchStats
    ADD CONSTRAINT fk_match_stats
    FOREIGN KEY (match_id) REFERENCES matches (match_id),
    ADD CONSTRAINT fk_batting_team
    FOREIGN KEY (batting_team_id) REFERENCES teams (team_id),
    ADD CONSTRAINT fk_bowling_team
    FOREIGN KEY (bowling_team_id) REFERENCES teams (team_id);
