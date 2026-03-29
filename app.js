
const stations = window.METRO_STATIONS || [];
const stationList = document.getElementById('stationList');
const counter = document.getElementById('counter');
const searchInput = document.getElementById('searchInput');
const filterButtons = document.querySelectorAll('.filter-btn');
const mapViewport = document.getElementById('mapViewport');
const mapScene = document.getElementById('mapScene');
const zoomInBtn = document.getElementById('zoomInBtn');
const zoomOutBtn = document.getElementById('zoomOutBtn');
const zoomResetBtn = document.getElementById('zoomResetBtn');
let currentLine = 'all';
let currentSearch = '';

function matchesFilters(station){const q=currentSearch.trim().toLowerCase();return (!q||station.name.toLowerCase().includes(q))&&(currentLine==='all'||station.line_id===currentLine)}
function renderPins(){}
function colorizePins(){}
function renderList(){if(!stationList)return;stationList.innerHTML='';const filtered=stations.filter(matchesFilters);if(counter)counter.textContent=filtered.length+' шт.';if(!filtered.length){stationList.innerHTML='<div class="station-item"><div class="station-item__meta"><div class="station-item__name">Ничего не найдено</div><div class="station-item__line">Попробуй другой запрос</div></div></div>';return}filtered.forEach((station)=>{const a=document.createElement('a');a.className='station-item';a.href=station.url;a.innerHTML=`<span class="station-item__dot" style="background:${station.color}"></span><span class="station-item__meta"><span class="station-item__name">${station.name}</span><span class="station-item__line">${station.line}</span></span>`;stationList.appendChild(a)})}
function rerender(){renderPins();renderList();document.querySelectorAll('.station-pin').forEach((pin)=>{const station=stations.find(s=>s.url===pin.getAttribute('href'));if(station){pin.style.setProperty('--pin-color', station.color);pin.style.setProperty('--dot-color', station.color);pin.style.setProperty('color', station.color);pin.style.setProperty('border-color', station.color);pin.style.setProperty('background', 'transparent');pin.style.setProperty('box-shadow', 'none');pin.style.setProperty('outline', 'none');pin.style.setProperty('opacity', '1');pin.style.setProperty('z-index', '5');pin.style.setProperty('position', 'absolute');pin.style.setProperty('text-decoration', 'none');pin.style.setProperty('cursor', 'pointer');pin.style.setProperty('display', matchesFilters(station)?'block':'none');pin.style.setProperty('--station-color', station.color);pin.style.setProperty('--fill', station.color);pin.style.setProperty('--stroke', '#fff');pin.style.setProperty('--ring', station.color);pin.style.setProperty('--size', station.is_transfer ? '20px' : '16px');
const beforeColor = station.color;
pin.style.background = 'transparent';
pin.style.border = '0';
pin.dataset.color = beforeColor;
}
});}
if(searchInput){searchInput.addEventListener('input',(e)=>{currentSearch=e.target.value||'';rerender()})}
filterButtons.forEach((btn)=>{btn.addEventListener('click',()=>{filterButtons.forEach((b)=>b.classList.remove('active'));btn.classList.add('active');currentLine=btn.dataset.line||'all';rerender()})});

