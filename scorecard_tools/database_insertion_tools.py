import pandas as pd
import mysql.connector
from credentials import password


def insert_data(dataframe, table_name):
    # Establish a connection to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="localhost",
            database="scorecards",
            user="root",
            password=password,
        )
        if connection.is_connected():
            print("Connected to MySQL server!")
    except Error as e:
        print(f"Error connecting to MySQL server: {e}")


    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Prepare the relevant SQL statement for inserting data into the table
    if table_name == "batting":
        sql = f"INSERT IGNORE INTO {table_name} (match_id, team_id, player_id, player_name, description, runs, balls, fours, sixes, strike_rate, batting_position, innings) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    elif table_name == "bowling":
        sql = f"INSERT IGNORE INTO {table_name} (match_id, team_id, player_id, player_name, overs, maidens, runs, wickets, economy, dots, fours, sixes, wides, no_balls, innings) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    elif table_name == "matches":
        sql = f"INSERT IGNORE INTO {table_name} (series_id, match_id, format, match_date, venue_id, team1_id, team2_id, toss_winner_id, toss_decision, match_winner_name, player_of_the_match, winning_margin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    elif table_name == "players":
        sql = f"INSERT IGNORE INTO {table_name} (player_id, player_name, date_of_birth, batting_style, bowling_style) VALUES (%s, %s, %s, %s, %s)" 
    elif table_name == "teams":
        sql = f"INSERT IGNORE INTO {table_name} (team_id, team_name) VALUES (%s, %s)"
    elif table_name == "series":
        sql = f"INSERT IGNORE INTO {table_name} (series_id, series_name, is_tournament) VALUES (%s, %s, %s)"
    elif table_name == "venues":
        sql = f"INSERT IGNORE INTO {table_name} (venue_id, venue_name) VALUES (%s, %s)"
    elif table_name == "matchStats":
        sql = f"INSERT IGNORE INTO {table_name} (match_id, batting_team_id, bowling_team_id, innings_number, innings_total, innings_wickets, innings_overs, innings_extras, innings_declared) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    else:
        print(f"Invalid table name: {table_name}")
    
    # Insert each row of data from the DataFrame into the table
    for row in dataframe.itertuples(index=False):
        cursor.execute(sql, row)

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()