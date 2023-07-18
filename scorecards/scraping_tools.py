import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from espncricinfo.match import Match
from espncricinfo.player import Player


def extract_batting_data(series_id, match_id):
    soup = get_cricinfo_scorecard()

    m = Match(match_id)
    team1_id = m._team_1_id()
    team2_id = m._team_2_id()

    if m.match_json()["batting_first_team_id"] == team1_id:
        batting_first = team1_id
        bowling_first = team2_id
    else:
        batting_first = team2_id
        bowling_first = team1_id

    table_body = soup.find_all("tbody")
    batsmen_df = pd.DataFrame(
        columns=[
            "Match ID",
            "Team ID",
            "Player ID",
            "Name",
            "Desc",
            "Runs",
            "Balls",
            "4s",
            "6s",
            "SR",
            "Innings",
        ]
    )

    for i, table in enumerate(table_body[::2]):
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            # Getting player id with each player
            if len(cols) == 8:
                for link in cols:
                    cols = link.find_all("a")
                    for href in cols:
                        value = href.get("href")
                        if value.startswith("/cricketers/"):
                            player_id = value.split("-")[-1].strip()

            cols = row.find_all("td")
            cols = [x.text.strip().replace("\xa0", " ") for x in cols]

            if cols[0] == "Extras" or cols[0] == "TOTAL":
                continue
            if len(cols) == 8:
                batsmen_df = batsmen_df.append(
                    pd.Series(
                        [
                            match_id,
                            batting_first if (i == 0 or i == 2) else bowling_first,
                            player_id,
                            re.sub(r"\W+", " ", cols[0].split("(c)")[0]).strip(),
                            cols[1],
                            cols[2],
                            cols[3],
                            cols[5],
                            cols[6],
                            None if cols[7] == "-" else cols[7],
                            i + 1,
                        ],
                        index=batsmen_df.columns,
                    ),
                    ignore_index=True,
                )
    return batsmen_df


def extract_bowling_data(series_id, match_id):
    soup = get_cricinfo_scorecard()

    m = Match(match_id)
    team1_id = m._team_1_id()
    team2_id = m._team_2_id()

    table_body = bs.find_all("tbody")
    bowler_df = pd.DataFrame(
        columns=[
            "Match ID",
            "Team ID",
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
                            match_id,
                            team1_id if (i == 0 or i == 2) else team2_id,
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


def extract_match_data(series_id, match_id):
    soup = get_cricinfo_scorecard()

    m = Match(match_id)
    boolean = None

    table_body = soup.find_all("tbody")
    match_df = pd.DataFrame(
        columns=[
            "Series ID",  #
            "Match ID",  #
            "Format",  #
            "Match Date",  #
            "Venue ID",  #
            "Team 1 ID",  #
            "Team 2 ID",  #
            "Toss Winner ID",  #
            "Toss Decision",  #
            "Match Winner ID",  #
            "POTM",  #
            # "Winning Margin",  #
        ]
    )

    for i, table in enumerate(table_body[::2]):
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            # Getting the format and POTM
            if len(cols) == 2:
                for td in cols:
                    text = td.text
                    info = re.findall(r"\b(Player Of The Match|Test|ODI|T20I)\b", text)
                    if info and info[0] in ["Test", "T20I", "ODI"]:
                        format = info[0]
                    # Gets the POTM
                    if info and info[0] == "Player Of The Match":
                        boolean = True
                        continue
                    if boolean == True:
                        potm = td.text
                        boolean = False

    match_df = match_df.append(
        pd.Series(
            [
                series_id,
                match_id,
                format,
                m._date(),
                m._ground_id(),
                m._team_1_id(),
                m._team_2_id(),
                m._toss_winner_team_id(),
                m._toss_decision_name(),
                m._match_winner(),
                potm,
            ],
            index=match_df.columns,
        ),
        ignore_index=True,
    )
    return match_df

def get_cricinfo_scorecard():
    URL = (
        "https://www.espncricinfo.com/series/"
        + str(series_id)
        + "/scorecard/"
        + str(match_id)
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")
    
    return soup

if __name__ == "__main__":
    pakvind_matchData = extract_match_data(1298134, 1298150)
    m = Match(1298150)
    filename = f"Details of {m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}.csv"
    pakvind_matchData.to_csv(filename, index=False)
