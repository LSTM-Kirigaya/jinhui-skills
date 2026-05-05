---
name: ddd-go-backend-auth
description: JWT + OAuth2 authentication system. Covers JWT middleware, bcrypt password hashing, refresh token rotation, multi-provider OAuth2 (GitHub, custom), device code flow, admin middleware, and banned user middleware.
---

# Auth: JWT + OAuth2 Authentication

## Overview

The auth system supports two authentication methods:
1. **Password-based** — email/username + password, bcrypt hashed
2. **OAuth2** — multi-provider (GitHub, Watcha, etc.) with account linking

## Domain Entities

```go
// internal/auth/domain/user.go
type User struct {
    common.Base
    Email        string `gorm:"uniqueIndex;size:255"`
    Username     string `gorm:"uniqueIndex;size:100"`
    PasswordHash string `gorm:"size:255"`
    Role         string `gorm:"size:50;default:'user'"`
    BannedAt     *time.Time
    Onboarded    bool   `gorm:"default:false"`
}

func (u *User) IsBanned() bool {
    return u.BannedAt != nil
}

func (u *User) RequiresOnboarding() bool {
    return !u.Onboarded
}

// internal/auth/domain/refresh_token.go
type RefreshToken struct {
    common.Base
    UserID    string `gorm:"index"`
    TokenHash string `gorm:"uniqueIndex;size:64"` // SHA256 hash
    DeviceID  string `gorm:"size:255"`
    ExpiresAt time.Time
}

// internal/auth/domain/oauth_account.go
type OAuthAccount struct {
    common.Base
    UserID         string `gorm:"index"`
    Provider       string `gorm:"size:50"`
    ProviderUserID string `gorm:"size:255"`
    AccessToken    string `gorm:"size:512"`
    RefreshToken   string `gorm:"size:512"`
    Email          string `gorm:"size:255"`
}
```

## JWT Middleware (`internal/auth/middleware.go`)

```go
type AuthServiceClaims struct {
    UserID   string `json:"user_id"`
    Email    string `json:"email"`
    Username string `json:"username"`
    Role     string `json:"role"`
    jwt.RegisteredClaims
}

func NewJWTAuthMiddleware(secret string, publicPaths []string) gin.HandlerFunc {
    return func(c *gin.Context) {
        // Skip public paths (prefix match)
        path := c.Request.URL.Path
        for _, p := range publicPaths {
            if strings.HasPrefix(path, p) {
                c.Next()
                return
            }
        }

        tokenStr := extractBearerToken(c)
        if tokenStr == "" {
            c.JSON(401, gin.H{"code": 20001, "message": "missing authorization header"})
            c.Abort()
            return
        }

        claims := &AuthServiceClaims{}
        token, err := jwt.ParseWithClaims(tokenStr, claims,
            func(t *jwt.Token) (interface{}, error) {
                return []byte(secret), nil
            },
        )
        if err != nil || !token.Valid {
            c.JSON(401, gin.H{"code": 20002, "message": "invalid or expired token"})
            c.Abort()
            return
        }

        // Inject claims into context
        c.Set("user_id", claims.UserID)
        c.Set("email", claims.Email)
        c.Set("username", claims.Username)
        c.Set("role", claims.Role)
        c.Next()
    }
}

// Context helpers
func GetUserIDFromContext(c *gin.Context) string {
    return c.GetString("user_id")
}

func GetUserRoleFromContext(c *gin.Context) string {
    return c.GetString("role")
}

func GetClaimsFromContext(c *gin.Context) *AuthServiceClaims {
    val, _ := c.Get("claims")
    return val.(*AuthServiceClaims)
}
```

### Admin Middleware

```go
func NewRequireAdminMiddleware(userRepo *UserRepository) gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := GetUserIDFromContext(c)
        user, err := userRepo.FindByID(c.Request.Context(), userID)
        if err != nil || user.Role != "admin" {
            c.JSON(403, gin.H{"code": 40001, "message": "admin access required"})
            c.Abort()
            return
        }
        c.Next()
    }
}
```

### Banned User Middleware

