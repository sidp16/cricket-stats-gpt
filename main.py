import requests
import pandas as pd
import re
import openai
import tempfile
import streamlit as st
from bs4 import BeautifulSoup
from streatlit_chat import message
from credentials import gpt_api_key
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
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
    m = Match("1298150")
    filename = (
        f"{m._team_1_abbreviation()} vs {m._team_2_abbreviation()} on {m._date()}"
    )
    pakvind_batting = extract_batting_data(1298134, 1298150)
    pakvind_batting.to_csv(filename, index=False)
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

    # openai.api_key = gpt_api_key
    # df = pd.read_csv("IND vs PAK on 2022-10-23")
    # chat = ChatOpenAI(
    # model_name="text-davinci-003", temperature=0.0, openai_api_key=gpt_api_key
    # )
    # agent = create_pandas_dataframe_agent(chat, df, verbose=True)

    user_api_key = st.sidebar.text_input(
        label="#### Your OpenAI API key.",
        placeholder="Paste your openAI API key, sk-",
        type="password",
    )

    uploaded_file = st.sidebar.file_uploader("upload", type="csv")

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = temp_file.name

        loader = CSVLoader(
            file_path=tmp_file_path, encoding="utf-8", csv_args={"delimiter": ","}
        )
        data = loader.load()

    st.write(data)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(data, embeddings)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo"),
        retriever=vectorstore.as_retriever(),
    )

    def conversational_chat(query):
        result = chain({"question": query, "chat_history": st.session_state["history"]})
        st.session_state["history"].append((query, result["answer"]))

        return result["answer"]

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "generated" not in st.session_state:
        st.session_state["generated"] = [
            "Hello ! Ask me anything about " + uploaded_file.name + " 🤗"
        ]

    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey ! 👋"]

    # container for the chat history
    response_container = st.container()
    # container for the user's text input
    container = st.container()

    with container:
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_input(
                "Query:", placeholder="Talk about your csv data here (:", key="input"
            )
            submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input:
            output = conversational_chat(user_input)

            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)

    if st.session_state["generated"]:
        with response_container:
            for i in range(len(st.session_state["generated"])):
                message(
                    st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="big-smile",
                )
                message(
                    st.session_state["generated"][i], key=str(i), avatar_style="thumbs"
                )
