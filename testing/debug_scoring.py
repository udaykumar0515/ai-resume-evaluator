#!/usr/bin/env python3
"""
Debug the scoring issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scoring import ResumeScorer
import json

def debug_scoring():
    """Debug the scoring issue"""
    print("🔍 Debugging scoring issue...")
    
    # Load one sample
    with open('dataset.json', 'r') as f:
        data = json.load(f)
    
    sample = data[0]
    print(f"Sample: {sample['job_role']}")
    print(f"Resume text: {sample['resume_text'][:100]}...")
    
    # Initialize scorer
    scorer = ResumeScorer(method="hybrid", embedding_model="balanced")
    print("✅ Scorer initialized")
    
    # Test with simple text
    jd_text = f"Job Role: {sample['job_role']}. We are looking for a {sample['job_role']} with relevant skills and experience."
    resume_text = sample['resume_text']
    
    print(f"JD Text: {jd_text}")
    print(f"Resume Text: {resume_text[:200]}...")
    
    try:
        print("\n🔍 Testing get_similarity_score...")
        scores = scorer.get_similarity_score(jd_text, [resume_text])
        print(f"✅ Scores: {scores}")
        print(f"Type: {type(scores)}")
        print(f"Length: {len(scores) if scores else 'None'}")
        
        if scores:
            print(f"First score: {scores[0]}")
            print(f"Type of first score: {type(scores[0])}")
            if len(scores[0]) > 1:
                print(f"Score value: {scores[0][1]}")
                print(f"Type of score value: {type(scores[0][1])}")
        
    except Exception as e:
        print(f"❌ Error in get_similarity_score: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with different methods
    print("\n🔍 Testing TF-IDF only...")
    try:
        scorer_tfidf = ResumeScorer(method="tfidf")
        scores_tfidf = scorer_tfidf.get_similarity_score(jd_text, [resume_text])
        print(f"✅ TF-IDF Scores: {scores_tfidf}")
    except Exception as e:
        print(f"❌ TF-IDF Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scoring()
