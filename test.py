#!/usr/bin/env python
"""
BuildLedger System Health Check
Verifies that all components are set up correctly
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_file(filepath, description):
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_python_package(package):
    try:
        __import__(package)
        print(f"✅ {package}")
        return True
    except ImportError:
        print(f"❌ {package}")
        return False

def test_api_endpoint(endpoint):
    try:
        import requests
        response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint}: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ {endpoint}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("  BuildLedger System Health Check")
    print("="*60)
    
    all_good = True
    
    # 1. File Structure
    print_section("1. File Structure")
    
    required_files = [
        ("index.html", "Frontend dashboard"),
        ("model_training.ipynb", "ML training notebook"),
        ("app.py", "Flask backend"),
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Documentation"),
    ]
    
    for filename, description in required_files:
        if not check_file(filename, description):
            all_good = False
    
    # 2. Model Files (optional at first)
    print_section("2. Model Artifacts (Generated After Training)")
    
    model_files = [
        ("model.pkl", "Trained model"),
        ("vectorizer.pkl", "Text vectorizer"),
        ("model_name.pkl", "Model type"),
    ]
    
    model_files_exist = []
    for filename, description in model_files:
        exists = check_file(filename, description)
        model_files_exist.append(exists)
    
    if not any(model_files_exist):
        print("\n⚠️  No model files found. You must run model_training.ipynb first!")
        print("   After training, come back and run this check again.")
    elif all(model_files_exist):
        print("\n✅ All model files present!")
    else:
        print("\n⚠️  Some model files missing. Make sure training completed successfully.")
    
    # 3. Python Packages
    print_section("3. Required Python Packages")
    
    packages = [
        'flask',
        'flask_cors',
        'numpy',
        'pandas',
        'sklearn',
        'joblib',
    ]
    
    missing_packages = []
    for package in packages:
        if not check_python_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        all_good = False
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print(f"   Run: pip install -r requirements.txt")
    else:
        print(f"\n✅ All required packages installed!")
    
    # 4. Frontend Check
    print_section("4. Frontend Code")
    
    with open('index.html', 'r') as f:
        frontend_code = f.read()
    
    checks = [
        ('Chart.js', 'Chart library'),
        ('smartCategory', 'AI categorization function'),
        ('API_BASE_URL', 'API endpoint configuration'),
        ('expenseForm', 'Expense form'),
    ]
    
    for keyword, description in checks:
        if keyword in frontend_code:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_good = False
    
    # 5. Backend Check
    print_section("5. Backend API Code")
    
    with open('app.py', 'r') as f:
        backend_code = f.read()
    
    backend_checks = [
        ('Flask', 'Flask framework'),
        ('CORS', 'CORS support'),
        ('/api/predict', 'Prediction endpoint'),
        ('/api/health', 'Health check endpoint'),
        ('predict_category', 'Prediction function'),
    ]
    
    for keyword, description in backend_checks:
        if keyword in backend_code:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_good = False
    
    # 6. API Runtime Check
    print_section("6. API Runtime Check")
    
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running") 
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            if data.get('model_loaded'):
                print(f"   Model type: {data.get('model_type')}")
        else:
            print(f"❌ API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️  API not running")
        print("   Start Flask: python app.py")
    except Exception as e:
        print(f"⚠️  Could not connect to API: {e}")
        print("   Make sure Flask is installed: pip install flask")
    
    # 7. Summary
    print_section("Summary")
    
    if all_good:
        print("✅ All checks passed!\n")
        print("📝 Next steps:")
        print("   1. Train the model: Run all cells in model_training.ipynb")
        print("   2. Start the backend: python app.py")
        print("   3. Open the frontend: index.html in your browser")
        print("   4. Test the system: Add an expense with live AI prediction\n")
    else:
        print("⚠️  Some issues detected. See above for details.\n")
        print("Common fixes:")
        print("   • Install packages: pip install -r requirements.txt")
        print("   • Train model: Run model_training.ipynb")
        print("   • Start API: python app.py")
        print("   • Clear cache: Ctrl+Shift+R in browser\n")
    
    print("="*60)
    print("For more help, see TROUBLESHOOTING.md\n")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
