"""Standalone offline explorer (design B, chosen at check-in 4): one HTML file, plain JS + canvas, data inlined."""
from __future__ import annotations

import json
from pathlib import Path


def build_html(data: dict, path: Path) -> Path:
    payload = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", payload)
    path.write_text(html, encoding="utf-8")
    return path


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CLIP shortcut explorer</title>
<style>
:root{--land:#E69F00;--water:#0072B2;--err:#D55E00;--ok:#9A9A9A;--slate:#2F3E46;--bird:#009E73;--scene:#CC79A7;
--fg:#1d1d1f;--muted:#5f6368;--line:#dadce0;--bg:#ffffff;--panel:#f7f7f8;--accent:#0072B2}
*{box-sizing:border-box}
body{margin:0;font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--fg);background:var(--bg)}
header{padding:12px 16px 4px}
h1{font-size:18px;margin:0 0 2px}
.sub{color:var(--muted);font-size:12.5px}
#controls{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;padding:8px 16px;border-bottom:1px solid var(--line)}
#controls label{font-size:13px;color:var(--muted)}
select,input[type=text]{font:inherit;font-size:13px;padding:4px 6px;border:1px solid var(--line);border-radius:6px;background:#fff}
button{font:inherit;font-size:13px;padding:4px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer}
button:hover{background:var(--panel)}
.gchk{display:inline-flex;align-items:center;gap:4px;margin-right:6px;font-size:13px;color:var(--fg)}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:12px;padding:12px 16px}
#mapwrap{position:relative;border:1px solid var(--line);border-radius:10px;height:620px;overflow:hidden;background:#fff}
#map{width:100%;height:100%;display:block;cursor:crosshair}
#tip{position:absolute;pointer-events:none;background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px;font-size:12px;display:none;box-shadow:0 2px 8px rgba(0,0,0,.12);max-width:220px}
#tip img{width:88px;height:88px;image-rendering:auto;border-radius:4px;display:block;margin-bottom:4px}
#legend{position:absolute;left:10px;bottom:10px;background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font-size:12px}
#hint{position:absolute;right:10px;top:8px;font-size:11.5px;color:var(--muted);background:rgba(255,255,255,.85);padding:2px 6px;border-radius:6px}
aside{display:flex;flex-direction:column;gap:12px;min-width:0}
.panel{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--panel)}
.panel h2{font-size:14px;margin:0 0 6px}
.kpi{display:flex;gap:16px;margin-bottom:6px}
.kpi div{font-size:12px;color:var(--muted)}
.kpi b{display:block;font-size:20px;color:var(--fg);font-weight:600}
.bar{display:flex;align-items:center;gap:6px;font-size:12px;margin:2px 0}
.bar span.l{width:120px;color:var(--muted)}
.bar .t{flex:1;height:10px;background:#e9e9ec;border-radius:3px;overflow:hidden}
.bar .t i{display:block;height:100%}
#sptable{max-height:300px;overflow:auto;border-top:1px solid var(--line);margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:12px}
th{position:sticky;top:0;background:var(--panel);text-align:right;padding:4px 4px;cursor:pointer;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
td{text-align:right;padding:3px 4px;border-bottom:1px solid #eee}
tr.sel td{background:#e5f0f8}
tr:hover td{background:#f0f0f2;cursor:pointer}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px;vertical-align:0}
#card{margin:0 16px 16px;border:1px solid var(--line);border-radius:10px;padding:12px;min-height:120px}
#card h2{font-size:15px;margin:0 0 4px}
.meta{color:var(--muted);font-size:12.5px}
.strip{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.strip figure{margin:0;width:84px;text-align:center;font-size:11px;color:var(--muted)}
.strip img{width:84px;height:84px;border-radius:4px;border:3px solid #ccc;display:block}
.strip b{display:block;font-size:12px}
.curves{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px}
.reason{margin-top:6px;font-size:12.5px}
.reason em{color:var(--muted)}
.cl{font-size:12px;margin:4px 0;color:var(--fg)}
.cl b{color:var(--err)}
@media (max-width: 1000px){.grid{grid-template-columns:1fr}#mapwrap{height:480px}}
</style>
</head>
<body>
<header>
<h1>Cross-modal shortcut explorer: CLIP ViT-B/32 on Waterbirds</h1>
<div class="sub">All 5,794 test images (corrected labels). Map = UMAP of CLIP's 230 output logits (or of DINOv2-small image vectors). Black box only: outputs, never CLIP's internals. AI-aided pair, JKU AI and Visualization WS 2026.</div>
</header>
<div id="controls">
<label>Map <select id="proj"><option value="clip">CLIP outputs (230 logits)</option><option value="dino">DINOv2-small image vectors</option></select></label>
<label>Color <select id="color"><option value="margin">margin (right / wrong)</option><option value="group">class (landbird / waterbird)</option><option value="rating">AI water rating of the species</option><option value="size">bird size (mask area)</option><option value="cluster">cluster (k-means in 230-d)</option></select></label>
<span id="gboxes"></span>
<label class="gchk"><input type="checkbox" id="errOnly"> errors only</label>
<label class="gchk"><input type="checkbox" id="showCl" checked> cluster labels</label>
<label>Species <input type="text" id="search" list="splist" placeholder="Belted Kingfisher" size="22"><datalist id="splist"></datalist></label>
<button id="clear">Clear selection</button>
</div>
<div class="grid">
<section id="mapwrap"><canvas id="map"></canvas><div id="tip"></div><div id="legend"></div>
<div id="hint">drag = lasso · click = pick a bird · wheel = zoom · shift + drag = pan · double-click = reset view</div></section>
<aside>
<div class="panel" id="summary"></div>
<div class="panel"><h2>Species</h2><div class="meta">Click a row to select its images. Hover for the AI's one-line rating reason.</div>
<div id="sptable"></div></div>
<div class="panel" id="clusters"></div>
</aside>
</div>
<section id="card"><h2>Bird card</h2><div class="meta">Click a point on the map to see that image. Birds from the cue-conflict sample also show their edited versions and dose-response curves.</div></section>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const IM = D.images, N = IM.length, BIRDS = D.birds, SP = D.species;
const SPI = {}; SP.forEach(s => SPI[s.species] = s);
const GROUPS = ["landbird / land","landbird / water","waterbird / land","waterbird / water"];
const COL = {land:"#E69F00", water:"#0072B2", err:"#D55E00", ok:"#9A9A9A", slate:"#2F3E46", bird:"#009E73", scene:"#CC79A7"};
const GCOL = g => g.startsWith("land") ? COL.land : COL.water;
const GFILLED = g => g.endsWith("/ land");
const GSHAPE = {"landbird / land":"circle","landbird / water":"square","waterbird / land":"triangle","waterbird / water":"diamond"};
const CLPAL = ["#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC"];
const DISP = {}; SP.forEach(s => DISP[s.species] = s.display_name || s.species.replace(/_/g, " "));
const nice = sp => DISP[sp] || sp.replace(/_/g, " ");
const pct = (x, d=0) => (100*x).toFixed(d) + "%";
const S = {proj:"clip", color:"margin", groups:new Set(GROUPS), errOnly:false, showCl:true, sel:null, selLabel:"", selSpecies:null, picked:null,
           view:{k:1, tx:0, ty:0}, sort:{key:"err", dir:-1}};

// ---------- coordinates normalised to [0,1] per projection
function norm(xs, ys){
  let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
  for (let i=0;i<xs.length;i++){x0=Math.min(x0,xs[i]);x1=Math.max(x1,xs[i]);y0=Math.min(y0,ys[i]);y1=Math.max(y1,ys[i]);}
  const s = Math.max(x1-x0, y1-y0);
  return [xs.map(v => (v-x0)/s + (1-(x1-x0)/s)/2), ys.map(v => 1-((v-y0)/s + (1-(y1-y0)/s)/2))];
}
const P = {clip: norm(IM.map(d=>d.ux), IM.map(d=>d.uy)), dino: norm(IM.map(d=>d.dx), IM.map(d=>d.dy))};

// ---------- colours
function lerp(a,b,t){const pa=parseInt(a.slice(1),16), pb=parseInt(b.slice(1),16);
  const r=((pa>>16)&255)+(((pb>>16)&255)-((pa>>16)&255))*t, g=((pa>>8)&255)+(((pb>>8)&255)-((pa>>8)&255))*t, bl=(pa&255)+((pb&255)-(pa&255))*t;
  return "rgb("+Math.round(r)+","+Math.round(g)+","+Math.round(bl)+")";}
function marginColor(m){const t=Math.max(-6,Math.min(6,m))/6; return t<0 ? lerp("#F2F2F2",COL.err,-t) : lerp("#F2F2F2",COL.slate,t);}
const RATING = ["#E3E3E3","#9EC6E3","#4A90C4","#0B4F8A"];
function colorOf(d){
  switch(S.color){
    case "margin": return marginColor(d.margin);
    case "group": return GCOL(d.group);
    case "rating": return RATING[d.water_rating];
    case "size": return lerp("#E5F3EE", "#00573F", Math.min(1, d.mask_area/0.4));
    case "cluster": return CLPAL[d.cluster % 10];
  }
}

// ---------- canvas
const cv = document.getElementById("map"), ctx = cv.getContext("2d"), wrap = document.getElementById("mapwrap");
let W=0,H=0,DPR=1;
function resize(){DPR=window.devicePixelRatio||1; W=wrap.clientWidth; H=wrap.clientHeight; cv.width=W*DPR; cv.height=H*DPR; draw();}
const PAD = 24;
function sx(i){const v=P[S.proj][0][i]; return (PAD + v*(Math.min(W,H)-2*PAD) + (W-Math.min(W,H))/2)*S.view.k + S.view.tx;}
function sy(i){const v=P[S.proj][1][i]; return (PAD + v*(Math.min(W,H)-2*PAD) + (H-Math.min(W,H))/2)*S.view.k + S.view.ty;}
function visible(i){const d=IM[i]; return S.groups.has(d.group) && (!S.errOnly || d.correct===0);}
function shape(x,y,r,sh,fill,stroke,filled){
  ctx.beginPath();
  if (sh==="circle") ctx.arc(x,y,r,0,2*Math.PI);
  else if (sh==="square") ctx.rect(x-r*0.9,y-r*0.9,r*1.8,r*1.8);
  else if (sh==="triangle"){ctx.moveTo(x,y-r*1.15);ctx.lineTo(x+r*1.05,y+r*0.8);ctx.lineTo(x-r*1.05,y+r*0.8);ctx.closePath();}
  else {ctx.moveTo(x,y-r*1.2);ctx.lineTo(x+r*1.1,y);ctx.lineTo(x,y+r*1.2);ctx.lineTo(x-r*1.1,y);ctx.closePath();}
  if (filled){ctx.fillStyle=fill; ctx.fill(); ctx.strokeStyle=stroke; ctx.lineWidth=0.5; ctx.stroke();}
  else {ctx.strokeStyle=fill; ctx.lineWidth=1.4; ctx.stroke();}
}
let lasso = null;
function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0); ctx.clearRect(0,0,W,H);
  const r = 2.6*Math.sqrt(S.view.k);
  const hasSel = S.sel !== null;
  for (let pass=0; pass<2; pass++){
    for (let i=0;i<N;i++){
      if (!visible(i)) continue;
      const inSel = !hasSel || S.sel.has(i);
      if ((pass===0) === inSel && hasSel) continue;
      if (!hasSel && pass===1) continue;
      const d = IM[i];
      ctx.globalAlpha = inSel ? 0.9 : 0.12;
      const filled = S.color==="group" ? GFILLED(d.group) : true;
      shape(sx(i), sy(i), r, GSHAPE[d.group], colorOf(d), "rgba(0,0,0,.35)", filled);
    }
  }
  ctx.globalAlpha = 1;
  if (S.showCl && S.proj){
    ctx.font = "600 12px system-ui, sans-serif"; ctx.textAlign="center";
    D.clusters.forEach(c => {
      if (!c.error_cluster && S.color!=="cluster") return;
      const xs=[], ys=[]; for (let i=0;i<N;i++) if (IM[i].cluster===c.id){xs.push(sx(i)); ys.push(sy(i));}
      xs.sort((a,b)=>a-b); ys.sort((a,b)=>a-b);
      const x = xs[xs.length>>1], y = ys[ys.length>>1];
      const t = "C"+c.id+" · "+pct(c.err)+" wrong";
      const w = ctx.measureText(t).width + 10;
      ctx.fillStyle="rgba(255,255,255,.88)"; ctx.fillRect(x-w/2,y-9,w,18);
      ctx.strokeStyle = c.error_cluster ? COL.err : "#999"; ctx.lineWidth=1; ctx.strokeRect(x-w/2,y-9,w,18);
      ctx.fillStyle = c.error_cluster ? COL.err : "#444"; ctx.fillText(t, x, y+4);
    });
  }
  if (S.picked !== null && visible(S.picked)){
    ctx.beginPath(); ctx.arc(sx(S.picked), sy(S.picked), 9, 0, 2*Math.PI); ctx.strokeStyle="#000"; ctx.lineWidth=2; ctx.stroke();
  }
  if (lasso && lasso.length>1){
    ctx.beginPath(); ctx.moveTo(lasso[0][0],lasso[0][1]); lasso.forEach(p=>ctx.lineTo(p[0],p[1]));
    ctx.closePath(); ctx.fillStyle="rgba(0,114,178,.08)"; ctx.fill(); ctx.strokeStyle=COL.water; ctx.lineWidth=1.2; ctx.setLineDash([4,3]); ctx.stroke(); ctx.setLineDash([]);
  }
  legend();
}
function legend(){
  const el = document.getElementById("legend"); let h = "";
  if (S.color==="margin") h = '<div style="display:flex;align-items:center;gap:6px">wrong <span style="display:inline-block;width:110px;height:10px;background:linear-gradient(90deg,'+COL.err+',#F2F2F2,'+COL.slate+')"></span> right</div><div class="meta">margin −6 … +6</div>';
  else if (S.color==="group") h = '<span class="dot" style="background:'+COL.land+'"></span>landbird <span class="dot" style="background:'+COL.water+'"></span>waterbird<div class="meta">filled = land bg, open = water bg</div>';
  else if (S.color==="rating") h = RATING.map((c,i)=>'<span class="dot" style="background:'+c+'"></span>'+i).join(" ")+'<div class="meta">0 no water tie … 3 aquatic (AI-rated)</div>';
  else if (S.color==="size") h = '<div style="display:flex;align-items:center;gap:6px">small <span style="display:inline-block;width:90px;height:10px;background:linear-gradient(90deg,#E5F3EE,#00573F)"></span> large</div><div class="meta">bird mask area 0 … 40%+</div>';
  else h = CLPAL.map((c,i)=>'<span class="dot" style="background:'+c+'"></span>C'+i).join(" ");
  h += '<div class="meta" style="margin-top:3px">shape: ● LB/land ■ LB/water ▲ WB/land ◆ WB/water</div>';
  el.innerHTML = h;
}

// ---------- interaction
function nearest(mx,my,maxd){let best=-1,bd=maxd*maxd;
  for (let i=0;i<N;i++){ if(!visible(i)) continue; const dx=sx(i)-mx, dy=sy(i)-my, dd=dx*dx+dy*dy; if(dd<bd){bd=dd;best=i;} }
  return best;}
function inPoly(x,y,poly){let c=false; for(let i=0,j=poly.length-1;i<poly.length;j=i++){const xi=poly[i][0],yi=poly[i][1],xj=poly[j][0],yj=poly[j][1];
  if(((yi>y)!==(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi)) c=!c;} return c;}
let drag = null;
cv.addEventListener("mousedown", e => {
  const b = cv.getBoundingClientRect(), x=e.clientX-b.left, y=e.clientY-b.top;
  if (e.shiftKey || e.button===1){ drag={mode:"pan", x, y, tx:S.view.tx, ty:S.view.ty}; }
  else { drag={mode:"lasso", x, y}; lasso=[[x,y]]; }
});
window.addEventListener("mousemove", e => {
  const b = cv.getBoundingClientRect(), x=e.clientX-b.left, y=e.clientY-b.top;
  if (drag && drag.mode==="pan"){ S.view.tx = drag.tx + (x-drag.x); S.view.ty = drag.ty + (y-drag.y); draw(); return; }
  if (drag && drag.mode==="lasso"){ lasso.push([x,y]); draw(); return; }
  if (x<0||y<0||x>W||y>H){ tip.style.display="none"; return; }
  const i = nearest(x,y,8);
  if (i<0){ tip.style.display="none"; return; }
  const d = IM[i];
  tip.innerHTML = '<img src="'+d.img+'" alt=""><b>'+nice(d.species)+'</b><br>'+d.group+'<br>margin '+d.margin.toFixed(2)+(d.correct? '' : ' <b style="color:'+COL.err+'">wrong</b>')+'<br>water rating '+d.water_rating+' · C'+d.cluster;
  tip.style.display="block"; tip.style.left=Math.min(x+14, W-230)+"px"; tip.style.top=Math.min(y+14, H-170)+"px";
});
const tip = document.getElementById("tip");
window.addEventListener("mouseup", e => {
  if (!drag) return;
  const b = cv.getBoundingClientRect(), x=e.clientX-b.left, y=e.clientY-b.top;
  if (drag.mode==="lasso"){
    const moved = Math.hypot(x-drag.x, y-drag.y);
    if (lasso.length < 6 || moved < 4 && lasso.length < 12){
      const i = nearest(x,y,10); if (i>=0) pick(i);
    } else {
      const sel = new Set(); for (let i=0;i<N;i++) if (visible(i) && inPoly(sx(i),sy(i),lasso)) sel.add(i);
      setSel(sel.size ? sel : null, "lasso selection", null);
    }
    lasso = null;
  }
  drag = null; draw();
});
cv.addEventListener("wheel", e => {
  e.preventDefault(); const b=cv.getBoundingClientRect(), x=e.clientX-b.left, y=e.clientY-b.top;
  const f = Math.exp(-e.deltaY*0.0015), k = Math.max(0.5, Math.min(30, S.view.k*f)), r = k/S.view.k;
  S.view.tx = x - (x - S.view.tx)*r; S.view.ty = y - (y - S.view.ty)*r; S.view.k = k; draw();
}, {passive:false});
cv.addEventListener("dblclick", () => { S.view={k:1,tx:0,ty:0}; draw(); });

// ---------- controls
const gb = document.getElementById("gboxes");
GROUPS.forEach(g => { const l=document.createElement("label"); l.className="gchk";
  l.innerHTML='<input type="checkbox" checked> <span class="dot" style="background:'+(GFILLED(g)?GCOL(g):'#fff')+';border:1.5px solid '+GCOL(g)+'"></span>'+g;
  l.querySelector("input").addEventListener("change", ev => { ev.target.checked ? S.groups.add(g) : S.groups.delete(g); update(); });
  gb.appendChild(l); });
document.getElementById("proj").addEventListener("change", e => { S.proj=e.target.value; S.view={k:1,tx:0,ty:0}; draw(); });
document.getElementById("color").addEventListener("change", e => { S.color=e.target.value; draw(); });
document.getElementById("errOnly").addEventListener("change", e => { S.errOnly=e.target.checked; update(); });
document.getElementById("showCl").addEventListener("change", e => { S.showCl=e.target.checked; draw(); });
document.getElementById("clear").addEventListener("click", () => { setSel(null,"",null); });
const dl = document.getElementById("splist");
SP.forEach(s => { const o=document.createElement("option"); o.value=nice(s.species); dl.appendChild(o); });
document.getElementById("search").addEventListener("change", e => {
  const q = e.target.value.trim().toLowerCase(); if (!q) return;
  const s = SP.find(s => nice(s.species).toLowerCase()===q) || SP.find(s => nice(s.species).toLowerCase().includes(q));
  if (s) selectSpecies(s.species);
});
function selectSpecies(sp){
  const sel = new Set(); for (let i=0;i<N;i++) if (IM[i].species===sp) sel.add(i);
  setSel(sel, nice(sp), sp);
}
function setSel(sel, label, sp){ S.sel=sel; S.selLabel=label; S.selSpecies=sp; update(); }
function update(){ draw(); summary(); table(); }

// ---------- summary panel
function summary(){
  const ids = []; for (let i=0;i<N;i++) if (visible(i) && (S.sel===null || S.sel.has(i))) ids.push(i);
  const n = ids.length, e = ids.filter(i => IM[i].correct===0).length;
  const g = {}; GROUPS.forEach(x=>g[x]=0); ids.forEach(i=>g[IM[i].group]++);
  const sp = {}; ids.forEach(i => { const s=IM[i].species; sp[s]=sp[s]||[0,0]; sp[s][0]++; if(IM[i].correct===0) sp[s][1]++; });
  const top = Object.entries(sp).sort((a,b)=>b[1][0]-a[1][0]).slice(0,5);
  let h = '<h2>'+(S.sel===null ? "All visible images" : "Selection: "+S.selLabel)+'</h2>';
  h += '<div class="kpi"><div><b>'+n.toLocaleString()+'</b>images</div><div><b style="color:'+COL.err+'">'+(n? pct(e/n,1):"–")+'</b>wrong</div><div><b>'+pct(D.overall_error,1)+'</b>wrong overall</div></div>';
  GROUPS.forEach(x => { h += '<div class="bar"><span class="l">'+x+'</span><span class="t"><i style="width:'+(n? 100*g[x]/n:0)+'%;background:'+GCOL(x)+(GFILLED(x)?'':';opacity:.45')+'"></i></span><span>'+g[x]+'</span></div>'; });
  if (top.length) h += '<div class="meta" style="margin-top:6px">Top species: '+top.map(t => nice(t[0])+' ('+t[1][0]+', '+pct(t[1][1]/t[1][0])+' wrong)').join(', ')+'</div>';
  document.getElementById("summary").innerHTML = h;
}

// ---------- species table
const COLS = [["species","Species"],["label","Class"],["rating","Rating"],["n","n"],["err","Error"],["err_land","on land"],["err_water","on water"]];
function table(){
  const rows = SP.slice();
  const k = S.sort.key, dir = S.sort.dir;
  rows.sort((a,b) => { const va=a[k], vb=b[k]; if (typeof va==="string") return dir*va.localeCompare(vb); return dir*((va??-1)-(vb??-1)); });
  let h = '<table><thead><tr>'+COLS.map(c => '<th data-k="'+c[0]+'">'+c[1]+(S.sort.key===c[0]?(dir>0?" ▲":" ▼"):"")+'</th>').join("")+'</tr></thead><tbody>';
  rows.forEach(s => {
    const reason = (s.reason||"").replace(/"/g,"&quot;");
    h += '<tr data-sp="'+s.species+'" class="'+(S.selSpecies===s.species?"sel":"")+'" title="AI rating '+s.rating+': '+reason+'"><td><span class="dot" style="background:'+(s.label?COL.water:COL.land)+'"></span>'+nice(s.species)+'</td><td>'+(s.label?"WB":"LB")+'</td><td>'+s.rating+'</td><td>'+s.n+'</td><td>'+pct(s.err)+'</td><td>'+(s.err_land==null?"–":pct(s.err_land))+'</td><td>'+(s.err_water==null?"–":pct(s.err_water))+'</td></tr>';
  });
  h += '</tbody></table>';
  const el = document.getElementById("sptable"); const st = el.scrollTop; el.innerHTML = h; el.scrollTop = st;
  el.querySelectorAll("th").forEach(th => th.addEventListener("click", () => { const kk=th.dataset.k; S.sort = {key:kk, dir: S.sort.key===kk ? -S.sort.dir : (kk==="species"?1:-1)}; table(); }));
  el.querySelectorAll("tbody tr").forEach(tr => tr.addEventListener("click", () => selectSpecies(tr.dataset.sp)));
}

// ---------- clusters panel
(function(){
  let h = '<h2>Error clusters (k-means in 230-d output space)</h2><div class="meta">Clusters with more errors than their class × background mix predicts. Descriptions drafted by the AI; only parts that passed a data check (notebook section 5) are shown.</div>';
  D.clusters.filter(c=>c.error_cluster).sort((a,b)=>b.err-a.err).forEach(c => {
    h += '<div class="cl"><a href="#" data-c="'+c.id+'"><b>C'+c.id+'</b></a> '+pct(c.err)+' wrong (expected '+pct(c.expected)+' from its group mix), n='+c.n+': '+(c.description||'no supported description')+'</div>';
  });
  const el = document.getElementById("clusters"); el.innerHTML = h;
  el.querySelectorAll("a").forEach(a => a.addEventListener("click", ev => { ev.preventDefault(); const c=+a.dataset.c;
    const sel=new Set(); for (let i=0;i<N;i++) if (IM[i].cluster===c) sel.add(i); setSel(sel, "cluster C"+c, null); }));
})();

// ---------- bird card
const KEYLAB = {"original|None":"original","bird_only|None":"bird only","bg_only|None":"background only","paste_gray|0.5":"on gray, 0.5",
  "paste_match|0.5":"matching plate, 0.5","paste_conflict|1.0":"conflicting plate, 1.0","paste_conflict|0.5":"conflicting plate, 0.5",
  "paste_conflict|0.2":"conflicting plate, 0.2","text_misleading|0.08":"misleading word, 8%","text_neutral|0.08":"neutral word, 8%"};
function marginFor(b, key){
  const [c, a] = key.split("|"); const si = D.scales.indexOf(parseFloat(a)), ti = D.sizes.indexOf(parseFloat(a));
  if (c==="original") return b.orig; if (c==="bird_only") return b.bird; if (c==="bg_only") return b.bg;
  if (c.startsWith("paste")) return b[c][si];
  if (c==="text_misleading") return b.text_mis[ti]; if (c==="text_neutral") return b.text_neu[ti];
  return null;
}
function curve(title, xs, series, xlab, logx){
  const w=300, h=150, l=34, r=8, t=18, bt=28;
  const X = v => { const a = logx ? Math.log(v) : v, a0 = logx ? Math.log(Math.min(...xs)) : Math.min(...xs), a1 = logx ? Math.log(Math.max(...xs)) : Math.max(...xs); return l + (a-a0)/(a1-a0)*(w-l-r); };
  let lo = -2, hi = 2; series.forEach(s => s.v.forEach(v => { lo=Math.min(lo,v); hi=Math.max(hi,v); }));
  lo = Math.floor(lo); hi = Math.ceil(hi);
  const Y = v => t + (hi-v)/(hi-lo)*(h-t-bt);
  let svg = '<svg width="'+w+'" height="'+h+'" role="img" aria-label="'+title+'"><text x="'+l+'" y="12" font-size="12" font-weight="600">'+title+'</text>';
  svg += '<line x1="'+l+'" x2="'+(w-r)+'" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="#222" stroke-width="0.8"/>';
  [lo, 0, hi].forEach(v => svg += '<text x="'+(l-4)+'" y="'+(Y(v)+4)+'" font-size="10" text-anchor="end" fill="#666">'+v+'</text>');
  xs.forEach(v => svg += '<text x="'+X(v)+'" y="'+(h-bt+12)+'" font-size="9.5" text-anchor="middle" fill="#666">'+v+'</text>');
  svg += '<text x="'+((l+w-r)/2)+'" y="'+(h-3)+'" font-size="10" text-anchor="middle" fill="#666">'+xlab+'</text>';
  series.forEach(s => { svg += '<polyline fill="none" stroke="'+s.c+'" stroke-width="2" stroke-dasharray="'+(s.d||"")+'" points="'+s.v.map((v,i)=>X(xs[i])+","+Y(v)).join(" ")+'"/>'; });
  const labs = series.map(s => ({n:s.n, c:s.c, y:Y(s.v[s.v.length-1])-4})).sort((a,b)=>a.y-b.y);
  for (let i=1;i<labs.length;i++) if (labs[i].y - labs[i-1].y < 11) labs[i].y = labs[i-1].y + 11;
  labs.forEach(lb => svg += '<text x="'+(w-r)+'" y="'+lb.y+'" font-size="10" text-anchor="end" fill="'+lb.c+'">'+lb.n+'</text>');
  return svg + '</svg>';
}
function pick(i){
  S.picked = i; const d = IM[i], b = BIRDS[String(d.idx)], s = SPI[d.species];
  let h = '<h2>'+nice(d.species)+' <span class="meta">#'+d.idx+'</span></h2>';
  h += '<div class="meta">'+d.group+' · margin <b style="color:'+(d.correct?COL.slate:COL.err)+'">'+d.margin.toFixed(2)+(d.correct?" (right)":" (wrong)")+'</b> · cluster C'+d.cluster+' · bird area '+pct(d.mask_area)+'</div>';
  if (s) h += '<div class="reason">AI water rating <b>'+s.rating+'</b>: '+(s.reason||"")+' <em>(GenAI-derived, see section 2)</em></div>';
  if (!b){ h += '<div class="strip"><figure><img src="'+d.img+'" alt="" style="border-color:'+(d.correct?COL.ok:COL.err)+'"><b>'+d.margin.toFixed(2)+'</b>original</figure></div><div class="meta" style="margin-top:6px">Not in the cue-conflict sample (clean masks, 300 birds per group).</div>'; }
  else {
    if (b.thumbs){
      h += '<div class="strip">' + D.thumb_keys.map((k,j) => { const m = marginFor(b,k); return '<figure><img src="'+b.thumbs[j]+'" alt="" style="border-color:'+(m>0?COL.ok:COL.err)+'"><b style="color:'+(m>0?COL.slate:COL.err)+'">'+(m==null?"":m.toFixed(2))+'</b>'+KEYLAB[k]+'</figure>'; }).join("") + '</div>';
    } else h += '<div class="meta" style="margin-top:6px">In the experiment sample; thumbnails of the edited images are stored for 150 birds per group only.</div>';
    const cc = d.label ? COL.water : COL.land;
    const pm = (b.paste_match_all || b.paste_match), pc = (b.paste_conflict_all || b.paste_conflict);
    h += '<div class="curves">' + curve("margin vs. bird size (mean of 10 plates)", D.scales.slice().reverse(), [
        {n:"gray", v:b.paste_gray.slice().reverse(), c:"#222", d:"2,3"}, {n:"matching", v:pm.slice().reverse(), c:"#222", d:"7,4"},
        {n:"conflicting", v:pc.slice().reverse(), c:cc}], "bird scale", true)
      + curve("margin vs. text size (on original)", D.sizes.map(v=>Math.round(v*100)), [
        {n:"neutral", v:b.text_neu, c:"#222", d:"2,3"}, {n:"correct", v:b.text_cor, c:"#222", d:"7,4"}, {n:"misleading", v:b.text_mis, c:cc}], "cap height (% of image)", false)
      + '</div>';
  }
  document.getElementById("card").innerHTML = h; draw();
}
window.addEventListener("resize", resize);
window.__explorer = {pick: i => pick(i), selectSpecies, setSel, state: S};
resize(); update();
})();
</script>
</body>
</html>
"""
