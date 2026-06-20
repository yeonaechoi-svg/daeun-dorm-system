import streamlit as st
from utils_auth import get_supabase


def login():
    st.title("남창고등학교 대운학사 관리 시스템")
    st.header("로그인")
    st.write("학사 관리 시스템 접속을 위해 로그인해 주세요.")

    with st.form("login_form"):
        email = st.text_input("이메일", placeholder="example@email.com")
        password = st.text_input("비밀번호", type="password")
        submit_button = st.form_submit_button("로그인")

    if submit_button:
        if email and password:
            supabase = get_supabase()
            try:
                # 1. Supabase Auth 인증
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})

                if res.user:
                    # 2. profiles 테이블에서 상세 정보(이름, 역할, 학번) 가져오기
                    profile = supabase.table("profiles").select("*").eq("id", res.user.id).single().execute()

                    if profile.data:
                        # 3. ★ 핵심: app.py가 사용할 세션 변수에 값 주입 ★
                        st.session_state.logged_in = True
                        st.session_state.user_name = profile.data.get("name", "사용자")
                        st.session_state.user_role = profile.data.get("role", "student")
                        st.session_state.student_id = profile.data.get("student_id", "")

                        st.success(f"{st.session_state.user_name}님, 환영합니다!")
                        st.rerun()  # app.py를 다시 실행시켜 메뉴를 바꾸게 함
                else:
                    st.error("이메일 또는 비밀번호가 올바르지 않습니다.")
            except Exception as e:
                st.error("로그인에 실패했습니다. 정보를 다시 확인하세요.")
        else:
            st.warning("이메일과 비밀번호를 모두 입력해 주세요.")

    st.divider()
    if st.button("계정이 없으신가요? 회원가입하기"):
        st.switch_page("pages/join_membership.py")


if __name__ == "__main__":
    login()