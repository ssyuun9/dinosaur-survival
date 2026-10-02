import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 기본 설정 (전체 화면 꽉 차게 설정)
st.set_page_config(
    page_title="Dino Survival Game",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 기본 CSS 적용 (여백 제거 및 100% 꽉 찬 화면)
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

# 3D 게임 및 HTML/JavaScript 전체 코드
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Game</title>
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
        #start-screen {
            position: absolute;
            width: 100%;
            height: 100%;
            /* 첨부해주신 공룡 배경 이미지 적용 */
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                        url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2000&auto=format&fit=crop') no-repeat center center / cover;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 10;
        }
        #start-btn, #exit-btn {
            padding: 15px 40px;
            font-size: 24px;
            font-weight: bold;
            color: white;
            background: #ff4b4b;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: 0.2s;
        }
        #start-btn:hover, #exit-btn:hover {
            background: #ff2b2b;
            transform: scale(1.05);
        }
        #instruction {
            position: absolute;
            top: 20px;
            color: white;
            font-size: 18px;
            background: rgba(0,0,0,0.6);
            padding: 10px 20px;
            border-radius: 20px;
            display: none;
            text-align: center;
        }
        #exit-btn-container {
            position: absolute;
            bottom: 100px;
            display: none;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            display: none;
            pointer-events: none;
        }
    </style>
    <!-- Three.js 스크립트 로드 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="start-screen" class="interactive">
        <h1 style="font-size: 52px; margin-bottom: 20px; text-shadow: 2px 2px 8px rgba(0,0,0,0.8);">공룡 생존 게임</h1>
        <button id="start-btn">START</button>
    </div>

    <div id="ui-layer">
        <div id="instruction">스페이스바(Space)를 누르면 조종을 시작합니다.<br>(마우스 버튼을 누른 채 드래그해야 화면이 회전합니다)</div>
        <div id="crosshair"></div>
        <div id="exit-btn-container" class="interactive">
            <button id="exit-btn">나가기</button>
        </div>
    </div>

    <canvas id="game-canvas"></canvas>

    <script>
        // 기본 씬 설정
        let scene, camera, renderer;
        let gameState = "START"; // START, LIVING_ROOM_TOP, FIRST_PERSON, OUTSIDE, ABDUCTED
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let yaw = 0, pitch = 0;
        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };
        let playerPos = new THREE.Vector3(0, 1.6, 0);
        let characterMesh;
        let isAbducted = false;
        let abductionTime = 0;
        let ufoGroup, tractorBeam;
        let abductionTriggerX = 0, abductionTriggerZ = 0;
        
        const canvas = document.getElementById('game-canvas');
        const startBtn = document.getElementById('start-btn');
        const startScreen = document.getElementById('start-screen');
        const instruction = document.getElementById('instruction');
        const exitBtnContainer = document.getElementById('exit-btn-container');
        const exitBtn = document.getElementById('exit-btn');
        const crosshair = document.getElementById('crosshair');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a1a);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
            
            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(50, 100, 50);
            scene.add(dirLight);

            // 초기 카메라 위치 (시작 화면용)
            camera.position.set(0, 10, 15);
            camera.lookAt(0, 0, 0);

            // 키보드 이벤트
            window.addEventListener('resize', onWindowResize);
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            // 마우스 클릭 시에만 화면 회전 처리
            window.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            window.addEventListener('mouseup', () => {
                isMouseDown = false;
            });

            window.addEventListener('mousemove', (e) => {
                if ((gameState === "FIRST_PERSON" || gameState === "OUTSIDE") && isMouseDown) {
                    const deltaX = e.clientX - previousMousePosition.x;
                    const deltaY = e.clientY - previousMousePosition.y;

                    const sensitivity = 0.004;
                    yaw -= deltaX * sensitivity;
                    pitch -= deltaY * sensitivity;

                    // 위아래 제한 (-89도 ~ 89도)
                    pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));

                    previousMousePosition = { x: e.clientX, y: e.clientY };
                }
            });

            startBtn.addEventListener('click', startGame);
            exitBtn.addEventListener('click', goOutside);

            animate();
        }

        // 1. START 버튼 클릭시: 거실 탑뷰 시점
        function startGame() {
            startScreen.style.display = 'none';
            gameState = "LIVING_ROOM_TOP";
            instruction.style.display = 'block';

            createLivingRoom();

            // 상공에서 위에서 내려다보는 3인칭 탑뷰 시점
            camera.position.set(0, 8, 5);
            camera.lookAt(0, 0, 0);
        }

        // 거실 생성
        function createLivingRoom() {
            scene.background = new THREE.Color(0x222222);

            // 바닥 (거실)
            const floorGeo = new THREE.PlaneGeometry(10, 10);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x8B5A2B });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 벽면
            const wallMat = new THREE.MeshStandardMaterial({ color: 0xdddddd });
            const backWall = new THREE.Mesh(new THREE.BoxGeometry(10, 4, 0.2), wallMat);
            backWall.position.set(0, 2, -5);
            scene.add(backWall);

            // 소파
            const sofa = new THREE.Mesh(new THREE.BoxGeometry(3, 1, 1.2), new THREE.MeshStandardMaterial({ color: 0x335588 }));
            sofa.position.set(-3, 0.5, -3);
            scene.add(sofa);

            // 현관문 (나가기 버튼 트리거 위치)
            const door = new THREE.Mesh(new THREE.BoxGeometry(1.5, 3, 0.1), new THREE.MeshStandardMaterial({ color: 0x4a2e00 }));
            door.position.set(0, 1.5, 4.9);
            scene.add(door);

            // 사람 캐릭터 (3인칭용)
            const charGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.6);
            const charMat = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
            characterMesh = new THREE.Mesh(charGeo, charMat);
            characterMesh.position.set(0, 0.8, 0);
            scene.add(characterMesh);
        }

        // 2. 스페이스바 눌렀을 때 1인칭 전환
        function switchToFirstPerson() {
            gameState = "FIRST_PERSON";
            instruction.style.display = 'none';
            crosshair.style.display = 'block';
            if (characterMesh) scene.remove(characterMesh); // 1인칭이므로 몸체 숨김

            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;
        }

        // 3. 집 밖으로 나가기 (도로 및 건물, 학교 로딩)
        function goOutside() {
            exitBtnContainer.style.display = 'none';
            gameState = "OUTSIDE";

            // 기존 거실 비우기
            while(scene.children.length > 0){ 
                scene.remove(scene.children[0]); 
            }

            // 하늘 및 야외 조명
            scene.background = new THREE.Color(0x87CEEB);
            const amb = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(amb);
            const sun = new THREE.DirectionalLight(0xffffcc, 1);
            sun.position.set(100, 200, 100);
            scene.add(sun);

            // 1km 굴곡 도로 및 다수의 건물, 학교 생성
            createCityAndRoad();

            // 플레이어 위치 초기화
            playerPos.set(0, 1.6, 0);
            yaw = 0;
            pitch = 0;

            // 외계인 납치 위치 지정 (도로 중간 꺾이는 구간 중 랜덤)
            abductionTriggerX = 200;
            abductionTriggerZ = -500;
        }

        // 도로, 많은 건물, 학교 지형 생성
        function createCityAndRoad() {
            const roadMat = new THREE.MeshStandardMaterial({ color: 0x333333 });
            const grassMat = new THREE.MeshStandardMaterial({ color: 0x2e8b57 });

            // 대지
            const ground = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), grassMat);
            ground.rotation.x = -Math.PI / 2;
            scene.add(ground);

            // 도로 구간 1: 직진 (0m ~ 300m)
            const r1 = new THREE.Mesh(new THREE.BoxGeometry(20, 0.1, 300), roadMat);
            r1.position.set(0, 0.05, -150);
            scene.add(r1);

            // 도로 구간 2: 우회전 후 이동 (X축 +200m)
            const r2 = new THREE.Mesh(new THREE.BoxGeometry(220, 0.1, 20), roadMat);
            r2.position.set(100, 0.05, -300);
            scene.add(r2);

            // 도로 구간 3: 좌회전 후 학교 방향 직진 (Z축 -500m)
            const r3 = new THREE.Mesh(new THREE.BoxGeometry(20, 0.1, 500), roadMat);
            r3.position.set(200, 0.05, -550);
            scene.add(r3);

            // 건물 색상 패럿
            const colors = [0xd1ccc0, 0x84817a, 0xcc8e35, 0xaaa69d, 0x40407a, 0x227093];

            // 1) 구간 1 양옆 건물 배치
            for(let z = -20; z > -280; z -= 30) {
                let h1 = 15 + Math.random() * 25;
                let b1 = new THREE.Mesh(new THREE.BoxGeometry(20, h1, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b1.position.set(-25, h1/2, z);
                scene.add(b1);

                let h2 = 15 + Math.random() * 25;
                let b2 = new THREE.Mesh(new THREE.BoxGeometry(20, h2, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b2.position.set(25, h2/2, z);
                scene.add(b2);
            }

            // 2) 구간 2 양옆 건물 배치
            for(let x = 10; x < 190; x += 30) {
                let h1 = 15 + Math.random() * 25;
                let b1 = new THREE.Mesh(new THREE.BoxGeometry(20, h1, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b1.position.set(x, h1/2, -275);
                scene.add(b1);

                let h2 = 15 + Math.random() * 25;
                let b2 = new THREE.Mesh(new THREE.BoxGeometry(20, h2, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b2.position.set(x, h2/2, -325);
                scene.add(b2);
            }

            // 3) 구간 3 양옆 건물 배치
            for(let z = -330; z > -750; z -= 35) {
                let h1 = 15 + Math.random() * 30;
                let b1 = new THREE.Mesh(new THREE.BoxGeometry(20, h1, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b1.position.set(175, h1/2, z);
                scene.add(b1);

                let h2 = 15 + Math.random() * 30;
                let b2 = new THREE.Mesh(new THREE.BoxGeometry(20, h2, 20), new THREE.MeshStandardMaterial({ color: colors[Math.floor(Math.random() * colors.length)] }));
                b2.position.set(225, h2/2, z);
                scene.add(b2);
            }

            // 학교 교문 & 운동장 (약 1km 거리 지점)
            const playground = new THREE.Mesh(new THREE.PlaneGeometry(200, 150), new THREE.MeshStandardMaterial({ color: 0xc2b280 }));
            playground.rotation.x = -Math.PI / 2;
            playground.position.set(200, 0.06, -875);
            scene.add(playground);

            // 학교 건물
            const schoolBuilding = new THREE.Mesh(new THREE.BoxGeometry(160, 30, 40), new THREE.MeshStandardMaterial({ color: 0xa52a2a }));
            schoolBuilding.position.set(200, 15, -970);
            scene.add(schoolBuilding);
        }

        // 4. UFO 및 외계인 납치 연출 생성
        function triggerAbduction() {
            isAbducted = true;
            gameState = "ABDUCTED";

            // UFO 생성
            ufoGroup = new THREE.Group();
            const ufoBody = new THREE.Mesh(
                new THREE.CylinderGeometry(15, 25, 5, 32),
                new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8, roughness: 0.2 })
            );
            const ufoDome = new THREE.Mesh(
                new THREE.SphereGeometry(10, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2),
                new THREE.MeshStandardMaterial({ color: 0x00ffff, transparent: true, opacity: 0.6 })
            );
            ufoDome.position.y = 2.5;
            ufoGroup.add(ufoBody, ufoDome);
            ufoGroup.position.set(playerPos.x, playerPos.y + 30, playerPos.z);
            scene.add(ufoGroup);

            // 초록색 광선 (Tractor Beam)
            const beamGeo = new THREE.CylinderGeometry(8, 12, 30, 32, 1, true);
            const beamMat = new THREE.MeshBasicMaterial({ color: 0x00ff00, transparent: true, opacity: 0.4, side: THREE.DoubleSide });
            tractorBeam = new THREE.Mesh(beamGeo, beamMat);
            tractorBeam.position.set(playerPos.x, playerPos.y + 15, playerPos.z);
            scene.add(tractorBeam);
        }

        // 입력 조작 처리
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

        // 매 프레임 업데이트 및 애니메이션 Loop
        function animate() {
            requestAnimationFrame(animate);

            // 1인칭 및 야외 지속 조종 이동 처리
            if (gameState === "FIRST_PERSON" || gameState === "OUTSIDE") {
                const speed = gameState === "OUTSIDE" ? 0.8 : 0.15;

                // 카메라 회전 계산 (마우스 드래그 360도 회전 적용)
                camera.rotation.order = "YXZ";
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;

                // 이동 방향 계산
                const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
                const side = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);

                if (moveForward) playerPos.addScaledVector(forward, speed);
                if (moveBackward) playerPos.addScaledVector(forward, -speed);
                if (moveLeft) playerPos.addScaledVector(side, -speed);
                if (moveRight) playerPos.addScaledVector(side, speed);

                camera.position.copy(playerPos);

                // 현관문 근처 도착 시 [나가기] 버튼 노출
                if (gameState === "FIRST_PERSON") {
                    if (playerPos.z > 3.8 && Math.abs(playerPos.x) < 1.5) {
                        exitBtnContainer.style.display = 'block';
                    } else {
                        exitBtnContainer.style.display = 'none';
                    }
                }

                // 야외 이동 중 랜덤 외계인 UFO 빨려 들어가는 트리거 체크
                if (gameState === "OUTSIDE" && !isAbducted) {
                    const distToTrigger = playerPos.distanceTo(new THREE.Vector3(abductionTriggerX, playerPos.y, abductionTriggerZ));
                    if (distToTrigger < 25) {
                        triggerAbduction();
                    }
                }
            }

            // UFO 납치 연출 (초록빛과 함께 몸이 떠오르는 연출)
            if (gameState === "ABDUCTED") {
                abductionTime += 0.05;
                playerPos.y += 0.15; // 캐릭터 상승
                camera.position.copy(playerPos);
                
                // UFO 회전 연출
                if (ufoGroup) ufoGroup.rotation.y += 0.05;

                // 카메라 화면을 약간 흔들리게 표현
                camera.position.x += Math.sin(abductionTime * 10) * 0.05;
            }

            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Streamlit 화면에 꽉 찬 3D 게임 임베딩
components.html(game_html, height=1000, scrolling=False)
