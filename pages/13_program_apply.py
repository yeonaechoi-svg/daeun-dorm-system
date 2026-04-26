import streamlit as st
from utils_auth import get_supabase
import datetime

def program_apply_page():
    st.header("기숙사 프로그램 신청")

    # 세션에서 기본 정보 로드
    s_id = st.session_state.get("student_id", "")
    s_name = st.session_state.get("user_name", "")

    # 1. 학번 및 2. 이름 기입 (수정 불가)
    col1, col2 = st.columns(2)
    student_id = col1.text_input("1. 학번", value=s_id, disabled=True)
    student_name = col2.text_input("2. 이름", value=s_name, disabled=True)

    supabase = get_supabase()
    today = str(datetime.date.today())

    # 신청 기간 내 프로그램 조회
    try:
        res = supabase.table("programs").select("*").lte("start_date", today).gte("end_date", today).execute()
        programs = res.data

        if not programs:
            st.warning("현재 신청 가능한 프로그램이 없습니다.")
        else:
            st.info(" 아래 프로그램의 내용을 확인하고 신청해 주세요.")
            for p in programs:
                # [수정] expanded=True 옵션을 추가하여 기본적으로 펼쳐진 상태로 표시
                with st.expander(f" {p['title']} (신청마감: {p['end_date'][:10]}까지)", expanded=True):
                    st.write(f"**상세내용:**")
                    st.info(p['description']) # 내용을 강조하기 위해 info 박스 사용
                    st.write(f"**모집인원:** {p['max_participants']}명")

                    # 3. 신청 여부 - 체크박스
                    is_apply = st.checkbox("신청하시겠습니까? (√ 체크)", key=f"chk_{p['id']}")

                    if st.button("신청하기", key=f"btn_{p['id']}"):
                        if not is_apply:
                            st.error("신청 여부(√ 체크)에 체크를 해주세요.")
                        elif not s_id:
                            st.error("로그인 정보가 없습니다. 다시 로그인해 주세요.")
                        else:
                            signup_data = {"program_id": p['id'], "student_id": s_id}

                            try:
                                res_apply = supabase.table("program_signups").insert(signup_data).execute()
                                if res_apply.data:
                                    st.success(f"'{p['title']}' 신청이 완료되었습니다!")
                            except Exception:
                                st.warning("이미 신청한 프로그램입니다.")
    except Exception as e:
        st.error(f"데이터 로드 중 오류: {e}")

if __name__ == "__main__":
    program_apply_page()