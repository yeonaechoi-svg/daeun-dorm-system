import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="남창고 대운학사 관리 시스템",
    layout="wide"
)

# 2. 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""

# 3. 페이지 정의 (이모티콘 icon 제거)
login_page = st.Page("pages/login.py", title="로그인")
join_page = st.Page("pages/join_membership.py", title="회원가입")
home_page = st.Page("pages/home.py", title="홈", default=True)

# 교사(관리자)용 메뉴
manage_roster = st.Page("pages/01_manage_roster.py", title="명단 업로드/관리")
manage_leave = st.Page("pages/02_leave_admin.py", title="외박 신청 관리")
manage_program = st.Page("pages/03_program_admin.py", title="프로그램 관리")
manage_notice = st.Page("pages/04_notice_admin.py", title="공지사항 관리")
manage_point = st.Page("pages/06_point_admin.py", title="상벌점 관리")
#room_assign = st.Page("pages/05_room_assign.py", title="룸메이트 배치")

# 공통 메뉴
view_calendar = st.Page("pages/10_calendar.py", title="달력")

# 학생용 메뉴
apply_leave = st.Page("pages/12_apply_leave.py", title="장기외박 신청")
apply_program = st.Page("pages/13_program_apply.py", title="프로그램 신청")
view_notice = st.Page("pages/11_notice.py", title="공지사항")
view_point = st.Page("pages/14_point_view.py", title="나의 상벌점")

# 4. 네비게이션 구성
if st.session_state.logged_in:
    # 사이드바 상단 사용자 정보 표시 (글자 크기로 위계 설정)
    user_name = st.session_state.user_name
    user_role = st.session_state.user_role

    st.sidebar.markdown(f"## {user_name} 님")  # 큰 글씨

    if user_role in ["teacher", "admin"]:
        #st.sidebar.markdown("#### [ 관리자 모드 ]")  # 중간 글씨
        st.sidebar.info("🏅 관리자 권한 접속 중")
        st.sidebar.divider()  # 구분선 추가

        # 주메뉴 이름을 굵고 크게 하여 하위메뉴와 구분
        pg = st.navigation({
            "메인": [home_page],
            "공통": [view_calendar],
            "교사 관리자 메뉴": [manage_roster, manage_leave, manage_program, manage_notice, manage_point]
        })
    else:
        #st.sidebar.markdown("#### [ 학생 모드 ]")
        st.sidebar.info("🎓 학생 권한 접속 중")
        st.sidebar.divider()

        pg = st.navigation({
            "메인": [home_page],
            "공통": [view_calendar],
            "학생 메뉴": [apply_leave, apply_program, view_notice, view_point]
        })

    # 로그아웃 버튼 (하단 배치)
    st.sidebar.write("")  # 간격 띄우기
    if st.sidebar.button("로그아웃", use_container_width=True):
        from utils_auth import logout

        logout()
        st.rerun()
else:
    # 로그인 전 메뉴 (이모티콘 제거)
    pg = st.navigation({
        "로그인/가입": [login_page, join_page]
    })

# 5. 시스템 가동
pg.run()