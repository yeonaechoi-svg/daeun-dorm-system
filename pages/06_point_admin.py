import streamlit as st
from utils_auth import get_supabase
import pandas as pd


def point_admin_page():
    st.header("상벌점 관리")

    user_role = st.session_state.get("user_role")
    if user_role not in ["teacher", "admin"]:
        st.error("관리자 권한이 필요합니다.")
        st.stop()

    given_by = st.session_state.get("user_name", "교사")
    supabase = get_supabase()

    tab1, tab2, tab3 = st.tabs(["상벌점 부여", "전체 내역 조회", "항목 관리"])

    # --- [Tab 1] 상벌점 부여 ---
    with tab1:
        st.subheader("학생 상벌점 부여")

        # 학생 목록 로드
        try:
            students_res = supabase.table("students").select("student_id, name").order("student_id").execute()
            students = students_res.data
        except Exception as e:
            st.error(f"학생 목록 로드 오류: {e}")
            st.stop()

        if not students:
            st.warning("등록된 학생이 없습니다. 먼저 명단을 업로드해주세요.")
            st.stop()

        student_options = {f"{s['name']} ({s['student_id']})": s['student_id'] for s in students}

        # 항목 목록 로드
        try:
            cat_res = supabase.table("point_categories").select("*").order("point_type").execute()
            categories = cat_res.data
        except Exception:
            categories = []

        selected_student = st.selectbox("학생 선택", list(student_options.keys()))
        point_type = st.radio("구분", ["상점", "벌점"], horizontal=True)
        type_key = "merit" if point_type == "상점" else "demerit"

        # 항목 드롭다운 (해당 구분 필터) - 폼 밖에서 실시간 반영
        filtered_cats = [c for c in categories if c['point_type'] == type_key]
        cat_names = ["직접 입력"] + [f"{c['name']} ({c['default_points']}점)" for c in filtered_cats]
        selected_cat = st.selectbox("사유 선택", cat_names)

        if selected_cat == "직접 입력":
            reason = st.text_input("사유 직접 입력")
            points = st.number_input("점수", min_value=1, max_value=100, value=1)
        else:
            idx = cat_names.index(selected_cat) - 1
            reason = filtered_cats[idx]['name']
            points = filtered_cats[idx]['default_points']
            st.info(f"사유: {reason}  |  점수: {points}점")

        if st.button("부여하기", type="primary", use_container_width=True):
            if not reason:
                st.error("사유를 입력해주세요.")
            else:
                try:
                    supabase.table("point_records").insert({
                        "student_id": student_options[selected_student],
                        "point_type": type_key,
                        "points": points,
                        "reason": reason,
                        "given_by": given_by,
                    }).execute()
                    st.success(f"✅ {selected_student}에게 {point_type} {points}점 부여 완료!")
                except Exception as e:
                    st.error(f"오류 발생: {e}")

    # --- [Tab 2] 전체 내역 조회 ---
    with tab2:
        st.subheader("전체 상벌점 내역")

        try:
            records_res = supabase.table("point_records").select("*").order("created_at", desc=True).execute()
            records = records_res.data

            if not records:
                st.info("부여된 상벌점 내역이 없습니다.")
            else:
                # 학생 이름 매핑
                name_map = {s['student_id']: s['name'] for s in students}

                df = pd.DataFrame(records)
                df['이름'] = df['student_id'].map(name_map).fillna("정보없음")
                df['구분'] = df['point_type'].map({"merit": "🟢 상점", "demerit": "🔴 벌점"})
                df['날짜'] = df['created_at'].str[:10]
                df_display = df[['이름', 'student_id', '구분', 'points', 'reason', 'given_by', '날짜']].rename(columns={
                    'student_id': '학번', 'points': '점수', 'reason': '사유', 'given_by': '부여교사'
                })

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # 학생별 합계
                st.divider()
                st.subheader("학생별 상벌점 합계")
                merit = df[df['point_type'] == 'merit'].groupby('student_id')['points'].sum()
                demerit = df[df['point_type'] == 'demerit'].groupby('student_id')['points'].sum()
                summary = pd.DataFrame({'상점': merit, '벌점': demerit}).fillna(0).astype(int)
                summary['순점수'] = summary['상점'] - summary['벌점']
                summary.index = summary.index.map(lambda x: f"{name_map.get(x, x)} ({x})")
                st.dataframe(summary, use_container_width=True)

        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")

    # --- [Tab 3] 항목 관리 ---
    with tab3:
        st.subheader("상벌점 항목 관리")

        with st.form("cat_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                cat_name = st.text_input("항목명")
            with col2:
                cat_type = st.radio("구분", ["상점", "벌점"], horizontal=True)
            with col3:
                cat_points = st.number_input("기본 점수", min_value=1, max_value=100, value=1)
            add_btn = st.form_submit_button("항목 추가")

            if add_btn:
                if not cat_name:
                    st.error("항목명을 입력해주세요.")
                else:
                    try:
                        supabase.table("point_categories").insert({
                            "name": cat_name,
                            "point_type": "merit" if cat_type == "상점" else "demerit",
                            "default_points": cat_points,
                        }).execute()
                        st.toast(f"✅ '{cat_name}' 항목이 추가되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

        st.divider()
        try:
            cat_res2 = supabase.table("point_categories").select("*").order("point_type").execute()
            if not cat_res2.data:
                st.info("등록된 항목이 없습니다.")
            else:
                for c in cat_res2.data:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        type_label = "🟢 상점" if c['point_type'] == 'merit' else "🔴 벌점"
                        st.write(f"{type_label}  |  **{c['name']}**  |  {c['default_points']}점")
                    with col2:
                        if st.button("삭제", key=f"del_cat_{c['id']}"):
                            supabase.table("point_categories").delete().eq("id", c['id']).execute()
                            st.rerun()
                    st.divider()
        except Exception as e:
            st.error(f"항목 로드 오류: {e}")


if __name__ == "__main__":
    point_admin_page()
