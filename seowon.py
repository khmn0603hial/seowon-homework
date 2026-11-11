import streamlit as st
import streamlit.components.v1 as components

# 웹페이지 기본 설정
st.set_page_config(page_title="3D 회로 시뮬레이터", layout="wide")

# 실행할 HTML 코드 (큰따옴표 3개로 감싸기)
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>3D Circuit Sandbox - Vertical Expansion Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background-color: #1a1a1a; font-family: 'Segoe UI', sans-serif; user-select: none; touch-action: none; }
        #canvas-container { width: 100vw; height: 100vh; display: block; }
        
        #ui-layer { position: absolute; top: 10px; left: 10px; pointer-events: none; z-index: 10; width: 290px; }
        .panel { background: rgba(20, 20, 25, 0.9); color: #ddd; padding: 12px; border-radius: 10px; border: 1px solid #444; pointer-events: auto; backdrop-filter: blur(8px); }
        
        h1 { margin: 0 0 8px 0; font-size: 16px; color: #fff; }
        p { margin: 0 0 10px 0; font-size: 11px; color: #aaa; line-height: 1.3; }

        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        button { background: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; }
        button.active { background: #007bff; border-color: #0056b3; box-shadow: 0 0 10px rgba(0, 123, 255, 0.4); }
        
        .action-btn { width: 100%; padding: 10px; font-size: 13px; margin-top: 8px; background: #28a745; border: none; border-radius: 6px; color: white; cursor: pointer; }
        .reset-btn { background: #dc3545; margin-top: 6px; }

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
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui-layer">
        <div class="panel">
            <h1>🏢 3D 입체 회로 샌드박스</h1>
            <p>• 전선/부품을 위로 계속 쌓을 수 있습니다.<br>• Y 높이에 따라 전선 색상이 달라집니다.<br>• [수직 도선]으로 층간 전기를 연결하세요.</p>
            
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
            
            <button class="action-btn" onclick="analyzeCircuit()">⚡ AI 회로 분석 & 전원 ON</button>
            <button class="action-btn reset-btn" onclick="clearAll()">전체 초기화</button>
        </div>
    </div>

    <div id="prop-panel">
        <h3 id="prop-title">부품 정보</h3>
        <div class="stat-row"><span>위치 (X, Y, Z):</span> <span id="prop-pos" class="stat-val">0, 0, 0</span></div>
        <div class="stat-row"><span>고유 저항 (R):</span> <span id="prop-r" class="stat-val">0 Ω</span></div>
        <div class="stat-row"><span>측정 전압 (V):</span> <span id="prop-v" class="stat-val">0 V</span></div>
        <div class="stat-row"><span>측정 전류 (I):</span> <span id="prop-i" class="stat-val">0 mA</span></div>
        <div class="stat-row"><span>소비 전력 (P):</span> <span id="prop-p" class="stat-val">0 mW</span></div>
        
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
        let blocks = {}; 
        let nextBlockId = 1;
        let previewMesh = null;
        let selectedBlock = null;

        const layerColors = [0xb87333, 0x00aaff, 0x00ffaa, 0xffaa00, 0xff0055, 0xaa00ff];

        function getWireColorByY(yIndex) {
            return layerColors[Math.min(yIndex, layerColors.length - 1)];
        }

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        camera.position.set(0, 10, 15);
        controls.enableDamping = true;

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
            battery: new THREE.MeshPhongMaterial({ color: 0x222222 }),
            batteryPos: new THREE.MeshBasicMaterial({ color: 0xff0000 }),
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
                const body = new THREE.Mesh(new THREE.BoxGeometry(1, 0.6, 1), materials.battery);
                const pos = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.7, 0.2), materials.batteryPos);
                pos.position.set(0.3, 0, 0.3);
                group.add(body, pos);
            } else if (type === 'wire') {
                const wireColor = getWireColorByY(yLayer);
                const wireMat = new THREE.MeshPhongMaterial({ color: wireColor });
                const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 0.2, 1), wireMat);
                group.add(mesh);
            } else if (type === 'vwire') {
                const mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 1, 16), materials.vwire);
                group.add(mesh);
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
                            if(c.isMesh) { 
                                c.material = c.material.clone(); 
                                c.material.transparent = true; 
                                c.material.opacity = 0.5; 
                            } 
                        });
                        scene.add(previewMesh);
                    }
                    previewMesh.position.copy(pos);
                }
            }
        });

        renderer.domElement.addEventListener('pointerdown', (event) => {
            if (event.pointerType === 'mouse' && event.button !== 0) return;
            if (event.clientX < 300 && event.clientY < 320) return;
            
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
                    
                    let resistance = 0.1;
                    if (type === 'led') resistance = 100;
                    if (type === 'battery') resistance = 1;
                    if (type === 'voltmeter') resistance = 100000;
                    if (type === 'ammeter') resistance = 0.01;
                    
                    const block = { 
                        id: nextBlockId++, type: type, 
                        x: pos.x, y: pos.y, z: pos.z, yLayer: yLayer,
                        mesh: createBlockMesh(type, yLayer),
                        r: resistance, v: 0, i: 0, p: 0,
                        isLit: false,
                        ledSettings: type === 'led' ? { color: '#ff0000', brightness: 2, blink: 'none' } : null
                    };
                    block.mesh.position.copy(pos);
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
            
            let titles = { 
                'battery': '🔋 배터리', 'wire': '〰️ 수평 전선', 'vwire': '🪜 수직 도선',
                'led': '💡 커스텀 LED', 'voltmeter': '📟 전압계', 'ammeter': '📊 전류계' 
            };
            document.getElementById('prop-title').innerText = titles[block.type];
            document.getElementById('prop-pos').innerText = `${block.x}, ${block.y}, ${block.z}`;
            
            document.getElementById('prop-r').innerText = block.r + " Ω";
            document.getElementById('prop-v').innerText = block.v.toFixed(2) + " V";
            document.getElementById('prop-i').innerText = (block.i * 1000).toFixed(1) + " mA";
            document.getElementById('prop-p').innerText = (block.p * 1000).toFixed(1) + " mW";
            
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

        window.analyzeCircuit = function() {
            const blockList = Object.values(blocks);
            
            blockList.forEach(b => {
                b.v = 0; b.i = 0; b.p = 0; b.isLit = false;
                if (b.type === 'led') {
                    b.mesh.userData.bulb.material.color.setHex(0x444444);
                    b.mesh.userData.bulb.material.emissive.setHex(0x000000);
                }
            });

            const batteries = blockList.filter(b => b.type === 'battery');
            if (batteries.length === 0) return;

            const adj = {};
            blockList.forEach(b => adj[b.id] = []);
            
            for(let i=0; i<blockList.length; i++) {
                for(let j=i+1; j<blockList.length; j++) {
                    const b1 = blockList[i]; 
                    const b2 = blockList[j];
                    
                    const dx = Math.abs(b1.x - b2.x);
                    const dy = Math.abs(b1.y - b2.y);
                    const dz = Math.abs(b1.z - b2.z);
                    
                    let canConnect = false;

                    if (dy === 0 && ((dx === 1 && dz === 0) || (dx === 0 && dz === 1))) {
                        canConnect = true;
                    } else if (dx === 0 && dz === 0 && dy === 1) {
                        if (b1.type === 'vwire' || b2.type === 'vwire' || b1.type === 'wire' || b2.type === 'wire') {
                            canConnect = true;
                        }
                    }

                    if (canConnect) {
                        adj[b1.id].push(b2.id); 
                        adj[b2.id].push(b1.id);
                    }
                }
            }

            let activeCount = 0;
            batteries.forEach(battery => {
                let visited = new Set();
                let queue = [battery.id];
                visited.add(battery.id);
                
                while(queue.length > 0) {
                    let curr = queue.shift();
                    adj[curr].forEach(neighbor => {
                        if(!visited.has(neighbor)) {
                            visited.add(neighbor); 
                            queue.push(neighbor);
                        }
                    });
                }

                let pathBlocks = blockList.filter(b => visited.has(b.id));
                
                if (pathBlocks.length > 1) {
                    let totalR = pathBlocks.reduce((sum, b) => sum + b.r, 0);
                    let circuitI = 9.0 / totalR;

                    pathBlocks.forEach(b => {
                        b.i = circuitI;
                        b.v = circuitI * b.r;
                        b.p = Math.pow(circuitI, 2) * b.r;
                        
                        if(b.type === 'led') {
                            b.isLit = true;
                            activeCount++;
                            const m = b.mesh.userData.bulb.material;
                            m.color.set(b.ledSettings.color);
                            m.emissive.set(b.ledSettings.color);
                            m.emissiveIntensity = b.ledSettings.brightness;
                        }
                    });
                }
            });

            if(activeCount > 0) showMessage(`3D 회로 전원 공급 중! ${activeCount}개 기기 작동`, "#00ffcc");

            if(selectedBlock && blocks[`${selectedBlock.x},${selectedBlock.y},${selectedBlock.z}`]) {
                openProperties(selectedBlock);
            }
        };

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            
            const time = Date.now() * 0.001;
            
            Object.values(blocks).forEach(b => {
                if(b.type === 'led' && b.isLit) {
                    const m = b.mesh.userData.bulb.material;
                    let intensity = b.ledSettings.brightness;
                    
                    if (b.ledSettings.blink === 'fast') {
                        intensity = (Math.sin(time * 15) > 0) ? b.ledSettings.brightness : 0;
                    } else if (b.ledSettings.blink === 'slow') {
                        intensity = (Math.sin(time * 5) > 0) ? b.ledSettings.brightness : 0;
                    }
                    m.emissiveIntensity = intensity;
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

# HTML을 Streamlit component로 출력
components.html(html_code, height=800, scrolling=False)
