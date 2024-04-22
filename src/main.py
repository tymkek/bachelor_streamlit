import json
import streamlit as st
import numpy as np
import pandas as pd
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

load_dotenv()


class SurveySite:
    def __init__(self):
        # self.input_text = input_text
        # self.messages = [
        # {"role": "system", "content": 'You will be given a text, generate 5 questions based on that text, response should be written in json format. Save both question and answer'
        # },
        # {"role": "user", "content": f'This is the mentioned text: {input_text}'},
        # ]
        with open("./config/books_questions.json", "r") as file:
            self.q_books = json.load(file)
        with open("./config/sigma_questions.json", "r") as file:
            self.q_sigma = json.load(file)
        with open("./config/books.txt", "r") as file:
            self.t_books = file.read()
        with open("./config/sigma.txt", "r") as file:
            self.t_sigma = file.read()

    # def generate_questions(self):

    #     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #     response = client.chat.completions.create(
    #     model=self.gpt_model,
    #     messages=self.messages,
    #     temperature=0
    #     )
    #     with open("sample2.json", "w") as outfile:
    #             json.dump(response.choices[0].message.content, outfile)

    #     return(response.choices[0].message.content)

    def set_state(self, state):
        st.session_state.page = state

    def set_questions(self, filename):
        print("1")

        with open(filename, "r") as file:
            q = json.load(file)
        self.questions = q

    def set_callback(self, state, filename):
        self.set_state(state)
        self.set_questions(filename)

    def question_page(self, questions):
        with st.container():
            ans_dict = {}
            for q in questions["questions"]:
                ans = st.text_area(q["question"])
                if ans:
                    ans_dict[q["question"]] = ans

            with open("sample.json", "w") as outfile:
                json.dump(ans_dict, outfile)

            st.button("Submit answers", on_click=self.set_state, args=["final"])

    def home_page(self):
        with st.container():
            st.title("Experiment")
            st.write("You will be given 4 texts to choose from")
            st.write("After choosing one, you will have 5 minutes to read it")
            st.write(
                "In the last stage, 5 question will be generated to chosen text, answer them as best as you can"
            )
            st.write("By pressing the button, you agree to participate in experiment")
            st.button("Next", on_click=self.set_state, args=["choose"])

    def final_page(self):
        with st.container():
            st.title("Thanks for participation")

    def choose_page(self):
        with st.container():
            tab1, tab2, tab3, tab4 = st.tabs(["Text 1", "Text 2", "Text 3", "Text 4"])
            with tab1:
                st.header("The truth about sigma males")
                st.write("A tale of toxic masculinity and romanticising loneliness")
                st.button("Choose", key="t1", on_click=self.set_state, args=["text1"])

            with tab2:
                st.header("Reading Books Is Useless: Here's a Better Way to Read")
                st.button("Choose", key="t2", on_click=self.set_state, args=["text2"])

            with tab3:
                st.header("text 3")
                st.button("Choose", key="t3", on_click=self.set_state, args=["text1"])

            with tab4:
                st.header("text 4")
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

            # if st.session_state.page == 'text1':
            #     print("Hello")
            #     self.set_state('question_page1')
            #     print(st.session_state.page)
            # if st.session_state.page == 'text2':
            #     self.set_state('question_page2')
            # if st.session_state.page == 'text3':
            #     self.set_state('question_page3')
            # if st.session_state.page == 'text4':
            #     self.set_state('question_page4')

    # def cooldown_page(self):
    #     with st.container():
    #         st.write("SIEMa")
    #         # countdown = st.empty()
    #         N = 5
    #         for secs in range(N,0,-1):
    #             mm, ss = secs//60, secs%60
    #             # countdown.metric("Text appears in: ", f"{mm:02d}:{ss:02d}")
    #             time.sleep(1)
    #         self.set_state('home')
    #         st.empty()

    def main(self):

        if "page" not in st.session_state:
            st.session_state.page = "home"

        with st.empty():

            print(st.session_state.page)

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

                case "final":
                    self.final_page()

            # if st.session_state.page == 'home':
            #         self.home_page()

            # if st.session_state.page == 'choose':
            #         self.choose_page()

            # if st.session_state.page == 'text1':
            #         self.text_page(self.t_sigma)

            # if st.session_state.page == 'question_page1':
            #         self.question_page(self.q_sigma)

            # if st.session_state.page == 'text2':
            #         self.text_page(self.t_books)

            # if st.session_state.page == 'question_page2':
            #         self.question_page(self.q_books)

            # if st.session_state.page == 'cooldown':
            #         self.cooldown_page()

            # if st.session_state.page == 'final':
            #         self.final_page()
            # print(st.session_state.page)


if __name__ == "__main__":
    site = SurveySite()
    site.main()
