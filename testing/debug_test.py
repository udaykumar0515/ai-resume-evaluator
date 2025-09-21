#!/usr/bin/env python3
"""
Debug test to identify issues with the scoring system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import parser
from modules.scoring import ResumeScorer
import json

def test_single_resume():
    """Test with a single resume to debug issues"""
    print("🔍 Testing single resume scoring...")
    
    # Load one sample from dataset
    with open('dataset.json', 'r') as f:
        data = json.load(f)
    
    sample = data[0]  # First sample
    print(f"Sample: {sample['job_role']} - Expected Score: {sample['match_score']}")
    
    # Initialize scorer
    scorer = ResumeScorer(method="hybrid", embedding_model="balanced")
    print("✅ Scorer initialized")
    
    # Test raw text scoring
    jd_text = f"Job Role: {sample['job_role']}. We are looking for a {sample['job_role']} with relevant skills and experience."
    resume_text = sample['resume_text']
    
    print(f"JD Text: {jd_text[:100]}...")
    print(f"Resume Text: {resume_text[:100]}...")
    
    try:
        scores = scorer.get_similarity_score(jd_text, [resume_text])
        print(f"✅ Raw text scoring successful: {scores}")
        
        if scores:
            predicted_score = int(scores[0][1] * 100)
            print(f"Predicted Score: {predicted_score}")
            print(f"Expected Score: {sample['match_score']}")
            print(f"Difference: {abs(predicted_score - sample['match_score'])}")
        
    except Exception as e:
        print(f"❌ Raw text scoring failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test parsing
    try:
        print("\n🔍 Testing resume parsing...")
        # Create temporary file for parsing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(resume_text)
            tmp_file_path = tmp_file.name
        
        parsed_data = parser.parse_resume(tmp_file_path, file_type='txt')
        os.unlink(tmp_file_path)
        print(f"✅ Parsing successful: {type(parsed_data)}")
        
        if parsed_data:
            print(f"Raw text length: {len(parsed_data.get('raw_text', ''))}")
            print(f"Skills found: {len(parsed_data.get('skills', []))}")
            
            # Test structured scoring
            print("\n🔍 Testing structured scoring...")
            resume_data = {
                'raw_text': parsed_data['raw_text'],
                'skills': parsed_data.get('skills', []),
                'experience': parsed_data.get('experience', []),
                'projects': parsed_data.get('projects', []),
                'education': parsed_data.get('education', [])
            }
            
            combined_text = parser.combine_structured_resume(resume_data)
            print(f"Combined text length: {len(combined_text)}")
            
            scores = scorer.get_similarity_score(jd_text, [combined_text])
            print(f"✅ Structured scoring successful: {scores}")
            
            if scores:
                predicted_score = int(scores[0][1] * 100)
                print(f"Structured Predicted Score: {predicted_score}")
        
    except Exception as e:
        print(f"❌ Parsing/structured scoring failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_resume()
