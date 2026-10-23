import streamlit as st
import streamlit.components.v1 as components

# Streamlit 기본 설정 (전체 화면 꽉 차게)
st.set_page_config(
    page_title="Dino Survival Era Game",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 화면 전체 꽉 차게 여백 제거 스타일 설정
st.markdown("""
    <style>
        #root > div:nth-child(1) > div > div > div {
            padding: 0rem;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        iframe {
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# 3D 엔진(Three.js) 기반 전체 HTML/JS 통합 코드
game_html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dino Survival Game</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #000;
            font-family: 'Noto Sans KR', sans-serif;
            user-select: none;
        }
        #game-canvas {
            width: 100%;
            height: 100%;
            display: block;
            cursor: grab;
            outline: none;
        }
        #game-canvas:active {
            cursor: grabbing;
        }
        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 5;
        }
        .interactive { pointer-events: auto; }

        /* 첫 화면 배경 */
        #start-screen {
            position: absolute;
            width: 100%; height: 100%;
            background: radial-gradient(circle at 50% 30%, rgba(255, 140, 0, 0.4), transparent 70%),
                        linear-gradient(to bottom, #11031d 0%, #3b1130 35%, #8b2f15 65%, #d35400 85%, #1a252f 100%);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 10;
        }
        .bg-dino-svg { position: absolute; bottom: 0; width: 100%; height: 100%; pointer-events: none; }
        .title-box {
            z-index: 2; text-align: center; background: rgba(0, 0, 0, 0.65);
            padding: 40px 60px; border-radius: 20px; border: 2px solid rgba(255, 154, 60, 0.5);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8); backdrop-filter: blur(8px);
        }
        .title-box h1 { font-size: 52px; margin: 0 0 10px 0; color: #ff9f43; text-shadow: 0 0 15px rgba(255,110,0,0.8); }

        .btn-style {
            padding: 16px 42px; font-size: 22px; font-weight: 800; color: #fff;
            background: linear-gradient(135deg, #ff416c, #ff4b2b); border: none; border-radius: 50px;
            cursor: pointer; box-shadow: 0 6px 20px rgba(255, 75, 43, 0.5); transition: 0.25s;
        }
        .btn-style:hover { transform: scale(1.06); background: linear-gradient(135deg, #ff4b2b, #ff416c); }

        /* HUD 안내 메시지 및 조작 */
        #instruction {
            position: absolute; top: 25px; color: #fff; font-size: 16px; font-weight: bold;
            background: rgba(0, 0, 0, 0.75); padding: 12px 28px; border-radius: 30px; display: none;
            text-align: center; border: 1px solid rgba(255,255,255,0.2);
        }
        #exit-btn-container { position: absolute; bottom: 80px; display: none; }

        /* 시대 선택 화면 */
        #era-select-screen {
            position: absolute; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(20,10,30,0.8) 0%, rgba(5,2,10,0.95) 100%),
                        url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2000&auto=format&fit=crop') center/cover;
            display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 15;
        }
        #era-select-screen h2 { font-size: 48px; color: #ffd166; margin-bottom: 40px; text-shadow: 0 0 15px #ff9f43; }
        .era-btn-group { display: flex; gap: 35px; }
        
        .paw-btn {
            width: 220px; height: 220px; background: rgba(30, 20, 10, 0.85); border: 4px solid #ff9f43;
            border-radius: 50% 50% 40% 40%; display: flex; flex-direction: column; justify-content: center;
            align-items: center; cursor: pointer; transition: 0.3s; box-shadow: 0 10px 25px rgba(0,0,0,0.8);
            color: #ffffff; font-size: 24px; font-weight: 900; position: relative;
        }
        .paw-btn:hover { transform: translateY(-10px) scale(1.08); background: rgba(255, 110, 0, 0.9); border-color: #fff; }
        .paw-icon { font-size: 50px; margin-bottom: 10px; }

        /* 알 부화 UI & 상태창 */
        #egg-ui { position: absolute; bottom: 80px; display: none; z-index: 12; }
        #info-card {
            position: absolute; right: 50px; top: 50%; transform: translateY(-50%);
            width: 320px; background: rgba(15, 23, 42, 0.9); border: 2px solid #38bdf8;
            border-radius: 20px; padding: 25px; color: white; display: none; z-index: 12;
            box-shadow: 0 10px 30px rgba(0,200,255,0.3); backdrop-filter: blur(10px);
        }
        #info-card h3 { color: #38bdf8; font-size: 28px; margin-top: 0; border-bottom: 2px solid #38bdf8; padding-bottom: 8px; }
        #info-card p { font-size: 15px; line-height: 1.6; margin: 8px 0; color: #e2e8f0; }

        /* 게임 플레이 HUD */
        #dino-hud {
            position: absolute; top: 20px; left: 20px; width: 280px;
            background: rgba(0, 0, 0, 0.65); border-radius: 15px; padding: 15px;
            display: none; flex-direction: column; gap: 12px; border: 1px solid rgba(255,255,255,0.15);
            z-index: 10;
        }
        .hud-row { display: flex; align-items: center; gap: 12px; font-size: 20px; }
        .hud-bar-bg { flex: 1; height: 16px; background: #333; border-radius: 8px; overflow: hidden; border: 1px solid #555; }
        .hud-bar-fill { height: 100%; width: 100%; transition: width 0.3s; }
        .hp-fill { background: linear-gradient(90deg, #ff4d4d, #ff0055); }
        .atk-fill { background: linear-gradient(90deg, #ffaa00, #ff5500); }
        .def-fill { background: linear-gradient(90deg, #00d2ff, #0072ff); }

        /* 화면 암전 효과 */
        #fade-overlay {
            position: absolute; width: 100%; height: 100%; background: black;
            opacity: 0; pointer-events: none; transition: opacity 1.2s ease; z-index: 30;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="fade-overlay"></div>

    <!-- 시작 화면 -->
    <div id="start-screen" class="interactive">
        <svg class="bg-dino-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="720" cy="380" rx="90" ry="90" fill="#fff5cc" opacity="0.85"/>
            <path d="M-100 450 Q 200 350, 500 420 T 1100 390 T 1600 450 L 1600 900 L -100 900 Z" fill="#2d0b1e" opacity="0.7"/>
            <path d="M400 420 L480 300 L560 420 Z M750 400 L850 250 L950 400 Z" fill="#200515" opacity="0.9"/>
            <path d="M-50 550 Q 300 480, 700 560 T 1500 520 L 1500 900 L -50 900 Z" fill="#12020c"/>
        </svg>

        <div class="title-box">
            <h1>공룡 생존 게임</h1>
            <p>시공간을 넘어 펼쳐지는 위대한 공룡 시대 생존기</p>
            <button id="start-btn" class="btn-style">GAME START</button>
        </div>
    </div>

    <!-- 시대 선택 화면 -->
    <div id="era-select-screen" class="interactive">
        <h2>선택하세용</h2>
        <div class="era-btn-group">
            <div class="paw-btn" onclick="selectEra('triassic')">
                <span class="paw-icon">🐾</span>
                <span>트라이아스기</span>
            </div>
            <div class="paw-btn" onclick="selectEra('jurassic')">
                <span class="paw-icon">🐾</span>
                <span>쥐라기</span>
            </div>
            <div class="paw-btn" onclick="selectEra('cretaceous')">
                <span class="paw-icon">🐾</span>
                <span>백악기</span>
            </div>
        </div>
    </div>

    <!-- 알 부화 버튼 & 정보창 -->
    <div id="egg-ui" class="interactive">
        <button id="hatch-btn" class="btn-style">🐣 부화하기</button>
    </div>

    <div id="info-card">
        <h3 id="dino-name">티라노사우루스</h3>
        <p><b>식성:</b> <span id="dino-diet">육식</span></p>
        <p><b>크기:</b> <span id="dino-size">12m / 7톤</span></p>
        <p><b>특징:</b> <span id="dino-feat">거대한 턱과 강력한 치악력을 지닌 최고 포식자</span></p>
        <p><b>주 먹이:</b> <span id="dino-food">대형 초식 공룡</span></p>
        <p><b>공격력:</b> <span id="dino-atk-val">95%</span> | <b>방어력:</b> <span id="dino-def-val">70%</span></p>
        <div style="margin-top: 20px; text-align: center;">
            <button id="next-btn" class="btn-style" style="display:none; padding:10px 30px; font-size:16px;">다음으로 ➔</button>
        </div>
    </div>

    <!-- 게임 플레이 HUD -->
    <div id="dino-hud">
        <div class="hud-row">
            <span>❤️</span>
            <div class="hud-bar-bg"><div id="hp-bar" class="hud-bar-fill hp-fill"></div></div>
        </div>
        <div class="hud-row">
            <span>🦷</span>
            <div class="hud-bar-bg"><div id="atk-bar" class="hud-bar-fill atk-fill"></div></div>
        </div>
        <div class="hud-row">
            <span>🛡️</span>
            <div class="hud-bar-bg"><div id="def-bar" class="hud-bar-fill def-fill"></div></div>
        </div>
    </div>

    <!-- UI 레이어 -->
    <div id="ui-layer">
        <div id="instruction">화면을 클릭한 후 스페이스바를 누르세요!<br>(W,A,S,D키로 이동하고 마우스 드래그로 시점을 조절하세요)</div>
        <div id="exit-btn-container" class="interactive">
            <button id="exit-btn" class="btn-style">🚪 문 열고 나가기</button>
        </div>
    </div>

    <canvas id="game-canvas" tabindex="1"></canvas>

    <script>
        let scene, camera, renderer;
        let gameState = "START"; 
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let yaw = 0, pitch = 0;
        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };
        let playerPos = new THREE.Vector3(0, 1.6, 0);
        let characterMesh;

        let colliders = [];
        let ufoGroup;

        const dinoDB = {
            triassic: [
                { name: "코엘로피시스", diet: "육식", size: "3m / 20kg", feat: "날렵하고 민첩한 날카로운 톱니 이빨을 가진 초기 공룡", food: "작은 파충류, 곤충", atk: 60, def: 40, hp: 70 },
                { name: "플라테오사우루스", diet: "초식", size: "8m / 4톤", feat: "긴 목과 튼튼한 뒷다리를 가진 초기 대형 공룡", food: "높은 나무의 잎사귀", atk: 45, def: 65, hp: 85 }
            ],
            jurassic: [
                { name: "알로사우루스", diet: "육식", size: "9m / 2.3톤", feat: "쥐라기 생태계 최고의 맹수 포식자", food: "대형 초식 공룡", atk: 85, def: 60, hp: 88 },
                { name: "브라키오사우루스", diet: "초식", size: "25m / 60톤", feat: "높은 거대 커튼형 목을 가진 초거대 공룡", food: "침엽수 잎사귀", atk: 50, def: 95, hp: 100 }
            ],
            cretaceous: [
                { name: "티라노사우루스", diet: "육식", size: "12m / 8톤", feat: "지상 최강의 치악력을 자랑하는 킹 포식자", food: "대형 공룡 전반", atk: 98, def: 75, hp: 95 },
                { name: "트리케라톱스", diet: "초식", size: "9m / 12톤", feat: "3개의 뿔과 튼튼한 프릴 장갑을 가진 방어형 공룡", food: "낮은 풀과 줄기", atk: 80, def: 92, hp: 90 }
            ]
        };

        let currentDino = null;
        let eggMesh;

        const canvas = document.getElementById('game-canvas');
        const fadeOverlay = document.getElementById('fade-overlay');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 3000);
            
            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
            dirLight.position.set(100, 200, 100);
            dirLight.castShadow = true;
            scene.add(dirLight);

            camera.position.set(0, 10, 15);
            camera.lookAt(0, 0, 0);

            window.addEventListener('resize', onWindowResize);
            
            // 캔버스 클릭 시 포커스 부여하여 키 입력 확실히 받기
            canvas.addEventListener('click', () => {
                canvas.focus();
            });

            window.addEventListener('keydown', onKeyDown);
            window.addEventListener('keyup', onKeyUp);

            window.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            window.addEventListener('mouseup', () => { isMouseDown = false; });

            window.addEventListener('mousemove', (e) => {
                if ((gameState === "FIRST_PERSON" || gameState === "OUTSIDE" || gameState === "DINO_PLAY") && isMouseDown) {
                    const deltaX = e.clientX - previousMousePosition.x;
                    const deltaY = e.clientY - previousMousePosition.y;

                    const sensitivity = 0.0035;
                    yaw -= deltaX * sensitivity;
                    pitch -= deltaY * sensitivity;

                    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));
                    previousMousePosition = { x: e.clientX, y: e.clientY };
                }
            });

            document.getElementById('start-btn').addEventListener('click', startHouseGame);
            document.getElementById('exit-btn').addEventListener('click', goOutside);
            document.getElementById('hatch-btn').addEventListener('click', hatchEgg);
            document.getElementById('next-btn').addEventListener('click', enterDinoWorld);

            animate();
        }

        function addCollider(x, z, width, depth) {
            colliders.push({
                minX: x - width / 2 - 0.4,
                maxX: x + width / 2 + 0.4,
                minZ: z - depth / 2 - 0.4,
                maxZ: z + depth / 2 + 0.4
            });
        }

        function doFade(callback) {
            fadeOverlay.style.opacity = '1';
            setTimeout(() => {
                if (callback) callback();
                fadeOverlay.style.opacity = '0';
            }, 1200);
        }

        function startHouseGame() {
            document.getElementById('start-screen').style.display = 'none';
            gameState = "LIVING_ROOM_TOP";
            document.getElementById('instruction').style.display = 'block';
            canvas.focus();

            createComplexHouse();

            camera.position.set(0, 11, 8);
            camera.lookAt(0, 0, 0);
        }

        function createComplexHouse() {
            colliders = [];
            scene.background = new THREE.Color(0x1a1a1a);

            const floorMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.4 });
            const floor = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            const wallMat = new THREE.MeshStandardMaterial({ color: 0xede0d4 });
            function addWall(x, z, w, d) {
                const wall = new THREE.Mesh(new THREE.BoxGeometry(w, 4, d), wallMat);
                wall.position.set(x, 2, z);
                wall.castShadow = true;
                wall.receiveShadow = true;
                scene.add(wall);
                addCollider(x, z, w, d);
            }

            addWall(0, -10, 20, 0.4);
            addWall(-10, 0, 0.4, 20);
            addWall(10, 0, 0.4, 20);
            addWall(-5, 10, 10, 0.4);
            addWall(5, 10, 10, 0.4);

            addWall(-3, -2, 14, 0.3);
            addWall(4, -3, 0.3, 12);
            addWall(-5, 4, 10, 0.3);

            const rug = new THREE.Mesh(new THREE.PlaneGeometry(6, 4), new THREE.MeshStandardMaterial({ color: 0x3a5a40 }));
            rug.rotation.x = -Math.PI / 2; rug.position.set(0, 0.01, 1); scene.add(rug);

            const sofa = new THREE.Mesh(new THREE.BoxGeometry(4, 1.2, 1.6), new THREE.MeshStandardMaterial({ color: 0x2b2d42 }));
            sofa.position.set(0, 0.6, -0.5); scene.add(sofa);
            addCollider(0, -0.5, 4, 1.6);

            const tvStand = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.8, 1), new THREE.MeshStandardMaterial({ color: 0x4a3b32 }));
            tvStand.position.set(0, 0.4, 3.5); scene.add(tvStand);
            addCollider(0, 3.5, 3.5, 1);

            const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(3, 1.8, 0.1), new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 }));
            tvScreen.position.set(0, 1.8, 3.5); scene.add(tvScreen);

            const diningTable = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.9, 1.5), new THREE.MeshStandardMaterial({ color: 0xddb892 }));
            diningTable.position.set(7, 0.45, -6); scene.add(diningTable);
            addCollider(7, -6, 2.5, 1.5);

            const bed = new THREE.Mesh(new THREE.BoxGeometry(3, 1, 4), new THREE.MeshStandardMaterial({ color: 0xf4a261 }));
            bed.position.set(-7, 0.5, -7); scene.add(bed);
            addCollider(-7, -7, 3, 4);

            const toilet = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1, 1), new THREE.MeshStandardMaterial({ color: 0xffffff }));
            toilet.position.set(-8, 0.5, 1); scene.add(toilet);
            addCollider(-8, 1, 0.8, 1);

            createDoorWithHandle(0, 9.8);

            const charGroup = new THREE.Group();
            const body = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.2), new THREE.MeshStandardMaterial({ color: 0x3a86ff }));
            body.position.y = 0.6;
            const head = new THREE.Mesh(new THREE.SphereGeometry(0.25, 16, 16), new THREE.MeshStandardMaterial({ color: 0xffcdb2 }));
            head.position.y = 1.4;
            charGroup.add(body, head);
            characterMesh = charGroup;
            characterMesh.position.set(0, 0, 0);
            scene.add(characterMesh);
        }

        function createDoorWithHandle(x, z) {
            const doorGroup = new THREE.Group();
            const door = new THREE.Mesh(new THREE.BoxGeometry(2, 3.2, 0.15), new THREE.MeshStandardMaterial({ color: 0x5c3a21 }));
            door.position.y = 1.6;
            
            const handle = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.8 }));
            handle.position.set(0.7, 1.5, 0.1);
            doorGroup.add(door, handle);
            doorGroup.position.set(x, 0, z);
            scene.add(doorGroup);
        }

        function switchToFirstPerson() {
            gameState = "FIRST_PERSON";
            document.getElementById('instruction').style.display = 'none';
            if (characterMesh) scene.remove(characterMesh);

            playerPos.set(0, 1.6, 0);
            yaw = 0; pitch = 0;
            canvas.focus();
        }

        function goOutside() {
            document.getElementById('exit-btn-container').style.display = 'none';
            gameState = "OUTSIDE";

            while(scene.children.length > 0){ scene.remove(scene.children[0]); }

            scene.background = new THREE.Color(0x87CEEB);
            colliders = [];

            createTownCityAndSchool();

            playerPos.set(0, 1.6, 0);
            yaw = 0; pitch = 0;
            canvas.focus();
        }

        function createTownCityAndSchool() {
            const ground = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({ color: 0x2e8b57, roughness: 0.9 }));
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);

            const roadMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8 });
            const r1 = new THREE.Mesh(new THREE.BoxGeometry(20, 0.1, 300), roadMat);
            r1.position.set(0, 0.05, -150); scene.add(r1);

            const r2 = new THREE.Mesh(new THREE.BoxGeometry(250, 0.1, 20), roadMat);
            r2.position.set(115, 0.05, -300); scene.add(r2);

            const r3 = new THREE.Mesh(new THREE.BoxGeometry(20, 0.1, 500), roadMat);
            r3.position.set(230, 0.05, -550); scene.add(r3);

            const bldgColors = [0xcfd8dc, 0x90a4ae, 0xb0bec5, 0x78909c, 0xd7ccc8, 0xa1887f];

            for(let z = -30; z > -250; z -= 40) {
                createBuilding(-25, 12, z, 18, 18, 0xd7ccc8);
                createBuilding(25, 14, z, 18, 18, 0xb0bec5);
            }

            for(let x = 10; x < 210; x += 40) {
                createBuilding(x, 25 + Math.random()*25, -270, 24, 24, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
                createBuilding(x, 25 + Math.random()*25, -330, 24, 24, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
            }

            for(let z = -360; z > -680; z -= 45) {
                createBuilding(200, 30 + Math.random()*30, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
                createBuilding(260, 30 + Math.random()*30, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
            }

            const scX = 230, scZ = -780;

            const playground = new THREE.Mesh(new THREE.PlaneGeometry(180, 140), new THREE.MeshStandardMaterial({ color: 0xc2a649, roughness: 0.9 }));
            playground.rotation.x = -Math.PI / 2;
            playground.position.set(scX, 0.06, scZ + 10); scene.add(playground);

            createPlaygroundEquipment(scX - 60, scZ + 40);

            const schoolBuilding = new THREE.Mesh(new THREE.BoxGeometry(140, 22, 30), new THREE.MeshStandardMaterial({ color: 0x8d5b4c, roughness: 0.7 }));
            schoolBuilding.position.set(scX, 11, scZ - 60);
            schoolBuilding.castShadow = true;
            scene.add(schoolBuilding);
            addCollider(scX, scZ - 60, 140, 30);

            for(let rx = -60; rx <= 60; rx += 15) {
                for(let ry = 4; ry <= 18; ry += 5) {
                    const win = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 2.5), new THREE.MeshStandardMaterial({ color: 0x87ceeb, metalness: 0.5 }));
                    win.position.set(scX + rx, ry, scZ - 44.9);
                    scene.add(win);
                }
            }

            const wallMat = new THREE.MeshStandardMaterial({ color: 0x6e3b2e });
            createFenceSegment(scX, scZ - 80, 200, 0.8, wallMat);
            createFenceSegment(scX - 100, scZ, 0.8, 160, wallMat);
            createFenceSegment(scX + 100, scZ, 0.8, 160, wallMat);
            createFenceSegment(scX - 60, scZ + 80, 80, 0.8, wallMat);
            createFenceSegment(scX + 60, scZ + 80, 80, 0.8, wallMat);
        }

        function createBuilding(x, height, z, width, depth, colorHex) {
            const building = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.5 }));
            building.position.set(x, height / 2, z);
            building.castShadow = true;
            building.receiveShadow = true;
            scene.add(building);

            const roofMesh = new THREE.Mesh(new THREE.BoxGeometry(width * 0.4, 3, depth * 0.4), new THREE.MeshStandardMaterial({ color: 0x333333 }));
            roofMesh.position.set(x, height + 1.5, z);
            scene.add(roofMesh);

            addCollider(x, z, width, depth);
        }

        function createFenceSegment(x, z, width, depth, material) {
            const wall = new THREE.Mesh(new THREE.BoxGeometry(width, 2.5, depth), material);
            wall.position.set(x, 1.25, z);
            scene.add(wall);
            addCollider(x, z, width, depth);
        }

        function createPlaygroundEquipment(x, z) {
            const pgGroup = new THREE.Group();
            const slideMain = new THREE.Mesh(new THREE.BoxGeometry(3, 4, 10), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
            slideMain.rotation.x = 0.3; slideMain.position.set(0, 2, 0);
            pgGroup.add(slideMain);

            const swingFrame = new THREE.Mesh(new THREE.BoxGeometry(8, 5, 0.5), new THREE.MeshStandardMaterial({ color: 0xeab308 }));
            swingFrame.position.set(12, 2.5, 0);
            pgGroup.add(swingFrame);

            pgGroup.position.set(x, 0, z);
            scene.add(pgGroup);
        }

        function triggerAbduction() {
            gameState = "ABDUCTED";

            ufoGroup = new THREE.Group();
            const ufoBody = new THREE.Mesh(new THREE.CylinderGeometry(10, 18, 4, 32), new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.8 }));
            ufoGroup.add(ufoBody);
            ufoGroup.position.set(playerPos.x, playerPos.y + 25, playerPos.z);
            scene.add(ufoGroup);

            const beam = new THREE.Mesh(new THREE.CylinderGeometry(5, 10, 25, 32, 1, true), new THREE.MeshBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.4, side: THREE.DoubleSide }));
            beam.position.set(playerPos.x, playerPos.y + 12.5, playerPos.z);
            scene.add(beam);
        }

        function enterUfoInside() {
            gameState = "UFO_INSIDE";
            while(scene.children.length > 0){ scene.remove(scene.children[0]); }

            scene.background = new THREE.Color(0x020617);

            const room = new THREE.Mesh(new THREE.SphereGeometry(12, 32, 16), new THREE.MeshStandardMaterial({ color: 0x1e293b, side: THREE.BackSide }));
            scene.add(room);

            for(let i = -1; i <= 1; i++) {
                const alien = new THREE.Group();
                const head = new THREE.Mesh(new THREE.SphereGeometry(0.6, 16, 16), new THREE.MeshStandardMaterial({ color: 0x22c55e }));
                head.position.y = 1.4;
                const body = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.2, 1), new THREE.MeshStandardMaterial({ color: 0x15803d }));
                body.position.y = 0.5;
                alien.add(head, body);
                alien.position.set(i * 2.5, 0, -4);
                scene.add(alien);
            }

            camera.position.set(0, 1.2, 2);
            camera.lookAt(0, 1, -4);

            setTimeout(() => {
                doFade(() => {
                    document.getElementById('era-select-screen').style.display = 'flex';
                    gameState = "ERA_SELECT";
                });
            }, 3000);
        }

        function selectEra(eraKey) {
            document.getElementById('era-select-screen').style.display = 'none';

            const list = dinoDB[eraKey];
            currentDino = list[Math.floor(Math.random() * list.length)];

            doFade(() => {
                setupEggHatchScene();
            });
        }

        function setupEggHatchScene() {
            gameState = "EGG_HATCH";
            while(scene.children.length > 0){ scene.remove(scene.children[0]); }

            scene.background = new THREE.Color(0x292524);

            const nest = new THREE.Mesh(new THREE.CylinderGeometry(2, 2.5, 0.4), new THREE.MeshStandardMaterial({ color: 0x78350f }));
            nest.position.set(0, 0, 0); scene.add(nest);

            eggMesh = new THREE.Mesh(new THREE.SphereGeometry(1.2, 32, 32), new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.6 }));
            eggMesh.scale.set(1, 1.3, 1); eggMesh.position.set(0, 1.2, 0);
            scene.add(eggMesh);

            camera.position.set(0, 3.5, 4.5);
            camera.lookAt(0, 1, 0);

            document.getElementById('egg-ui').style.display = 'block';
        }

        function hatchEgg() {
            document.getElementById('egg-ui').style.display = 'none';

            scene.remove(eggMesh);

            const dinoMesh = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.5, 2.2), new THREE.MeshStandardMaterial({ color: 0x15803d }));
            dinoMesh.position.set(0, 1, 0); scene.add(dinoMesh);

            camera.position.set(0, 1.5, 3.5);
            camera.lookAt(0, 1, 0);

            setTimeout(() => {
                document.getElementById('dino-name').innerText = currentDino.name;
                document.getElementById('dino-diet').innerText = currentDino.diet;
                document.getElementById('dino-size').innerText = currentDino.size;
                document.getElementById('dino-feat').innerText = currentDino.feat;
                document.getElementById('dino-food').innerText = currentDino.food;
                document.getElementById('dino-atk-val').innerText = currentDino.atk + "%";
                document.getElementById('dino-def-val').innerText = currentDino.def + "%";

                document.getElementById('info-card').style.display = 'block';

                setTimeout(() => {
                    document.getElementById('next-btn').style.display = 'inline-block';
                }, 5000);
            }, 1000);
        }

        function enterDinoWorld() {
            document.getElementById('info-card').style.display = 'none';

            doFade(() => {
                gameState = "DINO_PLAY";
                while(scene.children.length > 0){ scene.remove(scene.children[0]); }

                scene.background = new THREE.Color(0xa5f3fc);

                const worldGround = new THREE.Mesh(new THREE.PlaneGeometry(5000, 5000), new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.9 }));
                worldGround.rotation.x = -Math.PI / 2; scene.add(worldGround);

                for(let i=0; i<300; i++) {
                    const tree = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.8, 12), new THREE.MeshStandardMaterial({ color: 0x78350f }));
                    const leaves = new THREE.Mesh(new THREE.ConeGeometry(4, 10, 8), new THREE.MeshStandardMaterial({ color: 0x166534 }));
                    leaves.position.y = 8; tree.add(leaves);
                    
                    let tx = (Math.random() - 0.5) * 2000;
                    let tz = (Math.random() - 0.5) * 2000;
                    tree.position.set(tx, 6, tz); scene.add(tree);
                }

                for(let i=0; i<20; i++) {
                    const otherDino = new THREE.Mesh(new THREE.BoxGeometry(3, 4, 6), new THREE.MeshStandardMaterial({ color: 0xb45309 }));
                    otherDino.position.set((Math.random()-0.5)*800, 2, (Math.random()-0.5)*800);
                    scene.add(otherDino);
                }

                document.getElementById('dino-hud').style.display = 'flex';
                document.getElementById('hp-bar').style.width = currentDino.hp + '%';
                document.getElementById('atk-bar').style.width = currentDino.atk + '%';
                document.getElementById('def-bar').style.width = currentDino.def + '%';

                playerPos.set(0, 2.5, 0);
                yaw = 0; pitch = 0;
                canvas.focus();
            });
        }

        function onKeyDown(e) {
            const key = e.key.toLowerCase();
            const code = e.code;

            if ((code === 'Space' || e.key === ' ') && gameState === "LIVING_ROOM_TOP") {
                switchToFirstPerson();
            }

            if (code === 'KeyW' || key === 'w' || key === 'ㅈ') moveForward = true;
            if (code === 'KeyS' || key === 's' || key === 'ㄴ') moveBackward = true;
            if (code === 'KeyA' || key === 'a' || key === 'ㅁ') moveLeft = true;
            if (code === 'KeyD' || key === 'd' || key === 'ㅇ') moveRight = true;
        }

        function onKeyUp(e) {
            const key = e.key.toLowerCase();
            const code = e.code;

            if (code === 'KeyW' || key === 'w' || key === 'ㅈ') moveForward = false;
            if (code === 'KeyS' || key === 's' || key === 'ㄴ') moveBackward = false;
            if (code === 'KeyA' || key === 'a' || key === 'ㅁ') moveLeft = false;
            if (code === 'KeyD' || key === 'd' || key === 'ㅇ') moveRight = false;
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function checkCollisions(newPos) {
            for (let i = 0; i < colliders.length; i++) {
                let c = colliders[i];
                if (newPos.x > c.minX && newPos.x < c.maxX && newPos.z > c.minZ && newPos.z < c.maxZ) {
                    return true;
                }
            }
            return false;
        }

        function animate() {
            requestAnimationFrame(animate);

            if (gameState === "FIRST_PERSON" || gameState === "OUTSIDE" || gameState === "DINO_PLAY") {
                const speed = (gameState === "DINO_PLAY") ? 1.2 : 0.7;

                camera.rotation.order = "YXZ";
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;

                const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
                const side = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);

                let nextPos = playerPos.clone();
                if (moveForward) nextPos.addScaledVector(forward, speed);
                if (moveBackward) nextPos.addScaledVector(forward, -speed);
                if (moveLeft) nextPos.addScaledVector(side, -speed);
                if (moveRight) nextPos.addScaledVector(side, speed);

                if (gameState === "FIRST_PERSON" || gameState === "OUTSIDE") {
                    if (!checkCollisions(nextPos)) {
                        playerPos.copy(nextPos);
                    } else {
                        let testX = playerPos.clone(); testX.x = nextPos.x;
                        if (!checkCollisions(testX)) playerPos.x = nextPos.x;

                        let testZ = playerPos.clone(); testZ.z = nextPos.z;
                        if (!checkCollisions(testZ)) playerPos.z = nextPos.z;
                    }
                } else {
                    playerPos.copy(nextPos);
                }

                camera.position.copy(playerPos);

                if (gameState === "FIRST_PERSON" && playerPos.z > 8.5) {
                    document.getElementById('exit-btn-container').style.display = 'block';
                }

                if (gameState === "OUTSIDE" && playerPos.z < -700 && Math.abs(playerPos.x - 230) < 60) {
                    triggerAbduction();
                }
            }

            if (gameState === "ABDUCTED") {
                playerPos.y += 0.2;
                camera.position.copy(playerPos);
                if (playerPos.y >= 26) {
                    enterUfoInside();
                }
            }

            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>"""

components.html(game_html, height=1000, scrolling=False)
