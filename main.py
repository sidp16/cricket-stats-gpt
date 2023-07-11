import requests
import pandas as pd
import re
import openai
from bs4 import BeautifulSoup
from credentials import gpt_api_key
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from espncricinfo.match import Match


def extract_batting_data(series_id, match_id):
    URL = (
        "https://www.espncricinfo.com/series/"
        + str(series_id)
        + "/scorecard/"
        + str(match_id)
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")

    table_body = soup.find_all("tbody")
    batsmen_df = pd.DataFrame(
        columns=["Name", "Desc", "Runs", "Balls", "4s", "6s", "SR", "Innings"]
    )
    for i, table in enumerate(table_body[::2]):
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [x.text.strip().replace("\xa0", " ") for x in cols]
            if cols[0] == "Extras" or cols[0] == "TOTAL":
                continue
            if len(cols) == 8:
                batsmen_df = batsmen_df.append(
                    pd.Series(
                        [
                            re.sub(r"\W+", " ", cols[0].split("(c)")[0]).strip(),
                            cols[1],
                            cols[2],
                            cols[3],
                            cols[5],
                            cols[6],
                            cols[7],
                            i + 1,
                        ],
                        index=batsmen_df.columns,
                    ),
                    ignore_index=True,
                )
    return batsmen_df


def extract_bowling_data(series_id, match_id):
    URL = (
        "https://www.espncricinfo.com/series/"
        + str(series_id)
        + "/scorecard/"
        + str(match_id)
    )
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, "lxml")

    table_body = bs.find_all("tbody")
    bowler_df = pd.DataFrame(
        columns=[
            "Name",
            "Overs",
            "Maidens",
            "Runs",
            "Wickets",
            "Econ",
            "Dots",
            "4s",
            "6s",
            "Wd",
            "Nb",
            "Innings",
        ]
    )
    for i, table in enumerate(table_body[1::2]):
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [x.text.strip() for x in cols]
            if len(cols) == 11:
                bowler_df = bowler_df.append(
                    pd.Series(
                        [
                            cols[0],
                            cols[1],
                            cols[2],
                            cols[3],
                            cols[4],
                            cols[5],
                            cols[6],
                            cols[7],
                            cols[8],
                            cols[9],
                            cols[10],
                            i + 1,
                        ],
                        index=bowler_df.columns,
                    ),
                    ignore_index=True,
                )

    return bowler_df


if __name__ == "__main__":
    # MI V CSK 2018 IPL
    # extract_batting_data(8048, 1136561)
    # extract_bowling_data(8048, 1136561)

    # IND V PAK 2022 T20 WC
    # m = Match("1298150")
    # filename = (
    # f"{m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    # )
    # pakvind_batting = extract_batting_data(1298134, 1298150)
    # pakvind_batting.to_csv(filename, index=False)
    # pakvind_bowling = extract_bowling_data(1298134, 1298150)

    # Testing for an ODI: IND V SL 2011 ODI WC FINAL
    # indvsl_batting = extract_batting_data(381449, 433606)
    # indvsl_bowling = extract_bowling_data(381449, 433606)

    # Testing for a Test with 4 Innings: IND V ENG 2018 1st Test
    # indveng_batting18 = extract_batting_data(1119528, 1119549)
    # indveng_bowling18 = extract_bowling_data(1119528, 1119549)

    # Testing for a Test with 3 Innings: IND V ENG 2021 4th Test
    # indveng_batting21 = extract_batting_data(1243364, 1243387)
    # indveng_bowling21 = extract_bowling_data(1243364, 1243387)

    # Testing for a Test with 2 Innings: SA V ENG 2000 5th Test
    # engvsa_batting = extract_batting_data(61687, 63864)
    # engvsa_bowling = extract_bowling_data(61687, 63864)

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
        "IND vs PAK on 2022-10-23.csv",
        verbose=True,
    )

    agent.agent.llm_chain.prompt.template = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.

The dataframe you will be working with is scorecard data from a cricket match.
Each row is a specific players' statistics in a singular match.
Here are some useful definitons:
    - If a player has 2 4s, it means they hit two shots that count for 4 runs each. Therefore, in this case it means that they scored 8 runs by hitting 4s.
    - If a player has 5 6s, it means they hit 5 shots that counted for 6 runs each. Therefore, in this case it means that they scored 30 runs by hitting 6s. 

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

    # print(agent.agent.llm_chain.prompt.template)

    agent.run("Which team hit the most boundaries in the match?")
