# -*- coding: utf-8 -*-
"""GitHub 자동 푸시 스크립트"""
import subprocess
import os
import sys

# 현재 스크립트 위치로 이동
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

REMOTE_URL = "https://github.com/rlawldks56/making.nj.friend.git"

print("=" * 50)
print("  making.nj.friend -> GitHub 푸시")
print(f"  {REMOTE_URL}")
print("=" * 50)
print()

def run_git(cmd, desc, check=True):
    """Git 명령 실행"""
    print(f"[실행] {desc}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', cwd=script_dir)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            if result.returncode == 0:
                # 성공했지만 경고가 있는 경우
                pass
            else:
                print(f"경고: {result.stderr.strip()}")
        if result.returncode == 0:
            print(f"[OK] {desc} 완료\n")
            return True
        else:
            if check:
                print(f"[!!] {desc} 실패 (코드: {result.returncode})\n")
            return False
    except Exception as e:
        print(f"오류: {e}\n")
        return False

# 1. Git 저장소 초기화 확인
if not os.path.exists(".git"):
    print("[1/6] Git 저장소 초기화...")
    run_git(["git", "init"], "저장소 초기화")
else:
    print("[1/6] Git 저장소 확인 완료\n")

# 2. 원격 저장소 확인 및 설정
print("[2/6] 원격 저장소 확인...")
result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, encoding='utf-8', errors='ignore', cwd=script_dir)
if result.returncode != 0:
    print("원격 저장소가 없습니다. 추가합니다...")
    run_git(["git", "remote", "add", "origin", REMOTE_URL], "원격 저장소 추가")
else:
    print(f"원격 저장소: {result.stdout.strip()}")
    run_git(["git", "remote", "set-url", "origin", REMOTE_URL], "원격 저장소 URL 업데이트")
print()

# 3. 변경 파일 추가
print("[3/6] 변경 파일 추가...")
run_git(["git", "add", "."], "변경 파일 추가")
run_git(["git", "add", "-u"], "삭제된 파일 추적")
print()

# 4. 상태 확인
print("[4/6] 상태 확인...")
run_git(["git", "status"], "상태 확인", check=False)
print()

# 5. 커밋 생성
print("[5/6] 커밋 생성...")
commit_msg = "feat: 로그인 정보 자동 저장 및 자동완성 기능 추가"
result = run_git(["git", "commit", "-m", commit_msg], "커밋 생성", check=False)
if not result:
    print("커밋할 변경사항이 없거나 이미 커밋됨.\n")
print()

# 6. 브랜치 이름 변경 및 푸시
print("[6/6] GitHub로 푸시...")
run_git(["git", "branch", "-M", "main"], "브랜치 이름 변경", check=False)
result = run_git(["git", "push", "-u", "origin", "main"], "GitHub로 푸시", check=False)
if not result:
    # main 브랜치가 없으면 master 시도
    run_git(["git", "push", "-u", "origin", "master"], "GitHub로 푸시 (master)", check=False)

print("=" * 50)
print("  완료!")
print("  https://github.com/rlawldks56/making.nj.friend")
print("=" * 50)
print()
print("다음 단계: Streamlit Cloud에서 웹 주소 만들기")
print("  https://share.streamlit.io")
print("  -> New app -> Repository: rlawldks56/making.nj.friend")
print("  -> Main file: streamlit_app.py")
print("  -> Deploy!")
print()
# 브라우저로 Streamlit Cloud 열기 (다음 단계 자동 안내)
try:
    import webbrowser
    webbrowser.open("https://share.streamlit.io")
    print("Streamlit Cloud 페이지를 브라우저에서 열었습니다.")
except Exception:
    pass
try:
    input("아무 키나 누르면 종료합니다...")
except EOFError:
    pass
