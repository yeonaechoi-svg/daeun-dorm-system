import streamlit as st
from utils_auth import get_supabase
import pandas as pd


def point_view_page():
    st.header("나의 상벌점 현황")

    s_id = st.session_state.get("student_id", "")
    s_name = st.session_state.get("user_name", "")

    if not s_id:
        st.warning("로그인 정보가 없습니다. 다시 로그인해 주세요.")
        st.stop()

    supabase = get_supabase()

    try:
        res = supabase.table("point_records").select("*").eq("student_id", s_id).order("created_at", desc=True).execute()
        records = res.data

        # 합계 계산
        merit_total = sum(r['points'] for r in records if r['point_type'] == 'merit')
        demerit_total = sum(r['points'] for r in records if r['point_type'] == 'demerit')
        net = merit_total - demerit_total

        # 요약 카드
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 상점 합계", f"{merit_total}점")
        col2.metric("🔴 벌점 합계", f"{demerit_total}점")
        col3.metric("순점수", f"{net}점", delta=net)

        st.divider()

        if not records:
            st.info("아직 부여된 상벌점이 없습니다.")
        else:
            st.subheader(f"{s_name} 학생 상벌점 내역")
            df = pd.DataFrame(records)
            df['구분'] = df['point_type'].map({"merit": "🟢 상점", "demerit": "🔴 벌점"})
            df['날짜'] = df['created_at'].str[:10]
            df_display = df[['날짜', '구분', 'points', 'reason', 'given_by']].rename(columns={
                'points': '점수', 'reason': '사유', 'given_by': '부여교사'
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")


if __name__ == "__main__":
    point_view_page()
