package captcha

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"time"

	"dustbe/database"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

const captchaTTL = 5 * time.Minute

// ShapeType 几何体类型
type ShapeType int

const (
	ShapeCube     ShapeType = iota // 立方体
	ShapeCylinder                  // 圆柱体
	ShapeTriPrism                  // 三角柱
)

// Shape 3D几何体元数据
type Shape struct {
	Type      ShapeType `json:"type"`      // 0=cube, 1=cylinder, 2=tri_prism
	X         float64   `json:"x"`         // 3D世界坐标X
	Y         float64   `json:"y"`         // 3D世界坐标Y（底部贴地）
	Z         float64   `json:"z"`         // 3D世界坐标Z
	RotationY float64   `json:"rotationY"` // Y轴旋转（弧度）
	Scale     float64   `json:"scale"`     // 统一缩放系数
	Color     string    `json:"color"`     // 十六进制颜色 #RRGGBB
	Volume    float64   `json:"volume"`    // 体积（用于判断最大/最小）
}

// captchaData Redis存储
type captchaData struct {
	TargetIndex int     `json:"targetIndex"`
	Shapes      []Shape `json:"shapes"`
	Prompt      string  `json:"prompt"`
	TargetShape string  `json:"targetShape"`
}

type VerifyRequest struct {
	CaptchaID   string `json:"captchaId"`
	ShapeIndex  int    `json:"shapeIndex"`
}

var shapeColors = []string{
	"#56A2A0", // 青绿色
	"#D26955", // 橙红色
	"#6991D7", // 蓝色
	"#C3AF5A", // 金黄色
	"#AF73AF", // 紫色
	"#73B973", // 绿色
}

// shapeTypeName 返回形体类型的中文名称
func shapeTypeName(t ShapeType) string {
	switch t {
	case ShapeCube:
		return "正方体"
	case ShapeCylinder:
		return "圆柱体"
	case ShapeTriPrism:
		return "三角柱"
	}
	return "几何体"
}

// generateShapes 生成6个不重叠的3D几何体
func generateShapes(seed int64) ([]Shape, int, string, string) {
	rng := rand.New(rand.NewSource(seed))

	// ---- 比例尺：生成6个严格互不相同的大小 ----
	// 基础范围 [0.55, 1.30]，等差分布，加入微小扰动后仍保证唯一
	baseMin := 0.55
	baseMax := 1.30
	n := 6
	step := (baseMax - baseMin) / float64(n-1) // 等差步长 ≈ 0.15

	scales := make([]float64, n)
	for i := 0; i < n; i++ {
		base := baseMin + float64(i)*step
		// 微小扰动 ±0.03，由于基础间距 0.15 > 0.06，扰动后仍互不相同
		jitter := (rng.Float64() - 0.5) * 0.06
		scales[i] = math.Round((base+jitter)*100) / 100
	}
	// 打乱顺序分配给6个位置
	rng.Shuffle(n, func(i, j int) {
		scales[i], scales[j] = scales[j], scales[i]
	})

	// 2行 × 3列网格位置（中心点）
	gridPositions := [][2]float64{
		{-2.5, -1.2}, {0, -1.2}, {2.5, -1.2},
		{-2.5, 1.2}, {0, 1.2}, {2.5, 1.2},
	}
	rng.Shuffle(len(gridPositions), func(i, j int) {
		gridPositions[i], gridPositions[j] = gridPositions[j], gridPositions[i]
	})

	// 颜色随机分配，不重复
	colorIndices := []int{0, 1, 2, 3, 4, 5}
	rng.Shuffle(len(colorIndices), func(i, j int) {
		colorIndices[i], colorIndices[j] = colorIndices[j], colorIndices[i]
	})

	shapes := make([]Shape, 6)
	for i := 0; i < 6; i++ {
		scale := scales[i]

		// 在网格单元内加入随机偏移（±0.4）
		offsetX := (rng.Float64() - 0.5) * 0.8
		offsetZ := (rng.Float64() - 0.5) * 0.8
		x := gridPositions[i][0] + offsetX
		z := gridPositions[i][1] + offsetZ
		// Y坐标使物体底部贴地（scale/2是半高）
		y := scale / 2

		// 随机类型
		shapeType := ShapeType(rng.Intn(3))

		// 随机Y轴旋转 ±30度，增加立体感
		rotationY := (rng.Float64() - 0.5) * math.Pi / 3

		// 体积以 scale³ 为统一比较标准
		volume := scale * scale * scale

		shapes[i] = Shape{
			Type:      shapeType,
			X:         x,
			Y:         y,
			Z:         z,
			RotationY: rotationY,
			Scale:     scale,
			Color:     shapeColors[colorIndices[i]],
			Volume:    math.Round(volume*1000) / 1000,
		}
	}

	// 随机目标：最大或最小
	findMax := rng.Intn(2) == 0
	var targetIdx int
	var prompt string

	if findMax {
		prompt = "最大"
		maxScale := shapes[0].Scale
		targetIdx = 0
		for i := 1; i < len(shapes); i++ {
			if shapes[i].Scale > maxScale {
				maxScale = shapes[i].Scale
				targetIdx = i
			}
		}
	} else {
		prompt = "最小"
		minScale := shapes[0].Scale
		targetIdx = 0
		for i := 1; i < len(shapes); i++ {
			if shapes[i].Scale < minScale {
				minScale = shapes[i].Scale
				targetIdx = i
			}
		}
	}

	targetShape := shapeTypeName(shapes[targetIdx].Type)
	return shapes, targetIdx, prompt, targetShape
}

