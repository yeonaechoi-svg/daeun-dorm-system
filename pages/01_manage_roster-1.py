import streamlit as st
import pandas as pd
from utils_auth import get_supabase


def manage_roster():
    st.header("학생 명단 업로드 및 관리", anchor=False)
    st.write("교사 권한: 엑셀 파일을 업로드하여 기숙사생 명단을 일괄 등록합니다.")

    # 1. 파일 업로더
    uploaded_file = st.file_uploader("학생 명단 엑셀 파일을 선택하세요 (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("업로드 데이터 미리보기:")
            st.dataframe(df.head(), use_container_width=True)

            # 필수 컬럼 확인 (SQL 설계 기준)
            required_cols = ["student_id", "name", "gender", "grade"]
            if all(col in df.columns for col in required_cols):
                if st.button("DB에 명단 저장하기"):
                    supabase = get_supabase()

                    # 데이터 전처리: 학번을 문자열로 변환
                    df['student_id'] = df['student_id'].astype(str)

                    # 업로드할 레코드 생성 (NaN 값은 None으로 처리하여 에러 방지)
                    records = df.where(pd.notnull(df), None).to_dict(orient='records')

                    with st.spinner("데이터 업로드 중..."):
                        # student_id가 중복될 경우 기존 데이터를 업데이트(Upsert)
                        supabase.table("students").upsert(records, on_conflict="student_id").execute()

                    st.success(f"총 {len(records)}명의 명단이 성공적으로 등록되었습니다.")
            else:
                st.error(f"엑셀 컬럼명이 일치하지 않습니다. 필수 포함 컬럼: {required_cols}")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    st.divider()

    # 2. 현재 DB에 저장된 명단 보기
    if st.button("현재 등록된 명단 불러오기"):
        supabase = get_supabase()
        res = supabase.table("students").select("*").order("student_id").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        else:
            st.info("등록된 학생 데이터가 없습니다.")


if __name__ == "__main__":
    manage_roster()