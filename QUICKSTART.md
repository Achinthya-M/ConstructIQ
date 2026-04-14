# 🚀 BuildLedger - Quick Start Guide

## In 3 Minutes

### ⏱️ Step 1: Install (30 seconds)
```bash
pip install -r requirements.txt
```

### 📊 Step 2: Train Model (vary according to data size)
1. Open `model_training.ipynb`
2. Run all cells (Jupyter or VS Code)
3. Wait for model files: ✅ `model.pkl`, `vectorizer.pkl`, `model_name.pkl`

### 🔌 Step 3: Start Backend (5 seconds)
```bash
python app.py
```
Expected output:
```
🚀 BuildLedger AI Classifier Backend
============================================================
✅ Backend ready!
📍 API running at http://localhost:5000
```

### 🌐 Step 4: Open Frontend (10 seconds)
Open `index.html` in your browser
- You should see the **BuildLedger Dashboard**
- Navigation tabs: Dashboard, Add Expense, Expenses, Projects

### ✅ Done!
Start adding expenses and watch AI categorization work in real-time! 🤖

---

## What's Happening Behind the Scenes?

```
Your Browser
─────────────────────────────────────────────────
│ "50 bags of cement"                            │
│                ↓ (as you type)                 │
│ "🤖 Material (95%)" ← Live AI prediction       │
│                ↓ (click submit)                │
│ Expense saved to dashboard ✅                  │
─────────────────────────────────────────────────
         ↕ HTTP/JSON
Flask Backend (Python)
─────────────────────────────────────────────────
│ POST /api/predict                              │
│ ├─ Clean text                                  │
│ ├─ TF-IDF vectorize                            │
│ ├─ ML model predict                            │
│ └─ Return: category + confidence               │
─────────────────────────────────────────────────
```

---

## 💡 Key Features

### 🎯 Real-Time AI
- As you type, AI categorizes your expense live
- Shows confidence score (0-100%)
- Falls back to regex rules if API unavailable

### 📈 Dashboard
- KPI cards for each category (Material, Labor, etc.)
- Interactive chart of category breakdown
- Recent 5 transactions snapshot

### 📝 Smart Recording
- Project & location tracking
- Automatic data persistence (browser storage)
- Complete expense history

### 🤖 Powerful ML
- Trained on your construction data
- Highly accurate categorization
- Supports 5 expense categories

---

## 📂 File Guide

| File | Purpose |
|------|---------|
| `index.html` | Frontend dashboard |
| `model_training.ipynb` | Train ML model |
| `app.py` | Backend API server |
| `requirements.txt` | Install dependencies |
| `README.md` | Full documentation |
| `ARCHITECTURE.md` | Technical deep dive |
| `TROUBLESHOOTING.md` | Fix issues |

---

## 🆘 If Something Goes Wrong

### Error: "Model not found"
```bash
# Train the model first!
# Open model_training.ipynb and run all cells
```

### Error: "API connection refused"
```bash
# Start Flask backend
python app.py
```

### Error: "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

### Chart not showing or refresh issues
```
Press Ctrl+Shift+R to hard refresh browser
```

### Still stuck?
👉 See `TROUBLESHOOTING.md` for detailed solutions

---

## 🧪 Test Everything Works

Run the system test:
```bash
python test.py
```

Expected output:
```
✅ Frontend dashboard exists
✅ ML training notebook exists
✅ Backend API code exists
✅ All required packages installed
✅ All checks passed!
```

---

## 🎓 How to Use

### Adding an Expense

**1. Click "Add Expense" tab**

**2. Fill in the form:**
   - Project name (e.g., "Harbor View")
   - Location (e.g., "Chennai")
   - Description (e.g., "50 bags of cement for foundation")
   - Amount (e.g., 87500)
   - Date (auto-filled with today)

**3. Watch live AI prediction:**
   ```
   As you type description:
   ⏳ waiting... → 🔄 analyzing... → 🤖 Material (95%)
   ```

**4. Click "Register & Auto-categorize"**

**5. See success message:**
   ```
   ✅ Saved!
   🤖 AI Category: Material
   Confidence: 95% (AI)
   ```

**6. Go to Dashboard to see:**
   - KPI cards updated
   - Chart refreshed
   - Recent transactions list

---

## 🎨 Dashboard Views

### Dashboard Tab
- **KPI Cards** (6 cards): Material, Labor, Transport, Equipment, Subcontractor, Total
- **Chart**: Category breakdown visualization
- **Recent**: Last 5 transactions

### Add Expense Tab
- **Live Prediction**: Real-time AI as you type
- **Auto-Rules**: Keywords for each category
- **Form**: Project, Location, Description, Amount, Date

### Expenses Tab
- **Full Register**: All expenses with delete buttons
- **Sortable**: Date, Project, Location, Description, Category, Amount

### Projects Tab
- **Project Summary**: Per-project cost breakdown
- **Location**: Where each project is located
- **Entry Count**: Number of expenses per project

---

## 🔍 Understanding AI Predictions

### What does the model predict?

Given an expense description, it categorizes into:

| Category | Examples |
|----------|----------|
| **Material** | Cement, steel, bricks, paint, glass, wood |
| **Labor** | Wages, workers, electricians, plumbers, painters |
| **Transport** | Trucks, fuel, delivery, logistics, freight |
| **Equipment** | Excavators, cranes, rentals, machinery |
| **Subcontractor** | Plumbing, electrical, HVAC, painting, flooring |

### How accurate?

After training, typically **85-95%** accuracy on test data.

Improvements through:
1. More training data
2. Better feature engineering
3. Model selection (SVM usually best for text)
4. Hyperparameter tuning

---

## 🚀 Next Steps

### For Learning
- Read `ARCHITECTURE.md` to understand system design
- Check `model_training.ipynb` cells to see ML pipeline
- Review API responses in browser DevTools (F12)

### For Customization
- Add more categories by editing training data
- Adjust API URL: Edit `API_BASE_URL` in `index.html`
- Change model behavior: Modify `model_training.ipynb`

### For Production
- Deploy backend to cloud (AWS, GCP, Heroku)
- Host frontend on CDN (Vercel, Netlify)
- Add authentication & database
- See `ARCHITECTURE.md` for deployment patterns

---

## 📞 Support

1. **Quick Issues**: See `TROUBLESHOOTING.md`
2. **How It Works**: See `ARCHITECTURE.md`
3. **Full Guide**: See `README.md`
4. **Test System**: Run `python test.py`

---

## 🎉 Congratulations!

You now have a **production-ready AI-powered expense management system**!

Features you have:
- ✅ Real-time AI categorization
- ✅ Historical expense tracking
- ✅ Project-level analytics
- ✅ Beautiful interactive dashboard
- ✅ Fallback to regex if API down
- ✅ Mobile-responsive design
- ✅ Data persistence

**Start adding expenses and let the AI do the work!** 🤖

---

**Need help?** → Review TROUBLESHOOTING.md or README.md
**Want to learn more?** → Check ARCHITECTURE.md
**Something not working?** → Run `python test.py` to diagnose
