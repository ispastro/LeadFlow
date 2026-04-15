# Quick Start Guide

## Test Everything in 5 Minutes

### Step 1: Start Backend (Terminal 1)
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

Wait for: `✅ Model loaded successfully!`

### Step 2: Start Chat Widget (Terminal 2)
```bash
cd frontend/widget
npm install  # First time only
npm run dev
```

Visit: `http://localhost:5173`

### Step 3: Start Dashboard (Terminal 3)
```bash
cd frontend/dashboard
npm install  # First time only
npm run dev
```

Visit: `http://localhost:3000`

## Test the Flow

1. **Open Widget** (`http://localhost:5173`)
   - Click the blue chat bubble
   - Ask: "What are your pricing plans?"
   - Should see: $49/month and $149/month

2. **Check Dashboard** (`http://localhost:3000`)
   - View stats on homepage
   - Click "Leads" to see captured leads

3. **Test Lead Capture**
   - In widget, continue conversation
   - Provide email when asked
   - Check dashboard - new lead should appear

## Expected Results

✅ Widget loads with chat bubble
✅ Chat opens smoothly
✅ AI responds with correct pricing
✅ Dashboard shows stats
✅ Leads appear in table

## Troubleshooting

**Widget can't connect to API?**
- Check backend is running on port 8000
- Check CORS is enabled in backend

**Dashboard shows no data?**
- Check API URL in dashboard/.env
- Verify backend /api/leads endpoint works

**AI gives wrong answers?**
- Check backend terminal for context retrieval
- Verify knowledge base has data: `python scripts/test_rag_debug.py`

## Production Checklist

- [ ] Update API URLs in widget and dashboard
- [ ] Add your business knowledge to ingest_knowledge.py
- [ ] Customize widget colors/branding
- [ ] Set up error tracking
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Test end-to-end

🎉 Enjoy your AI Sales Agent!
