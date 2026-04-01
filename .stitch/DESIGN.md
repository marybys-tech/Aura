# Aura Design System

## 1. Visual Identity
Aura is a gamified habit tracker with a mystical, ethereal aesthetic. The design feels modern, sleek, and slightly magical — like a living organism tracking your growth.

## 2. Color Palette (Soft Neon)
| Category | Color | Glow | Usage |
|----------|-------|------|-------|
| Intelligence | #A78BFA | #C4B5FD | Primary accent, violet |
| Stamina | #34D399 | #6EE7B7 | Emerald green |
| Sociality | #FBBF24 | #FDE68A | Warm amber |
| Creativity | #FB923C | #FDBA74 | Soft orange |
| Discipline | #38BDF8 | #7DD3FC | Sky blue |
| Wellness | #F472B6 | #F9A8D4 | Soft pink |

### Dark Theme (default)
- **Background**: #0F0F1A (deep purple-black, with subtle gradient overlays)
- **Surface**: #1A1A2E (cards, panels)
- **Surface elevated**: #252540 (dropdowns, modals)
- **Text primary**: #F1F1F6
- **Text secondary**: #9CA3AF
- **Border**: rgba(255, 255, 255, 0.08)
- **Aura canvas bg**: #0F0F1A (pure dark for max contrast with glowing aura)

### Light Theme
- **Background**: #F8F7FC (warm off-white with faint violet tint)
- **Surface**: #FFFFFF (clean white cards)
- **Surface elevated**: #F0EEF6 (light lavender for dropdowns, modals)
- **Text primary**: #1A1A2E (dark navy)
- **Text secondary**: #6B7280 (medium gray)
- **Border**: rgba(0, 0, 0, 0.08)
- **Aura canvas bg**: #EEEAF6 (soft lavender for aura contrast — aura colors stay vivid)
- **Category colors stay the same** — soft neon works on both light and dark
- **Glow effects are reduced** in light mode — category colors are used at full saturation without outer glow, subtle inner shadows instead of glowing borders
- **Glass-morphism becomes subtle shadows** — cards use white bg with soft drop shadows instead of translucent dark bg

## 3. Typography
- **Headlines**: Space Grotesk (bold, modern geometric)
- **Body/Labels**: Inter (clean, readable)

## 4. Design Principles
- Dark backgrounds with subtle purple-tinted gradients
- Soft neon glowing accents — vibrant but never harsh
- Glass-morphism cards (translucent bg, soft borders, subtle backdrop blur)
- Generous spacing (16-24px padding on cards)
- Rounded corners (12px)
- Category colors as consistent visual identifiers (badges, progress bars, card accents)
- Mobile-first responsive layout
- Ethereal, alive feel — nothing static or rigid

## 5. Component Patterns

### Dark Theme
- **Cards**: dark translucent background, 1px border with category color at low opacity, rounded-xl
- **Buttons**: filled with category color, soft glow on hover
- **Progress bars**: gradient fill using category color → glow color
- **Badges**: small pill shapes with category color background at 20% opacity, text in category color

### Light Theme
- **Cards**: white background, soft drop shadow (0 2px 8px rgba(0,0,0,0.06)), rounded-xl
- **Buttons**: filled with category color (same as dark), no outer glow, subtle hover darken
- **Progress bars**: same gradient fill — colors pop on white background
- **Badges**: category color background at 12% opacity, text in category color (slightly darker)

### Both Themes
- **Navigation**: sidebar on desktop, bottom nav on mobile
- **Theme toggle**: sun/moon icon in header, persisted in localStorage

## 6. Design System Notes for Stitch Generation

**DESIGN SYSTEM:**
- Color mode: DARK with deep purple-black backgrounds (#0F0F1A)
- Primary color: #A78BFA (soft neon violet)
- Secondary: #34D399 (soft neon emerald)
- Tertiary: #F472B6 (soft neon pink)
- Additional category colors: #FBBF24 (amber), #FB923C (orange), #38BDF8 (sky blue)
- Font: Space Grotesk for headlines, Inter for body text
- Roundness: 12px corners
- Style: Glass-morphism cards with translucent backgrounds, soft neon glow accents, ethereal and modern
- Layout: Mobile-first, generous spacing, clean hierarchy
- Feel: Mystical, game-like, alive — like a character stats screen from an RPG
