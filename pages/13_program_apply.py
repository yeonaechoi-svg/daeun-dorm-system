import streamlit as st
from utils_auth import get_supabase
import datetime
import pandas as pd


def program_apply_page():
    st.header("기숙사 프로그램 신청 및 현황")

    # 세션에서 기본 정보 로드
    s_id = st.session_state.get("student_id", "")
    s_name = st.session_state.get("user_name", "")

    if not s_id:
        st.warning("로그인 정보가 없습니다. 다시 로그인해 주세요.")
        st.stop()

    supabase = get_supabase()
    today_date = datetime.date.today()
    today_str = str(today_date)

    # 탭 구성: 신청하기 / 나의 신청 현황
    tab1, tab2 = st.tabs(["🌟 프로그램 신청", "📅 나의 신청 현황"])

    # --- [Tab 1] 프로그램 신청 ---
    with tab1:
        st.subheader("모집 중인 프로그램")

        # 신청 기간(start_date ~ end_date) 내에 있는 프로그램 조회
        try:
            res = supabase.table("programs") \
                .select("*") \
                .lte("start_date", today_str) \
                .gte("end_date", today_str) \
                .order("id", desc=True) \
                .execute()
            programs = res.data

            # 내가 이미 신청한 프로그램 ID 목록 가져오기 (중복 체크용)
            res_my = supabase.table("program_signups").select("program_id").eq("student_id", s_id).execute()
            my_signup_ids = [item['program_id'] for item in res_my.data]

            if not programs:
                st.info("현재 신청 가능한 프로그램이 없습니다.")
            else:
                for p in programs:
                    is_already_signed_up = p['id'] in my_signup_ids

                    # 카드 형태로 표시
                    expander_label = f"📌 {p['title']} {'(✅ 신청완료)' if is_already_signed_up else ''}"
                    with st.expander(expander_label, expanded=not is_already_signed_up):
                        st.info(f"**상세내용:**\n\n{p['description']}")

                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.write(f"**신청마감:** {p['end_date']}")
                            st.write(f"**취소마감:** :red[{p.get('cancel_deadline', '미설정')}]")
                        with col_info2:
                            # 현재 인원 실시간 조회
                            count_res = supabase.table("program_signups").select("id", count="exact").eq("program_id",
                                                                                                         p[
                                                                                                             'id']).execute()
                            current_count = count_res.count if count_res.count is not None else 0
                            st.write(f"**모집인원:** {current_count} / {p['max_participants']} 명")

                        if is_already_signed_up:
                            st.success("이미 신청이 완료된 프로그램입니다. '나의 신청 현황' 탭에서 확인하세요.")
                        else:
                            # 신청 체크박스 및 버튼
                            is_apply = st.checkbox("위 내용을 확인했으며 신청에 동의합니다.", key=f"chk_{p['id']}")
                            if st.button("신청하기", key=f"btn_{p['id']}", use_container_width=True):
                                if not is_apply:
                                    st.error("신청 동의 체크박스에 체크해 주세요.")
                                elif current_count >= p['max_participants']:
                                    st.error("죄송합니다. 모집 인원이 마감되었습니다.")
                                else:
                                    signup_data = {"program_id": p['id'], "student_id": s_id}
                                    supabase.table("program_signups").insert(signup_data).execute()
                                    st.success(f"'{p['title']}' 신청이 완료되었습니다!")
                                    st.rerun()
        except Exception as e:
            st.error(f"데이터 로드 중 오류: {e}")

    # --- [Tab 2] 나의 신청 현황 및 취소 ---
    with tab2:
        st.subheader(f"🎓 {s_name} 학생의 신청 내역")

        try:
            # 내 신청 정보와 프로그램 정보를 조인하여 가져오기
            res_my_list = supabase.table("program_signups") \
                .select("id, signup_time, programs(id, title, cancel_deadline)") \
                .eq("student_id", s_id) \
                .execute()

            my_signups = res_my_list.data

            if not my_signups:
                st.info("아직 신청한 프로그램이 없습니다.")
            else:
                for item in my_signups:
                    p_info = item['programs']
                    p_title = p_info['title']
                    c_deadline_str = p_info.get('cancel_deadline')

                    # 취소 가능 여부 체크
                    can_cancel = False
                    if c_deadline_str:
                        c_deadline_date = datetime.date.fromisoformat(c_deadline_str)
                        if today_date <= c_deadline_date:
                            can_cancel = True

                    # 현황 카드 표시
                    with st.container():
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.write(f"**{p_title}**")
                            st.caption(f"신청일시: {item['signup_time'][:16].replace('T', ' ')}")
                            st.caption(f"취소 가능 마감일: {c_deadline_str if c_deadline_str else '정보 없음'}")

                        with c2:
                            if can_cancel:
                                if st.button("신청 취소", key=f"cancel_{item['id']}", type="secondary"):
                                    supabase.table("program_signups").delete().eq("id", item['id']).execute()
                                    st.toast(f"'{p_title}' 취소 완료")
                                    st.rerun()
                            else:
                                st.write(":grey[취소 불가]")
                                st.caption("(기한 만료)")
                        st.divider()

        except Exception as e:
            st.error(f"현황 조회 중 오류 발생: {e}")


if __name__ == "__main__":
    program_apply_page()