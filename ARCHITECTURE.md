# BuildLedger System Architecture & Implementation Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            index.html (Frontend)                     │  │
│  │  - Dashboard with KPI cards                          │  │
│  │  - Add Expense form with Live AI                     │  │
│  │  - Expense register & projects view                  │  │
│  │  - JavaScript API integration                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↕ HTTP/REST (JSON)
┌─────────────────────────────────────────────────────────────┐
│              Flask Backend API (Python)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  app.py - REST Endpoints                              │ │
│  │  - GET  /api/health                                   │ │
│  │  - POST /api/predict (single prediction)              │ │
│  │  - POST /api/batch-predict (multiple)                 │ │
│  │  - GET  /api/categories                               │ │
│  │  - GET  /api/model-info                               │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ML Model Pipeline                                     │ │
│  │  - Text preprocessing (clean_text)                     │ │
│  │  - TF-IDF vectorization (vectorizer.pkl)               │ │
│  │  - Prediction (model.pkl)                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         ↕ Joblib files
┌─────────────────────────────────────────────────────────────┐
│            Machine Learning Model                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  model_training.ipynb - Training Pipeline              │ │
│  │  - Data loading & cleaning                             │ │
│  │  - Feature engineering (TF-IDF)                        │ │
│  │  - Model training (3 algorithms)                       │ │
│  │  - Best model selection                                │ │
│  │  - Hyperparameter tuning                               │ │
│  │  - Model & vectorizer serialization                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 1. Frontend Layer (index.html)

### Key Components

#### API Integration
```javascript
const API_BASE_URL = 'http://localhost:5000/api';

// Async prediction with fallback
async function smartCategory(desc, proj, location) {
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: desc, project_name: proj, location })
        });
        
        if (response.ok) {
            const data = await response.json();
            return {
                category: data.category,
                confidence: data.confidence,
                method: 'AI'
            };
        }
    } catch (err) {
        // Fallback to regex if API fails
    }
    return { category: fallbackSmartCategory(desc, proj), confidence: 0.7, method: 'Regex' };
}
```

#### Live Prediction During Input
- As user types in description/project fields
- `updateLive()` function is called
- Displays 🤖 icon for AI predictions or 📋 for fallback
- Shows confidence percentage
- Updates in real-time with debouncing

#### Data Persistence
- LocalStorage: `buildLedgerData` key stores all expenses
- JSON serialization for storing/loading
- Automatic save after every operation

### User Flow

```
User Enters Expense Details
    ↓
Live AI Prediction (typing)
    ↓
Form Submission
    ↓
Backend Classification (API)
    ↓
Store in LocalStorage
    ↓
Update Dashboard & Tables
```

## 2. Backend API Layer (app.py)

### Flask Application Structure

```python
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Global state
model = None           # ML model instance
vectorizer = None      # TF-IDF vectorizer
model_name = None      # Type of model (Naive Bayes, SVM, RF)
```

### Request/Response Flow

**Example: POST /api/predict**

```
REQUEST:
{
    "description": "50 bags of cement",
    "project_name": "Harbor View",
    "location": "Chennai"
}
    ↓
PROCESSING:
1. Clean text: "50 bags of cement" → "50 bags cement"
2. Vectorize: TF-IDF transform
3. Predict: model.predict(X_vec)
4. Get confidence: model.predict_proba() or decision_function()
    ↓
RESPONSE:
{
    "success": true,
    "category": "Material",
    "confidence": 0.9234,
    "model_type": "Linear SVM"
}
```

### Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
```

### CORS Configuration
- Allows requests from any origin
- Supports all standard HTTP methods
- Handles preflight requests automatically

## 3. Machine Learning Pipeline (model_training.ipynb)

### Data Preparation Phase

```python
# Load data
df = pd.read_csv(DATASET_PATH)

# Clean text
def clean_text(text):
    text = str(text or '').lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # Remove special chars
    text = re.sub(r'\s+', ' ', text).strip()   # Normalize spaces
    return text

# Combine features
df['text'] = (df['Description'] + ' ' + df['Type'] + ' ' + df['Cause']).apply(clean_text)

# Remove invalid entries
df = df[(df['text'] != '') & (df['Task Group'] != '')]
```

### Feature Engineering Phase

```python
vectorizer = TfidfVectorizer(
    max_features=7000,      # Top 7000 terms
    ngram_range=(1, 2)      # Unigrams + bigrams
)

X_vec = vectorizer.fit_transform(X)  # Sparse matrix output

# Split: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)
```

### Model Selection Phase

```python
models = {
    'Naive Bayes': MultinomialNB(),
    'Linear SVM': LinearSVC(max_iter=2000),
    'Random Forest': RandomForestClassifier(n_estimators=100)
}

for name, model in models.items():
    model.fit(X_train, y_train)
    accuracy = accuracy_score(model.predict(X_test), y_test)
    # Select model with highest accuracy
```

### Hyperparameter Tuning Phase

```python
param_grid = {'C': [0.1, 1, 10, 100]}

grid_search = GridSearchCV(
    LinearSVC(max_iter=2000),
    param_grid,
    cv=3,
    n_jobs=-1
)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

### Evaluation Phase

