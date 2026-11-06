import streamlit as st
import streamlit.components.v1 as components
import urllib.request
import urllib.parse
import json

st.set_page_config(
    page_title="공룡 생존기",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 게임 화면은 브라우저 높이에 맞추고, 불필요한 상단 여백과 페이지 스크롤을 제거한다.
# Streamlit 기본 사이드바는 유지하되 흰색으로 표시하고 접기/펼치기 버튼을 왼쪽 아래에 둔다.
st.markdown(
    """
    <style>
      html, body, [data-testid="stAppViewContainer"],
      [data-testid="stApp"] {
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        height: 100dvh !important;
        min-height: 100dvh !important;
        overflow: hidden !important;
      }

      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"], footer {
        display: none !important;
        height: 0 !important;
      }

      [data-testid="stMain"], [data-testid="stMainBlockContainer"],
      [data-testid="stAppViewBlockContainer"], .block-container {
        margin: 0 !important;
        padding: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
      }

      [data-testid="stMain"] {
        height: 100vh !important;
        height: 100dvh !important;
        min-height: 0 !important;
        overflow: hidden !important;
      }

      [data-testid="stIFrame"] {
        display: block !important;
        height: 100vh !important;
        height: 100dvh !important;
        min-height: 0 !important;
        max-height: 100dvh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
      }
      [data-testid="stIFrame"] iframe, iframe {
        display: block !important;
        width: 100% !important;
        height: 100vh !important;
        height: 100dvh !important;
        min-height: 0 !important;
        max-height: 100dvh !important;
        border: 0 !important;
      }

      /* 왼쪽 페이지 선택 사이드바: 항상 읽기 쉬운 흰색 패널로 표시 */
      [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 260px !important;
        min-width: 260px !important;
        background: #ffffff !important;
        border-right: 1px solid #e6e6e6 !important;
      }
      [data-testid="stSidebar"] > div {
        background: #ffffff !important;
      }
      [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: #ffffff !important;
        height: 100dvh !important;
        overflow-y: auto !important;
        padding-top: 14px !important;
      }
      [data-testid="stSidebar"] * {
        color: #202124;
      }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #202124 !important;
      }
      [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 9px !important;
      }
      [data-testid="stSidebar"] [role="radiogroup"] label {
        background: #f7f9fb !important;
        border: 1px solid #e2e6ea !important;
        border-radius: 11px !important;
        padding: 10px 12px !important;
        margin: 0 !important;
      }

      /* 기본 접기/펼치기 화살표를 왼쪽 아래에 작게 고정 */
      [data-testid="stSidebarCollapseButton"],
      [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        left: 12px !important;
        bottom: 12px !important;
        top: auto !important;
        z-index: 1000000 !important;
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        min-height: 34px !important;
        border-radius: 9px !important;
        background: #f1f3f4 !important;
        box-shadow: 0 1px 5px #0002 !important;
      }
      [data-testid="stSidebarCollapseButton"] svg,
      [data-testid="stSidebarCollapsedControl"] svg {
        width: 16px !important;
        height: 16px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>공룡 생존기</title>
<style>
  * { box-sizing:border-box; }
  html, body { margin:0; width:100%; height:100%; overflow:hidden; background:#07110d; color:#fff;
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }
  #game { position:fixed; inset:0; width:100%; height:100%; overflow:hidden; }
  canvas { display:block; width:100%; height:100%; }
  .screen { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
    flex-direction:column; text-align:center; padding:24px; }
  #titleScreen { background:radial-gradient(ellipse at 50% 70%,#437b39 0%,#163a2b 35%,#07140f 75%); }
  #titleScreen:before { content:""; position:absolute; inset:0; opacity:.2; pointer-events:none;
    background:repeating-linear-gradient(115deg,transparent 0 45px,#b2d98d 46px 48px,transparent 49px 90px); }
  .hero { position:relative; z-index:1; text-shadow:0 5px 22px #000; }
  .title { font-size:clamp(42px,8vw,90px); line-height:1.05; font-weight:1000; letter-spacing:-2px; margin:0 0 14px; }
  .subtitle { font-size:clamp(15px,2vw,22px); color:#d9efcb; margin:0 0 34px; }
  .bigButton { border:2px solid #c9f39a; color:#10220f; font-weight:900; font-size:22px; padding:16px 38px;
    border-radius:18px; cursor:pointer; background:linear-gradient(135deg,#e0ff9c,#75c94d);
    box-shadow:0 8px 0 #315f2c,0 15px 35px #0008; transition:transform .15s; }
  .bigButton:hover { transform:translateY(-3px); }
  .smallButton { border:1px solid #d9f5c0; background:#173a27e8; color:white; padding:10px 16px;
    border-radius:10px; font-weight:800; cursor:pointer; }
  .smallButton:hover { background:#2d6a3d; }
  .smallButton:disabled { opacity:.78; cursor:default; }
  #eraScreen { display:none; background:linear-gradient(180deg,#071b13eF,#0c2717d9),radial-gradient(ellipse at bottom,#5a7f32,#08140e); }
  #eraTitle { font-size:clamp(28px,5vw,54px); margin:0 0 38px; text-shadow:0 4px 18px #000; }
  .eras { display:flex; gap:clamp(12px,3vw,34px); flex-wrap:wrap; justify-content:center; }
  .era { width:clamp(135px,22vw,235px); min-height:205px; border:2px solid #b6d99a; border-radius:22px;
    color:#fff; cursor:pointer; background:linear-gradient(160deg,#375d32dd,#101f17ee);
    box-shadow:0 12px 35px #0009; display:flex; align-items:center; justify-content:center; flex-direction:column;
    gap:12px; font-size:20px; font-weight:900; }
  .era:hover { transform:translateY(-5px); background:linear-gradient(160deg,#5a8c45,#183523); }
  .footprint { font-size:62px; filter:drop-shadow(0 4px 3px #0008); }
  #fade { position:absolute; inset:0; background:#000; opacity:0; pointer-events:none; transition:opacity 1.1s; z-index:20; }
  #hud { display:none; position:absolute; left:16px; top:16px; width:min(240px,55vw); padding:12px;
    border:1px solid #ffffff40; border-radius:14px; background:#07120dd9; backdrop-filter:blur(7px); }
  .stat { margin:7px 0; font-size:13px; text-align:left; }
  .statTop { display:flex; justify-content:space-between; gap:8px; margin-bottom:4px; }
  .bar { height:9px; border-radius:20px; overflow:hidden; background:#ffffff22; }
  .fill { height:100%; width:100%; border-radius:20px; transition:width .35s; }
  #healthFill { background:#ff5964; } #attackFill { background:#ffad42; } #defenseFill { background:#53c8ff; }
  /* 조종방법 안내는 화면 크기에 맞춰 줄바꿈하고 하단 안전 여백을 확보한다. */
  #help {
    display:none;
    position:absolute;
    left:50%;
    bottom:max(42px, calc(env(safe-area-inset-bottom, 0px) + 30px));
    transform:translateX(-50%);
    width:fit-content;
    max-width:min(94vw, 820px);
    padding:clamp(6px, 1.1vh, 9px) clamp(9px, 1.5vw, 13px);
    border-radius:12px;
    background:#07120de8;
    border:1px solid #ffffff45;
    font-size:clamp(10px, 1.35vh, 13px);
    line-height:1.35;
    text-align:center;
    overflow-wrap:anywhere;
    z-index:30;
  }
  #centerPrompt { position:absolute; left:50%; bottom:132px; transform:translateX(-50%); display:none; z-index:8; }
  #crosshair { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); color:#fff; opacity:.85; display:none;
    text-shadow:0 1px 5px #000; font-size:22px; pointer-events:none; }
  #infoCard { display:none; position:absolute; right:20px; top:50%; transform:translateY(-50%); width:min(310px,86vw);
    color:#fff; text-align:left; border:1px solid #d7e8be80; border-radius:18px; padding:18px;
    background:linear-gradient(145deg,#132b1ff2,#07130ff2); box-shadow:0 15px 40px #0009; }
  #infoCard h2 { margin:0 0 8px; font-size:25px; }
  #infoCard p { margin:7px 0; color:#e3efda; font-size:14px; line-height:1.45; }
  #eggHint { display:none; position:absolute; bottom:9%; left:50%; transform:translateX(-50%); }
  #survivalPanel {
    display:none; position:absolute; right:14px; top:14px; z-index:34;
    width:min(270px,48vw); padding:12px; border:1px solid #ffffff55;
    border-radius:14px; background:#071a13e8; color:#fff; text-align:left;
    box-shadow:0 8px 24px #0007; backdrop-filter:blur(7px);
  }
  #survivalPanel h3 { margin:0 0 8px; font-size:15px; }
  #inventoryText { font-size:12px; line-height:1.7; color:#e4f2df; margin-bottom:9px; }
  #survivalActions { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
  .survivalAction { border:1px solid #c5e7b4; border-radius:9px; padding:8px 5px;
    background:#245238; color:white; font-size:12px; font-weight:800; cursor:pointer; }
  .survivalAction:disabled { opacity:.4; cursor:not-allowed; }
  #survivalStatus { margin-top:8px; min-height:17px; color:#d7f5c9; font-size:11px; line-height:1.35; }
  #nextHint { display:none; position:absolute; bottom:24px; right:24px; }
  #message { display:none; position:absolute; inset:0; align-items:center; justify-content:center; flex-direction:column;
    background:#000; z-index:15; font-size:clamp(24px,4vw,44px); font-weight:900; }
  #message p { font-size:18px; font-weight:500; color:#bfe5b4; }
  #alienText { display:none; position:absolute; left:50%; top:16%; transform:translateX(-50%); font-size:clamp(20px,4vw,36px);
    text-shadow:0 2px 12px #000; background:#001b19a8; border-radius:14px; padding:14px 22px; }
  #combatPanel {
    display:none; position:absolute; right:104px; bottom:18px; z-index:35;
    width:min(286px, calc(100vw - 120px)); padding:10px 12px;
    border:1px solid #c9f5e6a8; border-radius:14px; background:#071b19e8;
    box-shadow:0 8px 24px #0008; color:#fff; text-align:left;
  }
  #combatStatus { min-height:18px; margin:0 0 7px; color:#e0f7ef; font-size:12px; line-height:1.35; }
  #enemyName { font-size:13px; font-weight:900; margin-bottom:5px; }
  #enemyHealthTrack { height:8px; overflow:hidden; border-radius:20px; background:#ffffff26; margin-bottom:8px; }
  #enemyHealthFill { width:0%; height:100%; border-radius:20px; background:linear-gradient(90deg,#ffcc65,#ff6d62); transition:width .2s; }
  #combatActions { display:flex; gap:7px; }
  .combatAction {
    flex:1; min-width:0; border:1px solid #b8eee0; border-radius:10px; padding:8px 7px;
    background:#17443b; color:#fff; font-weight:800; font-size:12px; cursor:pointer;
    touch-action:manipulation; user-select:none; -webkit-user-select:none;
  }
  .combatAction small { display:block; margin-top:2px; color:#d4f4e8; font-size:10px; font-weight:600; }
  .combatAction.active { background:#287b69; border-color:#aaffdf; box-shadow:0 0 0 2px #8affd944; }
  #deathActions { display:none; gap:12px; margin-top:24px; }
  .resultButton { min-width:112px; border:1px solid #d7f0da; border-radius:14px; padding:12px 24px; color:#102015;
    background:linear-gradient(135deg,#e6ffb4,#80d65b); font-size:19px; font-weight:900; cursor:pointer; }
  .resultButton.secondary { color:#fff; background:linear-gradient(135deg,#4b625a,#243a34); }
  #finalScreen { display:none; position:absolute; inset:0; z-index:45; pointer-events:none;
    background:linear-gradient(180deg,#06170a36 0%,#06170a08 48%,#06170a28 100%); }
  #finalTitle { position:absolute; top:15%; left:50%; transform:translateX(-50%); width:92%; margin:0;
    color:#fff; text-align:center; font-size:clamp(25px,4.2vw,48px); font-weight:1000;
    text-shadow:0 3px 16px #001b08,0 1px 4px #000; }
  #finalSub { position:absolute; top:24%; left:50%; transform:translateX(-50%); width:90%; color:#f0ffe7;
    text-align:center; font-size:clamp(13px,1.8vw,18px); text-shadow:0 2px 8px #000; }
  #exitBtn { position:absolute; top:67%; left:50%; transform:translate(-50%,-50%); pointer-events:auto;
    border:2px solid #ffffffb8; border-radius:16px; padding:13px 38px; color:#fff;
    background:#152c21eF; box-shadow:0 7px 22px #0008; font-size:20px; font-weight:900; cursor:pointer; }
  #exitNotice { display:none; position:absolute; inset:0; background:#07140f; color:#fff; align-items:center;
    justify-content:center; flex-direction:column; text-align:center; padding:24px; pointer-events:auto; }
  #exitNotice h2 { font-size:clamp(24px,4vw,42px); margin:0 0 12px; }
  #exitNotice p { color:#d7e8dc; font-size:15px; }
  #mobileControls { display:none; position:absolute; left:12px; bottom:55px; gap:10px; }
  .controlBtn { width:48px;height:48px;border-radius:14px;border:1px solid #fff8;background:#13271dbd;color:white;font-size:19px; }
  #runBtn {
    display:none; position:fixed; right:22px; bottom:24px; z-index:99999;
    width:68px; height:68px; border-radius:50%; border:2px solid #ffffffb8;
    background:#173a27ef; color:#fff; font-size:27px; font-weight:900;
    box-shadow:0 4px 14px #0008; cursor:pointer; pointer-events:auto;
    touch-action:manipulation; user-select:none; -webkit-user-select:none;
  }
  #runBtn.active { background:#79a83b; border-color:#e4ffc0; box-shadow:0 0 0 4px #d7ff8a55,0 4px 14px #0008; }
  #runBtn small { display:block; font-size:11px; line-height:1; margin-top:2px; }
  @media (max-width:700px) {
    #runBtn { right:16px; bottom:22px; width:62px; height:62px; }
    #combatPanel { right:84px; bottom:90px; width:min(270px, calc(100vw - 98px)); padding:8px 9px; }
    .combatAction { padding:7px 5px; font-size:11px; }
    #centerPrompt { bottom:118px; }
    #help {
      max-width:calc(100vw - 20px);
      font-size:clamp(10px, 1.5vh, 12px);
    }
  }
  @media (max-height:620px) {
    #help {
      bottom:max(32px, calc(env(safe-area-inset-bottom, 0px) + 24px));
      padding:5px 8px;
      font-size:10px;
      line-height:1.2;
    }
    #mobileControls { bottom:48px; }
    #runBtn { bottom:12px; width:56px; height:56px; }
  }
  @media (pointer:coarse) {
    #mobileControls { display:flex; flex-wrap:wrap; width:165px; }
    #help { bottom:max(34px, calc(env(safe-area-inset-bottom, 0px) + 24px)); }
  }
</style>
</head>
<body>
<div id="game">
  <div id="titleScreen" class="screen">
    <div class="hero">
      <div style="font-size:clamp(58px,10vw,112px);margin-bottom:12px">🦖 🌋 🦕</div>
      <h1 class="title">공룡 생존기</h1>
      <p class="subtitle">시간을 넘어, 공룡의 세계에서 살아남아라!</p>
      <button id="startBtn" class="bigButton">🌿 게임 시작 🌿</button>
    </div>
  </div>
  <div id="eraScreen" class="screen">
    <h1 id="eraTitle">발견할 시대를 선택하세용</h1>
    <div class="eras">
      <button class="era" data-era="jurassic"><span class="footprint">🐾</span><span>쥐라기</span><small>거대한 초식 공룡</small></button>
      <button class="era" data-era="cretaceous"><span class="footprint">🐾</span><span>백악기</span><small>다양한 공룡의 시대</small></button>
      <button class="era" data-era="triassic"><span class="footprint">🐾</span><span>트라이아스기</span><small>최초의 공룡 시대</small></button>
    </div>
  </div>
  <div id="hud">
    <div class="stat"><div class="statTop"><span>❤️ 체력</span><b id="healthPct">100%</b></div><div class="bar"><div id="healthFill" class="fill"></div></div></div>
    <div class="stat"><div class="statTop"><span>🦷 공격력</span><b id="attackPct">50%</b></div><div class="bar"><div id="attackFill" class="fill"></div></div></div>
    <div class="stat"><div class="statTop"><span>🛡️ 방어력</span><b id="defensePct">50%</b></div><div class="bar"><div id="defenseFill" class="fill"></div></div></div>
  </div>
  <div id="help">WASD 이동 · 마우스 시점 · Space 점프 · E 알 깨기/상호작용 · Shift 달리기 · Q 방어 · F 에너지 파동 · Esc 마우스 잠금 해제</div>
  <div id="crosshair">＋</div>
  <div id="centerPrompt"><button id="interactBtn" class="smallButton">상호작용</button></div>
  <div id="eggHint"><button id="hatchBtn" class="bigButton">🥚 부화하기</button></div>
  <div id="survivalPanel">
    <h3>🎒 생존 가방</h3>
    <div id="inventoryText">🍖 음식 0개 · 🪵 나무 0개 · 🪨 돌 0개</div>
    <div id="survivalActions">
      <button id="eatBtn" class="survivalAction" type="button">🍎 내가 먹기</button>
      <button id="buildBtn" class="survivalAction" type="button">🏠 집 짓기</button>
    </div>
    <div id="survivalStatus">주변의 알 가까이 가서 E 키를 눌러 깨 보세요!</div>
  </div>
  <div id="infoCard"><h2 id="dinoName">공룡</h2><p id="dinoFacts"></p></div>
  <div id="nextHint"><button id="nextBtn" class="bigButton">다음으로 ➜</button></div>
  <div id="message">
    <div id="messageMain">시간 이동 중...</div>
    <p id="messageSub"></p>
    <div id="deathActions">
      <button id="retryBtn" class="resultButton" type="button">다시?</button>
      <button id="endBtn" class="resultButton secondary" type="button">끝?</button>
    </div>
  </div>
  <div id="alienText">🛸 초록빛이 몸을 감싼다...</div>
  <div id="combatPanel">
    <div id="combatStatus">공룡이 가까이 오면 전투가 시작돼요.</div>
    <div id="enemyName">주변 탐색 중</div>
    <div id="enemyHealthTrack"><div id="enemyHealthFill"></div></div>
    <div id="combatActions">
      <button id="shieldBtn" class="combatAction" type="button">🛡️ 방어<small>Q · 누르고 있기</small></button>
      <button id="pulseBtn" class="combatAction" type="button">✨ 에너지 파동<small>F · 공격</small></button>
    </div>
  </div>
  <div id="finalScreen">
    <h1 id="finalTitle">🦖 함께 놀아줘서 고마워!</h1>
    <p id="finalSub">공룡 친구들이 작별 인사를 하고 있어요.</p>
    <button id="exitBtn" type="button">나가기</button>
    <div id="exitNotice"><h2>게임을 종료했습니다.</h2><p>브라우저에서 이 탭을 닫으면 완전히 나갈 수 있어요.</p></div>
  </div>
  <button id="runBtn" type="button" aria-label="달리기 켜기">🏃<small>달리기</small></button>
  <div id="mobileControls">
    <button class="controlBtn" data-key="w">▲</button>
    <button class="controlBtn" data-key="a">◀</button>
    <button class="controlBtn" data-key="s">▼</button>
    <button class="controlBtn" data-key="d">▶</button>
  </div>
  <div id="fade"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
(() => {
  const $ = id => document.getElementById(id);
  const game = $('game');
  let scene, camera, renderer, clock, player, yaw=0, pitch=0, pointerLocked=false;
  let phase='title', selectedEra='jurassic', hatchProgress=0, hatchStart=0, infoShownAt=0;
  let keys={}, objects=[], interactable=null, health=100, attack=50, defense=50, lastDamage=0;
  // 벽과 가구 등 충돌 대상
  let solidMeshes=[];
  let worldGroup, playerGroup, eggGroup, dinosaurGroup, alienGroup, cityGroup;
  let mouseDown=false, lastMouseX=0, lastMouseY=0, moving=false, abductionTriggered=false;
  let schoolBlackoutAt=0, fallingAvatar=null, fallingStartedAt=0;
  let livingDinos=[];
  // 선사시대 자원 알과 인벤토리
  let resourceEggs=[], inventory={food:0,wood:0,stone:0}, builtHouses=[];
  // 깨진 자원 알은 10초 후 같은 위치와 같은 보상으로 다시 생성한다.
  let eggRespawnQueue=[];
  const EGG_RESPAWN_DELAY=10000;
  let runEnabled=false;
  let jumpRequested=false;
  let verticalVelocity=0;
  let playerGrounded=true;
  let schoolEncounterStarted=false;
  // 선사시대 전투 및 엔딩 장면 상태
  let combatTarget=null, playerShielding=false, shieldReadyAt=0, pulseReadyAt=0;
  let combatNotice='공룡이 가까이 오면 전투가 시작돼요.', combatNoticeUntil=0;
  let shieldVisual=null, pulseEffects=[], celebrationDinos=[];
  const eras = {
    triassic: {
      label:'트라이아스기', color:0x9ca85a, sky:0xb7c6a0, ground:0x6f824a,
      dinos:[
        {name:'코엘로피시스',diet:'육식',size:'약 3m',traits:'가볍고 민첩하며 무리를 지어 움직임',food:'작은 파충류와 곤충',combat:'빠른 추격과 날카로운 이빨',kind:'small'},
        {name:'플라테오사우루스',diet:'초식',size:'약 8m',traits:'긴 목과 강한 뒷다리를 가진 초기 대형 공룡',food:'잎과 낮은 나뭇가지',combat:'몸집과 꼬리를 이용한 방어',kind:'long'},
        {name:'헤레라사우루스',diet:'육식',size:'약 6m',traits:'초기 육식 공룡으로 날카로운 이빨이 특징',food:'작은 동물과 다른 파충류',combat:'강한 턱과 빠른 돌진',kind:'raptor'}
      ]
    },
    jurassic: {
      label:'쥐라기', color:0x4f8748, sky:0x9db9a0, ground:0x416d3b,
      dinos:[
        {name:'스테고사우루스',diet:'초식',size:'약 9m',traits:'등의 골판과 꼬리 가시가 특징',food:'양치식물과 낮은 식물',combat:'가시 달린 꼬리로 방어',kind:'stego'},
        {name:'브라키오사우루스',diet:'초식',size:'약 22m',traits:'긴 목으로 높은 나뭇잎까지 먹음',food:'나무의 잎과 새순',combat:'거대한 몸집으로 위협을 막음',kind:'long'},
        {name:'알로사우루스',diet:'육식',size:'약 8.5m',traits:'큰 머리와 강한 뒷다리를 가진 포식자',food:'초식 공룡과 작은 동물',combat:'날카로운 이빨과 앞발톱',kind:'raptor'}
      ]
    },
    cretaceous: {
      label:'백악기', color:0x47844c, sky:0x9db8ad, ground:0x3d6b3c,
      dinos:[
        {name:'티라노사우루스',diet:'육식',size:'약 12m',traits:'큰 머리와 강력한 턱을 가진 대형 포식자',food:'큰 초식 공룡과 동물 사체',combat:'강력한 물기와 큰 체격',kind:'rex'},
        {name:'트리케라톱스',diet:'초식',size:'약 9m',traits:'세 개의 뿔과 목의 프릴이 특징',food:'낮은 식물과 관목',combat:'뿔과 단단한 프릴로 방어',kind:'trike'},
        {name:'파라사우롤로푸스',diet:'초식',size:'약 10m',traits:'머리 뒤로 길게 뻗은 볏이 특징',food:'잎과 여러 식물',combat:'무리 생활과 빠른 도주',kind:'long'}
      ]
    }
  };
  const setVisible = (id, show, display='block') => $(id).style.display = show ? display : 'none';
  function fadeToBlack(cb) {
    $('fade').style.opacity='1';
    setTimeout(() => { cb(); setTimeout(()=> $('fade').style.opacity='0', 120); }, 1000);
  }
  function initThree() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9db7a4);
    scene.fog = new THREE.Fog(0x9db7a4, 28, 160);
    shieldVisual = new THREE.Mesh(
      new THREE.SphereGeometry(1.25, 18, 14),
      new THREE.MeshBasicMaterial({color:0x70f5dc, wireframe:true, transparent:true, opacity:.30})
    );
    shieldVisual.visible=false;
    scene.add(shieldVisual);
    camera = new THREE.PerspectiveCamera(74, innerWidth/innerHeight, .1, 800);
    camera.rotation.order='YXZ';
    renderer = new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance'});
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.7));
    renderer.setSize(innerWidth,innerHeight);
    renderer.shadowMap.enabled=true;
    renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    game.insertBefore(renderer.domElement, game.firstChild);
    clock = new THREE.Clock();
    const hemi = new THREE.HemisphereLight(0xe5f4ff,0x40503a,2.0); scene.add(hemi);
    const sun = new THREE.DirectionalLight(0xfff0d5,2.2); sun.position.set(-30,55,25); sun.castShadow=true;
    sun.shadow.mapSize.set(1024,1024); scene.add(sun);
    window.addEventListener('resize', onResize);
    playerGroup = new THREE.Group(); scene.add(playerGroup);
    player = {position:new THREE.Vector3(0,1.7,6), speed:5.5, radius:.35};
    buildHome();
    animate();
  }
  function onResize() {
    if(!camera||!renderer) return;
    camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight);
  }
  function mat(color, roughness=.85, metalness=0) { return new THREE.MeshStandardMaterial({color,roughness,metalness}); }
  function box(parent, x,y,z, sx,sy,sz, material, opts={}) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz), material);
    m.position.set(x,y,z); m.castShadow=true; m.receiveShadow=true;
    if(opts.rotationY) m.rotation.y=opts.rotationY;
    parent.add(m);
    if(sx < 45 && sy > .35 && sz < 45) m.userData.solid = true;
    return m;
  }
  function sphere(parent,x,y,z,r,material, sx=1,sy=1,sz=1) {
    const m=new THREE.Mesh(new THREE.SphereGeometry(r,16,12),material); m.position.set(x,y,z); m.scale.set(sx,sy,sz);
    m.castShadow=true; parent.add(m); return m;
  }
  function cylinder(parent,x,y,z,rt,rb,h,material,segments=10) {
    const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,segments),material); m.position.set(x,y,z); m.castShadow=true; parent.add(m);
    if(h > 1.35 && Math.max(rt,rb) > .12 && Math.max(rt,rb) < 1.2) m.userData.solid = true;
    return m;
  }
  function clearWorld() {
    for(const obj of [...scene.children]) {
      if(obj !== camera && obj.type!=='HemisphereLight' && obj.type!=='DirectionalLight' && obj===playerGroup) continue;
      if(obj.userData.worldObject) scene.remove(obj);
    }
    if(worldGroup) scene.remove(worldGroup);
    if(cityGroup) scene.remove(cityGroup);
    if(eggGroup) scene.remove(eggGroup);
    if(dinosaurGroup) scene.remove(dinosaurGroup);
    if(alienGroup) scene.remove(alienGroup);
    worldGroup=cityGroup=eggGroup=dinosaurGroup=alienGroup=null;
    objects=[]; interactable=null; solidMeshes=[];
    resourceEggs=[];
    eggRespawnQueue=[];
  }
  function newWorld(color=0x73916a, sky=0xb5c9b2) {
    clearWorld();
    scene.background=new THREE.Color(sky); scene.fog=new THREE.Fog(sky,35,190);
    worldGroup=new THREE.Group(); scene.add(worldGroup);
    const ground=box(worldGroup,0,-.2,0,360,.4,360,mat(color)); ground.receiveShadow=true;
    return worldGroup;
  }
  function addTree(parent,x,z,scale=1,conifer=false) {
    const trunk=mat(0x59412b), leaf=mat(conifer?0x245333:0x32663a), leaf2=mat(0x487c43);
    cylinder(parent,x,1.3*scale,z,.18*scale,.28*scale,2.6*scale,trunk,8);
    if(conifer) {
      for(let i=0;i<3;i++){
        const c=new THREE.Mesh(new THREE.ConeGeometry((1.25-i*.23)*scale,1.8*scale,8),leaf);
        c.position.set(x,(2.4+i*.65)*scale,z); c.castShadow=true; parent.add(c);
      }
    } else {
      sphere(parent,x,3.1*scale,z,1.35*scale,leaf,1.0,1.05,.9);
      sphere(parent,x+.65*scale,3.45*scale,z-.15*scale,.85*scale,leaf2,1,1,.9);
      sphere(parent,x-.65*scale,3.4*scale,z+.2*scale,.8*scale,leaf,1,1,1);
    }
  }
  function addBush(parent,x,z,s=1) {
    const green=mat(0x3e783b);
    for(let i=0;i<4;i++) sphere(parent,x+(Math.random()-.5)*.8*s,.35*s,z+(Math.random()-.5)*.8*s,.45*s,green,1,.8,1);
  }
  function addRock(parent,x,z,s=1) {
    const m=new THREE.Mesh(new THREE.DodecahedronGeometry(s,0),mat(0x777b6a));
    m.position.set(x,s*.45,z); m.scale.y=.65; m.castShadow=true; parent.add(m);
  }
  function addHouse(parent,x,z,scale=1,color=0xd9c9a8) {
    const wall=mat(color), roof=mat(0x77463a), dark=mat(0x45352a), glass=mat(0x80b9c9,.35);
    box(parent,x,1.35*scale,z,5*scale,2.7*scale,4.6*scale,wall);
    const roofL=box(parent,x-.98*scale,3.15*scale,z,2.45*scale,.25*scale,5.25*scale,roof);
    roofL.rotation.z=.55;
    const roofR=box(parent,x+.98*scale,3.15*scale,z,2.45*scale,.25*scale,5.25*scale,roof);
    roofR.rotation.z=-.55;
    box(parent,x,0.85*scale,z+2.32*scale,.9*scale,1.7*scale,.12*scale,dark);
    sphere(parent,x+.28*scale,.9*scale,z+2.42*scale,.06*scale,mat(0xe4c15b));
    for(const wx of [-1.45,1.45]) {
      box(parent,x+wx*scale,1.65*scale,z+2.36*scale,.75*scale,.7*scale,.08*scale,glass);
      box(parent,x+wx*scale,1.65*scale,z+2.42*scale,.07*scale,.8*scale,.06*scale,dark);
      box(parent,x+wx*scale,1.65*scale,z+2.42*scale,.8*scale,.07*scale,.06*scale,dark);
    }
  }
  function addDoor(parent,x,z,rot=0,label='나가기') {
    const door=box(parent,x,1.05,z,.95,2.1,.12,mat(0x64432d),{rotationY:rot});
    const handle=sphere(parent,x+.3,1.05,z-.09,.07,mat(0xe0bd6b));
    door.userData.interact=true; door.userData.label=label; objects.push(door);
    return door;
  }
  function buildHome() {
    const g=newWorld(0x867f68,0xa7b8b7); scene.fog=new THREE.Fog(0xa7b8b7,30,100);
    const floor=mat(0xbcae91), wall=mat(0xe1d8c7), trim=mat(0x7b644d), wood=mat(0x785239), tile=mat(0x7c9a9c);
    // floorplan viewed from above-ish; rooms are open-roof for easier exploration
    box(g,0,-.1,0,24,.2,20,floor);
    // perimeter walls with gaps for doors
    box(g,0,1.5,-10,24,3,.3,wall); box(g,-12,1.5,0,.3,3,20,wall); box(g,12,1.5,0,.3,3,20,wall);
    box(g,-5.8,1.5,10,12.4,3,.3,wall); box(g,5.8,1.5,10,12.4,3,.3,wall);
    // internal partitions, leaving openings
    box(g,-3.2,1.5,-5, .25,3,10,wall); box(g,4.0,1.5,-5,.25,3,10,wall);
    box(g,0,1.5,0,8,.18,.18,trim);
    box(g,-7,1.5,2,.25,3,4,wall); box(g,7,1.5,2,.25,3,4,wall);
    // kitchen, bathroom tile, bedrooms and balcony
    box(g,-7,0.015,-5,9,.03,9,mat(0xc6b99e));
    box(g,8,0.02,-5,7,.04,9,tile);
    box(g,-7,0.02,5,9,.04,8,mat(0xb59a80));
    box(g,7,0.02,5,8,.04,8,mat(0xb59a80));
    // furniture living room
    box(g,0,.55,3,4,.8,1.4,mat(0x5c7664)); box(g,0,1.05,2.25,4,1,.3,mat(0x5c7664));
    box(g,-.1,.25,5.6,2.2,.3,1.3,wood); box(g,-.1,.43,5.6,2,.08,1.1,mat(0xd8c8a9));
    box(g,2.5,.8,-1,1.2,1.6,.3,trim); box(g,2.5,1.0,-.8,1,.8,.06,mat(0x263b3a));
    // kitchen cabinets and counter
    box(g,-8,.9,-8,6,1.8,.7,mat(0x92704f)); box(g,-8,1.9,-8,6,.15,.8,mat(0xd2c8b7));
    box(g,-10,.9,-4.2,1.3,1.8,1.2,mat(0xb5b7b4)); box(g,-6,.9,-4.2,1.4,1.8,1.2,mat(0xb5b7b4));
    // bathroom fixtures
    box(g,8,.4,-7,2.5,.7,1.5,mat(0xf2f1e9)); sphere(g,8,.9,-7,.5,mat(0xf2f1e9),1,.4,1);
    box(g,10,.6,-3.5,1.2,1.2,1.2,mat(0xf1f0e8)); cylinder(g,10,1.25,-3.5,.35,.35,.08,mat(0x9fc8d2));
    // beds
    for(const [x,z] of [[-8,5],[7,5]]) {
      box(g,x,.3,z,3.4,.5,4.2,wood); box(g,x,.62,z,3.2,.2,4,mat(0xd9d5ca));
      box(g,x,.78,z-1.2,3.1,.25,1.2,mat(x<0?0x91a9bd:0x9fba9b));
      box(g,x-1.2,.78,z-1.5,.7,.22,.7,mat(0xf1e9d9)); box(g,x+1.2,.78,z-1.5,.7,.22,.7,mat(0xf1e9d9));
    }
    // balcony
    box(g,0,.05,11.8,8,.1,3,mat(0x9e9b83));
    for(let x=-4;x<=4;x+=1) box(g,x,.65,13.1,.08,1.2,.08,trim);
    box(g,0,1.2,13.1,8,.1,.1,trim);
    // room labels on floor
    addDoor(g,0,9.8,0,'나가기');
    addDoor(g,-3.2,-1,Math.PI/2,'주방으로 이동');
    addDoor(g,4,-1,Math.PI/2,'욕실로 이동');
    addDoor(g,-7,0,0,'침실로 이동');
    addDoor(g,7,0,0,'침실로 이동');
    // exterior visible beyond front door
    for(let i=0;i<9;i++) addTree(g,-25+i*6,-20-Math.random()*10,.8+Math.random()*.5,i%2===0);
    for(let i=0;i<5;i++) addHouse(g,-18+i*9,-30,1.0, [0xd8c8a5,0xd7b9a2,0xb9c9b5][i%3]);
    player.position.set(0,1.7,5.7); yaw=0; pitch=0; updateCamera();
    phase='home'; setVisible('hud',false); setVisible('help',true); setVisible('crosshair',false);
  }
  function buildVillage() {
    const g=newWorld(0x687d4d,0xabc4d0);
    abductionTriggered=false;
    schoolEncounterStarted=false;
    schoolAliens=[];
    const houseSpots=[];
    for(let i=0;i<14;i++) houseSpots.push({
      x:(i%4-1.5)*17+(Math.random()-.5)*3,
      z:-10-Math.floor(i/4)*17,
      scale:.85+Math.random()*.3,
      color:[0xdccaa9,0xc8d2bf,0xd7b7a3,0xd9d9c7][i%4]
    });
    for(const h of houseSpots) addHouse(g,h.x,h.z,h.scale,h.color);
    for(const h of houseSpots) for(let j=0;j<4;j++) {
      let tx, tz, safe=false;
      for(let attempt=0;attempt<16;attempt++) {
        tx=h.x+(Math.random()-.5)*19;
        tz=h.z+(Math.random()-.5)*19;
        safe=!houseSpots.some(q=>Math.abs(tx-q.x)<5.0*q.scale && Math.abs(tz-q.z)<5.5*q.scale);
        if(safe) break;
      }
      // Keep the roadway and the school approach completely clear of trees.
      if(safe && !(Math.abs(tx)<5.8 && tz<18 && tz>-112) && !(Math.abs(tx)<14 && tz<-76 && tz>-108)) addTree(g,tx,tz,.7+Math.random()*.5,j%2===0);
    }
    // road
    box(g,0,.015,-45,8,.05,120,mat(0x555954));
    for(let z=8;z>-110;z-=7) box(g,0,.05,z, .18,.03,3,mat(0xe9dfad));
    // School at the far end of the village houses, directly connected to the road.
    box(g,0,.12,-94,38,.2,32,mat(0x4c7948));
    box(g,0,3.5,-98,22,7,13,mat(0xd8d8c9));
    box(g,0,7.1,-98,23,.35,14,mat(0x586b75));
    box(g,0,1.65,-91.35,3.1,3.3,.18,mat(0x527b8b));
    for(let x=-7;x<=7;x+=4) box(g,x,2.25,-91.25,1.65,1.7,.1,mat(0x8fc1d0));
    box(g,0,4.7,-91.18,9,.65,.12,mat(0xf2edda));
    // The school playground encounter starts automatically when the player enters its grounds.
    player.position.set(0,1.7,8); yaw=0; pitch=0; updateCamera();
    phase='village'; setVisible('hud',false); setVisible('help',true); setVisible('crosshair',true);
    // 마을 입구 정면의 불필요한 갈색 네모 문은 표시하지 않음.
  }
  function buildCity() {
    const g=newWorld(0x777b78,0xa9c0ce); cityGroup=g;
    const road=mat(0x45494c), sidewalk=mat(0xb7b8b1), glass=mat(0x54869b,.28,.15);
    box(g,0,.01,0,14,.08,300,road); box(g,-9,.03,0,4,.12,300,sidewalk); box(g,9,.03,0,4,.12,300,sidewalk);
    for(let z=12;z>-260;z-=8) box(g,0,.08,z, .2,.03,3.8,mat(0xf1e5b4));
    for(let side of [-1,1]) for(let i=0;i<18;i++){
      const z= -10-i*13, x=side*(16+Math.random()*5), h=8+Math.random()*30, w=7+Math.random()*5;
      box(g,x,h/2,z,w,h,8,mat([0x9eaaa9,0x8e9caa,0xb8b6a8,0x778d9a][i%4]));
      for(let y=2;y<h-1;y+=2.5) for(let wx=-w/2+1;wx<w/2;wx+=1.7)
        box(g,x+wx,y,z+4.08,.9,1.25,.04,glass);
    }
    // school at end of winding route, with left/right bends
    box(g,0,.03,-145,14,.1,38,road);
    box(g,-16,.03,-164,38,.1,10,road);
    box(g,-32,.03,-188,10,.1,40,road);
    box(g,-22,.03,-208,30,.1,10,road);
    // school grounds and building
    box(g,-22,.12,-231,54,.2,42,mat(0x53804a));
    box(g,-22,4.5,-246,32,9,14,mat(0xd9d6c7));
    box(g,-22,9.2,-246,33,.5,15,mat(0x66767c));
    box(g,-22,2.4,-238.8,4.5,4.8,.25,mat(0x6b8b9b));
    for(let x=-34;x<=-10;x+=6) box(g,x,2.8,-238.7,2.3,3.2,.12,mat(0x83b3c5));
    // gate posts and bars
    for(let x=-31;x<=-13;x+=3) box(g,x,1.8,-222,.16,3.6,.16,mat(0xddddcf));
    box(g,-22,3.6,-222,20,.2,.2,mat(0xddddcf));
    // playground: court, slide, swings
    box(g,-22,.25,-218,16,.25,10,mat(0x6e8c9b));
    for(let i=0;i<5;i++) box(g,-28+i*3,.4,-218, .08,.05,10,mat(0xf4f0d6));
    // slide
    box(g,-8,1.6,-232,.2,3,.2,mat(0xe9b53e)); box(g,-7,2.5,-230,2.2,.2,2,mat(0x4e8cc2));
    const slide=new THREE.Mesh(new THREE.BoxGeometry(1.4,.12,3.4),mat(0xe9b53e)); slide.position.set(-7,1.15,-227.7); slide.rotation.x=-.3; g.add(slide);
    // swings
    for(let x=-37;x<=-33;x+=4) {
      cylinder(g,x,2.3,-215,.07,.07,4.5,mat(0x5c6060));
      cylinder(g,x+3,2.3,-215,.07,.07,4.5,mat(0x5c6060));
      box(g,x+1.5,4.5,-215,3.2,.12,.12,mat(0x5c6060));
      for(let xx of [x+.7,x+2.3]) {
        cylinder(g,xx,2.7,-215,.025,.025,2.8,mat(0xdddddd));
        cylinder(g,xx,2.7,-213.9,.025,.025,2.8,mat(0xdddddd));
        box(g,xx,1.3,-214.45,.9,.14,.65,mat(0x3476aa));
      }
    }
    // surrounding trees
    for(let i=0;i<30;i++) {
      const tx=-55+Math.random()*65, tz=-185+Math.random()*55;
      if(tx>-42 && tx<-2 && tz>-256 && tz<-208) continue;
      addTree(g,tx,tz,.7+Math.random()*.6,i%2===0);
    }
    player.position.set(0,1.7,8); yaw=0; pitch=0; updateCamera();
    phase='city'; setVisible('crosshair',true); setVisible('help',true); setVisible('hud',false);
    const schoolTrigger=box(g,-22,1,-238,13,3,4,mat(0x000000)); schoolTrigger.material.transparent=true; schoolTrigger.material.opacity=0;
    schoolTrigger.userData.trigger='school'; objects.push(schoolTrigger);
  }
  function buildSchoolInterior() {
    const g=newWorld(0x9b9a85,0x91a9b4); scene.fog=new THREE.Fog(0x91a9b4,30,110);
    box(g,0,.05,0,36,.2,40,mat(0xc5c2b5));
    // corridor walls and classrooms
    box(g,-18,2.2,0,.3,4.4,40,mat(0xe1dfd2)); box(g,18,2.2,0,.3,4.4,40,mat(0xe1dfd2));
    box(g,0,2.2,-20,36,4.4,.3,mat(0xe1dfd2));
    box(g,-7,2.2,0,.25,4.4,36,mat(0xe1dfd2)); box(g,7,2.2,0,.25,4.4,36,mat(0xe1dfd2));
    // lockers, doors, classroom details
    for(let side of [-1,1]) for(let z=-15;z<=15;z+=3) {
      box(g,side*15,.95,z,1.2,1.9,1.0,mat(0x5d7c88));
      box(g,side*15.0,1.0,z,.04,.1,.06,mat(0xe4d8a9));
    }
    for(let x of [-12,0,12]) {
      box(g,x,.8,-10,3,.15,1.2,mat(0x8b6847)); box(g,x,1.35,-10,3,.9,.12,mat(0x3d594d));
      for(let dx of [-.8,.8]) box(g,x+dx,.48,-7,1.2,.1,.8,mat(0xb18a5c));
    }
    box(g,0,1.6,17,5,3.2,.25,mat(0x6b513a)); box(g,0,1.6,16.8,4.4,2.5,.1,mat(0x223d32));
    addDoor(g,0,19.5,0,'운동장으로 나가기');
    player.position.set(0,1.7,7); yaw=0; pitch=0; updateCamera();
    phase='school'; setVisible('help',true); setVisible('crosshair',true);
  }
  function addDinosaur(parent, spec, x=0,z=0,scale=1) {
    const group=new THREE.Group(); group.position.set(x,0,z); group.scale.setScalar(scale); parent.add(group);
    const skin=mat(spec.kind==='stego'?0x748f53:spec.kind==='trike'?0x7c9270:spec.kind==='rex'?0x657c4e:spec.kind==='long'?0x8a9c61:0x8a8659);
    const belly=mat(0xc5b98c), dark=mat(0x30372a), eye=mat(0xffd76c), horn=mat(0xd5c6a1);
    sphere(group,0,1.45,0,1,skin,1.35,.85,2.0);
    sphere(group,0,1.85,-1.25,.56,skin,1,.95,1.1);
    sphere(group,0,1.35,.95,.75,skin,.55,.65,2.4);
    sphere(group,0,1.1,1.6,.5,skin,.6,.55,1.8);
    // head and face direction toward -Z
    const headY=spec.kind==='long'?3.1:2.1;
    sphere(group,0,headY,-2.1,.65,skin,1,.85,1.05);
    sphere(group,0,headY-.28,-2.55,.48,belly,1,.45,.6);
    for(const side of [-1,1]) {
      sphere(group,side*.45,headY+.1,-2.45,.12,dark);
      sphere(group,side*.47,headY+.12,-2.52,.05,eye);
    }
    // legs
    for(const side of [-1,1]) for(const z of [-.75,.85]) {
      cylinder(group,side*.7,.58,z,.22,.28,1.05,skin,8);
      sphere(group,side*.7,.12,z-.08,.28,skin,1,.45,1.3);
    }
    if(spec.kind==='long') {
      cylinder(group,0,2.5,-1.35,.32,.48,2.5,skin,10).rotation.x=.45;
      sphere(group,0,3.6,-2.0,.3,skin,1,1,1);
    }
    if(spec.kind==='stego') {
      for(let i=0;i<7;i++) {
        const cone=new THREE.Mesh(new THREE.ConeGeometry(.35,.9,5),mat(0x8e6b48));
        cone.position.set(0,2.2,.85-i*.38); cone.rotation.x=Math.PI; group.add(cone);
      }
      for(let i=0;i<4;i++) {
        const plate=new THREE.Mesh(new THREE.ConeGeometry(.45,.85,5),skin);
        plate.position.set(i%2===0?-.42:.42,2.25,.8-i*.48); plate.rotation.z=i%2===0?.3:-.3; group.add(plate);
      }
    }
    if(spec.kind==='trike') {
      for(const side of [-1,1]) {
        const h=new THREE.Mesh(new THREE.ConeGeometry(.14,.85,8),horn); h.position.set(side*.45,headY+.45,-2.6); h.rotation.x=-Math.PI/2; h.rotation.z=side*.25; group.add(h);
      }
      const nose=new THREE.Mesh(new THREE.ConeGeometry(.13,.65,8),horn); nose.position.set(0,headY+.2,-2.9); nose.rotation.x=-Math.PI/2; group.add(nose);
      sphere(group,0,headY+.3,-1.8,.8,skin,1.25,.6,.5);
    }
    if(spec.kind==='rex'||spec.kind==='raptor'||spec.kind==='small') {
      for(const side of [-1,1]) cylinder(group,side*.85,1.55,-1.1,.12,.18,.8,skin,7).rotation.z=side*.7;
      for(let i=0;i<6;i++) {
        const tooth=new THREE.Mesh(new THREE.ConeGeometry(.06,.18,5),mat(0xf4ead3));
        tooth.position.set((i-2.5)*.12,headY-.42,-2.75); group.add(tooth);
      }
    }
    group.userData.spec=spec;
    return group;
  }
  function getDinoCombatProfile(spec) {
    // 공룡 종류별 체력·공격력·이동 속도. 큰 포식자일수록 상대하기 어렵다.
    const profiles = {
      small:  {hp:58,  power:17, speed:3.25},
      raptor: {hp:82,  power:25, speed:3.00},
      long:   {hp:116, power:31, speed:2.05},
      stego:  {hp:108, power:29, speed:2.15},
      trike:  {hp:132, power:38, speed:2.30},
      rex:    {hp:166, power:48, speed:2.75}
    };
    const base = profiles[spec.kind] || profiles.small;
    return {
      hp:base.hp, maxHp:base.hp, power:base.power, speed:base.speed,
      nextAttackAt:performance.now()+900+Math.random()*600,
      windupAt:0, stunnedUntil:0, defeated:false
    };
  }
  function setCombatNotice(message, duration=1700) {
    combatNotice=message;
    combatNoticeUntil=performance.now()+duration;
  }
  function refreshCombatPanel() {
    if(phase!=='prehistoric') { setVisible('combatPanel',false); return; }
    setVisible('combatPanel',true);
    if(combatTarget && combatTarget.userData.combat && !combatTarget.userData.combat.defeated) {
      const c=combatTarget.userData.combat;
      $('enemyName').textContent='🦖 '+combatTarget.userData.spec.name;
      $('enemyHealthFill').style.width=(Math.max(0,c.hp)/c.maxHp*100)+'%';
      if(performance.now()>combatNoticeUntil) {
        const playerPower=attack*.42+defense*.33+health*.25;
        $('combatStatus').textContent=c.power>playerPower+12
          ? '⚠️ 강한 상대예요! Q로 공격을 막아보세요.'
          : '공룡이 다가와요. F로 공격하고 Q로 방어하세요.';
      } else $('combatStatus').textContent=combatNotice;
    } else {
      $('enemyName').textContent='주변 공룡 탐색 중';
      $('enemyHealthFill').style.width='0%';
      $('combatStatus').textContent=performance.now()<combatNoticeUntil ? combatNotice : '공룡이 가까이 오면 전투가 시작돼요.';
    }
    $('shieldBtn').classList.toggle('active',playerShielding);
    $('shieldBtn').disabled=performance.now()<shieldReadyAt;
    $('shieldBtn').style.opacity=$('shieldBtn').disabled?'.58':'1';
  }
  function acquireCombatTarget() {
    if(combatTarget && combatTarget.parent && combatTarget.userData.combat && !combatTarget.userData.combat.defeated) return;
    combatTarget=null;
    let nearest=21;
    for(const d of livingDinos) {
      const c=d.userData.combat;
      if(!d.parent || !c || c.defeated) continue;
      const dx=d.position.x-player.position.x, dz=d.position.z-player.position.z;
      const dist=Math.hypot(dx,dz);
      if(dist<nearest) { nearest=dist; combatTarget=d; }
    }
    if(combatTarget) setCombatNotice('⚠️ '+combatTarget.userData.spec.name+'이(가) 다가옵니다!',1800);
  }
  function addPulseEffect(target) {
    const flash=new THREE.Mesh(
      new THREE.SphereGeometry(.72,16,12),
      new THREE.MeshBasicMaterial({color:0x75fff0,transparent:true,opacity:.78})
    );
    flash.position.set(target.position.x,1.5,target.position.z);
    scene.add(flash);
    pulseEffects.push({mesh:flash,bornAt:performance.now()});
  }
  function updatePulseEffects(now) {
    pulseEffects=pulseEffects.filter(effect=>{
      const progress=(now-effect.bornAt)/360;
      if(progress>=1) {
        scene.remove(effect.mesh); effect.mesh.geometry.dispose(); effect.mesh.material.dispose();
        return false;
      }
      effect.mesh.scale.setScalar(.7+progress*2.2);
      effect.mesh.material.opacity=.78*(1-progress);
      return true;
    });
  }
  function defeatDinosaur(dino) {
    if(!dino || !dino.userData.combat || dino.userData.combat.defeated) return;
    dino.userData.combat.defeated=true;
    dino.visible=false;
    scene.remove(dino);
    if(combatTarget===dino) combatTarget=null;
    health=Math.min(100,health+5);
    attack=Math.min(100,attack+1.5);
    updateStats();
    setCombatNotice('✨ '+dino.userData.spec.name+'이(가) 힘이 빠져 물러났어요! 체력이 조금 회복됐어요.',2300);
  }
  function fireEnergyPulse() {
    if(phase!=='prehistoric') return;
    const now=performance.now();
    if(now<pulseReadyAt) { setCombatNotice('에너지 파동을 충전하고 있어요!',650); return; }
    let target=combatTarget;
    if(!target || !target.parent || !target.userData.combat || target.userData.combat.defeated) {
      target=null;
      let nearest=11;
      for(const d of livingDinos) {
        if(!d.parent || !d.userData.combat || d.userData.combat.defeated) continue;
        const dist=Math.hypot(d.position.x-player.position.x,d.position.z-player.position.z);
        if(dist<nearest) { nearest=dist; target=d; }
      }
      if(target) combatTarget=target;
    }
    if(!target) { setCombatNotice('공격할 공룡이 사정거리 안에 없어요.',1000); return; }
    const distance=Math.hypot(target.position.x-player.position.x,target.position.z-player.position.z);
    if(distance>12) { setCombatNotice('공룡에게 조금 더 가까이 다가가세요.',1000); return; }
    pulseReadyAt=now+850;
    const c=target.userData.combat;
    const damage=Math.round(19+attack*.42);
    c.hp=Math.max(0,c.hp-damage);
    addPulseEffect(target);
    setCombatNotice('✨ 에너지 파동 적중! '+damage+' 만큼 힘을 약화했어요.',1100);
    if(c.hp<=0) defeatDinosaur(target);
    refreshCombatPanel();
  }
  function setPlayerShield(active) {
    playerShielding=!!active && phase==='prehistoric';
    if($('shieldBtn')) $('shieldBtn').classList.toggle('active',playerShielding);
    if(shieldVisual) shieldVisual.visible=playerShielding;
  }
  function playerDefeated() {
    if(phase!=='prehistoric') return;
    phase='playerDown';
    keys={}; setPlayerShield(false);
    document.exitPointerLock?.();
    setVisible('hud',false); setVisible('help',false); setVisible('combatPanel',false); setVisible('survivalPanel',false);
    setVisible('crosshair',false); setVisible('centerPrompt',false); setVisible('runBtn',false);
    setVisible('deathActions',true,'flex');
    $('message').style.background='linear-gradient(145deg,#101c18f5,#050907f5)';
    $('messageMain').textContent='🦖 공룡에게 패배했어요';
    $('messageSub').textContent='다시 도전할까요?';
    setVisible('message',true,'flex');
  }
  function updateCombatEncounter(dt) {
    if(phase!=='prehistoric') return;
    acquireCombatTarget();
    const d=combatTarget;
    if(!d) { refreshCombatPanel(); return; }
    const c=d.userData.combat;
    const dx=player.position.x-d.position.x, dz=player.position.z-d.position.z;
    const distance=Math.hypot(dx,dz)||.001;
    const now=performance.now();
    if(distance>38) {
      combatTarget=null; setCombatNotice('공룡이 멀리 물러났어요.',1200); refreshCombatPanel(); return;
    }
    if(now<c.stunnedUntil) {
      d.rotation.x=Math.sin(now*.015)*.08;
      refreshCombatPanel(); return;
    }
    d.rotation.y=Math.atan2(-dx,-dz);
    if(distance>2.75) {
      const speed=c.speed*(distance<5?0.72:1);
      d.position.x+=(dx/distance)*speed*dt;
      d.position.z+=(dz/distance)*speed*dt;
      c.windupAt=0;
    } else {
      if(!c.windupAt && now>=c.nextAttackAt) {
        c.windupAt=now+820;
        setCombatNotice('⚠️ '+d.userData.spec.name+'의 공격 준비! Q를 눌러 막으세요.',850);
      } else if(c.windupAt && now>=c.windupAt) {
        c.windupAt=0;
        c.nextAttackAt=now+1250;
        if(playerShielding && now>=shieldReadyAt) {
          shieldReadyAt=now+1650;
          const counterDamage=Math.round(20+attack*.25);
          c.hp=Math.max(0,c.hp-counterDamage);
          c.stunnedUntil=now+1050;
          addPulseEffect(d);
          setCombatNotice('🛡️ 방어 성공! 에너지 반격으로 '+counterDamage+' 만큼 약화했어요.',1450);
          if(c.hp<=0) defeatDinosaur(d);
        } else {
          const incoming=Math.max(6,Math.round(c.power*(1-defense/190)));
          health=Math.max(0,health-incoming);
          updateStats();
          setCombatNotice('💫 공룡의 공격을 받았어요! Q를 눌러 타이밍을 맞춰보세요.',1250);
          if(health<=0) playerDefeated();
        }
      }
    }
    refreshCombatPanel();
  }
  function addCheerDinosaur(parent,color,x,z,scale=1) {
    const g=new THREE.Group(); g.position.set(x,0,z); g.scale.setScalar(scale); parent.add(g);
    const skin=mat(color), belly=mat(0xd8c99b), eye=mat(0x17231b), iris=mat(0xffffff);
    sphere(g,0,1.55,0,.9,skin,1.0,1.0,.72);
    sphere(g,0,2.55,-.52,.63,skin,1.05,1.0,.9);
    sphere(g,0,2.34,-1.00,.34,belly,1.1,.65,.55);
    for(const side of [-1,1]) {
      sphere(g,side*.26,2.66,-1.04,.10,eye);
      sphere(g,side*.28,2.68,-1.12,.035,iris);
    }
    const tail=new THREE.Mesh(new THREE.ConeGeometry(.28,1.65,9),skin);
    tail.position.set(0,1.28,.95); tail.rotation.x=-Math.PI/2.35; g.add(tail);
    const legs=[];
    for(const side of [-1,1]) {
      const leg=new THREE.Group(); leg.position.set(side*.35,.92,.08); g.add(leg); legs.push(leg);
      const thigh=new THREE.Mesh(new THREE.CapsuleGeometry(.16,.52,4,8),skin); thigh.position.y=-.28; leg.add(thigh);
      const foot=new THREE.Mesh(new THREE.BoxGeometry(.32,.16,.45),skin); foot.position.set(0,-.58,-.08); leg.add(foot);
    }
    const arms=[];
    for(const side of [-1,1]) {
      const arm=new THREE.Group(); arm.position.set(side*.62,2.0,-.22); g.add(arm); arms.push(arm);
      const upper=new THREE.Mesh(new THREE.CapsuleGeometry(.105,.42,4,8),skin); upper.position.y=.28; arm.add(upper);
      const hand=new THREE.Mesh(new THREE.SphereGeometry(.14,10,8),skin); hand.position.set(0,.58,-.02); arm.add(hand);
    }
    g.userData.waveArms=arms; g.userData.waveLegs=legs; g.userData.wavePhase=Math.random()*Math.PI*2;
    return g;
  }
  function buildCelebrationScene() {
    setVisible('message',false); setVisible('deathActions',false);
    setVisible('hud',false); setVisible('help',false); setVisible('combatPanel',false); setVisible('survivalPanel',false);
    setVisible('crosshair',false); setVisible('runBtn',false); setVisible('mobileControls',false);
    setVisible('alienText',false); setVisible('centerPrompt',false);
    if(fallingAvatar) { scene.remove(fallingAvatar); fallingAvatar=null; }
    if(shieldVisual) shieldVisual.visible=false;
    combatTarget=null; playerShielding=false; celebrationDinos=[];
    const g=newWorld(0x5d9148,0x8ec8ee);
    box(g,0,.08,0,48,.16,22,mat(0x77a84e));
    for(let i=0;i<12;i++) {
      const x=(i-5.5)*6.5;
      if(Math.abs(x)>12) addTree(g,x,-9,.7+(i%3)*.12,i%2===0);
    }
    celebrationDinos.push(addCheerDinosaur(g,0x73a84b,-5.1,0,1.15));
    celebrationDinos.push(addCheerDinosaur(g,0x4b9b84,0, -1.1,1.32));
    celebrationDinos.push(addCheerDinosaur(g,0xd18b4f,5.1,0,1.15));
    player.position.set(0,1.7,20); yaw=0; pitch=0;
    camera.position.set(0,7.2,23); camera.lookAt(0,2.1,-.2);
    phase='ending';
    setVisible('finalScreen',true,'block');
    $('exitNotice').style.display='none';
    $('finalTitle').style.display='block'; $('finalSub').style.display='block'; $('exitBtn').style.display='block';
    renderer.domElement.style.display='block';
  }

  function updateInventoryUI() {
    $('inventoryText').textContent =
      `🍎 음식 ${inventory.food}개 · 🪵 나무 ${inventory.wood}개 · 🪨 돌 ${inventory.stone}개`;
    $('eatBtn').disabled=inventory.food<=0;
    $('buildBtn').disabled=inventory.wood<8 || inventory.stone<5;
  }
  function setSurvivalStatus(message) {
    $('survivalStatus').textContent=message;
  }
  function addResourceEgg(parent,x,z,index) {
    const group=new THREE.Group();
    group.position.set(x,0,z);
    parent.add(group);
    const nestMat=mat(0x65462f), shell=mat([0xe6d5a6,0xc9d8b0,0xd8c2a8][index%3],.55);
    // 작은 둥지와 알
    for(let i=0;i<9;i++) {
      const a=i*Math.PI*2/9;
      const twig=cylinder(group,Math.cos(a)*.58,.12,Math.sin(a)*.58,.045,.06,.32,nestMat,5);
      twig.rotation.z=Math.cos(a)*.45;
    }
    const egg=new THREE.Mesh(new THREE.SphereGeometry(.48,20,16),shell);
    egg.scale.set(.82,1.18,.82); egg.position.y=.62; egg.castShadow=true; group.add(egg);
    const spots=mat(0x8c7655);
    for(let i=0;i<3;i++) sphere(group,Math.cos(i*2.1)*.22,.72+(i%2)*.18,Math.sin(i*2.1)*.22,.055,spots,.8,1,.8);
    group.userData.resourceEgg=true;
    group.userData.eggMesh=egg;
    group.userData.spawnIndex=index;
    group.userData.reward=['food','wood','stone'][index%3];
    group.userData.rewardCount=group.userData.reward==='food'?2:(group.userData.reward==='wood'?3:2);
    group.userData.label='🥚 자원 알 깨기';
    group.userData.trigger='resourceEgg';
    resourceEggs.push(group);
    objects.push(group);
  }
  function placeResourceEggs(parent) {
    // 시작 둥지와 착지 위치를 피해서 숲·바위·강 주변에 골고루 배치
    const spots=[
      [-18,-18],[21,-24],[-42,-52],[43,-65],[-72,-12],[76,-38],
      [-95,-92],[91,-112],[-15,-118],[34,-145],[-118,35],[112,48]
    ];
    spots.forEach((p,i)=>addResourceEgg(parent,p[0],p[1],i));
  }
  function breakResourceEgg(eggGroupItem) {
    if(!eggGroupItem || !eggGroupItem.parent) return;
    const reward=eggGroupItem.userData.reward;
    const count=eggGroupItem.userData.rewardCount;
    // 알이 있던 위치와 종류를 저장해 10초 뒤 같은 자리에 다시 만든다.
    eggRespawnQueue.push({
      parent:eggGroupItem.parent,
      x:eggGroupItem.position.x,
      z:eggGroupItem.position.z,
      index:eggGroupItem.userData.spawnIndex||0,
      respawnAt:performance.now()+EGG_RESPAWN_DELAY
    });
    const mesh=eggGroupItem.userData.eggMesh;
    if(mesh) {
      mesh.material=mat(0x9b8060);
      mesh.scale.set(.2,.12,.2);
    }
    const labels={food:'음식',wood:'나무',stone:'돌'};
    inventory[reward]+=count;
    objects=objects.filter(o=>o!==eggGroupItem);
    resourceEggs=resourceEggs.filter(o=>o!==eggGroupItem);
    eggGroupItem.parent.remove(eggGroupItem);
    updateInventoryUI();
    setSurvivalStatus(`${labels[reward]} ${count}개를 얻었어요! 깨진 알은 10초 뒤 다시 나타나요.`);
    interactable=null;
    setVisible('centerPrompt',false);
  }
  // 10초가 지난 알을 원래 위치에 다시 생성한다.
  function updateResourceEggRespawns(now=performance.now()) {
    if(phase!=='prehistoric' || eggRespawnQueue.length===0) return;
    let respawned=0;
    for(let i=eggRespawnQueue.length-1;i>=0;i--) {
      const item=eggRespawnQueue[i];
      if(now<item.respawnAt) continue;
      // 시대가 바뀌어 이전 월드가 사라졌다면 해당 예약은 폐기한다.
      if(!item.parent || !item.parent.parent) {
        eggRespawnQueue.splice(i,1);
        continue;
      }
      addResourceEgg(item.parent,item.x,item.z,item.index);
      eggRespawnQueue.splice(i,1);
      respawned++;
    }
    if(respawned>0) {
      setSurvivalStatus(`🥚 깨졌던 알 ${respawned}개가 다시 나타났어요!`);
      checkInteractable();
    }
  }
  // 플레이어와 가까운 자원 알을 찾는다. 알은 E 키로만 깰 수 있다.
  function findNearbyResourceEgg(maxDistance=3.8) {
    let nearestEgg=null;
    let best=maxDistance;
    for(const egg of resourceEggs) {
      if(!egg || !egg.parent) continue;
      const p=new THREE.Vector3();
      egg.getWorldPosition(p);
      const distance=Math.hypot(p.x-player.position.x,p.z-player.position.z);
      if(distance<best) { best=distance; nearestEgg=egg; }
    }
    return nearestEgg;
  }
  function eatFood() {
    if(inventory.food<=0) { setSurvivalStatus('먹을 음식이 없어요. 알을 찾아보세요!'); return; }
    inventory.food--;
    const before=health;
    health=Math.min(100,health+24);
    updateStats(); updateInventoryUI();
    setSurvivalStatus(`음식을 먹었어요. 체력이 ${Math.round(health-before)} 회복됐어요!`);
  }
  function buildPlayerHouse() {
    if(inventory.wood<8 || inventory.stone<5) {
      setSurvivalStatus('집을 지으려면 나무 8개와 돌 5개가 필요해요.');
      return;
    }
    const x=Math.round(player.position.x/8)*8;
    const z=Math.round((player.position.z-8)/8)*8;
    // 플레이어 바로 위에 겹치지 않도록 앞쪽에 작은 집을 건설
    addHouse(worldGroup,x,z,1.05,0xb9a77f);
    inventory.wood-=8; inventory.stone-=5;
    builtHouses.push({x,z});
    refreshSolidMeshes();
    updateInventoryUI();
    setSurvivalStatus('🏠 집을 지었어요! 이제 안전한 거점을 만들 수 있어요.');
  }

  function buildPrehistoric() {
    inventory={food:0,wood:0,stone:0}; builtHouses=[];
    livingDinos=[]; resourceEggs=[]; combatTarget=null; playerShielding=false; shieldReadyAt=0; pulseReadyAt=0;
    if(shieldVisual) shieldVisual.visible=false;
    setVisible('combatPanel',false); setVisible('survivalPanel',false); setVisible('finalScreen',false); setVisible('deathActions',false);
    const era=eras[selectedEra], g=newWorld(era.ground,era.sky); scene.fog=new THREE.Fog(era.sky,42,230);
    // varied terrain with meadow patches, water river and sea
    for(let i=0;i<120;i++) {
      const x=(Math.random()-.5)*250,z=(Math.random()-.5)*250;
      if(Math.abs(x)<7 && z<25 && z>-70) continue;
      if(Math.random()<.7) addTree(g,x,z,.55+Math.random()*1.5,Math.random()<.35);
      else addBush(g,x,z,.7+Math.random()*1.4);
    }
    for(let i=0;i<55;i++) addRock(g,(Math.random()-.5)*180,(Math.random()-.5)*180,.5+Math.random()*1.5);
    // river bends through the valley
    const water=mat(0x3c9eb3,.24,.1);
    for(let i=0;i<12;i++) box(g, -28+Math.sin(i*.6)*9,.08,-75+i*12,8,.12,15,water,{rotationY:.1});
    // distant sea
    box(g,0,-.03,-155,340,.12,45,mat(0x247f9a,.28,.12));
    livingDinos=[];
    for(let i=0;i<20;i++) {
      const spec=era.dinos[Math.floor(Math.random()*era.dinos.length)];
      // 처음 몇 마리는 착지 지점에서 멀지 않은 곳에 배치해 전투를 바로 경험할 수 있게 한다.
      const startX=i===0 ? (Math.random()-.5)*7 : (i<5 ? (Math.random()-.5)*34 : (Math.random()-.5)*115);
      const startZ=i===0 ? -6-Math.random()*7 : (i<5 ? -4-Math.random()*23 : -25-Math.random()*135);
      const scale=.55+Math.random()*.6;
      const d=addDinosaur(g,spec,startX,startZ,scale);
      d.rotation.y=Math.random()*Math.PI*2;
      d.userData.wildAI={homeX:startX,homeZ:startZ,targetX:startX+(Math.random()-.5)*22,targetZ:startZ+(Math.random()-.5)*22,wait:Math.random()*4,grazing:false,phase:Math.random()*6.28};
      d.userData.combat=getDinoCombatProfile(spec);
      livingDinos.push(d);
      dinosaurGroup=dinosaurGroup||new THREE.Group();
    }
    // nest near player
    eggGroup=new THREE.Group(); eggGroup.position.set(0,0,-5); g.add(eggGroup);
    const nestMat=mat(0x72533a), eggMat=mat(0xcac2a0,.45);
    for(let i=0;i<18;i++) {
      const a=i*Math.PI*2/18, r=1.35;
      cylinder(eggGroup,Math.cos(a)*r,.2,Math.sin(a)*r,.12,.16,.55,nestMat,6).rotation.z=Math.cos(a)*.3;
    }
    const egg=new THREE.Mesh(new THREE.SphereGeometry(.85,32,24),eggMat);
    egg.scale.set(.78,1.12,.78); egg.position.set(0,1.05,0); egg.castShadow=true; eggGroup.add(egg);
    eggGroup.userData.egg=egg;
    for(let i=0;i<20;i++) addBush(g,(Math.random()-.5)*18,-8-Math.random()*20,.6);
    placeResourceEggs(g);
    player.position.set(0,1.7,7); yaw=0; pitch=0; updateCamera();
    phase='egg'; setVisible('hud',false); setVisible('help',false); setVisible('crosshair',false);
    setVisible('eggHint',true); setVisible('infoCard',false); setVisible('nextHint',false);
    camera.position.set(0,5.2,14); camera.lookAt(0,1,-5);
  }
  function buildHatchedDino(spec) {
    if(dinosaurGroup) scene.remove(dinosaurGroup);
    dinosaurGroup=new THREE.Group(); scene.add(dinosaurGroup);
    addDinosaur(dinosaurGroup,spec,0,0,1.0);
    dinosaurGroup.position.set(0,0,-5);
    if(eggGroup) { scene.remove(eggGroup); eggGroup=null; }
    camera.position.set(7,5.0,8); camera.lookAt(0,1.5,-5);
  }
  function buildAlienScene() {
    const g=newWorld(0x1b3527,0x071b20); scene.fog=new THREE.Fog(0x071b20,20,100);
    for(let i=0;i<20;i++) addTree(g,(Math.random()-.5)*60,(Math.random()-.5)*70,.8+Math.random(),true);
    alienGroup=new THREE.Group(); scene.add(alienGroup);
    const saucer=mat(0x9ca8a2,.25,.7), glow=mat(0x3dff9d,.2,.2), alienSkin=mat(0x4fbf69,.7);
    const disk=new THREE.Mesh(new THREE.SphereGeometry(4,32,16),saucer); disk.scale.y=.25; disk.position.set(0,15,-5); alienGroup.add(disk);
    cylinder(alienGroup,0,14.2,-5,2.3,2.3,.4,glow,24);
    const beam=new THREE.Mesh(new THREE.CylinderGeometry(1.4,4.8,12,24,1,true),new THREE.MeshBasicMaterial({color:0x35ff8b,transparent:true,opacity:.2,side:THREE.DoubleSide}));
    beam.position.set(0,8,-5); alienGroup.add(beam);
    for(let i=0;i<3;i++) {
      const x=(i-1)*2.0;
      sphere(alienGroup,x,14.1,-5,.65,alienSkin,.85,1.1,.7);
      sphere(alienGroup,x,14.85,-5,.8,alienSkin,.8,1,.7);
      for(const side of [-1,1]) sphere(alienGroup,x+side*.3,14.9,-5.55,.19,mat(0x08120e),1,.7,.5);
    }
    player.position.set(0,1.7,-5); yaw=0; pitch=0; updateCamera();
    phase='alien'; setVisible('alienText',true); setVisible('help',false); setVisible('crosshair',false);
  }
  function updateCamera() {
    if(!camera||!player) return;
    camera.position.copy(player.position);
    camera.rotation.order='YXZ'; camera.rotation.y=yaw; camera.rotation.x=pitch;
  }
  function refreshSolidMeshes() {
    solidMeshes=[];
    scene.updateMatrixWorld(true);
    scene.traverse(obj=>{ if(obj.isMesh && obj.userData.solid) solidMeshes.push(obj); });
  }
  function collidesAt(x,z) {
    const radius = player.radius || .35;
    const playerBottom = player.position.y - 1.65;
    const playerTop = player.position.y + .12;
    const probe = new THREE.Vector3(x, player.position.y, z);
    for(const obj of solidMeshes) {
      const b = new THREE.Box3().setFromObject(obj);
      if(b.max.y < playerBottom || b.min.y > playerTop) continue;
      if(probe.x + radius > b.min.x && probe.x - radius < b.max.x &&
         probe.z + radius > b.min.z && probe.z - radius < b.max.z) return true;
    }
    return false;
  }
  function movePlayer(dt) {
    if(!['village','city','school','schoolWarning','schoolChase','prehistoric','home'].includes(phase)) { $('runBtn').style.display='none'; return; }
    const canRun=['village','city','school','schoolWarning','schoolChase','prehistoric'].includes(phase);
    $('runBtn').style.display=canRun ? 'block' : 'none';
    $('runBtn').classList.toggle('active',runEnabled);
    $('runBtn').setAttribute('aria-pressed',runEnabled ? 'true' : 'false');
    $('runBtn').setAttribute('aria-label',runEnabled ? '달리기 끄기' : '달리기 켜기');
    if(jumpRequested && playerGrounded) { verticalVelocity=7.2; playerGrounded=false; }
    jumpRequested=false;
    if(!playerGrounded) {
      verticalVelocity-=18*dt;
      player.position.y+=verticalVelocity*dt;
      if(player.position.y<=1.7) { player.position.y=1.7; verticalVelocity=0; playerGrounded=true; }
    }
    const forward=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
    const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
    const dir=new THREE.Vector3();
    if(keys.w||keys.arrowup) dir.add(forward);
    if(keys.s||keys.arrowdown) dir.sub(forward);
    if(keys.d||keys.arrowright) dir.add(right);
    if(keys.a||keys.arrowleft) dir.sub(right);
    moving=dir.lengthSq()>0;
    if(moving) {
      dir.normalize();
      const outdoor=['village','city','school','prehistoric'].includes(phase);
      const speed=(outdoor && (keys.shift || runEnabled)) ? 11.5 : player.speed;
      const stepX = dir.x * speed * dt;
      const stepZ = dir.z * speed * dt;
      const nextX = player.position.x + stepX;
      if(!collidesAt(nextX, player.position.z)) player.position.x = nextX;
      const nextZ = player.position.z + stepZ;
      if(!collidesAt(player.position.x, nextZ)) player.position.z = nextZ;
      if(phase==='home') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-11,11);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-9.2,9.3);
      } else if(phase==='village' || phase==='schoolWarning' || phase==='schoolChase') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-70,70);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-110,18);
        // Entering the school playground automatically starts the encounter; no Space/E interaction.
        if(phase==='village' && !schoolEncounterStarted && player.position.z < -78 && Math.abs(player.position.x) < 18) {
          schoolEncounterStarted=true;
          startSchoolAlienWarning();
        }
      } else if(phase==='city') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-44,44);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-250,20);
      } else if(phase==='school') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-17,17);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-18,18);
      } else {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-150,150);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-180,150);
      }
    }
    updateCamera();
    checkInteractable();
    if(phase==='city' && !abductionTriggered && player.position.distanceTo(new THREE.Vector3(-22,1.7,-218))<7) {
      abductionTriggered=true;
      fadeToBlack(()=>startAlienSequence());
    }
  }
  function checkInteractable() {
    interactable=null;
    let nearest=3.0;
    for(const o of objects) {
      if(!o.parent) continue;
      const p=new THREE.Vector3(); o.getWorldPosition(p);
      const dist=p.distanceTo(player.position);
      if(dist<nearest) { nearest=dist; interactable=o; }
    }
    if(phase==='prehistoric') {
      const nearbyEgg=findNearbyResourceEgg();
      if(nearbyEgg) {
        interactable=nearbyEgg;
        interactable.userData.label='🥚 알 깨기 (E)';
      }
    }
    if(phase==='city' && player.position.distanceTo(new THREE.Vector3(-22,1.7,-218))<10) interactable={userData:{label:'운동장에 들어가기',trigger:'yard'}};
    if(phase==='school' && player.position.z>16) interactable={userData:{label:'운동장으로 나가기',trigger:'yard'}};
    if(phase==='home' && player.position.z>8.1 && Math.abs(player.position.x)<2.5) interactable={userData:{label:'나가기',trigger:'village'}};
    setVisible('centerPrompt',!!interactable);
    const eggNeedsEKey=phase==='prehistoric' && !!(interactable && interactable.userData.resourceEgg);
    $('interactBtn').disabled=eggNeedsEKey;
    if(interactable) $('interactBtn').textContent=interactable.userData.label||'상호작용';
    if(phase==='prehistoric') updateInventoryUI();
  }
  function interact() {
    if(phase==='prehistoric') {
      const nearbyEgg=findNearbyResourceEgg();
      if(nearbyEgg) { breakResourceEgg(nearbyEgg); return; }
    }
    if(!interactable) return;
    const trigger=interactable.userData.trigger;
    if(phase==='prehistoric' && interactable.userData.resourceEgg) {
      breakResourceEgg(interactable); return;
    }
    if(phase==='home') { buildVillage(); return; }
    if(phase==='city' && trigger==='yard') {
      // Entering the school playground triggers the alien abduction sequence.
      fadeToBlack(()=> { startAlienSequence(); });
      return;
    }
    if(phase==='city' && trigger==='school') { buildSchoolInterior(); return; }
    if(phase==='school' && trigger==='yard') {
      buildCity(); player.position.set(-22,1.7,-211); updateCamera(); checkInteractable(); return;
    }
  }
  let schoolAliens=[], schoolChaseStartedAt=0, schoolDragStartedAt=0;
  function startSchoolAlienWarning() {
    phase='schoolWarning'; schoolBlackoutAt=0; schoolAliens=[];
    setVisible('help',true); setVisible('crosshair',true); setVisible('centerPrompt',false);
    $('alienText').textContent='⚠️ 경고: 학교 안에 외계인이 접근하고 있습니다!';
    setVisible('alienText',true);
    // The warning remains visible for three seconds before the aliens appear.
    setTimeout(()=> {
      if(phase!=='schoolWarning') return;
      const alienMat=mat(0x35c96b), dark=mat(0x06150e), eye=mat(0xf4ffda);
      for(const x of [-3.2,3.2]) {
        const a=new THREE.Group();
        sphere(a,0,1.0,0,.42,alienMat,.72,1.05,.58);
        sphere(a,0,1.9,0,.58,alienMat,.82,1.05,.72);
        for(const ex of [-.22,.22]) sphere(a,ex,1.96,-.48,.13,dark,1,.8,.5);
        for(const ex of [-.22,.22]) sphere(a,ex,1.97,-.51,.055,eye,1,.8,.5);
        for(const side of [-1,1]) {
          const arm=new THREE.Mesh(new THREE.CylinderGeometry(.11,.14,.95,8),alienMat);
          arm.position.set(side*.48,1.05,-.02); arm.rotation.z=side*.45; a.add(arm);
          const leg=new THREE.Mesh(new THREE.CylinderGeometry(.13,.16,.8,8),alienMat);
          leg.position.set(side*.19,.38,.02); a.add(leg);
        }
        a.position.set(player.position.x+x,0,player.position.z-9); a.userData.startX=x; scene.add(a); schoolAliens.push(a);
      }
      phase='schoolChase'; schoolChaseStartedAt=performance.now();
      $('alienText').textContent='👽👽 외계인 두 명이 갑자기 나타나 달려온다!';
    },3000);
  }
  function startAlienSequence() {
    abductionTriggered=true;
    alienLiftComplete=false; alienFlyStartedAt=0;
    buildAlienScene();
    $('alienText').textContent='🛸 초록빛이 몸을 감싼다...';
    setTimeout(()=> {
      $('alienText').textContent='👽 외계인: 우주선으로 올라가는 중...';
    },1800);
    setTimeout(()=> {
      $('alienText').textContent='🛸 우주선 내부로 이동 중...';
    },3500);
    // The departure transition is handled after the saucer flies away in animate().
  }
  function buildFallingHuman() {
    if(fallingAvatar) scene.remove(fallingAvatar);
    const avatar=new THREE.Group();
    const skin=mat(0xd9a47d), shirt=mat(0x2e75a8), pants=mat(0x26374b), shoes=mat(0x242424), hair=mat(0x30251f);
    // Human-shaped third-person avatar: head, neck, torso, articulated arms and legs.
    const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.28, .58, 4, 8), shirt);
    torso.position.y=1.12; avatar.add(torso);
    const neck=new THREE.Mesh(new THREE.CylinderGeometry(.105,.12,.16,10),skin); neck.position.y=1.53; avatar.add(neck);
    const head=new THREE.Mesh(new THREE.SphereGeometry(.22,16,12),skin); head.position.y=1.78; head.scale.set(.88,1.08,.92); avatar.add(head);
    const hairCap=new THREE.Mesh(new THREE.SphereGeometry(.225,16,10,0,Math.PI*2,0,Math.PI*.55),hair); hairCap.position.set(0,1.86,-.015); avatar.add(hairCap);
    const face=new THREE.Mesh(new THREE.BoxGeometry(.15,.045,.025),mat(0x382b25)); face.position.set(0,1.78,-.202); avatar.add(face);
    const armPivots=[], legPivots=[];
    for(const side of [-1,1]) {
      const arm=new THREE.Group(); arm.position.set(side*.36,1.36,0); avatar.add(arm); armPivots.push(arm);
      const upper=new THREE.Mesh(new THREE.CapsuleGeometry(.09,.34,4,8),shirt); upper.position.y=-.22; arm.add(upper);
      const fore=new THREE.Mesh(new THREE.CapsuleGeometry(.073,.28,4,8),skin); fore.position.set(0,-.53,-.015); arm.add(fore);
      const hand=new THREE.Mesh(new THREE.SphereGeometry(.085,10,8),skin); hand.position.set(0,-.72,-.02); arm.add(hand);
      const leg=new THREE.Group(); leg.position.set(side*.16,.83,0); avatar.add(leg); legPivots.push(leg);
      const thigh=new THREE.Mesh(new THREE.CapsuleGeometry(.115,.34,4,8),pants); thigh.position.y=-.22; leg.add(thigh);
      const shin=new THREE.Mesh(new THREE.CapsuleGeometry(.085,.34,4,8),pants); shin.position.set(0,-.55,-.015); leg.add(shin);
      const shoe=new THREE.Mesh(new THREE.BoxGeometry(.18,.12,.32),shoes); shoe.position.set(0,-.77,-.075); leg.add(shoe);
    }
    avatar.userData.armPivots=armPivots; avatar.userData.legPivots=legPivots;
    avatar.position.set(player.position.x,player.position.y-1.7,player.position.z);
    avatar.rotation.y=yaw; scene.add(avatar); fallingAvatar=avatar;
    return avatar;
  }
  function beginEraFall() {
    // Build the selected era first, then place the unchanged human avatar high above it.
    if(fallingAvatar) { scene.remove(fallingAvatar); fallingAvatar=null; }
    buildPrehistoric();
    phase='falling';
    player.position.set(0,62,18); yaw=Math.PI; pitch=0;
    buildFallingHuman();
    setVisible('hud',false); setVisible('help',false); setVisible('crosshair',false);
    setVisible('eggHint',false); setVisible('infoCard',false); setVisible('nextHint',false);
    setVisible('centerPrompt',false); setVisible('message',false);
    fallingStartedAt=performance.now();
    camera.position.set(0,66,27); camera.lookAt(0,60,18);
    $('fade').style.transition='opacity 1.1s';
    $('fade').style.opacity='0';
  }
  function buildEraScreen() {
    phase='era';
    setVisible('titleScreen',false); setVisible('eraScreen',true,'flex');
    setVisible('hud',false); setVisible('help',false); setVisible('crosshair',false);
    setVisible('alienText',false); setVisible('centerPrompt',false);
    if(renderer) renderer.domElement.style.display='none';
  }
  function chooseEra(era) {
    selectedEra=era;
    setVisible('eraScreen',false);
    setVisible('message',false);
    renderer.domElement.style.display='block';
    $('fade').style.transition='opacity .65s'; $('fade').style.opacity='1';
    setTimeout(()=> {
      setVisible('titleScreen',false); setVisible('eraScreen',false);
      beginEraFall();
    },650);
  }
  function hatchEgg() {
    if(phase!=='egg') return;
    phase='hatching'; setVisible('eggHint',false);
    hatchStart=performance.now();
    const egg=eggGroup?.userData.egg;
    let steps=0;
    const crackTimer=setInterval(()=>{
      steps++;
      if(egg) { egg.rotation.z=(Math.random()-.5)*.08*steps; egg.scale.x*=.97; egg.scale.y*=.98; }
      if(steps>=8) {
        clearInterval(crackTimer);
        const list=eras[selectedEra].dinos;
        const spec=list[Math.floor(Math.random()*list.length)];
        buildHatchedDino(spec);
        $('dinoName').textContent=spec.name;
        $('dinoFacts').innerHTML='<b>식성:</b> '+spec.diet+'<br><b>크기:</b> '+spec.size+
          '<br><b>특징:</b> '+spec.traits+'<br><b>주요 먹이:</b> '+spec.food+'<br><b>공격·방어:</b> '+spec.combat;
        setTimeout(()=> { setVisible('infoCard',true); infoShownAt=performance.now(); },1000);
        setTimeout(()=> { setVisible('nextHint',true); },5000);
        phase='hatched';
      }
    },170);
  }
  function enterPrehistoric() {
    setVisible('infoCard',false); setVisible('nextHint',false);
    fadeToBlack(()=> {
      // return to full free-roam prehistoric view; keep era and add a random nest in the distance
      buildPrehistoric();
      phase='prehistoric';
      setVisible('hud',true); setVisible('help',true); setVisible('crosshair',true);
      setVisible('survivalPanel',true); updateInventoryUI();
      setVisible('eggHint',false); setVisible('infoCard',false); setVisible('nextHint',false);
      camera.position.copy(player.position); updateCamera();
      health=100; attack=50+Math.random()*20; defense=50+Math.random()*20; updateStats();
    });
  }
  function updateStats() {
    for(const [name,val] of [['health',health],['attack',attack],['defense',defense]]) {
      $(name+'Pct').textContent=Math.round(val)+'%'; $(name+'Fill').style.width=val+'%';
    }
  }
  let alienLiftComplete=false, alienFlyStartedAt=0;
  function animate() {
    requestAnimationFrame(animate);
    const dt=Math.min(clock.getDelta(),.05);
    updateResourceEggRespawns();
    if(solidMeshes.length===0 && ['prehistoric','village','city','school','home'].includes(phase)) refreshSolidMeshes();
    if(phase==='prehistoric' || phase==='village' || phase==='city' || phase==='school' || phase==='schoolWarning' || phase==='schoolChase' || phase==='home') movePlayer(dt);
    if(phase==='prehistoric') {
      // gentle stat variation and environmental challenge
      if(performance.now()-lastDamage>8000) {
        lastDamage=performance.now();
        attack=THREE.MathUtils.clamp(attack+(Math.random()-.48)*1.0,25,100);
        defense=THREE.MathUtils.clamp(defense+(Math.random()-.52)*.8,25,100);
        updateStats();
      }
      // Wild dinosaurs roam independently, pause to graze/drink, then choose a new destination.
      acquireCombatTarget();
      for(const d of livingDinos) {
        const ai=d.userData.wildAI; if(!ai) continue;
        if(d===combatTarget) { ai.phase+=dt; continue; }
        const aiCombat=d.userData.combat;
        if(aiCombat && aiCombat.defeated) continue;
        ai.phase+=dt; ai.wait-=dt;
        if(ai.wait<=0) {
          if(!ai.grazing && d.userData.spec.diet==='초식' && Math.random()<.58) {
            ai.grazing=true; ai.wait=2.5+Math.random()*3.5;
          } else {
            ai.grazing=false;
            ai.targetX=ai.homeX+(Math.random()-.5)*30;
            ai.targetZ=ai.homeZ+(Math.random()-.5)*30;
            ai.wait=5+Math.random()*7;
          }
        }
        if(!ai.grazing) {
          const dx=ai.targetX-d.position.x, dz=ai.targetZ-d.position.z;
          const dist=Math.hypot(dx,dz);
          if(dist>.8) {
            const speed=d.userData.spec.diet==='육식'?1.35:.72;
            d.position.x+=(dx/dist)*speed*dt; d.position.z+=(dz/dist)*speed*dt;
            d.rotation.y=Math.atan2(-dx,-dz);
          } else { ai.wait=Math.min(ai.wait,.4); }
          d.rotation.z=Math.sin(ai.phase*5)*.018;
        } else {
          // A small repeated head/body dip represents feeding.
          d.rotation.x=Math.sin(ai.phase*4)*.045;
        }
      }
      updateCombatEncounter(dt);
    }
    if(phase==='hatching' && eggGroup) eggGroup.rotation.y+=dt*.3;
    if(phase==='schoolChase' || phase==='schoolDragged') {
      const elapsed=(performance.now()-schoolChaseStartedAt)/1000;
      for(const a of schoolAliens) {
        const targetX=player.position.x;
        const targetZ=player.position.z;
        const dx=targetX-a.position.x, dz=targetZ-a.position.z;
        const dist=Math.hypot(dx,dz)||1;
        if(phase==='schoolChase') {
          a.position.x += dx/dist*dt*12.8;
          a.position.z += dz/dist*dt*12.8;
          a.rotation.y=Math.atan2(-dx,-dz);
        } else {
          a.position.x=player.position.x+(a.userData.startX<0?-0.8:0.8);
          a.position.z=player.position.z+1.0;
        }
      }
      if(phase==='schoolChase' && (elapsed>0.6 && schoolAliens.some(a=>a.position.distanceTo(player.position)<1.8))) {
        phase='schoolDragged'; schoolDragStartedAt=performance.now();
        $('alienText').textContent='👽 외계인들이 사용자를 붙잡아 끌고 간다!';
      }
      if(phase==='schoolDragged') {
        // Pull the player down the corridor while the aliens stay close on both sides.
        player.position.z -= dt*2.8;
        player.position.x += (0-player.position.x)*dt*.8;
        updateCamera();
        if(performance.now()-schoolDragStartedAt>1900) {
          phase='schoolBlackout'; schoolBlackoutAt=performance.now();
          $('alienText').textContent=''; setVisible('alienText',false);
          $('fade').style.transition='opacity 1.2s'; $('fade').style.opacity='1';
          setVisible('message',true,'flex');
          $('messageMain').textContent=''; $('messageSub').textContent='';
          $('message').style.background='#000';
        }
      }
    }
    if(phase==='alien') {
      // Lift the player into the saucer, stop at cabin height, then fly away.
      if(!alienLiftComplete) {
        player.position.y=Math.min(12.0,player.position.y+dt*2.4);
        updateCamera();
        if(player.position.y>=12.0) {
          alienLiftComplete=true; alienFlyStartedAt=performance.now();
          $('alienText').textContent='🛸 우주선 내부에 도착했다!';
        }
      } else if(performance.now()-alienFlyStartedAt>900) {
        alienGroup.position.y += dt*1.2;
        alienGroup.position.z -= dt*5.0;
        player.position.z -= dt*5.0;
        updateCamera();
        if(performance.now()-alienFlyStartedAt>3600) {
          setVisible('message',true,'flex');
          $('messageMain').textContent='🛸 우주선이 하늘로 날아간다';
          $('messageSub').textContent='새로운 시대를 선택하세요';
          phase='alienDeparture';
          setTimeout(()=>fadeToBlack(()=>{setVisible('message',false);buildEraScreen();}),1800);
        }
      }
    }
    if(phase==='schoolBlackout' && schoolBlackoutAt && performance.now()-schoolBlackoutAt>=2000) {
      schoolBlackoutAt=0;
      setVisible('message',false);
      buildEraScreen();
      $('fade').style.transition='opacity 1.1s'; $('fade').style.opacity='0';
    }
    if(phase==='prehistoric' && shieldVisual) {
      shieldVisual.visible=playerShielding;
      if(playerShielding) shieldVisual.position.set(player.position.x,player.position.y,player.position.z);
    } else if(shieldVisual) shieldVisual.visible=false;
    updatePulseEffects(performance.now());
    if(phase==='ending') {
      const t=performance.now()/1000;
      celebrationDinos.forEach((d,i)=>{
        const phaseOffset=d.userData.wavePhase||0;
        d.userData.waveArms.forEach((arm,j)=>{
          const side=j===0?-1:1;
          arm.rotation.z=side*(.42+Math.sin(t*5.2+phaseOffset+j)*.52);
          arm.rotation.x=Math.sin(t*4.4+phaseOffset+j)*.28;
        });
        d.userData.waveLegs.forEach((leg,j)=>{ leg.rotation.x=Math.sin(t*2.8+phaseOffset+j*Math.PI)*.045; });
        d.rotation.y=Math.sin(t*1.5+i)*.06;
        d.position.y=Math.sin(t*3.2+phaseOffset)*.08;
      });
    }
    if(phase==='falling' && fallingAvatar) {
      player.position.y=Math.max(1.7,player.position.y-dt*13.5);
      fallingAvatar.position.set(player.position.x,player.position.y-1.7,player.position.z);
      fallingAvatar.rotation.y=yaw;
      const t=(performance.now()-fallingStartedAt)/1000;
      fallingAvatar.rotation.z=Math.sin(t*5)*.10;
      fallingAvatar.rotation.x=.12+Math.sin(t*4)*.07;
      fallingAvatar.userData.armPivots.forEach((arm,i)=>{ arm.rotation.x=Math.sin(t*7+i*Math.PI)*.65; arm.rotation.z=(i===0?-.18:.18); });
      fallingAvatar.userData.legPivots.forEach((leg,i)=>{ leg.rotation.x=Math.sin(t*7+i*Math.PI)*.48; });
      camera.position.set(player.position.x,player.position.y+3.2,player.position.z+8.5);
      camera.lookAt(fallingAvatar.position.x,fallingAvatar.position.y+1.0,fallingAvatar.position.z);
      if(player.position.y<=1.7) {
        player.position.y=1.7;
        if(fallingAvatar) { scene.remove(fallingAvatar); fallingAvatar=null; }
        phase='prehistoric'; yaw=0; pitch=0; updateCamera();
        setVisible('hud',true); setVisible('help',true); setVisible('crosshair',true);
        setVisible('survivalPanel',true); updateInventoryUI();
        setVisible('eggHint',false); setVisible('infoCard',false); setVisible('nextHint',false);
        health=100; attack=50+Math.random()*20; defense=50+Math.random()*20; updateStats();
        combatTarget=null; playerShielding=false; shieldReadyAt=0; pulseReadyAt=0;
        setVisible('combatPanel',true);
        $('help').textContent='WASD 이동 · 마우스 시점 · Space 점프 · E 알 깨기/상호작용 · Shift 달리기 · Q 방어 · F 에너지 파동';
        setSurvivalStatus('주변의 알 가까이 가서 E 키를 눌러 깨고 자원을 모아보세요!');
        setCombatNotice('공룡이 가까이 오면 전투가 시작돼요.',2600);
        refreshCombatPanel();
      }
    }
    if(renderer && renderer.domElement.style.display!=='none') renderer.render(scene,camera);
  }
  // Start / era controls
  $('startBtn').addEventListener('click',()=> {
    setVisible('titleScreen',false);
    renderer.domElement.style.display='block';
    buildHome();
    setVisible('help',true);
  });
  document.querySelectorAll('.era').forEach(b=>b.addEventListener('click',()=>chooseEra(b.dataset.era)));
  $('interactBtn').addEventListener('click',()=> {
    // 자원 알은 버튼 클릭이 아니라 E 키를 눌렀을 때만 깨진다.
    if(phase==='prehistoric' && findNearbyResourceEgg()) return;
    interact();
  });
  $('runBtn').addEventListener('click',e=>{
    e.preventDefault();
    e.stopPropagation();
    runEnabled=!runEnabled;
    $('runBtn').classList.toggle('active',runEnabled);
    $('runBtn').setAttribute('aria-pressed',runEnabled ? 'true' : 'false');
    $('runBtn').setAttribute('aria-label',runEnabled ? '달리기 끄기' : '달리기 켜기');
  });
  $('hatchBtn').addEventListener('click',hatchEgg);
  $('eatBtn').addEventListener('click',eatFood);
  $('buildBtn').addEventListener('click',buildPlayerHouse);
  $('nextBtn').addEventListener('click',enterPrehistoric);
  $('pulseBtn').addEventListener('click',fireEnergyPulse);
  $('shieldBtn').addEventListener('pointerdown',e=>{ e.preventDefault(); setPlayerShield(true); });
  ['pointerup','pointercancel','pointerleave'].forEach(type=>
    $('shieldBtn').addEventListener(type,()=>setPlayerShield(false))
  );
  $('retryBtn').addEventListener('click',()=>{
    if(phase!=='playerDown') return;
    setVisible('deathActions',false); setVisible('message',false);
    health=100; attack=50+Math.random()*20; defense=50+Math.random()*20; updateStats();
    $('fade').style.transition='opacity .45s'; $('fade').style.opacity='1';
    setTimeout(()=>beginEraFall(),450);
  });
  $('endBtn').addEventListener('click',()=>{
    if(phase!=='playerDown') return;
    buildCelebrationScene();
  });
  $('exitBtn').addEventListener('click',()=>{
    phase='exited';
    renderer.domElement.style.display='none';
    $('finalTitle').style.display='none'; $('finalSub').style.display='none'; $('exitBtn').style.display='none';
    $('exitNotice').style.display='flex';
    // 브라우저 보안 정책상 스크립트가 사용자가 직접 연 탭이 아닌 탭을 닫지 못할 수 있다.
    try { window.close(); } catch(_) {}
  });
  window.addEventListener('keydown',e=>{
    const k=e.key.toLowerCase(); keys[k]=true;
    if([' ','arrowup','arrowdown','arrowleft','arrowright'].includes(k)) e.preventDefault();
    if(k===' ' && !e.repeat && ['home','village','city','school','schoolWarning','schoolChase','prehistoric'].includes(phase)) {
      // 스페이스바는 항상 점프 전용이다.
      jumpRequested=true;
    }
    if(k==='q' && phase==='prehistoric') setPlayerShield(true);
    if(k==='f' && !e.repeat && phase==='prehistoric') fireEnergyPulse();
    if(k==='e' && !e.repeat) interact();
    if(k==='escape') document.exitPointerLock?.();
  });
  window.addEventListener('keyup',e=>{
    const k=e.key.toLowerCase(); keys[k]=false;
    if(k==='q') setPlayerShield(false);
  });
  function rendererPointerSetup() {
    // Canvas click locks the pointer for FPS look. Escape releases it.
    const canvas=renderer.domElement;
    canvas.addEventListener('click',()=> {
      if(['village','city','school','prehistoric','home'].includes(phase)) canvas.requestPointerLock?.();
    });
    document.addEventListener('pointerlockchange',()=> {
      pointerLocked=document.pointerLockElement===canvas;
      if(pointerLocked) setVisible('help',true);
    });
    document.addEventListener('mousemove',e=>{
      if(!pointerLocked || !['village','city','school','prehistoric','home'].includes(phase)) return;
      yaw-=e.movementX*.0022;
      pitch-=e.movementY*.0020;
      pitch=THREE.MathUtils.clamp(pitch,-1.45,1.45);
      updateCamera();
    });
    // 마우스 클릭 후 드래그로 시점 회전(포인터 잠금 미지원 환경용)
    canvas.addEventListener('mousedown',e=>{
      if(pointerLocked || !['village','city','school','prehistoric','home'].includes(phase)) return;
      mouseDown=true; lastMouseX=e.clientX; lastMouseY=e.clientY;
    });
    window.addEventListener('mouseup',()=>mouseDown=false);
    window.addEventListener('mousemove',e=>{
      if(pointerLocked || !mouseDown || !['village','city','school','prehistoric','home'].includes(phase)) return;
      yaw-=(e.clientX-lastMouseX)*.004;
      pitch-=(e.clientY-lastMouseY)*.003;
      pitch=THREE.MathUtils.clamp(pitch,-1.45,1.45);
      lastMouseX=e.clientX; lastMouseY=e.clientY; updateCamera();
    });
    // 모바일 터치 드래그
    canvas.addEventListener('touchstart',e=>{
      if(e.touches.length){lastMouseX=e.touches[0].clientX;lastMouseY=e.touches[0].clientY;}
    },{passive:true});
    canvas.addEventListener('touchmove',e=>{
      if(e.touches.length && ['village','city','school','prehistoric','home'].includes(phase)) {
        const t=e.touches[0]; yaw-=(t.clientX-lastMouseX)*.006; pitch-=(t.clientY-lastMouseY)*.006;
        pitch=THREE.MathUtils.clamp(pitch,-1.35,1.35); lastMouseX=t.clientX;lastMouseY=t.clientY;updateCamera();
      }
    },{passive:true});
    document.querySelectorAll('[data-key]').forEach(btn=>{
      const k=btn.dataset.key;
      btn.addEventListener('touchstart',e=>{e.preventDefault();keys[k]=true;},{passive:false});
      btn.addEventListener('touchend',e=>{e.preventDefault();keys[k]=false;},{passive:false});
      btn.addEventListener('mousedown',()=>keys[k]=true); btn.addEventListener('mouseup',()=>keys[k]=false);
    });
  }
  initThree();
  renderer.domElement.style.display='none';
  rendererPointerSetup();
})();
</script>
</body>
</html>
"""



# ==========================================
# 공룡 도감 페이지 (별도 페이지로 통합)
# ==========================================

# 페이지 이동은 파일 하단의 st.navigation이 기본 사이드바에 표시한다.

# ==========================================
# 2. 공룡 데이터
# ==========================================

DINOSAURS = {
    "트라이아스기": [
        "헤레라사우루스", "스타우리코사우루스", "에오랍토르",
        "코엘로피시스", "릴리엔스테르누스", "프로콤프소그나투스",
        "에우디모르포돈", "플라테오사우루스", "리오자사우루스",
        "무사우루스", "안키사우루스", "세라토사우루스",
        "타니스트로페우스", "노토사우루스", "쇼니사우루스",
        "믹소사우루스", "심보스폰딜루스", "프테로닥틸루스",
        "람포린쿠스", "프레온닥틸루스", "스카포그나투스",
        "포스토수쿠스", "리스트로사우루스"
    ],

    "쥐라기": [
        "알로사우루스", "케라토사우루스", "딜로포사우루스",
        "메갈로사우루스", "토르보사우루스", "마르쇼사우루스",
        "콤프소그나투스", "오르니톨레스테스", "신랍토르",
        "양추아노사우루스", "모노로포사우루스", "크리올로포사우루스",
        "아파토사우루스", "브라키오사우루스", "디플로도쿠스",
        "카마라사우루스", "바로사우루스", "슈노사우루스",
        "마멘키사우루스", "슈퍼사우루스", "세이스모사우루스",
        "케티오사우루스", "투리아사우루스", "스테고사우루스",
        "켄트로사우루스", "화양고사우루스", "미라가이아",
        "드라코펠타", "가고사우루스", "에우로펠타",
        "캄토사우루스", "드리오사우루스", "오스니엘리아",
        "헤테로돈토사우루스", "리코리누스", "아브릭토사우루스",
        "오트니엘로사우루스", "마르기노케팔리아"
    ],

    "백악기": [
        "스피노사우루스", "카르카로돈토사우루스", "티라노사우루스",
        "유티라누스", "딜롱", "알렉트로사우루스",
        "벨로키사우루스", "드로마이오사우루스", "데이노니쿠스",
        "오비랍토르", "테리지노사우루스", "오르니토미무스",
        "시노사우롭테릭스", "마시아카사우루스", "델타드로메우스",
        "노아사우루스", "기가노토사우루스", "수코미무스",
        "아마르가사우루스", "사우로포세이돈", "황허티탄",
        "후쿠이티탄", "에우헬로푸스", "펠로로사우루스",
        "아르젠티노사우루스", "파타고티탄", "우에르호사우루스",
        "파란토돈", "안타르크토펠타", "스테고우로스",
        "안킬로사우루스", "에드몬토니아", "이구아노돈",
        "우리노사우루스", "테논토사우루스", "무타부라사우루스",
        "레아엘리나사우라", "가스파리니사우라", "콴타사우루스",
        "아틀라스콥코사우루스", "에드몬토사우루스",
        "프시타코사우루스", "프로토케라톱스", "트리케라톱스",
        "아퀼롭스", "랴오케라톱스", "렙토케라톱스",
        "파키케팔로사우루스", "미크로파키케팔로사우루스",
        "스테노펠릭스"
    ]
}

# ==========================================
# 3. 공룡 분류 데이터
# ==========================================

CATEGORIES = {
    "수각류": [
        "헤레라사우루스", "스타우리코사우루스", "에오랍토르",
        "코엘로피시스", "릴리엔스테르누스", "프로콤프소그나투스",
        "세라토사우루스", "알로사우루스", "케라토사우루스",
        "딜로포사우루스", "메갈로사우루스", "토르보사우루스",
        "마르쇼사우루스", "콤프소그나투스", "오르니톨레스테스",
        "신랍토르", "양추아노사우루스", "모노로포사우루스",
        "크리올로포사우루스", "스피노사우루스",
        "카르카로돈토사우루스", "티라노사우루스", "유티라누스",
        "딜롱", "알렉트로사우루스", "벨로키사우루스",
        "드로마이오사우루스", "데이노니쿠스", "오비랍토르",
        "테리지노사우루스", "오르니토미무스", "시노사우롭테릭스",
        "마시아카사우루스", "델타드로메우스", "노아사우루스",
        "기가노토사우루스", "수코미무스"
    ],

    "용각류 및 근연 분류군": [
        "플라테오사우루스", "리오자사우루스", "무사우루스",
        "안키사우루스", "아파토사우루스", "브라키오사우루스",
        "디플로도쿠스", "카마라사우루스", "바로사우루스",
        "슈노사우루스", "마멘키사우루스", "슈퍼사우루스",
        "세이스모사우루스", "케티오사우루스", "투리아사우루스",
        "아마르가사우루스", "사우로포세이돈", "황허티탄",
        "후쿠이티탄", "에우헬로푸스", "펠로로사우루스",
        "아르젠티노사우루스", "파타고티탄"
    ],

    "검룡류": [
        "스테고사우루스", "켄트로사우루스",
        "화양고사우루스", "미라가이아",
        "우에르호사우루스", "파란토돈", "스테고우로스"
    ],

    "곡룡류": [
        "드라코펠타", "가고사우루스", "에우로펠타",
        "안타르크토펠타", "안킬로사우루스", "에드몬토니아"
    ],

    "조각류 및 기타 조반류": [
        "캄토사우루스", "드리오사우루스", "오스니엘리아",
        "헤테로돈토사우루스", "리코리누스",
        "아브릭토사우루스", "오트니엘로사우루스",
        "이구아노돈", "테논토사우루스", "무타부라사우루스",
        "레아엘리나사우라", "가스파리니사우라",
        "콴타사우루스", "아틀라스콥코사우루스",
        "에드몬토사우루스"
    ],

    "각룡류": [
        "프시타코사우루스", "프로토케라톱스",
        "트리케라톱스", "아퀼롭스",
        "랴오케라톱스", "렙토케라톱스"
    ],

    "후두류": [
        "파키케팔로사우루스",
        "미크로파키케팔로사우루스", "스테노펠릭스"
    ]
}

# 기타 선사시대 동물
OTHER_ANIMALS = {
    "익룡": [
        "에우디모르포돈", "프테로닥틸루스",
        "람포린쿠스", "프레온닥틸루스",
        "스카포그나투스"
    ],
    "해양 파충류": [
        "타니스트로페우스", "노토사우루스",
        "쇼니사우루스", "믹소사우루스",
        "심보스폰딜루스"
    ],
    "기타 고대 동물": [
        "포스토수쿠스", "리스트로사우루스"
    ]
}

# ==========================================
# 4. 이미지 가져오기
# ==========================================

@st.cache_data(ttl=86400, show_spinner=False)
def get_dinosaur_image(name):
    try:
        query = urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": name,
            "gsrnamespace": 0,
            "gsrlimit": 1,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 700
        })

        url = "https://ko.wikipedia.org/w/api.php?" + query

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "DinosaurDictionary/1.0"}
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            return page.get("thumbnail", {}).get("source")

    except Exception:
        return None

    return None

