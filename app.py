#!/usr/bin/env python
# coding: utf-8


import streamlit as st
from streamlit_javascript import st_javascript
import pandas as pd
from datetime import datetime
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === 인증 설정 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key("1GzHvQUcgFqlUnyBOT2udLcHjslFjsMazlGPIUIDGG14").sheet1

# === 앱 UI 초기화 ===
st.set_page_config(page_title="지도교수님 메시지", layout="centered")
st.title("📨 황승식 교수님께 감사 메시지 남기기")

# === 위치 수집 시도
st.info("📍 브라우저 위치 권한을 요청합니다. 허용하지 않아도 메시지 저장은 가능합니다.")
coords = st_javascript("navigator.geolocation.getCurrentPosition((pos) => pos.coords);")

# === 위치 정보 처리
if isinstance(coords, dict) and coords.get("latitude") is not None:
    lat = coords["latitude"]
    lon = coords["longitude"]
    st.success(f"📌 위치 확인됨: {lat:.4f}, {lon:.4f}")
else:
    # 북한 내 무작위 좌표 생성
    lat = round(random.uniform(37.5, 43.0), 6)
    lon = round(random.uniform(124.0, 130.5), 6)
    st.warning(f"⚠️ 위치 정보를 사용할 수 없습니다. 북한 내 무작위 좌표가 사용됩니다: {lat}, {lon}")

# === 메시지 입력 폼
with st.form("message_form"):
    name = st.text_input("이름 (선택)", "")
    level = st.selectbox("소속 과정", ["석사", "박사"])
    message = st.text_area("메시지를 작성해 주세요 (100자 이내)", max_chars=100)
    submit = st.form_submit_button("메시지 보내기")

# === 메시지 저장
if submit:
    if message.strip() == "":
        st.warning("메시지를 입력해 주세요.")
    else:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name if name else "익명",
            level,
            message,
            lat,
            lon
        ]
        sheet.append_row(row)
        st.success("메시지가 구글 시트에 저장되었습니다. 감사합니다 💐")