(function(){
  if(!mapViewport || !mapScene || !mapContent) return;
  const state = {scale:1, minScale:1, maxScale:8, x:0, y:0, pointers:new Map(), dragStartX:0, dragStartY:0, startX:0, startY:0, pinchStartDistance:0, pinchStartScale:1, pinchWorldX:0, pinchWorldY:0};
  const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));
  const rect=()=>mapViewport.getBoundingClientRect();
  const sceneW=()=>mapContent.offsetWidth;
  const sceneH=()=>mapContent.offsetHeight;
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const center=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});

  function computeMinScale(){
    const fitX = mapViewport.clientWidth / sceneW();
    const fitY = mapViewport.clientHeight / sceneH();
    state.minScale = Math.min(fitX, fitY);
    if(!isFinite(state.minScale) || state.minScale <= 0) state.minScale = 1;
  }

  function clampPan(){
    const viewportW = mapViewport.clientWidth;
    const viewportH = mapViewport.clientHeight;
    const scaledW = sceneW() * state.scale;
    const scaledH = sceneH() * state.scale;
    const minX = scaledW <= viewportW ? (viewportW - scaledW) / 2 : viewportW - scaledW;
    const maxX = scaledW <= viewportW ? (viewportW - scaledW) / 2 : 0;
    const minY = scaledH <= viewportH ? (viewportH - scaledH) / 2 : viewportH - scaledH;
    const maxY = scaledH <= viewportH ? (viewportH - scaledH) / 2 : 0;
    state.x = clamp(state.x, minX, maxX);
    state.y = clamp(state.y, minY, maxY);
  }

  function applyTransform(){
    clampPan();
    mapContent.style.transform = `translate(${state.x}px, ${state.y}px) scale(${state.scale})`;
    if(zoomResetBtn) zoomResetBtn.textContent = Math.round((state.scale / state.minScale) * 100) + '%';
  }

  function zoomAt(clientX, clientY, nextScale){
    const r = rect();
    const localX = clientX - r.left;
    const localY = clientY - r.top;
    const worldX = (localX - state.x) / state.scale;
    const worldY = (localY - state.y) / state.scale;
    state.scale = clamp(nextScale, state.minScale * 0.35, state.maxScale);
    state.x = localX - worldX * state.scale;
    state.y = localY - worldY * state.scale;
    applyTransform();
  }

  function resetView(){
    computeMinScale();
    state.scale = state.minScale;
    state.x = (mapViewport.clientWidth - sceneW() * state.scale) / 2;
    state.y = (mapViewport.clientHeight - sceneH() * state.scale) / 2;
    applyTransform();
  }

  mapViewport.addEventListener('pointerdown', (e)=>{
    mapViewport.setPointerCapture(e.pointerId);
    state.pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
    if(state.pointers.size === 1){
      state.dragStartX = e.clientX; state.dragStartY = e.clientY; state.startX = state.x; state.startY = state.y;
    } else if(state.pointers.size === 2){
      const [p1,p2] = [...state.pointers.values()];
      const c = center(p1,p2);
      state.pinchStartDistance = distance(p1,p2);
      state.pinchStartScale = state.scale;
      const r = rect();
      state.pinchWorldX = (c.x - r.left - state.x) / state.scale;
      state.pinchWorldY = (c.y - r.top - state.y) / state.scale;
    }
    e.preventDefault();
  }, {passive:false});

  mapViewport.addEventListener('pointermove', (e)=>{
    if(!state.pointers.has(e.pointerId)) return;
    state.pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
    if(state.pointers.size === 1){
      state.x = state.startX + (e.clientX - state.dragStartX);
      state.y = state.startY + (e.clientY - state.dragStartY);
      applyTransform();
    } else if(state.pointers.size === 2){
      const [p1,p2] = [...state.pointers.values()];
      const c = center(p1,p2);
      const d = distance(p1,p2);
      state.scale = clamp(state.pinchStartScale * (d / Math.max(state.pinchStartDistance, 1)), state.minScale * 0.35, state.maxScale);
      const r = rect();
      state.x = (c.x - r.left) - state.pinchWorldX * state.scale;
      state.y = (c.y - r.top) - state.pinchWorldY * state.scale;
      applyTransform();
    }
    e.preventDefault();
  }, {passive:false});

  const release = (e)=>{ state.pointers.delete(e.pointerId); if(state.pointers.size === 1){ const p=[...state.pointers.values()][0]; state.dragStartX=p.x; state.dragStartY=p.y; state.startX=state.x; state.startY=state.y; } };
  mapViewport.addEventListener('pointerup', release);
  mapViewport.addEventListener('pointercancel', release);
  mapViewport.addEventListener('pointerleave', release);

  mapViewport.addEventListener('wheel', (e)=>{ e.preventDefault(); zoomAt(e.clientX, e.clientY, state.scale * (e.deltaY < 0 ? 1.12 : 0.88)); }, {passive:false});
  mapViewport.addEventListener('dblclick', (e)=>{ e.preventDefault(); zoomAt(e.clientX, e.clientY, state.scale * 1.3); });

  if(zoomInBtn) zoomInBtn.addEventListener('click', ()=>{ const r=rect(); zoomAt(r.left+r.width/2, r.top+r.height/2, state.scale*1.2); });
  if(zoomOutBtn) zoomOutBtn.addEventListener('click', ()=>{ const r=rect(); zoomAt(r.left+r.width/2, r.top+r.height/2, state.scale/1.2); });
  if(zoomResetBtn) zoomResetBtn.addEventListener('click', resetView);

  document.addEventListener('gesturestart', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('gesturechange', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('gestureend', (e)=>e.preventDefault(), {passive:false});
  document.addEventListener('touchmove', (e)=>{ if(e.touches && e.touches.length > 1) e.preventDefault(); }, {passive:false});

  window.addEventListener('resize', resetView);
  resetView();
})();

rerender();

