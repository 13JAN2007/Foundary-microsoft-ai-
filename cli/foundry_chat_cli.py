"""
Microsoft Foundry Chat Client (CLI Version)
Aligned with Week 3 Day 3:
"Creating a lightweight chat client application in Python by using the Foundry SDK
to send prompts to a deployed model and display responses."
"""

import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.foundry_chat import generate_foundry_chat_response, calculate_tokens

def main():
    print("=" * 70)
    print(" MICROSOFT FOUNDRY CHAT CLIENT (AI-901 PYTHON SDK)")
    print(" Author: Arnav Sharma | Chandigarh University")
    print("=" * 70)

    system_prompt = "You are an expert Azure AI assistant. Provide concise, grounded, and technically accurate responses."
    print(f"System Persona: {system_prompt}\n")

    history = []
    print("Enter your prompts below. Type 'exit' or 'quit' to terminate.")
    print("-" * 70)

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nTerminating Foundry Chat session. Goodbye!")
                break

            history.append({"role": "user", "content": user_input})
            
            # Token metrics
            tok_stats = calculate_tokens(user_input)
            print(f"[Prompt: {tok_stats['character_count']} chars, ~{tok_stats['estimated_tokens']} tokens]")

            print("\nFoundry Assistant > ", end="", flush=True)
            res = generate_foundry_chat_response(
                messages=history,
                model="gpt-4o",
                temperature=0.7,
                system_prompt=system_prompt
            )
            print(res["response"])
            print(f"\n[Inference: {res['latency_ms']} ms | Tokens: {res['usage']['total_tokens']} | Engine: {res['provider']}]")
            history.append({"role": "assistant", "content": res["response"]})

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break

if __name__ == "__main__":
    main()
