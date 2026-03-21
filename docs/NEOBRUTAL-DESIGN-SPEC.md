# TaskFolio Neobrutal Design Spec

## Overview

Transform TaskFolio from minimal zinc-gray aesthetic to bold neobrutalism while maintaining data clarity and accessibility.

**Neobrutalism characteristics:**
- Hard black borders (2px)
- Offset drop shadows (no blur)
- Bold, saturated colors
- High contrast typography
- Interactive feedback via shadow/translate animations
- Playful but functional

---

## Color Palette

### Core Colors
```css
:root {
  /* Base */
  --white: #ffffff;
  --black: #000000;
  
  /* Primary - AI/Tech Blue */
  --main: #88d4ee;
  --main-dark: #5bc0de;
  
  /* Background */
  --bg: #f0f8fc;
  --bg-alt: #e8f4fa;
  
  /* Risk Spectrum (exposure levels) */
  --danger: #ee8888;      /* High exposure (80%+) */
  --danger-dark: #dc6666;
  --warning: #fed170;     /* Medium exposure (40-79%) */
  --warning-dark: #f5b942;
  --success: #97ee88;     /* Low exposure (<40%) */
  --success-dark: #6bd65a;
  
  /* Accents */
  --purple: #b6ace4;      /* Future-proof index */
  --purple-dark: #9a8dd4;
}
```

### Usage Guidelines
| Element | Color |
|---------|-------|
| Page background | `--bg` |
| Cards/containers | `--white` |
| Primary actions | `--main` |
| High exposure | `--danger` |
| Medium exposure | `--warning` |
| Low exposure | `--success` |
| Future-proof badge | `--purple` |
| Text primary | `--black` |
| Text secondary | `#374151` (gray-700) |

---

## Typography

### Font Stack
```css
font-family: 'Public Sans', ui-sans-serif, system-ui, sans-serif;
```

### Scale
| Element | Size | Weight | Tracking |
|---------|------|--------|----------|
| H1 (page title) | 3rem / 48px | 800 (extrabold) | -0.025em |
| H2 (section) | 1.875rem / 30px | 700 (bold) | -0.025em |
| H3 (subsection) | 1.25rem / 20px | 700 (bold) | normal |
| Body | 1rem / 16px | 400 (normal) | normal |
| Small/caption | 0.875rem / 14px | 400 | normal |
| Badge text | 0.75rem / 12px | 700 (bold) | 0.025em |

### Neobrutalist Typography Rules
- Headlines: All uppercase optional for impact
- No subtle grays for important text
- High contrast always (min 4.5:1)

---

## Shadows & Borders

### Shadow System
```css
/* Standard brutal shadow */
--shadow-brutal: 4px 4px 0px 0px var(--black);

/* Small shadow (badges, small elements) */
--shadow-brutal-sm: 2px 2px 0px 0px var(--black);

/* Large shadow (hero cards) */
--shadow-brutal-lg: 6px 6px 0px 0px var(--black);

/* Colored shadows (for emphasis) */
--shadow-danger: 4px 4px 0px 0px var(--danger-dark);
--shadow-success: 4px 4px 0px 0px var(--success-dark);
```

### Border System
```css
/* Standard border */
border: 2px solid var(--black);

/* Radius */
--radius-base: 5px;
--radius-none: 0px;  /* For extra brutalist feel */
```

### Hover Animation
```css
/* Interactive elements translate on hover, shadow disappears */
.brutal-interactive {
  transition: transform 0.1s, box-shadow 0.1s;
}
.brutal-interactive:hover {
  transform: translate(2px, 2px);
  box-shadow: none;
}
.brutal-interactive:active {
  transform: translate(4px, 4px);
}
```

---

## Component Specifications

### 1. Card (Metric Cards)

**Current:**
```html
<div class="bg-white border border-zinc-200 rounded-xl p-5 shadow-lg">
```

**Neobrutal:**
```html
<div class="bg-white border-2 border-black rounded-[5px] p-5 shadow-brutal">
```

