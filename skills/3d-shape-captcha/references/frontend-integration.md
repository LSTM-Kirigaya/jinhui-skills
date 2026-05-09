# 3D Shape CAPTCHA - 前端集成参考

## 依赖

```bash
npm install three
```

## 场景配置

### 渲染器

```js
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
```

### 相机（正交投影）

使用 `OrthographicCamera` 消除透视变形，确保大小比较公平：

```js
const frustumSize = 7.5;
const aspect = width / height;
const camera = new THREE.OrthographicCamera(
    frustumSize * aspect / -2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    frustumSize / -2,
    0.1, 100
);
camera.position.set(8, 8, 8);
camera.lookAt(0, 0.5, 0);
```

### 光源（四级照明）

```js
// 环境基础光
const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
scene.add(ambientLight);

// 半球光（天空/地面反射）
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x888899, 0.4);
scene.add(hemiLight);

// 主光源（投射阴影）
const dirLight = new THREE.DirectionalLight(0xfff8f0, 1.4);
dirLight.position.set(4, 12, 6);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.left = -8;
dirLight.shadow.camera.right = 8;
dirLight.shadow.camera.top = 8;
dirLight.shadow.camera.bottom = -8;
dirLight.shadow.bias = -0.0005;
scene.add(dirLight);

// 补光
const fillLight = new THREE.DirectionalLight(0xcce0ff, 0.25);
fillLight.position.set(-6, 5, -4);
scene.add(fillLight);

// 轮廓光
const rimLight = new THREE.PointLight(0xffeedd, 0.4, 20);
rimLight.position.set(-2, 6, 4);
scene.add(rimLight);
```

## 几何体映射

| 类型值 | 形体 | Three.js 几何体 |
|---|---|---|
| 0 | 正方体 | `BoxGeometry(1, 1, 1)` |
| 1 | 圆柱体 | `CylinderGeometry(0.5, 0.5, 1, 32)` |
| 2 | 三角柱 | `CylinderGeometry(0.5, 0.5, 1.25, 3)` |

三角柱高度设为 1.25（其他为 1.0），使其在视觉上更易辨识。

## 材质

```js
const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color(shape.color),
    roughness: 0.35,
    metalness: 0.08,
});
mesh.castShadow = true;
mesh.receiveShadow = true;
```

## 交互（Raycaster）

```js
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

// 归一化设备坐标
mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

raycaster.setFromCamera(mouse, camera);
const intersects = raycaster.intersectObjects(shapeMeshes);

if (intersects.length > 0) {
    const shapeIndex = intersects[0].object.userData.index;
    // 发送 shapeIndex 到后端验证
}
```

## 响应式尺寸

```css
.captcha-dialog {
    width: 100%;
    max-width: 520px; /* 桌面端 */
}
.canvas-container {
    width: 100%;
    height: 360px; /* 桌面端 */
}

@media (max-width: 480px) {
    .canvas-container { height: 260px; }
}
@media (max-width: 360px) {
    .canvas-container { height: 220px; }
}
```

## 生命周期管理

```js
// 初始化
function initThreeJS() {
    // 创建 scene, camera, renderer, lights, meshes...
    renderer.render(scene, camera);
}

// 清理（防止内存泄漏）
function disposeThreeJS() {
    shapeMeshes.forEach(mesh => {
        mesh.geometry?.dispose();
        mesh.material?.dispose();
    });
    renderer?.dispose();
    // 移除 DOM 中的 canvas
}
```

## API 调用

```js
// 生成
export const reqGenerateCaptcha = () => 
    r({ url: "/captcha/generate", method: "GET" });

// 验证（改为 shapeIndex）
export const reqVerifyCaptcha = (captchaId, shapeIndex) => 
    r({ url: "/captcha/verify", method: "POST", data: { captchaId, shapeIndex } });
```
