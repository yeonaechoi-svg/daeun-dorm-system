import streamlit as st
from utils_auth import get_supabase
import datetime

try:
    from streamlit_calendar import calendar as st_calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


def calendar_page():
    st.header("기숙사 일정 달력")

    if not st.session_state.get("logged_in"):
        st.warning("로그인이 필요합니다.")
        st.stop()

    if not CALENDAR_AVAILABLE:
        st.error("streamlit-calendar 패키지가 설치되지 않았습니다. `.venv\\Scripts\\pip.exe install streamlit-calendar` 후 재시작하세요.")
        st.stop()

    user_role = st.session_state.get("user_role")
    supabase = get_supabase()

    # --- 이벤트 데이터 수집 ---
    calendar_events = []

    # 1. 프로그램 일정 (파란색)
    try:
        prog_res = supabase.table("programs").select("*").execute()
        for p in prog_res.data:
            start = p.get("start_date", "")[:10]
            end = p.get("end_date", "")[:10]
            if start:
                end_exclusive = str(datetime.date.fromisoformat(end) + datetime.timedelta(days=1)) if end else start
                calendar_events.append({
                    "title": f"[프로그램] {p['title']}",
                    "start": start,
                    "end": end_exclusive,
                    "color": "#3788d8",
                })
    except Exception as e:
        st.warning(f"프로그램 일정 로드 오류: {e}")

    # 2. 학사 일정 (초록색)
    try:
        event_res = supabase.table("events").select("*").execute()
        for ev in event_res.data:
            start = ev.get("start_date", "")[:10]
            end = ev.get("end_date", "")[:10]
            end_exclusive = str(datetime.date.fromisoformat(end) + datetime.timedelta(days=1)) if end else start
            calendar_events.append({
                "title": ev["title"],
                "start": start,
                "end": end_exclusive,
                "color": ev.get("color", "#2ecc71"),
            })
    except Exception as e:
        st.warning(f"학사 일정 로드 오류: {e}")

    # --- 달력 표시 ---
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek",
        },
        "initialView": "dayGridMonth",
        "locale": "ko",
        "height": 600,
        "buttonText": {
            "today": "오늘",
            "month": "월",
            "week": "주",
        },
    }

    st_calendar(events=calendar_events, options=calendar_options)

    # --- 범례 ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🔵 **프로그램 신청 기간**")
    with col2:
        st.markdown("🟢 **학사 일정**")

    # --- 교사 전용: 학사 일정 관리 ---
    if user_role in ["teacher", "admin"]:
        st.divider()
        st.subheader("학사 일정 관리")

        tab1, tab2 = st.tabs(["일정 추가", "일정 목록/삭제"])

        with tab1:
            with st.form("event_form", clear_on_submit=True):
                title = st.text_input("일정 제목")
                desc = st.text_area("설명 (선택)", height=80)
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("시작일")
                with col2:
                    end_date = st.date_input("종료일")
                color = st.color_picker("색상", value="#2ecc71")
                submit = st.form_submit_button("일정 추가")

                if submit:
                    if not title:
                        st.error("일정 제목을 입력해 주세요.")
                    elif end_date < start_date:
                        st.error("종료일이 시작일보다 앞설 수 없습니다.")
                    else:
                        try:
                            supabase.table("events").insert({
                                "title": title,
                                "start_date": str(start_date),
                                "end_date": str(end_date),
                                "description": desc,
                                "color": color,
                            }).execute()
                            st.success(f"✅ '{title}' 일정이 추가되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"추가 중 오류 발생: {e}")

        with tab2:
            try:
                ev_res = supabase.table("events").select("*").order("start_date").execute()
                if not ev_res.data:
                    st.info("등록된 학사 일정이 없습니다.")
                else:
                    for ev in ev_res.data:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{ev['title']}**  |  {ev['start_date']} ~ {ev.get('end_date', ev['start_date'])}")
                            if ev.get("description"):
                                st.caption(ev["description"])
                        with col2:
                            if st.button("삭제", key=f"del_ev_{ev['id']}"):
                                supabase.table("events").delete().eq("id", ev["id"]).execute()
                                st.rerun()
                        st.divider()
            except Exception as e:
                st.error(f"데이터 로드 오류: {e}")


if __name__ == "__main__":
    calendar_page()
