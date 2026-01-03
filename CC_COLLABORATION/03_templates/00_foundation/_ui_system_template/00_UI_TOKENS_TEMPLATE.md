# 00_UI_TOKENS.md
# UI 设计令牌

> 版本：v1.0
> 最后更新：{date}

---

## 1. 颜色系统

### 1.1 主色

| Token | 值 | 用途 |
|-------|-----|------|
| `--color-primary` | {value} | 主要操作、链接 |
| `--color-primary-light` | {value} | 悬停状态 |
| `--color-primary-dark` | {value} | 按下状态 |

### 1.2 语义色

| Token | 值 | 用途 |
|-------|-----|------|
| `--color-success` | {value} | 成功状态 |
| `--color-warning` | {value} | 警告状态 |
| `--color-danger` | {value} | 错误状态 |
| `--color-info` | {value} | 信息提示 |

### 1.3 中性色

| Token | 值 | 用途 |
|-------|-----|------|
| `--color-text-primary` | {value} | 主要文本 |
| `--color-text-secondary` | {value} | 次要文本 |
| `--color-text-disabled` | {value} | 禁用文本 |
| `--color-border` | {value} | 边框 |
| `--color-background` | {value} | 背景 |

---

## 2. 字体系统

### 2.1 字体族

```css
--font-family-base: {value};
--font-family-mono: {value};
```

### 2.2 字号

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-size-xs` | {value} | 辅助文本 |
| `--font-size-sm` | {value} | 次要文本 |
| `--font-size-base` | {value} | 正文 |
| `--font-size-lg` | {value} | 小标题 |
| `--font-size-xl` | {value} | 标题 |
| `--font-size-2xl` | {value} | 大标题 |

---

## 3. 间距系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--spacing-xs` | {value} | 极小间距 |
| `--spacing-sm` | {value} | 小间距 |
| `--spacing-md` | {value} | 中等间距 |
| `--spacing-lg` | {value} | 大间距 |
| `--spacing-xl` | {value} | 极大间距 |

---

## 4. 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | {value} | 小圆角 |
| `--radius-md` | {value} | 中等圆角 |
| `--radius-lg` | {value} | 大圆角 |
| `--radius-full` | 9999px | 全圆 |

---

## 5. 阴影

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | {value} | 轻微阴影 |
| `--shadow-md` | {value} | 中等阴影 |
| `--shadow-lg` | {value} | 强阴影 |

---

## 6. 过渡动画

```css
--transition-fast: 150ms ease;
--transition-base: 250ms ease;
--transition-slow: 350ms ease;
```

---

_从 00_UI_TOKENS_TEMPLATE.md 生成_