**Metric Card Layout:**
```
┌─────────────────────────────────────┐
│  ┌─────┐                    ┌─────┐ │
│  │SCORE│                    │BADGE│ │
│  │ 72  │                    │HIGH │ │
│  └─────┘                    └─────┘ │
│  AI Exposure Score                  │
│  ─────────────────────────────────  │
│  Description text here...           │
└─────────────────────────────────────┘
     ▓▓▓▓ (4px black shadow)
```

### 2. Badge

**Variants:**
```css
/* Danger badge */
.badge-danger {
  @apply bg-danger border-2 border-black text-black font-bold 
         px-3 py-1 rounded-[5px] shadow-brutal-sm;
}

/* Success badge */
.badge-success {
  @apply bg-success border-2 border-black text-black font-bold 
         px-3 py-1 rounded-[5px] shadow-brutal-sm;
}

/* Warning badge */
.badge-warning {
  @apply bg-warning border-2 border-black text-black font-bold 
         px-3 py-1 rounded-[5px] shadow-brutal-sm;
}
```

### 3. Button / Interactive Link

```css
.btn-brutal {
  @apply inline-flex items-center justify-center
         bg-main border-2 border-black rounded-[5px]
         px-4 py-2 font-bold text-black
         shadow-brutal
         hover:translate-x-[2px] hover:translate-y-[2px]
         hover:shadow-none
         transition-all duration-100
         focus-visible:outline-none focus-visible:ring-2 
         focus-visible:ring-black focus-visible:ring-offset-2;
}
```

### 4. Select / Dropdown

**Current:**
```html
<select class="rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-sm">
```

**Neobrutal:**
```html
<select class="rounded-[5px] border-2 border-black bg-white px-3 py-2 
               font-bold text-black shadow-brutal-sm
               focus:shadow-none focus:translate-x-[2px] focus:translate-y-[2px]">
```

### 5. Task Card (Timeline Items)

```
┌─────────────────────────────────────────────┐
│ ● Analyze business requirements             │
│   ──────────────────────────────────────    │
│   Automation: 65%  │  Augmentation: 25%     │
│   Speedup: 2.1x    │  Source: Anthropic     │
└─────────────────────────────────────────────┘
    ▓▓▓▓
```

### 6. Timeframe Section Headers

```css
.timeframe-header {
  @apply flex items-center gap-3 
         bg-danger/20 border-2 border-black rounded-[5px]
         px-4 py-2 font-bold;
}

/* Dot indicator */
.timeframe-dot {
  @apply w-4 h-4 rounded-full border-2 border-black;
}
```

**Color coding:**
| Timeframe | Background | Dot Color |
|-----------|------------|-----------|
| Now | `bg-danger/20` | `bg-danger` |
| 1-2y | `bg-warning/30` | `bg-warning` |
| 3-5y | `bg-warning/20` | `bg-warning` |
| 5-10y | `bg-main/20` | `bg-main` |
| 10y+ | `bg-success/20` | `bg-success` |

---

## Page-Specific Designs

### Home Page (Treemap)

**Header:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  TASKFOLIO                                           ┃
┃  See which tasks AI will automate — with timeframes  ┃
┃  ───────────────────────────────────────────────────  ┃
┃  361 Australian occupations • Click to explore       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Treemap Container:**
```
┌─────────────────────────────────────────────────────────┐
│ Australian Occupations           [Group by: ▼ Size]    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │                                                  │  │
│  │              TREEMAP SVG AREA                    │  │
│  │           (border-2 border-black)                │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Legend: [■ Low] [■ Med] [■ High] AI Impact            │
└─────────────────────────────────────────────────────────┘
    ▓▓▓▓▓▓
```

**Legend badges (inline):**
```html
<span class="inline-flex items-center gap-2 bg-success border-2 border-black 
             rounded-[5px] px-2 py-1 text-xs font-bold shadow-brutal-sm">
  Low AI Impact
</span>
```

### Occupation Detail Page

