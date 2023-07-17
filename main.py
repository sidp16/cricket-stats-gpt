from credentials import gpt_api_key, password, sql_database_uri
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from espncricinfo.match import Match
from scorecards.scraping_tools import extract_batting_data, extract_bowling_data
import mysql.connector
from mysql.connector import Error
from scorecards.database_insertion_tools import insert_batting_data

if __name__ == "__main__":
    # MI V CSK 2018 IPL
    # extract_batting_data(8048, 1136561)
    # extract_bowling_data(8048, 1136561)

    # IND V PAK 2022 T20 WC
    m = Match("1298150")
    filename = (
        f"{m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    )
    pakvind_batting = extract_batting_data(1298134, 1298150)
    pakvind_batting.to_csv(filename, index=False)
    insert_batting_data(pakvind_batting, "batting")
    # pakvind_bowling = extract_bowling_data(1298134, 1298150)
    # pakvind_bowling.to_csv(filename, index=False)

    # Testing for an ODI: IND V SL 2011 ODI WC FINAL
    # indvsl_batting = extract_batt~ing_data(381449, 433606)
    # indvsl_bowling = extract_bowling_data(381449, 433606)

    # Testing for a Test with 4 Innings: IND V ENG 2018 1st Test
    # m2 = Match("1119549")
    # filename = f"{m2._team_1_abbreviation()} vs {m2._team_2_abbreviation()} on {m2._date()}.csv"
    # indveng_batting18 = extract_batting_data(1119528, 1119549)
    # indveng_batting18.to_csv(filename, index=False)
    # print(indveng_batting18)
    # insert_batting_data(indveng_batting18, "batting")

    # indveng_bowling18 = extract_bowling_data(1119528, 1119549)

    # Testing for a Test with 3 Innings: IND V ENG 2021 4th Test
    # indveng_batting21 = extract_batting_data(1243364, 1243387)
    # indveng_bowling21 = extract_bowling_data(1243364, 1243387)

    # Testing for a Test with 2 Innings: SA V ENG 2000 5th Test
    # engvsa_batting = extract_batting_data(61687, 63864)
    # engvsa_bowling = extract_bowling_data(61687, 63864)

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

    # db = SQLDatabase.from_uri(sql_database_uri)
    # toolkit = SQLDatabaseToolkit(
    #     db=db, llm=OpenAI(temperature=0, openai_api_key=gpt_api_key)
    # )

    # agent = create_sql_agent(
    #     llm=ChatOpenAI(
    #         temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=gpt_api_key
    #     ),
    #     toolkit=toolkit,
    #     verbose=True,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    # )

    # agent.run("Who has hit the most boundaries in one game?")
