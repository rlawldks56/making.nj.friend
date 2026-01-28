import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CONFIG, COLLECTION_NAME, FIREBASE_TEST_MODE, DATABASE_URL
import uuid
from datetime import datetime
import json
import os
import traceback

class FirebaseManager:
    _instance = None
    TEST_DATA_FILE = "test_data.json"  # 테스트 데이터를 저장할 파일
    _initialized = False
    
    def __new__(cls, test_mode=None):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, test_mode=None):
        if self._initialized:
            return
            
        self.test_mode = test_mode if test_mode is not None else FIREBASE_TEST_MODE
        print(f"Firebase 매니저 초기화 (테스트 모드: {self.test_mode})")
        
        if self.test_mode:
            self.test_data = self.load_test_data()
            print("테스트 데이터 초기화 완료")
            self._initialized = True
            return

        try:
            # Firebase 앱이 이미 초기화되어 있는지 확인
            if not firebase_admin._apps:
                if not os.path.exists(FIREBASE_CONFIG):
                    raise FileNotFoundError(f"Firebase 설정 파일을 찾을 수 없습니다: {FIREBASE_CONFIG}")

                try:
                    cred = credentials.Certificate(FIREBASE_CONFIG)
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': DATABASE_URL
                    })
                    print("Firebase 앱 초기화 성공")
                except ValueError as ve:
                    print(f"Firebase 인증 정보가 올바르지 않습니다: {str(ve)}")
                    raise
                except Exception as e:
                    print(f"Firebase 초기화 중 오류 발생: {str(e)}")
                    raise

            # Firestore 클라이언트 생성
            try:
                self.db = firestore.client()
                print("Firestore 클라이언트 생성 성공")
            except Exception as e:
                print(f"Firestore 클라이언트 생성 실패: {str(e)}")
                raise

        except Exception as e:
            print("Firebase 연결 실패, 테스트 모드로 전환합니다.")
            print(f"오류 내용: {str(e)}")
            traceback.print_exc()
            self.test_mode = True
            self.test_data = self.load_test_data()

        self._initialized = True
        
    def load_test_data(self):
        """테스트 데이터 파일에서 데이터 불러오기"""
        try:
            if os.path.exists(self.TEST_DATA_FILE):
                with open(self.TEST_DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"테스트 데이터 파일 로드 완료: {len(data.get('students', []))}명의 학생 데이터")
                return data
        except Exception as e:
            print(f"테스트 데이터 파일 로드 실패: {str(e)}")
        
        # 파일이 없거나 로드 실패 시 기본 데이터 구조 반환
        return {
            'students': [],
            'matchings': []
        }

    def save_test_data(self):
        """테스트 데이터를 파일에 저장"""
        try:
            with open(self.TEST_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.test_data, f, ensure_ascii=False, indent=2)
            print("테스트 데이터 파일 저장 완료")
            return True
        except Exception as e:
            print(f"테스트 데이터 파일 저장 실패: {str(e)}")
            return False

    def save_profile(self, profile_data):
        """프로필 저장"""
        try:
            if self.test_mode:
                user_id = str(uuid.uuid4())
                profile_data['user_id'] = user_id
                self.test_data['students'].append(profile_data)
                self.save_test_data()
                print(f"테스트 모드: 프로필 저장 완료 (ID: {user_id})")
                return user_id
            else:
                # Firestore에 저장
                print("Firestore에 프로필 저장 시도...")
                print(f"저장할 데이터: {profile_data}")
                
                user_id = str(uuid.uuid4())
                doc_ref = self.db.collection('students').document(user_id)
                profile_data['user_id'] = user_id
                
                print(f"문서 경로: students/{user_id}")
                doc_ref.set(profile_data)
                print(f"Firestore 프로필 저장 완료 (ID: {user_id})")
                return user_id
        except Exception as e:
            print(f"프로필 저장 중 오류 발생: {str(e)}")
            print("오류 상세 정보:")
            traceback.print_exc()
            return None

    def get_all_users(self):
        """모든 사용자 조회"""
        try:
            if self.test_mode:
                return self.test_data['students']
            else:
                users = []
                docs = self.db.collection('students').stream()
                for doc in docs:
                    user_data = doc.to_dict()
                    user_data['user_id'] = doc.id
                    users.append(user_data)
                return users
        except Exception as e:
            print(f"사용자 조회 오류: {str(e)}")
            return []

    def save_matching(self, matching_data):
        """매칭 정보 저장"""
        try:
            if self.test_mode:
                matching_id = str(uuid.uuid4())
                matching_data['matching_id'] = matching_id
                self.test_data['matchings'].append(matching_data)
                self.save_test_data()  # 파일에 저장
                return True
            else:
                # Firestore에 저장
                matching_id = str(uuid.uuid4())
                doc_ref = self.db.collection('matchings').document(matching_id)
                matching_data['matching_id'] = matching_id
                doc_ref.set(matching_data)
                return True
        except Exception as e:
            print(f"매칭 저장 오류: {str(e)}")
            return False

    def get_matchings_for_user(self, user_id):
        """사용자의 매칭 요청 조회"""
        try:
            if self.test_mode:
                return [m for m in self.test_data['matchings'] 
                       if m['sender_id'] == user_id or m['receiver_id'] == user_id]
            else:
                matchings = []
                # 보낸 매칭 요청
                sent = self.db.collection('matchings').where('sender_id', '==', user_id).stream()
                # 받은 매칭 요청
                received = self.db.collection('matchings').where('receiver_id', '==', user_id).stream()
                
                for doc in list(sent) + list(received):
                    matching_data = doc.to_dict()
                    matching_data['id'] = doc.id
                    matchings.append(matching_data)
                return matchings
        except Exception as e:
            print(f"매칭 조회 오류: {str(e)}")
            return []

    def update_matching(self, matching_data):
        """매칭 상태 업데이트"""
        try:
            if self.test_mode:
                for match in self.test_data['matchings']:
                    if match['matching_id'] == matching_data['matching_id']:
                        match.update(matching_data)
                        self.save_test_data()  # 파일에 저장
                        return True
                return False
            else:
                # Firestore 업데이트
                doc_ref = self.db.collection('matchings').document(matching_data['matching_id'])
                doc_ref.update(matching_data)
                return True
        except Exception as e:
            print(f"매칭 업데이트 오류: {str(e)}")
            return False
    
    def get_profile(self, user_id):
        """사용자 프로필 조회"""
        try:
            if self.test_mode:
                for student in self.test_data['students']:
                    if student.get('user_id') == user_id:
                        return student
                return None
            
            doc = self.db.collection(COLLECTION_NAME).document(user_id).get()
            if doc.exists:
                profile_data = doc.to_dict()
                profile_data['user_id'] = doc.id  # user_id 추가
                return profile_data
            return None
        except Exception as e:
            print(f"프로필 조회 중 오류 발생: {str(e)}")
            raise
    
    def update_profile(self, user_id, profile_data):
        """프로필 정보 업데이트"""
        try:
            if self.test_mode:
                for student in self.test_data['students']:
                    if student['id'] == user_id:
                        student.update(profile_data)
                        return True
                return False
            
            profile_data['updated_at'] = firestore.SERVER_TIMESTAMP
            self.db.collection(COLLECTION_NAME).document(user_id).update(profile_data)
            return True
        except Exception as e:
            print(f"프로필 업데이트 중 오류 발생: {str(e)}")
            raise
    
    def delete_profile(self, user_id):
        """프로필 삭제"""
        try:
            if self.test_mode:
                self.test_data['students'] = [s for s in self.test_data['students'] if s['id'] != user_id]
                return True
            
            self.db.collection(COLLECTION_NAME).document(user_id).delete()
            return True
        except Exception as e:
            print(f"프로필 삭제 중 오류 발생: {str(e)}")
            raise
    
    def get_all_profiles(self):
        """모든 프로필 조회"""
        try:
            if self.test_mode:
                return self.test_data['students']
            
            docs = self.db.collection(COLLECTION_NAME).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"프로필 목록 조회 중 오류 발생: {str(e)}")
            raise
            
    def create_matching(self, from_id, to_id):
        """매칭 요청 생성"""
        try:
            # 이미 존재하는 매칭 확인
            existing_matching = self.get_existing_matching(from_id, to_id)
            if existing_matching:
                return existing_matching

            if self.test_mode:
                matching = {
                    'id': str(uuid.uuid4()),
                    'from_id': from_id,
                    'to_id': to_id,
                    'status': 'pending',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                self.test_data['matchings'].append(matching)
                return matching
            
            matching_id = str(uuid.uuid4())
            matching_data = {
                'from_id': from_id,
                'to_id': to_id,
                'status': 'pending',
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            self.db.collection('matchings').document(matching_id).set(matching_data)
            return matching_data
        except Exception as e:
            print(f"매칭 생성 중 오류 발생: {str(e)}")
            raise
            
    def get_matchings(self, user_id):
        """사용자의 매칭 요청 목록 조회"""
        try:
            if self.test_mode:
                return [m for m in self.test_data['matchings'] 
                       if m['to_id'] == user_id or m['from_id'] == user_id]
            
            # 받은 매칭 요청과 보낸 매칭 요청 모두 조회
            received = self.db.collection('matchings').where('to_id', '==', user_id).stream()
            sent = self.db.collection('matchings').where('from_id', '==', user_id).stream()
            
            return [doc.to_dict() for doc in list(received) + list(sent)]
        except Exception as e:
            print(f"매칭 목록 조회 중 오류 발생: {str(e)}")
            raise

    def get_existing_matching(self, from_id, to_id):
        """기존 매칭 요청 확인"""
        try:
            if self.test_mode:
                for matching in self.test_data['matchings']:
                    if (matching['from_id'] == from_id and matching['to_id'] == to_id) or \
                       (matching['from_id'] == to_id and matching['to_id'] == from_id):
                        return matching
                return None
            
            # 양방향 매칭 확인
            matching1 = self.db.collection('matchings').where('from_id', '==', from_id).where('to_id', '==', to_id).limit(1).stream()
            matching2 = self.db.collection('matchings').where('from_id', '==', to_id).where('to_id', '==', from_id).limit(1).stream()
            
            matching1_list = list(matching1)
            matching2_list = list(matching2)
            
            if matching1_list:
                return matching1_list[0].to_dict()
            if matching2_list:
                return matching2_list[0].to_dict()
            return None
        except Exception as e:
            print(f"기존 매칭 확인 중 오류 발생: {str(e)}")
            raise

    def update_matching_status(self, from_id, to_id, status):
        """매칭 상태 업데이트"""
        try:
            if not status in ['pending', 'accepted', 'rejected']:
                raise ValueError("Invalid matching status")

            matching = self.get_existing_matching(from_id, to_id)
            if not matching:
                raise ValueError("Matching not found")

            if self.test_mode:
                for m in self.test_data['matchings']:
                    if (m['from_id'] == from_id and m['to_id'] == to_id) or \
                       (m['from_id'] == to_id and m['to_id'] == from_id):
                        m['status'] = status
                        m['updated_at'] = datetime.now()
                        return m
                return None

            # Firestore에서 매칭 문서 찾기
            matching_query = self.db.collection('matchings').where('from_id', '==', from_id).where('to_id', '==', to_id)
            docs = list(matching_query.stream())
            
            if not docs:
                matching_query = self.db.collection('matchings').where('from_id', '==', to_id).where('to_id', '==', from_id)
                docs = list(matching_query.stream())

            if docs:
                doc_ref = docs[0].reference
                doc_ref.update({
                    'status': status,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                return doc_ref.get().to_dict()
            return None
        except Exception as e:
            print(f"매칭 상태 업데이트 중 오류 발생: {str(e)}")
            raise

    def check_nickname_exists(self, nickname):
        """별명 중복 체크"""
        try:
            if self.test_mode:
                return any(student.get('nickname') == nickname for student in self.test_data['students'])
            else:
                # Firestore에서 별명으로 검색
                docs = self.db.collection('students').where('nickname', '==', nickname).limit(1).stream()
                return len(list(docs)) > 0
        except Exception as e:
            print(f"별명 중복 체크 중 오류 발생: {str(e)}")
            return False

    def get_matching_attempts(self, user_id, date):
        """특정 날짜의 매칭 시도 횟수 조회"""
        try:
            if self.test_mode:
                return 0
                
            doc = self.db.collection('matching_attempts').document(f"{user_id}_{date}").get()
            if doc.exists:
                return doc.to_dict().get('attempts', 0)
            return 0
        except Exception as e:
            print(f"매칭 시도 횟수 조회 중 오류: {str(e)}")
            return 0
            
    def increment_matching_attempts(self, user_id, date):
        """매칭 시도 횟수 증가"""
        try:
            if self.test_mode:
                return True
                
            doc_ref = self.db.collection('matching_attempts').document(f"{user_id}_{date}")
            doc = doc_ref.get()
            
            if doc.exists:
                current_attempts = doc.to_dict().get('attempts', 0)
                doc_ref.update({
                    'attempts': current_attempts + 1,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                doc_ref.set({
                    'user_id': user_id,
                    'date': date,
                    'attempts': 1,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return True
        except Exception as e:
            print(f"매칭 시도 횟수 증가 중 오류: {str(e)}")
            return False

    def reset_matching_attempts(self, user_id, date):
        """매칭 시도 횟수 리셋"""
        try:
            if self.test_mode:
                return True
                
            doc_ref = self.db.collection('matching_attempts').document(f"{user_id}_{date}")
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.update({
                    'attempts': 0,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                doc_ref.set({
                    'user_id': user_id,
                    'date': date,
                    'attempts': 0,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return True
        except Exception as e:
            print(f"매칭 시도 횟수 리셋 중 오류 발생: {str(e)}")
            return False

    def get_last_reset_date(self, user_id):
        """마지막 리셋 날짜 조회"""
        try:
            if self.test_mode:
                return None
                
            doc = self.db.collection('matching_attempts').document(f"{user_id}_last_reset").get()
            if doc.exists:
                return doc.to_dict().get('last_reset_date', None)
            return None
        except Exception as e:
            print(f"마지막 리셋 날짜 조회 중 오류 발생: {str(e)}")
            return None
    
    def save_message(self, sender_id, receiver_id, message_text):
        """메시지 저장"""
        try:
            message_data = {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message': message_text,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'read': False
            }
            
            if self.test_mode:
                message_id = str(uuid.uuid4())
                message_data['message_id'] = message_id
                if 'messages' not in self.test_data:
                    self.test_data['messages'] = []
                self.test_data['messages'].append(message_data)
                self.save_test_data()
                return message_id
            else:
                message_id = str(uuid.uuid4())
                message_data['message_id'] = message_id
                doc_ref = self.db.collection('messages').document(message_id)
                doc_ref.set(message_data)
                return message_id
        except Exception as e:
            print(f"메시지 저장 오류: {str(e)}")
            return None
    
    def get_messages(self, user_id, other_user_id):
        """두 사용자 간의 메시지 조회"""
        try:
            if self.test_mode:
                messages = []
                if 'messages' in self.test_data:
                    for msg in self.test_data['messages']:
                        if ((msg['sender_id'] == user_id and msg['receiver_id'] == other_user_id) or
                            (msg['sender_id'] == other_user_id and msg['receiver_id'] == user_id)):
                            messages.append(msg)
                # 시간순 정렬
                messages.sort(key=lambda x: x.get('timestamp', ''))
                return messages
            else:
                messages = []
                # 내가 보낸 메시지
                sent = self.db.collection('messages').where('sender_id', '==', user_id).where('receiver_id', '==', other_user_id).stream()
                # 내가 받은 메시지
                received = self.db.collection('messages').where('sender_id', '==', other_user_id).where('receiver_id', '==', user_id).stream()
                
                for doc in list(sent) + list(received):
                    msg_data = doc.to_dict()
                    msg_data['message_id'] = doc.id
                    messages.append(msg_data)
                
                # 시간순 정렬
                messages.sort(key=lambda x: x.get('timestamp', ''))
                return messages
        except Exception as e:
            print(f"메시지 조회 오류: {str(e)}")
            return []
    
    def get_unread_messages_count(self, user_id):
        """사용자가 받은 읽지 않은 메시지 수 조회"""
        try:
            if self.test_mode:
                if 'messages' not in self.test_data:
                    return 0
                unread_count = 0
                for msg in self.test_data['messages']:
                    if msg.get('receiver_id') == user_id and not msg.get('read', False):
                        unread_count += 1
                return unread_count
            else:
                unread_messages = self.db.collection('messages').where('receiver_id', '==', user_id).where('read', '==', False).stream()
                return len(list(unread_messages))
        except Exception as e:
            print(f"읽지 않은 메시지 수 조회 오류: {str(e)}")
            return 0
    
    def get_unread_messages_by_sender(self, user_id):
        """사용자가 받은 읽지 않은 메시지를 보낸 사람별로 그룹화"""
        try:
            if self.test_mode:
                if 'messages' not in self.test_data:
                    return {}
                unread_by_sender = {}
                for msg in self.test_data['messages']:
                    if msg.get('receiver_id') == user_id and not msg.get('read', False):
                        sender_id = msg.get('sender_id')
                        if sender_id not in unread_by_sender:
                            unread_by_sender[sender_id] = 0
                        unread_by_sender[sender_id] += 1
                return unread_by_sender
            else:
                unread_messages = self.db.collection('messages').where('receiver_id', '==', user_id).where('read', '==', False).stream()
                unread_by_sender = {}
                for doc in unread_messages:
                    msg_data = doc.to_dict()
                    sender_id = msg_data.get('sender_id')
                    if sender_id not in unread_by_sender:
                        unread_by_sender[sender_id] = 0
                    unread_by_sender[sender_id] += 1
                return unread_by_sender
        except Exception as e:
            print(f"읽지 않은 메시지 그룹화 오류: {str(e)}")
            return {}
    
    def mark_messages_as_read(self, user_id, other_user_id):
        """특정 사용자로부터 받은 메시지를 읽음으로 표시"""
        try:
            if self.test_mode:
                if 'messages' not in self.test_data:
                    return True
                for msg in self.test_data['messages']:
                    if msg.get('receiver_id') == user_id and msg.get('sender_id') == other_user_id:
                        msg['read'] = True
                self.save_test_data()
                return True
            else:
                unread_messages = self.db.collection('messages').where('receiver_id', '==', user_id).where('sender_id', '==', other_user_id).where('read', '==', False).stream()
                for doc in unread_messages:
                    doc.reference.update({'read': True})
                return True
        except Exception as e:
            print(f"메시지 읽음 표시 오류: {str(e)}")
            return False 