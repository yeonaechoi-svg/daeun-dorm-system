import streamlit as st
from utils_auth import get_supabase
from datetime import date
import pandas as pd


def apply_leave_page():
    st.header("장기외박 신청")

    # 안내 문구
    st.info("장기 외박신청은 1주일 전 신청 & 장기 외박(5일 이상) 신청해주시기 바랍니다.")

    # 1. 로그인 여부 확인
    if not st.session_state.get("logged_in"):
        st.warning("로그인이 필요한 서비스입니다.")
        st.stop()

    supabase = get_supabase()
    user_name = st.session_state.get("user_name", "")
    user_role = st.session_state.get("user_role", "")
    student_id = st.session_state.get("student_id", "")

    if user_role != "student":
        st.info("교직원은 외박 신청 기능을 이용할 수 없습니다. 학생 계정으로 테스트해 주세요.")
        return

    # --- [섹션 1] 외박 신청 양식 영역 ---
    # 신청 완료 여부 세션 상태 (해당 브라우저 세션 동안만 유지)
    submit_key = f"submitted_{student_id}"
    if submit_key not in st.session_state:
        st.session_state[submit_key] = False

    if st.session_state[submit_key]:
        st.success("✅ 외박 신청이 완료되었습니다.")
        if st.button("새로 신청하기"):
            st.session_state[submit_key] = False
            st.rerun()
    else:
        with st.expander("📝 새 외박 신청하기", expanded=True):
            with st.form("leave_form", clear_on_submit=True):
                st.subheader("외박 일정 및 사유")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("외박 시작일", min_value=date.today())
                with col2:
                    end_date = st.date_input("외박 종료일", min_value=start_date)

                reason = st.text_area("외박 사유", placeholder="사유를 상세히 입력해 주세요.")
                submit = st.form_submit_button("신청하기")

            if submit:
                if not reason:
                    st.error("외박 사유를 입력해 주세요.")
                else:
                    try:
                        data = {
                            "student_id": student_id,
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "reason": reason,
                            "status": "pending"
                        }
                        supabase.table("leave_applications").insert(data).execute()
                        st.session_state[submit_key] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"신청 중 오류 발생: {e}")

    st.divider()

    # --- [섹션 2] 나의 신청 현황 확인 영역 (항상 표시됨) ---
    st.subheader("📅 나의 외박 신청 현황")

    try:
        # 로그인 시점에 상관없이 DB에서 해당 학생의 데이터를 항상 불러옴
        response = supabase.table("leave_applications") \
            .select("*") \
            .eq("student_id", student_id) \
            .order("created_at", desc=True) \
            .execute()

        applications = response.data

        if not applications:
            st.info("현재 신청 내역이 없습니다.")
        else:
            df = pd.DataFrame(applications)
            # 화면에 보여줄 컬럼 설정
            display_cols = ['start_date', 'end_date', 'reason', 'status', 'created_at']
            df_display = df[display_cols].copy()
            df_display.columns = ['시작일', '종료일', '사유', '상태', '신청일시']

            # 상태(status)를 한글 및 이모지로 변환
            status_map = {
                "pending": "⏳ 대기",
                "approved": "✅ 승인",
                "rejected": "❌ 반려"
            }
            df_display['상태'] = df_display['상태'].map(status_map)

            # 데이터프레임 출력
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption("※ 최근 신청한 내역부터 정렬되어 표시됩니다.")

    except Exception as e:
        st.error(f"현황 데이터를 불러오는 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    apply_leave_page()