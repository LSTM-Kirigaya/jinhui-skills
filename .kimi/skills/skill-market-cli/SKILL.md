---
name: skill-market-upload
purpose: 指导 AI Agent 使用 skill-market-cli 将本地 SKILL 上传至 Skill Market，含用户案例与轨迹采集要求
tags:
  - skill-market
  - cli
  - upload
model: deepseek-chat
rootUrl: https://raw.githubusercontent.com/LSTM-Kirigaya/skill-market-cli/refs/heads/main/src/skills/skill-market-upload/SKILL.md
---

# Skill Market 上传助手（给 AI Agent 用）

本说明面向 **代表用户操作终端的 AI Agent**。目标：在已登录 `skill-market-cli` 的前提下，通过 **`skill-market-cli upload`** 完成上传，并满足服务端对 **AI 渠道** 的必填规则。

## 你必须知道的约束

1. **登录**：用户须先执行 `skill-market-cli login`（可用 `--mode development` 指向本地）。凭证在 `~/.skill-market-cli/config.json`。
2. **上传走 AI 渠道**：CLI 使用 `POST /api/skill/ai/upload`，要求 **全部字段非空**，且 **`tags`、`usageExamples` 不得为空数组**。
3. **用户案例（必填）**：`usageExamples` 中每一项必须包含：
   - **`prompt`**：终端用户会如何向该 Skill 提问（由用户或你根据上下文代写，但必须经用户确认）。
   - **`aiResponses`**：一次「示例运行」采集到的轨迹（thinking / toolcall / message）。上传命令会在本地 **自动调用采集逻辑** 生成（当前为可替换的模拟实现，结构需与后端一致）。
   - **`model`**：推荐模型名（如 `deepseek-chat`）。
4. **无法仅从文件推断的字段**：若 SKILL.md 未写全，上传流程会 **交互询问**：名称、描述、标签、`rootUrl`、推荐模型等。Agent 应结合仓库上下文、README、用户口述 **帮用户预填**，并在询问环节确认。

## 推荐工作流（Agent）

1. 确认仓库中存在 **`SKILL.md`**（目录则路径指向该目录）。
2. 读取 frontmatter，整理候选：`name`、`purpose`/`description`、`tags`、`model`、`rootUrl`。
3. 与用户确认 **至少一条「用户会如何提问」的测试案例**（可多轮补充）。案例文本即 `prompt`。
4. 在终端执行上传（勿省略路径）：
   ```bash
   skill-market-cli upload
   ```
5. 按 CLI 提示补全缺失字段；当提示采集轨迹时，**允许命令自动运行**（会调用内置采集器写入 `aiResponses`）。
6. 上传成功后，CLI 会在技能目录写入 **`.skill-examples.json`**，便于复查与再次上传。

## 与 `run-example` 的关系

- 可先运行 `skill-market-cli run-example <skill-dir>` 预采集，生成 `.skill-examples.json`；再执行 `upload` 时会 **自动合并** 该文件。
- 若未预先运行，`upload` 会引导用户 **逐条输入案例并自动采集轨迹**，无需用户手动拼 JSON。

## 禁止事项

- 不要编造不存在的 Git 仓库 URL；`rootUrl` 可用 `file:///...` 指向本地 `SKILL.md` 的绝对路径（CLI 默认值），或用户提供的 raw URL。
- 不要跳过「用户案例」；没有案例与轨迹，AI 渠道上传会失败。

## Usage Examples

### Example 1

**User:** 请根据我仓库里的 SKILL.md 帮我执行上传，并告诉我你要确认哪些字段。

**AI:** 我会先读取 `SKILL.md` 的 frontmatter，列出缺失的 name、描述、标签、模型与 rootUrl；请你至少提供一条「最终用户会对该 Skill 说的话」作为测试案例。然后我在终端运行 `skill-market-cli upload .`，在交互中替你填入并确认，自动完成轨迹采集后提交。
