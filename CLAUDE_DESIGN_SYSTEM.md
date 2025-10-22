# 🎨 Claude Anthropic Inspired Design System

## Overview
This document outlines the design system inspired by Claude (Anthropic), featuring warm, minimal aesthetics with excellent typography and thoughtful spacing.

---

## 🎯 Design Philosophy

### Core Principles
1. **Warmth over coldness** - Beige/cream tones instead of stark whites
2. **Clarity over decoration** - Minimal, functional design
3. **Readability first** - Excellent typography hierarchy
4. **Subtle interactions** - Smooth, natural transitions
5. **Professional yet approachable** - Balanced formality

---

## 🎨 Color Palette

### Primary Colors
```css
Background:        #F5F3EE  /* Warm beige cream */
Surface:           #FFFFFF  /* Pure white for cards */
Surface Hover:     #FAFAF8  /* Subtle hover state */
```

### Text Colors
```css
Primary Text:      #2D2A26  /* Warm dark brown */
Secondary Text:    #6B6662  /* Medium gray-brown */
Border:            #D4CFC7  /* Light warm gray */
Border Hover:      #A39D94  /* Medium warm gray */
Border Subtle:     #E8E4DD  /* Very light warm gray */
```

### Accent Colors
```css
Accent Primary:    #D97706  /* Warm amber/orange */
Accent Dark:       #1A1917  /* Almost black */
Button Primary:    #2D2A26  /* Warm dark brown */
Button Hover:      #1A1917  /* Darker brown */
```

### States
```css
Success:           #059669  /* Green */
Warning:           #D97706  /* Amber */
Error:             #DC2626  /* Red */
Live Indicator:    #D97706  /* Amber dot */
```

---

## 📝 Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
```

### Font Sizes & Weights
```css
/* Headings */
H1:               32px, 600 weight, -0.5px letter-spacing
H2:               24px, 600 weight, -0.3px letter-spacing
H3:               18px, 600 weight

/* Body */
Body Text:        16px, 400 weight
Small Text:       13px, 400 weight
Micro Text:       12px, 500 weight

/* Special */
Display Numbers:  72px, 600 weight, -2px letter-spacing
Labels:           12px, 500 weight, 1px letter-spacing (uppercase)
```

---

## 📦 Components

### Buttons

#### Primary Button
```css
background: #2D2A26
color: #F5F3EE
border: 1.5px solid #2D2A26
border-radius: 8px
padding: 14px 40px
font-size: 15px
font-weight: 500
box-shadow: 0 2px 8px rgba(45, 42, 38, 0.1)

/* Hover */
background: #1A1917
box-shadow: 0 4px 12px rgba(45, 42, 38, 0.15)
transform: translateY(-1px)
```

#### Secondary Button
```css
background: #FFFFFF
color: #2D2A26
border: 1.5px solid #D4CFC7
border-radius: 8px
padding: 12px 24px
font-size: 15px
font-weight: 500

/* Hover */
background: #FAFAF8
border-color: #A39D94
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08)
transform: translateY(-1px)
```

#### Active Button
```css
background: #2D2A26
color: #F5F3EE
border-color: #2D2A26
box-shadow: 0 2px 12px rgba(45, 42, 38, 0.15)
```

### Cards

#### Default Card
```css
background: #FFFFFF
border: 1px solid #E8E4DD
border-radius: 12px
padding: 24px 32px
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1)
```

#### Overlay Card (on video)
```css
background: rgba(255, 255, 255, 0.95)
backdrop-filter: blur(12px)
border: 1px solid rgba(212, 207, 199, 0.6)
border-radius: 12px
padding: 24px 32px
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1)
```

### Upload Section
```css
background: #FFFFFF
border: 1.5px dashed #D4CFC7
border-radius: 12px
padding: 32px

/* Hover */
background: #FAFAF8
border-color: #A39D94
```

### Stats Bar
```css
background: rgba(255, 255, 255, 0.95)
backdrop-filter: blur(12px)
border-top: 1px solid rgba(212, 207, 199, 0.6)
padding: 16px 24px
```

---

## 🎭 Spacing System

### Base Unit: 4px

```css
4px   = 0.25rem  /* Tiny */
8px   = 0.5rem   /* Extra small */
12px  = 0.75rem  /* Small */
16px  = 1rem     /* Medium */
20px  = 1.25rem  /* Medium-large */
24px  = 1.5rem   /* Large */
32px  = 2rem     /* Extra large */
40px  = 2.5rem   /* XX-large */
48px  = 3rem     /* XXX-large */
```

### Common Patterns
```css
/* Padding */
Button:           12-14px vertical, 24-40px horizontal
Card:             24-32px all sides
Section:          32px all sides

/* Margins */
Between sections: 24-32px
Between elements: 12-16px
Between buttons:  12px
```

---

## 🌊 Transitions & Animations

### Standard Transition
```css
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
```

### Hover Transform
```css
transform: translateY(-1px);
```

### Slide In
```css
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

