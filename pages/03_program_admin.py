import streamlit as st
from utils_auth import get_supabase
import pandas as pd


def program_admin_page():
    # 1. 페이지 제목 및 보안 확인
    st.header("기숙사 프로그램 개설 및 관리")

    user_role = st.session_state.get("user_role")
    if user_role not in ["teacher", "admin"]:
        st.error("관리자 권한이 필요합니다.")
        st.stop()

    supabase = get_supabase()

    # 2. 탭 구성
    tab1, tab2 = st.tabs(["새 프로그램 등록", "개설 프로그램 및 신청 명단"])

    # --- [Tab 1] 새 프로그램 등록 ---
    with tab1:
        # clear_on_submit=True를 통해 등록 후 입력창을 자동으로 비웁니다.
        with st.form("program_reg_form", clear_on_submit=True):
            st.subheader(" 프로그램 정보 입력")
            title = st.text_input("1. 체험 프로그램 명")
            desc = st.text_area("2. 체험 프로그램 상세 내용")
            max_p = st.number_input("3. 모집인원", min_value=1, value=20)

            st.write("4. 일정 및 기간 설정")
            col1, col2, col3 = st.columns(3)
            with col1:
                s_date = st.date_input("신청 시작일")
            with col2:
                e_date = st.date_input("신청 마감일")
            with col3:
                c_date = st.date_input("취소 가능 마감일", help="학생들이 직접 취소를 할 수 있는 최종 기한입니다.")

            submit_button = st.form_submit_button("프로그램 등록")

            if submit_button:
                if not title:
                    st.error("프로그램 명을 입력해 주세요.")
                else:
                    try:
                        data = {
                            "title": title,
                            "description": desc,
                            "start_date": str(s_date),
                            "end_date": str(e_date),
                            "cancel_deadline": str(c_date),
                            "max_participants": max_p
                        }
                        res = supabase.table("programs").insert(data).execute()
                        if res.data:
                            # 등록 즉시 성공 메시지 표시 (Tab 2에 갔다와도 이 메시지는 사라집니다)
                            st.success(f"✅ '{title}' 프로그램이 성공적으로 등록되었습니다.")
                            st.balloons()
                            # st.rerun()을 하지 않아야 성공 메시지가 현재 화면에 유지됩니다.
                    except Exception as e:
                        st.error(f"등록 중 오류 발생: {e}")

    # --- [Tab 2] 개설 프로그램 및 신청 명단 ---
    with tab2:
        st.subheader("📋 개설 프로그램 관리")
        try:
            # DB에서 프로그램 목록 최신순 조회
            res = supabase.table("programs").select("*").order("id", desc=True).execute()

            if not res.data:
                st.info("현재 개설된 프로그램이 없습니다.")
            else:
                for p in res.data:
                    # 날짜 데이터 처리 (None 값 대응)
                    raw_deadline = p.get('cancel_deadline')
                    cancel_info = str(raw_deadline)[:10] if raw_deadline else "미설정"

                    raw_start = p.get('start_date')
                    start_info = str(raw_start)[:10] if raw_start else "미설정"

                    raw_end = p.get('end_date')
                    end_info = str(raw_end)[:10] if raw_end else "미설정"

                    # 프로그램별 Expander
                    expander_title = f"📦 {p['title']} (신청: {start_info} ~ {end_info})"
                    with st.expander(expander_title):
                        st.write(f"**상세설명:** {p['description']}")
                        st.write(f"**취소 마감일:** :red[{cancel_info}]")
                        st.write(f"**모집 정원:** {p['max_participants']}명")

                        st.divider()

                        # --- 신청 학생 명단 조회 섹션 ---
                        signup_res = supabase.table("program_signups").select("*").eq("program_id", p['id']).execute()

                        if not signup_res.data:
                            st.warning("현재 신청한 학생이 없습니다.")
                        else:
                            st.write(f"**현재 신청 인원:** {len(signup_res.data)}명")
                            student_list = []
                            for s in signup_res.data:
                                # 학생 이름 매칭 (profiles 테이블)
                                p_res = supabase.table("profiles").select("name").eq("student_id",
                                                                                     s['student_id']).execute()
                                s_name = p_res.data[0]['name'] if p_res.data else "정보 없음"

                                student_list.append({
                                    "학번": s['student_id'],
                                    "이름": s_name,
                                    "신청시간": pd.to_datetime(s['signup_time']).tz_convert('Asia/Seoul').strftime(
                                        '%Y-%m-%d %H:%M')
                                })

                            df_students = pd.DataFrame(student_list)
                            st.dataframe(df_students, use_container_width=True, hide_index=True)

                            # 명단 다운로드
                            csv = df_students.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label="📥 명단 다운로드 (CSV)",
                                data=csv,
                                file_name=f"{p['title']}_신청명단.csv",
                                mime="text/csv",
                                key=f"dl_{p['id']}"
                            )

                        # 프로그램 삭제 버튼
                        if st.button("🗑️ 프로그램 삭제", key=f"del_{p['id']}", help="해당 프로그램과 모든 신청 기록이 삭제됩니다."):
                            supabase.table("programs").delete().eq("id", p['id']).execute()
                            st.rerun()

        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")


if __name__ == "__main__":
    program_admin_page()