**Metric Cards Row:**
```
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│   AI EXPOSURE     │  │   HALF-LIFE       │  │  FUTURE-PROOF     │
│      72/100       │  │    5 years        │  │     42/100        │
│   ┌─────────┐     │  │        ⏳         │  │   ┌─────────┐     │
│   │  HIGH   │     │  │                   │  │   │AT RISK  │     │
│   └─────────┘     │  │                   │  │   └─────────┘     │
└───────────────────┘  └───────────────────┘  └───────────────────┘
    ▓▓▓▓                   ▓▓▓▓                   ▓▓▓▓
```

**Stats Row (smaller cards):**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Employment  │  │ Median Pay  │  │   Tasks     │  │   Source    │
│   51,500    │  │  $140,244   │  │     18      │  │ ABS+Anthro  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Treemap Customization

### Cell Styling
```javascript
// Treemap cells get brutalist treatment
cell.append('rect')
  .attr('stroke', '#000000')
  .attr('stroke-width', 2)
  .attr('rx', 5)  // rounded-base
  
// Colors remain risk-spectrum but more saturated
const colorScale = d3.scaleLinear()
  .domain([0, 0.4, 0.6, 0.8, 1])
  .range(['#97ee88', '#fed170', '#fed170', '#ee8888', '#ee8888'])
```

### Hover State
```javascript
.on('mouseenter', function() {
  d3.select(this)
    .attr('stroke-width', 3)
    .attr('transform', 'translate(-2, -2)')  // Inverse of brutal hover
})
```

---

## Dark Mode

**Approach:** Invert with care — keep brutal shadows visible.

```css
.dark {
  --bg: #1a1a2e;
  --white: #16213e;
  --black: #ffffff;
  --main: #5bc0de;
  --danger: #ff6b6b;
  --warning: #ffd93d;
  --success: #6bcb77;
  
  --shadow-brutal: 4px 4px 0px 0px rgba(255,255,255,0.3);
}
```

---

## Accessibility Considerations

1. **Color contrast:** All text meets WCAG AA (4.5:1 minimum)
2. **Focus indicators:** Black ring with white offset (high visibility)
3. **Motion:** Respect `prefers-reduced-motion`
4. **Touch targets:** Minimum 44x44px for interactive elements

```css
@media (prefers-reduced-motion: reduce) {
  .brutal-interactive {
    transition: none;
  }
  .brutal-interactive:hover {
    transform: none;
    box-shadow: none;
    outline: 3px solid var(--black);
  }
}
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Add CSS variables to globals.css
- [ ] Add Tailwind theme extensions
- [ ] Add utility classes (shadow-brutal, etc.)

### Phase 2: Components
- [ ] Update Card components (metric cards)
- [ ] Update Badge components
- [ ] Update Select dropdown
- [ ] Update Button/Link styles
- [ ] Update Task cards

### Phase 3: Page Layout
- [ ] Home page header
- [ ] Treemap container
- [ ] Legend styling
- [ ] Footer navigation

### Phase 4: Occupation Page
- [ ] Metric cards row
- [ ] Stats row
- [ ] Timeframe sections
- [ ] Task cards
- [ ] Breadcrumb navigation

### Phase 5: Polish
- [ ] Dark mode adjustments
- [ ] Motion preferences
- [ ] Final accessibility audit
- [ ] Cross-browser testing

---

## Reference Examples

**Before (Current):**
![Current minimal design with subtle shadows and borders]

**After (Neobrutal):**
```
┌────────────────────────────────────────┐
│  TASKFOLIO                             │
│  ══════════════════════════════════    │
│  ┌──────────────────────────────────┐  │
│  │    TREEMAP WITH BOLD BORDERS     │  │
│  └──────────────────────────────────┘  │
│      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     │
│                                        │
│  [■ Low] [■ Med] [■ High]              │
└────────────────────────────────────────┘
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

---

*Design spec v1.0 — TaskFolio Neobrutal Upgrade*
*Created: 2026-03-21*
