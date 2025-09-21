# AI Resume Evaluator - Testing Framework

## 📁 Organized Testing Structure

This testing folder contains organized tests for both scoring modes in the AI Resume Evaluator project.

### 🚀 **test_bulk_mode.py** - BULK MODE Testing
- **Purpose**: Tests the fast scoring used in **Resume Ranking tab**
- **Method**: Raw text + TF-IDF only (like `ResumeRanker`)
- **Use Case**: Bulk processing multiple resumes quickly
- **Command**: `python test_bulk_mode.py`

### 🎯 **test_detailed_mode.py** - DETAILED MODE Testing  
- **Purpose**: Tests the complete pipeline used in **Single Resume Evaluation tab**
- **Method**: Parsing + Structured data + Hybrid scoring (like main app)
- **Use Case**: Individual resume analysis with high accuracy
- **Command**: `python test_detailed_mode.py`

### 📊 **test_both_modes.py** - COMPARISON Testing
- **Purpose**: Runs both modes and compares their performance
- **Method**: Side-by-side comparison of bulk vs detailed modes
- **Use Case**: Understanding trade-offs between speed and accuracy
- **Command**: `python test_both_modes.py`

## 📋 Testing Flow (Correct Approach)

```
Dataset → Score using scoring.py → Compare with actual scores
```

1. **Dataset**: Contains resume text + job role + expected score
2. **Score using scoring.py**: Use actual scoring algorithms
3. **Compare**: Calculate metrics (MAE, R², accuracy, etc.)

## 📈 Metrics Calculated

### Regression Metrics
- **MAE**: Mean Absolute Error
- **MSE**: Mean Squared Error  
- **RMSE**: Root Mean Squared Error
- **R²**: Coefficient of Determination

### Classification Metrics
- **Accuracy**: Overall classification accuracy
- **Precision**: Weighted precision score
- **Recall**: Weighted recall score
- **F1-Score**: Weighted F1 score

## 🎯 Performance Categories

- **Poor**: < 60 points
- **Fair**: 60-74 points
- **Good**: 75-89 points
- **Excellent**: 90+ points

## 📁 Output Files

Each test generates:
- `*_mode_performance.png` - Visualization charts
- `*_mode_results.csv` - Detailed results per sample
- Console output with comprehensive metrics

## 🚀 Quick Start

1. **Test Bulk Mode** (Fast):
   ```bash
   python test_bulk_mode.py
   ```

2. **Test Detailed Mode** (Accurate):
   ```bash
   python test_detailed_mode.py
   ```

3. **Compare Both Modes**:
   ```bash
   python test_both_modes.py
   ```

## 🔧 Dependencies

Install testing requirements:
```bash
pip install -r requirements_testing.txt
```

## 📊 Current Baseline Performance

### Bulk Mode (TF-IDF Only)
- **MAE**: ~38 points
- **R²**: ~-1.95 (needs improvement)
- **Classification Accuracy**: ~25%

### Detailed Mode (Hybrid)
- **Expected**: Better than bulk mode
- **Status**: To be tested

## 🎯 Improvement Strategy

1. **Start with Bulk Mode**: Improve core scoring algorithms
2. **Test Detailed Mode**: Verify improvements carry over
3. **Compare Results**: Ensure both modes benefit from improvements
4. **Iterate**: Continue improving based on metrics

## 📝 Notes

- Both modes use the same `scoring.py` module
- Improving bulk mode automatically improves detailed mode
- Focus on core scoring algorithms for maximum impact
- Test frequently to track improvement progress