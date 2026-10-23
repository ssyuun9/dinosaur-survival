import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="Dino Survival Game",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 여백 제거 및 꽉 찬 화면 스타일 설정
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

# Three.js 기반 3D 게임 HTML/JS
game_html = """
<!DOCTYPE html>
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
        }
        .interactive {
            pointer-events: auto;
        }
        /* 공룡 생존 테마 SVG/CSS 그래픽 배경 */
        #start-screen {
            position: absolute;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 50% 30%, rgba(255, 140, 0, 0.4), transparent 70%),
                linear-gradient(to bottom, #11031d 0%, #3b1130 35%, #8b2f15 65%, #d35400 85%, #2c3e50 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 10;
            overflow: hidden;
        }

        .bg-dino-svg {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }

        .title-box {
            z-index: 2;
            text-align: center;
            background: rgba(0, 0, 0, 0.55);
            padding: 40px 60px;
            border-radius: 20px;
            border: 2px solid rgba(255, 154, 60, 0.5);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 15px rgba(255, 100, 0, 0.3);
            backdrop-filter: blur(8px);
        }

        .title-box h1 {
            font-size: 56px;
            margin: 0 0 10px 0;
            color: #ff9f43;
            text-shadow: 0 0 15px rgba(255, 110, 0, 0.8), 3px 3px 6px #000;
            letter-spacing: 2px;
        }

        .title-box p {
            font-size: 18px;
            color: #dddddd;
            margin-bottom: 25px;
            text-shadow: 1px 1px 3px #000;
        }

        #start-btn, #exit-btn {
            padding: 16px 48px;
            font-size: 24px;
            font-weight: 800;
            color: #ffffff;
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            border: none;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(255, 75, 43, 0.5);
            transition: all 0.25s ease;
            letter-spacing: 1px;
        }
        #start-btn:hover, #exit-btn:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 25px rgba(255, 75, 43, 0.8);
            background: linear-gradient(135deg, #ff4b2b, #ff416c);
        }

        #instruction {
            position: absolute;
            top: 30px;
            color: #ffffff;
            font-size: 17px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.75);
            padding: 12px 28px;
            border-radius: 30px;
            display: none;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        #exit-btn-container {
            position: absolute;
            bottom: 80px;
            display: none;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 10px;
            height: 10px;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(0,0,0,0.5);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            display: none;
            pointer-events: none;
        }
        #warning-msg {
            position: absolute;
            bottom: 120px;
            color: #ff3333;
            font-size: 26px;
            font-weight: 900;
            text-shadow: 0 0 10px #000;
            display: none;
            animation: blink 0.8s infinite alternate;
        }
        @keyframes blink {
            from { opacity: 0.2; }
            to { opacity: 1; }
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <!-- 고품질 공룡 배경 첫 화면 -->
    <div id="start-screen" class="interactive">
        <svg class="bg-dino-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="720" cy="380" rx="90" ry="90" fill="#fff5cc" opacity="0.85"/>
            <path d="M-100 450 Q 200 350, 500 420 T 1100 390 T 1600 450 L 1600 900 L -100 900 Z" fill="#2d0b1e" opacity="0.7"/>
            <path d="M400 420 L480 300 L560 420 Z M750 400 L850 250 L950 400 Z" fill="#200515" opacity="0.9"/>
            <path d="M830 280 Q850 240, 870 280 Z" fill="#ff5500" opacity="0.8"/>
            <path d="M-50 550 Q 300 480, 700 560 T 1500 520 L 1500 900 L -50 900 Z" fill="#12020c"/>
            <path d="M 150,750 Q 130,620 170,550 Q 190,520 220,530 Q 250,540 240,570 Q 220,600 230,650 Q 250,680 280,720 Q 300,750 260,780 Q 200,800 150,750 Z" fill="#090106"/>
            <path d="M 220,530 Q 260,510 290,525 Q 310,535 295,545 Q 260,550 230,540 Z" fill="#090106"/>
            <path d="M 1200,780 Q 1150,680 1170,620 Q 1180,590 1210,580 Q 1240,570 1260,590 Q 1280,620 1260,660 Q 1230,720 1280,770 Z" fill="#090106"/>
            <path d="M 1210,580 Q 1230,550 1270,550 Q 1290,560 1270,575 Q 1240,585 1220,585 Z" fill="#090106"/>
            <path d="M 300 200 Q 340 180 380 210 Q 340 215 300 200 Z M 330 200 L 320 230 L 340 205 Z" fill="#090106"/>
            <path d="M 1000 150 Q 1040 130 1080 160 Q 1040 165 1000 150 Z" fill="#090106"/>
        </svg>

        <div class="title-box">
            <h1>공룡 생존 게임</h1>
            <p>미지의 외계 생명체와 도심 속 공룡 위협에서 생존하세요</p>
            <button id="start-btn">GAME START</button>
        </div>
    </div>

    <div id="ui-layer">
        <div id="instruction">스페이스바(Space)를 누르면 조종을 시작합니다.<br>(마우스를 드래그하여 시점을 회전할 수 있습니다)</div>
        <div id="crosshair"></div>
        <div id="warning-msg">⚠️ 미확인 비행물체(UFO) 접근 중!</div>
        <div id="exit-btn-container" class="interactive">
            <button id="exit-btn">🚪 문 열고 나가기</button>
        </div>
    </div>

    <canvas id="game-canvas"></canvas>

    <script>
        let scene, camera, renderer;
        let gameState = "START"; 
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let yaw = 0, pitch = 0;
        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };
        let playerPos = new THREE.Vector3(0, 1.6, 0);
        let characterMesh;

        // 충돌체 Box 목록 (AABB 충돌 판정용)
        let colliders = [];

        // 외계인 납치 관련 변수
        let isAbducted = false;
        let abductionTime = 0;
        let ufoGroup, tractorBeam;
        let schoolZoneTrigger = false;
        let abductionTimer = null;

        const canvas = document.getElementById('game-canvas');
        const startBtn = document.getElementById('start-btn');
        const startScreen = document.getElementById('start-screen');
        const instruction = document.getElementById('instruction');
        const exitBtnContainer = document.getElementById('exit-btn-container');
        const exitBtn = document.getElementById('exit-btn');
        const crosshair = document.getElementById('crosshair');
        const warningMsg = document.getElementById('warning-msg');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
            
            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(50, 100, 50);
            dirLight.castShadow = true;
            scene.add(dirLight);

            camera.position.set(0, 10, 15);
            camera.lookAt(0, 0, 0);

            window.addEventListener('resize', onWindowResize);
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            window.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            window.addEventListener('mouseup', () => { isMouseDown = false; });

            window.addEventListener('mousemove', (e) => {
                if ((gameState === "FIRST_PERSON" || gameState === "OUTSIDE") && isMouseDown) {
                    const deltaX = e.clientX - previousMousePosition.x;
                    const deltaY = e.clientY - previousMousePosition.y;

                    const sensitivity = 0.0035;
                    yaw -= deltaX * sensitivity;
                    pitch -= deltaY * sensitivity;

                    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));
                    previousMousePosition = { x: e.clientX, y: e.clientY };
                }
            });

            startBtn.addEventListener('click', startGame);
            exitBtn.addEventListener('click', goOutside);

            animate();
        }

        // 1. 거실 화면 시작
        function startGame() {
            startScreen.style.display = 'none';
            gameState = "LIVING_ROOM_TOP";
            instruction.style.display = 'block';

            createDetailedLivingRoom();

            camera.position.set(0, 8, 6);
            camera.lookAt(0, 0, 0);
        }

        // 구체적이고 디테일한 집(거실) 내부 생성
        function createDetailedLivingRoom() {
            colliders = []; // 초기화

            scene.background = new THREE.Color(0x1e1e1e);

            // 마루 바닥
            const floorGeo = new THREE.PlaneGeometry(12, 12);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.4 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            // 카펫
            const rug = new THREE.Mesh(new THREE.PlaneGeometry(6, 4), new THREE.MeshStandardMaterial({ color: 0x3a5a40, roughness: 0.9 }));
            rug.rotation.x = -Math.PI / 2;
            rug.position.set(0, 0.01, 0);
            scene.add(rug);

            // 벽면
            const wallMat = new THREE.MeshStandardMaterial({ color: 0xede0d4 });
            const backWall = new THREE.Mesh(new THREE.BoxGeometry(12, 4, 0.2), wallMat);
            backWall.position.set(0, 2, -6);
            scene.add(backWall);

            const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 12), wallMat);
            leftWall.position.set(-6, 2, 0);
            scene.add(leftWall);

            const rightWall = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 12), wallMat);
            rightWall.position.set(6, 2, 0);
            scene.add(rightWall);

            // 소파
            const sofaGroup = new THREE.Group();
            const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(4, 0.6, 1.8), new THREE.MeshStandardMaterial({ color: 0x2b2d42 }));
            sofaBase.position.set(0, 0.3, 0);
            const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(4, 1.2, 0.4), new THREE.MeshStandardMaterial({ color: 0x2b2d42 }));
            sofaBack.position.set(0, 0.9, -0.7);
            sofaGroup.add(sofaBase, sofaBack);
            sofaGroup.position.set(-3.5, 0, -3);
            scene.add(sofaGroup);

            // TV 및 TV 장식장
            const tvStand = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.8, 1), new THREE.MeshStandardMaterial({ color: 0x4a3b32 }));
            tvStand.position.set(-3.5, 0.4, 3.5);
            scene.add(tvStand);

            const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(3, 1.8, 0.1), new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 }));
            tvScreen.position.set(-3.5, 1.8, 3.5);
            scene.add(tvScreen);

            // 거실 테이블
            const table = new THREE.Mesh(new THREE.BoxGeometry(2, 0.5, 1.2), new THREE.MeshStandardMaterial({ color: 0xddb892 }));
            table.position.set(0, 0.25, -0.5);
            scene.add(table);

            // 액자
            const frame = new THREE.Mesh(new THREE.BoxGeometry(2, 1.2, 0.05), new THREE.MeshStandardMaterial({ color: 0xb08968 }));
            frame.position.set(0, 2.5, -5.88);
            scene.add(frame);

            // 디테일 현관문
            const doorFrame = new THREE.Mesh(new THREE.BoxGeometry(2.2, 3.2, 0.2), new THREE.MeshStandardMaterial({ color: 0x333333 }));
            doorFrame.position.set(0, 1.6, 5.9);
            scene.add(doorFrame);

            const door = new THREE.Mesh(new THREE.BoxGeometry(2, 3, 0.1), new THREE.MeshStandardMaterial({ color: 0x7f5539 }));
            door.position.set(0, 1.5, 5.85);
            scene.add(door);

            const handle = new THREE.Mesh(new THREE.SphereGeometry(0.08, 16, 16), new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.8 }));
            handle.position.set(0.7, 1.5, 5.75);
            scene.add(handle);

            // 사람 캐릭터 (3인칭 표시용)
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

        // 1인칭 시점 전환
        function switchToFirstPerson() {
            gameState = "FIRST_PERSON";
            instruction.style.display = 'none';
            crosshair.style.display = 'block';
            if (characterMesh) scene.remove(characterMesh);

            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;
        }

        // 2. 야외 도심 및 한국 학교 환경
        function goOutside() {
            exitBtnContainer.style.display = 'none';
            gameState = "OUTSIDE";

            while(scene.children.length > 0){ 
                scene.remove(scene.children[0]); 
            }

            scene.background = new THREE.Color(0x87CEEB);
            
            const amb = new THREE.AmbientLight(0xffffff, 0.65);
            scene.add(amb);
            
            const sun = new THREE.DirectionalLight(0xfffaed, 1.1);
            sun.position.set(150, 250, 100);
            sun.castShadow = true;
            sun.shadow.mapSize.width = 2048;
            sun.shadow.mapSize.height = 2048;
            scene.add(sun);

            colliders = []; // 충돌 박스 초기화

            createRealisticCityAndSchool();

            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;
        }

        // 충돌체 등록 헬퍼 함수
        function addCollider(x, z, width, depth) {
            colliders.push({
                minX: x - width / 2 - 0.5,
                maxX: x + width / 2 + 0.5,
                minZ: z - depth / 2 - 0.5,
                maxZ: z + depth / 2 + 0.5
            });
        }

        // 사실적인 도심 건물 및 한국 학교 세팅
        function createRealisticCityAndSchool() {
            // 아스팔트 도로 & 잔디
            const ground = new THREE.Mesh(new THREE.PlaneGeometry(2500, 2500), new THREE.MeshStandardMaterial({ color: 0x385e38, roughness: 0.9 }));
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);

            // 도로망
            const roadMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.8 });
            
            const mainRoad = new THREE.Mesh(new THREE.BoxGeometry(24, 0.1, 800), roadMat);
            mainRoad.position.set(0, 0.05, -350);
            scene.add(mainRoad);

            const crossRoad = new THREE.Mesh(new THREE.BoxGeometry(400, 0.1, 24), roadMat);
            crossRoad.position.set(100, 0.05, -300);
            scene.add(crossRoad);

            // 건물 배치 (사실감 넘치는 창문 및 입체감)
            const bldgColors = [0xcfd8dc, 0x90a4ae, 0xb0bec5, 0x78909c, 0xd7ccc8, 0xa1887f];
            
            for(let z = -40; z > -650; z -= 55) {
                if (Math.abs(z - (-300)) < 40) continue; // 교차로 비우기

                // 좌측 건물군
                let h1 = 20 + Math.random() * 35;
                createBuilding(-30, h1, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
                
                // 우측 건물군
                let h2 = 20 + Math.random() * 35;
                createBuilding(30, h2, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
            }

            // --------------------------------------------------
            // 한국식 학교 영역 생성 (Z: -680 ~ -880, X: -100 ~ 100)
            // --------------------------------------------------
            const schoolCenterX = 0;
            const schoolCenterZ = -780;

            // 1) 흙 운동장
            const playground = new THREE.Mesh(new THREE.PlaneGeometry(180, 130), new THREE.MeshStandardMaterial({ color: 0xc2a649, roughness: 0.9 }));
            playground.rotation.x = -Math.PI / 2;
            playground.position.set(schoolCenterX, 0.06, schoolCenterZ + 10);
            scene.add(playground);

            // 축구대 (운동장 요소)
            const goalMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            const goal = new THREE.Mesh(new THREE.BoxGeometry(10, 3, 0.2), goalMat);
            goal.position.set(schoolCenterX, 1.5, schoolCenterZ + 60);
            scene.add(goal);

            // 2) 한국 학교 본관 건물
            const schoolBuilding = new THREE.Mesh(
                new THREE.BoxGeometry(140, 22, 30), 
                new THREE.MeshStandardMaterial({ color: 0x8d5b4c, roughness: 0.7 })
            );
            schoolBuilding.position.set(schoolCenterX, 11, schoolCenterZ - 60);
            schoolBuilding.castShadow = true;
            scene.add(schoolBuilding);
            addCollider(schoolCenterX, schoolCenterZ - 60, 140, 30);

            // 학교 창문 레이어
            for(let rx = -60; rx <= 60; rx += 15) {
                for(let ry = 4; ry <= 18; ry += 5) {
                    const win = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 2.5), new THREE.MeshStandardMaterial({ color: 0x87ceeb, metalness: 0.5 }));
                    win.position.set(schoolCenterX + rx, ry, schoolCenterZ - 44.9);
                    scene.add(win);
                }
            }

            // 3) 학교 둘레 담장 (붉은 벽돌 + 철제 펜스)
            const wallHeight = 2.5;
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x6e3b2e });

            // 뒷담장
            createFenceSegment(schoolCenterX, schoolCenterZ - 80, 200, 0.8, wallMat);
            // 좌측 담장
            createFenceSegment(schoolCenterX - 100, schoolCenterZ, 0.8, 160, wallMat);
            // 우측 담장
            createFenceSegment(schoolCenterX + 100, schoolCenterZ, 0.8, 160, wallMat);
            
            // 정면 담장 (교문 자리 비움: X: -20 ~ 20 보류)
            createFenceSegment(schoolCenterX - 60, schoolCenterZ + 80, 80, 0.8, wallMat);
            createFenceSegment(schoolCenterX + 60, schoolCenterZ + 80, 80, 0.8, wallMat);

            // 4) 교문 (정문 문주 및 철제 게이트)
            const gatePillarMat = new THREE.MeshStandardMaterial({ color: 0x444444 });
            const gate1 = new THREE.Mesh(new THREE.BoxGeometry(2.5, 4, 2.5), gatePillarMat);
            gate1.position.set(schoolCenterX - 18, 2, schoolCenterZ + 80);
            scene.add(gate1);
            addCollider(schoolCenterX - 18, schoolCenterZ + 80, 2.5, 2.5);

            const gate2 = new THREE.Mesh(new THREE.BoxGeometry(2.5, 4, 2.5), gatePillarMat);
            gate2.position.set(schoolCenterX + 18, 2, schoolCenterZ + 80);
            scene.add(gate2);
            addCollider(schoolCenterX + 18, schoolCenterZ + 80, 2.5, 2.5);

            // 교문 현판
            const nameplate = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.8, 0.1), new THREE.MeshStandardMaterial({ color: 0xd4af37 }));
            nameplate.position.set(schoolCenterX - 18, 2.8, schoolCenterZ + 78.7);
            scene.add(nameplate);
        }

        // 사실적인 건물 생성 함수 (충돌 박스 포함)
        function createBuilding(x, height, z, width, depth, colorHex) {
            const bldgGeo = new THREE.BoxGeometry(width, height, depth);
            const bldgMat = new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.5 });
            const building = new THREE.Mesh(bldgGeo, bldgMat);
            building.position.set(x, height / 2, z);
            building.castShadow = true;
            building.receiveShadow = true;
            scene.add(building);

            // 옥상 구조물
            const roofGeo = new THREE.BoxGeometry(width * 0.4, 3, depth * 0.4);
            const roofMesh = new THREE.Mesh(roofGeo, new THREE.MeshStandardMaterial({ color: 0x333333 }));
            roofMesh.position.set(x, height + 1.5, z);
            scene.add(roofMesh);

            // 충돌체에 추가
            addCollider(x, z, width, depth);
        }

        // 담장 및 충돌체 생성 함수
        function createFenceSegment(x, z, width, depth, material) {
            const wall = new THREE.Mesh(new THREE.BoxGeometry(width, 2.5, depth), material);
            wall.position.set(x, 1.25, z);
            wall.castShadow = true;
            scene.add(wall);

            addCollider(x, z, width, depth);
        }

        // 학교 영역 내 랜덤 외계인 납치 트리가
        function checkSchoolZoneAndTriggerAbduction() {
            // 학교 내부 영역 범위 (X: -95 ~ 95, Z: -850 ~ -700)
            const inSchool = (playerPos.x > -95 && playerPos.x < 95 && playerPos.z > -850 && playerPos.z < -700);

            if (inSchool && !schoolZoneTrigger && !isAbducted) {
                schoolZoneTrigger = true; // 감지 시작

                // 3초 ~ 9초 사이 랜덤 지연 후 납치 발생!
                const randomDelay = Math.random() * 6000 + 3000;

                warningMsg.style.display = 'block';

                abductionTimer = setTimeout(() => {
                    if (gameState === "OUTSIDE") {
                        triggerAbduction();
                    }
                }, randomDelay);
            }
        }

        // 외계인 납치 실행 연출
        function triggerAbduction() {
            isAbducted = true;
            gameState = "ABDUCTED";
            warningMsg.style.display = 'none';

            // UFO 생성
            ufoGroup = new THREE.Group();
            const ufoBody = new THREE.Mesh(
                new THREE.CylinderGeometry(12, 20, 4, 32),
                new THREE.MeshStandardMaterial({ color: 0x555555, metalness: 0.9, roughness: 0.1 })
            );
            const ufoDome = new THREE.Mesh(
                new THREE.SphereGeometry(8, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2),
                new THREE.MeshStandardMaterial({ color: 0x00ffff, transparent: true, opacity: 0.7 })
            );
            ufoDome.position.y = 2;
            ufoGroup.add(ufoBody, ufoDome);
            ufoGroup.position.set(playerPos.x, playerPos.y + 35, playerPos.z);
            scene.add(ufoGroup);

            // 초록색 수송 광선 (Tractor Beam)
            const beamGeo = new THREE.CylinderGeometry(6, 14, 40, 32, 1, true);
            const beamMat = new THREE.MeshBasicMaterial({ color: 0x00ff66, transparent: true, opacity: 0.45, side: THREE.DoubleSide });
            tractorBeam = new THREE.Mesh(beamGeo, beamMat);
            tractorBeam.position.set(playerPos.x, playerPos.y + 20, playerPos.z);
            scene.add(tractorBeam);
        }

        function onKeyDown(e) {
            if (e.code === 'Space' && gameState === "LIVING_ROOM_TOP") {
                switchToFirstPerson();
            }
            if (e.code === 'KeyW') moveForward = true;
            if (e.code === 'KeyS') moveBackward = true;
            if (e.code === 'KeyA') moveLeft = true;
            if (e.code === 'KeyD') moveRight = true;
        }

        function onKeyUp(e) {
            if (e.code === 'KeyW') moveForward = false;
            if (e.code === 'KeyS') moveBackward = false;
            if (e.code === 'KeyA') moveLeft = false;
            if (e.code === 'KeyD') moveRight = false;
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // 충돌 검사 알고리즘 (AABB)
        function checkCollisions(newPos) {
            for (let i = 0; i < colliders.length; i++) {
                let c = colliders[i];
                if (newPos.x > c.minX && newPos.x < c.maxX && newPos.z > c.minZ && newPos.z < c.maxZ) {
                    return true; // 충돌 발생
                }
            }
            return false;
        }

        // 메인 프레임 루프
        function animate() {
            requestAnimationFrame(animate);

            if (gameState === "FIRST_PERSON" || gameState === "OUTSIDE") {
                const speed = gameState === "OUTSIDE" ? 0.75 : 0.12;

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

                // 야외 이동 시 건물 및 담장 충돌 체크
                if (gameState === "OUTSIDE") {
                    if (!checkCollisions(nextPos)) {
                        playerPos.copy(nextPos);
                    } else {
                        // X축 및 Z축 각각 이동 테스트 (벽 밀림 완화)
                        let testX = playerPos.clone();
                        testX.x = nextPos.x;
                        if (!checkCollisions(testX)) playerPos.x = nextPos.x;

                        let testZ = playerPos.clone();
                        testZ.z = nextPos.z;
                        if (!checkCollisions(testZ)) playerPos.z = nextPos.z;
                    }

                    // 학교 영역 접근 시 랜덤 외계인 이벤트 체크
                    checkSchoolZoneAndTriggerAbduction();

                } else {
                    // 집 내부 이동 제한
                    playerPos.x = Math.max(-5.5, Math.min(5.5, nextPos.x));
                    playerPos.z = Math.max(-5.5, Math.min(5.5, nextPos.z));
                }

                camera.position.copy(playerPos);

                // 집 문 근처 시 나가기 버튼 표출
                if (gameState === "FIRST_PERSON") {
                    if (playerPos.z > 4.2 && Math.abs(playerPos.x) < 1.8) {
                        exitBtnContainer.style.display = 'block';
                    } else {
                        exitBtnContainer.style.display = 'none';
                    }
                }
            }

            // UFO 납치 연출
            if (gameState === "ABDUCTED") {
                abductionTime += 0.04;
                playerPos.y += 0.18; // 플레이어가 공중으로 떠오름
                camera.position.copy(playerPos);
                
                if (ufoGroup) ufoGroup.rotation.y += 0.08;
                camera.position.x += Math.sin(abductionTime * 12) * 0.08;
            }

            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Streamlit 화면에 렌더링
components.html(game_html, height=1000, scrolling=False)