// GenerateCaptcha 生成验证码
func GenerateCaptcha(c *gin.Context) {
	seed := time.Now().UnixNano()

	shapes, targetIdx, prompt, targetShape := generateShapes(seed)

	captchaID := fmt.Sprintf("%d_%d", seed, rand.Intn(1000000))

	data := captchaData{
		TargetIndex: targetIdx,
		Shapes:      shapes,
		Prompt:      prompt,
		TargetShape: targetShape,
	}
	dataBytes, _ := json.Marshal(data)
	ctx := database.RedisDriver.Context()
	key := fmt.Sprintf("captcha:%s", captchaID)
	if err := database.RedisDriver.Set(ctx, key, string(dataBytes), captchaTTL).Err(); err != nil {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证服务不可用", "data": nil})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "验证码生成成功",
		"data": gin.H{
			"captchaId":   captchaID,
			"shapes":      shapes,
			"prompt":      prompt,
			"targetShape": targetShape,
			"width":       500,
			"height":      400,
		},
	})
}

// VerifyCaptcha 验证
func VerifyCaptcha(c *gin.Context) {
	var req VerifyRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "参数错误", "data": nil})
		return
	}

	if req.CaptchaID == "" {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证码ID不能为空", "data": nil})
		return
	}

	if req.ShapeIndex < 0 || req.ShapeIndex >= 6 {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "选择错误，请重试", "data": nil})
		return
	}

	ctx := database.RedisDriver.Context()
	key := fmt.Sprintf("captcha:%s", req.CaptchaID)
	dataStr, err := database.RedisDriver.Get(ctx, key).Result()
	if err != nil {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证码已过期或不存在", "data": nil})
		return
	}

	var data captchaData
	if err := json.Unmarshal([]byte(dataStr), &data); err != nil {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证数据异常", "data": nil})
		return
	}

	if data.TargetIndex < 0 || data.TargetIndex >= len(data.Shapes) {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证数据异常", "data": nil})
		return
	}

	if req.ShapeIndex != data.TargetIndex {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "选择错误，请重试", "data": nil})
		return
	}

	database.RedisDriver.Del(ctx, key)

	token := fmt.Sprintf("captcha_pass_%d", rand.Int63())
	tokenKey := fmt.Sprintf("captcha_token:%s", token)
	if err := database.RedisDriver.Set(ctx, tokenKey, "1", 5*time.Minute).Err(); err != nil {
		c.JSON(http.StatusOK, gin.H{"success": false, "message": "验证服务不可用", "data": nil})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "验证通过",
		"data":    gin.H{"token": token},
	})
}

// ValidateCaptchaToken 校验token
func ValidateCaptchaToken(redisClient *redis.Client, token string) bool {
	if token == "" {
		return false
	}
	ctx := redisClient.Context()
	key := fmt.Sprintf("captcha_token:%s", token)
	exists, err := redisClient.Exists(ctx, key).Result()
	if err != nil || exists == 0 {
		return false
	}
	redisClient.Del(ctx, key)
	return true
}
