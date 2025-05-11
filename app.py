#!/usr/bin/env python
# coding: utf-8


import streamlit as st
from streamlit_javascript import st_javascript
import pandas as pd
from datetime import datetime
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

# === 브라우저 위치 요청 ===
st.info("📍 현재 위치 정보를 수집 중입니다. 브라우저 위치 권한을 허용해 주세요.")
coords = st_javascript("navigator.geolocation.getCurrentPosition((pos) => pos.coords);")

# === 위치 권한이 있을 때만 처리 ===
if isinstance(coords, dict) and coords.get("latitude") is not None:
    lat = coords["latitude"]
    lon = coords["longitude"]
    st.success(f"📌 위치 확인됨: {lat:.4f}, {lon:.4f}")

    # 메시지 입력
    with st.form("message_form"):
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
    st.warning("⚠️ 위치 정보를 사용할 수 없습니다. 브라우저 주소창의 🔒 아이콘을 눌러 위치 권한을 허용해 주세요.")
    if st.button("🔁 위치 다시 요청"):
        st.rerun()
