#!/usr/bin/env python3
"""
AI Resume Evaluator - Test Runner
Run this script to execute all accuracy tests
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_accuracy import ResumeEvaluatorTester

def main():
    print("🧪 AI Resume Evaluator - Test Suite")
    print("=" * 50)
    
    try:
        # Initialize tester
        tester = ResumeEvaluatorTester()
        
        # Run complete test suite
        tester.run_complete_test()
        
        print("\n✅ All tests completed successfully!")
        print("\n📁 Generated files:")
        print("  • testing/dataset.csv - Converted dataset")
        print("  • testing/detailed_results.csv - Detailed results")
        print("  • testing/performance_analysis.png - Visualizations")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
