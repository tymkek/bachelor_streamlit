import json
import streamlit as st
import numpy as np
import pandas as pd
from openai import OpenAI
import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from itertools import islice

load_dotenv()


@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["db_uri"], tlsCAFile=certifi.where())

client = init_connection()
db = client["bacluster"]

@st.cache_data(ttl=600)
def get_data():

    collection = db['ans']

    filter_criteria = {
             'questions_id': st.session_state.questions_id 
        }
    pipeline = [
            {
            '$match': {
                '_id': {'$ne': st.session_state.file_id},
                **filter_criteria
            }
        },
            {
            '$sample': {'size': 1}  
        }
        ]
    
    result = list(collection.aggregate(pipeline))
    return result


class SurveySite:

    def __init__(self):
        with open("./config/books_questions.json", "r") as file:
            self.q_books = json.load(file)
        with open("./config/sigma_questions.json", "r") as file:
            self.q_sigma = json.load(file)
        with open("./config/books.txt", "r") as file:
            self.t_books = file.read()
        with open("./config/sigma.txt", "r") as file:
            self.t_sigma = file.read()

    def set_state(self, state):
        st.session_state.page = state
    
    def db_callback(self, file, state, collection):
        insert_result = db[collection].insert_one(file)
        st.session_state.file_id = insert_result.inserted_id
        self.set_state(state)
        st.cache_data.clear()
    
    def question_page(self, questions):
        
        st.session_state.questions_id = st.session_state.page
        with st.container():
            ans_dict = {}
            ans_dict["questions_id"] = st.session_state.page
            
            for q in questions["questions"]:
                ans = st.text_area(q["question"])
                if ans:
                    ans_dict[q["question"]] = ans
            
            st.button("Submit answers", on_click=self.db_callback, args=[ans_dict, "rate_page", "ans"])


    def home_page(self):
        with st.container():
            st.title("Evaluation of user knowledge with LLM and human feedback - experiment")
            st.write("Experiment is conducted in a survey form, consisting of two parts. Completing the test will take you approximately **7 minutes**.")
            st.write(
                "In the first part, you will be choosing a short article to read. You will have 5 minutes to do so, with option to proceed further, regardless of the remaining time. After that you will be shown five questions based on the chosen text, answer them **accordingly to your knowledge**."
            )
            st.write(
                "In the second part, you will be evaluating 5 different answers to the same questions set, with given evaluation scale."
            )
            st.write("Participation is anonymous, by pressing the button, you agree to the experiment terms.")
            st.button("Next", on_click=self.set_state, args=["choose"])

    def final_page(self):
        with st.container():
            st.title("Thanks for participation")

    def choose_page(self):
        with st.container():
            st.title("Please, choose the article you would like to read")
            tab1, tab2, tab3, tab4 = st.tabs(["Article 1", "Article 2", "Article 3", "Article 4"])
            with tab1:
                st.header("The truth about sigma males")
                st.write("A tale of toxic masculinity and romanticising loneliness")
                st.write("Genere: pop culture, social media")
                st.button("Choose", key="t1", on_click=self.set_state, args=["text1"])

            with tab2:
                st.header("Reading Books Is Useless: Here's a Better Way to Read")
                st.write("Genere: studying, ")
                st.button("Choose", key="t2", on_click=self.set_state, args=["text2"])

            with tab3:
                st.header("Article 3 placeholder, choosing it will redirect you to article 1")
                st.write("Genere: science")
                st.button("Choose", key="t3", on_click=self.set_state, args=["text1"])

            with tab4:
                st.header("Article 4 placeholder, choosing it will redirect you to article 1")
                st.write("Genere: politics")
                st.button("Choose", key="t4", on_click=self.set_state, args=["text1"])

    def text_page(self, text):
        with st.container():

            timer = st.empty()
            article = st.empty()
            article.write(text)
            N = 10
            match st.session_state.page:
                case "text1":
                    st.button(
                        "Go next", on_click=self.set_state, args=["question_page1"]
                    )
                case "text2":
                    st.button(
                        "Go next", on_click=self.set_state, args=["question_page2"]
                    )
                case "text3":
                    st.button(
                        "Go next", on_click=self.set_state, args=["question_page3"]
                    )
                case "text4":
                    st.button(
                        "Go next", on_click=self.set_state, args=["question_page4"]
                    )
            for secs in range(N, 0, -1):
                mm, ss = secs // 60, secs % 60
                timer.metric("Countdown", f"{mm:02d}:{ss:02d}")
                time.sleep(1)
            timer.write("")
            article.write("Time ended, please proceed further")


    def rate_page(self):
        
        result = get_data()
        selected_options = {}
        selected_options["questions_id"] = st.session_state.questions_id
        with st.container():
            for key, value in islice(result[0].items(), 2, None):
    
                st.subheader(key)
                st.write(f"Answer: {value}")
    
                choice = st.radio(
                    f"Your evaluation of the given answer:",
                    ('very bad', 'bad', 'average', 'good', 'excellent'),
                    key=key
                )
                selected_options[key] = {"ans": value, "eval": choice}

            st.button("Submit", on_click=self.db_callback, args=[selected_options, "final", "eval"])

    def main(self):

        if "page" not in st.session_state:
            st.session_state.page = "home"

        with st.empty():

            match st.session_state.page:

                case "home":
                    self.home_page()

                case "choose":
                    self.choose_page()

                case "question_page1":
                    self.question_page(self.q_sigma)

                case "text1":
                    self.text_page(self.t_sigma)

                case "question_page2":
                    self.question_page(self.q_books)

                case "text2":
                    self.text_page(self.t_books)
                
                case "rate_page":
                    self.rate_page()

                case "final":
                    self.final_page()


if __name__ == "__main__":
    site = SurveySite()
    site.main()
