import streamlit as st
import streamlit.components.v1 as components
import random
import time

# 페이지 기본 설정
st.set_page_config(page_title="공룡 시대 생존기", page_icon="🦖", layout="centered")

# --- CSS 스타일링 (화면 연출용) ---
st.markdown("""
    <style>
    .story-box {
        background-color: #1e1e1e;
        color: #00ff66;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 18px;
        border: 2px solid #00ff66;
        margin-bottom: 20px;
    }
    .egg-crack {
        text-align: center;
        font-size: 80px;
        animation: shake 0.5s infinite;
    }
    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        40% { transform: translate(1px, -1px) rotate(-1deg); }
        60% { transform: translate(-3px, 1px) rotate(0deg); }
        80% { transform: translate(1px, 1px) rotate(1deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .flash-screen {
        background-color: white;
        height: 100vh;
    }
    </style>
""", unsafe_allow_html=True)

# --- 데이터 정의 ---
ERA_DATA = {
    "트라이아스기": {
        "desc": "초대륙 판게아의 건조하고 뜨거운 땅. 공룡들이 막 등장하기 시작한 시대입니다.",
        "dinos": [
            {"name": "에오랍토르", "color": "#00ff88", "hp": 80, "desc": "크기는 작지만 날렵한 잡식 공룡"},
            {"name": "코엘로피시스", "color": "#ffaa00", "hp": 70, "desc": "날카로운 이빨을 가진 빠른 육식 공룡"}
        ],
        "events": [
            "가뭄이 시작되었습니다. 물을 찾아 이동합니다.",
            "작은 소형 파충류 무리를 발견하여 배를 채웠습니다.",
            "갑작스러운 모래폭풍이 몰아칩니다!"
        ]
    },
    "쥐라기": {
        "desc": "울창한 침엽수림과 거대한 거대 용각류가 지배하는 온난한 시대입니다.",
        "dinos": [
            {"name": "알로사우루스", "color": "#ff3333", "hp": 120, "desc": "쥐라기 최고의 맹렬한 포식자"},
            {"name": "스테고사우루스", "color": "#3388ff", "hp": 150, "desc": "등의 골판과 꼬리 가시를 가진 초식 공룡"}
        ],
        "events": [
            "거대한 브라키오사우루스 무리가 지나가며 열매를 떨어뜨렸습니다.",
            "숲 속에서 다른 육식 공룡과 영역 다툼이 벌어졌습니다.",
            "신선한 침엽수 잎과 물웅덩이를 찾았습니다."
        ]
    },
    "백악기": {
        "desc": "공룡의 황금기. 최강의 공룡들이 다양하게 진화한 시대입니다.",
        "dinos": [
            {"name": "티라노사우루스", "color": "#cc0000", "hp": 150, "desc": "압도적인 턱 힘을 가진 백악기의 제왕"},
            {"name": "트리케라톱스", "color": "#885522", "hp": 180, "desc": "세 개의 뿔과 단단한 프릴을 가진 초식 공룡"}
        ],
        "events": [
            "화산 재가 내리기 시작합니다. 안전한 곳으로 이동해야 합니다.",
            "사냥에 성공하여 든든하게 배를 채웠습니다.",
            "새로운 종류의 속씨식물 열매를 발견했습니다."
        ]
    }
}

# --- 세션 상태 초기화 ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'STORY_INTRO'  # STORY_INTRO -> ERA_SELECT -> FLASH -> EGG -> DINO_3D -> PLAYING
if 'intro_step' not in st.session_state:
    st.session_state.intro_step = 0
if 'selected_era' not in st.session_state:
    st.session_state.selected_era = None
if 'player_dino' not in st.session_state:
    st.session_state.player_dino = None
if 'crack_count' not in st.session_state:
    st.session_state.crack_count = 0
if 'hp' not in st.session_state:
    st.session_state.hp = 100
