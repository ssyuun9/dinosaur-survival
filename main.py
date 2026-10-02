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

        #start-btn, #exit-btn, #restart-btn {
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
        #start-btn:hover, #exit-btn:hover, #restart-btn:hover {
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

        /* 우주 진출 성공/엔딩 오버레이 UI */
        #ending-screen {
            position: absolute;
            width: 100%;
            height: 100%;
            background: rgba(5, 5, 15, 0.85);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #00ffff;
            z-index: 20;
            backdrop-filter: blur(5px);
        }
        #ending-screen h2 {
            font-size: 48px;
            margin-bottom: 15px;
            text-shadow: 0 0 20px #00ffff;
        }
        #ending-screen p {
            font-size: 20px;
            color: #ffffff;
            margin-bottom: 30px;
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

    <!-- 우주 이송 엔딩 화면 -->
    <div id="ending-screen" class="interactive">
        <h2>🛸 외계인에게 납치되었습니다!</h2>
        <p>UFO에 실려 지구를 떠나 우주로 날아갔습니다...</p>
        <button id="restart-btn">처음부터 다시하기</button>
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

        let colliders = [];

        // 외계인 납치 & 우주 이송 상태 변수
        let isAbducted = false;
        let abductionTime = 0;
        let ufoGroup, tractorBeam;
        let schoolZoneTrigger = false;
        let abductionTimer = null;
        let ufoTargetHeight = 35; // UFO 설치 높이
        let abductionPhase = "LIFTING"; // "LIFTING", "BOARDED", "FLYING_TO_SPACE"
        let flySpeed = 0.5;

        const canvas = document.getElementById('game-canvas');
        const startBtn = document.getElementById('start-btn');
        const startScreen = document.getElementById('start-screen');
        const instruction = document.getElementById('instruction');
        const exitBtnContainer = document.getElementById('exit-btn-container');
        const exitBtn = document.getElementById('exit-btn');
        const crosshair = document.getElementById('crosshair');
        const warningMsg = document.getElementById('warning-msg');
        const endingScreen = document.getElementById('ending-screen');
        const restartBtn = document.getElementById('restart-btn');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 3000);
            
            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
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
            restartBtn.addEventListener('click', restartGame);

            animate();
        }

        function startGame() {
            startScreen.style.display = 'none';
            endingScreen.style.display = 'none';
            gameState = "LIVING_ROOM_TOP";
            instruction.style.display = 'block';

            createDetailedLivingRoom();

            camera.position.set(0, 8, 6);
            camera.lookAt(0, 0, 0);
        }

        function restartGame() {
            if (abductionTimer) clearTimeout(abductionTimer);
            isAbducted = false;
            schoolZoneTrigger = false;
            abductionPhase = "LIFTING";
            abductionTime = 0;
            flySpeed = 0.5;

            endingScreen.style.display = 'none';
            startScreen.style.display = 'flex';
            crosshair.style.display = 'none';
            warningMsg.style.display = 'none';

            while(scene.children.length > 0){ 
                scene.remove(scene.children[0]); 
            }
            gameState = "START";
        }

        function createDetailedLivingRoom() {
            colliders = [];

            scene.background = new THREE.Color(0x1e1e1e);

            const floor = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.4 }));
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            const rug = new THREE.Mesh(new THREE.PlaneGeometry(6, 4), new THREE.MeshStandardMaterial({ color: 0x3a5a40, roughness: 0.9 }));
            rug.rotation.x = -Math.PI / 2;
            rug.position.set(0, 0.01, 0);
            scene.add(rug);

            const wallMat = new THREE.MeshStandardMaterial({ color: 0xede0d4 });
            const backWall = new THREE.Mesh(new THREE.BoxGeometry(12, 4, 0.2), wallMat);
            backWall.position.set(0, 2, -6);
            scene.add(backWall);

            const sofaGroup = new THREE.Group();
            const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(4, 0.6, 1.8), new THREE.MeshStandardMaterial({ color: 0x2b2d42 }));
            sofaBase.position.set(0, 0.3, 0);
            const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(4, 1.2, 0.4), new THREE.MeshStandardMaterial({ color: 0x2b2d42 }));
            sofaBack.position.set(0, 0.9, -0.7);
            sofaGroup.add(sofaBase, sofaBack);
            sofaGroup.position.set(-3.5, 0, -3);
            scene.add(sofaGroup);

            const tvStand = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.8, 1), new THREE.MeshStandardMaterial({ color: 0x4a3b32 }));
            tvStand.position.set(-3.5, 0.4, 3.5);
            scene.add(tvStand);

            const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(3, 1.8, 0.1), new THREE.MeshStandardMaterial({ color: 0x050505 }));
            tvScreen.position.set(-3.5, 1.8, 3.5);
            scene.add(tvScreen);

            const doorFrame = new THREE.Mesh(new THREE.BoxGeometry(2.2, 3.2, 0.2), new THREE.MeshStandardMaterial({ color: 0x333333 }));
            doorFrame.position.set(0, 1.6, 5.9);
            scene.add(doorFrame);

            const door = new THREE.Mesh(new THREE.BoxGeometry(2, 3, 0.1), new THREE.MeshStandardMaterial({ color: 0x7f5539 }));
            door.position.set(0, 1.5, 5.85);
            scene.add(door);

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

        function switchToFirstPerson() {
            gameState = "FIRST_PERSON";
            instruction.style.display = 'none';
            crosshair.style.display = 'block';
            if (characterMesh) scene.remove(characterMesh);

            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;
        }

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
            scene.add(sun);

            colliders = [];

            createRealisticCityAndSchool();

            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;
        }

        function addCollider(x, z, width, depth) {
            colliders.push({
                minX: x - width / 2 - 0.5,
                maxX: x + width / 2 + 0.5,
                minZ: z - depth / 2 - 0.5,
                maxZ: z + depth / 2 + 0.5
            });
        }

        function createRealisticCityAndSchool() {
            const ground = new THREE.Mesh(new THREE.PlaneGeometry(2500, 2500), new THREE.MeshStandardMaterial({ color: 0x385e38, roughness: 0.9 }));
            ground.rotation.x = -Math.PI / 2;
            scene.add(ground);

            const roadMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.8 });
            const mainRoad = new THREE.Mesh(new THREE.BoxGeometry(24, 0.1, 800), roadMat);
            mainRoad.position.set(0, 0.05, -350);
            scene.add(mainRoad);

            const bldgColors = [0xcfd8dc, 0x90a4ae, 0xb0bec5, 0x78909c, 0xd7ccc8];
            for(let z = -40; z > -650; z -= 55) {
                if (Math.abs(z - (-300)) < 40) continue;
                let h1 = 20 + Math.random() * 35;
                createBuilding(-30, h1, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
                let h2 = 20 + Math.random() * 35;
                createBuilding(30, h2, z, 26, 26, bldgColors[Math.floor(Math.random()*bldgColors.length)]);
            }

            // 한국식 학교
            const schoolCenterX = 0;
            const schoolCenterZ = -780;

            const playground = new THREE.Mesh(new THREE.PlaneGeometry(180, 130), new THREE.MeshStandardMaterial({ color: 0xc2a649 }));
            playground.rotation.x = -Math.PI / 2;
            playground.position.set(schoolCenterX, 0.06, schoolCenterZ + 10);
            scene.add(playground);

            const schoolBuilding = new THREE.Mesh(new THREE.BoxGeometry(140, 22, 30), new THREE.MeshStandardMaterial({ color: 0x8d5b4c }));
            schoolBuilding.position.set(schoolCenterX, 11, schoolCenterZ - 60);
            scene.add(schoolBuilding);
            addCollider(schoolCenterX, schoolCenterZ - 60, 140, 30);

            const wallMat = new THREE.MeshStandardMaterial({ color: 0x6e3b2e });
            createFenceSegment(schoolCenterX, schoolCenterZ - 80, 200, 0.8, wallMat);
            createFenceSegment(schoolCenterX - 100, schoolCenterZ, 0.8, 160, wallMat);
            createFenceSegment(schoolCenterX + 100, schoolCenterZ, 0.8, 160, wallMat);
            createFenceSegment(schoolCenterX - 60, schoolCenterZ + 80, 80, 0.8, wallMat);
            createFenceSegment(schoolCenterX + 60, schoolCenterZ + 80, 80, 0.8, wallMat);
        }

        function createBuilding(x, height, z, width, depth, colorHex) {
            const building = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), new THREE.MeshStandardMaterial({ color: colorHex }));
            building.position.set(x, height / 2, z);
            scene.add(building);
            addCollider(x, z, width, depth);
        }

        function createFenceSegment(x, z, width, depth, material) {
            const wall = new THREE.Mesh(new THREE.BoxGeometry(width, 2.5, depth), material);
            wall.position.set(x, 1.25, z);
            scene.add(wall);
            addCollider(x, z, width, depth);
        }

        function checkSchoolZoneAndTriggerAbduction() {
            const inSchool = (playerPos.x > -95 && playerPos.x < 95 && playerPos.z > -850 && playerPos.z < -700);

            if (inSchool && !schoolZoneTrigger && !isAbducted) {
                schoolZoneTrigger = true;
                const randomDelay = Math.random() * 5000 + 3000;
                warningMsg.style.display = 'block';

                abductionTimer = setTimeout(() => {
                    if (gameState === "OUTSIDE") {
                        triggerAbduction();
                    }
                }, randomDelay);
            }
        }

        function triggerAbduction() {
            isAbducted = true;
            gameState = "ABDUCTED";
            abductionPhase = "LIFTING";
            warningMsg.style.display = 'none';

            ufoGroup = new THREE.Group();
            const ufoBody = new THREE.Mesh(
                new THREE.CylinderGeometry(12, 22, 4, 32),
                new THREE.MeshStandardMaterial({ color: 0x444444, metalness: 0.9, roughness: 0.1 })
            );
            const ufoDome = new THREE.Mesh(
                new THREE.SphereGeometry(8, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2),
                new THREE.MeshStandardMaterial({ color: 0x00ffff, transparent: true, opacity: 0.7 })
            );
            ufoDome.position.y = 2;
            ufoGroup.add(ufoBody, ufoDome);

            ufoGroup.position.set(playerPos.x, playerPos.y + ufoTargetHeight, playerPos.z);
            scene.add(ufoGroup);

            const beamGeo = new THREE.CylinderGeometry(6, 14, ufoTargetHeight, 32, 1, true);
            const beamMat = new THREE.MeshBasicMaterial({ color: 0x00ff66, transparent: true, opacity: 0.45, side: THREE.DoubleSide });
            tractorBeam = new THREE.Mesh(beamGeo, beamMat);
            tractorBeam.position.set(playerPos.x, playerPos.y + ufoTargetHeight / 2, playerPos.z);
            scene.add(tractorBeam);
        }

        function onKeyDown(e) {
            if (e.code === 'Space' && gameState === "LIVING_ROOM_TOP") switchToFirstPerson();
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

                if (gameState === "OUTSIDE") {
                    if (!checkCollisions(nextPos)) {
                        playerPos.copy(nextPos);
                    }
                    checkSchoolZoneAndTriggerAbduction();
                } else {
                    playerPos.x = Math.max(-5.5, Math.min(5.5, nextPos.x));
                    playerPos.z = Math.max(-5.5, Math.min(5.5, nextPos.z));
                }

                camera.position.copy(playerPos);

                if (gameState === "FIRST_PERSON") {
                    if (playerPos.z > 4.2 && Math.abs(playerPos.x) < 1.8) {
                        exitBtnContainer.style.display = 'block';
                    } else {
                        exitBtnContainer.style.display = 'none';
                    }
                }
            }

            // 외계인 납치 단계별 우주 발사 연출
            if (gameState === "ABDUCTED") {
                abductionTime += 0.03;

                // 1단계: 플레이어가 UFO 높이까지 수직 조용히 끌려올라감
                if (abductionPhase === "LIFTING") {
                    playerPos.y += 0.25;
                    camera.position.copy(playerPos);

                    if (ufoGroup) ufoGroup.rotation.y += 0.08;

                    // UFO 바닥 높이에 도착하면 탑승 완료!
                    if (playerPos.y >= ufoGroup.position.y - 1.5) {
                        abductionPhase = "BOARDED";
                        if (tractorBeam) scene.remove(tractorBeam); // 광선 끄기
                        crosshair.style.display = 'none';
                    }
                }

                // 2단계: UFO 탑승 후 잠시 후 우주로 순간 가속 발사!
                if (abductionPhase === "BOARDED") {
                    // 카메라 시점을 UFO 외부 시점으로 전환하여 날아가는 장면 연출
                    camera.position.set(ufoGroup.position.x, ufoGroup.position.y + 5, ufoGroup.position.z + 30);
                    camera.lookAt(ufoGroup.position);

                    abductionPhase = "FLYING_TO_SPACE";
                }

                // 3단계: UFO 우주로 급상승 (지구가 멀어짐)
                if (abductionPhase === "FLYING_TO_SPACE") {
                    flySpeed *= 1.05; // 가속도
                    ufoGroup.position.y += flySpeed;
                    ufoGroup.rotation.y += 0.15;

                    // 카메라가 UFO를 따라 같이 우주로 상공을 바라보며 추적
                    camera.position.y = ufoGroup.position.y - 10;
                    camera.position.z = ufoGroup.position.z + 40;
                    camera.lookAt(ufoGroup.position);

                    // 하늘 배경을 점차 캄캄한 우주(검정색)로 변경
                    scene.background.lerp(new THREE.Color(0x000005), 0.02);

                    // 약 400m 이상 우주 상공으로 날아가면 엔딩창 표출
                    if (ufoGroup.position.y > 450) {
                        gameState = "ENDED";
                        endingScreen.style.display = 'flex';
                    }
                }
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
