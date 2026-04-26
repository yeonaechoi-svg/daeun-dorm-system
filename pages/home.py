# pages/home.py
import streamlit as st

# 사이드바에서 이미 정보를 보여주고 있지만, 홈 화면 중앙에도 환영 인사를 띄워줍니다.
st.title("남창고등학교 대운학사 관리 시스템")

# 세션에서 이름과 역할을 가져옵니다. (없을 경우를 대비해 기본값 설정)
user_name = st.session_state.get("user_name", "사용자")
user_role = st.session_state.get("user_role", "유저")

# 역할에 따른 명칭 설정 (학부모 제거)
role_display = ""
if user_role in ["admin", "teacher"]:
    role_display = "선생님"
else:
    role_display = "학생"

st.write(f"### 환영합니다, **{user_name} {role_display}**!")
st.divider()

# 홈 화면에 간단한 가이드나 공지사항을 추가할 수 있습니다.
st.info("왼쪽 사이드바 메뉴를 이용해 원하는 기능을 선택해 주세요.")

if user_role in ["admin", "teacher"]:
    st.write("🏅 **교사용 빠른 안내**")
    st.write("- 학생 명단이 아직 없다면 **[명단 업로드/관리]** 메뉴를 먼저 이용해 주세요.")
    st.write("- 외박 신청 현황 및 프로그램 관리는 관리자 메뉴에서 확인 가능합니다.")
else:
    st.write("🎓 **학생 빠른 안내**")
    st.write("- 장기외박 신청은 매주 지정된 시간까지 완료해 주세요.")
    st.write("- 신청한 프로그램의 일시와 장소를 반드시 확인하시기 바랍니다.")
    st.write("- 기타 문의 사항은 사감실로 방문해 주세요.")