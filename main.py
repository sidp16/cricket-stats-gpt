from credentials import gpt_api_key, password, sql_database_uri
from langchain.agents import create_csv_agent, create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from espncricinfo.match import Match
from scorecards.scraping_tools import extract_batting_data, extract_bowling_data
import mysql.connector
from mysql.connector import Error

if __name__ == "__main__":
    # MI V CSK 2018 IPL
    # extract_batting_data(8048, 1136561)
    # extract_bowling_data(8048, 1136561)

    # IND V PAK 2022 T20 WC
    # m = Match("1298150")
    # filename = f"{m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    # pakvind_batting = extract_batting_data(1298134, 1298150)
    # pakvind_batting.to_csv(filename, index=False)
    # pakvind_bowling = extract_bowling_data(1298134, 1298150)

    # Testing for an ODI: IND V SL 2011 ODI WC FINAL
    # indvsl_batting = extract_batting_data(381449, 433606)
    # indvsl_bowling = extract_bowling_data(381449, 433606)

    # Testing for a Test with 4 Innings: IND V ENG 2018 1st Test
    # m2 = Match("1119549")
    # filename = f"{m2._team_1_abbreviation()} vs {m2._team_2_abbreviation()} on {m2._date()}.csv"
    # indveng_batting18 = extract_batting_data(1119528, 1119549)
    # indveng_batting18.to_csv(filename, index=False)
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
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    agent.run("Who has hit the most boundaries in one game?")

    ## -- METHOD 1 -- ##
    # openai.api_key = gpt_api_key
    # df = pd.read_csv("IND vs PAK on 2022-10-23.csv")
    # chat = ChatOpenAI(
    # model_name="gpt-3.5-turbo", temperature=0.0, openai_api_key=gpt_api_key
    # )
    # agent = create_pandas_dataframe_agent(chat, df, verbose=True)
    # agent.run("Who scored the most runs in the game?")

    ## -- METHOD 2 -- ##
    agent = create_csv_agent(
        OpenAI(temperature=0, openai_api_key=gpt_api_key),
        "ENG vs IND on 2018-08-01.csv",
        verbose=True,
    )

    agent.agent.llm_chain.prompt.template = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.

The dataframe you will be working with is scorecard data from a cricket match.
Each row is a specific players' statistics in a singular match.
Some player's go by just their surname, or just their first name. Learn to adapt to either.
Here are some useful definitons:
    - If a player has 2 4s, it means they hit two shots that count for 4 runs each. Therefore, in this case it means that they scored 8 runs by hitting 4s.
    - If a player has 5 6s, it means they hit 5 shots that counted for 6 runs each. Therefore, in this case it means that they scored 30 runs by hitting 6s. 
    - Boundary: A boundary is the scoring of 4 or 6 runs from a single shot. 
    - Innings: An innings is one of the divisions of a cricket match during which one team takes its turn to bat. Therefore, if the innings number
    is 2, they batted in the 2nd innings - therefore meaning that they batted 2nd in the match.
    - Batting Average: A batting average is the total number of runs scored divided by the number of times they have been out. Therefore, if a player has
    scored 60 runs and gotten out twice, their average is 30. Similarly, if a player has scored 150 runs but not gotten out, their average is undefined.

You should use the tools below to answer the question posed of you:

python_repl_ast: A Python shell. Use this to execute python commands. Input should be a valid python command. When using this tool, sometimes output is abbreviated - make sure it does not look abbreviated before using it in your answer.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [python_repl_ast]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question


This is the result of `print(df.head())`:
{df_head}

Begin!
Question: {input}
{agent_scratchpad}
    """
