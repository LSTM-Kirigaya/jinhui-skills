# 3D Shape CAPTCHA - 后端 API 参考

## 架构

后端不渲染图片，只生成 3D 场景元数据（6 个几何体的位置、旋转、大小、颜色、类型），由前端用 Three.js 实时渲染。

## 数据模型

### Shape 结构体

```go
type Shape struct {
    Type      ShapeType `json:"type"`      // 0=cube, 1=cylinder, 2=tri_prism
    X         float64   `json:"x"`         // 3D 世界坐标
    Y         float64   `json:"y"`
    Z         float64   `json:"z"`
    RotationY float64   `json:"rotationY"` // Y 轴旋转（弧度）
    Scale     float64   `json:"scale"`     // 统一缩放系数
    Color     string    `json:"color"`     // 十六进制颜色 #RRGGBB
    Volume    float64   `json:"volume"`    // 体积（scale³）
}
```

### captchaData（Redis 存储）

```go
type captchaData struct {
    TargetIndex int     `json:"targetIndex"` // 目标物体索引
    Shapes      []Shape `json:"shapes"`
    Prompt      string  `json:"prompt"`      // "最大" 或 "最小"
    TargetShape string  `json:"targetShape"` // "正方体"/"圆柱体"/"三角柱"
}
```

## API 端点

### GET /api/captcha/generate

生成新的 CAPTCHA 挑战。

**响应：**
```json
{
  "success": true,
  "data": {
    "captchaId": "seed_rand",
    "shapes": [
      {"type":0, "x":-2.5, "y":0.5, "z":-1.2, "rotationY":0.3, "scale":0.58, "color":"#56A2A0", "volume":0.195}
    ],
    "prompt": "最大",
    "targetShape": "正方体",
    "width": 500,
    "height": 400
  }
}
```

### POST /api/captcha/verify

验证用户点击的物体。

**请求体：**
```json
{"captchaId": "...", "shapeIndex": 3}
```

**成功响应：**
```json
{"success": true, "data": {"token": "captcha_pass_..."}}
```

**失败响应：**
```json
{"success": false, "message": "选择错误，请重试"}
```

## 比例尺生成算法

核心要求：**6 个物体大小严格互不相同**。

```go
baseMin := 0.55
baseMax := 1.30
n := 6
step := (baseMax - baseMin) / float64(n-1) // 等差步长 ≈ 0.15

scales := make([]float64, n)
for i := 0; i < n; i++ {
    base := baseMin + float64(i)*step
    jitter := (rng.Float64() - 0.5) * 0.06 // 微小扰动 ±0.03
    scales[i] = math.Round((base+jitter)*100) / 100
}
rng.Shuffle(n, func(i, j int) {
    scales[i], scales[j] = scales[j], scales[i]
})
```

**唯一性保证：**
- 基础间距 0.15 > 扰动范围 0.06
- 扰动后相邻值最小差距 ≈ 0.09
- 6 个值分布在 6 个互不相交的区间内

**结果示例：** `[0.58, 0.71, 0.85, 0.98, 1.17, 1.32]` — 最大/最小比例约 2.3:1

## 布局算法

```
2行 × 3列网格，中心点：
  {-2.5, -1.2}, {0, -1.2}, {2.5, -1.2},
  {-2.5, 1.2},  {0, 1.2},  {2.5, 1.2}
```

每个物体在单元格内随机偏移 ±0.4，网格打乱后分配。最大物体 scale=1.3 时占据空间约 1.3，中心间距 2.5，保证不重叠。

## Redis 存储

- Key: `captcha:{captchaId}`，TTL: 5 分钟
- 验证通过后删除 captcha key，生成一次性 token: `captcha_token:{token}`，TTL: 5 分钟
- Token 校验函数 `ValidateCaptchaToken` 供其他模块（如邮件发送）调用

## 集成邮件验证码

邮件发送接口需校验 `captchaToken`：

```go
if !captcha.ValidateCaptchaToken(redisClient, req.CaptchaToken) {
    // 拒绝：图形验证未通过或已过期
}
```
