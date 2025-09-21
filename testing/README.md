# AI Resume Evaluator - Testing Framework

This directory contains comprehensive testing tools to evaluate the accuracy and performance of the AI Resume Evaluator system.

## 📁 Files

- `dataset.json` - Test dataset with 100 resume samples, job roles, and ground truth scores
- `test_accuracy.py` - Main testing framework with ML metrics
- `run_tests.py` - Simple test runner script
- `requirements_testing.txt` - Additional packages needed for testing
- `README.md` - This file

## 🚀 Quick Start

### 1. Install Testing Dependencies
```bash
pip install -r requirements_testing.txt
```

### 2. Run Tests
```bash
# Simple way
python run_tests.py

# Or directly
python test_accuracy.py
```

## 📊 What Gets Tested

### Regression Metrics
- **MAE (Mean Absolute Error)** - Average prediction error
- **MSE (Mean Squared Error)** - Squared prediction error
- **RMSE (Root Mean Squared Error)** - Square root of MSE
- **R² (R-squared)** - Coefficient of determination

### Classification Metrics
- **Accuracy** - Overall correctness
- **Precision** - True positives / (True positives + False positives)
- **Recall** - True positives / (True positives + False negatives)
- **F1-Score** - Harmonic mean of precision and recall

### Score Categories
- **Poor** (0-60): Low match
- **Fair** (60-75): Moderate match
- **Good** (75-90): Good match
- **Excellent** (90-100): Excellent match

## 📈 Output Files

After running tests, you'll get:

1. **`dataset.csv`** - Converted JSON to CSV format
2. **`detailed_results.csv`** - Sample-by-sample results with errors
3. **`performance_analysis.png`** - Visualization plots

## 🔍 Interpreting Results

### Good Performance Indicators
- **R² > 0.8** - Strong correlation between predicted and actual
- **F1-Score > 0.8** - Good classification accuracy
- **MAE < 10** - Low average prediction error

### Areas for Improvement
- **R² < 0.6** - Need better feature extraction
- **F1-Score < 0.6** - Need better job-resume matching
- **MAE > 15** - Need more training data or better algorithms

## 🛠️ Customizing Tests

### Modify Scoring Logic
Edit the `calculate_mock_score()` function in `test_accuracy.py` to use your actual scoring algorithm.

### Add More Metrics
Extend the `calculate_metrics()` function to include additional evaluation metrics.

### Test Different Datasets
Replace `dataset.json` with your own test data following the same format:
```json
[
  {
    "job_role": "Job Title",
    "resume_text": "Resume content...",
    "match_score": 85
  }
]
```

## 📋 Test Data Format

Each test sample should have:
- `job_role`: The job position being applied for
- `resume_text`: The resume content as text
- `match_score`: Ground truth score (0-100)

## 🎯 Performance Benchmarks

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| R² | > 0.8 | 0.6-0.8 | 0.4-0.6 | < 0.4 |
| F1-Score | > 0.8 | 0.6-0.8 | 0.4-0.6 | < 0.4 |
| MAE | < 8 | 8-12 | 12-18 | > 18 |

## 🔧 Troubleshooting

### Common Issues
1. **Import errors**: Make sure you're in the project root directory
2. **Module not found**: Install requirements from main project
3. **Memory issues**: Reduce dataset size for testing

### Getting Help
- Check the console output for detailed error messages
- Ensure all dependencies are installed
- Verify the dataset format is correct
