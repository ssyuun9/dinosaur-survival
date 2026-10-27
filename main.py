import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="공룡 생존기",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome so the game can use almost the whole viewport.
st.markdown(
    """
    <style>
      html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
      [data-testid="stMainBlockContainer"] {
        margin: 0 !important; padding: 0 !important; width: 100% !important;
        max-width: 100% !important; overflow: hidden !important;
      }
      [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], footer { display: none !important; }
      iframe { display: block; border: 0 !important; }
      .block-container { padding: 0 !important; }
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
  #help { display:none; position:absolute; bottom:14px; left:50%; transform:translateX(-50%); width:max-content; max-width:92%;
    padding:9px 13px; border-radius:12px; background:#07120dc9; border:1px solid #ffffff35; font-size:13px; }
  #centerPrompt { position:absolute; left:50%; bottom:70px; transform:translateX(-50%); display:none; }
  #crosshair { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); color:#fff; opacity:.85; display:none;
    text-shadow:0 1px 5px #000; font-size:22px; pointer-events:none; }
  #infoCard { display:none; position:absolute; right:20px; top:50%; transform:translateY(-50%); width:min(310px,86vw);
    color:#fff; text-align:left; border:1px solid #d7e8be80; border-radius:18px; padding:18px;
    background:linear-gradient(145deg,#132b1ff2,#07130ff2); box-shadow:0 15px 40px #0009; }
  #infoCard h2 { margin:0 0 8px; font-size:25px; }
  #infoCard p { margin:7px 0; color:#e3efda; font-size:14px; line-height:1.45; }
  #eggHint { display:none; position:absolute; bottom:9%; left:50%; transform:translateX(-50%); }
  #nextHint { display:none; position:absolute; bottom:24px; right:24px; }
  #message { display:none; position:absolute; inset:0; align-items:center; justify-content:center; flex-direction:column;
    background:#000; z-index:15; font-size:clamp(24px,4vw,44px); font-weight:900; }
  #message p { font-size:18px; font-weight:500; color:#bfe5b4; }
  #alienText { display:none; position:absolute; left:50%; top:16%; transform:translateX(-50%); font-size:clamp(20px,4vw,36px);
    text-shadow:0 2px 12px #000; background:#001b19a8; border-radius:14px; padding:14px 22px; }
  #mobileControls { display:none; position:absolute; left:12px; bottom:55px; gap:10px; }
  .controlBtn { width:48px;height:48px;border-radius:14px;border:1px solid #fff8;background:#13271dbd;color:white;font-size:19px; }
  @media (pointer:coarse) { #mobileControls { display:flex; flex-wrap:wrap; width:165px; } #help { bottom:8px; } }
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
      <button class="era" data-era="triassic"><span class="footprint">🐾</span><span>트라이아스기</span><small>최초의 공룡 시대</small></button>
      <button class="era" data-era="jurassic"><span class="footprint">🐾</span><span>쥐라기</span><small>거대한 초식 공룡</small></button>
      <button class="era" data-era="cretaceous"><span class="footprint">🐾</span><span>백악기</span><small>다양한 공룡의 시대</small></button>
    </div>
  </div>
  <div id="hud">
    <div class="stat"><div class="statTop"><span>❤️ 체력</span><b id="healthPct">100%</b></div><div class="bar"><div id="healthFill" class="fill"></div></div></div>
    <div class="stat"><div class="statTop"><span>🦷 공격력</span><b id="attackPct">50%</b></div><div class="bar"><div id="attackFill" class="fill"></div></div></div>
    <div class="stat"><div class="statTop"><span>🛡️ 방어력</span><b id="defensePct">50%</b></div><div class="bar"><div id="defenseFill" class="fill"></div></div></div>
  </div>
  <div id="help">WASD 이동 · 마우스 시점 · Space 상호작용/시작 · Shift 달리기 · Esc 마우스 잠금 해제</div>
  <div id="crosshair">＋</div>
  <div id="centerPrompt"><button id="interactBtn" class="smallButton">상호작용</button></div>
  <div id="eggHint"><button id="hatchBtn" class="bigButton">🥚 부화하기</button></div>
  <div id="infoCard"><h2 id="dinoName">공룡</h2><p id="dinoFacts"></p></div>
  <div id="nextHint"><button id="nextBtn" class="bigButton">다음으로 ➜</button></div>
  <div id="message"><div id="messageMain">시간 이동 중...</div><p id="messageSub"></p></div>
  <div id="alienText">🛸 초록빛이 몸을 감싼다...</div>
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
      if(safe) addTree(g,tx,tz,.7+Math.random()*.5,j%2===0);
    }
    // road
    box(g,0,.015,-45,8,.05,120,mat(0x555954));
    for(let z=8;z>-110;z-=7) box(g,0,.05,z, .18,.03,3,mat(0xe9dfad));
    player.position.set(0,1.7,8); yaw=0; pitch=0; updateCamera();
    phase='village'; setVisible('hud',false); setVisible('help',true); setVisible('crosshair',true);
    addDoor(g,0,2,0,'마을로 나가기');
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
  function buildPrehistoric() {
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
    for(let i=0;i<16;i++) {
      const spec=era.dinos[Math.floor(Math.random()*era.dinos.length)];
      const d=addDinosaur(g,spec,(Math.random()-.5)*115,-25-Math.random()*135,.55+Math.random()*.6);
      d.rotation.y=Math.random()*Math.PI*2;
      dinosaurGroup=dinosaurGroup||new THREE.Group();
      // The dino meshes are already children of the world.
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
    if(!['village','city','school','prehistoric','home'].includes(phase)) return;
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
      const speed=keys.shift?10:player.speed;
      const stepX = dir.x * speed * dt;
      const stepZ = dir.z * speed * dt;
      const nextX = player.position.x + stepX;
      if(!collidesAt(nextX, player.position.z)) player.position.x = nextX;
      const nextZ = player.position.z + stepZ;
      if(!collidesAt(player.position.x, nextZ)) player.position.z = nextZ;
      if(phase==='home') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-11,11);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-9.2,9.3);
      } else if(phase==='village') {
        player.position.x=THREE.MathUtils.clamp(player.position.x,-70,70);
        player.position.z=THREE.MathUtils.clamp(player.position.z,-110,18);
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
    if(phase==='city' && player.position.distanceTo(new THREE.Vector3(-22,1.7,-218))<10) interactable={userData:{label:'운동장에 들어가기',trigger:'yard'}};
    if(phase==='school' && player.position.z>16) interactable={userData:{label:'운동장으로 나가기',trigger:'yard'}};
    if(phase==='home' && player.position.z>8.1 && Math.abs(player.position.x)<2.5) interactable={userData:{label:'나가기',trigger:'village'}};
    if(phase==='village' && player.position.z< -90) interactable={userData:{label:'도시로 이동하기',trigger:'city'}};
    setVisible('centerPrompt',!!interactable);
    if(interactable) $('interactBtn').textContent=interactable.userData.label||'상호작용';
  }
  function interact() {
    if(!interactable) return;
    const trigger=interactable.userData.trigger;
    if(phase==='home') { buildVillage(); return; }
    if(phase==='village') { buildCity(); return; }
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
    renderer.domElement.style.display='block';
    fadeToBlack(()=> {
      buildPrehistoric();
      setVisible('titleScreen',false);
      setVisible('eraScreen',false);
    });
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
    if(solidMeshes.length===0 && ['prehistoric','village','city','school','home'].includes(phase)) refreshSolidMeshes();
    if(phase==='prehistoric' || phase==='village' || phase==='city' || phase==='school' || phase==='home') movePlayer(dt);
    if(phase==='prehistoric') {
      // gentle stat variation and environmental challenge
      if(performance.now()-lastDamage>8000) {
        lastDamage=performance.now();
        if(Math.random()<.18) health=Math.max(20,health-2);
        attack=THREE.MathUtils.clamp(attack+(Math.random()-.48)*1.4,25,100);
        defense=THREE.MathUtils.clamp(defense+(Math.random()-.52)*1.1,25,100);
        updateStats();
      }
      if(dinosaurGroup) dinosaurGroup.rotation.y+=dt*.05;
    }
    if(phase==='hatching' && eggGroup) eggGroup.rotation.y+=dt*.3;
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
  $('interactBtn').addEventListener('click',interact);
  $('hatchBtn').addEventListener('click',hatchEgg);
  $('nextBtn').addEventListener('click',enterPrehistoric);
  window.addEventListener('keydown',e=>{
    const k=e.key.toLowerCase(); keys[k]=true;
    if([' ','arrowup','arrowdown','arrowleft','arrowright'].includes(k)) e.preventDefault();
    if(k===' ' && phase==='home' && !interactable) {
      // Space starts movement by requesting mouse lock; it is not required for WASD.
      renderer.domElement.requestPointerLock?.();
    } else if(k===' ' && interactable && ['home','village','city','school'].includes(phase)) interact();
    if(k==='e') interact();
    if(k==='escape') document.exitPointerLock?.();
  });
  window.addEventListener('keyup',e=>keys[e.key.toLowerCase()]=false);
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

components.html(GAME_HTML, height=1000, scrolling=False)
