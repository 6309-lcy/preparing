# UI redesign notes — SOA Grind

## Design intent
Shift from a dark, gamified look to a **premium professional study tool**: calm, spacious, and serious enough for actuarial candidates (Linear × Apple Health × high-end education).

## System
| Token | Value | Role |
|---|---|---|
| Canvas | `#F8FAFC` | Page background |
| Surface | `#FFFFFF` + soft shadow | Cards |
| Ink | `#0F172A` | Primary text |
| Mute | `#64748B` | Secondary text |
| Brand | `#0F766E` | Primary actions / progress |
| OK / Bad | `#059669` / `#DC2626` | Quiz feedback (restrained) |

- **Typography:** Inter + system-ui, tight tracking on titles, generous line-height on body.
- **Icons:** Lucide via CDN only (no AI illustrations).
- **CSS:** Tailwind Play CDN + lightweight `styles.css` for components and micro-interactions (200–350ms).

## Screens
1. **Today** — hero with progress ring, streak/XP pills, locked/unlocked quiz state, quick cards, quiet note.
2. **Learn** — stepped lesson cards (concept → example → why → check).
3. **Quiz** — PDF crop first, premium choice buttons, refined feedback, session complete screen.
4. **Wrong / Sunday** — scannable pool + recap actions.
5. **Stats** — dual rings, streak/XP/attempts, LO weakness bars.
6. **More** — account, notifications, export/import, reset.

## Motion
Hover lift on cards/buttons, smooth progress bars and SVG rings, toast slide-fade, modal blur backdrop, choice select transitions. No confetti, no cartoon animation.

## Compatibility
- `localStorage` key remains **`soa_grind_v1`** — existing progress, streaks, wrong pool preserved.
- Teach-first lock, 30% wrong-pool mix, Grok deep links, Firebase optional sync, PWA SW all retained.
- Question images under `data/qimg/` unchanged.

## Deploy
```bash
cd app && python -m http.server 8080
# GitHub Pages: copy app → docs as before
```

Hard-refresh after pull (`Ctrl+F5`) so service worker `soa-grind-v4` picks up the new shell.
