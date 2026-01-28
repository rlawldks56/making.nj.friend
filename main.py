import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import json
import random
from datetime import datetime
import tkinter.font as tkfont
from config import APP_WIDTH, APP_HEIGHT, FIREBASE_TEST_MODE, FONT_FAMILY, TITLE_FONT_SIZE, CONTENT_FONT_SIZE
from firebase_manager import FirebaseManager
import traceback
import uuid

# 공통 색상 정의
APP_COLORS = {
    'background': '#FFF5F7',  # 매우 연한 핑크 배경
    'primary': '#FFB5C5',    # 연한 핑크
    'secondary': '#FFC0CB',  # 밝은 핑크
    'text': '#4A4A4A',      # 텍스트 색상
    'white': '#FFFFFF',     # 흰색
    'title': '#FF9AAC',     # 중간 톤의 핑크
    'subtitle': '#FFB5C5',   # 연한 핑크
    'accent': '#FFD1DC',    # 매우 연한 분홍색
    'light_gray': '#F8F9FA', # 연한 회색
    'gray': '#808080',      # 회색
    'dark_gray': '#4A4A4A',  # 어두운 회색
    'matching_bg': '#FFF5F7', # 매칭 화면용 연한 분홍색 배경
    'button': '#FFB5C5',     # 버튼 색상 (연한 핑크)
    'button_hover': '#FF9AAC', # 버튼 호버 색상 (중간 톤의 핑크)
    'result_bg': '#FFF5F7',   # 결과 배경 색상 (연한 핑크)
    'bg': '#FFF5F7'          # 기본 배경 색상
}

class MBTITest:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.colors = APP_COLORS
        
        self.root.configure(bg=self.colors['background'])
        
        # 질문과 답변 설정
        self.questions = [
            {
                'question': '시험이 끝난 후 귀사하였다.\n기숙사에 왔을 때 나는?',
                'answers': [
                    '시험도 끝났는데 놀아야지!!\n애들 방으로 놀러가야지~~',
                    '애들이랑 노는 것도 좋지만\n오늘은 혼자 쉬어야지 침대와 몰아일체!'
                ],
                'types': ['E', 'I']
            },
            {
                'question': '기숙사 방을 옮기고\n새로 세팅을 할 때 나는?',
                'answers': [
                    '있는 그대로 사용한다.\n필요한 거만 쓰면 되지',
                    '나만의 취향과 생활습관에 맞춰서\n효율적으로 세팅해야지.'
                ],
                'types': ['S', 'N']
            },
            {
                'question': '친구가 시험을 망쳤다고\n울고 있다. 이때 나는?',
                'answers': [
                    '속상했겠다ㅠㅠ\n다음엔 더 잘할 수 있을거야!!',
                    '너가 더 노력하면 다음에 더 잘되겠지\n일단 에쏠부터 가자'
                ],
                'types': ['F', 'T']
            },
            {
                'question': '시험 일주일 전!!\n이때 나의 상태는?',
                'answers': [
                    '한건 많은 것 같은데\n플래너는 텅 비었음..',
                    '내일 플래너까지 세워져 있고\n앞으로의 계획이 완벽!!'
                ],
                'types': ['P', 'J']
            }
        ]
        
        self.mbti_descriptions = {
            'ENFP': '능주 핵인싸, 기숙사 복도만 걸어도 친구생김',
            'ENTP': '공부하다가 창업 아이템 생각해냄',
            'ESFP': '쉬는 시간 = 복도 런웨이',
            'ESTP': '공부? 일단 이것만 보고',
            'INFP': '계획은 잘 세움, 실천은 내일',
            'INFJ': '조용한데 친해지면 투머치토커',
            'ISFP': '방 꾸미기에 진심, 자기 혼자 인스타 감성',
            'ISTP': '무심한 해결사, 기숙사 맥가이버',
            'INTP': '단어 외우다가 존재 이유에 대해 고민함',
            'INTJ': '시험계획은 3주 전에 완성, 실천도 함',
            'ISTJ': '매일 같은 루틴으로 삶, 루틴 깨지면 멘붕',
            'ESTJ': '자습 때 말하는 애들이 세상에서 제일 싫음',
            'ENFJ': '기숙사 엄마상, 찾았다 우리엄마',
            'ESFJ': '우리 반 분위기는 내가 책임진다.',
            'ISFJ': '쟤 청소 진짜 열심히 한다. 에서 쟤',
            'ENTJ': '실행력 10000%'
        }
        
        self.current_question = 0
        self.answers = []
        
        self.create_welcome_screen()
        
    def create_welcome_screen(self):
        # 시작 화면 프레임
        welcome_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        welcome_frame.pack(fill="both", expand=True)
        
        # 제목
        title = ctk.CTkLabel(
            welcome_frame, 
            text="MBTI 성격유형 테스트",
            font=("Pretendard", 24, "bold"),
            text_color=self.colors['text']
        )
        title.pack(pady=20)
        
        # 시작 버튼
        start_button = ctk.CTkButton(
            welcome_frame,
            text="검사 시작하기",
            font=("Pretendard", 16),
            command=self.start_test
        )
        start_button.pack(pady=20)
        
    def start_test(self):
        self.show_question()
        
    def show_question(self):
        # 기존 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if self.current_question >= len(self.questions):
            self.show_result()
            return
            
        question = self.questions[self.current_question]
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=20
        )
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # 진행 상황 표시
        progress_text = f"Question {self.current_question + 1}/{len(self.questions)}"
        progress_label = ctk.CTkLabel(
            main_frame,
            text=progress_text,
            font=("Pretendard", 20),
            text_color=self.colors['primary']
        )
        progress_label.pack(pady=(20, 10))
        
        # 질문 텍스트
        question_label = ctk.CTkLabel(
            main_frame,
            text=question['question'],
            font=("Pretendard", 28, "bold"),
            text_color=self.colors['title']
        )
        question_label.pack(pady=(20, 40))
        
        # 답변 버튼들을 위한 프레임
        answers_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        answers_frame.pack(fill="x", padx=40, pady=20)
        
        # 답변 버튼들
        for i, answer in enumerate(question['answers']):
            # 답변 버튼
            btn = ctk.CTkButton(
                answers_frame,
                text=answer,
                font=("Pretendard", 18),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                text_color=self.colors['white'],
                width=700,
                height=120,
                corner_radius=15,
                command=lambda x=i: self.answer_selected(x)
            )
            btn.pack(pady=15)
        
    def answer_selected(self, answer_index):
        question = self.questions[self.current_question]
        self.answers.append(question['types'][answer_index])
        self.current_question += 1
        self.show_question()
        
    def show_result(self):
        # 기존 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # MBTI 결과 계산
        mbti = ''.join(self.answers)
        description = self.mbti_descriptions.get(mbti, "알 수 없는 유형")
        
        # 결과 프레임
        result_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['result_bg'],
            corner_radius=20
        )
        result_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # MBTI 결과
        mbti_label = ctk.CTkLabel(
            result_frame,
            text=mbti,
            font=("Pretendard", 48, "bold"),
            text_color=self.colors['title']
        )
        mbti_label.pack(pady=(60, 30))
        
        # 설명
        desc_label = ctk.CTkLabel(
            result_frame,
            text=description,
            font=("Pretendard", 24),
            wraplength=600,
            text_color=self.colors['text']
        )
        desc_label.pack(pady=40)
        
        # 확인 버튼
        confirm_button = ctk.CTkButton(
            result_frame,
            text="결과 확인",
            font=("Pretendard", 20),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: self.confirm_result(confirm_button, mbti)
        )
        confirm_button.pack(pady=40)

    def confirm_result(self, button, mbti):
        """결과 확인 버튼 클릭 처리"""
        # 버튼 비활성화 및 텍스트 변경
        button.configure(
            state="disabled",
            text="✓ 결과 확인 완료",
            fg_color=["#2ecc71", "#27ae60"]  # 초록색 계열
        )
        # 콜백 함수 호출
        self.callback(mbti)

