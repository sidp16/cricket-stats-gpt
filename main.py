from credentials import gpt_api_key, password, sql_database_uri
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from kor import create_extraction_chain, Object, Text
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from espncricinfo.match import Match
from espncricinfo.player import Player
from langchain.callbacks import get_openai_callback
from scorecard_tools.scraping_tools import (
    extract_batting_data,
    extract_bowling_data,
    extract_match_data,
    extract_series_data,
    extract_team_data,
    extract_venue_data,
)
import mysql.connector
from mysql.connector import Error
from scorecard_tools.database_insertion_tools import insert_data


def make_filename(type, match_id):
    print(type)
    types = ["Batting of", "Bowling of", "Match details of", "Match stats of"]
    m = Match(match_id)
    if type == "batting":
        filename = f"{types[0]} {m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    if type == "bowling":
        filename = f"{types[1]} {m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    if type == "details":
        filename = f"{types[2]} {m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    if type == "match stats":
        filename = f"{types[3]} {m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"

    return filename


def run(match_id):
    batting, players1 = extract_batting_data(match_id)
    bowling, players2 = extract_bowling_data(match_id)
    venues = extract_venue_data(match_id)
    series = extract_series_data(match_id)
    teams = extract_team_data(match_id)
    matches = extract_match_data(match_id)

    print("\n\n\nInserting...")
    insert_data(players1, "players")
    insert_data(players2, "players")
    insert_data(teams, "teams")
    insert_data(series, "series")
    insert_data(venues, "venues")
    insert_data(matches, "matches")
    insert_data(batting, "batting")
    insert_data(bowling, "bowling")

    print("ALL DONE!")


if __name__ == "__main__":
    run(1144526)
    # IND V PAK 2022 T20 WC
    # matchDetails = extract_match_data("1298134", "1298150")
    # insert_data(matchDetails, "matches")
    # batting = extract_batting_data("1298134", "1298150")
    # insert_data(batting, "batting")

    # MI V CSK 2018 IPL
    # runMatch("8048", "1136561")

    # Testing for an ODI: IND V SL 2011 ODI WC FINAL
    # matchDetails2 = extract_match_data("381449", "433606")

    # Testing for a Test with 4 Innings: IND V ENG 2018 1st Test
    # runMatch("1119528", "1119549")

    # Testing for a Test with 3 Innings: IND V ENG 2021 4th Test
    # runMatch("1243364", "1243387")

    # Testing for a Test with 2 Innings: SA V ENG 2000 5th Test
    # runMatch("61687", "63864")

    ## -- METHOD 3 -- ##
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

    db = SQLDatabase.from_uri(sql_database_uri)
    toolkit = SQLDatabaseToolkit(
        db=db, llm=OpenAI(temperature=0, openai_api_key=gpt_api_key)
    )

    agent = create_sql_agent(
        llm=ChatOpenAI(
            temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=gpt_api_key
        ),
        toolkit=toolkit,
        verbose=True,
        # agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    # print(agent.agent.llm_chain.prompt.template)

    # agent.run(f"List all the games Sachin has played in.")
