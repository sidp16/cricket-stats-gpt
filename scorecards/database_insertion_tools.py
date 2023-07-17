import pandas as pd
import mysql.connector
from credentials import password


def insert_batting_data(dataframe, table_name):
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host="localhost", database="scorecards", user="root", password=password
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Prepare the SQL statement for inserting data into the table
    sql = f"INSERT INTO {table_name} (match_id, team_id, player_id, player_name, description, runs, balls, fours, sixes, strike_rate, innings) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # Insert each row of data from the DataFrame into the table
    for row in dataframe.itertuples(index=False):
        cursor.execute(sql, row)

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()


def insert_match_data(dataframe, table_name):
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host="localhost", database="scorecards", user="root", password=password
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Prepare the SQL statement for inserting data into the table
    sql = f"INSERT INTO {table_name} (series_id, match_id, match_date, venue, team1, team2, toss_winner, toss_decision, match_winner, player_of_the_match, format, winning_margin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # Insert each row of data from the DataFrame into the table
    for row in dataframe.itertuples(index=False):
        cursor.execute(sql, row)

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
