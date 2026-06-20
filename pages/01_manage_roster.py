import os

# [중요] 판다스가 보안에 걸리는 pyarrow를 아예 찾지 않도록 최상단에서 차단
os.environ["PANDAS_ARROW_ENABLED"] = "0"

import streamlit as st
import pandas as pd
import numpy as np
from utils_auth import get_supabase


def manage_roster():
    st.header("학생 명단 업로드 및 관리", anchor=False)
    st.write("교사 권한: CSV 또는 엑셀 파일을 업로드하여 명단을 등록합니다.")

    # 1. 파일 업로더
    uploaded_file = st.file_uploader("명단 파일을 선택하세요 (.csv 또는 .xlsx)", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # 파일 확장자에 따라 읽기 엔진을 보안에 안전한 방식으로 지정
            if uploaded_file.name.endswith('.csv'):
                # engine='python'을 명시하여 pyarrow 없이 텍스트 방식으로 읽음
                df = pd.read_csv(uploaded_file, engine='python')
            else:
                # 엑셀은 기본 openpyxl 엔진 사용
                df = pd.read_excel(uploaded_file, engine='openpyxl')

            st.write("업로드 데이터 미리보기:")
            st.dataframe(df.head(), use_container_width=True)

            required_cols = ["student_id", "name", "gender", "grade"]
            if all(col in df.columns for col in required_cols):
                if st.button("DB에 명단 저장하기"):
                    supabase = get_supabase()

                    # 데이터 전처리: 학번 문자열 변환 및 결측치 처리
                    df['student_id'] = df['student_id'].astype(str)
                    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

                    records = df.to_dict(orient='records')

                    with st.spinner("데이터 업로드 중..."):
                        # upsert를 사용하여 중복 학번은 업데이트, 새 학번은 추가
                        supabase.table("students").upsert(records, on_conflict="student_id").execute()

                    st.success(f"총 {len(records)}명의 명단이 성공적으로 등록되었습니다.")
            else:
                st.error(f"컬럼명이 일치하지 않습니다. 필수 포함 컬럼: {required_cols}")

        except Exception as e:
            # pyarrow 관련 에러가 발생하더라도 구체적인 원인을 파악하기 위해 출력
            st.error(f"오류 발생: {e}")

    st.divider()

    # 2. 현재 DB에 저장된 명단 보기
    # 집에서 올리신 명단이 여기서 보인다면 학교 노트북의 보안을 성공적으로 우회한 것입니다.
    if st.button("현재 등록된 명단 불러오기"):
        try:
            supabase = get_supabase()
            res = supabase.table("students").select("*").order("student_id").execute()

            if res.data:
                st.write("현재 등록된 학생 명단:")
                # 불러온 데이터를 데이터프레임으로 변환하여 출력
                display_df = pd.DataFrame(res.data)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("등록된 학생 데이터가 없습니다.")
        except Exception as e:
            st.error(f"명단 불러오기 중 오류 발생: {e}")


if __name__ == "__main__":
    manage_roster()