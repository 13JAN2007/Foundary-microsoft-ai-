"""
Responsible AI Scenario Evaluator (CLI Version)
Aligned with Week 1 Day 2-5:
"The six principles of responsible AI: fairness, reliability and safety,
privacy and security, inclusiveness, transparency and accountability."
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.responsible_ai import PREDEFINED_SCENARIOS, evaluate_custom_scenario

def main():
    print("=" * 70)
    print(" MICROSOFT RESPONSIBLE AI AUDIT ENGINE (STANDARD V2)")
    print(" Author: Arnav Sharma | Chandigarh University")
    print("=" * 70)

    print("\nAuditing Predefined AI Scenarios:\n")
    for s in PREDEFINED_SCENARIOS:
        print(f"Scenario: {s['title']} ({s['domain']})")
        print(f"Description: {s['description']}")
        print(f"Identified Principle Concerns: {', '.join(s['primary_risks'])}")
        print(f"Compliance Score: {s['compliance_score']}/100 [{s['status']}]")
        print(f"Analysis: {s['analysis']}")
        print("Remediations:")
        for r in s["remediations"]:
            print(f" • {r}")
        print("-" * 70)

    print("\nTesting Custom Scenario Evaluation:")
    test_scenario = "Deploying an autonomous candidate filter that rejects resumes containing parental leave or gap years without candidate recourse."
    print(f"Input: \"{test_scenario}\"")
    res = evaluate_custom_scenario(test_scenario)
    print(f"Audit Score: {res['overall_score']}/100 ({res['status']})")
    print(f"Risks: {res['identified_risks']}")
    print(f"Remediations: {res['remediations']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
