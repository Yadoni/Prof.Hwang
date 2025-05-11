#!/usr/bin/env python
# coding: utf-8


import streamlit as st
from streamlit_javascript import st_javascript
import pandas as pd
from datetime import datetime
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_folium import st_folium
import folium
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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
st.title("\U0001F4E8 황승식 교수님께 감사 메시지 남기기")

# === 위치 수집 시도
st.info("\U0001F4CD 브라우저 위치 권한을 요청합니다. 허용하지 않아도 메시지 저장은 가능합니다.")
coords = st_javascript("navigator.geolocation.getCurrentPosition((pos) => pos.coords);")

# === 위치 정보 처리
if isinstance(coords, dict) and coords.get("latitude") is not None:
    lat = coords["latitude"]
    lon = coords["longitude"]
    st.success(f"\U0001F4CC 위치 확인됨: {lat:.4f}, {lon:.4f}")
else:
    sea_areas = {
        "남해": {"lat": (33.0, 34.5), "lon": (126.0, 129.5)},
        "동해": {"lat": (36.0, 38.5), "lon": (129.5, 131.5)},
        "서해": {"lat": (34.5, 37.5), "lon": (124.5, 126.5)}
    }
    selected_sea = random.choice(list(sea_areas.keys()))
    sea = sea_areas[selected_sea]
    lat = round(random.uniform(*sea["lat"]), 6)
    lon = round(random.uniform(*sea["lon"]), 6)
    st.warning(f"\U0001F30A 위치 정보를 사용할 수 없습니다. {selected_sea} 바다 위 무작위 좌표가 사용됩니다: {lat}, {lon}")

# === 메시지 입력 폼
with st.form("message_form"):
    name = st.text_input("이름 (익명 가능)", "")
    level = st.selectbox("level", ["재학생", "졸업생", "휴학생"])
    message = st.text_area("메시지를 작성해 주세요 (100자 이내)", max_chars=100)
    submit = st.form_submit_button("메시지 보내기")

# === 메시지 저장
if submit:
    if message.strip() == "":
        st.warning("메시지를 입력해 주세요.")
    else:
        row = [
            datetime.now().strftime("%Y-%m-%d"),
            name if name else "익명",
            level,
            message,
            lat,
            lon
        ]
        sheet.append_row(row)
        st.success("메시지가 구글 시트에 저장되었습니다. 감사합니다 \U0001F490")

# === 실시간 데이터 로딩
records = sheet.get_all_records()
df = pd.DataFrame(records)

# === 지도 시각화
st.subheader("🗺️ 메시지 지도")
map_center = [df["lat"].mean(), df["lon"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

for _, row in df.iterrows():
    color = "blue" if row["level"] == "재학생" else ("green" if row["level"] == "휴학생" else "red")
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"{row['name']} ({row['level']}): {row['message']}",
        icon=folium.Icon(color=color)
    ).add_to(m)

st_folium(m, width=700, height=500)

# === 통계 차트
st.subheader("📊 level별 메시지 수")
st.bar_chart(df["level"].value_counts())

# === 워드클라우드
st.subheader("☁️ 메시지 워드클라우드")

if not df["message"].empty:
    text = " ".join(df["message"].astype(str))

    wc = WordCloud(
        font_path="NanumGothic.ttf",  # ✔ 여기서 나눔고딕 폰트 사용
        background_color="white",
        width=800,
        height=400
    ).generate(text)

    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)
else:
    st.info("메시지가 아직 없습니다.")
