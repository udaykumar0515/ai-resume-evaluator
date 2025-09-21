#!/usr/bin/env python3
"""
BULK MODE ACCURACY TEST
Tests the raw text scoring used in Resume Ranking tab (TF-IDF only)
This is the FAST mode for bulk processing multiple resumes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from modules.scoring import ResumeScorer
import warnings
warnings.filterwarnings('ignore')

class BulkModeAccuracyTester:
    def __init__(self, dataset_path="dataset.json"):
        self.dataset_path = dataset_path
        self.data = None
        self.predictions = []
        self.actual_scores = []
        self.results = {}
        # Initialize scorer with BULK MODE config (TF-IDF only, like ResumeRanker)
        self.scorer = ResumeScorer(method="tfidf", embedding_model="balanced")
        
    def load_dataset(self):
        """Load the JSON dataset"""
        print("📊 Loading dataset...")
        with open(self.dataset_path, 'r') as f:
            self.data = json.load(f)
        print(f"✅ Loaded {len(self.data)} resume samples")
        return self.data
    
    def load_job_descriptions(self):
        """Load predefined job descriptions"""
        try:
            with open("../data/predefined_jds.json", "r") as f:
                self.job_descriptions = json.load(f)
            print("✅ Loaded predefined job descriptions")
        except:
            self.job_descriptions = {}
            print("⚠️ Could not load predefined JDs, using simple descriptions")
    
    def get_job_description(self, job_role):
        """Get full job description for a role"""
        if hasattr(self, 'job_descriptions') and job_role in self.job_descriptions:
            jd_data = self.job_descriptions[job_role]
            if isinstance(jd_data, dict):
                return f"{jd_data['description']}\n\nRequirements: {'; '.join(jd_data['requirements'])}\n\nResponsibilities: {'; '.join(jd_data['responsibilities'])}"
            else:
                return str(jd_data)
        else:
            return f"Job Role: {job_role}. We are looking for a {job_role} with relevant skills and experience."
    
    def calculate_bulk_score(self, resume_text, job_role):
        """Calculate score using BULK MODE (raw text, TF-IDF only)"""
        try:
            jd_text = self.get_job_description(job_role)
            scores = self.scorer.get_similarity_score(jd_text, [resume_text])
            
            if scores and len(scores) > 0 and len(scores[0]) > 1:
                return int(scores[0][1] * 100)
            else:
                print(f"❌ Invalid scores returned: {scores}")
                return 50
        except Exception as e:
            print(f"❌ Error in bulk scoring: {e}")
            import traceback
            traceback.print_exc()
            return 50
    
    def run_predictions(self):
        """Run predictions using BULK MODE pipeline"""
        print("🔍 Running BULK MODE predictions...")
        print("   ✓ Raw text processing (no parsing)")
        print("   ✓ TF-IDF similarity only")
        print("   ✓ Fast processing for bulk operations")
        
        self.predictions = []
        self.actual_scores = []
        
        successful_predictions = 0
        failed_predictions = 0
        
        for i, sample in enumerate(self.data):
            if i % 20 == 0:
                print(f"Processing sample {i+1}/{len(self.data)}")
            
            try:
                predicted_score = self.calculate_bulk_score(
                    sample['resume_text'], 
                    sample['job_role']
                )
                
                if i < 5:  # Debug first 5 samples
                    print(f"Sample {i+1}: Predicted={predicted_score}, Actual={sample['match_score']}")
                
                self.predictions.append(predicted_score)
                self.actual_scores.append(sample['match_score'])
                successful_predictions += 1
                
            except Exception as e:
                print(f"❌ Failed to process sample {i+1}: {e}")
                self.predictions.append(50)
                self.actual_scores.append(sample['match_score'])
                failed_predictions += 1
        
        print(f"✅ BULK MODE predictions completed: {successful_predictions} successful, {failed_predictions} failed")
    
    def calculate_metrics(self):
        """Calculate comprehensive ML metrics"""
        print("📈 Calculating metrics...")
        
        # Convert to numpy arrays
        y_true = np.array(self.actual_scores)
        y_pred = np.array(self.predictions)
        
        # Regression metrics
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # Classification metrics (using score ranges)
        def score_to_category(score):
            if score < 60:
                return 0  # Poor
            elif score < 75:
                return 1  # Fair
            elif score < 90:
                return 2  # Good
            else:
                return 3  # Excellent
        
        y_true_cat = [score_to_category(score) for score in y_true]
        y_pred_cat = [score_to_category(score) for score in y_pred]
        
        # Classification metrics
        accuracy = accuracy_score(y_true_cat, y_pred_cat)
        precision = precision_score(y_true_cat, y_pred_cat, average='weighted')
        recall = recall_score(y_true_cat, y_pred_cat, average='weighted')
        f1 = f1_score(y_true_cat, y_pred_cat, average='weighted')
        
        # Store results
        self.results = {
            'regression_metrics': {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'R²': r2
            },
            'classification_metrics': {
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1-Score': f1
            },
            'raw_scores': {
                'Mean_Actual': np.mean(y_true),
                'Mean_Predicted': np.mean(y_pred),
                'Std_Actual': np.std(y_true),
                'Std_Predicted': np.std(y_pred)
            }
        }
        
        print("✅ Metrics calculated")
        return self.results
    
    def print_results(self):
        """Print comprehensive results"""
        print("\n" + "="*70)
        print("🎯 AI RESUME EVALUATOR - BULK MODE ACCURACY TEST")
        print("   (Raw Text + TF-IDF Only - Used in Resume Ranking Tab)")
        print("="*70)
        
        print("\n📊 REGRESSION METRICS:")
        print("-" * 30)
        for metric, value in self.results['regression_metrics'].items():
            print(f"{metric:>10}: {value:.4f}")
        
        print("\n🎯 CLASSIFICATION METRICS:")
        print("-" * 30)
        for metric, value in self.results['classification_metrics'].items():
            print(f"{metric:>10}: {value:.4f}")
        
        print("\n📈 RAW SCORE STATISTICS:")
        print("-" * 30)
        for metric, value in self.results['raw_scores'].items():
            print(f"{metric:>15}: {value:.2f}")
        
        # Performance interpretation
        print("\n🔍 PERFORMANCE INTERPRETATION:")
        print("-" * 30)
        
        r2 = self.results['regression_metrics']['R²']
        f1 = self.results['classification_metrics']['F1-Score']
        
        if r2 > 0.8 and f1 > 0.8:
            print("🟢 EXCELLENT: Bulk mode performs very well")
        elif r2 > 0.6 and f1 > 0.6:
            print("🟡 GOOD: Bulk mode performs reasonably well")
        elif r2 > 0.4 and f1 > 0.4:
            print("🟠 FAIR: Bulk mode needs improvement")
        else:
            print("🔴 POOR: Bulk mode needs significant improvement")
        
        print(f"\n📋 IMPROVEMENT RECOMMENDATIONS:")
        if r2 < 0.6:
            print("• Improve TF-IDF text preprocessing")
            print("• Add better keyword extraction")
            print("• Optimize n-gram ranges and parameters")
        if f1 < 0.6:
            print("• Better job-resume matching logic")
            print("• Add skill-specific scoring weights")
        if self.results['regression_metrics']['MAE'] > 15:
            print("• Reduce prediction variance")
            print("• Add more sophisticated text features")
    
    def create_visualizations(self):
        """Create visualization plots"""
        print("📊 Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Resume Evaluator - BULK MODE Performance Analysis\n(Raw Text + TF-IDF Only)', fontsize=16)
        
        # 1. Actual vs Predicted Scatter Plot
        axes[0, 0].scatter(self.actual_scores, self.predictions, alpha=0.6)
        axes[0, 0].plot([0, 100], [0, 100], 'r--', lw=2)
        axes[0, 0].set_xlabel('Actual Scores')
        axes[0, 0].set_ylabel('Predicted Scores')
        axes[0, 0].set_title('Actual vs Predicted Scores')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Residuals Plot
        residuals = np.array(self.actual_scores) - np.array(self.predictions)
        axes[0, 1].scatter(self.predictions, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Scores')
        axes[0, 1].set_ylabel('Residuals')
        axes[0, 1].set_title('Residuals Plot')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Score Distribution
        axes[1, 0].hist(self.actual_scores, bins=20, alpha=0.7, label='Actual', color='blue')
        axes[1, 0].hist(self.predictions, bins=20, alpha=0.7, label='Predicted', color='red')
        axes[1, 0].set_xlabel('Scores')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Score Distribution')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Error Distribution
        axes[1, 1].hist(residuals, bins=20, alpha=0.7, color='green')
        axes[1, 1].set_xlabel('Prediction Error')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Error Distribution')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('bulk_mode_performance.png', dpi=300, bbox_inches='tight')
        print("✅ Visualizations saved to bulk_mode_performance.png")
        plt.show()
    
    def save_detailed_results(self, output_path="bulk_mode_results.csv"):
        """Save detailed results to CSV"""
        print("💾 Saving detailed results...")
        
        # Create detailed results dataframe
        detailed_results = []
        for i, (actual, pred) in enumerate(zip(self.actual_scores, self.predictions)):
            error = abs(actual - pred)
            detailed_results.append({
                'Sample_ID': i + 1,
                'Job_Role': self.data[i]['job_role'],
                'Actual_Score': actual,
                'Predicted_Score': pred,
                'Absolute_Error': error,
                'Percentage_Error': (error / actual) * 100 if actual > 0 else 0,
                'Category_Actual': 'Poor' if actual < 60 else 'Fair' if actual < 75 else 'Good' if actual < 90 else 'Excellent',
                'Category_Predicted': 'Poor' if pred < 60 else 'Fair' if pred < 75 else 'Good' if pred < 90 else 'Excellent'
            })
        
        df_results = pd.DataFrame(detailed_results)
        df_results.to_csv(output_path, index=False)
        print(f"✅ Detailed results saved to {output_path}")
        return df_results
    
    def run_complete_test(self):
        """Run the complete BULK MODE testing pipeline"""
        print("🚀 Starting AI Resume Evaluator BULK MODE Accuracy Test")
        print("   Testing the fast scoring used in Resume Ranking tab")
        print("="*70)
        
        # Load dataset
        self.load_dataset()
        
        # Load job descriptions
        self.load_job_descriptions()
        
        # Run predictions
        self.run_predictions()
        
        # Calculate metrics
        self.calculate_metrics()
        
        # Print results
        self.print_results()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save detailed results
        self.save_detailed_results()
        
        print("\n🎉 BULK MODE testing completed successfully!")
        print("📁 Check the 'testing' folder for all output files")

if __name__ == "__main__":
    # Run the complete test
    tester = BulkModeAccuracyTester()
    tester.run_complete_test()
