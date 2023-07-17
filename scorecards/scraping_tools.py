import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


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
