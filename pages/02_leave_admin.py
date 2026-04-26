import streamlit as st
from utils_auth import get_supabase
import pandas as pd
import smtplib
from email.mime.text import MIMEText


# --- 1. 이메일 발송 함수 ---
def send_approval_email(to_email, name, start_date, end_date, reason):
    """학생에게 상세 승인 정보를 포함한 메일을 발송하는 함수"""
    try:
        smtp_user = st.secrets["smtp_user"]
        smtp_pw = st.secrets["smtp_pw"]

        # 메일 본문 구성 (선생님 요청 서식 반영)
        msg_content = f"""
{name} 학생의 {start_date}자 장기 외박이 승인되었습니다.

- 외박 기간: {start_date} ~ {end_date}
- 사유: {reason}

본 메일은 시스템에서 발송된 자동 발신 메일입니다.
        """

        msg = MIMEText(msg_content)
        msg['Subject'] = f"[남창고] {name} 학생 장기 외박 승인 완료 안내"
        msg['From'] = smtp_user
        msg['To'] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_pw)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"메일 발송 중 오류 발생: {e}")
        return False


# --- 2. 메인 페이지 함수 ---
def leave_admin_page():
    st.header("외박 신청 승인 및 현황 관리")

    # 권한 확인
    user_role = st.session_state.get("user_role")
    if user_role not in ["teacher", "admin"]:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        st.stop()

    supabase = get_supabase()

    # --- [섹션 1] 전체 신청 현황 데이터프레임 ---
    st.subheader("전체 신청 현황")
    try:
        all_res = supabase.table("leave_applications").select("*").order("id", desc=True).execute()
        if all_res.data:
            table_data = []
            for row in all_res.data:
                # 학생 성함 조회
                prof_res = supabase.table("profiles").select("name").eq("student_id", row['student_id']).execute()
                student_name = prof_res.data[0]['name'] if prof_res.data else "미등록"

                # 신청 작성일 한국 시간 변환
                raw_at = row.get('created_at')
                applied_date = "-"
                if raw_at:
                    try:
                        dt = pd.to_datetime(raw_at)
                        dt_korea = dt.tz_convert('Asia/Seoul') if dt.tzinfo else dt.tz_localize('UTC').tz_convert(
                            'Asia/Seoul')
                        applied_date = dt_korea.strftime('%Y-%m-%d')
                    except:
                        applied_date = str(raw_at)[:10]

                status_display = "승인 완료" if row['status'] == 'approved' else "대기 중"

                table_data.append({
                    "학생 정보": f"{row['student_id']} {student_name}",
                    "신청 작성일": applied_date,
                    "외박 시작일": row['start_date'],
                    "외박 종료일": row['end_date'],
                    "사유": row['reason'],
                    "승인 여부": status_display
                })

            df = pd.DataFrame(table_data)
            st.dataframe(
                df[["학생 정보", "신청 작성일", "외박 시작일", "외박 종료일", "사유", "승인 여부"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "사유": st.column_config.TextColumn("사유", width="medium"),
                    "승인 여부": st.column_config.TextColumn("승인 여부", width="small")
                }
            )
        else:
            st.info("현재 기록된 외박 신청 내역이 없습니다.")
    except Exception as e:
        st.error(f"현황표 로드 중 오류: {e}")

    st.divider()

    # --- [섹션 2] 실시간 승인 처리 (Expander 레이아웃) ---
    st.subheader("승인 대기 목록")

    try:
        pending_res = supabase.table("leave_applications").select("*").eq("status", "pending").execute()
        pending_apps = pending_res.data

        if not pending_apps:
            st.success("현재 모든 승인 처리가 완료되었습니다.")
        else:
            st.write(f"처리 대기 건수: {len(pending_apps)}건")

            for app in pending_apps:
                p_info = supabase.table("profiles").select("name, email").eq("student_id", app['student_id']).execute()
                name = p_info.data[0]['name'] if p_info.data else "정보 없음"
                email = p_info.data[0]['email'] if p_info.data else None

                # 신청 일시 한국 시간 변환 (시:분 포함)
                raw_created_at = app.get('created_at')
                applied_dt_display = "-"
                if raw_created_at:
                    try:
                        dt = pd.to_datetime(raw_created_at)
                        dt_korea = dt.tz_convert('Asia/Seoul') if dt.tzinfo else dt.tz_localize('UTC').tz_convert(
                            'Asia/Seoul')
                        applied_dt_display = dt_korea.strftime('%Y-%m-%d %H:%M')
                    except:
                        applied_dt_display = str(raw_created_at)[:16]

                with st.expander(f"{app['student_id']} {name}"):
                    # 요청하신 상세 레이아웃
                    st.write(f"- **신청일시** : {applied_dt_display}")
                    st.write(f"- **외박기간** : {app['start_date']} ~ {app['end_date']}")
                    st.write(f"- **상세 사유** : {app['reason']}")
                    st.write(f"- **학생 이메일** : {email if email else '이메일 정보 없음'}")

                    st.write("")

                    if st.button("최종 승인 및 메일 발송", key=f"app_{app['id']}"):
                        # DB 업데이트
                        supabase.table("leave_applications").update({"status": "approved"}).eq("id",
                                                                                               app['id']).execute()

                        # 메일 발송
                        if email:
                            with st.spinner(f"{name} 학생에게 승인 메일을 발송 중입니다..."):
                                success = send_approval_email(
                                    to_email=email,
                                    name=name,
                                    start_date=app['start_date'],
                                    end_date=app['end_date'],
                                    reason=app['reason']
                                )
                                if success:
                                    st.toast(f"{name} 학생에게 승인 알림을 보냈습니다.")
                                else:
                                    st.warning("메일 발송에 실패했습니다. SMTP 설정을 확인해 주세요.")

                        st.success(f"{name} 학생의 외박 신청을 승인했습니다.")
                        st.rerun()
    except Exception as e:
        st.error(f"승인 처리 섹션 로드 중 오류: {e}")


if __name__ == "__main__":
    leave_admin_page()