### Fade In
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### Blink (Live indicator)
```css
@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0.4; }
}
animation: blink 2s infinite;
```

---

## 📐 Borders & Shadows

### Border Radius
```css
Small:    6px
Medium:   8px
Large:    12px
XL:       16px
```

### Shadows
```css
/* Subtle */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

/* Default */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

/* Lifted */
box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);

/* Hover */
box-shadow: 0 4px 12px rgba(45, 42, 38, 0.15);
```

---

## 🎯 Component States

### Default
- Neutral colors
- Standard border
- No transform

### Hover
- Slightly darker/lighter background
- Darker border
- Lifted shadow
- `translateY(-1px)`

### Active/Selected
- Primary color background
- Primary color border
- Stronger shadow

### Disabled
- `opacity: 0.4`
- `cursor: not-allowed`
- No hover effects

### Focus
- 2px outline with primary color
- Subtle glow effect

---

## 📱 Responsive Breakpoints

```css
Mobile:      < 640px
Tablet:      640px - 1024px
Desktop:     > 1024px
Large:       > 1440px
```

### Responsive Padding
```css
/* Mobile */
padding: 16px;

/* Tablet+ */
padding: 20px;

/* Desktop+ */
padding: 32px;
```

---

## ✨ Special Elements

### Counter Display
```css
font-size: 72px
font-weight: 600
color: #2D2A26
letter-spacing: -2px

/* When live */
color: #D97706
```

### Labels (uppercase)
```css
font-size: 12px
font-weight: 500
color: #6B6662
letter-spacing: 1px
text-transform: uppercase
```

### Live Indicator
```css
/* Dot before text */
content: "● "
color: #D97706
animation: blink 2s infinite
```

---

## 🎨 Implementation Examples

### Example 1: Primary Button
```html
<button class="primary-btn">
    Start Analysis
</button>

<style>
.primary-btn {
    background: #2D2A26;
    color: #F5F3EE;
    border: 1.5px solid #2D2A26;
    border-radius: 8px;
    padding: 14px 40px;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(45, 42, 38, 0.1);
}

.primary-btn:hover {
    background: #1A1917;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45, 42, 38, 0.15);
}
</style>
```

### Example 2: Card
```html
<div class="card">
    <h3>Detection Results</h3>
    <p>Analysis complete with 5 detections</p>
</div>

<style>
.card {
    background: #FFFFFF;
    border: 1px solid #E8E4DD;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.card h3 {
    font-size: 18px;
    font-weight: 600;
    color: #2D2A26;
    margin-bottom: 8px;
}

.card p {
    font-size: 14px;
    color: #6B6662;
}
</style>
```

### Example 3: Stat Display
```html
<div class="stat">
    Frame: <span class="stat-value">5</span>/10
</div>

<style>
.stat {
    color: #2D2A26;
    font-size: 13px;
}

.stat-value {
    font-weight: 600;
    color: #D97706;
    margin-left: 6px;
}
</style>
```

---

## 🔍 Accessibility

### Contrast Ratios
- Text on #F5F3EE background: 14:1 (AAA)
- Text on #FFFFFF background: 16:1 (AAA)
- Accent color: 4.5:1 minimum (AA)

### Focus States
- Visible focus indicators
- Keyboard navigation support
- ARIA labels where needed

### Color Blindness
- Don't rely solely on color
- Use icons and labels
- Test with color blindness simulators

---

## 📚 Resources

### Inspiration
- Claude.ai interface
- Anthropic website
- Modern minimalist design

### Tools
- Figma for design
- CSS custom properties for theming
- System fonts for performance

### Testing
- Chrome DevTools
- Lighthouse accessibility
- Multiple devices

---

## 🎯 Usage Guidelines

### DO
✅ Use warm beige/cream backgrounds  
✅ Maintain generous spacing  
✅ Use subtle shadows and borders  
✅ Keep typography clean and readable  
✅ Use smooth, natural transitions  

### DON'T
❌ Use bright, neon colors  
❌ Overcrowd the interface  
❌ Use heavy shadows  
❌ Mix too many font weights  
❌ Add unnecessary animations  

---

## 🚀 Quick Start

To apply Claude aesthetic to a new component:

1. **Colors**: Start with `#F5F3EE` background, `#FFFFFF` cards
2. **Text**: Use `#2D2A26` for primary, `#6B6662` for secondary
3. **Borders**: `1.5px solid #D4CFC7`, `8px` border-radius
4. **Shadows**: `0 4px 16px rgba(0, 0, 0, 0.1)`
5. **Transitions**: `0.2s cubic-bezier(0.4, 0, 0.2, 1)`
6. **Spacing**: Use 8px grid (8, 16, 24, 32)
7. **Typography**: System fonts, 600 weight for headings

---

## 📝 Changelog

**v1.0.0** (2025-10-23)
- Initial Claude-inspired design system
- Complete color palette
- Typography scale
- Component library
- Animation system

---

**Design System by StreamBet**  
Inspired by Claude (Anthropic) · 2025