if 'day' not in st.session_state:
    st.session_state.day = 1
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- 3D 공룡 렌더링 함수 (Three.js) ---
def render_3d_dino(dino_name, dino_color):
    html_code = f"""
    <div id="dino-3d-container" style="width: 100%; height: 350px; background-color: #111; border-radius: 10px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('dino-3d-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // 조명
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        // 공룡 그룹 (3D 입체 도형으로 조립)
        const dinoGroup = new THREE.Group();
        const material = new THREE.MeshStandardMaterial({{ color: '{dino_color}', roughness: 0.4 }});

        // 몸통
        const bodyGeo = new THREE.BoxGeometry(1.5, 1.2, 2);
        const body = new THREE.Mesh(bodyGeo, material);
        dinoGroup.add(body);

        // 머리
        const headGeo = new THREE.BoxGeometry(1, 0.9, 1.3);
        const head = new THREE.Mesh(headGeo, material);
        head.position.set(0, 0.8, 1.2);
        dinoGroup.add(head);

        // 꼬리
        const tailGeo = new THREE.ConeGeometry(0.5, 2.5, 8);
        const tail = new THREE.Mesh(tailGeo, material);
        tail.rotation.x = -Math.PI / 3;
        tail.position.set(0, -0.2, -1.8);
        dinoGroup.add(tail);

        // 다리
        const legGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 8);
        const leg1 = new THREE.Mesh(legGeo, material);
        leg1.position.set(-0.6, -1, 0);
        const leg2 = new THREE.Mesh(legGeo, material);
        leg2.position.set(0.6, -1, 0);
        dinoGroup.add(leg1);
        dinoGroup.add(leg2);

        scene.add(dinoGroup);
        camera.position.set(3, 2, 5);
        camera.lookAt(0, 0, 0);

        // 회전 애니메이션
        function animate() {{
            requestAnimationFrame(animate);
            dinoGroup.rotation.y += 0.02;
            renderer.render(scene, camera);
        }}
        animate();
    </script>
    """
    components.html(html_code, height=370)

# ==========================================
# 게임 진행 스테이지별 제어
# ==========================================

# 1. 스토리 오프닝 (가정집 -> UFO 납치)
if st.session_state.stage == 'STORY_INTRO':
    st.title("🏠 일상적인 어느 날...")
    
    story_scripts = [
        "평범한 주말 오후, 당신은 집 안 거실에 서 있습니다.",
        "문득 달콤한 아이스크림이 먹고 싶어져 밖으로 나갑니다. 🍦",
        "아이스크림 가게로 향하던 중, 갑자기 하늘이 요란하게 반짝입니다!",
        "하늘을 올려다보니 초록색 외계인이 타고 있는 UFO가 나타났습니다! 🛸👽",
        "우웅---! 강한 빛과 함께 당신은 UFO 안으로 빨려 들어갑니다!!"
    ]
    
    current_text = story_scripts[st.session_state.intro_step]
    st.markdown(f'<div class="story-box">💬 {current_text}</div>', unsafe_allow_html=True)
    
    if st.session_state.intro_step < len(story_scripts) - 1:
        if st.button("다음 ▶"):
            st.session_state.intro_step += 1
            st.rerun()
    else:
        if st.button("정신 차리기 🌀"):
            st.session_state.stage = 'ERA_SELECT'
            st.rerun()

# 2. 시대 선택
elif st.session_state.stage == 'ERA_SELECT':
    st.title("🌀 시간의 틈새")
    st.subheader("정신을 차려보니 시공간이 일그러져 있습니다. 떨어질 시대를 선택하세요!")
    
    era_choice = st.radio("시대를 선택하세요:", list(ERA_DATA.keys()))
    st.info(ERA_DATA[era_choice]["desc"])
    
    if st.button("이 시대로 뛰어들기 🚀"):
        st.session_state.selected_era = era_choice
        st.session_state.player_dino = random.choice(ERA_DATA[era_choice]["dinos"])
        st.session_state.hp = st.session_state.player_dino["hp"]
        st.session_state.stage = 'FLASH'
        st.rerun()

