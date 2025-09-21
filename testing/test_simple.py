#!/usr/bin/env python3
"""
Simple test to verify both testing files work without full dependencies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        import json
        import pandas as pd
        import numpy as np
        print("✅ Basic imports successful")
        
        # Test sklearn imports
        from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
        print("✅ Scikit-learn imports successful")
        
        # Test project modules
        from modules.scoring import ResumeScorer
        print("✅ ResumeScorer import successful")
        
        # Test accuracy tracker
        from accuracy_tracker import AccuracyTracker
        print("✅ AccuracyTracker import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without running full tests"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        # Test ResumeScorer initialization
        from modules.scoring import ResumeScorer
        scorer = ResumeScorer(method="tfidf")
        print("✅ ResumeScorer initialization successful")
        
        # Test basic scoring
        test_jd = "Software Engineer with Python experience"
        test_resume = "I am a Python developer with 3 years experience"
        scores = scorer.get_similarity_score(test_jd, [test_resume])
        print(f"✅ Basic scoring successful: {scores}")
        
        # Test accuracy tracker
        from accuracy_tracker import AccuracyTracker
        tracker = AccuracyTracker()
        print("✅ AccuracyTracker initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "test_bulk_mode.py",
        "test_detailed_mode.py", 
        "test_both_modes.py",
        "accuracy_tracker.py",
        "dataset.json",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🚀 AI Resume Evaluator - Simple Test Suite")
    print("="*50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Testing framework is ready.")
        print("📝 You can now run:")
        print("   - python test_bulk_mode.py")
        print("   - python test_detailed_mode.py") 
        print("   - python test_both_modes.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
