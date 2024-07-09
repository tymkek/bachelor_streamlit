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

        with open("./config/humor_questions.json", "r") as file:
            self.q_humor = json.load(file)
        with open("./config/humor.txt", "r") as file:
            self.t_humor = file.read()

        with open("./config/koty_questions.json", "r") as file:
            self.q_koty = json.load(file)
        with open("./config/koty.txt", "r") as file:
            self.t_koty = file.read()

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
            st.title("Evaluation of user knowledge with LLM and human feedback - badanie")
            st.write("Zapraszam do wypełnienia zadania związanego z moją pracą licencjacką. Całośc zjamie ci około **7 minut**.")
            st.write("Badanie składa się z dwóch części")
            st.write(
                "Część pierwsza, ma postać testu czytania ze zrozumieniem. Do wyboru masz dwa teskty, wybierz ten który uważasz za ciekawszy. Następnie, będziesz mieć 5 minut na przeczytanie go, z możliwością przejścia do pytań szybciej. Do przeczytanego tekstu nie ma możliwości powrotu. Odpowiadaj na pytania zgodnie ze **swoim stanem wiedzy**, nie zostawiaj pustych odpowiedzi (odpowiedź *nie wiem* też jest poprawna, jendak lepiej zostawić odpowiedź częściowo poprawną)")
            st.write(
                "W drugiej części dostaniesz zestaw odpowiedzi na te same pytania, proszę oceń ich poprawność."
            )
            st.write("Udział jest anonimowy, wyrazajac zgodę na udział, przechodzisz do pierwszej części.")
            st.button("Wyrażam zgodę.", on_click=self.set_state, args=["choose"])

    def final_page(self):
        with st.container():
            st.title("Dziękuję za udział")
            st.write("W razie pytań, proszę o kontakt na email: t.dubowski@student.uw.edu.pl")

    def choose_page(self):
        with st.container():
            st.title("Wybierz tekst, który wolisz przeczytać")
            tab1, tab2 = st.tabs(["Pierwszy tekst", "Drugi tekst"])
            with tab1:
                st.header("O komizmie")
                st.write("Tagi: samopoczucie, styl zycia, filozofia")
                st.button("Wybieram", key="t1", on_click=self.set_state, args=["text1"])

            with tab2:
                st.header("Kocia długowieczność na wyciągnięcie ręki? Nowy lek ma przedłużyć życie kotów")
                st.write("Tagi: biologia, koty, obyczajowe, badania naukowe")
                st.button("Wybieram", key="t2", on_click=self.set_state, args=["text2"])


    def text_page(self, text):
        with st.container():

            timer = st.empty()
            article = st.empty()
            article.markdown(text)
            N = 300
            match st.session_state.page:
                case "text1":
                    st.button(
                        "Przechodzę dalej", on_click=self.set_state, args=["question_page1"]
                    )
                case "text2":
                    st.button(
                        "Przechodzę dalej", on_click=self.set_state, args=["question_page2"]
                    )
        
            for secs in range(N, 0, -1):
                mm, ss = secs // 60, secs % 60
                timer.metric("Pozostały czas", f"{mm:02d}:{ss:02d}")
                time.sleep(1)
            timer.write("")
            article.write("Czas się skończył, proszę przejść dalej")


    def rate_page(self):
        
        result = get_data()
        selected_options = {}
        selected_options["questions_id"] = st.session_state.questions_id
        
        with st.container():
            
            with st.popover("Pokaz arytkuł"):
                article = st.empty()

            if st.session_state.questions_id == "question_page1":
                    article.markdown(self.t_humor)
            else:
                    article.markdown(self.t_koty)
            
            for key, value in islice(result[0].items(), 2, None):
    
                st.subheader(key)
                st.write(f"**Odpowiedź**: {value}")
    
                choice = st.radio(
                    f"Twoja ocena:",
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
                    self.question_page(self.q_humor)

                case "text1":
                    self.text_page(self.t_humor)

                case "question_page2":
                    self.question_page(self.q_koty)

                case "text2":
                    self.text_page(self.t_koty)
                
                case "rate_page":
                    self.rate_page()

                case "final":
                    self.final_page()


if __name__ == "__main__":
    site = SurveySite()
    site.main()