```python
# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision, recall, f1 = precision_recall_fscore_support(...)

# Visualization
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm)  # Plot confusion matrix
```

### Model Persistence

```python
joblib.dump(best_model, 'model.pkl')      # Model
joblib.dump(vectorizer, 'vectorizer.pkl')  # Vectorizer
joblib.dump(model_name, 'model_name.pkl')  # Model type
```

## 4. Data Flow Example: Adding an Expense

### Step-by-Step Execution

```
1. USER EVENT
   ├─ Enters: "50 bags of premium cement for foundation"
   ├─ Project: "Harbor View"
   └─ Location: "Chennai"

2. LIVE PREDICTION (Real-time, while typing)
   ├─ Frontend: updateLive() triggered
   ├─ API Call: POST /api/predict
   ├─ Backend: 
   │  ├─ Clean text: "50 bags premium cement foundation"
   │  ├─ Vectorize: TF-IDF transformation
   │  ├─ Model.predict([...]) → "Material"
   │  └─ Confidence: 0.95
   └─ Frontend: Display "🤖 Material (95%)"

3. USER SUBMISSION
   ├─ Clicks "Register & Auto-categorize"
   ├─ Form validation passes
   └─ Event listener: expenseForm.submit

4. BACKEND PREDICTION (On submission)
   ├─ API Call: POST /api/predict (again if fresh)
   ├─ Receives result: category="Material", confidence=0.95
   └─ Returns category name

5. DATA STORAGE
   ├─ Create expense object:
   │  {
   │    id: 1713103200000,
   │    date: "2026-04-14",
   │    project: "Harbor View",
   │    location: "Chennai",
   │    description: "50 bags of premium cement...",
   │    amount: 87500,
   │    category: "Material"
   │  }
   ├─ Push to expenses array
   └─ Save to LocalStorage

6. UI UPDATE
   ├─ renderAll() function:
   │  ├─ updateDashboard() → Recalculate KPIs
   │  ├─ updateChart() → Redraw category breakdown
   │  ├─ renderExpenses() → Add row to table
   │  └─ renderProjects() → Update project view
   └─ Display success alert with category & confidence

7. USER NAVIGATION
   ├─ Form reset
   └─ Switch to Dashboard page
```

## 5. Confidence Scoring

Different models provide confidence differently:

### MultinomialNB
```python
probabilities = model.predict_proba(X_vec)
confidence = np.max(probabilities)  # 0.0-1.0
```

### LinearSVC
```python
decision_scores = model.decision_function(X_vec)
confidence = np.max(np.abs(decision_scores))
confidence = min(confidence / 10, 0.99)  # Normalize to 0-1
```

### RandomForest
```python
probabilities = model.predict_proba(X_vec)
confidence = np.max(probabilities)  # 0.0-1.0
```

## 6. Fallback Mechanism

If API is unavailable:

```
User types expense → updateLive() triggered → 
API call fails → Catch exception → 
Use fallbackSmartCategory(desc, proj) → 
Regex-based rule matching → 
Display with 📋 icon (not 🤖)
```

### Regex Rules
```javascript
const rules = [
  {pattern: /cement|concrete|steel|brick.../i, category: "Material"},
  {pattern: /labor|worker|wage|plumber.../i, category: "Labor"},
  {pattern: /transport|truck|fuel|delivery.../i, category: "Transport"},
  {pattern: /equipment|excavator|crane.../i, category: "Equipment"},
  {pattern: /electrical|plumbing|hvac.../i, category: "Subcontractor"}
];
```

## 7. Performance Optimization

### Frontend
- Async/await for non-blocking API calls
- Debounced updateLive() to avoid excessive API calls
- LocalStorage for fast data retrieval
- Chart reuse to avoid recreation

### Backend
- Model loaded once at startup
- Vectorizer cached in memory
- Sparse matrix format for TF-IDF
- Efficient NumPy operations

### Model Training
- Stratified split to maintain class balance
- N_jobs=-1 for parallel processing
- Cross-validation for robustness

## 8. Deployment Considerations

### Development
```bash
python app.py  # Built-in Flask dev server
```

### Production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Cloud Deployment
- **Backend**: AWS Lambda, Google Cloud Run, Heroku
- **Frontend**: Vercel, Netlify, GitHub Pages
- **Model Storage**: S3, GCS, blob storage

## 9. Security Considerations

### Input Validation
```python
# Check content before processing
if not data or 'description' not in data:
    return jsonify({'error': 'Missing field'}), 400

description = data.get('description', '').strip()
```

### CORS Headers
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Rate Limiting (Optional)
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/predict')
@limiter.limit("100 per minute")
def predict():
    ...
```

## 10. Future Enhancements

### Model Improvements
- [ ] Deep learning (LSTM, Transformer)
- [ ] Word embeddings (Word2Vec, GloVe)
- [ ] Active learning for continuous improvement
- [ ] Ensemble methods

### Backend Features
- [ ] Authentication & authorization
- [ ] Database integration (PostgreSQL)
- [ ] Prediction history logging
- [ ] Model versioning & rollback

### Frontend Features
- [ ] Export reports (PDF, Excel)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced filtering & analytics

### DevOps
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring & logging (ELK stack)
- [ ] Model serving platform (BentoML)
