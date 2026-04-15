# LeadFlow UI Design Preview

## 🎨 Chat Widget (Customer-Facing)

### Chat Bubble (Closed State)
```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│                              ┌────┐ │
│                              │ 💬 │ │ ← Blue circle (56px)
│                              └────┘ │   Hover: darker blue
│                                     │   Shadow: soft
└─────────────────────────────────────┘
```

### Chat Window (Open State)
```
┌──────────────────────────────────────┐
│ ┌──────────────────────────────────┐ │
│ │ 💬 AI Assistant        Online  ✕ │ │ ← Blue header
│ ├──────────────────────────────────┤ │
│ │                                  │ │
│ │  ┌─────────────────────────┐    │ │ ← AI message
│ │  │ Hi! How can I help you? │    │ │   (white bubble)
│ │  └─────────────────────────┘    │ │
│ │                                  │ │
│ │         ┌──────────────────┐    │ │ ← User message
│ │         │ What's pricing?  │    │ │   (blue bubble)
│ │         └──────────────────┘    │ │
│ │                                  │ │
│ │  ┌─────────────────────────┐    │ │
│ │  │ We have 3 plans:        │    │ │
│ │  │ - Starter: $49/month    │    │ │
│ │  │ - Pro: $149/month       │    │ │
│ │  └─────────────────────────┘    │ │
│ │                                  │ │
│ ├──────────────────────────────────┤ │
│ │ [Type your message...]      [→] │ │ ← Input area
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
  380px × 600px
  Rounded corners, soft shadow
```

## 🎨 Admin Dashboard (Internal)

### Sidebar Navigation
```
┌─────────────────┐
│  LeadFlow       │ ← Logo/Title
│  AI Sales Agent │
├─────────────────┤
│ 📊 Dashboard    │ ← Active (blue bg)
│ 👥 Leads        │
│ 💬 Conversations│
│ 📚 Knowledge    │
│ ⚙️  Settings    │
└─────────────────┘
  264px wide
  White background
```

### Dashboard Page
```
┌────────────────────────────────────────────────────────────┐
│ Dashboard                                                  │
│ Welcome back! Here's your overview.                        │
│                                                            │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│ │ Total Leads  │ │ Conversations│ │ Conversion   │      │
│ │     👥       │ │      💬      │ │ Rate   📈    │      │
│ │     42       │ │     156      │ │    26.9%     │      │
│ └──────────────┘ └──────────────┘ └──────────────┘      │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ System Status                                          ││
│ │                                                        ││
│ │ API Status        [✓ healthy]                         ││
│ │ Database          [✓ Connected]                       ││
│ │ AI Model          [✓ Active]                          ││
│ └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

### Leads Page
```
┌────────────────────────────────────────────────────────────┐
│ Leads                                    Total: 42         │
│ Manage your captured leads                                 │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ NAME          EMAIL              INTENT      CAPTURED  ││
│ ├────────────────────────────────────────────────────────┤│
│ │ John Doe      john@example.com   HIGH        Jan 15   ││
│ │ Jane Smith    jane@example.com   READY       Jan 14   ││
│ │ Bob Johnson   bob@example.com    MEDIUM      Jan 13   ││
│ └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

## 🎨 Color Palette

### Primary Colors
- **Blue**: `#2563eb` (buttons, active states)
- **Blue Hover**: `#1d4ed8`
- **Blue Light**: `#dbeafe` (backgrounds)

### Neutral Colors
- **White**: `#ffffff` (cards, backgrounds)
- **Gray 50**: `#f9fafb` (page background)
- **Gray 100**: `#f3f4f6` (hover states)
- **Gray 200**: `#e5e7eb` (borders)
- **Gray 600**: `#4b5563` (secondary text)
- **Gray 900**: `#111827` (primary text)

### Status Colors
- **Green**: `#10b981` (success, online)
- **Purple**: `#8b5cf6` (high priority)
- **Red**: `#ef4444` (errors)

## 🎨 Typography

- **Font Family**: System UI (native fonts)
- **Headings**: Bold, 24-32px
- **Body**: Regular, 14-16px
- **Small**: 12-14px

## 🎨 Spacing

- **Padding**: 16px, 24px, 32px
- **Gaps**: 8px, 16px, 24px
- **Border Radius**: 8px (small), 12px (medium), 16px (large)

## 🎨 Shadows

- **Small**: `0 1px 2px rgba(0,0,0,0.05)`
- **Medium**: `0 4px 6px rgba(0,0,0,0.1)`
- **Large**: `0 10px 15px rgba(0,0,0,0.1)`

## 🎨 Animations

- **Transitions**: 200ms ease
- **Hover**: Scale 1.02, brightness increase
- **Loading**: Bouncing dots (3 dots, staggered)

## 🎨 Design Principles

1. **Minimalism** - Only essential elements
2. **Whitespace** - Generous spacing
3. **Consistency** - Same patterns throughout
4. **Clarity** - Clear hierarchy and labels
5. **Speed** - Fast, smooth interactions
6. **Accessibility** - High contrast, semantic HTML

## 🎨 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

Widget and dashboard both adapt to screen size automatically.
