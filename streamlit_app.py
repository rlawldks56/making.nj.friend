# -*- coding: utf-8 -*-
"""
능친 만들기 - Streamlit 웹 버전
인터넷 주소로 접속해서 사용할 수 있습니다.
"""

import streamlit as st
import random
from datetime import datetime
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정 — Streamlit 규칙상 맨 먼저 호출
st.set_page_config(
    page_title="🌸 능친 만들기 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit Cloud: Secrets에 firebase 키가 있으면 실데이터, 없으면 테스트 모드
try:
    from firebase_manager import FirebaseManager
    from config import FIREBASE_TEST_MODE
    _cred_dict = None
    try:
        if hasattr(st, "secrets") and st.secrets.get("firebase"):
            _cred_dict = dict(st.secrets["firebase"])
    except Exception:
        pass
    _fm = FirebaseManager(test_mode=FIREBASE_TEST_MODE, credential_dict=_cred_dict)
except Exception as e:
    st.warning(f"Firebase 연결 실패: {e}. 테스트 모드로 진행합니다.")
    try:
        _fm = FirebaseManager(test_mode=True)
    except Exception:
        _fm = None

# 커스텀 스타일
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #FF9AAC; text-align: center; margin: 2rem 0; }
    .sub-header { font-size: 1.2rem; color: #FFB5C5; text-align: center; margin-bottom: 2rem; }
    .stButton>button { background-color: #FFB5C5; color: white; border-radius: 25px; padding: 0.5rem 2rem; }
    .stButton>button:hover { background-color: #FF9AAC; color: white; }
    div[data-testid="stVerticalBlock"] > div { padding: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"
if "profile_data" not in st.session_state:
    st.session_state.profile_data = None
if "mbti_answers" not in st.session_state:
    st.session_state.mbti_answers = []
if "mbti_step" not in st.session_state:
    st.session_state.mbti_step = 0

MBTI_QUESTIONS = [
    {"q": "시험이 끝난 후 귀사하였다. 기숙사에 왔을 때 나는?", "a": ["시험도 끝났는데 놀아야지!! 애들 방으로 놀러가야지~~", "애들이랑 노는 것도 좋지만 오늘은 혼자 쉬어야지 침대와 몰아일체!"], "t": ["E", "I"]},
    {"q": "기숙사 방을 옮기고 새로 세팅을 할 때 나는?", "a": ["있는 그대로 사용한다. 필요한 거만 쓰면 되지", "나만의 취향과 생활습관에 맞춰서 효율적으로 세팅해야지."], "t": ["S", "N"]},
    {"q": "친구가 시험을 망쳤다고 울고 있다. 이때 나는?", "a": ["속상했겠다ㅠㅠ 다음엔 더 잘할 수 있을거야!!", "너가 더 노력하면 다음에 더 잘되겠지 일단 에쏠부터 가자"], "t": ["F", "T"]},
    {"q": "시험 일주일 전!! 이때 나의 상태는?", "a": ["한건 많은 것 같은데 플래너는 텅 비었음..", "내일 플래너까지 세워져 있고 앞으로의 계획이 완벽!!"], "t": ["P", "J"]},
]
MBTI_DESC = {
    "ENFP": "능주 핵인싸, 기숙사 복도만 걸어도 친구생김", "ENTP": "공부하다가 창업 아이템 생각해냄",
    "ESFP": "쉬는 시간 = 복도 런웨이", "ESTP": "공부? 일단 이것만 보고",
    "INFP": "계획은 잘 세움, 실천은 내일", "INFJ": "조용한데 친해지면 투머치토커",
    "ISFP": "방 꾸미기에 진심, 자기 혼자 인스타 감성", "ISTP": "무심한 해결사, 기숙사 맥가이버",
    "INTP": "단어 외우다가 존재 이유에 대해 고민함", "INTJ": "시험계획은 3주 전에 완성, 실천도 함",
    "ISTJ": "매일 같은 루틴으로 삶, 루틴 깨지면 멘붕", "ESTJ": "자습 때 말하는 애들이 세상에서 제일 싫음",
    "ENFJ": "기숙사 엄마상, 찾았다 우리엄마", "ESFJ": "우리 반 분위기는 내가 책임진다.",
    "ISFJ": "쟤 청소 진짜 열심히 한다. 에서 쟤", "ENTJ": "실행력 10000%"
}

def firebase():
    return _fm

def render_start():
    st.markdown('<p class="main-header">🌸 능친 만들기 🌸</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">당신의 특별한 인연을 찾아보세요</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("START", use_container_width=True):
            st.session_state.page = "login_options"
            st.rerun()

def render_login_options():
    st.markdown('<p class="main-header">💝 능친 만들기 💝</p>', unsafe_allow_html=True)
    if st.button("기존 프로필로 로그인"):
        st.session_state.page = "login"
        st.rerun()
    if st.button("새 프로필 만들기"):
        st.session_state.page = "privacy"
        st.rerun()

def render_login():
    st.markdown("### 프로필 로그인")
    name = st.text_input("이름", placeholder="본인 이름")
    nickname = st.text_input("별명", placeholder="기존 별명")
    insta = st.text_input("인스타그램 아이디", placeholder="@아이디", value="@")
    if insta and not insta.startswith("@"):
        insta = "@" + insta
    if st.button("로그인"):
        if not (name and nickname and insta and insta != "@"):
            st.error("이름, 별명, 인스타 아이디를 모두 입력해주세요.")
        else:
            fb = firebase()
            if not fb:
                st.error("데이터베이스 연결이 없습니다.")
            else:
                users = fb.get_all_users()
                insta_clean = insta.replace("@", "").lower()
                match = next((u for u in users if (u.get("nickname") or "").lower() == nickname.lower() and (u.get("instagram") or "").lower() == insta_clean and (u.get("name") or "").lower() == name.lower()), None)
                if match:
                    st.session_state.profile_data = {
                        "user_id": match.get("user_id"), "nickname": match.get("nickname"), "instagram": match.get("instagram", ""),
                        "grade": match.get("grade"), "gender": match.get("gender"), "mbti": match.get("mbti"), "name": match.get("name")
                    }
                    st.session_state.page = "home"
                    st.success("로그인되었습니다!")
                    st.rerun()
                else:
                    st.error("일치하는 프로필이 없습니다.")
    if st.button("← 뒤로"):
        st.session_state.page = "login_options"
        st.rerun()

def render_privacy():
    st.markdown("### 개인정보 이용 동의")
    st.info("""
    귀하의 소중한 개인정보를 수집·이용하고자 개인정보보호법에 따라 동의를 받습니다.
    본인의 개인정보 제공에 동의하시겠습니까?
    개인정보는 친구 매칭 목적으로만 사용됩니다.
    """)
    if st.button("동의"):
        st.session_state.page = "signup"
        st.rerun()
    if st.button("비동의"):
        st.warning("서비스 이용이 불가합니다.")
        if st.button("← 뒤로가기"):
            st.session_state.page = "login_options"
            st.rerun()

def render_signup():
    st.markdown("### 프로필 입력")
    gender = st.radio("성별", ["남자", "여자"], horizontal=True)
    grade = st.radio("학년", ["1학년", "2학년", "3학년"], horizontal=True)
    name = st.text_input("이름", placeholder="본인 이름")
    nickname = st.text_input("별명", placeholder="별명")
    insta = st.text_input("인스타그램 아이디", placeholder="@아이디", value="@")
    if insta and not insta.startswith("@"):
        insta = "@" + insta
    if st.button("별명 중복 확인") and nickname:
        fb = firebase()
        if fb and fb.check_nickname_exists(nickname):
            st.error("이미 사용 중인 별명입니다.")
        else:
            st.success("사용 가능한 별명입니다.")
    if st.button("다음 (MBTI 테스트)"):
        if not (name and nickname and insta and insta != "@"):
            st.error("이름, 별명, 인스타 아이디를 모두 입력해주세요.")
        else:
            st.session_state.temp_profile = {"gender": gender, "grade": grade, "name": name, "nickname": nickname, "instagram": insta}
            st.session_state.mbti_answers = []
            st.session_state.mbti_step = 0
            st.session_state.page = "mbti"
            st.rerun()
    if st.button("← 뒤로"):
        st.session_state.page = "privacy"
        st.rerun()

def render_mbti():
    step = st.session_state.mbti_step
    if step >= len(MBTI_QUESTIONS):
        mbti = "".join(st.session_state.mbti_answers)
        desc = MBTI_DESC.get(mbti, "알 수 없는 유형")
        st.success(f"당신의 MBTI: **{mbti}**")
        st.info(desc)
        if st.button("확인하고 프로필 저장"):
            tp = st.session_state.temp_profile
            tp["mbti"] = mbti
            fb = firebase()
            if fb:
                pd = {
                    "gender": tp["gender"], "grade": tp["grade"].replace("학년", ""),
                    "nickname": tp["nickname"], "instagram": tp["instagram"].replace("@", ""),
                    "mbti": mbti, "name": tp["name"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                uid = fb.save_profile(pd)
                if uid:
                    st.session_state.profile_data = {**pd, "user_id": uid, "instagram": pd["instagram"], "grade": pd["grade"]}
                    st.session_state.page = "home"
                    st.rerun()
            else:
                st.error("저장 실패")
        return
    q = MBTI_QUESTIONS[step]
    st.markdown(f"### {step+1}/{len(MBTI_QUESTIONS)} {q['q']}")
    idx = st.radio("선택", range(2), format_func=lambda i: q["a"][i], key=f"mbti_{step}")
    if st.button("다음"):
        st.session_state.mbti_answers.append(q["t"][idx])
        st.session_state.mbti_step += 1
        st.rerun()

def render_home():
    pd = st.session_state.profile_data
    if not pd:
        st.session_state.page = "start"
        st.rerun()
        return
    st.markdown("### ✨ 환영합니다! ✨")
    st.markdown(f"💝 **{pd.get('name','')}님**  |  📷 @{pd.get('instagram','')}  |  🎭 {pd.get('mbti','')}")
    st.markdown("---")
    if st.button("💝 친구 찾기"):
        st.session_state.page = "matching"
        st.rerun()
    if st.button("💌 나에게 온 알림"):
        st.session_state.page = "notifications"
        st.rerun()
    if st.button("💕 매칭된 친구"):
        st.session_state.page = "matched_friends"
        st.rerun()
    if st.button("💬 채팅창"):
        st.session_state.page = "chat_list"
        st.rerun()
    st.markdown("---")
    if st.button("로그아웃"):
        st.session_state.profile_data = None
        st.session_state.page = "start"
        st.rerun()

def render_matching():
    pd = st.session_state.profile_data
    fb = firebase()
    if not fb:
        st.error("데이터베이스 연결이 없습니다.")
        if st.button("홈으로"):
            st.session_state.page = "home"
            st.rerun()
        return
    uid = pd.get("user_id")
    today = datetime.now().strftime("%Y-%m-%d")
    attempts = fb.get_matching_attempts(uid, today)
    st.markdown(f"### 친구 찾기 (남은 횟수: {5 - attempts}회)")
    grade_opt = st.selectbox("매칭 학년", ["전체", "1학년", "2학년", "3학년"])
    if st.button("랜덤 매칭 시작") and attempts < 5:
        users = fb.get_all_users()
        target_grade = None if grade_opt == "전체" else int(grade_opt[0])
        insta_me = (pd.get("instagram") or "").replace("@", "")
        cand = [u for u in users if u.get("user_id") != uid and (u.get("instagram") or "").replace("@", "") != insta_me]
        if target_grade is not None:
            cand = [u for u in cand if str(u.get("grade", "")).replace("학년", "") == str(target_grade)]
        if not cand:
            st.warning("매칭 가능한 친구가 없습니다.")
        else:
            other = random.choice(cand)
            st.success(f"매칭된 친구: **{other.get('nickname','')}** (@{other.get('instagram','')}) | {other.get('grade','')}학년 | {other.get('mbti','')}")
            if st.button("친구 요청 보내기"):
                md = {"sender_id": uid, "sender_instagram": insta_me, "receiver_id": other.get("user_id"), "receiver_instagram": other.get("instagram", ""), "status": "pending", "matched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                if "matching_id" not in md:
                    md["matching_id"] = str(__import__("uuid").uuid4())
                fb.save_matching(md)
                fb.increment_matching_attempts(uid, today)
                st.success("친구 요청을 보냈습니다!")
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()

def render_notifications():
    pd = st.session_state.profile_data
    fb = firebase()
    st.markdown("### 💌 나에게 온 알림")
    if fb:
        matchings = fb.get_matchings_for_user(pd.get("user_id"))
        recv = [m for m in matchings if m.get("receiver_id") == pd.get("user_id") and m.get("status") == "pending"]
        for m in recv:
            with st.expander(f"💝 {m.get('sender_instagram','')}님의 매칭 요청"):
                if st.button("수락", key=m.get("matching_id", "")):
                    m["status"] = "accepted"
                    m["matched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    fb.update_matching(m)
                    st.success("수락했습니다!")
                    st.rerun()
        if not recv:
            st.info("새로운 알림이 없습니다.")
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()

def render_matched_friends():
    pd = st.session_state.profile_data
    fb = firebase()
    st.markdown("### 💕 매칭된 친구")
    if fb:
        matchings = fb.get_matchings_for_user(pd.get("user_id"))
        accepted = [m for m in matchings if m.get("status") == "accepted"]
        users = {u.get("user_id"): u for u in fb.get_all_users()}
        for m in accepted:
            oid = m.get("receiver_id") if m.get("sender_id") == pd.get("user_id") else m.get("sender_id")
            u = users.get(oid, {})
            st.write(f"💝 **{u.get('nickname','')}** (@{u.get('instagram','')}) | {u.get('grade','')}학년 | {u.get('mbti','')}")
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()

def render_chat_list():
    pd = st.session_state.profile_data
    fb = firebase()
    st.markdown("### 💬 채팅 목록")
    if fb:
        matchings = fb.get_matchings_for_user(pd.get("user_id"))
        accepted = [m for m in matchings if m.get("status") == "accepted"]
        users = {u.get("user_id"): u for u in fb.get_all_users()}
        for m in accepted:
            oid = m.get("receiver_id") if m.get("sender_id") == pd.get("user_id") else m.get("sender_id")
            u = users.get(oid, {})
            if st.button(f"💬 {u.get('nickname','')}님과 채팅하기", key=oid):
                st.session_state.chat_with = oid
                st.session_state.page = "chat_room"
                st.rerun()
        if not accepted:
            st.info("매칭된 친구가 없습니다.")
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()

def render_chat_room():
    pd = st.session_state.profile_data
    oid = st.session_state.get("chat_with")
    fb = firebase()
    if not oid or not fb:
        st.session_state.page = "chat_list"
        st.rerun()
        return
    users = {u.get("user_id"): u for u in fb.get_all_users()}
    other = users.get(oid, {})
    st.markdown(f"### 💬 {other.get('nickname','')}님과의 채팅")
    msgs = fb.get_messages(pd.get("user_id"), oid) if hasattr(fb, "get_messages") else []
    for m in (msgs or []):
        who = "나" if m.get("sender_id") == pd.get("user_id") else other.get("nickname", "")
        st.chat_message("user" if who == "나" else "assistant").write(f"**{who}**: {m.get('message','')}")
    msg = st.chat_input("메시지를 입력하세요...")
    if msg:
        if hasattr(fb, "save_message"):
            fb.save_message(pd.get("user_id"), oid, msg)
        st.rerun()
    if st.button("← 채팅 목록"):
        st.session_state.page = "chat_list"
        st.rerun()

def main():
    page = st.session_state.page
    if page == "start":
        render_start()
    elif page == "login_options":
        render_login_options()
    elif page == "login":
        render_login()
    elif page == "privacy":
        render_privacy()
    elif page == "signup":
        render_signup()
    elif page == "mbti":
        render_mbti()
    elif page == "home":
        render_home()
    elif page == "matching":
        render_matching()
    elif page == "notifications":
        render_notifications()
    elif page == "matched_friends":
        render_matched_friends()
    elif page == "chat_list":
        render_chat_list()
    elif page == "chat_room":
        render_chat_room()
    else:
        st.session_state.page = "start"
        st.rerun()

if __name__ == "__main__":
    main()
