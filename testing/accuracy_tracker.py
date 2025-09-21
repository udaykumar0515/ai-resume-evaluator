#!/usr/bin/env python3
"""
Accuracy Tracker - Stores and visualizes accuracy improvements over time
For research paper-style plots showing model improvement progression
"""
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

class AccuracyTracker:
    def __init__(self, tracking_file="accuracy_history.json"):
        self.tracking_file = tracking_file
        self.history = self.load_history()
    
    def load_history(self):
        """Load existing accuracy history"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return {
            "bulk_mode": [],
            "detailed_mode": [],
            "improvements": []
        }
    
    def save_history(self):
        """Save accuracy history to file"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def record_accuracy(self, mode, metrics, notes=""):
        """Record accuracy metrics for a specific mode"""
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "metrics": metrics,
            "notes": notes
        }
        
        self.history[mode].append(record)
        self.save_history()
        
        print(f"✅ Recorded {mode} accuracy: R²={metrics.get('R²', 0):.4f}, F1={metrics.get('F1-Score', 0):.4f}")
    
    def get_latest_metrics(self, mode):
        """Get the latest metrics for a mode"""
        if self.history[mode]:
            return self.history[mode][-1]['metrics']
        return None
    
    def calculate_improvement(self, mode, metric_name):
        """Calculate improvement in a specific metric over time"""
        if len(self.history[mode]) < 2:
            return 0
        
        latest = self.history[mode][-1]['metrics'].get(metric_name, 0)
        previous = self.history[mode][-2]['metrics'].get(metric_name, 0)
        
        return latest - previous
    
    def create_improvement_plot(self, save_path="accuracy_improvement_timeline.png"):
        """Create research paper-style improvement plot"""
        print("📊 Creating accuracy improvement timeline plot...")
        
        # Prepare data
        bulk_data = []
        detailed_data = []
        
        for record in self.history['bulk_mode']:
            bulk_data.append({
                'date': record['date'],
                'R²': record['metrics'].get('R²', 0),
                'F1-Score': record['metrics'].get('F1-Score', 0),
                'MAE': record['metrics'].get('MAE', 0),
                'mode': 'Bulk Mode'
            })
        
        for record in self.history['detailed_mode']:
            detailed_data.append({
                'date': record['date'],
                'R²': record['metrics'].get('R²', 0),
                'F1-Score': record['metrics'].get('F1-Score', 0),
                'MAE': record['metrics'].get('MAE', 0),
                'mode': 'Detailed Mode'
            })
        
        if not bulk_data and not detailed_data:
            print("⚠️ No data available for plotting")
            return
        
        # Create the plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('AI Resume Evaluator - Accuracy Improvement Timeline\nResearch Paper Style', fontsize=16, fontweight='bold')
        
        # Plot 1: R² Score over time
        if bulk_data:
            bulk_df = pd.DataFrame(bulk_data)
            axes[0, 0].plot(range(len(bulk_df)), bulk_df['R²'], 'o-', label='Bulk Mode', linewidth=2, markersize=6)
        if detailed_data:
            detailed_df = pd.DataFrame(detailed_data)
            axes[0, 0].plot(range(len(detailed_df)), detailed_df['R²'], 's-', label='Detailed Mode', linewidth=2, markersize=6)
        
        axes[0, 0].set_title('R² Score Improvement Over Time', fontweight='bold')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        
        # Plot 2: F1-Score over time
        if bulk_data:
            axes[0, 1].plot(range(len(bulk_df)), bulk_df['F1-Score'], 'o-', label='Bulk Mode', linewidth=2, markersize=6)
        if detailed_data:
            axes[0, 1].plot(range(len(detailed_df)), detailed_df['F1-Score'], 's-', label='Detailed Mode', linewidth=2, markersize=6)
        
        axes[0, 1].set_title('F1-Score Improvement Over Time', fontweight='bold')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('F1-Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Good Performance')
        
        # Plot 3: MAE reduction over time
        if bulk_data:
            axes[1, 0].plot(range(len(bulk_df)), bulk_df['MAE'], 'o-', label='Bulk Mode', linewidth=2, markersize=6)
        if detailed_data:
            axes[1, 0].plot(range(len(detailed_df)), detailed_df['MAE'], 's-', label='Detailed Mode', linewidth=2, markersize=6)
        
        axes[1, 0].set_title('Mean Absolute Error Reduction Over Time', fontweight='bold')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('MAE (Lower is Better)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].axhline(y=20, color='red', linestyle='--', alpha=0.7, label='Target MAE')
        
        # Plot 4: Combined performance comparison
        if bulk_data and detailed_data:
            # Create a combined performance score
            bulk_performance = bulk_df['R²'] * 0.5 + bulk_df['F1-Score'] * 0.5
            detailed_performance = detailed_df['R²'] * 0.5 + detailed_df['F1-Score'] * 0.5
            
            axes[1, 1].plot(range(len(bulk_performance)), bulk_performance, 'o-', label='Bulk Mode', linewidth=2, markersize=6)
            axes[1, 1].plot(range(len(detailed_performance)), detailed_performance, 's-', label='Detailed Mode', linewidth=2, markersize=6)
            
            axes[1, 1].set_title('Combined Performance Score (R² + F1)', fontweight='bold')
            axes[1, 1].set_xlabel('Iteration')
            axes[1, 1].set_ylabel('Combined Score')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].axhline(y=0.6, color='red', linestyle='--', alpha=0.7, label='Good Performance')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Improvement timeline saved to {save_path}")
        plt.show()
    
    def print_improvement_summary(self):
        """Print a summary of improvements"""
        print("\n" + "="*60)
        print("📈 ACCURACY IMPROVEMENT SUMMARY")
        print("="*60)
        
        for mode in ['bulk_mode', 'detailed_mode']:
            if len(self.history[mode]) >= 2:
                print(f"\n{mode.upper().replace('_', ' ')}:")
                print("-" * 30)
                
                latest = self.history[mode][-1]['metrics']
                previous = self.history[mode][-2]['metrics']
                
                for metric in ['R²', 'F1-Score', 'MAE']:
                    if metric in latest and metric in previous:
                        improvement = latest[metric] - previous[metric]
                        direction = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
                        print(f"{metric:>10}: {previous[metric]:.4f} → {latest[metric]:.4f} ({improvement:+.4f}) {direction}")
            else:
                print(f"\n{mode.upper().replace('_', ' ')}: No improvement data available")
    
    def export_for_research(self, output_file="research_accuracy_data.csv"):
        """Export data in research paper format"""
        print("📊 Exporting data for research paper...")
        
        all_data = []
        for mode in ['bulk_mode', 'detailed_mode']:
            for i, record in enumerate(self.history[mode]):
                all_data.append({
                    'Iteration': i + 1,
                    'Mode': mode.replace('_', ' ').title(),
                    'Date': record['date'],
                    'R2_Score': record['metrics'].get('R²', 0),
                    'F1_Score': record['metrics'].get('F1-Score', 0),
                    'MAE': record['metrics'].get('MAE', 0),
                    'RMSE': record['metrics'].get('RMSE', 0),
                    'Accuracy': record['metrics'].get('Accuracy', 0),
                    'Notes': record.get('notes', '')
                })
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_file, index=False)
            print(f"✅ Research data exported to {output_file}")
        else:
            print("⚠️ No data available for export")

# Global tracker instance
tracker = AccuracyTracker()

def record_bulk_mode_accuracy(metrics, notes=""):
    """Convenience function to record bulk mode accuracy"""
    tracker.record_accuracy("bulk_mode", metrics, notes)

def record_detailed_mode_accuracy(metrics, notes=""):
    """Convenience function to record detailed mode accuracy"""
    tracker.record_accuracy("detailed_mode", metrics, notes)

def create_improvement_plot():
    """Convenience function to create improvement plot"""
    tracker.create_improvement_plot()

def print_improvement_summary():
    """Convenience function to print improvement summary"""
    tracker.print_improvement_summary()

if __name__ == "__main__":
    # Example usage
    tracker.print_improvement_summary()
    tracker.create_improvement_plot()
    tracker.export_for_research()
