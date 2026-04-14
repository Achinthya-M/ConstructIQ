# Troubleshooting & FAQ Guide

## Quick Reference

| Issue | Solution |
|-------|----------|
| "Model not found" | Run all cells in `model_training.ipynb` |
| "API connection refused" | Start Flask: `python app.py` |
| "CORS error" | Flask-CORS is enabled in `app.py` |
| "Low accuracy" | Check dataset, retrain with tuning |
| "Predictions take too long" | Use Linear SVM (faster than RF) |

---

## Common Issues & Solutions

### 1️⃣ Model Training Issues

#### "ModuleNotFoundError: No module named 'sklearn'"
```bash
# Install scikit-learn
pip install scikit-learn==1.3.1
# Or install all requirements
pip install -r requirements.txt
```

#### "FileNotFoundError: dataset not found"
```
Expected path: ../dataset/Construction_Data_PM_Tasks_All_Projects.csv
Actual structure: 
  MT/
  ├─ model_training.ipynb
  ├─ index.html
  dataset/
  └─ Construction_Data_PM_Tasks_All_Projects.csv
```

**Fix**: Adjust path in notebook cell:
```python
DATASET_PATH = os.path.join('..', 'dataset', 'Construction_Data_PM_Tasks_All_Projects.csv')
```

#### "ValueError: Unknown label type: 'continuous'"
- Ensure target column (Task Group) contains categories, not numbers
- Check for NaN values in labels

#### Memory error during training
```python
# Reduce features in notebook
vectorizer = TfidfVectorizer(max_features=3000)  # Was 7000
```

---

### 2️⃣ Backend API Issues

#### "ConnectionRefusedError: [Errno 111] Connection refused"
```
Error: Cannot connect to http://localhost:5000
```

**Solutions**:
1. Start the Flask app:
   ```bash
   python app.py
   ```
2. Check if port 5000 is in use:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   # macOS/Linux
   lsof -i :5000
   ```
3. Use different port:
   ```python
   # In app.py
   app.run(host='0.0.0.0', port=5001)
   ```

#### "⚠ Model not loaded" response
```json
{"status": "ok", "model_loaded": false}
```

**Causes**:
- Model files not in current directory
- App started before training completed
- File permissions issue

**Solutions**:
1. Verify files exist:
   ```bash
   ls -la *.pkl
   # Should show:
   # model.pkl
   # vectorizer.pkl
   # model_name.pkl
   ```
2. Check read permissions
3. Train model: Run notebook again

#### "405 Method Not Allowed"
```
POST to GET endpoint or vice versa
```

**Correct endpoints**:
- `GET /api/health`
- `POST /api/predict`
- `GET /api/categories`

#### Import errors in app.py
```bash
pip install Flask==2.3.3 Flask-CORS==4.0.0
```

---

### 3️⃣ Frontend Issues

#### "API unavailable" message stays
```javascript
// updateLive() shows "🔄 analyzing..." then falls back
```

**Causes**:
- Flask not running
- CORS error
- Wrong API_BASE_URL

**Debug**:
```javascript
// Open browser console (F12)
// Check Network tab
// Should see POST to http://localhost:5000/api/predict

// Or test manually:
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

#### Predictions not updating in real-time
- Wait for previous request to complete
- Check browser console for errors (F12)
- Verify Flask is responding:
  ```bash
  curl http://localhost:5000/api/health
  ```

#### LocalStorage not persisting data
```javascript
// Clear and reload
localStorage.clear()
location.reload()
```

#### Chart not displaying
- Check Chart.js CDN is loaded
- Open browser console for errors
- Verify data format in `renderDashboard()`

#### "Cannot read property 'toLocaleString' of undefined"
- Data might be missing from chart
- Verify `totals()` function returns all categories

---

### 4️⃣ Model Accuracy Issues

#### Low accuracy (< 70%)
1. **Check data quality**:
   ```python
   # In notebook
   print("Shape:", df.shape)
   print("Classes:", df['Task Group'].value_counts())
   print("Missing:", df.isnull().sum())
   ```

2. **Increase training data**: More examples improve accuracy

3. **Try different algorithms** in notebook:
   ```python
   from sklearn.linear_model import LogisticRegression
   models['LogisticRegression'] = LogisticRegression(max_iter=1000)
   ```

4. **Better hyperparameters**:
   ```python
   # In hyperparameter tuning section
   param_grid = {
       'C': [0.01, 0.1, 1, 10, 100, 1000],
       # Add more parameters based on model
   }
   ```

