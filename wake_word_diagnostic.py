#!/usr/bin/env python3
"""
Wake Word Training Diagnostic
Help diagnose and fix wake word training issues
"""

import pickle
import numpy as np
from scipy.spatial.distance import cosine
import json
import os

def diagnose_wake_word_model():
    """Diagnose issues with wake word training"""
    print("🔍 Wake Word Training Diagnostic")
    print("="*40)
    
    # Check if model exists
    if not os.path.exists('custom_wake_word_model.pkl'):
        print("❌ No wake word model found!")
        print("Please train a wake word first using: py custom_wake_word_trainer.py")
        return
    
    try:
        # Load the model
        with open('custom_wake_word_model.pkl', 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"Wake Word: '{model_data['word']}'")
        print(f"Trained: {model_data.get('trained', False)}")
        print(f"Number of samples: {len(model_data.get('features', []))}")
        print()
        
        if not model_data.get('trained', False):
            print("❌ Model is not trained!")
            return
        
        # Analyze the model
        model = model_data['model']
        features = model_data.get('features', [])
        
        if len(features) < 3:
            print("❌ Insufficient training samples!")
            print(f"Found: {len(features)}, Need: 3+")
            return
        
        # Convert to numpy array
        features_array = np.array(features)
        
        print("📊 TRAINING ANALYSIS:")
        print("-" * 30)
        
        # Calculate similarities between samples
        similarities = []
        for i in range(len(features_array)):
            for j in range(i + 1, len(features_array)):
                similarity = 1 - cosine(features_array[i], features_array[j])
                similarities.append(similarity)
                print(f"Sample {i+1} vs Sample {j+1}: {similarity:.3f}")
        
        avg_similarity = np.mean(similarities) if similarities else 0.0
        min_similarity = np.min(similarities) if similarities else 0.0
        max_similarity = np.max(similarities) if similarities else 0.0
        
        print(f"\nSimilarity Stats:")
        print(f"  Average: {avg_similarity:.3f}")
        print(f"  Minimum: {min_similarity:.3f}")
        print(f"  Maximum: {max_similarity:.3f}")
        
        # Calculate variance
        feature_variance = np.var(features_array, axis=0)
        avg_variance = np.mean(feature_variance)
        consistency_score = 1.0 / (1.0 + avg_variance)
        
        print(f"\nConsistency Stats:")
        print(f"  Average Variance: {avg_variance:.3f}")
        print(f"  Consistency Score: {consistency_score:.3f}")
        
        # Calculate quality
        quality_score = min(1.0, avg_similarity * consistency_score)
        
        print(f"\nQUALITY ANALYSIS:")
        print(f"  Quality Score: {quality_score:.3f}")
        
        # Provide diagnosis
        print(f"\n🎯 DIAGNOSIS:")
        if quality_score >= 0.8:
            print("✅ EXCELLENT - Your training is very good!")
        elif quality_score >= 0.6:
            print("✅ GOOD - Your training should work well")
        elif quality_score >= 0.4:
            print("⚠️ FAIR - Training might work but could be improved")
        elif quality_score >= 0.2:
            print("❌ POOR - Training needs improvement")
        else:
            print("❌ VERY POOR - Training is likely unusable")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if avg_similarity < 0.3:
            print("• Your pronunciations are very inconsistent")
            print("• Try saying the wake word exactly the same way each time")
            print("• Speak clearly and at the same pace")
        elif avg_similarity < 0.6:
            print("• Your pronunciations are somewhat inconsistent")
            print("• Try to be more consistent in how you say the wake word")
        
        if consistency_score < 0.3:
            print("• High variance in audio features detected")
            print("• Check for background noise during recording")
            print("• Make sure microphone distance is consistent")
            print("• Record in a quiet environment")
        
        if min_similarity < 0.1:
            print("• At least one sample is very different from others")
            print("• One recording might have failed or been mispronounced")
            print("• Consider retraining all samples")
        
        # Show threshold info
        threshold = model.get('confidence_threshold', 0.7)
        print(f"\nCurrent Detection Threshold: {threshold:.3f}")
        
        if quality_score < threshold:
            print("⚠️ WARNING: Quality is below detection threshold!")
            print("   This means the wake word might not work reliably")
            print("   Recommendation: Retrain with better consistency")
        
    except Exception as e:
        print(f"❌ Error analyzing model: {e}")

def suggest_training_tips():
    """Provide training tips"""
    print("\n" + "="*40)
    print("🎓 TRAINING TIPS FOR BETTER QUALITY:")
    print("="*40)
    
    tips = [
        "🎤 Use a good microphone (headset preferred)",
        "🔇 Record in a quiet room with no background noise",
        "📏 Keep consistent distance from microphone",
        "🗣️ Speak clearly and at normal volume",
        "⏱️ Say the wake word at the same pace each time",
        "🎯 Use the exact same pronunciation each time",
        "⏸️ Wait for the recording prompt before speaking",
        "🔄 If quality is poor, retrain all samples",
        "📝 Choose a wake word that's easy to say consistently",
        "🎵 Avoid wake words with similar-sounding syllables"
    ]
    
    for tip in tips:
        print(f"  {tip}")
    
    print(f"\n🎯 IDEAL WAKE WORDS:")
    print("  • 'Hey Assistant' - Clear, distinct sounds")
    print("  • 'Computer Sarah' - Different syllables")
    print("  • 'Activate System' - Professional sounding")
    
    print(f"\n❌ AVOID THESE:")
    print("  • Single words like 'Hey' - too common")
    print("  • Similar sounds like 'Hey Bay' - confusing")
    print("  • Very long phrases - hard to be consistent")

if __name__ == "__main__":
    diagnose_wake_word_model()
    suggest_training_tips()
    
    print(f"\n🔄 TO RETRAIN:")
    print("  py custom_wake_word_trainer.py")
    
    input("\nPress Enter to exit...")