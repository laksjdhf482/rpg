import streamlit as st
from pathlib import Path
from PIL import Image, ImageOps
import base64
import time

# 클릭 좌표를 받기 위한 Streamlit 컴포넌트
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(
    page_title="거지 탈출 RPG",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 파일
# ============================================================

BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"
CHARACTER_PATH = ASSET_DIR / "character.png"
COIN_SOUND_PATH = ASSET_DIR / "coin.wav"

STAGE_BACKGROUNDS = [
    ASSET_DIR / "stage1.jpg",
    ASSET_DIR / "stage2.jpg",
    ASSET_DIR / "stage3.jpg",
    ASSET_DIR / "stage4.jpg",
    ASSET_DIR / "stage5.jpg",
]

STAGES = [
    ("시골 탈출", "시골", 1_000_000, "🌾"),
    ("길거리 탈출", "길거리 인도", 5_000_000, "🚶"),
    ("서울역 탈출", "서울역", 50_000_000, "🚉"),
    ("반지하 탈출", "반지하", 250_000_000, "🏠"),
    ("1층집 탈출", "지방 도시의 아파트", 1_250_000_000, "🏢"),
]

SHOP_ITEMS = [
    ("돈 증가", "클릭당 수입 +1,000원", "money"),
    ("클릭 더블", "한 번 터치하면 2번 클릭한 것으로 적용", "double"),
]

# ============================================================
# 상태
# ============================================================

def init_game():
    defaults = {
        "money": 0,
        "stage": 0,
        "click_power": 1_000,
        "double_click": False,
        "shop_level": [0, 0],
        "shop_open": False,
        "notice": "",
        "popup": None,
        "sound": False,
        "clear": False,
        "last_click_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def reset_game():
    st.session_state.money = 0
    st.session_state.stage = 0
    st.session_state.click_power = 1_000
    st.session_state.double_click = False
    st.session_state.shop_level = [0, 0]
    st.session_state.shop_open = False
    st.session_state.notice = ""
    st.session_state.popup = None
    st.session_state.sound = False
    st.session_state.clear = False
    st.session_state.last_click_key = None


init_game()

# ============================================================
# 계산
# ============================================================

def money_text(value):
    return f"{value:,}원"


def upgrade_cost(level):
    return int(1000 * (1.5 ** level))


def click_income():
    return st.session_state.click_power * (2 if st.session_state.double_click else 1)


def handle_click(x, y):
    income = click_income()
    st.session_state.money += income

    # 터치한 위치를 기준으로 +금액 애니메이션 위치 저장
    st.session_state.popup = {
        "text": f"+{money_text(income)}",
        "x": float(x),
        "y": float(y),
        "time": time.time(),
    }
    st.session_state.sound = True
    st.session_state.notice = ""

    goal = STAGES[st.session_state.stage][2]
    if st.session_state.money >= goal:
        if st.session_state.stage < len(STAGES) - 1:
            st.session_state.stage += 1
            st.session_state.notice = (
                f"STAGE CLEAR! → {STAGES[st.session_state.stage][0]}"
            )
        else:
            st.session_state.clear = True
            st.session_state.notice = "최종 탈출 성공!"


def buy_upgrade(index):
    level = st.session_state.shop_level[index]
    cost = upgrade_cost(level)

    if st.session_state.money < cost:
        st.session_state.notice = "돈이 부족합니다"
        return

    if index == 1 and st.session_state.double_click:
        st.session_state.notice = "이미 구매했습니다"
        return

    st.session_state.money -= cost
    st.session_state.shop_level[index] += 1

    if index == 0:
        st.session_state.click_power += 1_000
        st.session_state.notice = "돈 증가 업그레이드 완료!"
    else:
        st.session_state.double_click = True
        st.session_state.notice = "클릭 더블 업그레이드 완료!"

# ============================================================
# 이미지 합성
# 배경 + 캐릭터를 하나의 게임 화면으로 만들어 터치 좌표를 정확히 받음
# ============================================================

def make_game_image(stage_index):
    bg = Image.open(STAGE_BACKGROUNDS[stage_index]).convert("RGB")
    bg = ImageOps.fit(bg, (960, 540), method=Image.Resampling.LANCZOS)

    character = Image.open(CHARACTER_PATH).convert("RGBA")

    # 캐릭터를 화면 중앙에 서 있도록 배치
    target_h = 465
    ratio = target_h / character.height
    target_w = int(character.width * ratio)
    character = character.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 바닥에서 약간 띄워 중앙에 서게 배치
    x = (bg.width - character.width) // 2
    y = bg.height - character.height - 4

    bg_rgba = bg.convert("RGBA")
    bg_rgba.alpha_composite(character, (x, y))
    return bg_rgba.convert("RGB")

# ============================================================
# 모바일 CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(#f5e7c8, #e5cfa3);
    min-height: 100vh;
}

.block-container {
    max-width: 680px !important;
    padding: 7px 9px 12px !important;
}

.game-title {
    text-align: center;
    font-size: clamp(26px, 7vw, 38px);
    line-height: 1;
    font-weight: 900;
    color: #3b3025;
    margin: 0 0 3px;
}

.location-card, .money-card {
    background: #fff9e9;
    border: 3px solid #44372b;
    border-radius: 14px;
    box-shadow: 3px 3px 0 #44372b;
    text-align: center;
}

.location-card {
    padding: 5px 8px;
    margin-bottom: 7px;
}

.location-name {
    font-size: clamp(17px, 5vw, 24px);
    font-weight: 900;
}

.location-desc {
    font-size: 10px;
    color: #756451;
}

.money-card {
    padding: 5px;
    margin-bottom: 5px;
}

.money-label {
    font-size: 9px;
    color: #776752;
}

.money-value {
    font-size: clamp(25px, 7.5vw, 40px);
    line-height: 1;
    font-weight: 900;
}

.stProgress {
    margin: 0 !important;
}

.game-image {
    border: 3px solid #44372b;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 4px 4px 0 #44372b;
    margin: 5px 0;
}

.touch-help {
    text-align: center;
    font-size: 9px;
    color: #665541;
    margin: 2px 0;
}

.notice {
    text-align: center;
    height: 20px;
    font-size: 12px;
    font-weight: 900;
    color: #a55708;
}

.clear-box {
    background: #fff2a8;
    border: 3px solid #44372b;
    border-radius: 14px;
    padding: 10px;
    text-align: center;
    font-size: 19px;
    font-weight: 900;
    margin: 5px 0;
}

.shop-title {
    text-align: center;
    font-size: 20px;
    font-weight: 900;
}

.shop-card {
    background: #fff9e9;
    border: 2px solid #554536;
    border-radius: 10px;
    padding: 7px;
    margin: 5px 0;
}

.shop-name {
    font-size: 15px;
    font-weight: 900;
}

.shop-desc {
    font-size: 10px;
    color: #756451;
}

div.stButton > button {
    border: 2px solid #44372b;
    border-radius: 10px;
    font-family: 'Jua', sans-serif;
    font-weight: 900;
    min-height: 35px;
    padding: 3px 5px;
}

/* 상점 버튼을 오른쪽 아래에 고정 */
.shop-floating {
    position: fixed;
    right: 10px;
    bottom: 10px;
    z-index: 9999;
}

.shop-floating div.stButton > button {
    width: 64px !important;
    height: 64px !important;
    min-height: 64px !important;
    border-radius: 50% !important;
    background: #f7c65d !important;
    box-shadow: 3px 3px 0 #44372b;
    font-size: 13px;
}

@media (max-width: 420px) {
    .block-container {
        padding: 5px 7px 9px !important;
    }
    .location-card {
        padding: 4px 6px;
    }
    .shop-floating {
        right: 7px;
        bottom: 7px;
    }
    .shop-floating div.stButton > button {
        width: 57px !important;
        height: 57px !important;
        min-height: 57px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 화면 상단
# ============================================================

stage_name, place, goal, emoji = STAGES[st.session_state.stage]

st.markdown('<div class="game-title">거지 탈출 RPG</div>', unsafe_allow_html=True)

st.markdown(
    f"""
<div class="location-card">
    <div class="location-name">{emoji} STAGE {st.session_state.stage + 1} · {stage_name}</div>
    <div class="location-desc">{place} · 목표 {money_text(goal)}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="money-card">
    <div class="money-label">현재 보유 금액</div>
    <div class="money-value">{money_text(st.session_state.money)}</div>
</div>
""",
    unsafe_allow_html=True,
)

progress = min(st.session_state.money / goal, 1.0)
st.progress(progress)

# ============================================================
# 캐릭터 + 배경이 합성된 실제 터치 영역
# ============================================================

game_image = make_game_image(st.session_state.stage)

st.markdown('<div class="game-image">', unsafe_allow_html=True)
coords = streamlit_image_coordinates(
    game_image,
    key=f"game_scene_{st.session_state.stage}",
    width=960,
)
st.markdown('</div>', unsafe_allow_html=True)

# 새 터치가 발생했을 때만 처리
if coords:
    x = coords.get("x")
    y = coords.get("y")
    click_key = f"{st.session_state.stage}:{x}:{y}"

    if click_key != st.session_state.last_click_key:
        st.session_state.last_click_key = click_key
        handle_click(x, y)
        st.rerun()

st.markdown(
    '<div class="touch-help">화면 아무 곳이나 터치하면 돈을 벌 수 있습니다</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 터치 위치에 +금액 애니메이션
# ============================================================

if st.session_state.popup:
    p = st.session_state.popup
    # 컴포넌트 기준 좌표를 퍼센트로 변환
    left = max(4, min(88, (p["x"] / 960) * 100))
    top = max(5, min(88, (p["y"] / 540) * 100))

    st.markdown(
        f"""
<style>
.touch-popup {{
    position: fixed;
    left: {left}%;
    top: {top + 5}%;
    transform: translate(-50%, -50%);
    z-index: 10000;
    pointer-events: none;
    font-size: clamp(18px, 5vw, 30px);
    font-weight: 900;
    color: #ffe27a;
    text-shadow: 2px 2px 0 #5a3811, -1px -1px 0 #5a3811;
    animation: moneyFloat .9s ease-out forwards;
}}
@keyframes moneyFloat {{
    0% {{ opacity: 1; transform: translate(-50%, -20%) scale(1); }}
    100% {{ opacity: 0; transform: translate(-50%, -100%) scale(1.12); }}
}}
</style>
<div class="touch-popup">{p['text']}</div>
""",
        unsafe_allow_html=True,
    )

    # 팝업이 계속 남지 않게 다음 실행에서 제거
    if time.time() - p["time"] > 0.9:
        st.session_state.popup = None

# ============================================================
# 효과음
# ============================================================

if st.session_state.sound:
    # 클릭 후 발생한 rerun에서 자동 재생
    audio_b64 = base64.b64encode(COIN_SOUND_PATH.read_bytes()).decode()
    st.markdown(
        f"""
<audio id="coinSound" autoplay playsinline>
    <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
</audio>
<script>
const audio = document.getElementById('coinSound');
if (audio) {{
    audio.volume = 0.55;
    audio.play().catch(() => {{}});
}}
</script>
""",
        unsafe_allow_html=True,
    )
    st.session_state.sound = False

# ============================================================
# 안내 / 클리어
# ============================================================

if st.session_state.notice:
    st.markdown(
        f'<div class="notice">{st.session_state.notice}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="notice"></div>', unsafe_allow_html=True)

if st.session_state.clear:
    st.markdown(
        '<div class="clear-box">최종 탈출 성공!<br>12억 5천만 원 달성</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 상점 버튼
# ============================================================

st.markdown('<div class="shop-floating">', unsafe_allow_html=True)
if st.button("상점", key="shop_button"):
    st.session_state.shop_open = not st.session_state.shop_open
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.shop_open:
    st.markdown('<div class="shop-title">상점</div>', unsafe_allow_html=True)

    for i, (name, desc, item_type) in enumerate(SHOP_ITEMS):
        level = st.session_state.shop_level[i]
        cost = upgrade_cost(level)

        if item_type == "double" and st.session_state.double_click:
            button_text = "구매 완료"
            disabled = True
        else:
            button_text = f"업그레이드 · {money_text(cost)}"
            disabled = False

        st.markdown(
            f"""
<div class="shop-card">
    <div class="shop-name">{name} · Lv.{level}</div>
    <div class="shop-desc">{desc}</div>
    <div class="shop-desc">다음 비용: <b>{money_text(cost)}</b></div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(
            button_text,
            key=f"upgrade_{i}",
            use_container_width=True,
            disabled=disabled,
        ):
            buy_upgrade(i)
            st.rerun()

# 초기화
if st.button("게임 초기화", use_container_width=True):
    reset_game()
    st.rerun()
