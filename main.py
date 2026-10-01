import streamlit as st
import streamlit.components.v1 as components
import random
import time
import base64

# 1. 페이지 및 전체 화면 CSS 설정
st.set_page_config(page_title="공룡 시대 생존기", page_icon="🦖", layout="wide")

# 로컬 이미지(background.png)를 Base64로 변환하여 CSS 배경으로 적용하는 함수
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

bg_base64 = get_base64_of_bin_file('background.png')

if bg_base64:
    bg_style = f"""
        background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.5)), url("data:image/png;base64,{bg_base64}");
    """
else:
    # background.png 파일이 없을 경우 기본 온라인 예시 배경
    bg_style = """
        background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1920');
    """

st.markdown(f"""
    <style>
    /* Streamlit 기본 여백 완전 제거 및 꽉 찬 화면 */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* 시작 화면 이미지 전면 배경 스타일 */
    .title-screen {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        {bg_style}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999;
    }}

    .title-box {{
        background: rgba(0, 0, 0, 0.7);
        padding: 50px 80px;
        border-radius: 20px;
        border: 2px solid #00ff66;
        box-shadow: 0 0 35px rgba(0, 255, 102, 0.5);
        text-align: center;
        color: white;
    }}

    .egg-crack {{
        text-align: center;
        font-size: 80px;
        user-select: none;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 데이터 정의 ---
ERA_DATA = {
    "트라이아스기": {
        "desc": "초대륙 판게아의 건조하고 뜨거운 땅. 초기 공룡들이 막 등장하기 시작한 시대입니다.",
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
        "desc": "울창한 침엽수림과 거대한 용각류가 지배하는 온난한 시대입니다.",
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
    st.session_state.stage = 'TITLE'  # TITLE -> STORY_3D -> ERA_SELECT -> FLASH -> EGG -> DINO_3D -> PLAYING
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

# --- 3D 인터랙티브 월드 (Three.js 기반) ---
def render_interactive_3d_world():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; font-family: sans-serif; background: #000; }
            #canvas-container { width: 100vw; height: 80vh; position: relative; user-select: none; }
            #ui-box {
                position: absolute; bottom: 20px; left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.85); color: #00ff66;
                padding: 12px 28px; border-radius: 8px;
                border: 2px solid #00ff66; font-size: 16px; text-align: center;
                z-index: 5; pointer-events: none;
            }
            #door-handle-btn {
                position: absolute; top: 20px; left: 50%;
                transform: translateX(-50%);
                background: #ffcc00; color: #000; font-weight: bold;
                padding: 12px 24px; border-radius: 8px; font-size: 18px;
                border: 2px solid #fff; cursor: pointer; display: none; z-index: 20;
                box-shadow: 0 0 15px #ffcc00;
            }
            #guide-overlay {
                position: absolute; top: 10px; left: 10px;
                background: rgba(0,0,0,0.75); color: #fff;
                padding: 10px 14px; border-radius: 6px; font-size: 13px;
                z-index: 10; pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="guide-overlay">
                🖱️ <b>화면 클릭 후 드래그:</b> 360도 & 위아래 시점 자유 회전<br>
                ⌨️ <b>W, A, S, D:</b> 이동 (이동 시 1인칭 시점으로 즉시 전환)
            </div>
            <button id="door-handle-btn" onclick="openDoorAndExit()">✊ 문손잡이 잡고 문 열기</button>
            <div id="ui-box">💬 가정집 거실에 서 있습니다. 마우스와 키보드로 이동해 보세요.</div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

        <script>
            let container = document.getElementById('canvas-container');
            let scene = new THREE.Scene();
            let camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            let renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            let uiBox = document.getElementById('ui-box');
            let doorBtn = document.getElementById('door-handle-btn');

            let currentZone = 0; // 0: 집 안, 1: 도시
            let isFirstPerson = false; // 시작은 위에서 내려다보는 탑뷰

            // 조작 변수
            let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
            let isMouseDown = false;
            let mouseX = 0, mouseY = 0;
            let lon = -90, lat = -20;
            let phi = 0, theta = 0;
            
            // 로블록스 형태 캐릭터
            let playerGroup = new THREE.Group();
            let charBody, charHead;

            function createRobloxCharacter() {
                let bodyGeo = new THREE.BoxGeometry(0.8, 1.0, 0.4);
                let bodyMat = new THREE.MeshStandardMaterial({ color: 0x0088ff });
                charBody = new THREE.Mesh(bodyGeo, bodyMat);
                charBody.position.y = 0.5;

                let headGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
                let headMat = new THREE.MeshStandardMaterial({ color: 0xffcc99 });
                charHead = new THREE.Mesh(headGeo, headMat);
                charHead.position.y = 1.25;

                playerGroup.add(charBody, charHead);
                playerGroup.position.set(0, 0, 0);
            }

            // 키보드 조작
            window.addEventListener('keydown', (e) => {
                switch (e.code) {
                    case 'KeyW': moveForward = true; break;
                    case 'KeyA': moveLeft = true; break;
                    case 'KeyS': moveBackward = true; break;
                    case 'KeyD': moveRight = true; break;
                }
                if (moveForward || moveBackward || moveLeft || moveRight) {
                    if (!isFirstPerson && currentZone === 0) {
                        isFirstPerson = true; // 이동 시작 시 1인칭 전환
                    }
                }
            });

            window.addEventListener('keyup', (e) => {
                switch (e.code) {
                    case 'KeyW': moveForward = false; break;
                    case 'KeyA': moveLeft = false; break;
                    case 'KeyS': moveBackward = false; break;
                    case 'KeyD': moveRight = false; break;
                }
            });

            // 마우스 드래그 시점 회전 (360도 + 위아래)
            container.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
            });
            window.addEventListener('mouseup', () => { isMouseDown = false; });
            window.addEventListener('mousemove', (e) => {
                if (isMouseDown) {
                    lon += (e.clientX - mouseX) * 0.3;
                    lat -= (e.clientY - mouseY) * 0.3;
                    lat = Math.max(-85, Math.min(85, lat));
                    mouseX = e.clientX;
                    mouseY = e.clientY;
                }
            });

            // --- 환경 구축 ---
            let houseGroup = new THREE.Group();
            let cityGroup = new THREE.Group();
            let doorMesh, handleMesh;

            function buildHouse() {
                scene.background = new THREE.Color(0x1a1a1a);
                createRobloxCharacter();
                houseGroup.add(playerGroup);

                // 바닥 & 벽
                let floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.MeshStandardMaterial({ color: 0x8b5a2b }));
                floor.rotation.x = -Math.PI / 2;
                houseGroup.add(floor);

                let wallMat = new THREE.MeshStandardMaterial({ color: 0xdddddd });
                let wall1 = new THREE.Mesh(new THREE.BoxGeometry(16, 4, 0.2), wallMat); wall1.position.set(0, 2, -8);
                let wall2 = new THREE.Mesh(new THREE.BoxGeometry(16, 4, 0.2), wallMat); wall2.position.set(0, 2, 8);
                let wall3 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 16), wallMat); wall3.position.set(-8, 2, 0);
                houseGroup.add(wall1, wall2, wall3);

                // 현관문 & 문손잡이 (오른쪽 벽)
                doorMesh = new THREE.Mesh(new THREE.BoxGeometry(0.2, 3.5, 2), new THREE.MeshStandardMaterial({ color: 0x553311 }));
                doorMesh.position.set(7.9, 1.75, 0);
                
                handleMesh = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), new THREE.MeshStandardMaterial({ color: 0xffd700 }));
                handleMesh.position.set(7.7, 1.75, 0.6);
                houseGroup.add(doorMesh, handleMesh);

                // 소파
                let sofa = new THREE.Mesh(new THREE.BoxGeometry(3, 1, 1.5), new THREE.MeshStandardMaterial({ color: 0x992222 }));
                sofa.position.set(-4, 0.5, -4);
                houseGroup.add(sofa);

                scene.add(houseGroup);
            }

            let ufoGroup = new THREE.Group();
            let ufoBeam = null;

            function buildCity() {
                scene.remove(houseGroup);
                scene.background = new THREE.Color(0x87ceeb);

                // 도로 (진입 방향 도로)
                let road = new THREE.Mesh(new THREE.PlaneGeometry(16, 80), new THREE.MeshStandardMaterial({ color: 0x333333 }));
                road.rotation.x = -Math.PI / 2;
                cityGroup.add(road);

                // ⭐ 횡단보도 세로(종방향) 배치 (z축 길을 따라 세로 줄무늬 배치)
                for (let i = 2; i >= -12; i -= 2.0) {
                    let stripe = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 1.4), new THREE.MeshStandardMaterial({ color: 0xffffff }));
                    stripe.rotation.x = -Math.PI / 2;
                    stripe.position.set(0, 0.01, i); // 세로 길을 따라 배치
                    cityGroup.add(stripe);
                }

                // 주변 건물들
                for(let i = -30; i <= 30; i += 15) {
                    if (i === -20) continue; // 아이스크림 가게 자리
                    let b1 = new THREE.Mesh(new THREE.BoxGeometry(8, 12 + Math.random()*6, 8), new THREE.MeshStandardMaterial({ color: 0x778899 }));
                    b1.position.set(-12, 6, i);
                    let b2 = new THREE.Mesh(new THREE.BoxGeometry(8, 12 + Math.random()*6, 8), new THREE.MeshStandardMaterial({ color: 0x778899 }));
                    b2.position.set(12, 6, i);
                    cityGroup.add(b1, b2);
                }

                // 아이스크림 가게 (세로 횡단보도 끝 정면)
                let shop = new THREE.Mesh(new THREE.BoxGeometry(10, 5, 8), new THREE.MeshStandardMaterial({ color: 0xff6699 }));
                shop.position.set(0, 2.5, -22);
                cityGroup.add(shop);

                // 아이스크림 간판
                let sign = new THREE.Mesh(new THREE.ConeGeometry(1.2, 2.5, 8), new THREE.MeshStandardMaterial({ color: 0xffcc00 }));
                sign.position.set(0, 6.5, -18);
                cityGroup.add(sign);

                // UFO (처음에는 등장하지 않음)
                let ufoDisc = new THREE.Mesh(new THREE.CylinderGeometry(4, 4, 0.8, 16), new THREE.MeshStandardMaterial({ color: 0x444444 }));
                let ufoDome = new THREE.Mesh(new THREE.SphereGeometry(2, 16, 16), new THREE.MeshStandardMaterial({ color: 0x00ff00, transparent: true, opacity: 0.8 }));
                ufoDome.position.y = 0.4;
                ufoGroup.add(ufoDisc, ufoDome);
                ufoGroup.position.set(0, 18, -5); // 횡단보도 상공
                ufoGroup.visible = false; // 숨김 설정
                cityGroup.add(ufoGroup);

                // 플레이어 초기 위치 (도시 입구)
                playerGroup.position.set(0, 0, 10);
                cityGroup.add(playerGroup);

                scene.add(cityGroup);
                uiBox.innerText = "🍦 밖으로 나왔습니다! 세로 횡단보도를 지나 아이스크림 가게로 걸어가세요.";
            }

            // 조명 설정
            let light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(10, 20, 10);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));

            buildHouse();

            // 현관문 열기 인터랙션
            window.openDoorAndExit = function() {
                doorMesh.rotation.y = -Math.PI / 2;
                handleMesh.position.x = 7.9;
                doorBtn.style.display = 'none';
                uiBox.innerText = "🚪 문이 열렸습니다. 밖으로 나갑니다...";
                
                setTimeout(() => {
                    currentZone = 1;
                    isFirstPerson = true;
                    buildCity();
                }, 800);
            };

            let captured = false;
            let floatSpeed = 0.08;
            let isFloating = false;

            function animate() {
                requestAnimationFrame(animate);

                lat = Math.max(-85, Math.min(85, lat));
                phi = THREE.MathUtils.degToRad(90 - lat);
                theta = THREE.MathUtils.degToRad(lon);

                let dir = new THREE.Vector3();
                dir.x = Math.sin(phi) * Math.cos(theta);
                dir.y = Math.cos(phi);
                dir.z = Math.sin(phi) * Math.sin(theta);
                dir.normalize();

                let moveDir = new THREE.Vector3(dir.x, 0, dir.z).normalize();
                let sideDir = new THREE.Vector3(-moveDir.z, 0, moveDir.x);

                let speed = 0.12;

                // 이동 처리
                if (!isFloating) {
                    if (moveForward) playerGroup.position.addScaledVector(moveDir, speed);
                    if (moveBackward) playerGroup.position.addScaledVector(moveDir, -speed);
                    if (moveLeft) playerGroup.position.addScaledVector(sideDir, -speed);
                    if (moveRight) playerGroup.position.addScaledVector(sideDir, speed);
                }

                // 시점 제어
                if (isFirstPerson) {
                    camera.position.set(playerGroup.position.x, playerGroup.position.y + 1.4, playerGroup.position.z);
                    let target = new THREE.Vector3().addVectors(camera.position, dir);
                    camera.lookAt(target);
                } else {
                    camera.position.set(playerGroup.position.x, playerGroup.position.y + 5, playerGroup.position.z + 4);
                    camera.lookAt(playerGroup.position);
                }

                // 1. 집 안: 문손잡이 위치 접근 감지
                if (currentZone === 0) {
                    if (playerGroup.position.x > 5.5 && Math.abs(playerGroup.position.z) < 2.5) {
                        doorBtn.style.display = 'block';
                        uiBox.innerText = "🚪 문손잡이를 잡았습니다. 버튼을 눌러 문을 여세요!";
                    } else {
                        doorBtn.style.display = 'none';
                        if (isFirstPerson) {
                            uiBox.innerText = "💬 현관문(오른쪽 벽) 문손잡이로 걸어가세요.";
                        }
                    }
                }

                // 2. 도시: 세로 횡단보도 진입 및 약 3발자국 이동 시 UFO 갑툭튀 & 공중 부양
                if (currentZone === 1 && !captured) {
                    // 세로 횡단보도 위치(z = 0 부근)에 도달했을 때
                    if (playerGroup.position.z < 2) {
                        captured = true;
                        isFloating = true;
                        ufoGroup.visible = true; // 외계인 UFO 갑자기 등장

                        // 초록빛 광선 기둥 생성
                        let beamGeo = new THREE.CylinderGeometry(2.5, 4, 20, 16);
                        let beamMat = new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: 0.65 });
                        ufoBeam = new THREE.Mesh(beamGeo, beamMat);
                        ufoBeam.position.set(0, 8, -5);
                        cityGroup.add(ufoBeam);

                        uiBox.innerText = "🛸 갑자기 하늘에서 초록 외계인 UFO가 나타나 캐릭터를 붕 띄워 빨아들입니다!!";
                    }
                }

                // 캐릭터 공중 부양 애니메이션
                if (isFloating) {
                    playerGroup.position.y += floatSpeed; // 붕 떠오름
                    playerGroup.rotation.y += 0.12;       // 공중 회전
                    if (playerGroup.position.y > 15) {
                        isFloating = false;
                        uiBox.innerText = "🌀 UFO 빛 속으로 완전히 빨려 들어갔습니다...";
                    }
                }

                renderer.render(scene, camera);
            }

            animate();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=680)

# 3D 공룡 렌더링 함수
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

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        const dinoGroup = new THREE.Group();
        const material = new THREE.MeshStandardMaterial({{ color: '{dino_color}', roughness: 0.4 }});

        const body = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.2, 2), material);
        dinoGroup.add(body);
        const head = new THREE.Mesh(new THREE.BoxGeometry(1, 0.9, 1.3), material);
        head.position.set(0, 0.8, 1.2);
        dinoGroup.add(head);
        const tail = new THREE.Mesh(new THREE.ConeGeometry(0.5, 2.5, 8), material);
        tail.rotation.x = -Math.PI / 3;
        tail.position.set(0, -0.2, -1.8);
        dinoGroup.add(tail);

        const legGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.2, 8);
        const leg1 = new THREE.Mesh(legGeo, material); leg1.position.set(-0.6, -1, 0);
        const leg2 = new THREE.Mesh(legGeo, material); leg2.position.set(0.6, -1, 0);
        dinoGroup.add(leg1); dinoGroup.add(leg2);

        scene.add(dinoGroup);
        camera.position.set(3, 2, 5);
        camera.lookAt(0, 0, 0);

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
# 게임 단계별 진행
# ==========================================

# 0. 시작 화면 (사진 배경 + START 버튼)
if st.session_state.stage == 'TITLE':
    st.markdown("""
        <div class="title-screen">
            <div class="title-box">
                <h1 style="font-size: 55px; margin-bottom: 10px;">🦖 공룡 시대 생존기 🛸</h1>
                <p style="font-size: 20px; color: #ddd; margin-bottom: 30px;">일상에서 공룡 시대로! 1인칭 직접 조작 생존 게임</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
        if st.button("🚀 START", use_container_width=True):
            st.session_state.stage = 'STORY_3D'
            st.rerun()

# 1. 3D 스토리 직접 조작 (탑뷰 -> 이동 시 1인칭 -> 현관문 -> 세로 횡단보도 -> UFO 납치)
elif st.session_state.stage == 'STORY_3D':
    render_interactive_3d_world()
    
    if st.button("🌀 UFO에 납치되어 다음 단계로 진행", use_container_width=True):
        st.session_state.stage = 'ERA_SELECT'
        st.rerun()

# 2. 시대 선택
elif st.session_state.stage == 'ERA_SELECT':
    st.title("🌀 시공간의 틈새")
    st.subheader("정신을 차려보니 시공간이 일그러져 있습니다. 살아남을 시대를 선택하세요!")
    
    era_choice = st.radio("시대를 선택하세요:", list(ERA_DATA.keys()))
    st.info(ERA_DATA[era_choice]["desc"])
    
    if st.button("이 시대로 뛰어들기 🚀", use_container_width=True):
        st.session_state.selected_era = era_choice
        st.session_state.player_dino = random.choice(ERA_DATA[era_choice]["dinos"])
        st.session_state.hp = st.session_state.player_dino["hp"]
        st.session_state.stage = 'FLASH'
        st.rerun()

# 3. 번쩍이는 효과
elif st.session_state.stage == 'FLASH':
    flash_holder = st.empty()
    flash_holder.markdown("<h1 style='text-align: center; font-size: 100px; color: #ffff00;'>⚡⚡⚡</h1>", unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.stage = 'EGG'
    st.rerun()

# 4. 검은 화면 & 알 깨기 연출
elif st.session_state.stage == 'EGG':
    st.title("⬛ 어둠 속에서...")
    st.caption("눈을 떠보니 좁고 컴컴한 공간입니다. 알을 깨고 나가세요!")
    
    egg_states = ["🥚", "🥚 (금 가기 시작)", "🥚💥 (금이 쩍쩍 갈라집니다!)", "🐣 부화 성공!"]
    st.markdown(f'<div class="egg-crack">{egg_states[st.session_state.crack_count]}</div>', unsafe_allow_html=True)
    
    if st.session_state.crack_count < 3:
        if st.button("알 껍질 밀어내기! 🔨", use_container_width=True):
            st.session_state.crack_count += 1
            st.rerun()
    else:
        if st.button("밖으로 나가기 ✨", use_container_width=True):
            st.session_state.stage = 'DINO_3D'
            st.rerun()

# 5. 3D 공룡 확인 & 'ㄱㄱ' 버튼
elif st.session_state.stage == 'DINO_3D':
    dino = st.session_state.player_dino
    st.title(f"🦖 당신은 **{dino['name']}**(으)로 태어났습니다!")
    st.write(dino['desc'])
    
    render_3d_dino(dino['name'], dino['color'])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ㄱㄱ", use_container_width=True):
            st.session_state.stage = 'PLAYING'
            st.session_state.logs.append(f"[{st.session_state.selected_era}] 시대에 {dino['name']}(으)로 생존을 시작합니다!")
            st.rerun()

# 6. 메인 생존 게임
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
            st.error("☠ 체력이 다하여 생존에 실패했습니다...")
            if st.button("처음부터 다시하기"):
                st.session_state.clear()
                st.rerun()
        else:
            st.rerun()
            
    st.write("---")
    st.subheader("📜 생존 기록")
    for log in reversed(st.session_state.logs):
        st.write(log)
       
      