5. **Feature engineering**:
   ```python
   vectorizer = TfidfVectorizer(
       max_features=10000,      # Increase
       ngram_range=(1, 3),      # Add trigrams
       min_df=2,                # Filter rare terms
       max_df=0.8               # Filter common terms
   )
   ```

#### High accuracy but low prediction confidence
- Model is uncertain about predictions
- Add more training diversity
- Use `predict_proba()` to see all class probabilities

#### Different results after retraining
- Normal! Models are stochastic
- Use `random_state=42` for reproducibility
- Check if it's within normal variance

---

### 5️⃣ Performance Issues

#### API responses slow (> 1 second)
1. **Use faster model**:
   - Linear SVM: Fast ✅
   - Naive Bayes: Very fast ✅✅
   - Random Forest: Slower ❌

2. **Reduce features**:
   ```python
   vectorizer = TfidfVectorizer(max_features=3000)
   ```

3. **Use GPU** (if available):
   ```python
   from cuml.svm import LinearSVC  # RAPIDS GPU
   ```

4. **Profile the code**:
   ```python
   import cProfile
   cProfile.run('predict(description)')
   ```

#### Frontend slow with large datasets
1. **Paginate expenses table**
2. **Virtual scrolling** for long lists
3. **Lazy load** chart data

#### Training takes too long
```python
# In notebook
# 1. Sample dataset (for testing)
df_sample = df.sample(n=5000)

# 2. Reduce features
vectorizer = TfidfVectorizer(max_features=3000)

# 3. Use fewer CV folds
grid_search = GridSearchCV(..., cv=2)
```

---

### 6️⃣ Deployment Issues

#### Cannot deploy model file to cloud
- Model and vectorizer files are usually < 50MB
- Upload to cloud storage (S3, GCS)
- Load from cloud in app.py:
  ```python
  import boto3
  s3 = boto3.client('s3')
  model = joblib.load(s3.get_object(...))
  ```

#### Port 5000 already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

## Performance Benchmarks

Expected performance on typical hardware:

| Operation | Time |
|-----------|------|
| Load model from disk | < 1s |
| Predict single expense | 10-50ms (SVM/NB), 100-300ms (RF) |
| Predict 100 expenses (batch) | 100-500ms |
| Train model | 5-30s (depends on data size) |
| Hyperparameter tuning | 1-5 min |

---

## Debug Mode

### Enable verbose output

**Backend (app.py)**:
```python
app.run(debug=True)  # Shows detailed error messages
```

**Frontend (browser console)**:
```javascript
// In updateLive() and predict()
console.log('Input:', description);
console.log('API response:', data);
```

### Test API manually

```bash
# Test prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"description":"cement bags","project_name":"Project A"}'

# Test health
curl http://localhost:5000/api/health

# Test categories
curl http://localhost:5000/api/categories
```

---

## Frequently Asked Questions

### Q: Can I use a different dataset?
**A**: Yes! Just ensure your CSV has:
- `Description` column (text)
- `Task Group` column (categories)
- Optional: `Type`, `Cause` columns

Replace path in notebook:
```python
DATASET_PATH = 'path/to/your/data.csv'
```

### Q: How do I add more categories?
**A**: 
1. Ensure training data has new categories
2. Retrain the model
3. Frontend automatically detects categories via `/api/categories`

### Q: Can I use pre-trained models?
**A**: Yes! Replace in `app.py`:
```python
from transformers import pipeline
model = pipeline('zero-shot-classification')
```

### Q: How do I improve prediction accuracy?
**A**:
1. More training data (>1000 examples)
2. Better feature engineering
3. Hyperparameter tuning
4. Try ensemble methods
5. Use deep learning (transformer models)

### Q: Can I deploy without Flask?
**A**: Yes! Options:
- AWS Lambda with Zappa
- Google Cloud Functions
- Azure Functions
- FastAPI + Uvicorn

### Q: How do I handle class imbalance?
**A**:
```python
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', classes=y_train.unique(), y=y_train)
model.fit(X_train, y_train, sample_weight=class_weights)
```

---

## Getting Help

1. **Check documentation**: [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Review notebooks**: Check output cells in `model_training.ipynb`
3. **Test endpoints**: Use curl/Postman to test API
4. **See logs**: Check Flask console output
5. **Browser DevTools**: F12 to see frontend errors

---

## Report a Bug

Include:
- Exact error message
- Steps to reproduce
- Expected vs actual result
- OS, Python version, pip list output
- Browser console errors (if frontend issue)
