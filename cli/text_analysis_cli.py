"""
NLP Text Analysis Client (CLI Version)
Aligned with Week 2 Day 4 & Week 3 Day 5:
"Text analysis techniques: keyword extraction, entity detection,
sentiment analysis, and summarization; building a lightweight application with text analysis."
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.text_analysis import run_comprehensive_text_analysis

def main():
    print("=" * 70)
    print(" AZURE AI NLP TEXT ANALYSIS PIPELINE")
    print(" Author: Arnav Sharma | Chandigarh University")
    print("=" * 70)

    sample_file = os.path.join(os.path.dirname(__file__), "..", "app", "static", "samples", "sample_contract.txt")
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = "Contoso Cloud Services provides Microsoft Foundry models to Chandigarh University under Responsible AI guidelines."

    print("Analyzing Sample Service Agreement:\n")
    print(text[:300] + "...\n")
    print("-" * 70)

    results = run_comprehensive_text_analysis(text)

    # 1. Sentiment
    s = results["sentiment"]
    print(f"1. SENTIMENT ANALYSIS:")
    print(f"   Polarity: {s['polarity']} | Subjectivity: {s['subjectivity']} | Label: {s['sentiment']} ({s['confidence']*100:.0f}% confidence)")

    # 2. Entities
    print(f"\n2. NAMED ENTITY RECOGNITION (NER):")
    for ent in results["entities"]:
        print(f"   • [{ent['category']}] {ent['text']} (Confidence: {ent['confidence']*100:.0f}%)")

    # 3. Keyphrases
    print(f"\n3. SALIENT KEYPHRASES:")
    for kp in results["keyphrases"]:
        print(f"   • {kp['phrase']} (Freq: {kp['frequency']}, Relevance: {kp['relevance_score']})")

    # 4. Summary
    sm = results["summary"]
    print(f"\n4. EXTRACTIVE SUMMARY ({sm['compression_ratio']}):")
    print(f"   {sm['summary']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
