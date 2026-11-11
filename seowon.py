import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D 입체 회로 시뮬레이터", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>3D Circuit Sandbox - Pro Update</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background-color: #1a1a1a; font-family: 'Segoe UI', sans-serif; user-select: none; touch-action: none; }
        #canvas-container { width: 100vw; height: 100vh; display: block; }
        
        #ui-layer { position: absolute; top: 10px; left: 10px; pointer-events: none; z-index: 10; width: 310px; }
        .panel { background: rgba(20, 20, 25, 0.9); color: #ddd; padding: 12px; border-radius: 10px; border: 1px solid #444; pointer-events: auto; backdrop-filter: blur(8px); }
        
        h1 { margin: 0 0 8px 0; font-size: 16px; color: #fff; }
        p { margin: 0 0 10px 0; font-size: 11px; color: #aaa; line-height: 1.3; }

        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        button { background: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; }
        button.active { background: #007bff; border-color: #0056b3; box-shadow: 0 0 10px rgba(0, 123, 255, 0.4); }
        
        .action-btn { width: 100%; padding: 10px; font-size: 13px; margin-top: 8px; background: #28a745; border: none; border-radius: 6px; color: white; cursor: pointer; }
        .reset-btn { background: #dc3545; margin-top: 6px; }
        .rotate-btn { background: #8844ff; margin-top: 6px; }

        #system-msg { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.85); color: #00ffcc; padding: 10px 20px; border-radius: 20px; font-size: 13px; display: none; z-index: 20; pointer-events: none;}

        #prop-panel { position: absolute; top: 10px; right: 10px; width: 220px; background: rgba(30, 30, 35, 0.95); color: #eee; padding: 15px; border-radius: 10px; border: 1px solid #555; z-index: 15; display: none; pointer-events: auto; font-size: 12px; }
        #prop-panel h3 { margin: 0 0 10px 0; color: #00ffcc; font-size: 14px; border-bottom: 1px solid #555; padding-bottom: 5px; }
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .stat-val { color: #ffcc00; font-weight: bold; }
        
        .led-setting { margin-top: 12px; border-top: 1px solid #555; padding-top: 10px; }
        .led-setting label { display: block; margin-bottom: 4px; color: #aaa; }
        .led-setting input[type="color"] { width: 100%; height: 28px; border: none; background: none; cursor: pointer; }
        .led-setting input[type="range"] { width: 100%; margin-bottom: 8px; }
        .led-setting select { width: 100%; padding: 5px; background: #222; color: white; border: 1px solid #555; border-radius: 4px; }
        .close-prop-btn { width: 100%; margin-top: 12px; background: #555; padding: 7px; border: none; color: white; border-radius: 5px; cursor: pointer; }
        
        #controls-info { font-size: 11px; color: #888; margin-top: 10px; background: #222; padding: 8px; border-radius: 6px; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui-layer">
        <div class="panel">
            <h1>🏢 3D 입체 회로 시뮬레이터</h1>
            <p>• 폐회로 완성 시 (+)에서 (-)로 입자가 흐릅니다.</p>
            
            <div class="btn-grid" id="toolbar">
                <button id="btn-select" onclick="setTool('select')">👆 선택/정보</button>
                <button id="btn-delete" onclick="setTool('delete')" style="background-color: #6a1a21;">🗑️ 삭제</button>
                <button id="btn-battery" class="active" onclick="setTool('battery')">🔋 배터리(9V)</button>
                <button id="btn-wire" onclick="setTool('wire')">〰️ 수평 전선</button>
                <button id="btn-vwire" onclick="setTool('vwire')">🪜 수직 도선</button>
                <button id="btn-led" onclick="setTool('led')">💡 커스텀 LED</button>
                <button id="btn-voltmeter" onclick="setTool('voltmeter')">📟 전압계 (V)</button>
                <button id="btn-ammeter" onclick="setTool('ammeter')">📊 전류계 (A)</button>
            </div>
            
            <button class="action-btn rotate-btn" onclick="rotatePreview()">🔄 부품 회전 (R 키)</button>
            <button class="action-btn" onclick="analyzeCircuit()">⚡ 회로 분석 & 작동 테스트</button>
            <button class="action-btn reset-btn" onclick="clearAll()">전체 초기화</button>
            
            <div id="controls-info">
                🖱️ <b>마우스 좌클릭</b>: 부품 배치 / 선택<br>
                🖱️ <b>마우스 우클릭</b>: 화면(카메라) 회전<br>
                🖱️ <b>마우스 휠(클릭)</b>: 화면 상하좌우 이동
            </div>
        </div>
    </div>

    <div id="prop-panel">
        <h3 id="prop-title">부품 정보</h3>
        <div class="stat-row"><span>위치 (X, Y, Z):</span> <span id="prop-pos" class="stat-val">0, 0, 0</span></div>
        
        <div id="prop-group-general">
            <div class="stat-row"><span>고유 저항 (R):</span> <span id="prop-r" class="stat-val">0 Ω</span></div>
            <div class="stat-row"><span>측정 전압 (V):</span> <span id="prop-v" class="stat-val">0 V</span></div>
            <div class="stat-row"><span>측정 전류 (I):</span> <span id="prop-i" class="stat-val">0 mA</span></div>
            <div class="stat-row"><span>소비 전력 (P):</span> <span id="prop-p" class="stat-val">0 mW</span></div>
        </div>
        
        <div id="prop-group-voltmeter" style="display:none;">
            <div class="stat-row"><span>측정 전압 (V):</span> <span id="prop-v-only" class="stat-val">0 V</span></div>
        </div>
        
        <div id="prop-group-ammeter" style="display:none;">
            <div class="stat-row"><span>측정 전류 (I):</span> <span id="prop-i-only" class="stat-val">0 mA</span></div>
        </div>
        
        <div id="led-controls" class="led-setting" style="display: none;">
            <label>🎨 LED 색상</label>
            <input type="color" id="led-color" oninput="updateLEDSettings()">
            <label style="margin-top:6px;">☀️ 밝기</label>
            <input type="range" id="led-brightness" min="0.2" max="5" step="0.1" value="2" oninput="updateLEDSettings()">
            <label>⚡ 깜빡임 패턴</label>
            <select id="led-blink" onchange="updateLEDSettings()">
                <option value="none">점등 (상시 켜짐)</option>
                <option value="fast">빠른 점멸</option>
                <option value="slow">느린 점멸</option>
            </select>
        </div>
        <button class="close-prop-btn" onclick="document.getElementById('prop-panel').style.display='none'">닫기</button>
    </div>
    
    <div id="system-msg">회로 분석 완료!</div>
    <div id="canvas-container"></div>

    <script>
        let currentTool = 'battery';
        let currentRotation = 0; // 0, 1, 2, 3 (x90 degrees)
        let blocks = {}; 
        let nextBlockId = 1;
        let previewMesh = null;
        let selectedBlock = null;
        let flowParticles = []; // 흐르는 전기 입자들

        const layerColors = [0xb87333, 0x00aaff, 0x00ffaa, 0xffaa00, 0xff0055, 0xaa00ff];
        function getWireColorByY(yIndex) { return layerColors[Math.min(yIndex, layerColors.length - 1)]; }

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        camera.position.set(0, 10, 15);
        controls.enableDamping = true;
        // 조작법 변경: 좌클릭 제한(Raycast용), 우클릭 회전, 휠클릭 이동
        controls.mouseButtons = {
            LEFT: null,
            MIDDLE: THREE.MOUSE.PAN,
            RIGHT: THREE.MOUSE.ROTATE
        };

        scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 10);
        dirLight.castShadow = true;
        scene.add(dirLight);

        const gridHelper = new THREE.GridHelper(20, 20, 0x555555, 0x222222);
        scene.add(gridHelper);
        const floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.MeshPhongMaterial({ color: 0x111111, depthWrite: false }));
        floorMesh.rotation.x = -Math.PI / 2;
        floorMesh.receiveShadow = true;
        scene.add(floorMesh);

        const materials = {
            batteryBody: new THREE.MeshPhongMaterial({ color: 0x333333 }),
            batteryPlus: new THREE.MeshPhongMaterial({ color: 0xff3333 }),  // +극 (빨강)
            batteryMinus: new THREE.MeshPhongMaterial({ color: 0x3355ff }), // -극 (파랑)
            plastic: new THREE.MeshPhongMaterial({ color: 0xcccccc }),
            vwire: new THREE.MeshPhongMaterial({ color: 0xffcc00 }),
            ledOff: new THREE.MeshStandardMaterial({ color: 0x444444, transparent: true, opacity: 0.8 }),
            voltmeter: new THREE.MeshPhongMaterial({ color: 0x115599 }),
            ammeter: new THREE.MeshPhongMaterial({ color: 0x995511 }),
            screen: new THREE.MeshBasicMaterial({ color: 0x002200 })
        };

        function createBlockMesh(type, yLayer = 0) {
            const group = new THREE.Group();
            if (type === 'battery') {
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.6, 1), materials.batteryBody);
                const plusSide = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 1), materials.batteryPlus);
                plusSide.position.x = 0.45; // Local +X direction is (+)
                const minusSide = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 1), materials.batteryMinus);
                minusSide.position.x = -0.45; // Local -X direction is (-)
                group.add(body, plusSide, minusSide);
            } else if (type === 'wire') {
                const wireMat = new THREE.MeshPhongMaterial({ color: getWireColorByY(yLayer) });
                group.add(new THREE.Mesh(new THREE.BoxGeometry(1, 0.2, 1), wireMat));
            } else if (type === 'vwire') {
                group.add(new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 1, 16), materials.vwire));
            } else if (type === 'led') {
                const base = new THREE.Mesh(new THREE.BoxGeometry(1, 0.2, 1), materials.plastic);
                const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.4, 16, 16), materials.ledOff.clone());
                bulb.position.y = 0.4;
                group.add(base, bulb);
                group.userData.bulb = bulb;
            } else if (type === 'voltmeter' || type === 'ammeter') {
                const bodyMat = (type === 'voltmeter') ? materials.voltmeter : materials.ammeter;
                const body = new THREE.Mesh(new THREE.BoxGeometry(1, 0.6, 1), bodyMat);
                const screen = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.1, 0.4), materials.screen);
                screen.position.set(0, 0.31, 0);
                group.add(body, screen);
            }
            return group;
        }

        window.setTool = function(tool) {
            currentTool = tool;
            document.querySelectorAll('#toolbar button').forEach(b => b.classList.remove('active'));
            document.getElementById(`btn-${tool}`).classList.add('active');
            if(previewMesh) { scene.remove(previewMesh); previewMesh = null; }
            if(tool !== 'select') document.getElementById('prop-panel').style.display = 'none';
        };

        window.rotatePreview = function() {
            currentRotation = (currentRotation + 1) % 4;
            if (previewMesh) {
                previewMesh.rotation.y = currentRotation * (Math.PI / 2);
            }
        };

        window.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') rotatePreview();
        });

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        renderer.domElement.addEventListener('pointermove', (event) => {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            if (['battery', 'wire', 'vwire', 'led', 'voltmeter', 'ammeter'].includes(currentTool)) {
                raycaster.setFromCamera(mouse, camera);
                const targets = [floorMesh, ...Object.values(blocks).map(b => b.mesh)];
                const intersects = raycaster.intersectObjects(targets, true);
                
                if (intersects.length > 0) {
                    const hit = intersects[0];
                    let pos = new THREE.Vector3();
                    
                    if (hit.object === floorMesh) {
                        pos.x = Math.floor(hit.point.x) + 0.5;
                        pos.y = 0.5;
                        pos.z = Math.floor(hit.point.z) + 0.5;
                    } else {
                        let obj = hit.object;
                        while(obj.parent && obj.parent !== scene) obj = obj.parent;
                        pos.copy(obj.position);
                        const normal = hit.face.normal;
                        pos.x += Math.round(normal.x);
                        pos.y += Math.round(normal.y);
                        pos.z += Math.round(normal.z);
                    }

                    const yLayer = Math.max(0, Math.round(pos.y - 0.5));

                    if (!previewMesh || previewMesh.userData.tool !== currentTool || previewMesh.userData.yLayer !== yLayer) {
                        if (previewMesh) scene.remove(previewMesh);
                        previewMesh = createBlockMesh(currentTool, yLayer);
                        previewMesh.userData.tool = currentTool;
                        previewMesh.userData.yLayer = yLayer;
                        previewMesh.traverse(c => { 
                            if(c.isMesh) { c.material = c.material.clone(); c.material.transparent = true; c.material.opacity = 0.5; } 
                        });
                        scene.add(previewMesh);
                    }
                    previewMesh.position.copy(pos);
                    previewMesh.rotation.y = currentRotation * (Math.PI / 2);
                }
            }
        });

        renderer.domElement.addEventListener('pointerdown', (event) => {
            if (event.pointerType === 'mouse' && event.button !== 0) return;
            if (event.clientX < 320 && event.clientY < 400) return; // UI 영역 클릭 무시
            
            raycaster.setFromCamera(mouse, camera);

            if (currentTool === 'select' || currentTool === 'delete') {
                const interactables = Object.values(blocks).map(b => b.mesh);
                const intersects = raycaster.intersectObjects(interactables, true);
                if (intersects.length > 0) {
                    let obj = intersects[0].object;
                    while(obj.parent && obj.parent !== scene) obj = obj.parent;
                    const key = Object.keys(blocks).find(k => blocks[k].mesh === obj);
                    
                    if (currentTool === 'delete') {
                        scene.remove(blocks[key].mesh);
                        delete blocks[key];
                        document.getElementById('prop-panel').style.display = 'none';
                        analyzeCircuit();
                    } else if (currentTool === 'select') {
                        openProperties(blocks[key]);
                    }
                }
            } else if (previewMesh) {
                const pos = previewMesh.position;
                const key = `${pos.x},${pos.y},${pos.z}`;
                
                if (!blocks[key]) {
                    const type = currentTool;
                    const yLayer = Math.max(0, Math.round(pos.y - 0.5));
                    
                    // 저항 설정
                    let resistance = 0.1; // 전선
                    if (type === 'led') resistance = 100;
                    if (type === 'battery') resistance = 1;
                    if (type === 'voltmeter') resistance = 100000; // 전압계는 전류를 안 뺏어가도록 높게 설정
                    if (type === 'ammeter') resistance = 0.01;     // 전류계는 저항이 없어야 함
                    
                    const block = { 
                        id: nextBlockId++, type: type, 
                        x: pos.x, y: pos.y, z: pos.z, yLayer: yLayer,
                        rot: currentRotation, // 회전값 저장
                        mesh: createBlockMesh(type, yLayer),
                        r: resistance, v: 0, i: 0, p: 0, flowOrder: -1,
                        isLit: false,
                        ledSettings: type === 'led' ? { color: '#ff0000', brightness: 2, blink: 'none' } : null
                    };
                    block.mesh.position.copy(pos);
                    block.mesh.rotation.y = currentRotation * (Math.PI / 2);
                    scene.add(block.mesh);
                    blocks[key] = block;
                    
                    scene.remove(previewMesh);
                    previewMesh = null;
                    analyzeCircuit();
                }
            }
        });

        function openProperties(block) {
            selectedBlock = block;
            const p = document.getElementById('prop-panel');
            p.style.display = 'block';
            
            let titles = { 'battery': '🔋 배터리', 'wire': '〰️ 수평 전선', 'vwire': '🪜 수직 도선', 'led': '💡 커스텀 LED', 'voltmeter': '📟 전압계', 'ammeter': '📊 전류계' };
            document.getElementById('prop-title').innerText = titles[block.type];
            document.getElementById('prop-pos').innerText = `${block.x}, ${block.y}, ${block.z}`;
            
            // UI 정리: 전압계/전류계에 따라 보여지는 정보 분리
            document.getElementById('prop-group-general').style.display = 'none';
            document.getElementById('prop-group-voltmeter').style.display = 'none';
            document.getElementById('prop-group-ammeter').style.display = 'none';

            if (block.type === 'voltmeter') {
                document.getElementById('prop-group-voltmeter').style.display = 'block';
                document.getElementById('prop-v-only').innerText = block.v.toFixed(2) + " V";
            } else if (block.type === 'ammeter') {
                document.getElementById('prop-group-ammeter').style.display = 'block';
                document.getElementById('prop-i-only').innerText = (block.i * 1000).toFixed(1) + " mA";
            } else {
                document.getElementById('prop-group-general').style.display = 'block';
                document.getElementById('prop-r').innerText = block.r + " Ω";
                document.getElementById('prop-v').innerText = block.v.toFixed(2) + " V";
                document.getElementById('prop-i').innerText = (block.i * 1000).toFixed(1) + " mA";
                document.getElementById('prop-p').innerText = (block.p * 1000).toFixed(1) + " mW";
            }
            
            const ledControls = document.getElementById('led-controls');
            if (block.type === 'led') {
                ledControls.style.display = 'block';
                document.getElementById('led-color').value = block.ledSettings.color;
                document.getElementById('led-brightness').value = block.ledSettings.brightness;
                document.getElementById('led-blink').value = block.ledSettings.blink;
            } else {
                ledControls.style.display = 'none';
            }
        }

        window.updateLEDSettings = function() {
            if (!selectedBlock || selectedBlock.type !== 'led') return;
            selectedBlock.ledSettings.color = document.getElementById('led-color').value;
            selectedBlock.ledSettings.brightness = parseFloat(document.getElementById('led-brightness').value);
            selectedBlock.ledSettings.blink = document.getElementById('led-blink').value;
            
            if(selectedBlock.isLit) {
                const m = selectedBlock.mesh.userData.bulb.material;
                m.color.set(selectedBlock.ledSettings.color);
                m.emissive.set(selectedBlock.ledSettings.color);
                m.emissiveIntensity = selectedBlock.ledSettings.brightness;
            }
        };

        window.clearAll = function() {
            Object.values(blocks).forEach(b => scene.remove(b.mesh));
            blocks = {};
            document.getElementById('prop-panel').style.display = 'none';
            analyzeCircuit();
        };

        function showMessage(msg, color) {
            const el = document.getElementById('system-msg');
            el.innerText = msg;
            el.style.color = color;
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 3000);
        }

        // 전기 흐름 이펙트 지우기
        function clearParticles() {
            flowParticles.forEach(p => scene.remove(p.mesh));
            flowParticles = [];
        }

        window.analyzeCircuit = function() {
            const blockList = Object.values(blocks);
            clearParticles();
            
            blockList.forEach(b => {
                b.v = 0; b.i = 0; b.p = 0; b.isLit = false; b.flowOrder = -1;
                if (b.type === 'led') {
                    b.mesh.userData.bulb.material.color.setHex(0x444444);
                    b.mesh.userData.bulb.material.emissive.setHex(0x000000);
                }
            });

            const batteries = blockList.filter(b => b.type === 'battery');
            if (batteries.length === 0) return;

            let adj = {};
            blockList.forEach(b => adj[b.id] = []);
            
            for(let i=0; i<blockList.length; i++) {
                for(let j=i+1; j<blockList.length; j++) {
                    const b1 = blockList[i]; 
                    const b2 = blockList[j];
                    const dx = Math.abs(b1.x - b2.x);
                    const dy = Math.abs(b1.y - b2.y);
                    const dz = Math.abs(b1.z - b2.z);
                    let canConnect = false;

                    if (dy === 0 && ((dx === 1 && dz === 0) || (dx === 0 && dz === 1))) canConnect = true;
                    else if (dx === 0 && dz === 0 && dy === 1) {
                        if (b1.type === 'vwire' || b2.type === 'vwire') canConnect = true;
                    }
                    if (canConnect) { adj[b1.id].push(b2.id); adj[b2.id].push(b1.id); }
                }
            }

            // 막힌 길(Dead-end) 커팅 알고리즘
            let changed = true;
            while(changed) {
                changed = false;
                for(let id in adj) {
                    let numId = parseInt(id);
                    let block = blockList.find(b => b.id === numId);
                    if (block.type !== 'battery' && adj[id].length <= 1) {
                        adj[id].forEach(neighborId => {
                            if(adj[neighborId]) adj[neighborId] = adj[neighborId].filter(n => n !== numId);
                        });
                        delete adj[id];
                        changed = true;
                    }
                }
            }

            let activeCount = 0;
            
            batteries.forEach(battery => {
                if(!adj[battery.id] || adj[battery.id].length === 0) return;

                // 극성 방향 및 거리 계산 (BFS from Plus to Minus)
                // 배터리의 +극 위치 판단 (로컬 +X 방향)
                let plusDir = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0,1,0), battery.rot * Math.PI/2);
                plusDir.x = Math.round(plusDir.x);
                plusDir.z = Math.round(plusDir.z);
                
                let expectedPlusX = battery.x + plusDir.x;
                let expectedPlusZ = battery.z + plusDir.z;

                let startNode = null;
                adj[battery.id].forEach(neighborId => {
                    let nBlock = blockList.find(b => b.id === neighborId);
                    if(nBlock.x === expectedPlusX && nBlock.z === expectedPlusZ && nBlock.y === battery.y) {
                        startNode = nBlock.id;
                    }
                });

                // 만약 +극에 도선이 연결되지 않았다면 전기가 흐르지 않음!
                if (!startNode) return; 

                // 거리 계산 (전기 입자 애니메이션을 위함)
                let distances = {};
                let queue = [startNode];
                distances[startNode] = 0;
                
                while(queue.length > 0) {
                    let curr = queue.shift();
                    if(adj[curr]) {
                        adj[curr].forEach(neighbor => {
                            if(neighbor !== battery.id && distances[neighbor] === undefined) {
                                distances[neighbor] = distances[curr] + 1;
                                queue.push(neighbor);
                            }
                        });
                    }
                }

                let pathBlocks = blockList.filter(b => distances[b.id] !== undefined || b.id === battery.id);
                
                if (pathBlocks.length > 1) {
                    let totalR = pathBlocks.reduce((sum, b) => sum + b.r, 0);
                    let circuitI = 9.0 / totalR;

                    pathBlocks.forEach(b => {
                        b.i = circuitI;
                        b.v = circuitI * b.r;
                        b.p = Math.pow(circuitI, 2) * b.r;
                        
                        if (distances[b.id] !== undefined) b.flowOrder = distances[b.id];

                        if(b.type === 'led') {
                            b.isLit = true;
                            activeCount++;
                            const m = b.mesh.userData.bulb.material;
                            m.color.set(b.ledSettings.color);
                            m.emissive.set(b.ledSettings.color);
                            m.emissiveIntensity = b.ledSettings.brightness;
                        }
                    });

                    // 파티클 생성 (흐르는 전기)
                    pathBlocks.forEach(b => {
                        if (b.type !== 'battery' && b.flowOrder !== -1) {
                            let pMat = new THREE.MeshBasicMaterial({ color: 0xffff00 });
                            let pMesh = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), pMat);
                            pMesh.position.copy(b.mesh.position);
                            scene.add(pMesh);
                            flowParticles.push({ mesh: pMesh, block: b, progress: 0 });
                        }
                    });
                }
            });

            if(activeCount > 0) showMessage(`정상 회로 ⚡! ${activeCount}개 기기 켜짐`, "#00ffcc");

            if(selectedBlock && blocks[`${selectedBlock.x},${selectedBlock.y},${selectedBlock.z}`]) {
                openProperties(selectedBlock);
            }
        };

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            const time = Date.now() * 0.001;
            
            // LED 깜빡임
            Object.values(blocks).forEach(b => {
                if(b.type === 'led' && b.isLit) {
                    const m = b.mesh.userData.bulb.material;
                    let intensity = b.ledSettings.brightness;
                    if (b.ledSettings.blink === 'fast') intensity = (Math.sin(time * 15) > 0) ? b.ledSettings.brightness : 0;
                    else if (b.ledSettings.blink === 'slow') intensity = (Math.sin(time * 5) > 0) ? b.ledSettings.brightness : 0;
                    m.emissiveIntensity = intensity;
                }
            });

            // 전기 입자(전자) 이동 애니메이션
            const blockList = Object.values(blocks);
            flowParticles.forEach(p => {
                p.progress += 0.02; // 이동 속도
                if(p.progress > 1) p.progress = 0;
                
                // 다음 연결 부품 찾기 (flowOrder가 나보다 1 큰 블록)
                let nextBlock = blockList.find(b => b.flowOrder === p.block.flowOrder + 1);
                
                // 만약 다음 블록이 없으면(마지막 부품) 배터리(-)극으로 돌아가도록 임시 설정
                let targetPos = nextBlock ? nextBlock.mesh.position : p.block.mesh.position;
                
                if (nextBlock) {
                    p.mesh.position.lerpVectors(p.block.mesh.position, targetPos, p.progress);
                }
            });

            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            renderer.setSize(window.innerWidth, window.innerHeight);
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
        });
    </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
