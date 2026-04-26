import streamlit as st

st.set_page_config(page_title="룸메이트 배치", layout="wide")
st.title("룸메이트 자동 배치 시스템")
st.write("성별, 학년, 희망 조건을 바탕으로 생활실을 배치합니다.")

if st.button("자동 배치 알고리즘 실행"):
    st.info("알고리즘을 가동합니다... (데이터 로드 중)")

st.table({"호실": ["101호", "102호"], "배정 학생": ["김철수, 이영희", "박민수, 최다은"]})