# ==========================================
# 5. 디자인
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #101a17;
    color: #f3f5ee;
}

h1, h2, h3, p, label {
    color: #f3f5ee;
}

.dino-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    margin-top: 25px;
    color: #b7e4c7;
}

.dino-subtitle {
    text-align: center;
    color: #c1cec3;
    font-size: 17px;
    margin-bottom: 35px;
}

.dino-card {
    background: #20332b;
    border: 1px solid #456653;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
}

.dino-card h3 {
    color: #d4f2dc;
}

div.stButton > button {
    border-radius: 12px;
    border: 1px solid #719b7d;
    background-color: #294638;
    color: white;
    font-weight: bold;
    min-height: 48px;
}

div.stButton > button:hover {
    background-color: #477858;
    color: white;
    border-color: #b7e4c7;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 세부 정보 생성
# ==========================================

def get_category(name):
    for category, animals in CATEGORIES.items():
        if name in animals:
            return category

    for category, animals in OTHER_ANIMALS.items():
        if name in animals:
            return category

    if name == "마르기노케팔리아":
        return "조반류의 분류군"

    return "분류 확인 필요"


def get_food(name):
    if name in OTHER_ANIMALS.get("익룡", []):
        return "동물성 먹이를 먹었음"
    if name in OTHER_ANIMALS.get("해양 파충류", []):
        return "주로 물속의 동물을 먹었음"
    if name in OTHER_ANIMALS.get("기타 고대 동물", []):
        return "종에 따라 식성이 다름"

    category = get_category(name)

    if category == "수각류":
        if name in ["오비랍토르", "테리지노사우루스",
                    "오르니토미무스"]:
            return "잡식성 또는 식물성 먹이 섭취 가능성"
        return "육식성"

    if category in [
        "용각류 및 근연 분류군", "검룡류", "곡룡류",
        "조각류 및 기타 조반류", "각룡류", "후두류"
    ]:
        return "초식성"

    return "확인 필요"


def get_era_note(name, era):
    if name == "세라토사우루스":
        return "실제 생존 시기는 쥐라기입니다. 원래 보내준 목록의 트라이아스기 항목에 표시되어 있습니다."
    if name == "프테로닥틸루스":
        return "실제 생존 시기는 쥐라기 후기입니다."
    if name == "람포린쿠스":
        return "실제 생존 시기는 쥐라기 후기입니다."
    if name == "마르기노케팔리아":
        return "개별 공룡 속명이 아니라 각룡류와 후두류 등을 포함하는 분류군의 이름입니다."
    if name in OTHER_ANIMALS.get("익룡", []):
        return "공룡이 아닌 익룡입니다."
    if name in OTHER_ANIMALS.get("해양 파충류", []):
        return "공룡이 아닌 해양 파충류입니다."
    if name in OTHER_ANIMALS.get("기타 고대 동물", []):
        return "공룡이 아닌 다른 고대 파충류 또는 단궁류입니다."
    return "정확한 생존 시기는 종별 화석 기록에 따라 확인해야 합니다."


# ==========================================
# 7. 페이지 상태
# ==========================================

if "selected_era" not in st.session_state:
    st.session_state.selected_era = None

if "selected_dinosaur" not in st.session_state:
    st.session_state.selected_dinosaur = None


# ==========================================
# 8. 첫 화면
# ==========================================

def show_home():

    st.markdown(
        '<div class="dino-title">🦖 공룡 도감</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dino-subtitle">'
        '공룡들이 살았던 세상으로 떠나 보세요!'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # 세 시대 버튼을 화면 중앙에 일렬로 배치
    left, col1, col2, col3, right = st.columns(
        [1, 2, 2, 2, 1]
    )

    eras = [
        ("트라이아스기", "🦕", "약 2억 5200만~2억 100만 년 전"),
        ("쥐라기", "🦖", "약 2억 100만~1억 4500만 년 전"),
        ("백악기", "🦕", "약 1억 4500만~6600만 년 전")
    ]

    for col, (era, emoji, period) in zip(
        [col1, col2, col3], eras
    ):
        with col:
            st.markdown(
                f"""
                <div class="dino-card">
                    <h2 style="text-align:center;">{emoji}</h2>
                    <h3 style="text-align:center;">{era}</h3>
                    <p style="text-align:center;font-size:12px;">
                        {period}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"{era} 탐험하기",
                key=f"era_{era}",
                use_container_width=True
            ):
                st.session_state.selected_era = era
                st.session_state.selected_dinosaur = None
                st.rerun()

    st.write("")
    st.markdown(
        "<h3 style='text-align:center;'>"
        "세 시대의 다양한 고대 생물들을 만나 보세요!"
        "</h3>",
        unsafe_allow_html=True
    )


# ==========================================
# 9. 시대별 공룡 목록
# ==========================================

def show_era(era):

    if st.button("← 시대 선택으로 돌아가기"):
        st.session_state.selected_era = None
        st.session_state.selected_dinosaur = None
        st.rerun()

    st.markdown(
        f'<div class="dino-title">🦖 {era} 도감</div>',
        unsafe_allow_html=True
    )

    dinosaurs = DINOSAURS[era]

    st.write(f"총 {len(dinosaurs)}종의 목록")

    search = st.text_input(
        "🔍 공룡 이름 검색",
        placeholder="예: 티라노사우루스, 알로사우루스"
    )

    category_options = [
        "전체",
        "수각류",
        "용각류 및 근연 분류군",
        "검룡류",
        "곡룡류",
        "조각류 및 기타 조반류",
        "각룡류",
        "후두류",
        "익룡",
        "해양 파충류",
        "기타 고대 동물",
        "조반류의 분류군",
        "분류 확인 필요"
    ]

    selected_category = st.selectbox(
        "공룡 종류별 분류",
        category_options
    )

    filtered = []

    for name in dinosaurs:
        if search and search not in name:
            continue

        category = get_category(name)

        if selected_category != "전체":
            if category != selected_category:
                continue

        filtered.append(name)

    st.write(f"검색 결과: {len(filtered)}종")

    if not filtered:
        st.info("검색 결과가 없습니다.")
        return

    # 두 열로 공룡 카드 표시
    for i in range(0, len(filtered), 2):

        cols = st.columns(2)

        for j in range(2):
            if i + j >= len(filtered):
                break

            name = filtered[i + j]
            category = get_category(name)
            food = get_food(name)

            with cols[j]:
                st.markdown(
                    f"""
                    <div class="dino-card">
                        <h3>{name}</h3>
                        <p>분류: {category}</p>
                        <p>식성: {food}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    f"{name} 자세히 보기",
                    key=f"detail_{era}_{name}",
                    use_container_width=True
                ):
                    st.session_state.selected_dinosaur = name
                    st.rerun()


# ==========================================
# 10. 공룡 상세 도감
# ==========================================

def show_detail(name, era):

    if st.button("← 공룡 목록으로 돌아가기"):
        st.session_state.selected_dinosaur = None
        st.rerun()

    st.title(f"🦖 {name}")

    category = get_category(name)
    food = get_food(name)

    image_url = get_dinosaur_image(name)

    if image_url:
        st.image(
            image_url,
            caption=f"{name}",
            use_container_width=True
        )
    else:
        st.info(
            "대표 이미지를 자동으로 불러오지 못했습니다. "
            "공룡 이름을 검색해 이미지를 확인해 주세요."
        )

    st.subheader("📖 기본 정보")

    info1, info2 = st.columns(2)

    with info1:
        st.markdown("**목록에 수록된 시대**")
        st.write(era)

        st.markdown("**분류**")
        st.write(category)

    with info2:
        st.markdown("**식성**")
        st.write(food)

        st.markdown("**생물 종류**")
        if name in OTHER_ANIMALS.get("익룡", []):
            st.write("익룡")
        elif name in OTHER_ANIMALS.get("해양 파충류", []):
            st.write("해양 파충류")
        elif name in OTHER_ANIMALS.get("기타 고대 동물", []):
            st.write("기타 고대 동물")
        else:
            st.write("공룡 또는 관련 분류군")

    st.divider()

    st.subheader("🔎 생물학적 특징")

    st.write(
        f"{name}은(는) {category}에 해당하는 "
        f"생물입니다. 식성은 {food}으로 분류됩니다."
    )

    st.subheader("⚠️ 시대 및 분류 참고")

    st.write(get_era_note(name, era))

    st.caption(
        "※ 도감의 분류와 식성은 기본적인 안내 정보입니다. "
        "정확한 크기, 생존 시기 및 생태 정보는 "
        "해당 종의 화석 연구 자료를 추가로 확인해야 합니다."
    )

    wiki_query = urllib.parse.quote(name)

    st.link_button(
        "📚 더 자세한 정보 검색하기",
        f"https://ko.wikipedia.org/wiki/{wiki_query}"
    )




def render_game_page():
    """공룡 생존 게임 화면."""
    components.html(GAME_HTML, height=1000, scrolling=False)


def render_dinosaur_dictionary_page():
    """사용자가 제공한 시대별 공룡 도감 화면."""
    # st.markdown()은 일부 실행 환경에서 <style> 태그를 제거하고
    # CSS 내용을 일반 글자로 표시할 수 있으므로, st.html()로 스타일을 삽입한다.
    # 숨겨진 표식이 있을 때만 아래 CSS가 적용되어 게임 페이지에는 영향이 없다.
    st.html(
        """
        <div class="dictionary-page-marker" style="display:none;"></div>
        <style>
          /* 도감 페이지에서만 세로 스크롤을 허용하고, 페이지 전체 배경을 어둡게 고정한다. */
          html:has(.dictionary-page-marker),
          body:has(.dictionary-page-marker) {
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;
            overflow-x: hidden !important;
            overflow-y: auto !important;
            background: #101a17 !important;
            color: #f3f5ee !important;
          }

          body:has(.dictionary-page-marker) [data-testid="stAppViewContainer"],
          body:has(.dictionary-page-marker) [data-testid="stApp"],
          body:has(.dictionary-page-marker) [data-testid="stMain"],
          body:has(.dictionary-page-marker) [data-testid="stMainBlockContainer"],
          body:has(.dictionary-page-marker) [data-testid="stAppViewBlockContainer"],
          body:has(.dictionary-page-marker) .block-container,
          body:has(.dictionary-page-marker) .stApp {
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;
            overflow-x: visible !important;
            overflow-y: visible !important;
            background-color: #101a17 !important;
            color: #f3f5ee !important;
          }

          /* 각 본문 영역에도 배경색을 직접 적용해 스크롤 아래쪽이 흰색으로 바뀌지 않게 한다. */
          body:has(.dictionary-page-marker) [data-testid="stMain"] > div,
          body:has(.dictionary-page-marker) [data-testid="stMainBlockContainer"] > div,
          body:has(.dictionary-page-marker) [data-testid="stAppViewBlockContainer"] > div,
          body:has(.dictionary-page-marker) .block-container > div {
            background-color: #101a17 !important;
            color: #f3f5ee !important;
          }

          /* 도감 내용은 어두운 배경에서 항상 읽을 수 있는 밝은 글자색으로 표시한다. */
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"],
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] p,
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] span,
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] li,
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] h1,
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] h2,
          body:has(.dictionary-page-marker) [data-testid="stMarkdownContainer"] h3,
          body:has(.dictionary-page-marker) label,
          body:has(.dictionary-page-marker) [data-testid="stCaptionContainer"],
          body:has(.dictionary-page-marker) [data-testid="stText"] {
            color: #f3f5ee !important;
          }

          body:has(.dictionary-page-marker) a {
            color: #9edbb5 !important;
          }

          body:has(.dictionary-page-marker) input,
          body:has(.dictionary-page-marker) textarea,
          body:has(.dictionary-page-marker) [data-baseweb="select"] > div {
            background-color: #20332b !important;
            color: #f3f5ee !important;
            border-color: #456653 !important;
          }

          body:has(.dictionary-page-marker) [data-testid="stMainBlockContainer"],
          body:has(.dictionary-page-marker) [data-testid="stAppViewBlockContainer"],
          body:has(.dictionary-page-marker) .block-container {
            padding-bottom: 48px !important;
          }
        </style>
        """
    )

    if "selected_era" not in st.session_state:
        st.session_state.selected_era = None
    if "selected_dinosaur" not in st.session_state:
        st.session_state.selected_dinosaur = None

    if st.session_state.selected_era is None:
        show_home()
    elif st.session_state.selected_dinosaur is not None:
        show_detail(
            st.session_state.selected_dinosaur,
            st.session_state.selected_era,
        )
    else:
        show_era(st.session_state.selected_era)


# 공식 멀티페이지 내비게이션을 사용하면 Streamlit이 페이지 선택 메뉴를
# 왼쪽 사이드바에 직접 표시한다. 별도의 radio로 페이지를 흉내 내지 않는다.
page = st.navigation(
    [
        st.Page(
            render_game_page,
            title="게임 페이지",
            icon="🎮",
            default=True,
        ),
        st.Page(
            render_dinosaur_dictionary_page,
            title="공룡 도감 페이지",
            icon="📚",
        ),
    ],
    position="sidebar",
)
page.run()