# 3. 번쩍이는 효과 연출
elif st.session_state.stage == 'FLASH':
    flash_holder = st.empty()
    flash_holder.markdown("<h1 style='text-align: center; font-size: 100px;'>⚡⚡⚡</h1>", unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.stage = 'EGG'
    st.rerun()

# 4. 검은 화면 & 알 부화 연출
elif st.session_state.stage == 'EGG':
    st.title("⬛ 어둠 속에서...")
    st.caption("눈을 떠보니 좁고 컴컴한 공간입니다.")
    
    egg_states = ["🥚", "🥚 (금 가기 시작)", "🥚💥 (금이 쩍쩍 갈라집니다!)", "🐣 부화 성공!"]
    
    st.markdown(f'<div class="egg-crack">{egg_states[st.session_state.crack_count]}</div>', unsafe_allow_html=True)
    
    if st.session_state.crack_count < 3:
        if st.button("알 껍질 밀어내기! 🔨"):
            st.session_state.crack_count += 1
            st.rerun()
    else:
        if st.button("밖으로 나가기 ✨"):
            st.session_state.stage = 'DINO_3D'
            st.rerun()

# 5. 3D 공룡 확인 & 'ㄱㄱ' 버튼
elif st.session_state.stage == 'DINO_3D':
    dino = st.session_state.player_dino
    st.title(f"🦖 당신은 **{dino['name']}**(으)로 태어났습니다!")
    st.write(dino['desc'])
    
    # 3D 입체 모델 출력
    render_3d_dino(dino['name'], dino['color'])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ㄱㄱ", use_container_width=True):
            st.session_state.stage = 'PLAYING'
            st.session_state.logs.append(f"[{st.session_state.selected_era}] 시대에 {dino['name']}(으)로 생존을 시작합니다!")
            st.rerun()

# 6. 메인 1인칭 생존 게임
elif st.session_state.stage == 'PLAYING':
    dino = st.session_state.player_dino
    era = st.session_state.selected_era
    
    st.sidebar.header("📊 현재 상태")
    st.sidebar.write(f"**공룡:** {dino['name']}")
    st.sidebar.write(f"**시대:** {era}")
    st.sidebar.write(f"**생존일:** {st.session_state.day}일 차")
    st.sidebar.progress(max(0, st.session_state.hp) / dino['hp'], text=f"체력: {st.session_state.hp}/{dino['hp']}")
    
    st.title(f"👁️ 1인칭 생존 - {st.session_state.day}일 차")
    st.caption(f"당신({dino['name']})의 눈으로 본 {era}의 세계입니다.")
    
    col1, col2, col3 = st.columns(3)
    action = None
    with col1:
        if st.button("🔍 주변 탐색"): action = "explore"
    with col2:
        if st.button("🍖 먹이 구하기"): action = "eat"
    with col3:
        if st.button("💤 휴식 취하기"): action = "rest"
        
    if action:
        st.session_state.day += 1
        if action == "explore":
            evt = random.choice(ERA_DATA[era]["events"])
            st.session_state.hp -= 15
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] {evt}")
        elif action == "eat":
            st.session_state.hp = min(dino['hp'], st.session_state.hp + 20)
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] 먹이를 먹어 체력을 회복했습니다.")
        elif action == "rest":
            st.session_state.hp = min(dino['hp'], st.session_state.hp + 15)
            st.session_state.logs.append(f"[{st.session_state.day-1}일차] 휴식을 취했습니다.")
            
        if st.session_state.hp <= 0:
            st.error("☠️ 체력이 다하여 생존에 실패했습니다...")
            if st.button("처음부터 다시하기"):
                st.session_state.clear()
                st.rerun()
        else:
            st.rerun()
            
    st.write("---")
    st.subheader("📜 생존 기록")
    for log in reversed(st.session_state.logs):
        st.write(log)
