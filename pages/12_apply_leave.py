import streamlit as st
from utils_auth import get_supabase
from datetime import date


def apply_leave_page():
    st.header("장기외박 신청")

    # 안내 문구
    st.info("장기 외박신청은 1주일 전 신청 & 장기 외박(5일 이상) 신청해주시기 바랍니다.")

    # 1. 로그인 여부 확인
    if not st.session_state.get("logged_in"):
        st.warning("로그인이 필요한 서비스입니다.")
        st.stop()

    # 2. 세션 초기화 (신청 완료 상태를 추적하기 위함)
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # 3. 화면 분기 처리
    # 신청 완료 상태라면 완료 메시지만 보여줌
    if st.session_state.submitted:
        st.success("외박 신청이 정상적으로 접수되었습니다.")
        st.write("선생님의 승인이 완료되면 안내 메일이 발송될 예정입니다.")

        if st.button("추가 신청하기"):
            st.session_state.submitted = False
            st.rerun()
        return

    # --- 아래는 신청 전: 입력 양식 표시 ---
    user_name = st.session_state.get("user_name", "")
    user_role = st.session_state.get("user_role", "")
    student_id = st.session_state.get("student_id", "")

    if user_role != "student":
        st.info("교직원은 외박 신청 기능을 이용할 수 없습니다. 학생 계정으로 테스트해 주세요.")
        return

    with st.form("leave_form"):
        st.subheader("신청자 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("학번", value=student_id, disabled=True)
        with col2:
            st.text_input("성명", value=user_name, disabled=True)

        st.divider()
        st.subheader("외박 일정 및 사유")

        start_date = st.date_input("외박 시작일", min_value=date.today())
        end_date = st.date_input("외박 종료일", min_value=start_date)
        reason = st.text_area("외박 사유", placeholder="사유를 상세히 입력해 주세요.")

        submit = st.form_submit_button("신청하기")

    if submit:
        if not reason:
            st.error("외박 사유를 입력해 주세요.")
        else:
            supabase = get_supabase()
            try:
                data = {
                    "student_id": student_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "reason": reason,
                    "status": "pending"
                }
                supabase.table("leave_applications").insert(data).execute()

                # 신청 성공 시 상태를 True로 변경
                st.session_state.submitted = True
                st.rerun()  # 화면을 다시 그려서 완료 페이지로 전환

            except Exception as e:
                st.error(f"신청 중 오류 발생: {e}")


if __name__ == "__main__":
    apply_leave_page()