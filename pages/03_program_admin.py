import streamlit as st
from utils_auth import get_supabase
import pandas as pd


def program_admin_page():
    st.header("기숙사 프로그램 개설 및 관리")

    user_role = st.session_state.get("user_role")
    if user_role not in ["teacher", "admin"]:
        st.error("관리자 권한이 필요합니다.")
        st.stop()

    supabase = get_supabase()

    tab1, tab2 = st.tabs(["새 프로그램 등록", "개설 프로그램 및 신청 명단"])

    with tab1:
        with st.form("program_reg_form", clear_on_submit=True):
            title = st.text_input("1. 체험 프로그램 명")
            desc = st.text_area("2. 체험 프로그램 상세 내용")
            max_p = st.number_input("3. 모집인원", min_value=1, value=20)

            st.write("4. 신청 기간 설정")
            col1, col2 = st.columns(2)
            s_date = col1.date_input("신청 시작일")
            e_date = col2.date_input("신청 마감일")

            if st.form_submit_button("프로그램 등록"):
                data = {
                    "title": title,
                    "description": desc,
                    "start_date": str(s_date),
                    "end_date": str(e_date),
                    "max_participants": max_p
                }
                res = supabase.table("programs").insert(data).execute()
                if res.data:
                    st.success(f"'{title}' 프로그램이 등록되었습니다.")
                    st.rerun()

    with tab2:
        st.subheader("개설 프로그램 관리")
        # 등록된 프로그램 전체 조회
        res = supabase.table("programs").select("*").order("id", desc=True).execute()

        if not res.data:
            st.info("개설된 프로그램이 없습니다.")
        else:
            for p in res.data:
                # 프로그램별 Expander 생성
                with st.expander(f"📋 {p['title']} (신청기간: {p['start_date'][:10]} ~ {p['end_date'][:10]})"):
                    st.write(f"**상세내용:** {p['description']}")
                    st.write(f"**모집정원:** {p['max_participants']}명")

                    # 해당 프로그램의 신청 명단 조회 (JOIN 형태)
                    # program_signups 테이블에서 이 프로그램 ID와 일치하는 데이터 가져오기
                    signup_res = supabase.table("program_signups").select("*").eq("program_id", p['id']).execute()

                    if not signup_res.data:
                        st.warning("아직 신청한 학생이 없습니다.")
                    else:
                        st.write(f"**현재 신청 인원:** {len(signup_res.data)}명")

                        # 학생 상세 정보를 포함한 리스트 생성
                        student_list = []
                        for s in signup_res.data:
                            # profiles 테이블에서 학생 이름 가져오기
                            p_res = supabase.table("profiles").select("name").eq("student_id",
                                                                                 s['student_id']).execute()
                            s_name = p_res.data[0]['name'] if p_res.data else "정보 없음"

                            student_list.append({
                                "학번": s['student_id'],
                                "이름": s_name,
                                "신청시간": pd.to_datetime(s['signup_time']).tz_convert('Asia/Seoul').strftime(
                                    '%Y-%m-%d %H:%M')
                            })

                        # 데이터프레임으로 표시
                        df_students = pd.DataFrame(student_list)
                        st.dataframe(df_students, use_container_width=True, hide_index=True)

                        # (선택 사항) 엑셀/CSV 다운로드 기능
                        csv = df_students.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="명단 다운로드 (CSV)",
                            data=csv,
                            file_name=f"{p['title']}_신청명단.csv",
                            mime="text/csv",
                            key=f"dl_{p['id']}"
                        )

                    # 프로그램 삭제 버튼 (필요 시)
                    if st.button("프로그램 삭제", key=f"del_{p['id']}", help="해당 프로그램과 모든 신청 내역이 삭제됩니다."):
                        supabase.table("programs").delete().eq("id", p['id']).execute()
                        st.rerun()


if __name__ == "__main__":
    program_admin_page()