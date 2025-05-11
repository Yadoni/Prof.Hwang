#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.write("Secrets loaded:", list(st.secrets.keys()))
# === Google Sheets 인증 설정 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ✅ secrets.toml에서 환경변수 가져오기
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scope
)
client = gspread.authorize(creds)

# === 시트 열기 ===
sheet = client.open("professor_messages").sheet1  # 시트 이름 확인 필요

# === IP 기반 위치 자동 수집 ===
try:
    res = requests.get("https://ipinfo.io/json").json()
    lat, lon = map(float, res["loc"].split(','))
    location_available = True
except:
    st.warning("위치 정보를 자동으로 불러올 수 없습니다.")
    location_available = False

# === 앱 UI ===
st.set_page_config(page_title="지도교수님 메시지", layout="centered")
st.title("📨 황승식 교수님께 감사 메시지 남기기")

if location_available:
    with st.form(key="message_form"):
        name = st.text_input("이름 (선택)", "")
        level = st.selectbox("소속 과정", ["석사", "박사"])
        message = st.text_area("메시지를 작성해 주세요 (100자 이내)", max_chars=100)
        submit = st.form_submit_button("메시지 보내기")

    if submit:
        if message.strip() == "":
            st.warning("메시지를 입력해 주세요.")
        else:
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   name if name else "익명",
                   level,
                   message,
                   lat,
                   lon]
            sheet.append_row(row)
            st.success("메시지가 구글 시트에 저장되었습니다. 감사합니다 💐")
else:
    st.error("위치 정보가 없어 메시지를 보낼 수 없습니다. VPN 또는 인터넷 설정을 확인해 주세요.")
