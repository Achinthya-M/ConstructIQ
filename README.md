# BuildLedger: AI-Powered Construction Cost Management

An intelligent construction expense tracking system that combines machine learning with an interactive dashboard.

## 📁 Project Structure

```
MT/
├── index.html                # Frontend dashboard (modern UI)
├── model_training.ipynb      # ML model training notebook (enhanced with multiple algorithms)
├── app.py                    # Flask backend API server
├── requirements.txt          # Python dependencies
├── model.pkl                 # Trained ML model (generated)
├── vectorizer.pkl            # Text vectorizer (generated)
├── model_name.pkl            # Model type (generated)
└── README.md                 # This file
```

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train the Model
1. Open `model_training.ipynb` in Jupyter or VS Code
2. Ensure your dataset is at `../dataset/Construction_Data_PM_Tasks_All_Projects.csv`
3. Run all cells to:
   - Load and preprocess data
   - Train multiple algorithms (Naive Bayes, Linear SVM, Random Forest)
   - Select the best performing model
   - Perform hyperparameter tuning
   - Save model artifacts (`model.pkl`, `vectorizer.pkl`, `model_name.pkl`)

### Step 3: Start the Backend API
```bash
python app.py
```
The API will start at `http://localhost:5000`

**Verify API is working:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "Linear SVM"
}
```

### Step 4: Open the Frontend
1. Open `index.html` in your web browser, or
2. Use VS Code's Live Server extension

## 🧠 Machine Learning Model

### Model Training Process

The notebook implements a powerful training pipeline:

1. **Data Preparation**
   - Loads construction project expense data
   - Cleans text descriptions (removes special characters, normalizes)
   - Combines Description, Type, and Cause fields
   - Handles missing values and filters invalid entries

2. **Feature Engineering**
   - Uses TF-IDF vectorization (7000 features, 1-2 grams)
   - Captures both individual words and word pairs
   - Optimized for construction terminology

3. **Multiple Algorithms Comparison**
   - **Naive Bayes**: Fast, good baseline
   - **Linear SVM**: Excellent for text classification
   - **Random Forest**: Captures non-linear patterns

4. **Hyperparameter Tuning**
   - Grid search for optimal parameters
   - Cross-validation (3-fold)
   - Selects best model automatically

5. **Evaluation Metrics**
   - Accuracy, Precision, Recall, F1-Score
   - Confusion matrix visualization
   - Per-category performance analysis

### Categories Predicted
- **Material**: Cement, steel, bricks, paint, glass, etc.
- **Labor**: Wages, workers, electricians, plumbers, etc.
- **Transport**: Trucks, fuel, delivery, logistics, etc.
- **Equipment**: Excavators, cranes, rentals, machinery, etc.
- **Subcontractor**: Electrical, plumbing, HVAC, painting, etc.

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns model status and type.

### Single Prediction
```
POST /api/predict
Content-Type: application/json

{
  "description": "50 bags of cement for foundation",
  "project_name": "Harbor View",
  "location": "Chennai"
}
```

**Response:**
```json
{
  "success": true,
  "category": "Material",
  "confidence": 0.9234,
  "model_type": "Linear SVM"
}
```

### Batch Prediction
```
POST /api/batch-predict
Content-Type: application/json

{
  "items": [
    {"description": "Electrician wages", "project_name": "Project A"},
    {"description": "Truck fuel", "project_name": "Project B"}
  ]
}
```

### Get All Categories
```
GET /api/categories
```

Returns list of all possible expense categories.

### Model Information
```
GET /api/model-info
```

Returns detailed model metadata.

## 🎨 Frontend Features

### Dashboard
- Real-time KPI cards for each expense category
- Category breakdown chart
- Recent 5 transactions
- Project-wise financial summary

### Add Expense (with Live AI)
- **Live AI Prediction**: As you type, the AI predicts the category
- Shows prediction confidence and method (AI vs Regex fallback)
- One-click submission with confirmation

### Expense Register
- Complete table of all expenses
- Filter by category, project, or date
- Delete individual entries

### Project View
- Project-wise cost breakdown
- Location information
- Entry count per project

## 💡 Key Improvements Made

1. **Better ML Model**
   - ✅ Multiple algorithms comparison
   - ✅ Hyperparameter tuning for SVM
   - ✅ Better feature engineering (TF-IDF with bigrams)
   - ✅ Cross-validation for robustness
   - ✅ Comprehensive metrics reporting

2. **Backend Integration**
   - ✅ Flask REST API with CORS
   - ✅ Production-ready error handling
   - ✅ Batch prediction support
   - ✅ Model metadata endpoints

3. **Enhanced Frontend**
   - ✅ Real-time AI predictions while typing
   - ✅ Confidence scores displayed
   - ✅ Graceful fallback to regex rules
   - ✅ Visual feedback (🤖 AI vs 📋 Regex)
   - ✅ Async/await for smooth UX

## 🔧 Configuration

### API URL
Edit the frontend's API_BASE_URL in `index.html`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Model Features
In `model_training.ipynb`, adjust:
- `max_features`: TF-IDF vocabulary size (default: 7000)
- `ngram_range`: N-gram type (default: (1,2))
- `test_size`: Train/test split (default: 0.2)

## 🐛 Troubleshooting

### Model not loading
```
Error: Model files not found
```
**Solution**: Run all cells in `model_training.ipynb` first.

### API connection refused
```
"API unavailable"
```
**Solution**: 
1. Check Flask is running: `python app.py`
2. Verify API_BASE_URL is correct
3. Check CORS is enabled (should work cross-origin)

### Low prediction accuracy
1. Check dataset quality and size
2. Run hyperparameter tuning in the notebook
3. Add more training data if possible
4. Try different algorithms (edit the notebook)

### CORS Issues
Already handled with `Flask-CORS`. If issues persist:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## 📊 Performance Tips

1. **Faster Training**: Use GPU
   ```python
   # In model_training.ipynb
   from sklearn.svm import LinearSVC
   # SVM automatically uses multi-threading with n_jobs=-1
   ```

2. **Production Deployment**:
   ```bash
   # Use Gunicorn instead of Flask dev server
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Caching Predictions**: Add Redis for frequently predicted items

## 📚 Advanced Customization

### Add New Categories
1. Update training data with new category labels
2. Retrain the model
3. Update category rules in frontend if needed

### Use Deep Learning
Replace model in `app.py`:
```python
# Instead of sklearn, use:
import tensorflow as tf
model = tf.keras.models.load_model('model.h5')
```

### Deploy to Cloud
- **Backend**: Use AWS Lambda, Google Cloud Run, or Heroku
- **Frontend**: Deploy to GitHub Pages, Vercel, or Netlify
- **Model**: Store in cloud storage (S3, GCS)

## 📝 License
MIT License - feel free to use and modify

## 🤝 Support
For issues or feature requests, check the troubleshooting section above.
# ConstructIQ