```go
func NewBannedUserMiddleware(userRepo *UserRepository) gin.HandlerFunc {
    return func(c *gin.Context) {
        userID := GetUserIDFromContext(c)
        if userID == "" {
            c.Next()
            return
        }
        user, err := userRepo.FindByID(c.Request.Context(), userID)
        if err == nil && user.IsBanned() {
            c.JSON(403, gin.H{"code": 40002, "message": "user is banned"})
            c.Abort()
            return
        }
        c.Next()
    }
}
```

## Middleware Stack Order

Applied to `/api/v1` group:

```go
api := r.Group("/api/v1")
api.Use(gin.Logger())
api.Use(gin.Recovery())
api.Use(otelgin.Middleware(cfg.App.Name))  // if OTel enabled
api.Use(NewJWTAuthMiddleware(cfg.JWT.Secret, publicPaths))
api.Use(NewBannedUserMiddleware(userRepo))
```

## Password Auth Service

```go
type AuthService struct {
    userRepo  *UserRepository
    tokenRepo *TokenRepository
    jwtCfg    JWTConfig
}

// Register
func (s *AuthService) Register(ctx context.Context, email, username, password string) (*User, error) {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        return nil, err
    }
    user := &domain.User{
        Email:        email,
        Username:     username,
        PasswordHash: string(hash),
        Role:         "user",
    }
    if err := s.userRepo.Create(ctx, user); err != nil {
        return nil, err
    }
    return user, nil
}

// Login (by email OR username)
func (s *AuthService) Login(ctx context.Context, identifier, password, deviceID string) (*TokenPair, error) {
    user, err := s.userRepo.FindByIdentifier(ctx, identifier) // searches email AND username
    if err != nil {
        return nil, commonerrors.ErrInvalidCredentials
    }
    if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)); err != nil {
        return nil, commonerrors.ErrInvalidCredentials
    }
    if user.IsBanned() {
        return nil, commonerrors.ErrUserBanned
    }
    return s.generateTokenPair(ctx, user, deviceID)
}

// Token generation
func (s *AuthService) generateTokenPair(ctx context.Context, user *User, deviceID string) (*TokenPair, error) {
    now := time.Now()

    accessToken, _ := s.createJWT(user, now.Add(time.Duration(s.jwtCfg.AccessTokenTTL)*time.Second))
    refreshToken := generateRandomToken(64)

    // Store SHA256 hash of refresh token
    hash := sha256Hex(refreshToken)
    err := s.tokenRepo.Save(ctx, &domain.RefreshToken{
        UserID:    user.ID,
        TokenHash: hash,
        DeviceID:  deviceID,
        ExpiresAt: now.Add(time.Duration(s.jwtCfg.RefreshTokenTTL) * time.Second),
    })

    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
        ExpiresIn:    s.jwtCfg.AccessTokenTTL,
    }, err
}

// Refresh
func (s *AuthService) Refresh(ctx context.Context, refreshToken, deviceID string) (*TokenPair, error) {
    hash := sha256Hex(refreshToken)
    stored, err := s.tokenRepo.FindByHash(ctx, hash)
    if err != nil || stored.ExpiresAt.Before(time.Now()) {
        return nil, commonerrors.ErrInvalidRefreshToken
    }
    // Rotate: delete old, issue new
    s.tokenRepo.DeleteByHash(ctx, hash)

    user, _ := s.userRepo.FindByID(ctx, stored.UserID)
    return s.generateTokenPair(ctx, user, deviceID)
}

// Logout single device
func (s *AuthService) Logout(ctx context.Context, userID, deviceID string) error {
    return s.tokenRepo.DeleteByUserAndDevice(ctx, userID, deviceID)
}

// Logout all devices
func (s *AuthService) LogoutAll(ctx context.Context, userID string) error {
    return s.tokenRepo.DeleteAllByUser(ctx, userID)
}
```

## OAuth2 Multi-Provider Service

