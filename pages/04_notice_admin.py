import streamlit as st
from utils_auth import get_supabase
import datetime


def notice_admin_page():
    st.header("공지사항 관리")

    user_role = st.session_state.get("user_role")
    if user_role not in ["teacher", "admin"]:
        st.error("관리자 권한이 필요합니다.")
        st.stop()

    author_name = st.session_state.get("user_name", "관리자")
    supabase = get_supabase()

    tab1, tab2 = st.tabs(["새 공지 작성", "공지 목록 관리"])

    # --- [Tab 1] 새 공지 작성 ---
    with tab1:
        with st.form("notice_form", clear_on_submit=True):
            st.subheader("공지사항 작성")
            title = st.text_input("제목")
            content = st.text_area("내용", height=200)
            is_pinned = st.checkbox("상단 고정", help="체크 시 공지 목록 최상단에 고정됩니다.")
            submit = st.form_submit_button("등록하기")

            if submit:
                if not title or not content:
                    st.error("제목과 내용을 모두 입력해 주세요.")
                else:
                    try:
                        data = {
                            "title": title,
                            "content": content,
                            "author_name": author_name,
                            "is_pinned": is_pinned,
                        }
                        res = supabase.table("notices").insert(data).execute()
                        if res.data:
                            st.success(f"✅ '{title}' 공지가 등록되었습니다.")
                    except Exception as e:
                        st.error(f"등록 중 오류 발생: {e}")

    # --- [Tab 2] 공지 목록 관리 ---
    with tab2:
        st.subheader("등록된 공지사항")
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
                        st.divider()

                        col1, col2 = st.columns(2)
                        with col1:
                            # 고정/고정해제 토글
                            current_pin = notice.get("is_pinned", False)
                            pin_btn_label = "고정 해제" if current_pin else "상단 고정"
                            if st.button(pin_btn_label, key=f"pin_{notice['id']}"):
                                supabase.table("notices").update({"is_pinned": not current_pin}).eq("id", notice["id"]).execute()
                                st.rerun()
                        with col2:
                            if st.button("🗑️ 삭제", key=f"del_{notice['id']}"):
                                supabase.table("notices").delete().eq("id", notice["id"]).execute()
                                st.rerun()

        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")


if __name__ == "__main__":
    notice_admin_page()
