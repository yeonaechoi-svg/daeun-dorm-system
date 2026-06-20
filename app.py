import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="남창고 대운학사 관리 시스템",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 사이드바 그라데이션 (연한 라벤더 → 연한 블루) */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #C9B8F5 0%, #B8D4F5 100%) !important;
    }

    /* 사이드바 전체 텍스트 진한 남보라 */
    [data-testid="stSidebar"] * {
        color: #1E1040 !important;
    }

    /* 네비게이션 링크 흰색 카드 버튼 스타일 */
    [data-testid="stSidebarNavLink"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 10px !important;
        margin: 3px 8px !important;
        padding: 8px 14px !important;
        box-shadow: 0 1px 4px rgba(92, 75, 180, 0.12) !important;
        font-weight: 600 !important;
        color: #1E1040 !important;
        transition: all 0.2s ease !important;
    }

    /* 메뉴 호버 효과 */
    [data-testid="stSidebarNavLink"]:hover {
        background-color: rgba(255, 255, 255, 1) !important;
        box-shadow: 0 3px 8px rgba(92, 75, 180, 0.22) !important;
        transform: translateX(3px) !important;
    }

    /* 활성 메뉴 강조 */
    [data-testid="stSidebarNavLink"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 3px 10px rgba(92, 75, 180, 0.3) !important;
        border-left: 4px solid #6C5CE7 !important;
        font-weight: 700 !important;
        color: #4A2C8F !important;
    }

    /* 페이지 제목 (h1) 강조색 */
    h1 {
        color: #4A2C8F !important;
        border-bottom: 3px solid #6C5CE7;
        padding-bottom: 8px;
    }

    /* 섹션 제목 (h2, h3) */
    h2, h3 {
        color: #5B4FCF !important;
    }

    /* 구분선 강조색 */
    hr {
        border-color: #6C5CE7 !important;
    }

    /* 상단 여백 축소 */
    .block-container {
        padding-top: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

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
home_page = st.Page("pages/home.py", title="🏠 홈", default=True)

# 교사(관리자)용 메뉴
manage_roster = st.Page("pages/01_manage_roster.py", title="📋 명단 관리")
manage_leave = st.Page("pages/02_leave_admin.py", title="🌙 외박 신청 관리")
manage_program = st.Page("pages/03_program_admin.py", title="🎯 프로그램 관리")
manage_notice = st.Page("pages/04_notice_admin.py", title="📢 공지사항 관리")
manage_point = st.Page("pages/06_point_admin.py", title="⭐ 상벌점 관리")

# 공통 메뉴
view_calendar = st.Page("pages/10_calendar.py", title="📅 달력")

# 학생용 메뉴
apply_leave = st.Page("pages/12_apply_leave.py", title="🌙 장기외박 신청")
apply_program = st.Page("pages/13_program_apply.py", title="🎯 프로그램 신청")
view_notice = st.Page("pages/11_notice.py", title="📢 공지사항")
view_point = st.Page("pages/14_point_view.py", title="⭐ 나의 상벌점")

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
st.title("남창고등학교 대운학사 관리 시스템")
pg.run()