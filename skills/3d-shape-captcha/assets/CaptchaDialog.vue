<template>
    <Teleport to="body">
        <div v-if="visible" class="captcha-overlay" @click.self="close">
            <div class="captcha-dialog">
                <div class="captcha-header">
                    <h3>安全验证</h3>
                    <button class="close-btn" @click="close">
                        <span class="iconfont icon-close"></span>
                    </button>
                </div>
                <div class="captcha-body">
                    <p class="captcha-tip">
                        请点击画面中<strong>{{ prompt || '最小' }}的{{ targetShape || '几何体' }}</strong>
                    </p>
                    <div class="captcha-canvas-wrap" :class="{ 'is-loading': !shapes.length }">
                        <div v-if="shapes.length" ref="canvasContainer" class="canvas-container"></div>
                        <div v-else class="captcha-loading">
                            <span class="iconfont icon-loading spin"></span>
                            <span>加载中...</span>
                        </div>
                        <div v-if="verifying" class="verifying-mask">
                            <span class="iconfont icon-loading spin"></span>
                        </div>
                    </div>
                    <div class="captcha-actions">
                        <button class="refresh-btn" @click="loadCaptcha" :disabled="loading">
                            <span class="iconfont icon-refresh" :class="{ spin: loading }"></span>
                            换一张
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script>
import { ref, watch, onBeforeUnmount, nextTick } from 'vue';
import * as THREE from 'three';
import { reqGenerateCaptcha, reqVerifyCaptcha } from '@/api';
import { showInfoWindow } from '@/hook/window';

