import json
import openai

training_data = [
    {
        "prompt": "List the games Virat Kohli has scored over 65 runs.",
        "completion": """SELECT matches.match_id, matches.match_date, matches.format, matches.venue_id, 
       CASE
           WHEN matches.team1_id = batting.team_id THEN team2.team_name
           ELSE team1.team_name
       END AS opponent_team,
       batting.runs
FROM matches
INNER JOIN teams AS team1 ON matches.team1_id = team1.team_id
INNER JOIN teams AS team2 ON matches.team2_id = team2.team_id
INNER JOIN batting ON matches.match_id = batting.match_id AND batting.player_name = 'Virat Kohli'
WHERE matches.match_date <= NOW() AND batting.runs > 65
ORDER BY matches.match_date DESC;
""",
    },
    {
        "prompt": "Who are the top 5 batsmen with the highest strike rate in T20Is?",
        "completion": """SELECT players.player_name, 
       SUM(batting.runs) AS total_runs, 
       SUM(batting.balls) AS total_balls, 
       ROUND((SUM(batting.runs) / SUM(batting.balls) * 100), 2) AS strike_rate
FROM batting
JOIN players ON batting.player_id = players.player_id
JOIN matches ON batting.match_id = matches.match_id
WHERE matches.format = 'T20I'
GROUP BY batting.player_id, players.player_name
HAVING total_balls > 50 -- Minimum 50 balls faced to qualify
ORDER BY strike_rate DESC
LIMIT 5;
""",
    },
    {
        "prompt": "Which games has Ben Stokes been man of the match?",
        "completion": """SELECT m.match_id, m.match_date, m.match_winner_name, m.player_of_the_match
FROM matches m
WHERE m.player_of_the_match = 'Ben Stokes';
""",
    },
    {
        "prompt": "What was Kohli's ODI batting average in 2019?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(bat.runs) AS total_runs,
       COUNT(CASE WHEN bat.description NOT LIKE '%not out%' AND bat.description NOT LIKE '%retired hurt%' THEN 1 END) AS total_dismissals,
       ROUND(SUM(bat.runs) / COUNT(CASE WHEN bat.description NOT LIKE '%not out%' AND bat.description NOT LIKE '%retired hurt%' THEN 1 END), 2) AS batting_average
FROM batting bat
JOIN players p ON bat.player_id = p.player_id
JOIN matches m ON bat.match_id = m.match_id
WHERE p.player_name LIKE '%Kohli%' AND m.format = 'ODI' AND YEAR(m.match_date) = 2019
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "What is Shami's career white ball bowling average?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(bowl.runs) AS total_runs_conceded,
       SUM(bowl.wickets) AS total_wickets,
       SUM(bowl.runs) / SUM(bowl.wickets) AS bowling_average
FROM bowling bowl
JOIN players p ON bowl.player_id = p.player_id
JOIN matches m ON bowl.match_id = m.match_id
WHERE p.player_name LIKE '%Shami%' AND m.format IN ('ODI', 'T20I')
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "List the bowlers with the best bowling average in Test cricket.",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(bowl.runs) AS total_runs_conceded,
       SUM(bowl.wickets) AS total_wickets,
       SUM(bowl.runs) / SUM(bowl.wickets) AS bowling_average
FROM bowling bowl
JOIN players p ON bowl.player_id = p.player_id
JOIN matches m ON bowl.match_id = m.match_id
WHERE m.format = 'Test' AND bowl.wickets > 0
GROUP BY p.player_id, p.player_name
ORDER BY bowling_average ASC;
""",
    },
    {
        "prompt": "What is Ravichandran Ashwin's bowling strike rate in test cricket?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(FLOOR(bowl.overs) * 6 + ((bowl.overs - FLOOR(bowl.overs)) * 10)) AS total_balls_bowled,
       SUM(bowl.wickets) AS total_wickets,
       ROUND(SUM(FLOOR(bowl.overs) * 6 + ((bowl.overs - FLOOR(bowl.overs)) * 10)) / SUM(bowl.wickets), 2) AS bowling_strike_rate
FROM bowling bowl
JOIN players p ON bowl.player_id = p.player_id
JOIN matches m ON bowl.match_id = m.match_id
WHERE p.player_name = 'Ravichandran Ashwin' AND m.format = 'Test' AND bowl.wickets > 0
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "What is Rohit Sharma's career ODI boundary percentage?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(batting.fours + batting.sixes) AS total_boundaries,
       SUM(batting.balls) AS total_balls_faced,
       ROUND((SUM(batting.fours + batting.sixes) / SUM(batting.balls) * 100), 2) AS boundary_percentage
FROM batting
JOIN players p ON batting.player_id = p.player_id
JOIN matches m ON batting.match_id = m.match_id
WHERE p.player_name = 'Rohit Sharma' AND m.format = 'ODI'
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "What is Rohit Sharma's average while opening in ODIs?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(bat.runs) AS total_runs,
       COUNT(CASE WHEN bat.batting_position IN (1, 2) THEN 1 END) AS total_matches_as_opener,
       COUNT(CASE WHEN bat.batting_position IN (1, 2) AND bat.description NOT LIKE '%not out%' AND bat.description NOT LIKE '%retired hurt%' THEN 1 END) AS total_dismissals,
       SUM(bat.runs) / COUNT(CASE WHEN bat.batting_position IN (1, 2) AND bat.description NOT LIKE '%not out%' AND bat.description NOT LIKE '%retired hurt%' THEN 1 END) AS batting_average_as_opener
FROM batting bat
JOIN players p ON bat.player_id = p.player_id
JOIN matches m ON bat.match_id = m.match_id
WHERE p.player_name LIKE '%Rohit Sharma%' AND m.format = 'ODI' AND bat.batting_position IN (1, 2)
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "What is Stokes's average while batting at no.5 in ODIs?",
        "completion": """SELECT p.player_id, p.player_name,
       SUM(bat.runs) AS total_runs,
       COUNT(CASE WHEN bat.batting_position = 5 THEN 1 END) AS total_matches_at_no_5,
       COUNT(CASE WHEN bat.batting_position = 5 AND bat.description NOT LIKE '%not out%' THEN 1 END) AS total_dismissals_at_no_5,
       SUM(bat.runs) / COUNT(CASE WHEN bat.batting_position = 5 AND bat.description NOT LIKE '%not out%' THEN 1 END) AS batting_average_at_no_5
FROM batting bat
JOIN players p ON bat.player_id = p.player_id
JOIN matches m ON bat.match_id = m.match_id
WHERE p.player_name LIKE '%Stokes%' AND m.format = 'ODI' AND bat.batting_position = 5
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "How many ducks has Kohli gotten in his career?",
        "completion": """SELECT p.player_id, p.player_name,
       COUNT(CASE WHEN bat.runs = 0 AND bat.description NOT LIKE '%not out%' THEN 1 END) AS total_ducks
FROM batting bat
JOIN players p ON bat.player_id = p.player_id
WHERE p.player_name LIKE '%Kohli%' 
GROUP BY p.player_id, p.player_name;
""",
    },
    {
        "prompt": "List the 100s in ODI cricket with the highest strike rate.",
        "completion": """SELECT p.player_id, p.player_name,
       bat.runs AS century_runs,
       bat.balls AS balls_faced,
       ROUND((bat.runs / bat.balls * 100), 2) AS strike_rate
FROM batting bat
JOIN players p ON bat.player_id = p.player_id
JOIN matches m ON bat.match_id = m.match_id
WHERE bat.runs >= 100 AND m.format = 'ODI'
ORDER BY (bat.runs / bat.balls * 100) DESC;
""",
    },
]

if __name__ == "__main__":
    file_name = "training_data.jsonl"

    with open(file_name, "w") as output_file:
        for entry in training_data:
            json.dump(entry, output_file)
            output_file.write("\n")
