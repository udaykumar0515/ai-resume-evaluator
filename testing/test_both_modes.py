#!/usr/bin/env python3
"""
COMPARISON TEST - Both Modes
Runs both bulk and detailed modes and compares their performance
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_bulk_mode import BulkModeAccuracyTester
from test_detailed_mode import DetailedModeAccuracyTester
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_comparison_test():
    """Run both modes and compare results"""
    print("🚀 Starting AI Resume Evaluator - BOTH MODES COMPARISON TEST")
    print("="*80)
    
    # Run Bulk Mode Test
    print("\n" + "="*50)
    print("🔍 RUNNING BULK MODE TEST")
    print("="*50)
    bulk_tester = BulkModeAccuracyTester()
    bulk_tester.load_dataset()
    bulk_tester.load_job_descriptions()
    bulk_tester.run_predictions()
    bulk_tester.calculate_metrics()
    
    # Run Detailed Mode Test
    print("\n" + "="*50)
    print("🔍 RUNNING DETAILED MODE TEST")
    print("="*50)
    detailed_tester = DetailedModeAccuracyTester()
    detailed_tester.load_dataset()
    detailed_tester.load_job_descriptions()
    detailed_tester.run_predictions()
    detailed_tester.calculate_metrics()
    
    # Compare Results
    print("\n" + "="*80)
    print("📊 COMPARISON RESULTS")
    print("="*80)
    
    print("\n📈 REGRESSION METRICS COMPARISON:")
    print("-" * 50)
    print(f"{'Metric':<15} {'Bulk Mode':<15} {'Detailed Mode':<15} {'Difference':<15}")
    print("-" * 50)
    
    for metric in ['MAE', 'MSE', 'RMSE', 'R²']:
        bulk_val = bulk_tester.results['regression_metrics'][metric]
        detailed_val = detailed_tester.results['regression_metrics'][metric]
        diff = detailed_val - bulk_val
        print(f"{metric:<15} {bulk_val:<15.4f} {detailed_val:<15.4f} {diff:<15.4f}")
    
    print("\n🎯 CLASSIFICATION METRICS COMPARISON:")
    print("-" * 50)
    print(f"{'Metric':<15} {'Bulk Mode':<15} {'Detailed Mode':<15} {'Difference':<15}")
    print("-" * 50)
    
    for metric in ['Accuracy', 'Precision', 'Recall', 'F1-Score']:
        bulk_val = bulk_tester.results['classification_metrics'][metric]
        detailed_val = detailed_tester.results['classification_metrics'][metric]
        diff = detailed_val - bulk_val
        print(f"{metric:<15} {bulk_val:<15.4f} {detailed_val:<15.4f} {diff:<15.4f}")
    
    # Performance Analysis
    print("\n🔍 PERFORMANCE ANALYSIS:")
    print("-" * 50)
    
    bulk_r2 = bulk_tester.results['regression_metrics']['R²']
    detailed_r2 = detailed_tester.results['regression_metrics']['R²']
    bulk_f1 = bulk_tester.results['classification_metrics']['F1-Score']
    detailed_f1 = detailed_tester.results['classification_metrics']['F1-Score']
    
    print(f"Bulk Mode R²: {bulk_r2:.4f}")
    print(f"Detailed Mode R²: {detailed_r2:.4f}")
    print(f"R² Improvement: {detailed_r2 - bulk_r2:.4f}")
    print()
    print(f"Bulk Mode F1: {bulk_f1:.4f}")
    print(f"Detailed Mode F1: {detailed_f1:.4f}")
    print(f"F1 Improvement: {detailed_f1 - bulk_f1:.4f}")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    print("-" * 50)
    
    if detailed_r2 > bulk_r2:
        print("✅ Detailed mode performs better than bulk mode")
        print("   → Parsing and structured data help accuracy")
    else:
        print("⚠️ Detailed mode not significantly better than bulk mode")
        print("   → Need to improve parsing or section weighting")
    
    if detailed_f1 > bulk_f1:
        print("✅ Detailed mode has better classification accuracy")
        print("   → Hybrid scoring provides better categorization")
    else:
        print("⚠️ Detailed mode classification needs improvement")
        print("   → Need to improve hybrid scoring combination")
    
    if bulk_r2 < 0.6:
        print("🔴 Both modes need significant improvement")
        print("   → Focus on core scoring algorithms first")
    elif detailed_r2 > 0.6:
        print("🟢 Detailed mode is performing well")
        print("   → Focus on improving bulk mode efficiency")
    
    # Create comparison visualization
    create_comparison_visualization(bulk_tester, detailed_tester)
    
    # Save comparison results
    save_comparison_results(bulk_tester, detailed_tester)
    
    print("\n🎉 Comparison test completed successfully!")
    print("📁 Check the 'testing' folder for comparison results")

def create_comparison_visualization(bulk_tester, detailed_tester):
    """Create side-by-side comparison visualization"""
    print("📊 Creating comparison visualizations...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('AI Resume Evaluator - Bulk vs Detailed Mode Comparison', fontsize=16)
    
    # 1. Actual vs Predicted - Bulk Mode
    axes[0, 0].scatter(bulk_tester.actual_scores, bulk_tester.predictions, alpha=0.6, color='blue')
    axes[0, 0].plot([0, 100], [0, 100], 'r--', lw=2)
    axes[0, 0].set_xlabel('Actual Scores')
    axes[0, 0].set_ylabel('Predicted Scores')
    axes[0, 0].set_title('Bulk Mode (TF-IDF Only)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Actual vs Predicted - Detailed Mode
    axes[0, 1].scatter(detailed_tester.actual_scores, detailed_tester.predictions, alpha=0.6, color='red')
    axes[0, 1].plot([0, 100], [0, 100], 'r--', lw=2)
    axes[0, 1].set_xlabel('Actual Scores')
    axes[0, 1].set_ylabel('Predicted Scores')
    axes[0, 1].set_title('Detailed Mode (Hybrid)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Score Distribution Comparison
    axes[0, 2].hist(bulk_tester.actual_scores, bins=20, alpha=0.7, label='Actual', color='green')
    axes[0, 2].hist(bulk_tester.predictions, bins=20, alpha=0.7, label='Bulk Predicted', color='blue')
    axes[0, 2].hist(detailed_tester.predictions, bins=20, alpha=0.7, label='Detailed Predicted', color='red')
    axes[0, 2].set_xlabel('Scores')
    axes[0, 2].set_ylabel('Frequency')
    axes[0, 2].set_title('Score Distribution Comparison')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Error Distribution Comparison
    bulk_residuals = np.array(bulk_tester.actual_scores) - np.array(bulk_tester.predictions)
    detailed_residuals = np.array(detailed_tester.actual_scores) - np.array(detailed_tester.predictions)
    
    axes[1, 0].hist(bulk_residuals, bins=20, alpha=0.7, color='blue', label='Bulk Mode')
    axes[1, 0].set_xlabel('Prediction Error')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Bulk Mode Error Distribution')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].hist(detailed_residuals, bins=20, alpha=0.7, color='red', label='Detailed Mode')
    axes[1, 1].set_xlabel('Prediction Error')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Detailed Mode Error Distribution')
    axes[1, 1].grid(True, alpha=0.3)
    
    # 5. Metrics Comparison Bar Chart
    metrics = ['MAE', 'RMSE', 'R²', 'F1-Score']
    bulk_values = [
        bulk_tester.results['regression_metrics']['MAE'],
        bulk_tester.results['regression_metrics']['RMSE'],
        bulk_tester.results['regression_metrics']['R²'],
        bulk_tester.results['classification_metrics']['F1-Score']
    ]
    detailed_values = [
        detailed_tester.results['regression_metrics']['MAE'],
        detailed_tester.results['regression_metrics']['RMSE'],
        detailed_tester.results['regression_metrics']['R²'],
        detailed_tester.results['classification_metrics']['F1-Score']
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    axes[1, 2].bar(x - width/2, bulk_values, width, label='Bulk Mode', color='blue', alpha=0.7)
    axes[1, 2].bar(x + width/2, detailed_values, width, label='Detailed Mode', color='red', alpha=0.7)
    axes[1, 2].set_xlabel('Metrics')
    axes[1, 2].set_ylabel('Values')
    axes[1, 2].set_title('Metrics Comparison')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(metrics)
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('both_modes_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Comparison visualization saved to both_modes_comparison.png")
    plt.show()

def save_comparison_results(bulk_tester, detailed_tester):
    """Save detailed comparison results"""
    print("💾 Saving comparison results...")
    
    # Create comparison dataframe
    comparison_data = []
    
    for i in range(len(bulk_tester.actual_scores)):
        comparison_data.append({
            'Sample_ID': i + 1,
            'Job_Role': bulk_tester.data[i]['job_role'],
            'Actual_Score': bulk_tester.actual_scores[i],
            'Bulk_Predicted': bulk_tester.predictions[i],
            'Detailed_Predicted': detailed_tester.predictions[i],
            'Bulk_Error': abs(bulk_tester.actual_scores[i] - bulk_tester.predictions[i]),
            'Detailed_Error': abs(detailed_tester.actual_scores[i] - detailed_tester.predictions[i]),
            'Error_Difference': abs(bulk_tester.actual_scores[i] - bulk_tester.predictions[i]) - 
                              abs(detailed_tester.actual_scores[i] - detailed_tester.predictions[i])
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    df_comparison.to_csv('both_modes_comparison.csv', index=False)
    print("✅ Comparison results saved to both_modes_comparison.csv")
    
    return df_comparison

if __name__ == "__main__":
    run_comparison_test()
