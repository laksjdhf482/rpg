# 거지 탈출 RPG

Streamlit 기반 클릭형 RPG 게임입니다

## GitHub 구조

```text
main.py
requirements.txt
assets/
 ├─ character.png
 ├─ stage1.jpg
 ├─ stage2.jpg
 ├─ stage3.jpg
 ├─ stage4.jpg
 ├─ stage5.jpg
 └─ coin.wav
```

## 실행

```bash
pip install -r requirements.txt
streamlit run main.py
```

## 포함 기능

- 모바일 화면 최적화
- 5개 스테이지 배경 자동 변경
- 동일한 캐릭터를 모든 스테이지에서 사용
- 스테이지별 배경에 맞춰 캐릭터 위치 자동 변경
- 클릭당 1,000원
- +금액 페이드아웃 표시
- 클릭 효과음
- 오른쪽 하단 상점 버튼
- 상점 2종
  - 돈 증가
  - 클릭 더블
- 업그레이드 비용 1,000원 시작, 이후 50% 증가
- 12억 5천만 원 최종 탈출
