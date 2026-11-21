"""
Microsoft Foundry Single-Agent Solution (CLI Version)
Aligned with Week 3 Day 4:
"Creating and testing a single-agent solution in the Foundry portal,
and creating a lightweight client application for the agent."
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.foundry_agent import run_foundry_agent, TOOLS_REGISTRY

def main():
    print("=" * 70)
    print(" MICROSOFT FOUNDRY AGENT CLIENT (AI-901 AUTONOMOUS RE-ACT)")
    print(" Author: Arnav Sharma | Chandigarh University")
    print("=" * 70)

    print("Registered Capabilities / Tools:")
    for t in TOOLS_REGISTRY:
        print(f" • {t['name']}: {t['description']}")
    print("-" * 70)

    sample_goals = [
        "Calculate 18% tax on invoice subtotal $1,450, verify if total exceeds $1,500, and check active invoice due date.",
        "What are the six principles of Responsible AI?",
        "Lookup vendor details and payment terms for invoice INV-2026-8942."
    ]

    print("\nSample Agent Objectives:")
    for idx, g in enumerate(sample_goals, 1):
        print(f" [{idx}] {g}")
    print(" [0] Enter custom goal")

    choice = input("\nSelect sample [1-3] or 0 for custom: ").strip()
    if choice in ["1", "2", "3"]:
        goal = sample_goals[int(choice) - 1]
    else:
        goal = input("Enter custom goal: ").strip()
        if not goal:
            goal = sample_goals[0]

    print(f"\n[Executing Autonomous Agent for Goal: \"{goal}\"]\n")
    result = run_foundry_agent(goal)

    for step in result["execution_steps"]:
        st_type = step["type"].upper()
        if step["type"] == "thought":
            print(f"[Step {step['step']}] THOUGHT: {step['content']}")
        elif step["type"] == "action":
            print(f"[Step {step['step']}] ACTION: Tool '{step['tool']}' with args {step.get('arguments')}")
            print(f"        ↳ OBSERVATION: {step.get('observation')}")

    print("\n" + "=" * 70)
    print("AGENT FINAL ANSWER:")
    print("=" * 70)
    print(result["final_answer"])
    print("=" * 70)

if __name__ == "__main__":
    main()
