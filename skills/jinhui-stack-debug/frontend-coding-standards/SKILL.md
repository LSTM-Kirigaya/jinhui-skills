---
name: frontend-coding-standards
description: 前端开发准则，适用于 Vue、React、Next.js、Taro 等框架。Use when developing frontend components to ensure: (1) Separation of component logic and styles, (2) Modular file organization with single-responsibility components, (3) File size control (split when exceeding 1000 lines), (4) Proper extraction and migration of sub-modules with their dependencies, (5) Regular creation of reusable component modules for better decoupling and software robustness.
---

# 前端开发准则

适用于 Vue、React、Next.js、Taro 等前端框架的组件开发规范。通过模块化组织代码，提升代码的可维护性、复用性和健壮性。

---

## 核心原则

> **小文件、高内聚、低耦合。**

组件应该小而专注，每个文件只负责一个明确的职责，避免将所有逻辑堆积在单个文件中。

---

## 四大准则

### 准则一：职责分离

**组件函数和样式必须分开开发，禁止在一个文件中堆积多个模块的实现。**

#### 推荐的文件组织方式

```
ComponentName/
├── index.tsx          # 组件入口（导出主组件）
├── Component.tsx      # 组件逻辑实现
├── Component.types.ts # 类型定义（Props、State、Interface）
├── Component.utils.ts # 工具函数（数据处理、格式化等）
├── Component.hooks.ts # 自定义 Hooks（复杂逻辑抽取）
└── Component.module.css / Component.styles.ts  # 样式定义
```

#### 禁止的做法

```tsx
// ❌ 错误示例：所有逻辑、样式、类型全部堆积在一个文件中
// pages/Dashboard.tsx (2000+ 行)

import React, { useState, useEffect } from 'react';

// 类型定义混杂
interface User { ... }
interface Order { ... }
interface Product { ... }
// ... 数十个类型定义

// 工具函数混杂
const formatDate = (date: string) => { ... };
const calculateTotal = (items: Item[]) => { ... };
// ... 数十个工具函数

// 子组件定义混杂
const UserCard = ({ user }) => { ... };
const OrderList = ({ orders }) => { ... };
const ProductGrid = ({ products }) => { ... };
// ... 数十个子组件

// 样式定义混杂（内联样式或 styled-components）
const styles = { ... };

// 主组件
export default function Dashboard() {
  // 数千行状态管理和业务逻辑
  // ...
  return (
    <div>
      <UserCard user={user} />
      <OrderList orders={orders} />
      <ProductGrid products={products} />
      {/* 数百行 JSX */}
    </div>
  );
}
```

#### 推荐的做法

```tsx
// ✅ 正确示例：模块拆分

// components/UserCard/index.tsx
export { UserCard } from './UserCard';

// components/UserCard/UserCard.tsx
import { UserCardProps } from './UserCard.types';
import { formatUserName } from './UserCard.utils';
import styles from './UserCard.module.css';

export function UserCard({ user }: UserCardProps) {
  return <div className={styles.card}>{formatUserName(user)}</div>;
}

// components/UserCard/UserCard.types.ts
export interface UserCardProps {
  user: User;
}

// components/UserCard/UserCard.utils.ts
export function formatUserName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}

// components/UserCard/UserCard.module.css
.card { padding: 16px; border: 1px solid #eee; }

// pages/Dashboard/index.tsx
import { UserCard } from '@/components/UserCard';
import { OrderList } from '@/components/OrderList';
import { ProductGrid } from '@/components/ProductGrid';

export default function Dashboard() {
  // 简洁的主组件，引用独立模块
  return (
    <div>
      <UserCard user={user} />
      <OrderList orders={orders} />
      <ProductGrid products={products} />
    </div>
  );
}
```

---

### 准则二：文件行数控制

**当一个文件超过 1000 行时，必须考虑将组件模块拆分到单独的文件中。**

#### 拆分检查清单

| 文件行数 | 处理方式 |
|---------|---------|
| < 300 行 | 可以接受，保持现状 |
| 300-500 行 | 观察是否有可抽取的重复逻辑 |
| 500-800 行 | 建议拆分，寻找内聚的子模块 |
| 800-1000 行 | 必须拆分，避免继续膨胀 |
| > 1000 行 | **强制拆分**，按功能模块分离 |

#### 拆分策略

```
拆分前：
├── pages/
│   └── Dashboard.tsx (1500 行)  ❌

拆分后：
├── pages/
│   └── Dashboard/
│       ├── index.tsx           # 入口文件（50 行）
│       ├── Dashboard.tsx       # 主组件逻辑（200 行）
│       ├── Dashboard.types.ts  # 类型定义（100 行）
│       ├── Dashboard.utils.ts  # 工具函数（150 行）
│       ├── Dashboard.hooks.ts  # 自定义 Hooks（200 行）
│       ├── Dashboard.styles.ts # 样式定义（150 行）
│       └── components/         # 子组件目录
│           ├── UserSection/
│           │   ├── index.tsx
│           │   ├── UserSection.tsx
│           │   ├── UserSection.types.ts
│           │   └── UserSection.styles.ts
│           ├── StatsSection/
│           └── ActivitySection/
```

