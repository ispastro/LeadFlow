# LeadFlow Chat Widget

Minimalist, professional chat widget for customer engagement.

## Development

```bash
npm install
npm run dev
```

Visit `http://localhost:5173` to see the widget in action.

## Build

```bash
npm run build
```

This creates `dist/widget.iife.js` and `dist/widget.css`.

## Installation (For Customers)

Add this code before the closing `</body>` tag:

```html
<script src="https://your-domain.com/widget.iife.js"></script>
<link rel="stylesheet" href="https://your-domain.com/widget.css">
<script>
  LeadFlowWidget.init({
    apiUrl: 'https://your-api-domain.com'
  });
</script>
```

## Features

- ✅ Clean, modern design
- ✅ Smooth animations
- ✅ Mobile responsive
- ✅ Typing indicators
- ✅ Auto-scroll
- ✅ Session management
- ✅ < 100KB total size
