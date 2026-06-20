import streamlit as st
from utils_auth import get_supabase


def notice_page():
    st.header("공지사항")

    if not st.session_state.get("logged_in"):
        st.warning("로그인이 필요합니다.")
        st.stop()

    supabase = get_supabase()

    try:
        res = supabase.table("notices").select("*").order("is_pinned", desc=True).order("created_at", desc=True).execute()

        if not res.data:
            st.info("등록된 공지사항이 없습니다.")
        else:
            for notice in res.data:
                pin_label = "📌 " if notice.get("is_pinned") else ""
                created_at = notice.get("created_at", "")[:10]
                expander_title = f"{pin_label}{notice['title']}  |  {notice['author_name']}  |  {created_at}"

                with st.expander(expander_title):
                    st.write(notice["content"])

    except Exception as e:
        st.error(f"공지사항을 불러오는 중 오류 발생: {e}")


if __name__ == "__main__":
    notice_page()