---

### 准则三：依赖一并迁移

**迁移子模块时，该子组件使用到的函数和样式必须一并迁移到新文件中。**

#### 迁移检查清单

在拆分组件时，确保以下依赖完整迁移：

| 依赖类型 | 检查项 | 迁移目标 |
|---------|-------|---------|
| 类型定义 | Props、Interface、Type | `Component.types.ts` |
| 工具函数 | 数据处理、格式化、校验 | `Component.utils.ts` |
| 自定义 Hooks | useEffect、useState 等封装 | `Component.hooks.ts` |
| 样式定义 | CSS、Styled-components、Tailwind | `Component.styles.ts` 或 `.module.css` |
| 常量定义 | 枚举、配置项、魔法数字 | `Component.const.ts` |
| 子子组件 | 仅该组件使用的子组件 | `components/` 子目录 |

#### 迁移示例

```tsx
// ❌ 错误示例：拆分不彻底，依赖仍留在父组件中
// Dashboard.tsx
import { UserCard } from './components/UserCard';

// 这个函数应该跟随 UserCard 迁移
function formatUserName(user: User) {
  return `${user.firstName} ${user.lastName}`;
}

export default function Dashboard() {
  // ...
}

// ✅ 正确示例：依赖完整迁移
// Dashboard.tsx
import { UserCard } from './components/UserCard';

export default function Dashboard() {
  // 直接引用，无需关心实现细节
  return <UserCard user={user} />;
}

// components/UserCard/UserCard.tsx
import { formatUserName } from './UserCard.utils';  // 函数已迁移
import styles from './UserCard.module.css';          // 样式已迁移

export function UserCard({ user }: UserCardProps) {
  return <div className={styles.card}>{formatUserName(user)}</div>;
}

// components/UserCard/UserCard.utils.ts
export function formatUserName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}
```

---

### 准则四：积极创建组件

**前端开发必须经常创建新的组件模块，不要犹豫。**

#### 何时应该创建新组件

| 场景 | 示例 |
|-----|-----|
| 代码复用 | 同样的 JSX 结构在多处使用 |
| 逻辑复杂 | 某一部分有独立的状态管理和生命周期 |
| 文件膨胀 | 当前文件行数超过阈值 |
| 功能独立 | 可以独立开发、测试、部署的单元 |
| 团队协作 | 不同成员负责不同模块 |

#### 创建新组件的流程

```
发现可抽取的模块
    ↓
分析依赖关系（函数、样式、类型、子组件）
    ↓
创建组件目录和文件结构
    ↓
迁移代码和依赖到新组件
    ↓
在父组件中引用新组件
    ↓
验证功能完整性
```

#### 组件粒度参考

```tsx
// ❌ 过度拆分（ too granular ）
function ButtonText({ text }) {
  return <span>{text}</span>;
}

function ButtonIcon({ icon }) {
  return <i className={icon} />;
}

// ✅ 合理粒度
function Button({ text, icon, onClick }) {
  return (
    <button onClick={onClick}>
      {icon && <i className={icon} />}
      <span>{text}</span>
    </button>
  );
}

// ✅ 复杂组件拆分
function DataTable({ data, columns }) {
  return (
    <table>
      <TableHeader columns={columns} />
      <TableBody data={data} columns={columns} />
      <TableFooter data={data} />
    </table>
  );
}
```

---

## 收益

遵循以上准则，你将获得：

| 收益 | 说明 |
|-----|-----|
| **降低文件行数** | 单文件复杂度下降，易于阅读和维护 |
| **增强复用性** | 独立的组件可以在多处复用，减少重复代码 |
| **模块解耦** | 组件间依赖清晰，修改一个模块不会影响其他模块 |
| **提高健壮性** | 故障隔离，局部问题不会扩散到整个系统 |
| **便于协作** | 不同开发者可以并行开发不同模块 |
| **易于测试** | 独立的组件更容易编写单元测试 |

---

## 检查清单

在开发或重构前端代码时，使用以下清单进行自我检查：

### 代码审查前

- [ ] 单文件行数是否控制在 1000 行以内
- [ ] 组件逻辑和样式是否已分离
- [ ] 是否存在可复用的重复代码块
- [ ] 类型定义是否集中在 `.types.ts` 文件中
- [ ] 工具函数是否已抽取到 `.utils.ts` 文件中

### 拆分组件时

- [ ] 新组件是否有清晰的单一职责
- [ ] 子组件使用的类型定义是否一并迁移
- [ ] 子组件使用的工具函数是否一并迁移
- [ ] 子组件使用的样式是否一并迁移
- [ ] 子组件使用的自定义 Hooks 是否一并迁移
- [ ] 父组件是否正确引用了新组件

### 代码提交前

- [ ] 新创建的组件是否在适当位置有 index.ts 导出
- [ ] 组件的 Props 类型是否已正确定义
- [ ] 样式文件是否与组件在同一目录
- [ ] 是否存在循环依赖问题