class StudentMatchingApp:
    def __init__(self, root):
        self.root = root
        self.current_student = None
        self.colors = APP_COLORS
        self.matching_attempts = 0
        
        # 기본 폰트 설정
        self.title_font = ("Pretendard", 24, "bold")
        self.content_font = ("Pretendard", 14)
        
        # Firebase 초기화
        try:
            self.firebase = FirebaseManager()
            print("StudentMatchingApp Firebase 초기화 완료")
        except Exception as e:
            print(f"StudentMatchingApp Firebase 초기화 오류: {str(e)}")
            messagebox.showerror("오류", "매칭 시스템 초기화 중 오류가 발생했습니다.")
        
    def initialize(self, student_data):
        """앱 초기화"""
        try:
            print("초기화 시작:", student_data)
            self.current_student = student_data
            
            # 학년 데이터 처리
            grade = student_data.get('grade')
            if isinstance(grade, str):
                grade = int(grade.replace('학년', ''))
            
            # user_id가 이미 있다면 기존 사용자이므로 저장하지 않음
            if not student_data.get('user_id'):
                # 새로운 사용자의 경우에만 Firebase에 저장
                profile_data = {
                    'nickname': student_data.get('name', ''),
                    'name': student_data.get('name', ''),
                    'grade': grade,
                    'instagram': student_data.get('instagram', '').replace('@', ''),
                    'mbti': student_data.get('mbti', ''),
                    'gender': student_data.get('gender', ''),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_reset_date': datetime.now().strftime("%Y-%m-%d")
                }
                
                print("저장할 프로필 데이터:", profile_data)
                
                # Firebase에 프로필 저장
                user_id = self.firebase.save_profile(profile_data)
                if user_id:
                    self.current_student['user_id'] = user_id
                    print(f"프로필 저장 완료 (ID: {user_id})")
                else:
                    print("프로필 저장 실패")
                    raise Exception("프로필 저장에 실패했습니다.")
            
            # 오늘의 매칭 시도 횟수 확인 및 리셋
            today = datetime.now().strftime("%Y-%m-%d")
            current_id = student_data.get('user_id')
            if current_id:
                # 마지막 리셋 날짜 확인
                last_reset_date = self.firebase.get_last_reset_date(current_id)
                if last_reset_date != today:
                    # 날짜가 변경되었으면 매칭 횟수 리셋
                    self.firebase.reset_matching_attempts(current_id, today)
                    self.matching_attempts = 0
                else:
                    self.matching_attempts = self.firebase.get_matching_attempts(current_id, today)
                print(f"오늘의 매칭 시도 횟수: {self.matching_attempts}")
            else:
                print("사용자 ID를 찾을 수 없습니다.")
                raise Exception("사용자 ID를 찾을 수 없습니다.")
            
            self.create_widgets()
            
        except Exception as e:
            print(f"초기화 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"매칭 시스템 초기화 중 오류가 발생했습니다.\n{str(e)}")

    def create_widgets(self):
        """UI 위젯 생성"""
        # 메인 컨테이너
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["bg"],
            corner_radius=20
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title = ctk.CTkLabel(
            self.main_frame, 
            text="능주고등학교 친구 찾기",
            font=("Pretendard", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(pady=20)
        
        # 현재 학생 정보 카드
        self.create_profile_card()
        
        # 학년 선택 섹션
        self.create_grade_selection()
        
        # 매칭 버튼
        self.create_matching_button()
        
        # 매칭 결과 영역
        self.create_result_section()

    def create_matching_button(self):
        """매칭 버튼 생성"""
        # 남은 매칭 횟수 표시 레이블
        self.attempts_label = ctk.CTkLabel(
            self.main_frame,
            text=f"남은 매칭 횟수: {5 - self.matching_attempts}회",
            font=("Pretendard", 16),
            text_color=self.colors['text']
        )
        self.attempts_label.pack(pady=(0, 10))

        # 매칭 버튼
        self.match_button = ctk.CTkButton(
            self.main_frame,
            text="랜덤 매칭 시작",
            font=("Pretendard", 16, "bold"),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            corner_radius=30,
            width=250,
            height=50,
            command=self.start_matching
        )
        
        # 매칭 횟수가 5회 이상이면 버튼 비활성화
        if self.matching_attempts >= 5:
            self.match_button.configure(
                state="disabled",
                fg_color=self.colors['gray'],
                text="오늘의 매칭 완료"
            )
        
        self.match_button.pack(pady=10)

    def create_result_section(self):
        """매칭 결과 섹션 생성"""
        self.result_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["white"],
            corner_radius=15,
            height=200
        )
        self.result_frame.pack(fill="x", padx=20, pady=10)
        self.result_frame.pack_propagate(False)
        
        # 결과 섹션 제목
        result_title = ctk.CTkLabel(
            self.result_frame,
            text="매칭 결과",
            font=("Pretendard", 20, "bold"),
            text_color=self.colors["primary"]
        )
        result_title.pack(pady=(20, 15))
        
        # 결과 표시 영역
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="매칭 결과가 여기에 표시됩니다",
            font=("Pretendard", 16),
            text_color=self.colors["text"],
            wraplength=500
        )
        self.result_label.pack(pady=(0, 20))

    def start_matching(self):
        """매칭 시작"""
        try:
            # 현재 사용자 ID 확인
            current_id = self.current_student.get('user_id')
            if not current_id:
                raise Exception("현재 사용자 ID를 찾을 수 없습니다.")

            # 오늘 날짜의 매칭 시도 횟수 확인
            today = datetime.now().strftime("%Y-%m-%d")
            current_attempts = self.firebase.get_matching_attempts(current_id, today)
            
            # 매칭 횟수 초과 확인
            if current_attempts >= 5:
                messagebox.showwarning(
                    "매칭 제한",
                    "남은 매칭 횟수가 없습니다.\n내일 다시 시도해주세요!"
                )
                return
                
            # 매칭 시작 전 알림 (남은 횟수 표시)
            if not messagebox.askokcancel(
                "매칭 시작",
                f"매칭을 시작합니다!\n\n" +
                f"오늘 남은 매칭 횟수: {5 - current_attempts}회\n\n" +
                "선택한 학년의 데이터가 충분하지 않으면\n" +
                "다른 학년과 랜덤으로 매치될 수 있습니다.\n\n" +
                "계속하시겠습니까?"
            ):
                return

            # 모든 사용자 조회
            all_users = self.firebase.get_all_users()
            print(f"전체 사용자 수: {len(all_users)}")
            
            # 현재 학생과 다른 학년의 학생들만 필터링
            available_students = []
            target_grade = None
            
            if hasattr(self, 'target_grade') and self.target_grade != "전체":
                target_grade = int(self.target_grade[0])
            
            current_instagram = self.current_student.get('instagram', '').replace('@', '')
            
            for student in all_users:
                student_id = student.get('user_id')
                student_instagram = student.get('instagram', '').replace('@', '')
                
                if student_id == current_id or student_instagram == current_instagram:
                    continue
                    
                student_grade = student.get('grade')
                if isinstance(student_grade, str):
                    student_grade = int(student_grade.replace('학년', ''))
                
                if target_grade and student_grade != target_grade:
                    continue
                    
                available_students.append(student)
            
            if not available_students:
                messagebox.showinfo(
                    "알림", 
                    "매칭 가능한 학생이 없습니다.\n다른 학년을 선택해보세요!"
                )
                return
                
            # 랜덤으로 학생 선택
            matched_student = random.choice(available_students)
            student_grade = matched_student.get('grade')
            if isinstance(student_grade, str):
                student_grade = student_grade.replace('학년', '')
                
            # 매칭 결과 표시
            result_text = f"""
매칭된 친구 정보

별명: {matched_student.get('nickname', '알 수 없음')}
학년: {student_grade}학년
성별: {matched_student.get('gender', '알 수 없음')}
MBTI: {matched_student.get('mbti', '알 수 없음')}
            """
            self.result_label.configure(
                text=result_text,
                justify="left"
            )
            
            # 친구 요청 확인 창
            if messagebox.askyesno(
                "친구 요청 확인",
                f"이 친구에게 친구 요청을 보내시겠습니까?\n\n{result_text}",
                icon="question"
            ):
                # 매칭 요청 생성
                matching_data = {
                    'sender_id': current_id,
                    'sender_instagram': self.current_student.get('instagram', '').replace('@', ''),
                    'receiver_id': matched_student.get('user_id'),
                    'receiver_instagram': matched_student.get('instagram', ''),
                    'status': 'pending',
                    'matched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # 매칭 시도 횟수 증가 및 저장
                if self.firebase.increment_matching_attempts(current_id, today):
                    print(f"매칭 시도 횟수 증가 성공 (현재: {current_attempts + 1})")
                    # 남은 매칭 횟수 업데이트
                    self.matching_attempts = current_attempts + 1
                    self.attempts_label.configure(text=f"남은 매칭 횟수: {5 - self.matching_attempts}회")
                    
                    # 매칭 횟수가 5회가 되면 버튼 비활성화
                    if self.matching_attempts >= 5:
                        self.match_button.configure(
                            state="disabled",
                            fg_color=self.colors['gray'],
                            text="오늘의 매칭 완료"
                        )
                else:
                    raise Exception("매칭 시도 횟수 증가 실패")
                
                if self.firebase.save_matching(matching_data):
                    messagebox.showinfo(
                        "성공", 
                        f"{matched_student.get('nickname', '알 수 없음')} 학생에게\n친구 요청을 보냈습니다!\n\n상대방의 수락을 기다려주세요."
                    )
                else:
                    raise Exception("매칭 요청 저장에 실패했습니다.")
            else:
                # 거절 시 결과 텍스트 초기화
                self.result_label.configure(
                    text="매칭 결과가 여기에 표시됩니다",
                    justify="center"
                )
                
        except Exception as e:
            print(f"매칭 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"매칭 처리 중 오류가 발생했습니다.\n{str(e)}")

    def create_grade_selection(self):
        """학년 선택 섹션 생성"""
        grade_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["white"],
            corner_radius=15
        )
        grade_frame.pack(fill="x", padx=20, pady=10)
        
        # 학년 선택 제목
        grade_title = ctk.CTkLabel(
            grade_frame,
            text="매칭 학년 선택",
            font=("Pretendard", 16, "bold"),
            text_color=self.colors["primary"]
        )
        grade_title.pack(pady=(15, 10))
        
        # 콤보박스 생성
        self.grade_var = tk.StringVar(value="전체")
        grade_combo = ttk.Combobox(
            grade_frame,
            textvariable=self.grade_var,
            values=["전체", "1학년", "2학년", "3학년"],
            state="readonly",
            width=15,
            font=self.content_font
        )
        grade_combo.pack(pady=(0, 15))
        grade_combo.bind('<<ComboboxSelected>>', self.on_grade_selected)

    def on_grade_selected(self, event):
        """학년 선택 시 호출되는 콜백"""
        self.target_grade = self.grade_var.get()

    def create_profile_card(self):
        """프로필 카드 생성"""
        profile_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["secondary"],
            corner_radius=15
        )
        profile_frame.pack(fill="x", padx=20, pady=10)
        
        # 프로필 제목
        profile_title = ctk.CTkLabel(
            profile_frame,
            text="내 정보",
            font=("Pretendard", 18, "bold"),
            text_color=self.colors["white"]
        )
        profile_title.pack(pady=(15, 10))
        
        # 프로필 정보
        info_text = f"""
인스타그램: {self.current_student.get('instagram', '')}
학년: {self.current_student.get('grade', '')}학년
MBTI: {self.current_student.get('mbti', '')}
성별: {self.current_student.get('gender', '')}
        """
        
        profile_label = ctk.CTkLabel(
            profile_frame,
            text=info_text,
            font=("Pretendard", 14),
            text_color=self.colors["white"]
        )
        profile_label.pack(pady=(0, 15))

    def update_requests_list(self):
        """받은 요청 목록 업데이트"""
        # 기존 위젯 제거
        for widget in self.requests_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # 제목 라벨 제외
                widget.destroy()
        
        # 현재 학생이 받은 요청 필터링 (대기 중인 요청만)
        received_requests = [
            r for r in self.matching_requests 
            if r['receiver_id'] == self.current_student['user_id'] and 
            r['status'] == "pending"
        ]
        
        if not received_requests:
            no_requests_label = ctk.CTkLabel(
                self.requests_frame,
                text="💌 새로운 매칭 요청이 없습니다",
                font=("Pretendard", 14),
                text_color=self.colors["text"]
            )
            no_requests_label.pack(pady=(0, 15))
            return
            
        # 요청 목록 표시
        for request in received_requests:
            self.create_request_item(request)
            
    def create_request_item(self, request):
        """요청 아이템 UI 생성"""
        item_frame = ctk.CTkFrame(
            self.requests_frame,
            fg_color=self.colors["bg"],
            corner_radius=10
        )
        item_frame.pack(fill="x", padx=15, pady=5)
        
        # 요청 정보 표시
        sender = next((s for s in self.students if s['user_id'] == request['sender_id']), None)
        if sender:
            info_text = f"""
📨 {sender['nickname']}님의 매칭 요청
📚 {sender['grade']}학년 {sender['class']}반
💝 관심사: {', '.join(sender['interests'])}
            """
        else:
            info_text = f"📨 {request['sender_name']}님의 매칭 요청"
            
        info_label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=("Pretendard", 14),
            text_color=self.colors["text"]
        )
        info_label.pack(side="left", padx=15, pady=10)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            item_frame,
            fg_color="transparent"
        )
        button_frame.pack(side="right", padx=15, pady=10)
        
        # 수락 버튼
        accept_button = ctk.CTkButton(
            button_frame,
            text="✅ 수락",
            font=("Pretendard", 14),
            fg_color=self.colors["accent"],
            text_color=self.colors["text"],
            width=80,
            height=30,
            corner_radius=15,
            command=lambda m=request: self.handle_request(m, 'accepted')
        )
        accept_button.pack(side="left", padx=5)
        
        # 거절 버튼
        reject_button = ctk.CTkButton(
            button_frame,
            text="❌ 거절",
            font=("Pretendard", 14),
            fg_color=self.colors["secondary"],
            text_color=self.colors["text"],
            width=80,
            height=30,
            corner_radius=15,
            command=lambda m=request: self.handle_request(m, 'rejected')
        )
        reject_button.pack(side="left", padx=5)
        
    def handle_request(self, request, status):
        """요청 처리"""
        request['status'] = status
        
        # Firebase/로컬 저장소에 상태 업데이트
        self.firebase.update_matching(request)
        
        sender = next((s for s in self.students if s['user_id'] == request['sender_id']), None)
        sender_name = sender['nickname'] if sender else request['sender_name']
        
        if status == "accepted":
            messagebox.showinfo(
                "매칭 수락", 
                f"✨ {sender_name} 학생과의 매칭이 성사되었습니다!\n\n" +
                "서로 존중하고 배려하는 멋진 친구 관계가 되길 바랍니다. 💝"
            )
        else:
            messagebox.showinfo(
                "매칭 거절", 
                f"😢 {sender_name} 학생과의 매칭을 거절했습니다."
            )
            
        # 요청 목록 업데이트
        self.update_requests_list()

    def on_mbti_result(self, mbti_result):
        """MBTI 테스트 결과 처리"""
        try:
            # 프로필 정보에 MBTI 결과 추가
            self.temp_profile['mbti'] = mbti_result
            
            # Firebase에 저장할 데이터 준비
            profile_data = {
                'gender': self.temp_profile['gender'],
                'grade': self.temp_profile['grade'].replace('학년', ''),  # '1학년' -> '1'
                'nickname': self.temp_profile['nickname'],
                'instagram': self.temp_profile['instagram'].replace('@', ''),  # @ 제거
                'mbti': self.temp_profile['mbti'],
                'name': self.temp_profile['name'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("Firebase에 저장할 프로필 데이터:", profile_data)  # 디버깅 로그
            
            # Firebase에 프로필 저장
            try:
                user_id = self.firebase_manager.save_profile(profile_data)
                if user_id:
                    print(f"Firebase에 프로필 저장 성공 (ID: {user_id})")  # 디버깅 로그
                    
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': user_id,
                        'nickname': profile_data['nickname'],
                        'instagram': profile_data['instagram'],
                        'grade': profile_data['grade'],
                        'gender': profile_data['gender'],
                        'mbti': profile_data['mbti'],
                        'name': profile_data['name']
                    }
                    
                    messagebox.showinfo("성공", "프로필이 저장되었습니다!")
                    self.show_home_screen()
                else:
                    raise Exception("Firebase 저장 실패: user_id가 반환되지 않음")
            except Exception as e:
                print(f"Firebase 저장 오류: {str(e)}")  # 디버깅 로그
                raise Exception(f"Firebase 저장 실패: {str(e)}")
        except Exception as e:
            error_msg = f"프로필 저장 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)  # 디버깅 로그
            messagebox.showerror("오류", error_msg)
            print("Error details:", e)  # 디버깅 로그

    def run(self):
        self.root.mainloop()

class FriendFinderApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌸 능친 만들기 🌸")
        self.root.geometry("800x600")
        
        # 색상 테마 설정
        self.colors = APP_COLORS
        
        # Firebase 매니저 초기화
        self.firebase_manager = FirebaseManager()
        self.profile_data = None
        
        self.root.configure(fg_color=self.colors['background'])
        self.show_initial_screen()
        
    def show_initial_screen(self):
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 시작 화면 프레임
        self.start_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background']
        )
        self.start_frame.pack(fill="both", expand=True)
        
        # 메인 타이틀
        title = ctk.CTkLabel(
            self.start_frame,
            text="능친 만들기",
            font=("Pretendard", 52, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(120, 40))
        
        # 부제목
        subtitle = ctk.CTkLabel(
            self.start_frame,
            text="당신의 특별한 인연을 찾아보세요",
            font=("Pretendard", 24),
            text_color=self.colors['subtitle']
        )
        subtitle.pack(pady=20)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            self.start_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=60)
        
        # START 버튼
        start_button = ctk.CTkButton(
            button_frame,
            text="START",
            font=("Pretendard", 32, "bold"),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=300,
            height=80,
            corner_radius=40,
            command=self.show_login_options
        )
        start_button.pack()
        
        # 하단 장식
        decoration2 = ctk.CTkLabel(
            self.start_frame,
            text="✧･ﾟ: *✧･ﾟ:* ♡ *:･ﾟ✧*:･ﾟ✧",
            font=("Pretendard", 24),
            text_color=self.colors['primary']
        )
        decoration2.pack(pady=20)
        
    def is_valid_mbti(self, mbti):
        """MBTI 유효성 검사"""
        if len(mbti) != 4:
            return False
            
        valid_chars = {
            0: {'E', 'I'},
            1: {'N', 'S'},
            2: {'F', 'T'},
            3: {'J', 'P'}
        }
        
        for i, char in enumerate(mbti):
            if char not in valid_chars[i]:
                return False
        return True
        
    def show_login_options(self):
        """START 버튼 클릭 시 로그인 옵션 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="💝 능친 만들기 💝",
            font=("Pretendard", 28, "bold"),
            text_color="#FF1493"  # 밝은 핫핑크
        )
        title.pack(pady=(100, 50))
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # 기존 프로필로 로그인 버튼
        login_button = ctk.CTkButton(
            button_frame,
            text="기존 프로필로 로그인",
            font=("Pretendard", 16),
            fg_color="#FFB6C1",  # 연한 분홍색
            hover_color="#FFA0B0",  # 진한 분홍색
            text_color="#FFFFFF",  # 흰색
            width=250,
            height=50,
            corner_radius=25,
            command=self.show_login_screen
        )
        login_button.pack(pady=10)
        
        # 새 프로필 만들기 버튼
        new_profile_button = ctk.CTkButton(
            button_frame,
            text="새 프로필 만들기",
            font=("Pretendard", 16),
            fg_color="transparent",
            hover_color="#FFA0B0",  # 진한 분홍색
            text_color="#FF69B4",  # 중간 톤의 핑크
            border_color="#FFB6C1",  # 연한 분홍색
            border_width=2,
            width=250,
            height=50,
            corner_radius=25,
            command=self.show_privacy_consent
        )
        new_profile_button.pack(pady=10)
        
    def show_login_screen(self):
        """기존 프로필로 로그인 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        main_frame.pack(fill="both", expand=True)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="프로필 로그인",
            font=("Pretendard", 28, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(80, 50))
        
        # 입력 필드 프레임
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=20)
        
        # 이름 입력
        name_label = ctk.CTkLabel(
            input_frame,
            text="이름",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        name_label.pack(pady=(0, 5))
        
        self.login_name_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="본인 이름 입력"
        )
        self.login_name_entry.pack(pady=(0, 15))

        # 별명 입력
        nickname_label = ctk.CTkLabel(
            input_frame,
            text="별명",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        nickname_label.pack(pady=(0, 5))
        
        self.login_nickname_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="기존 별명 입력"
        )
        self.login_nickname_entry.pack(pady=(0, 15))
        
        # 인스타그램 아이디 입력
        insta_label = ctk.CTkLabel(
            input_frame,
            text="인스타그램 아이디",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        insta_label.pack(pady=(0, 5))
        
        self.login_insta_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="@아이디"
        )
        self.login_insta_entry.pack(pady=(0, 25))
        self.login_insta_entry.insert(0, '@')  # 초기값으로 @ 설정
        
        # 입력 내용이 변경될 때마다 호출되는 함수
        def on_insta_change(event=None):
            current_text = self.login_insta_entry.get()
            cursor_position = self.login_insta_entry.index(tk.INSERT)
            
            if not current_text.startswith('@'):
                self.login_insta_entry.delete(0, tk.END)
                self.login_insta_entry.insert(0, '@' + current_text.replace('@', ''))
                self.login_insta_entry.icursor(cursor_position + 1)
            
            if current_text == '@':
                self.login_insta_entry.icursor(1)
                
        self.login_insta_entry.bind('<KeyRelease>', on_insta_change)
        
        # 백스페이스로 @ 삭제 방지
        def prevent_at_deletion(event):
            if event.keysym == 'BackSpace' and self.login_insta_entry.index(tk.INSERT) <= 1:
                return 'break'
            
        self.login_insta_entry.bind('<Key>', prevent_at_deletion)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # 로그인 버튼
        login_button = ctk.CTkButton(
            button_frame,
            text="로그인",
            font=("Pretendard", 16),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=250,
            height=45,
            corner_radius=25,
            command=self.verify_login
        )
        login_button.pack(pady=10)
        
        # 뒤로가기 버튼
        back_button = ctk.CTkButton(
            button_frame,
            text="← 뒤로가기",
            font=("Pretendard", 14),
            fg_color='transparent',
            hover_color=self.colors['button_hover'],
            text_color=self.colors['text'],
            border_color=self.colors['button'],
            border_width=2,
            width=250,
            height=45,
            corner_radius=25,
            command=self.show_login_options
        )
        back_button.pack(pady=10)
        
    def verify_login(self):
        """로그인 정보 확인"""
        try:
            # 입력값 검증
            nickname = self.login_nickname_entry.get().strip()
            instagram = self.login_insta_entry.get().strip().replace('@', '')
            name = self.login_name_entry.get().strip()
            
            # 입력값 유효성 검사
            if not all([nickname, instagram, name]):
                messagebox.showerror("오류", "모든 정보를 입력해주세요.")
                return
                
            if len(name) < 2:
                messagebox.showerror("오류", "올바른 이름을 입력해주세요.")
                return
                
            if len(nickname) < 2:
                messagebox.showerror("오류", "올바른 별명을 입력해주세요.")
                return
                
            if len(instagram) < 2:
                messagebox.showerror("오류", "올바른 인스타그램 아이디를 입력해주세요.")
                return
            
            try:
                # Firebase에서 사용자 정보 확인
                users = self.firebase_manager.get_all_users()
                if not users:
                    raise Exception("사용자 정보를 불러올 수 없습니다.")
                    
                matching_user = None
                for user in users:
                    if (user.get('nickname', '').lower() == nickname.lower() and 
                        user.get('instagram', '').lower() == instagram.lower() and
                        user.get('name', '').lower() == name.lower()):
                        matching_user = user
                        break
                
                if matching_user:
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': matching_user.get('user_id'),
                        'nickname': matching_user.get('nickname'),
                        'instagram': matching_user.get('instagram'),
                        'grade': matching_user.get('grade'),
                        'gender': matching_user.get('gender'),
                        'mbti': matching_user.get('mbti'),
                        'name': matching_user.get('name')
                    }
                    
                    # 필수 필드 확인
                    missing_fields = [field for field, value in self.profile_data.items() 
                                   if not value and field != 'mbti']
                    if missing_fields:
                        raise Exception(f"프로필 정보가 불완전합니다: {', '.join(missing_fields)}")
                    
                    print("로그인 성공 - 프로필 데이터:", self.profile_data)
                    messagebox.showinfo("성공", "로그인되었습니다!")
                    self.show_home_screen()
                else:
                    messagebox.showerror("오류", "일치하는 프로필을 찾을 수 없습니다.\n입력하신 정보를 다시 확인해주세요.")
                    
            except Exception as e:
                print(f"Firebase 데이터 조회 중 오류: {str(e)}")
                raise Exception(f"데이터베이스 오류: {str(e)}")
                
        except Exception as e:
            print(f"로그인 처리 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"로그인 처리 중 오류가 발생했습니다.\n{str(e)}")

    def show_home_screen(self):
        # 프로필 데이터 확인
        if not self.profile_data:
            print("프로필 데이터가 없습니다.")
            messagebox.showerror("오류", "프로필 정보를 찾을 수 없습니다.")
            return
            
        print("홈 화면에서 저장된 프로필:", self.profile_data)
        
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 상단 프로필 카드
        profile_card = ctk.CTkFrame(
            main_frame,
            fg_color="#FFB6C1",  # 연한 분홍색
            corner_radius=15
        )
        profile_card.pack(fill="x", padx=20, pady=20)
        
        # 환영 메시지
        welcome_text = f"✨ 환영합니다! ✨"
        welcome_label = ctk.CTkLabel(
            profile_card,
            text=welcome_text,
            font=("Pretendard", 24, "bold"),
            text_color="#FFFFFF"
        )
        welcome_label.pack(pady=(20, 5))
        
        # 이름 정보
        name_label = ctk.CTkLabel(
            profile_card,
            text=f"💝 {self.profile_data['name']}님",
            font=("Pretendard", 18),
            text_color="#FFFFFF"
        )
        name_label.pack(pady=5)
        
        # 프로필 정보
        info_frame = ctk.CTkFrame(
            profile_card,
            fg_color="transparent"
        )
        info_frame.pack(pady=15)
        
        # 인스타그램 정보
        insta_frame = ctk.CTkFrame(
            info_frame,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        insta_frame.pack(pady=5, padx=20, fill="x")
        
        insta_label = ctk.CTkLabel(
            insta_frame,
            text=f"📷 {self.profile_data['instagram']}",
            font=("Pretendard", 14),
            text_color="#4A4A4A"
        )
        insta_label.pack(pady=8, padx=15)
        
        # MBTI 정보
        mbti_frame = ctk.CTkFrame(
            info_frame,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        mbti_frame.pack(pady=5, padx=20, fill="x")
        
        mbti_label = ctk.CTkLabel(
            mbti_frame,
            text=f"🎭 MBTI: {self.profile_data['mbti']}",
            font=("Pretendard", 14),
            text_color="#4A4A4A"
        )
        mbti_label.pack(pady=8, padx=15)
        
        # 버튼 섹션
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=30)
        
        # 친구 찾기 버튼
        find_friend_button = ctk.CTkButton(
            button_frame,
            text="💝 친구 찾기",
            font=("Pretendard", 16, "bold"),
            fg_color="#FFB6C1",  # 연한 분홍색
            hover_color="#FFA0B0",  # 진한 분홍색
            corner_radius=30,
            width=200,
            height=50,
            command=self.start_matching_from_428
        )
        find_friend_button.pack(pady=10)
        
        # 알림 버튼
        notification_button = ctk.CTkButton(
            button_frame,
            text="💌 나에게 온 알림",
            font=("Pretendard", 16),
            fg_color=self.colors["light_gray"],
            text_color=self.colors["dark_gray"],
            hover_color=self.colors["gray"],
            corner_radius=30,
            width=200,
            height=50,
            command=self.show_notifications
        )
        notification_button.pack(pady=10)
        
        # 매칭된 친구 버튼
        matched_friends_button = ctk.CTkButton(
            button_frame,
            text="💕 매칭된 친구",
            font=("Pretendard", 16),
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            text_color=self.colors["text"],
            corner_radius=30,
            width=200,
            height=50,
            command=self.show_matched_friends
        )
        matched_friends_button.pack(pady=10)
        
        # 채팅창 버튼 (읽지 않은 메시지 알림 표시)
        self.chat_button = ctk.CTkButton(
            button_frame,
            text="💬 채팅창",
            font=("Pretendard", 16),
            fg_color=self.colors["primary"],
            hover_color=self.colors["button_hover"],
            text_color=self.colors["white"],
            corner_radius=30,
            width=200,
            height=50,
            command=self.show_chat_list
        )
        self.chat_button.pack(pady=10)
        
        # 읽지 않은 메시지 수 확인 및 업데이트
        self.update_unread_message_count()
        
        # 하단 정보
        footer_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # 왼쪽 하단 로그아웃 버튼
        logout_button = ctk.CTkButton(
            footer_frame,
            text="로그아웃",
            font=("Pretendard", 11),
            fg_color=self.colors["gray"],
            hover_color=self.colors["dark_gray"],
            text_color=self.colors["white"],
            width=80,
            height=30,
            corner_radius=15,
            command=self.logout
        )
        logout_button.pack(side="left", padx=5, pady=5)
        
        # 오른쪽 버전 정보
        version_label = ctk.CTkLabel(
            footer_frame,
            text="Version 1.0.0 | Made with 💖",
            font=("Pretendard", 12),
            text_color=self.colors["dark_gray"]
        )
        version_label.pack(side="right", padx=5, pady=5)

    def logout(self):
        """로그아웃 처리 - 초기 화면으로 돌아가기"""
        # 프로필 데이터 초기화
        self.profile_data = None
        # 초기 화면으로 돌아가기
        self.show_initial_screen()
    
    def update_unread_message_count(self):
        """읽지 않은 메시지 수 업데이트"""
        try:
            if not hasattr(self, 'profile_data') or not self.profile_data:
                return
            
            user_id = self.profile_data.get('user_id')
            if not user_id:
                return
            
            unread_count = self.firebase_manager.get_unread_messages_count(user_id)
            
            if unread_count > 0:
                self.chat_button.configure(
                    text=f"💬 채팅창 ({unread_count})",
                    fg_color=self.colors["title"]
                )
            else:
                self.chat_button.configure(
                    text="💬 채팅창",
                    fg_color=self.colors["primary"]
                )
        except Exception as e:
            print(f"읽지 않은 메시지 수 업데이트 오류: {str(e)}")
    
    def show_chat_list(self):
        """채팅 목록 화면 표시"""
        try:
            user_id = self.profile_data.get('user_id')
            if not user_id:
                messagebox.showerror("오류", "사용자 정보를 찾을 수 없습니다.")
                return
            
            # 채팅 목록 창 생성
            chat_list_window = ctk.CTkToplevel(self.root)
            chat_list_window.title("💬 채팅 목록")
            chat_list_window.geometry("700x600")
            chat_list_window.transient(self.root)
            chat_list_window.configure(fg_color=self.colors['background'])
            
            # 메인 프레임
            main_frame = ctk.CTkFrame(
                chat_list_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 제목
            title_label = ctk.CTkLabel(
                main_frame,
                text="💬 채팅 목록",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors["primary"]
            )
            title_label.pack(pady=(10, 20))
            
            # 스크롤 가능한 프레임
            scrollable_frame = ctk.CTkScrollableFrame(
                main_frame,
                fg_color=self.colors['background'],
                width=650,
                height=450
            )
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 매칭된 친구 목록 가져오기
            matchings = self.firebase_manager.get_matchings_for_user(user_id)
            accepted_matchings = [m for m in matchings if m.get('status') == 'accepted']
            
            if not accepted_matchings:
                no_chat_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="아직 채팅할 친구가 없습니다 💬\n매칭된 친구와 채팅을 시작해보세요!",
                    font=("Pretendard", 16),
                    text_color=self.colors["dark_gray"],
                    wraplength=500
                )
                no_chat_label.pack(pady=50)
            else:
                # 모든 사용자 정보 가져오기
                all_users = self.firebase_manager.get_all_users()
                
                # 읽지 않은 메시지 수 가져오기
                unread_by_sender = self.firebase_manager.get_unread_messages_by_sender(user_id)
                
                # 각 친구와의 채팅 카드 표시
                for matching in accepted_matchings:
                    # 상대방 정보 찾기
                    other_id = matching['receiver_id'] if matching['sender_id'] == user_id else matching['sender_id']
                    
                    matched_user = None
                    for user in all_users:
                        if user.get('user_id') == other_id:
                            matched_user = user
                            break
                    
                    if not matched_user:
                        continue
                    
                    # 최근 메시지 가져오기
                    messages = self.firebase_manager.get_messages(user_id, other_id)
                    last_message = messages[-1] if messages else None
                    
                    # 읽지 않은 메시지 수
                    unread_count = unread_by_sender.get(other_id, 0)
                    
                    # 채팅 카드
                    chat_card = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color=self.colors['white'],
                        corner_radius=15
                    )
                    chat_card.pack(fill="x", padx=10, pady=8)
                    
                    # 카드 클릭 시 채팅 열기
                    def open_chat_from_list(user=matched_user, other_id=other_id):
                        chat_list_window.destroy()
                        self.open_chat(user, other_id)
                    
                    chat_card.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    
                    # 카드 내용 프레임
                    card_content = ctk.CTkFrame(
                        chat_card,
                        fg_color="transparent"
                    )
                    card_content.pack(fill="x", padx=20, pady=15)
                    card_content.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    
                    # 친구 이름과 읽지 않은 메시지 수
                    name_frame = ctk.CTkFrame(
                        card_content,
                        fg_color="transparent"
                    )
                    name_frame.pack(fill="x", pady=(0, 8))
                    name_frame.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    
                    friend_name = ctk.CTkLabel(
                        name_frame,
                        text=f"💝 {matched_user.get('nickname', '알 수 없음')}",
                        font=("Pretendard", 18, "bold"),
                        text_color=self.colors['title']
                    )
                    friend_name.pack(side="left")
                    friend_name.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    
                    # 읽지 않은 메시지 알림 배지
                    if unread_count > 0:
                        badge = ctk.CTkLabel(
                            name_frame,
                            text=f" {unread_count} ",
                            font=("Pretendard", 12, "bold"),
                            text_color=self.colors['white'],
                            fg_color=self.colors['title'],
                            corner_radius=10
                        )
                        badge.pack(side="right", padx=5)
                        badge.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    
                    # 최근 메시지 미리보기
                    if last_message:
                        preview_text = last_message.get('message', '')
                        if len(preview_text) > 40:
                            preview_text = preview_text[:40] + "..."
                        
                        is_sender = last_message.get('sender_id') == user_id
                        prefix = "나: " if is_sender else ""
                        
                        preview_label = ctk.CTkLabel(
                            card_content,
                            text=f"{prefix}{preview_text}",
                            font=("Pretendard", 12),
                            text_color=self.colors['text'],
                            anchor="w"
                        )
                        preview_label.pack(anchor="w", pady=(0, 5))
                        preview_label.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                        
                        # 시간 표시
                        timestamp = last_message.get('timestamp', '')
                        if timestamp:
                            time_str = timestamp.split()[1][:5] if ' ' in timestamp else timestamp[:5]
                            time_label = ctk.CTkLabel(
                                card_content,
                                text=time_str,
                                font=("Pretendard", 10),
                                text_color=self.colors['gray']
                            )
                            time_label.pack(anchor="e")
                            time_label.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
                    else:
                        no_msg_label = ctk.CTkLabel(
                            card_content,
                            text="아직 주고받은 메시지가 없습니다.",
                            font=("Pretendard", 12),
                            text_color=self.colors['gray'],
                            anchor="w"
                        )
                        no_msg_label.pack(anchor="w")
                        no_msg_label.bind("<Button-1>", lambda e, user=matched_user, oid=other_id: open_chat_from_list(user, oid))
            
            # 닫기 버튼
            close_button = ctk.CTkButton(
                main_frame,
                text="닫기",
                font=("Pretendard", 14),
                fg_color=self.colors['light_gray'],
                hover_color=self.colors['gray'],
                text_color=self.colors['dark_gray'],
                width=150,
                height=40,
                corner_radius=20,
                command=lambda: [chat_list_window.destroy(), self.update_unread_message_count()]
            )
            close_button.pack(pady=15)
            
        except Exception as e:
            print(f"채팅 목록 표시 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", "채팅 목록을 불러오는 중 오류가 발생했습니다.")

    def show_matching_success_screen(self, matching):
        """매칭 성사 축하 화면 표시"""
        try:
            # 상대방 정보 가져오기
            user_id = self.profile_data.get('user_id')
            is_sender = matching['sender_id'] == user_id
            other_id = matching['receiver_id'] if is_sender else matching['sender_id']
            other_instagram = matching['receiver_instagram'] if is_sender else matching['sender_instagram']
            
            # Firebase에서 상대방 프로필 정보 가져오기
            all_users = self.firebase_manager.get_all_users()
            matched_user = None
            for user in all_users:
                if user.get('user_id') == other_id:
                    matched_user = user
                    break
            
            if not matched_user:
                # 프로필 정보를 찾을 수 없으면 기본 정보만 표시
                matched_user = {
                    'nickname': other_instagram,
                    'instagram': other_instagram,
                    'grade': '?',
                    'mbti': '?',
                    'gender': '?'
                }
            
            # 축하 창 생성
            success_window = ctk.CTkToplevel(self.root)
            success_window.title("✨ 매칭 성사! ✨")
            success_window.geometry("500x700")
            success_window.transient(self.root)
            success_window.grab_set()
            success_window.configure(fg_color=self.colors['background'])
            
            # 메인 프레임
            main_frame = ctk.CTkFrame(
                success_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # 축하 메시지
            congrats_label = ctk.CTkLabel(
                main_frame,
                text="🎉 매칭 성사! 🎉",
                font=("Pretendard", 32, "bold"),
                text_color=self.colors['title']
            )
            congrats_label.pack(pady=(20, 10))
            
            # 하트 이모지
            heart_label = ctk.CTkLabel(
                main_frame,
                text="💕",
                font=("Pretendard", 60),
                text_color=self.colors['primary']
            )
            heart_label.pack(pady=10)
            
            # 상대방 프로필 카드
            profile_card = ctk.CTkFrame(
                main_frame,
                fg_color=self.colors['white'],
                corner_radius=20
            )
            profile_card.pack(fill="x", pady=20)
            
            # 상대방 이름/별명
            name_label = ctk.CTkLabel(
                profile_card,
                text=f"💝 {matched_user.get('nickname', '알 수 없음')}님",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors['title']
            )
            name_label.pack(pady=(25, 15))
            
            # 프로필 정보 프레임
            info_frame = ctk.CTkFrame(
                profile_card,
                fg_color="transparent"
            )
            info_frame.pack(pady=10, padx=20)
            
            # MBTI만 표시
            mbti_text = f"🎭 MBTI: {matched_user.get('mbti', '?')}"
            mbti_label = ctk.CTkLabel(
                info_frame,
                text=mbti_text,
                font=("Pretendard", 16),
                text_color=self.colors['text']
            )
            mbti_label.pack(pady=8)
            
            # 버튼 프레임
            button_frame = ctk.CTkFrame(
                main_frame,
                fg_color="transparent"
            )
            button_frame.pack(pady=20)
            
            # 인스타그램 바로가기 버튼
            insta_button = ctk.CTkButton(
                button_frame,
                text="📱 인스타그램 보기",
                font=("Pretendard", 14),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                width=200,
                height=40,
                corner_radius=20,
                command=lambda: self.open_instagram(matched_user.get('instagram', ''))
            )
            insta_button.pack(pady=8)
            
            # 첫 인사 보내기 버튼
            greeting_button = ctk.CTkButton(
                button_frame,
                text="💌 첫 인사 보내기",
                font=("Pretendard", 14),
                fg_color=self.colors['secondary'],
                hover_color=self.colors['primary'],
                width=200,
                height=40,
                corner_radius=20,
                command=lambda: self.send_first_greeting(matched_user, success_window)
            )
            greeting_button.pack(pady=8)
            
            # 확인 버튼
            confirm_button = ctk.CTkButton(
                button_frame,
                text="확인",
                font=("Pretendard", 14),
                fg_color=self.colors['light_gray'],
                hover_color=self.colors['gray'],
                text_color=self.colors['dark_gray'],
                width=200,
                height=40,
                corner_radius=20,
                command=lambda: [success_window.destroy(), self.show_notifications()]
            )
            confirm_button.pack(pady=8)
            
        except Exception as e:
            print(f"매칭 성사 화면 표시 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showinfo("성공", "매칭 요청을 수락했습니다!")
            self.show_notifications()

    def open_instagram(self, instagram_id):
        """인스타그램 프로필 열기"""
        try:
            import webbrowser
            instagram_url = f"https://www.instagram.com/{instagram_id.replace('@', '')}/"
            webbrowser.open(instagram_url)
        except Exception as e:
            print(f"인스타그램 열기 중 오류: {str(e)}")
            messagebox.showinfo("알림", f"인스타그램 아이디: @{instagram_id.replace('@', '')}")

    def send_first_greeting(self, matched_user, window):
        """첫 인사 메시지 보내기"""
        try:
            # 인사 메시지 입력 창
            greeting_window = ctk.CTkToplevel(window)
            greeting_window.title("💌 첫 인사 보내기")
            greeting_window.geometry("500x400")
            greeting_window.transient(window)
            greeting_window.grab_set()
            greeting_window.configure(fg_color=self.colors['background'])
            
            # 메인 프레임
            main_frame = ctk.CTkFrame(
                greeting_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # 제목
            title_label = ctk.CTkLabel(
                main_frame,
                text=f"💌 {matched_user.get('nickname', '친구')}님에게 인사하기",
                font=("Pretendard", 20, "bold"),
                text_color=self.colors['title']
            )
            title_label.pack(pady=(10, 20))
            
            # 인사말 템플릿
            templates_frame = ctk.CTkFrame(
                main_frame,
                fg_color="transparent"
            )
            templates_frame.pack(pady=10)
            
            templates = [
                "안녕하세요! 매칭되어서 반가워요 😊",
                "안녕하세요! 인사드려요~ 💕",
                "안녕하세요! 앞으로 잘 부탁드려요! ✨",
                "안녕하세요! 친하게 지내요~ 🌸"
            ]
            
            for i, template in enumerate(templates):
                template_btn = ctk.CTkButton(
                    templates_frame,
                    text=template,
                    font=("Pretendard", 12),
                    fg_color=self.colors['light_gray'],
                    hover_color=self.colors['secondary'],
                    text_color=self.colors['dark_gray'],
                    width=400,
                    height=35,
                    corner_radius=15,
                    command=lambda t=template: self.fill_greeting_text(t, greeting_text)
                )
                template_btn.pack(pady=5)
            
            # 직접 입력 텍스트 박스
            greeting_label = ctk.CTkLabel(
                main_frame,
                text="또는 직접 입력하기:",
                font=("Pretendard", 14),
                text_color=self.colors['text']
            )
            greeting_label.pack(pady=(20, 5))
            
            greeting_text = ctk.CTkTextbox(
                main_frame,
                width=400,
                height=100,
                font=("Pretendard", 12),
                corner_radius=10
            )
            greeting_text.pack(pady=10)
            
            # 버튼 프레임
            btn_frame = ctk.CTkFrame(
                main_frame,
                fg_color="transparent"
            )
            btn_frame.pack(pady=10)
            
            # 보내기 버튼
            send_button = ctk.CTkButton(
                btn_frame,
                text="💌 보내기",
                font=("Pretendard", 14),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                width=150,
                height=40,
                corner_radius=20,
                command=lambda: self.send_greeting_message(greeting_text.get("1.0", "end-1c"), matched_user, greeting_window, window)
            )
            send_button.pack(side="left", padx=5)
            
            # 취소 버튼
            cancel_button = ctk.CTkButton(
                btn_frame,
                text="취소",
                font=("Pretendard", 14),
                fg_color=self.colors['light_gray'],
                hover_color=self.colors['gray'],
                text_color=self.colors['dark_gray'],
                width=150,
                height=40,
                corner_radius=20,
                command=greeting_window.destroy
            )
            cancel_button.pack(side="left", padx=5)
            
        except Exception as e:
            print(f"첫 인사 보내기 화면 표시 중 오류: {str(e)}")
            traceback.print_exc()

    def fill_greeting_text(self, text, textbox):
        """인사말 템플릿을 텍스트 박스에 채우기"""
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)

    def send_greeting_message(self, message, matched_user, greeting_window, success_window):
        """인사 메시지 보내기"""
        try:
            if not message.strip():
                messagebox.showwarning("알림", "인사말을 입력해주세요.")
                return
            
            # 여기서는 실제 메시지 전송 기능 대신 알림만 표시
            # 실제 구현 시에는 Firebase에 메시지를 저장하거나 다른 방식으로 전달
            messagebox.showinfo(
                "전송 완료",
                f"💌 {matched_user.get('nickname', '친구')}님에게 인사말을 보냈습니다!\n\n"
                f"인스타그램(@{matched_user.get('instagram', '')})에서 확인해주세요."
            )
            
            greeting_window.destroy()
            success_window.destroy()
            self.show_notifications()
            
        except Exception as e:
            print(f"인사 메시지 전송 중 오류: {str(e)}")
            messagebox.showerror("오류", "메시지 전송 중 오류가 발생했습니다.")

    def show_matched_friends(self):
        """매칭된 친구 목록 표시"""
        try:
            # 매칭된 친구 창 생성
            friends_window = ctk.CTkToplevel(self.root)
            friends_window.title("💕 매칭된 친구")
            friends_window.geometry("700x600")
            friends_window.transient(self.root)
            friends_window.grab_set()
            friends_window.configure(fg_color=self.colors['background'])
            
            # 메인 프레임
            main_frame = ctk.CTkFrame(
                friends_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 제목
            title_label = ctk.CTkLabel(
                main_frame,
                text="💕 매칭된 친구",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors["primary"]
            )
            title_label.pack(pady=(10, 20))
            
            # 스크롤 가능한 프레임
            scrollable_frame = ctk.CTkScrollableFrame(
                main_frame,
                fg_color=self.colors['background'],
                width=650,
                height=450
            )
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 현재 사용자 ID
            user_id = self.profile_data.get('user_id')
            if not user_id:
                raise Exception("사용자 ID를 찾을 수 없습니다.")
            
            # 매칭 목록 가져오기
            matchings = self.firebase_manager.get_matchings_for_user(user_id)
            
            # 수락된 매칭만 필터링
            accepted_matchings = [m for m in matchings if m.get('status') == 'accepted']
            
            if not accepted_matchings:
                # 매칭된 친구가 없는 경우
                no_friends_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="아직 매칭된 친구가 없습니다 💕\n친구 찾기를 통해 새로운 인연을 찾아보세요!",
                    font=("Pretendard", 16),
                    text_color=self.colors["dark_gray"],
                    wraplength=500
                )
                no_friends_label.pack(pady=50)
            else:
                # 매칭 통계 표시
                stats_label = ctk.CTkLabel(
                    scrollable_frame,
                    text=f"총 {len(accepted_matchings)}명의 친구와 매칭되었습니다 ✨",
                    font=("Pretendard", 14, "bold"),
                    text_color=self.colors["primary"]
                )
                stats_label.pack(pady=(0, 15))
                
                # 모든 사용자 정보 가져오기
                all_users = self.firebase_manager.get_all_users()
                
                # 매칭된 친구 카드 표시
                for matching in accepted_matchings:
                    # 상대방 정보 찾기
                    other_id = matching['receiver_id'] if matching['sender_id'] == user_id else matching['sender_id']
                    other_instagram = matching['receiver_instagram'] if matching['sender_id'] == user_id else matching['sender_instagram']
                    
                    matched_user = None
                    for user in all_users:
                        if user.get('user_id') == other_id:
                            matched_user = user
                            break
                    
                    if not matched_user:
                        matched_user = {
                            'nickname': other_instagram,
                            'instagram': other_instagram,
                            'grade': '?',
                            'mbti': '?',
                            'gender': '?'
                        }
                    
                    # 친구 카드
                    friend_card = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color=self.colors['white'],
                        corner_radius=15
                    )
                    friend_card.pack(fill="x", padx=10, pady=8)
                    
                    # 카드 내용 프레임
                    card_content = ctk.CTkFrame(
                        friend_card,
                        fg_color="transparent"
                    )
                    card_content.pack(fill="x", padx=20, pady=15)
                    
                    # 친구 이름
                    friend_name = ctk.CTkLabel(
                        card_content,
                        text=f"💝 {matched_user.get('nickname', '알 수 없음')}",
                        font=("Pretendard", 18, "bold"),
                        text_color=self.colors['title']
                    )
                    friend_name.pack(anchor="w", pady=(0, 8))
                    
                    # 친구 정보
                    info_text = f"📷 @{matched_user.get('instagram', '알 수 없음')}  |  "
                    info_text += f"📚 {matched_user.get('grade', '?')}학년  |  "
                    info_text += f"🎭 {matched_user.get('mbti', '?')}"
                    
                    friend_info = ctk.CTkLabel(
                        card_content,
                        text=info_text,
                        font=("Pretendard", 12),
                        text_color=self.colors['text']
                    )
                    friend_info.pack(anchor="w", pady=(0, 10))
                    
                    # 매칭 날짜
                    matched_date = matching.get('matched_at', matching.get('created_at', ''))
                    if matched_date:
                        date_label = ctk.CTkLabel(
                            card_content,
                            text=f"매칭일: {matched_date.split()[0] if ' ' in matched_date else matched_date}",
                            font=("Pretendard", 10),
                            text_color=self.colors['gray']
                        )
                        date_label.pack(anchor="w", pady=(0, 10))
                    
                    # 버튼 프레임
                    button_frame = ctk.CTkFrame(
                        card_content,
                        fg_color="transparent"
                    )
                    button_frame.pack(fill="x", pady=(5, 0))
                    
                    # 인스타그램 보기 버튼
                    insta_btn = ctk.CTkButton(
                        button_frame,
                        text="📱 인스타그램",
                        font=("Pretendard", 11),
                        fg_color=self.colors['button'],
                        hover_color=self.colors['button_hover'],
                        width=120,
                        height=30,
                        corner_radius=15,
                        command=lambda insta=matched_user.get('instagram', ''): self.open_instagram(insta)
                    )
                    insta_btn.pack(side="left", padx=5)
                    
                    # 1:1 채팅하기 버튼
                    chat_btn = ctk.CTkButton(
                        button_frame,
                        text="💬 1:1 채팅하기",
                        font=("Pretendard", 11),
                        fg_color=self.colors['accent'],
                        hover_color=self.colors['secondary'],
                        text_color=self.colors['text'],
                        width=130,
                        height=30,
                        corner_radius=15,
                        command=lambda user=matched_user, other_id=other_id: self.open_chat(user, other_id)
                    )
                    chat_btn.pack(side="left", padx=5)
            
            # 닫기 버튼
            close_button = ctk.CTkButton(
                main_frame,
                text="닫기",
                font=("Pretendard", 14),
                fg_color=self.colors['light_gray'],
                hover_color=self.colors['gray'],
                text_color=self.colors['dark_gray'],
                width=150,
                height=40,
                corner_radius=20,
                command=friends_window.destroy
            )
            close_button.pack(pady=15)
            
        except Exception as e:
            print(f"매칭된 친구 목록 표시 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", "매칭된 친구 목록을 불러오는 중 오류가 발생했습니다.")

    def open_chat(self, matched_user, other_user_id):
        """1:1 채팅 창 열기"""
        try:
            current_user_id = self.profile_data.get('user_id')
            if not current_user_id:
                messagebox.showerror("오류", "사용자 정보를 찾을 수 없습니다.")
                return
            
            # 읽지 않은 메시지를 읽음으로 표시
            self.firebase_manager.mark_messages_as_read(current_user_id, other_user_id)
            # 읽지 않은 메시지 수 업데이트
            self.update_unread_message_count()
            
            # 채팅 창 생성 (tkinter Toplevel 사용 - 입력 필드가 확실하게 작동)
            chat_window = tk.Toplevel(self.root)
            chat_window.title(f"💬 {matched_user.get('nickname', '친구')}님과의 채팅")
            chat_window.geometry("600x700")
            chat_window.transient(self.root)
            chat_window.configure(bg=self.colors['background'])
            # grab_set() 제거 - 입력을 막을 수 있음
            
            # 상단 헤더 (tkinter Frame 사용)
            header_frame = tk.Frame(
                chat_window,
                bg=self.colors['primary'],
                height=60
            )
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)
            
            # 닫기 버튼
            close_btn = tk.Button(
                header_frame,
                text="✕",
                font=("Pretendard", 16, "bold"),
                bg=self.colors['primary'],
                fg="#FFFFFF",
                relief="flat",
                command=chat_window.destroy,
                cursor="hand2"
            )
            close_btn.pack(side="right", padx=10, pady=10)
            
            # 친구 정보
            friend_info = tk.Label(
                header_frame,
                text=f"💕 {matched_user.get('nickname', '친구')}님",
                font=("Pretendard", 18, "bold"),
                bg=self.colors['primary'],
                fg="#FFFFFF"
            )
            friend_info.pack(pady=15)
            
            # 메시지 표시 영역 (tkinter Frame + Canvas + Scrollbar)
            messages_container_frame = tk.Frame(chat_window, bg=self.colors['white'])
            messages_container_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 스크롤바
            scrollbar = tk.Scrollbar(messages_container_frame)
            scrollbar.pack(side="right", fill="y")
            
            # Canvas
            canvas = tk.Canvas(
                messages_container_frame,
                bg=self.colors['white'],
                yscrollcommand=scrollbar.set,
                highlightthickness=0
            )
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=canvas.yview)
            
            # 스크롤 가능한 프레임
            messages_frame = tk.Frame(canvas, bg=self.colors['white'])
            canvas_window = canvas.create_window((0, 0), window=messages_frame, anchor="nw")
            
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            messages_frame.bind("<Configure>", configure_scroll_region)
            
            def on_canvas_configure(event):
                canvas_width = event.width
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            canvas.bind("<Configure>", on_canvas_configure)
            
            # 메시지 로드 및 표시
            self.messages_container = messages_frame
            self.messages_canvas = canvas
            self.current_chat_user_id = other_user_id
            self.current_chat_window = chat_window
            
            # 기존 메시지 로드
            self.load_chat_messages(current_user_id, other_user_id)
            
            # 하단 입력 영역 (tkinter로 완전히 구성 - 확실하게 작동)
            input_frame = tk.Frame(
                chat_window,
                bg="#FFFFFF",
                relief="flat"
            )
            input_frame.pack(fill="x", padx=10, pady=10)
            
            # 입력 필드와 버튼을 담을 내부 프레임
            inner_frame = tk.Frame(
                input_frame,
                bg="#FFFFFF"
            )
            inner_frame.pack(fill="x", padx=10, pady=10)
            
            # 메시지 입력 필드 (tkinter Entry 사용 - 확실하게 작동)
            message_entry = tk.Entry(
                inner_frame,
                font=("Pretendard", 14),
                width=50,
                relief="solid",
                bg="#FFFFFF",
                fg="#000000",
                insertbackground="#000000",
                borderwidth=2,
                highlightthickness=0
            )
            message_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True, ipady=10)
            
            # 플레이스홀더 기능
            placeholder_text = "메시지를 입력하세요..."
            
            def on_entry_focus_in(event):
                if message_entry.get() == placeholder_text:
                    message_entry.delete(0, "end")
                    message_entry.config(fg="#000000")
            
            def on_entry_focus_out(event):
                if message_entry.get() == "":
                    message_entry.insert(0, placeholder_text)
                    message_entry.config(fg="#808080")
            
            # 초기 플레이스홀더 설정
            message_entry.insert(0, placeholder_text)
            message_entry.config(fg="#808080")
            message_entry.bind("<FocusIn>", on_entry_focus_in)
            message_entry.bind("<FocusOut>", on_entry_focus_out)
            
            # 입력 필드 클릭 이벤트
            def on_entry_click(event):
                message_entry.focus_set()
                if message_entry.get() == placeholder_text:
                    message_entry.delete(0, "end")
                    message_entry.config(fg="#000000")
                message_entry.icursor("end")
            
            message_entry.bind("<Button-1>", on_entry_click)
            
            # 프레임 클릭 시에도 포커스
            def on_frame_click(event):
                message_entry.focus_set()
                if message_entry.get() == placeholder_text:
                    message_entry.delete(0, "end")
                    message_entry.config(fg="#000000")
                message_entry.icursor("end")
            
            inner_frame.bind("<Button-1>", on_frame_click)
            input_frame.bind("<Button-1>", on_frame_click)
            
            # 전송 버튼 (tkinter Button 사용)
            send_button = tk.Button(
                inner_frame,
                text="전송",
                font=("Pretendard", 14, "bold"),
                bg=self.colors['button'],
                fg="#FFFFFF",
                relief="flat",
                width=10,
                height=2,
                cursor="hand2",
                command=lambda: self.send_chat_message(message_entry, current_user_id, other_user_id, matched_user)
            )
            send_button.pack(side="left", padx=5, pady=5)
            
            # Enter 키로 전송
            def on_enter(event):
                send_button.invoke()
                return "break"
            
            message_entry.bind("<Return>", on_enter)
            
            # 창이 열릴 때 포커스 설정
            def set_focus():
                try:
                    chat_window.focus_force()
                    chat_window.lift()
                    chat_window.update()
                    message_entry.focus_set()
                except Exception as e:
                    print(f"포커스 설정 오류: {e}")
            
            # 여러 시점에 포커스 설정 시도
            chat_window.after(100, set_focus)
            chat_window.after(300, set_focus)
            
            # 입력 필드가 항상 활성화되도록 보장
            message_entry.config(state="normal")
            
        except Exception as e:
            error_msg = f"채팅 창 열기 중 오류 발생: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            messagebox.showerror("오류", "채팅 창을 열 수 없습니다.")

    def load_chat_messages(self, user_id, other_user_id):
        """채팅 메시지 로드 및 표시"""
        try:
            # 기존 메시지 제거
            for widget in self.messages_container.winfo_children():
                widget.destroy()
            
            # 메시지 가져오기
            messages = self.firebase_manager.get_messages(user_id, other_user_id)
            
            if not messages:
                # 메시지가 없는 경우
                no_msg_label = tk.Label(
                    self.messages_container,
                    text="아직 주고받은 메시지가 없습니다.\n첫 메시지를 보내보세요! 💬",
                    font=("Pretendard", 14),
                    bg=self.colors['white'],
                    fg=self.colors['gray'],
                    wraplength=500,
                    justify="center"
                )
                no_msg_label.pack(pady=50)
                # Canvas 스크롤 영역 업데이트
                if hasattr(self, 'messages_canvas'):
                    self.messages_canvas.update_idletasks()
                    self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
                return
            
            # 메시지 표시
            for msg in messages:
                is_sender = msg['sender_id'] == user_id
                self.display_message(msg, is_sender)
            
            # 스크롤을 맨 아래로
            self.messages_container.update_idletasks()
            if hasattr(self, 'messages_canvas'):
                self.messages_canvas.update_idletasks()
                self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
                self.messages_canvas.yview_moveto(1.0)
            
        except Exception as e:
            print(f"메시지 로드 중 오류 발생: {str(e)}")
            traceback.print_exc()

    def display_message(self, message_data, is_sender):
        """메시지 표시"""
        try:
            # 메시지 프레임
            msg_frame = tk.Frame(
                self.messages_container,
                bg=self.colors['white']
            )
            msg_frame.pack(fill="x", padx=10, pady=5)
            
            if is_sender:
                # 내가 보낸 메시지 (오른쪽 정렬)
                msg_frame.pack(anchor="e")
                msg_bubble = tk.Frame(
                    msg_frame,
                    bg=self.colors['button'],
                    relief="flat"
                )
                msg_bubble.pack(anchor="e", padx=(100, 0))
            else:
                # 받은 메시지 (왼쪽 정렬)
                msg_frame.pack(anchor="w")
                msg_bubble = tk.Frame(
                    msg_frame,
                    bg=self.colors['light_gray'],
                    relief="flat"
                )
                msg_bubble.pack(anchor="w", padx=(0, 100))
            
            # 메시지 내용
            msg_text = message_data.get('message', '')
            msg_label = tk.Label(
                msg_bubble,
                text=msg_text,
                font=("Pretendard", 12),
                bg=self.colors['button'] if is_sender else self.colors['light_gray'],
                fg="#FFFFFF" if is_sender else self.colors['text'],
                wraplength=300,
                justify="left",
                padx=15,
                pady=10
            )
            msg_label.pack()
            
            # 시간 표시
            timestamp = message_data.get('timestamp', '')
            if timestamp:
                time_str = timestamp.split()[1][:5] if ' ' in timestamp else timestamp[:5]
                time_label = tk.Label(
                    msg_frame,
                    text=time_str,
                    font=("Pretendard", 9),
                    bg=self.colors['white'],
                    fg=self.colors['gray']
                )
                if is_sender:
                    time_label.pack(anchor="e", padx=(100, 5))
                else:
                    time_label.pack(anchor="w", padx=(5, 100))
                    
        except Exception as e:
            print(f"메시지 표시 중 오류 발생: {str(e)}")

    def send_chat_message(self, message_entry, sender_id, receiver_id, matched_user):
        """채팅 메시지 전송"""
        try:
            # tkinter Entry에서 텍스트 가져오기
            message_text = message_entry.get().strip()
            
            # 플레이스홀더 텍스트는 무시
            if not message_text or message_text == "메시지를 입력하세요...":
                return
            
            # 메시지 저장
            message_id = self.firebase_manager.save_message(sender_id, receiver_id, message_text)
            if message_id:
                # 입력 필드 초기화 및 플레이스홀더 복원
                message_entry.delete(0, "end")
                message_entry.insert(0, "메시지를 입력하세요...")
                message_entry.config(fg="#808080")
                
                # 메시지 목록 새로고침
                self.load_chat_messages(sender_id, receiver_id)
                
                # 읽지 않은 메시지 수 업데이트
                self.update_unread_message_count()
                
                # 포커스 다시 설정
                message_entry.focus_set()
            else:
                messagebox.showerror("오류", "메시지 전송에 실패했습니다.")
                
        except Exception as e:
            print(f"메시지 전송 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", "메시지 전송 중 오류가 발생했습니다.")

    def show_notifications(self):
        """알림 창 표시"""
        # 알림 창 생성
        notification_window = ctk.CTkToplevel(self.root)
        notification_window.title("💌 나에게 온 알림")
        notification_window.geometry("600x400")
        notification_window.transient(self.root)
        notification_window.grab_set()
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            notification_window,
            fg_color=self.colors['background']
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="💌 나에게 온 알림",
            font=("Pretendard", 20, "bold"),
            text_color=self.colors["primary"]
        )
        title_label.pack(pady=20)
        
        try:
            # 현재 사용자의 매칭 요청 조회
            user_id = self.profile_data.get('user_id')
            if not user_id:
                raise Exception("사용자 ID를 찾을 수 없습니다.")
            
            matchings = self.firebase_manager.get_matchings_for_user(user_id)
            
            if not matchings:
                # 알림이 없는 경우
                no_notifications_label = ctk.CTkLabel(
                    main_frame,
                    text="아직 도착한 알림이 없습니다 💌",
                    font=("Pretendard", 14),
                    text_color=self.colors["dark_gray"]
                )
                no_notifications_label.pack(pady=30)
                return
            
            # 알림 목록 표시
            for matching in matchings:
                # 매칭 카드 프레임
                card_frame = ctk.CTkFrame(
                    main_frame,
                    fg_color=self.colors["light_gray"],
                    corner_radius=10
                )
                card_frame.pack(fill="x", padx=10, pady=5)
                
                # 매칭 정보 텍스트
                is_sender = matching['sender_id'] == user_id
                other_instagram = matching['receiver_instagram'] if is_sender else matching['sender_instagram']
                status = matching['status']
                
                # 상태에 따른 메시지 설정
                if is_sender:
                    if status == 'pending':
                        message = f"✉️ {other_instagram}님에게 보낸 매칭 요청을 기다리는 중입니다."
                    elif status == 'accepted':
                        message = f"✨ {other_instagram}님이 매칭 요청을 수락했습니다!"
                    else:  # rejected
                        message = f"😢 {other_instagram}님이 매칭 요청을 거절했습니다."
                else:
                    if status == 'pending':
                        message = f"💝 {other_instagram}님이 매칭을 요청했습니다!"
                    elif status == 'accepted':
                        message = f"✨ {other_instagram}님과 매칭이 성사되었습니다!"
                    else:  # rejected
                        message = f"💔 {other_instagram}님의 매칭 요청을 거절했습니다."
                
                # 메시지 라벨
                message_label = ctk.CTkLabel(
                    card_frame,
                    text=message,
                    font=("Pretendard", 14),
                    text_color=self.colors["dark_gray"]
                )
                message_label.pack(pady=10, padx=15)
                
                # 보류 중인 요청에 대한 수락/거절 버튼 추가
                if not is_sender and status == 'pending':
                    button_frame = ctk.CTkFrame(
                        card_frame,
                        fg_color="transparent"
                    )
                    button_frame.pack(pady=(0, 10))
                    
                    # 수락 버튼
                    accept_button = ctk.CTkButton(
                        button_frame,
                        text="수락",
                        font=("Pretendard", 12),
                        fg_color=self.colors["primary"],
                        hover_color=self.colors["secondary"],
                        width=80,
                        command=lambda m=matching: self.handle_matching_response(m, 'accepted', notification_window)
                    )
                    accept_button.pack(side="left", padx=5)
                    
                    # 거절 버튼
                    reject_button = ctk.CTkButton(
                        button_frame,
                        text="거절",
                        font=("Pretendard", 12),
                        fg_color=self.colors["gray"],
                        hover_color=self.colors["dark_gray"],
                        width=80,
                        command=lambda m=matching: self.handle_matching_response(m, 'rejected', notification_window)
                    )
                    reject_button.pack(side="left", padx=5)
        
        except Exception as e:
            print(f"알림 조회 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "알림을 불러오는 중 오류가 발생했습니다.")
            notification_window.destroy()

    def handle_matching_response(self, matching, response, window):
        """매칭 요청 응답 처리"""
        try:
            # 매칭 상태 업데이트
            matching['status'] = response
            # 수락 시 매칭 날짜 추가
            if response == 'accepted' and 'matched_at' not in matching:
                matching['matched_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.firebase_manager.update_matching(matching):
                # 알림 창 닫기
                window.destroy()
                
                if response == 'accepted':
                    # 매칭 성사 축하 화면 표시
                    self.show_matching_success_screen(matching)
                else:
                    messagebox.showinfo("알림", "매칭 요청을 거절했습니다.")
                self.show_notifications()
            else:
                raise Exception("매칭 상태 업데이트 실패")
                
        except Exception as e:
            print(f"매칭 응답 처리 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "매칭 응답 처리 중 오류가 발생했습니다.")

    def start_matching_from_428(self):
        """428줄부터 매칭 로직 실행"""
        try:
            print("매칭 시작...")  # 디버깅 로그
            
            # 프로필 데이터가 없는 경우 체크
            if not hasattr(self, 'profile_data') or not self.profile_data:
                print("프로필 데이터 없음:", getattr(self, 'profile_data', None))  # 디버깅 로그
                messagebox.showerror("오류", "프로필 정보가 없습니다. 프로필을 먼저 생성해주세요.")
                return
                
            print("현재 프로필 데이터:", self.profile_data)  # 디버깅 로그
                
            # 새 창 생성
            matching_window = ctk.CTkToplevel()
            matching_window.title("💕 능주고등학교 선후배 매칭 💕")
            matching_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
            matching_window.configure(fg_color=self.colors["matching_bg"])  # 매칭 화면만 연한 분홍색 배경
            
            # 모달 창으로 설정
            matching_window.transient(self.root)  # 부모 창 설정
            matching_window.grab_set()  # 모달 모드 설정
            
            # 로딩 메시지
            loading_label = ctk.CTkLabel(
                matching_window,
                text="✨ 매칭 시스템 준비중... ✨",
                font=("Pretendard", 20, "bold"),
                text_color="#FF6B6B"
            )
            loading_label.pack(pady=50)
            matching_window.update()
            
            try:
                # 현재 프로필 정보 설정
                student_data = {
                    'user_id': self.profile_data.get('user_id'),  # 실제 user_id 사용
                    'instagram': self.profile_data.get('instagram', ''),
                    'name': self.profile_data.get('name', ''),
                    'nickname': self.profile_data.get('nickname', ''),
                    'grade': int(self.profile_data.get('grade', '1').replace('학년', '')),
                    'gender': self.profile_data.get('gender', ''),
                    'mbti': self.profile_data.get('mbti', ''),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print("매칭에 사용될 학생 데이터:", student_data)  # 디버깅 로그
                
                # 오늘의 매칭 시도 횟수 확인
                today = datetime.now().strftime("%Y-%m-%d")
                matching_attempts = self.firebase_manager.get_matching_attempts(student_data['user_id'], today)
                
                if matching_attempts >= 5:
                    messagebox.showwarning(
                        "매칭 제한",
                        "오늘의 매칭 횟수를 모두 사용했습니다.\n내일 다시 시도해주세요!"
                    )
                    matching_window.destroy()
                    return
                
                # StudentMatchingApp 인스턴스 생성
                app = StudentMatchingApp(matching_window)
                app.matching_attempts = matching_attempts  # 매칭 시도 횟수 설정
                
                # 앱 초기화
                app.initialize(student_data)
                
                # 로딩 라벨 제거
                loading_label.destroy()
                
            except Exception as e:
                print("데이터 변환 중 오류:", str(e))  # 디버깅 로그
                raise
            
        except Exception as e:
            print("매칭 시스템 오류:", str(e))  # 디버깅 로그
            print("오류 발생 위치:", e.__traceback__.tb_lineno)  # 오류 발생 라인 번호
            messagebox.showerror("오류", f"매칭 시스템 실행 중 오류가 발생했습니다:\n{str(e)}")
            if 'matching_window' in locals():
                matching_window.destroy()

    def show_privacy_consent(self):
        """개인정보 동의 화면 표시"""
        # 개인정보 동의 팝업
        consent_window = ctk.CTkToplevel(self.root)
        consent_window.title("개인정보 이용 동의")
        consent_window.geometry("600x700")
        consent_window.configure(fg_color=self.colors['background'])
        
        consent_window.transient(self.root)  # 메인 창의 자식 창으로 설정
        consent_window.grab_set()  # 모달 창으로 설정
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            consent_window,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="개인정보 이용 동의",
            font=("Pretendard", 32, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(0, 40))
        
        # 동의 내용 프레임
        content_frame = ctk.CTkFrame(
            main_frame, 
            fg_color=self.colors['white'],
            corner_radius=15
        )
        content_frame.pack(fill="both", expand=True, pady=(0, 40))
        
        # 개인정보 동의 텍스트
        consent_text = """
< 능친 만들기 >

귀하의 소중한 개인정보를 수집, 이용, 활용하고자
개인정보보호법에 따라 동의를 얻고 있습니다.

본인의 개인정보를 제공하는 것에 대해
동의해주시겠습니까?

개인정보는 친구 매칭을 위한 목적 외에는
사용되지 않음을 알려드리며,

개인정보 수집에 비동의할 시
프로그램 이용이 어려울 수 있습니다."""
        
        text_label = ctk.CTkLabel(
            content_frame,
            text=consent_text,
            font=("Pretendard", 20),
            text_color=self.colors['text'],
            justify="center",
            wraplength=450
        )
        text_label.pack(pady=50, padx=30)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 30))
        
        # 동의 버튼
        agree_button = ctk.CTkButton(
            button_frame,
            text="동의",
            font=("Pretendard", 20),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: [consent_window.destroy(), self.show_profile_input()]
        )
        agree_button.pack(side='left', padx=10)
        
        # 비동의 버튼
        disagree_button = ctk.CTkButton(
            button_frame,
            text="비동의",
            font=("Pretendard", 20),
            fg_color='transparent',
            hover_color=self.colors['button_hover'],
            text_color=self.colors['text'],
            border_color=self.colors['button'],
            border_width=2,
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: [
                messagebox.showwarning(
                    "알림",
                    "서비스 이용이 불가합니다.",
                    font=("Pretendard", 20)
                ),
                consent_window.destroy()
            ]
        )
        disagree_button.pack(side='left', padx=10)

    def show_profile_input(self):
        """프로필 입력 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 프로필 입력 프레임
        profile_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        profile_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ctk.CTkLabel(
            profile_frame,
            text="프로필 입력",
            font=("Pretendard", 24, "bold")
        )
        title_label.pack(pady=20)
        
        # 성별 선택
        gender_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        gender_frame.pack(pady=10)
        
        gender_label = ctk.CTkLabel(
            gender_frame,
            text="성별을 선택해주세요",
            font=("Pretendard", 14)
        )
        gender_label.pack()
        
        self.gender_var = tk.StringVar()
        male_btn = ctk.CTkRadioButton(
            gender_frame,
            text="남자",
            variable=self.gender_var,
            value="남자",
            font=("Pretendard", 12)
        )
        male_btn.pack(side="left", padx=10)
        
        female_btn = ctk.CTkRadioButton(
            gender_frame,
            text="여자",
            variable=self.gender_var,
            value="여자",
            font=("Pretendard", 12)
        )
        female_btn.pack(side="left", padx=10)
        
        # 학년 선택
        grade_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        grade_frame.pack(pady=10)
        
        grade_label = ctk.CTkLabel(
            grade_frame,
            text="학년을 선택해주세요",
            font=("Pretendard", 14)
        )
        grade_label.pack()
        
        self.grade_var = tk.StringVar()
        grades = ["1학년", "2학년", "3학년"]
        for grade in grades:
            grade_btn = ctk.CTkRadioButton(
                grade_frame,
                text=grade,
                variable=self.grade_var,
                value=grade,
                font=("Pretendard", 12)
            )
            grade_btn.pack(side="left", padx=10)

        # 이름 입력
        name_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        name_frame.pack(pady=10)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text="이름을 입력해주세요",
            font=("Pretendard", 14)
        )
        name_label.pack()
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            width=200,
            font=("Pretendard", 12),
            placeholder_text="본인 이름 입력"
        )
        self.name_entry.pack(pady=5)
        
        # 별명 입력
        nickname_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        nickname_frame.pack(pady=10)
        
        nickname_label = ctk.CTkLabel(
            nickname_frame,
            text="별명을 입력해주세요",
            font=("Pretendard", 14)
        )
        nickname_label.pack()
        
        # 별명 입력 및 중복확인 버튼을 위한 하위 프레임
        nickname_input_frame = ctk.CTkFrame(nickname_frame, fg_color="transparent")
        nickname_input_frame.pack(pady=5)
        
        self.nickname_entry = ctk.CTkEntry(
            nickname_input_frame,
            width=200,
            font=("Pretendard", 12),
            placeholder_text="별명 입력"
        )
        self.nickname_entry.pack(side="left", padx=(0, 10))
        
        # 중복확인 버튼
        self.check_nickname_button = ctk.CTkButton(
            nickname_input_frame,
            text="중복확인",
            font=("Pretendard", 12),
            width=80,
            command=self.check_nickname_duplicate
        )
        self.check_nickname_button.pack(side="left")
        
        # 중복확인 완료 여부
        self.nickname_checked = False
        
        # 별명 입력 필드 변경 감지
        def on_nickname_change(event=None):
            if self.nickname_checked:
                self.nickname_checked = False
                self.check_nickname_button.configure(
                    text="중복확인",
                    fg_color=["#3a7ebf", "#1f538d"]
                )
        
        self.nickname_entry.bind('<KeyRelease>', on_nickname_change)
        
        # 인스타그램 아이디 입력
        insta_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        insta_frame.pack(pady=10)
        
        insta_label = ctk.CTkLabel(
            insta_frame,
            text="인스타그램 아이디를 입력해주세요",
            font=("Pretendard", 14)
        )
        insta_label.pack()
        
        # 인스타그램 아이디 입력 필드
        self.insta_entry = ctk.CTkEntry(
            insta_frame,
            width=200,
            font=("Pretendard", 12)
        )
        self.insta_entry.pack(pady=5)
        self.insta_entry.insert(0, '@')  # 초기값으로 @ 설정
        
        # 입력 내용이 변경될 때마다 호출되는 함수
        def on_insta_change(event=None):
            current_text = self.insta_entry.get()
            cursor_position = self.insta_entry.index(tk.INSERT)
            
            if not current_text.startswith('@'):
                self.insta_entry.delete(0, tk.END)
                self.insta_entry.insert(0, '@' + current_text.replace('@', ''))
                self.insta_entry.icursor(cursor_position + 1)
            
            if current_text == '@':
                self.insta_entry.icursor(1)
                
        self.insta_entry.bind('<KeyRelease>', on_insta_change)
        
        # 백스페이스로 @ 삭제 방지
        def prevent_at_deletion(event):
            if event.keysym == 'BackSpace' and self.insta_entry.index(tk.INSERT) <= 1:
                return 'break'
            
        self.insta_entry.bind('<Key>', prevent_at_deletion)
        
        # 다음 버튼
        next_button = ctk.CTkButton(
            profile_frame,
            text="다음",
            font=("Pretendard", 14),
            command=self.validate_profile
        )
        next_button.pack(pady=20)
        
    def validate_profile(self):
        """프로필 정보 유효성 검사 및 저장"""
        # 성별 선택 확인
        if not self.gender_var.get():
            messagebox.showerror("오류", "성별을 선택해주세요.")
            return
            
        # 학년 선택 확인
        if not self.grade_var.get():
            messagebox.showerror("오류", "학년을 선택해주세요.")
            return
            
        # 별명 입력 확인
        nickname = self.nickname_entry.get().strip()
        if not nickname:
            messagebox.showerror("오류", "별명을 입력해주세요.")
            return
            
        # 별명 중복 확인 여부 체크
        if not self.nickname_checked:
            messagebox.showerror("오류", "별명 중복 확인을 해주세요.")
            return
            
        # 인스타그램 아이디 확인
        instagram_id = self.insta_entry.get().strip()
        if not instagram_id or instagram_id == '@':
            messagebox.showerror("오류", "인스타그램 아이디를 입력해주세요.")
            return
            
        # 이름 확인
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("오류", "이름을 입력해주세요.")
            return

        # 이름과 인스타그램 아이디 동시 중복 확인
        try:
            users = self.firebase_manager.get_all_users()
            instagram_id_clean = instagram_id.replace('@', '').lower()
            name_clean = name.lower()

            for user in users:
                user_instagram = user.get('instagram', '').lower()
                user_name = user.get('name', '').lower()
                
                if user_instagram == instagram_id_clean and user_name == name_clean:
                    messagebox.showerror(
                        "오류",
                        "이미 존재하는 프로필입니다.\n기존 프로필로 로그인해주세요."
                    )
                    return

        except Exception as e:
            print(f"프로필 중복 확인 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "프로필 확인 중 오류가 발생했습니다.")
            return
            
        # 임시로 프로필 정보 저장
        self.temp_profile = {
            'gender': self.gender_var.get(),
            'grade': self.grade_var.get(),
            'nickname': nickname,
            'instagram': instagram_id,
            'name': name
        }
        
        # MBTI 테스트 시작
        self.show_mbti_test()

    def check_nickname_duplicate(self):
        """별명 중복 확인"""
        nickname = self.nickname_entry.get().strip()
        if not nickname:
            messagebox.showerror("오류", "별명을 입력해주세요.")
            return

        firebase_manager = FirebaseManager()
        if firebase_manager.check_nickname_exists(nickname):
            messagebox.showerror(
                "오류", 
                "이미 사용 중인 별명입니다.\n다른 별명을 입력해주세요."
            )
            self.nickname_entry.delete(0, tk.END)
            self.nickname_entry.focus()
            self.nickname_checked = False
        else:
            messagebox.showinfo("확인", "사용 가능한 별명입니다!")
            self.nickname_checked = True
            self.check_nickname_button.configure(
                text="✓",
                fg_color=["#2ecc71", "#27ae60"]  # 초록색 계열
            )

    def show_mbti_test(self):
        """MBTI 테스트 창 생성"""
        # MBTI 테스트 창 생성
        test_window = ctk.CTkToplevel(self.root)
        test_window.title("MBTI 성격유형 테스트")
        test_window.geometry("800x800")  # 창 크기 증가
        test_window.transient(self.root)  # 메인 창의 자식 창으로 설정
        test_window.grab_set()  # 모달 창으로 설정
        
        # MBTI 테스트 인스턴스 생성
        self.mbti_test = MBTITest(test_window, self.on_mbti_result)
        
    def on_mbti_result(self, mbti_result):
        """MBTI 테스트 결과 처리"""
        try:
            # 프로필 정보에 MBTI 결과 추가
            self.temp_profile['mbti'] = mbti_result
            
            # Firebase에 저장할 데이터 준비
            profile_data = {
                'gender': self.temp_profile['gender'],
                'grade': self.temp_profile['grade'].replace('학년', ''),  # '1학년' -> '1'
                'nickname': self.temp_profile['nickname'],
                'instagram': self.temp_profile['instagram'].replace('@', ''),  # @ 제거
                'mbti': self.temp_profile['mbti'],
                'name': self.temp_profile['name'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("Firebase에 저장할 프로필 데이터:", profile_data)  # 디버깅 로그
            
            # Firebase에 프로필 저장
            try:
                user_id = self.firebase_manager.save_profile(profile_data)
                if user_id:
                    print(f"Firebase에 프로필 저장 성공 (ID: {user_id})")  # 디버깅 로그
                    
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': user_id,
                        'nickname': profile_data['nickname'],
                        'instagram': profile_data['instagram'],
                        'grade': profile_data['grade'],
                        'gender': profile_data['gender'],
                        'mbti': profile_data['mbti'],
                        'name': profile_data['name']
                    }
                    
                    messagebox.showinfo("성공", "프로필이 저장되었습니다!")
                    self.show_home_screen()
                else:
                    raise Exception("Firebase 저장 실패: user_id가 반환되지 않음")
            except Exception as e:
                print(f"Firebase 저장 오류: {str(e)}")  # 디버깅 로그
                raise Exception(f"Firebase 저장 실패: {str(e)}")
        except Exception as e:
            error_msg = f"프로필 저장 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)  # 디버깅 로그
            messagebox.showerror("오류", error_msg)
            print("Error details:", e)  # 디버깅 로그

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FriendFinderApp()
    app.run() 