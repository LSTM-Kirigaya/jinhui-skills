---
name: build-test-suite
description: 构建软件测试集的指南。Use when creating or improving test coverage for software projects for: (1) Setting up test infrastructure for backend APIs and services, (2) Designing test cases with idempotency guarantees, (3) Selecting appropriate testing frameworks for the current tech stack, (4) Maintaining test quality across long-term iterations, (5) Running full test suites before commits. Must follow the 5 golden rules: user approval before creation, test idempotency, pre-commit validation, no modification of existing tests, backend-first execution order.
---

# 构建软件测试集

软件测试集的构建指南。构建测试集是为了维持软件在长期迭代中的稳定性，是保障代码质量的必要过程。

---

## 核心原则

> **测试集是长期迭代的保护伞，而非一次性任务。**

构建测试集的首要目标是保证后端功能的正确性，其次才是前端测试。

---

## 测试集类型

| 类型 | 优先级 | 说明 | 相关 Skill |
|-----|-------|------|-----------|
| **后端功能测试** | P0（优先） | 测试 API、Service、Database 操作等 | - |
| **前端测试** | P1 | 测试 UI 交互、页面流程 | [web-devtools](../web-devtools/SKILL.md)、[weapp-devtools](../weapp-devtools/SKILL.md) |

---

## 构建流程

### 第一步：分析后端代码

1. 扫描项目中的所有后端代码文件
2. 识别核心业务逻辑（API 接口、Service 层、关键函数）
3. 搜索当前技术栈的主流测试框架
4. 整理需要测试的模块列表

### 第二步：设计方案（用户确认）

**⚠️ 重要：在用户确认前，禁止直接创建测试文件。**

以表格形式输出测试集设计方案：

| 模块 | 测试点 | 测试框架 | 优先级 | 预估工作量 |
|-----|-------|---------|-------|-----------|
| UserService | CRUD 操作 | Jest | P0 | 2h |
| Auth API | 登录/鉴权 | Jest + supertest | P0 | 3h |
| ... | ... | ... | ... | ... |

等待用户确认或修改方案后，方可进入实施阶段。

### 第三步：选择测试框架

**操作步骤：**

1. **分析技术栈**：扫描项目代码，识别当前使用的后端技术栈（如 Node.js、Python、Go、Java、Rust 等）
2. **网络搜索**：针对识别出的技术栈，搜索网络获取该领域成熟的测试框架
   - 搜索关键词："{技术栈} testing framework 2024"、"{技术栈} best test framework"
   - 关注：社区活跃度、GitHub stars、官方推荐、与当前项目匹配度
3. **评估选择**：综合考虑以下因素选择最合适的框架
   - 与现有技术栈的兼容性
   - 学习成本
   - 社区支持和文档完善度
   - 是否支持所需的测试类型（单元、集成、覆盖率等）

### 第四步：实施构建

按照确认的测试集方案，逐步实现测试代码。

---

## 五大准则

### 准则一：用户确认制

- **禁止行为**：未经用户确认，直接创建测试文件
- **正确流程**：
  1. 分析后端代码
  2. 整理测试集方案（表格形式）
  3. 提交给用户确认
  4. 用户同意后方可构建

### 准则二：幂等性保证

> **无论运行多少次测试，系统状态必须保持一致。**

- **查询操作**：天然幂等，无需特殊处理
- **数据变更操作**：必须配套清理逻辑

```javascript
// ✅ 正确示例：测试后清理数据
it('should create user', async () => {
  const user = await createUser({ name: 'Test' });
  expect(user.name).toBe('Test');
  
  // 测试结束后删除
  await deleteUser(user.id);
});

// ✅ 或使用 beforeEach/afterEach
beforeEach(async () => {
  await db.clean();  // 清理测试数据
});
```

### 准则三：提交前必测

- **触发时机**：
  - 准备提交代码到 GitHub 时
  - 用户要求提交时
  
- **执行流程**：
  1. 运行全部测试文件
  2. 如有失败，分析错误信息
  3. 修改代码直至全部通过
  4. 方可提交

### 准则四：测试文件不可随意修改

- **禁止行为**：修改已写好的测试文件
- **例外情况**：
  - 用户明确要求修改
  - 情况紧急（大量测试未建立，需要调整策略）

> **理由**：测试文件是功能的契约，随意修改会降低测试可信度。

### 准则五：执行顺序

**必须遵循：后端测试 → 前端测试**

1. 先运行所有后端测试
2. 确认后端测试全部通过
3. 再运行前端测试
4. 确保开发环境本身无问题

---

## 前端测试引用

前端测试可借助以下 Skill 完成：

- **网站调试**：`../web-devtools/SKILL.md`
  - UI 自动化测试
  - 截图对比
  - 表单交互测试

- **小程序调试**：`../weapp-devtools/SKILL.md`
  - 小程序自动化测试
  - 页面导航测试
  - 网络 Mock 测试

---

## 测试集检查清单

- [ ] 是否已获取用户对方案的确认
- [ ] 所有测试是否满足幂等性
- [ ] 数据变更操作是否有配套清理
- [ ] 提交前是否已运行全部测试
- [ ] 后端测试是否先于前端测试运行
- [ ] 测试框架是否与当前技术栈匹配