export default {
    name: 'CaptchaDialog',
    props: {
        modelValue: {
            type: Boolean,
            default: false
        }
    },
    emits: ['update:modelValue', 'success'],
    setup(props, { emit }) {
        const visible = ref(props.modelValue);
        const captchaId = ref('');
        const prompt = ref('');
        const targetShape = ref('');
        const shapes = ref([]);
        const loading = ref(false);
        const verifying = ref(false);
        const canvasContainer = ref(null);

        // Three.js refs
        let renderer = null;
        let scene = null;
        let camera = null;
        let raycaster = null;
        let mouse = null;
        let shapeMeshes = [];
        let clickMarker = null;
        let onClickHandler = null;
        let onTouchHandler = null;
        let onResizeHandler = null;

        watch(() => props.modelValue, (val) => {
            visible.value = val;
            if (val) {
                loadCaptcha();
            } else {
                disposeThreeJS();
            }
        });

        watch(visible, (val) => {
            emit('update:modelValue', val);
        });

        function close() {
            visible.value = false;
            shapes.value = [];
            captchaId.value = '';
            prompt.value = '';
            targetShape.value = '';
        }

        function disposeThreeJS() {
            if (clickMarker) {
                scene?.remove(clickMarker);
                clickMarker.geometry?.dispose();
                clickMarker.material?.dispose();
                clickMarker = null;
            }
            shapeMeshes.forEach(mesh => {
                scene?.remove(mesh);
                mesh.geometry?.dispose();
                mesh.material?.dispose();
            });
            shapeMeshes = [];

            if (renderer) {
                const canvas = renderer.domElement;
                if (onClickHandler) canvas.removeEventListener('click', onClickHandler);
                if (onTouchHandler) canvas.removeEventListener('touchend', onTouchHandler);
                renderer.dispose();
                if (canvas.parentNode) {
                    canvas.parentNode.removeChild(canvas);
                }
                renderer = null;
            }

            if (onResizeHandler) {
                window.removeEventListener('resize', onResizeHandler);
                onResizeHandler = null;
            }

            scene = null;
            camera = null;
            raycaster = null;
            mouse = null;
            onClickHandler = null;
            onTouchHandler = null;
        }

        async function loadCaptcha() {
            loading.value = true;
            shapes.value = [];
            disposeThreeJS();

            try {
                const res = await reqGenerateCaptcha();
                if (res.success && res.data) {
                    captchaId.value = res.data.captchaId;
                    shapes.value = res.data.shapes || [];
                    prompt.value = res.data.prompt || '';
                    targetShape.value = res.data.targetShape || '';

                    await nextTick();
                    initThreeJS();
                } else {
                    showInfoWindow('验证码加载失败', res.message || '请稍后重试');
                }
            } catch (e) {
                showInfoWindow('网络错误', '验证码加载失败，请稍后重试');
            } finally {
                loading.value = false;
            }
        }

        function initThreeJS() {
            if (!canvasContainer.value || shapes.value.length === 0) return;

            const container = canvasContainer.value;
            const width = container.clientWidth;
            const height = container.clientHeight;

            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf8f9fc);

            // Camera - Orthographic for fair size comparison
            const aspect = width / height;
            const frustumSize = 7.5;
            camera = new THREE.OrthographicCamera(
                frustumSize * aspect / -2,
                frustumSize * aspect / 2,
                frustumSize / 2,
                frustumSize / -2,
                0.1,
                100
            );
            camera.position.set(8, 8, 8);
            camera.lookAt(0, 0.5, 0);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            // Lights - enhanced three-point lighting for dramatic shadows
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
            scene.add(ambientLight);

            const hemiLight = new THREE.HemisphereLight(0xffffff, 0x888899, 0.4);
            scene.add(hemiLight);

            const dirLight = new THREE.DirectionalLight(0xfff8f0, 1.4);
            dirLight.position.set(4, 12, 6);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            dirLight.shadow.camera.near = 0.1;
            dirLight.shadow.camera.far = 30;
            dirLight.shadow.camera.left = -8;
            dirLight.shadow.camera.right = 8;
            dirLight.shadow.camera.top = 8;
            dirLight.shadow.camera.bottom = -8;
            dirLight.shadow.bias = -0.0005;
            dirLight.shadow.radius = 3;
            scene.add(dirLight);

            const fillLight = new THREE.DirectionalLight(0xcce0ff, 0.25);
            fillLight.position.set(-6, 5, -4);
            scene.add(fillLight);

            const rimLight = new THREE.PointLight(0xffeedd, 0.4, 20);
            rimLight.position.set(-2, 6, 4);
            scene.add(rimLight);

            // Ground plane
            const groundGeo = new THREE.PlaneGeometry(20, 20);
            const groundMat = new THREE.MeshStandardMaterial({
                color: 0xd8dbe2,
                roughness: 0.9,
                metalness: 0.0
            });
            const ground = new THREE.Mesh(groundGeo, groundMat);
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);

            // Create shapes
            shapeMeshes = [];
            shapes.value.forEach((shape, index) => {
                let geometry;
                switch (shape.type) {
                    case 0: // Cube
                        geometry = new THREE.BoxGeometry(1, 1, 1);
                        break;
                    case 1: // Cylinder
                        geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 32);
                        break;
                    case 2: // Triangular prism - taller for visibility
                        geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.25, 3);
                        break;
                    default:
                        geometry = new THREE.BoxGeometry(1, 1, 1);
                }

                const material = new THREE.MeshStandardMaterial({
                    color: new THREE.Color(shape.color),
                    roughness: 0.35,
                    metalness: 0.08,
                });

                const mesh = new THREE.Mesh(geometry, material);
                // Triangular prism has taller geometry (1.25 vs 1.0), adjust Y so bottom touches ground
                const yPos = shape.type === 2 ? shape.scale * 1.25 / 2 : shape.y;
                mesh.position.set(shape.x, yPos, shape.z);
                mesh.rotation.y = shape.rotationY;
                mesh.scale.setScalar(shape.scale);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.userData = { index };

                scene.add(mesh);
                shapeMeshes.push(mesh);
            });

            // Raycaster
            raycaster = new THREE.Raycaster();
            mouse = new THREE.Vector2();

            // Event handlers
            onClickHandler = (event) => {
                if (verifying.value || !renderer) return;
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                handleRaycast();
            };

            onTouchHandler = (event) => {
                if (verifying.value || !renderer) return;
                event.preventDefault();
                const touch = event.changedTouches[0];
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
                handleRaycast();
            };

            renderer.domElement.addEventListener('click', onClickHandler);
            renderer.domElement.addEventListener('touchend', onTouchHandler, { passive: false });

            // Handle window resize
            onResizeHandler = () => {
                if (!renderer || !camera || !canvasContainer.value) return;
                const w = canvasContainer.value.clientWidth;
                const h = canvasContainer.value.clientHeight;
                const a = w / h;
                camera.left = frustumSize * a / -2;
                camera.right = frustumSize * a / 2;
                camera.top = frustumSize / 2;
                camera.bottom = frustumSize / -2;
                camera.updateProjectionMatrix();
                renderer.setSize(w, h);
                renderer.render(scene, camera);
            };
            window.addEventListener('resize', onResizeHandler);

            // Initial render
            renderer.render(scene, camera);
        }

        function handleRaycast() {
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(shapeMeshes);

            if (intersects.length > 0) {
                const hitMesh = intersects[0].object;
                const shapeIndex = hitMesh.userData.index;
                const hitPoint = intersects[0].point;

                // Visual feedback
                showClickMarker(hitPoint);

                // Verify
                verifyShape(shapeIndex);
            }
        }

        function showClickMarker(point) {
            if (clickMarker) {
                scene.remove(clickMarker);
                clickMarker.geometry.dispose();
                clickMarker.material.dispose();
            }

            const markerGeo = new THREE.SphereGeometry(0.1, 16, 16);
            const markerMat = new THREE.MeshBasicMaterial({
                color: 0x56A2A0,
                transparent: true,
                opacity: 0.85
            });
            clickMarker = new THREE.Mesh(markerGeo, markerMat);
            clickMarker.position.copy(point);
            clickMarker.position.y += 0.15;
            scene.add(clickMarker);

            renderer.render(scene, camera);
        }

        async function verifyShape(shapeIndex) {
            verifying.value = true;
            try {
                const res = await reqVerifyCaptcha(captchaId.value, shapeIndex);
                if (res.success && res.data && res.data.token) {
                    emit('success', res.data.token);
                    close();
                } else {
                    showInfoWindow('验证失败', res.message || '选择错误，请重试');
                    setTimeout(() => loadCaptcha(), 600);
                }
            } catch (e) {
                showInfoWindow('网络错误', '验证失败，请稍后重试');
            } finally {
                verifying.value = false;
            }
        }

        onBeforeUnmount(() => {
            disposeThreeJS();
        });

        return {
            visible,
            shapes,
            prompt,
            targetShape,
            loading,
            verifying,
            canvasContainer,
            close,
            loadCaptcha
        };
    }
}
</script>

