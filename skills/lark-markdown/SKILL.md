---
name: lark-markdown
description: >
  Build and send Feishu (Lark) interactive rich-text cards using lark_md format.
  Use when the user needs to: (1) construct Feishu card messages with markdown support,
  (2) send interactive cards via the Feishu Bot API, (3) format text with bold, inline code,
  lists, tables, or code blocks inside Feishu cards, or (4) convert markdown content into
  Feishu card elements.
---

# Feishu Lark MD Card Skill

## Lark MD Format

In Feishu interactive cards, use `tag: 'lark_md'` to render Markdown inline formatting inside text elements. Use `tag: 'plain_text'` for unformatted text.

### Supported Syntax in `lark_md`

| Syntax | Example | Rendered |
|--------|---------|----------|
| Bold | `**text**` | **text** |
| Italic | `*text*` | *text* |
| Inline code | `` `code` `` | `code` |
| Strikethrough | `~~text~~` | ~~text~~ |
| Link | `[title](url)` | link |
| Line break | `  \n` or `\n\n` | new line |
| Emoji | raw Unicode | ✅ |

**Important:** Block-level elements (headings, code blocks, tables, lists) are **not** supported inside `lark_md`. Use dedicated card elements for those.

## Card Structure

```typescript
const card = {
  config: { wide_screen_mode: true, enable_forward: true },
  header: {
    title: { tag: 'plain_text', content: 'Card Title' },
    subtitle: { tag: 'plain_text', content: 'Optional subtitle' },
    template: 'green', // green | red | blue | grey | wathet | yellow | orange | purple | carmine
  },
  elements: [
    // see element types below
  ],
};
```

Send with:

```typescript
await client.im.v1.message.create({
  params: { receive_id_type: 'open_id' },
  data: {
    receive_id: receiveId,
    msg_type: 'interactive',
    content: JSON.stringify(card),
  },
});
```

## Element Types

### Text Block

```typescript
{
  tag: 'div',
  text: { tag: 'lark_md', content: '**Bold** and `inline code`' },
}
```

### Multi-column Fields

```typescript
{
  tag: 'div',
  fields: [
    { is_short: true, text: { tag: 'lark_md', content: '**Label**\nValue' } },
    { is_short: true, text: { tag: 'lark_md', content: '**Label**\nValue' } },
  ],
}
```

### Code Block with Syntax Highlighting

Use `tag: 'markdown'` (not `lark_md`) for code blocks to get Feishu syntax highlighting:

```typescript
{
  tag: 'markdown',
  content: '```typescript\nconst x = 1;\n```',
}
```

Supported languages: `javascript`, `typescript`, `python`, `bash`, `json`, `html`, `css`, `go`, `rust`, `java`, `cpp`, `csharp`, `kotlin`, `ruby`, `yaml`, `markdown`, `sql`, `xml`, `php`. Aliases like `js`/`ts`/`py`/`sh`/`yml` are accepted; normalize them if needed.

### Horizontal Rule

```typescript
{ tag: 'hr' }
```

### Quote / Note

```typescript
{
  tag: 'note',
  elements: [
    { tag: 'plain_text', content: 'Quoted text' },
  ],
}
```

### Table (via column_set)

```typescript
{
  tag: 'column_set',
  flex_mode: 'stretch',
  background_style: 'grey',
  columns: [
    {
      tag: 'column',
      width: 'weighted',
      weight: 1,
      elements: [
        { tag: 'div', text: { tag: 'lark_md', content: 'Header 1' } },
        { tag: 'div', text: { tag: 'lark_md', content: 'Row 1 Col 1' } },
        { tag: 'div', text: { tag: 'lark_md', content: 'Row 2 Col 1' } },
      ],
    },
    {
      tag: 'column',
      width: 'weighted',
      weight: 1,
      elements: [
        { tag: 'div', text: { tag: 'lark_md', content: 'Header 2' } },
        { tag: 'div', text: { tag: 'lark_md', content: 'Row 1 Col 2' } },
        { tag: 'div', text: { tag: 'lark_md', content: 'Row 2 Col 2' } },
      ],
    },
  ],
}
```

### List Items

Render as multiple `div` elements with `•` prefix:

```typescript
{ tag: 'div', text: { tag: 'lark_md', content: '• First item' } },
{ tag: 'div', text: { tag: 'lark_md', content: '• Second item' } },
```

### Form & Action (Interactive)

```typescript
// Input
{
  tag: 'input',
  placeholder: { tag: 'plain_text', content: 'Enter path...' },
  name: 'path_input',
  required: true,
}

// Button
{
  tag: 'button',
  text: { tag: 'plain_text', content: 'Submit' },
  type: 'primary', // primary | default | danger
  value: { action: 'submit_form' },
}
```

Wrap buttons in an `action` element:

```typescript
{
  tag: 'action',
  actions: [
    { tag: 'button', text: { tag: 'plain_text', content: 'OK' }, type: 'primary', value: { action: 'ok' } },
    { tag: 'button', text: { tag: 'plain_text', content: 'Cancel' }, type: 'default', value: { action: 'cancel' } },
  ],
}
```

## Converting Markdown to Card Elements

When converting user-provided Markdown into card elements, map block-level syntax as follows:

| Markdown | Card Element |
|----------|-------------|
| `# Title` | `div` with `plain_text` |
| `## Title` | `div` with `plain_text` |
| `### Title` | `div` with `plain_text` |
| `` ```lang\ncode\n``` `` | `markdown` tag with fenced code |
| `\| col1 \| col2 \|` | `column_set` with `column` per column |
| `- item` / `* item` | `div` with `lark_md` and `• ` prefix |
| `> quote` | `note` element |
| `---` / `***` | `hr` |
| paragraph | `div` with `lark_md` |

## Minimal Example

```typescript
import * as lark from '@larksuiteoapi/node-sdk';

const client = new lark.Client({
  appId: process.env.FEISHU_APP_ID!,
  appSecret: process.env.FEISHU_APP_SECRET!,
  appType: lark.AppType.SelfBuild,
});

const card = {
  config: { wide_screen_mode: true },
  header: {
    template: 'green',
    title: { tag: 'plain_text', content: 'Reply' },
  },
  elements: [
    {
      tag: 'div',
      text: { tag: 'lark_md', content: '**Hello** from `lark_md`!' },
    },
    { tag: 'hr' },
    {
      tag: 'markdown',
      content: '```typescript\nconsole.log("hi");\n```',
    },
  ],
};

await client.im.v1.message.create({
  params: { receive_id_type: 'open_id' },
  data: {
    receive_id: userOpenId,
    msg_type: 'interactive',
    content: JSON.stringify(card),
  },
});
```
