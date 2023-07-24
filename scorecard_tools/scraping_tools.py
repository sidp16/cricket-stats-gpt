import dateparser
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from espncricinfo.series import Series
from espncricinfo.match import Match
from espncricinfo.player import Player


def extract_batting_data(match_id):
    URL = "https://www.espncricinfo.com/matches/engine/match/{0}.html".format(
        str(match_id)
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")

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
            "Batting Position",
            "Innings",
        ]
    )

    players_df = pd.DataFrame(
        columns=[
            "Player ID",
            "Player Name",
            "DOB",
            "Batting Style",
            "Bowling Style",
        ]
    )

    for i, table in enumerate(table_body[::2]):
        j = 0
        k = 0
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
                innings_number = i + 1
                if innings_number == 1:
                    k += 1
                else:
                    j += 1

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
                            k if innings_number == 1 else j,
                            innings_number,
                        ],
                        index=batsmen_df.columns,
                    ),
                    ignore_index=True,
                )
                p = Player(player_id)
                try:
                    batting_style = p._batting_style()["description"]
                except:
                    batting_style = None
                try:
                    bowling_style = p._bowling_style()["description"]
                except:
                    bowling_style = None

                players_df = players_df.append(
                    pd.Series(
                        [
                            player_id,
                            re.sub(r"\W+", " ", cols[0].split("(c)")[0]).strip(),
                            dateparser.parse(p._date_of_birth()).strftime("%Y-%m-%d"),
                            batting_style,
                            bowling_style,
                        ],
                        index=players_df.columns,
                    ),
                    ignore_index=True,
                )
    return batsmen_df, players_df


def extract_bowling_data(match_id):
    URL = "https://www.espncricinfo.com/matches/engine/match/{0}.html".format(
        str(match_id)
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")

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
    bowler_df = pd.DataFrame(
        columns=[
            "Match ID",
            "Team ID",
            "Player ID",
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

    players_df = pd.DataFrame(
        columns=[
            "Player ID",
            "Player Name",
            "DOB",
            "Batting Style",
            "Bowling Style",
        ]
    )

    for i, table in enumerate(table_body[1::2]):
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 11:
                for link in cols:
                    cols = link.find_all("a")
                    for href in cols:
                        value = href.get("href")
                        if value.startswith("/cricketers/"):
                            player_id = value.split("-")[-1].strip()

            cols = row.find_all("td")
            cols = [x.text.strip() for x in cols]
            if len(cols) == 11:
                bowler_df = bowler_df.append(
                    pd.Series(
                        [
                            match_id,
                            bowling_first if (i == 0 or i == 2) else batting_first,
                            player_id,
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
                p = Player(player_id)
                try:
                    batting_style = p._batting_style()["description"]
                except:
                    batting_style = None
                try:
                    bowling_style = p._bowling_style()["description"]
                except:
                    bowling_style = None

                players_df = players_df.append(
                    pd.Series(
                        [
                            player_id,
                            re.sub(r"\W+", " ", cols[0].split("(c)")[0]).strip(),
                            dateparser.parse(p._date_of_birth()).strftime("%Y-%m-%d"),
                            batting_style,
                            bowling_style,
                        ],
                        index=players_df.columns,
                    ),
                    ignore_index=True,
                )

    return bowler_df, players_df


def extract_match_data(match_id):
    URL = "https://www.espncricinfo.com/matches/engine/match/{0}.html".format(
        str(match_id)
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "lxml")

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
            "Match Winner Name",  #
            "POTM",  #
            "Winning Margin",  #
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
                    # Gets the format
                    if info and info[0] in ["Test", "T20I", "ODI"]:
                        format = info[0]
                    # Gets the POTM
                    if info and info[0] == "Player Of The Match":
                        boolean = True
                        continue
                    if boolean == True:
                        potm = td.text
                        boolean = False

    m = Match(match_id)
    match_df = match_df.append(
        pd.Series(
            [
                m.get_json()["series"][0]["object_id"],
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
                None,
            ],
            index=match_df.columns,
        ),
        ignore_index=True,
    )

    return match_df


def extract_series_data(match_id):
    m = Match(match_id)
    series_id = m.get_json()["series"][0]["object_id"]
    s = Series(series_id)
    series_df = pd.DataFrame(
        columns=[
            "Series ID",
            "Series Name",
            "Is Tournament",
        ]
    )

    series_df = series_df.append(
        pd.Series(
            [
                series_id,
                s.name,
                s.is_tournament,
            ],
            index=series_df.columns,
        ),
        ignore_index=True,
    )

    return series_df


def extract_team_data(match_id):
    m = Match(match_id)
    teams_df = pd.DataFrame(columns=["Team ID", "Team Name"])

    team1_series = pd.Series(
        [m._team_1_id(), m._team_1_abbreviation()], index=teams_df.columns
    )
    teams_df = teams_df.append(team1_series, ignore_index=True)

    team2_series = pd.Series(
        [m._team_2_id(), m._team_2_abbreviation()], index=teams_df.columns
    )
    teams_df = teams_df.append(team2_series, ignore_index=True)

    return teams_df


def extract_venue_data(match_id):
    m = Match(match_id)
    venues_df = pd.DataFrame(columns=["Venue ID", "Venue Name"])

    venue_series = pd.Series(
        [m._ground_id(), m._ground_name()], index=venues_df.columns
    )
    venues_df = venues_df.append(venue_series, ignore_index=True)

    return venues_df