<style scoped>
.captcha-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    animation: fadeIn 0.25s ease;
    padding: 16px;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.captcha-dialog {
    background: rgba(255, 255, 255, 0.96);
    border-radius: 20px;
    box-shadow:
        0 25px 50px -12px rgba(0, 0, 0, 0.2),
        0 0 0 1px rgba(255, 255, 255, 0.5) inset;
    width: 100%;
    max-width: 520px;
    overflow: hidden;
    animation: dialogSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid rgba(255, 255, 255, 0.6);
}

@keyframes dialogSlideIn {
    from {
        opacity: 0;
        transform: translateY(30px) scale(0.96);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.captcha-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px 14px;
    position: relative;
}

.captcha-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    font-family: var(--base-font);
}

.close-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: none;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    font-size: 16px;
    transition: all 0.2s;
}

.close-btn:hover {
    background: #f1f5f9;
    color: #475569;
}

.captcha-body {
    padding: 0 24px 24px;
}

.captcha-tip {
    margin: 0 0 16px;
    font-size: 14px;
    color: #64748b;
    text-align: center;
    font-family: var(--base-font);
    line-height: 1.5;
}

.captcha-tip strong {
    color: var(--main-color);
    font-weight: 700;
    background: linear-gradient(180deg, transparent 60%, rgba(86, 162, 160, 0.15) 60%);
    padding: 0 3px;
}

.captcha-canvas-wrap {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    border: 1.5px solid #e2e8f0;
    overflow: hidden;
    min-height: 280px;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 12px rgba(0, 0, 0, 0.03),
        0 0 0 1px rgba(255, 255, 255, 0.8) inset;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.captcha-canvas-wrap:hover {
    border-color: var(--main-color);
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 12px rgba(86, 162, 160, 0.08),
        0 0 0 1px rgba(255, 255, 255, 0.8) inset;
}

.captcha-canvas-wrap.is-loading {
    background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
}

.canvas-container {
    width: 100%;
    height: 360px;
    cursor: pointer;
}

.canvas-container canvas {
    display: block;
    width: 100%;
    height: 100%;
    outline: none;
    -webkit-tap-highlight-color: transparent;
}

.captcha-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 80px 20px;
    color: #94a3b8;
    font-size: 14px;
    font-family: var(--base-font);
}

.captcha-loading .iconfont {
    font-size: 28px;
    color: var(--main-color);
}

.verifying-mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(2px);
}

.verifying-mask .iconfont {
    font-size: 32px;
    color: var(--main-color);
}

.captcha-actions {
    display: flex;
    justify-content: center;
    margin-top: 16px;
}

.refresh-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 18px;
    background: #fff;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    cursor: pointer;
    font-size: 13px;
    color: #64748b;
    font-family: var(--base-font);
    transition: all 0.2s;
    font-weight: 500;
}

.refresh-btn:hover:not(:disabled) {
    border-color: var(--main-color);
    color: var(--main-color);
    background: #f0fdfa;
    box-shadow: 0 2px 8px rgba(86, 162, 160, 0.12);
}

.refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.spin {
    animation: spin 0.8s linear infinite;
    display: inline-block;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Mobile responsive */
@media (max-width: 480px) {
    .captcha-overlay {
        padding: 8px;
        align-items: flex-end;
    }

    .captcha-dialog {
        border-radius: 16px;
        max-width: 100%;
    }

    .captcha-header {
        padding: 16px 16px 10px;
    }

    .captcha-header h3 {
        font-size: 16px;
    }

    .captcha-body {
        padding: 0 16px 16px;
    }

    .captcha-tip {
        font-size: 13px;
        margin-bottom: 12px;
    }

    .captcha-canvas-wrap {
        min-height: 220px;
        border-radius: 12px;
    }

    .canvas-container {
        height: 260px;
    }

    .captcha-loading {
        padding: 60px 16px;
    }
}

@media (max-width: 360px) {
    .canvas-container {
        height: 220px;
    }

    .captcha-canvas-wrap {
        min-height: 200px;
    }
}
</style>