```go
type OAuthService struct {
    userRepo   *UserRepository
    oauthRepo  *OAuthRepository
    tokenRepo  *TokenRepository
    jwtCfg     JWTConfig
    providers  map[string]*oauth2.Config
}

func NewOAuthService(/* ... */) *OAuthService {
    svc := &OAuthService{/* ... */}
    svc.providers = map[string]*oauth2.Config{
        "github": {
            ClientID:     cfg.Github.ClientID,
            ClientSecret: cfg.Github.ClientSecret,
            RedirectURL:  cfg.Github.RedirectURL,
            Scopes:       []string{"user:email"},
            Endpoint:     github.Endpoint,
        },
    }
    return svc
}

// Get authorization URL
func (s *OAuthService) GetAuthURL(provider string, state string) (string, error) {
    cfg, ok := s.providers[provider]
    if !ok {
        return "", commonerrors.ErrUnknownProvider
    }
    return cfg.AuthCodeURL(state, oauth2.AccessTypeOffline), nil
}

// Handle callback — exchange code, fetch user info, find-or-create user
func (s *OAuthService) HandleCallback(ctx context.Context, provider, code string) (*TokenPair, error) {
    cfg := s.providers[provider]
    token, err := cfg.Exchange(ctx, code)
    if err != nil {
        return nil, err
    }

    // Fetch user info from provider
    userInfo, err := s.fetchProviderUserInfo(ctx, provider, token)
    if err != nil {
        return nil, err
    }

    // Find or create user
    user, err := s.findOrCreateUser(ctx, provider, userInfo)
    if err != nil {
        return nil, err
    }

    // Link OAuth account
    s.oauthRepo.Upsert(ctx, &domain.OAuthAccount{
        UserID:         user.ID,
        Provider:       provider,
        ProviderUserID: userInfo.ID,
        Email:          userInfo.Email,
        AccessToken:    token.AccessToken,
        RefreshToken:   token.RefreshToken,
    })

    return s.generateTokenPair(ctx, user, "oauth")
}

// findOrCreate: try to link by email, otherwise create new user
func (s *OAuthService) findOrCreateUser(ctx context.Context, provider string, info *ProviderUserInfo) (*domain.User, error) {
    // Check if this OAuth account already linked
    existing, _ := s.oauthRepo.FindByProviderAndID(ctx, provider, info.ID)
    if existing != nil {
        return s.userRepo.FindByID(ctx, existing.UserID)
    }

    // Try to link by email
    if info.Email != "" {
        user, err := s.userRepo.FindByEmail(ctx, info.Email)
        if err == nil {
            return user, nil
        }
    }

    // Create new user with synthetic email
    syntheticEmail := fmt.Sprintf("%s-%s@oauth.%s", provider, info.ID, cfg.App.Name)
    user := &domain.User{
        Email:    syntheticEmail,
        Username: info.Username,
        Role:     "user",
    }
    if err := s.userRepo.Create(ctx, user); err != nil {
        return nil, err
    }
    return user, nil
}
```

## OAuth Callback Handler — Three Modes

The callback handler supports three completion modes based on the `state` parameter:

### 1. Device Flow
User approves on browser → writes tokens to device session → shows success page.

### 2. Local Redirect Flow
Stores a nonce in DB with 10-minute expiry → redirects to a local URI with the nonce → client exchanges nonce for tokens.

### 3. Popup Flow
Renders an HTML page with `postMessage` to the opener window.

```go
func (h *AuthHandler) OAuthCallback(c *gin.Context) {
    provider := c.Param("provider")
    state := c.Query("state")

    tokenPair, err := h.oauthService.HandleCallback(c.Request.Context(), provider, c.Query("code"))
    if err != nil {
        response.Error(c, err)
        return
    }

    // Route by state mode
    switch {
    case strings.HasPrefix(state, "device:"):
        // Store tokens in device session, render success HTML
        deviceCode := strings.TrimPrefix(state, "device:")
        h.oauthService.StoreDeviceTokens(c.Request.Context(), deviceCode, tokenPair)
        c.Data(200, "text/html", []byte(successHTML))

    case strings.HasPrefix(state, "redirect:"):
        // Store nonce, redirect to local URI
        nonce := uuid.New().String()
        h.oauthService.StoreNonce(c.Request.Context(), nonce, tokenPair)
        c.Redirect(302, fmt.Sprintf("http://localhost:0/callback?nonce=%s", nonce))

    default:
        // Popup: render postMessage HTML
        c.Data(200, "text/html", []byte(popupHTML(tokenPair)))
    }
}
```

## Public Paths (no JWT required)

```go
var publicPaths = []string{
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/oauth/",
    "/api/v1/auth/device/",
    "/api/v1/billing/webhooks/",
    "/api/v1/announcements/active",
}
```

Note: paths ending with `/` match by prefix — `/api/v1/auth/oauth/` covers all OAuth endpoints.
