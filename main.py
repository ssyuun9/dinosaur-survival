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
