# LeadFlow Frontend

Minimalist, clean, and professional frontend for the AI Sales & Support Agent.

## Structure

```
frontend/
├── widget/       # Customer-facing chat widget (embeddable)
└── dashboard/    # Admin dashboard (internal)
```

## Quick Start

### 1. Chat Widget

```bash
cd widget
npm install
npm run dev
```

Visit `http://localhost:5173` to see the widget.

**Build for production:**
```bash
npm run build
```

### 2. Admin Dashboard

```bash
cd dashboard
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:3000` to see the dashboard.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool (fast, modern)
- **Tailwind CSS** - Utility-first styling
- **React Router** - Navigation (dashboard only)

## Design Philosophy

- ✅ **Minimalist** - Clean, uncluttered interfaces
- ✅ **Professional** - Modern, polished look
- ✅ **Fast** - Optimized bundle sizes
- ✅ **Responsive** - Works on all devices
- ✅ **Accessible** - Semantic HTML, ARIA labels

## Features

### Chat Widget
- Floating chat bubble
- Smooth animations
- Typing indicators
- Auto-scroll
- Session management
- < 100KB bundle size

### Admin Dashboard
- Overview dashboard with stats
- Lead management table
- System health monitoring
- Clean navigation
- Responsive design

## Integration

### Widget Integration (For Customers)

Add to your website:

```html
<script src="https://your-domain.com/widget.iife.js"></script>
<link rel="stylesheet" href="https://your-domain.com/widget.css">
<script>
  LeadFlowWidget.init({
    apiUrl: 'https://your-api-domain.com'
  });
</script>
```

## Next Steps

1. ✅ Widget and Dashboard created
2. 🔄 Test with backend API
3. 🔄 Add more dashboard features (conversations, knowledge base)
4. 🔄 Deploy to production
