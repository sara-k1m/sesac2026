import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

## .env 파일에서 OPENAI_API_KEY를 부분 
load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

## client 객체 생성
client = OpenAI()
MODEL = "gpt-4o-mini"

st.title("💬 간단한 챗봇")

question = st.chat_input("질문을 입력하세요.")

if question:
    # user: 사용자가 입력한 질문
    with st.chat_message("user"):
        st.write(question)

    ## AI 모델에 질문을 보내고 답변을 받는 부분
    response = client.responses.create(
        model=MODEL,
        input =question,
    )

    # assistant: AI가 생성한 답변
    with st.chat_message("assistant"):
        ## AI 모델의 답변을 출력하는 부분
        st.write(response.output_text)