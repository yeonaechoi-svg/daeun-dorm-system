import streamlit as st
import re
from utils_auth import get_supabase


def check_password_strength(password):
    """
    비밀번호 복잡성 검사 함수 (8~16자, 3가지 이상 조합)
    """
    # 1. 길이 검사
    if not (8 <= len(password) <= 16):
        return False, "비밀번호는 8자에서 16자 사이여야 합니다."

    # 2. 조합 종류 계산 (영문 대문자, 소문자, 숫자, 특수문자)
    count = 0
    if re.search("[a-z]", password): count += 1  # 소문자 포함 시 +1
    if re.search("[A-Z]", password): count += 1  # 대문자 포함 시 +1
    if re.search("[0-9]", password): count += 1  # 숫자 포함 시 +1
    if re.search("[!@#$%^&*(),.?\":{}|<>]", password): count += 1  # 특수문자 포함 시 +1

    # 3. 3가지 이상 조합 여부 확인
    if count < 3:
        return False, "영문 대소문자, 숫자, 특수문자 중 3가지 이상을 조합해야 합니다."

    return True, ""


def join_membership():
    st.title("남창고등학교 대운학사 관리 시스템")
    st.header("회원가입")
    st.write("사용자 정보를 입력하여 계정을 생성해 주세요.")

    if "join_success" not in st.session_state:
        st.session_state.join_success = False

    if not st.session_state.join_success:
        st.subheader("사용자 유형 선택")
        user_type = st.radio(
            "본인에게 해당하는 유형을 선택하세요",
            ["학생", "교사"],
            horizontal=True
        )
        st.divider()

        with st.form("join_form", clear_on_submit=False):
            st.subheader(f"{user_type} 정보 입력")

            # 1. 공통 정보 입력
            email = st.text_input("이메일 주소 (ID)", placeholder="nshs@example.com")

            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input(
                    "비밀번호",
                    type="password",
                    placeholder="영문 대소문자/숫자/특수문자 중 3가지 이상 조합, 8~16자",
                    help="영문 대문자, 소문자, 숫자, 특수문자 중 3가지 이상을 조합하여 8~16자로 입력하세요."
                )
            with col2:
                password_confirm = st.text_input(
                    "비밀번호 확인",
                    type="password",
                    placeholder="비밀번호 재입력"
                )

            name = st.text_input("이름 (본인 성함)")

            # 2. 유형별 추가 정보 입력
            student_id = None
            admin_code_input = ""

            if user_type == "학생":
                student_id = st.text_input("학번을 입력하세요 (예: 10101)")
            elif user_type == "교사":
                admin_code_input = st.text_input("교사 인증 코드를 입력하세요", type="password")

            st.divider()
            submit_button = st.form_submit_button("가입 신청")

            if submit_button:
                # 필수 항목 체크
                if not (email and password and password_confirm and name):
                    st.warning("모든 항목을 입력해 주세요.")

                # 비밀번호 일치 체크
                elif password != password_confirm:
                    st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")

                else:
                    # 비밀번호 강도 및 조합 체크
                    is_strong, msg = check_password_strength(password)
                    if not is_strong:
                        st.error(msg)
                        st.stop()

                    supabase = get_supabase()
                    role = "student"

                    # --- 본인 인증 로직 ---
                    if user_type == "학생":
                        if not student_id:
                            st.error("학번을 입력해주세요.")
                            st.stop()

                        # 명단 대조
                        student_check = supabase.table("students") \
                            .select("*") \
                            .eq("student_id", student_id) \
                            .eq("name", name) \
                            .execute()

                        if not student_check.data:
                            st.error("등록된 학생 명단에서 정보를 찾을 수 없습니다. 학번과 이름을 다시 확인하세요.")
                            st.stop()

                    elif user_type == "교사":
                        master_code = st.secrets.get("admin_code")
                        if admin_code_input != master_code:
                            st.error("교사 인증 코드가 올바르지 않습니다.")
                            st.stop()
                        role = "teacher"

                    # --- 계정 생성 ---
                    try:
                        auth_res = supabase.auth.sign_up({"email": email, "password": password})

                        if auth_res.user:
                            profile_data = {
                                "id": auth_res.user.id,
                                "email": email,
                                "name": name,
                                "role": role,
                                "student_id": student_id if role == "student" else None
                            }
                            supabase.table("profiles").upsert(profile_data).execute()

                            st.session_state.join_success = True
                            st.rerun()
                    except Exception as e:
                        if "already registered" in str(e):
                            st.error("이미 등록된 이메일입니다.")
                        else:
                            st.error(f"가입 중 오류 발생: {e}")

        if st.button("로그인 화면으로 돌아가기"):
            st.switch_page("pages/login.py")

    else:
        # 가입 성공 시 화면
        st.success("회원가입이 완료되었습니다.")
        if st.button("지금 로그인하기"):
            st.session_state.join_success = False
            st.switch_page("pages/login.py")


if __name__ == "__main__":
    join_membership()