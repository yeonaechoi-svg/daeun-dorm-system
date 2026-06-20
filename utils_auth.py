import streamlit as st
from supabase import create_client, Client


# 1. Supabase 연결 초기화 (앱 실행 중 한 번만 연결)
@st.cache_resource
def get_supabase() -> Client:
    """
    secrets.toml의 정보를 사용하여 Supabase 클라이언트를 생성합니다.
    """
    try:
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error("Supabase 연결 설정(secrets.toml)을 확인해주세요.")
        raise e


# 2. 로그인 함수
def sign_in(email, password):
    """
    이메일/비밀번호로 Supabase Auth에 로그인을 시도합니다.
    """
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        # 로그인 실패 시 에러 메시지 반환
        return str(e)


# 3. 사용자 프로필 및 권한 가져오기
def get_user_profile(user_id):
    """
    profiles 테이블에서 사용자의 이름과 역할(role)을 가져옵니다.
    """
    supabase = get_supabase()
    try:
        # DB의 profiles 테이블에서 id가 일치하는 행 1개를 가져옴
        result = supabase.table("profiles").select("role, name, student_id, child_name").eq("id", user_id).single().execute()
        return result.data
    except Exception:
        return None


# 4. 로그아웃 처리
def sign_out():
    """
    세션을 정리하고 앱을 초기 상태로 되돌립니다.
    """
    supabase = get_supabase()
    supabase.auth.sign_out()

    # 세션 상태 초기화
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_info = None

    st.rerun()


# 5. 권한 확인용 도구 (데코레이터 대용)
def check_permission(allowed_roles):
    """
    현재 사용자가 허용된 권한을 가졌는지 확인합니다.
    사용 예시: if not check_permission(["admin", "teacher"]): st.stop()
    """
    if not st.session_state.get("logged_in"):
        return False
    return st.session_state.get("user_role") in allowed_roles


# utils_auth.py 파일에 추가해야 할 내용

def logout():
    """
    Supabase 로그아웃을 처리하고 세션 상태를 초기화합니다.
    """
    supabase = get_supabase()
    supabase.auth.sign_out()

    # 스트림릿 세션 상태 초기화
    if "authenticated" in st.session_state:
        st.session_state.authenticated = False
    if "logged_in" in st.session_state:
        st.session_state.logged_in = False
    if "user_info" in st.session_state:
        st.session_state.user_info = None
    if "user_name" in st.session_state:
        st.session_state.user_name = ""
    if "user_role" in st.session_state:
        st.session_state.user_role = None