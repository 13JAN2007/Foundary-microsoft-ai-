"""
Microsoft Foundry Chat Client Service
Aligned with AI-901 Exam Objectives:
"Implement generative AI apps and agents: effective system and user prompts;
deploy and interact with a model in the Foundry portal; lightweight chat client
with the Foundry SDK; token calculation; configuration parameters (temperature, top_p, max_tokens)."
"""

from typing import Dict, List, Any, Optional
import time
import os
import math
from app.config import settings

# Available Foundry Catalog Models
FOUNDRY_MODELS = [
    {
        "id": "gpt-4o",
        "name": "GPT-4o (Omni)",
        "provider": "OpenAI / Microsoft",
        "type": "Multimodal (Text + Vision + Audio)",
        "context_window": "128,000 tokens",
        "latency_tier": "Low Latency (Fast)",
        "cost_per_1k": "$0.005",
        "recommended_for": "Complex reasoning, multimodal inspection, agent orchestration"
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI / Microsoft",
        "type": "Multimodal (Text + Vision)",
        "context_window": "128,000 tokens",
        "latency_tier": "Ultra-Fast",
        "cost_per_1k": "$0.00015",
        "recommended_for": "High-volume tasks, quick chat, lightweight extraction"
    },
    {
        "id": "phi-3.5-mini",
        "name": "Phi-3.5 Mini (3.8B)",
        "provider": "Microsoft Research",
        "type": "Small Language Model (SLM)",
        "context_window": "128,000 tokens",
        "latency_tier": "Edge / Real-Time",
        "cost_per_1k": "$0.0001",
        "recommended_for": "Local edge compute, low latency, structured JSON output"
    },
    {
        "id": "dall-e-3",
        "name": "DALL-E 3",
        "provider": "OpenAI / Microsoft",
        "type": "Generative Vision",
        "context_window": "N/A",
        "latency_tier": "Standard",
        "cost_per_1k": "$0.040 / image",
        "recommended_for": "High-fidelity visual generation and concept art"
    }
]

def calculate_tokens(text: str) -> Dict[str, Any]:
    """
    Simulates BPE (Byte Pair Encoding) tokenization and provides token statistics.
    Average ratio for English is ~4 characters per token.
    """
    words = text.split()
    estimated_tokens = max(1, math.ceil(len(text) / 3.8))
    
    return {
        "character_count": len(text),
        "word_count": len(words),
        "estimated_tokens": estimated_tokens,
        "token_ratio": round(len(text) / max(1, estimated_tokens), 2)
    }

def generate_foundry_chat_response(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_tokens: int = 800,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates response from Microsoft Foundry.
    If Azure OpenAI or OpenAI credentials are provided, attempts live API call.
    Otherwise, uses the local Foundry Intelligent Simulation Engine.
    """
    start_time = time.time()
    
    # Check if real API keys are present
    has_openai = bool(settings.OPENAI_API_KEY)
    has_azure = bool(settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_ENDPOINT)
    has_gemini = bool(settings.GEMINI_API_KEY)

    # 1. Try Gemini API if configured
    if has_gemini:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            last_user_query = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    last_user_query = m.get("content", "")
                    break

            full_prompt = (f"System Instruction: {system_prompt}\n\n" if system_prompt else "") + last_user_query
            content = None
            gemini_candidates = [
                "gemini-flash-latest",
                "gemini-3-flash-preview",
                "gemini-flash-lite-latest",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash"
            ]
            active_model = "gemini-flash-latest"
            for m in gemini_candidates:
                try:
                    resp = client.models.generate_content(
                        model=m,
                        contents=full_prompt
                    )
                    if resp and resp.text:
                        content = resp.text
                        active_model = m
                        break
                except Exception:
                    continue

            if content:
                elapsed = round((time.time() - start_time) * 1000, 1)
                tok_count = max(1, len(content) // 4)
                return {
                    "response": content,
                    "model": f"Gemini Live Cloud Model ({active_model})",
                    "provider": "Google Gemini Cloud API (Live)",
                    "latency_ms": elapsed,
                    "temperature": temperature,
                    "top_p": top_p,
                    "usage": {
                        "prompt_tokens": max(1, len(full_prompt) // 4),
                        "completion_tokens": tok_count,
                        "total_tokens": max(2, (len(full_prompt) + len(content)) // 4)
                    },
                    "status": "success"
                }
        except Exception as e:
            print(f"Gemini chat API fallback: {e}")

    if has_azure or has_openai:
        try:
            import openai
            if has_azure:
                client = openai.AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
                deployment = settings.AZURE_OPENAI_DEPLOYMENT
            else:
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                deployment = model

            formatted_msgs = []
            if system_prompt:
                formatted_msgs.append({"role": "system", "content": system_prompt})
            for m in messages:
                formatted_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

            response = client.chat.completions.create(
                model=deployment,
                messages=formatted_msgs,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
            elapsed = round((time.time() - start_time) * 1000, 1)
            content = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            comp_tokens = response.usage.completion_tokens

            return {
                "response": content,
                "model": model,
                "provider": "Azure OpenAI (Live Endpoint)",
                "latency_ms": elapsed,
                "temperature": temperature,
                "top_p": top_p,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": comp_tokens,
                    "total_tokens": prompt_tokens + comp_tokens
                },
                "status": "success"
            }
        except Exception as e:
            # Fall back to simulation gracefully if network or quota fails
            print(f"API fallback triggered due to: {e}")

    # Local Intelligent Foundry Engine
    user_query = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_query = m.get("content", "")
            break

    query_lower = user_query.lower()
    
    # Context-aware intelligent responses aligned with AI-901 and Azure Foundry
    if "responsible ai" in query_lower or "principle" in query_lower:
        reply = (
            "Under Microsoft's Responsible AI Standard v2 (as assessed in AI-901), there are six core principles:\n\n"
            "1. **Fairness**: AI systems must treat demographic groups equitably without algorithmic bias.\n"
            "2. **Reliability & Safety**: Systems must operate dependably within specified performance thresholds.\n"
            "3. **Privacy & Security**: Protecting confidential data and respecting privacy regulations (GDPR/HIPAA).\n"
            "4. **Inclusiveness**: Ensuring accessibility across diverse physical abilities, languages, and cultures.\n"
            "5. **Transparency**: Clear model documentation, explainable predictions, and disclosure that users are interacting with AI.\n"
            "6. **Accountability**: Designating human oversight (Human-in-the-loop) and organizational audit trails.\n\n"
            "In Microsoft Foundry, Content Safety filters and Model Cards directly enforce these principles."
        )
    elif "content understanding" in query_lower or "extract" in query_lower or "invoice" in query_lower:
        reply = (
            "Azure Content Understanding in Microsoft Foundry is designed for multimodal information extraction:\n\n"
            "• **Document & Form Processing**: Extracts key-value pairs, tables, line items, and addresses from invoices, receipts, and contracts.\n"
            "• **Vision & OCR**: Reads scene text, detects objects, and tags visual components.\n"
            "• **Audio & Video**: Generates transcripts with timestamps, diarization (speaker identification), and sentiment trajectory.\n\n"
            "You can test this directly in our **Content Understanding Studio** tab!"
        )
    elif "agent" in query_lower or "tool" in query_lower or "react" in query_lower:
        reply = (
            "In Microsoft Foundry, an **AI Agent** enhances standard generative models by introducing:\n\n"
            "1. **System Persona & Goal Instructions**: Defining specific roles and boundaries.\n"
            "2. **Tool / Function Calling**: Equipping the model with deterministic capabilities such as database lookup, API calls, and mathematical calculations.\n"
            "3. **Reasoning Loop (Thought -> Action -> Observation)**: Allowing multi-step problem solving.\n\n"
            "Check out our **Foundry Agent Studio** tab to see real-time tool calling and reasoning traces in action."
        )
    elif "temperature" in query_lower or "top_p" in query_lower or "tokens" in query_lower or "transformer" in query_lower:
        reply = (
            f"**Model Configuration Settings Analysis** (Current Temp: `{temperature}`, Top_P: `{top_p}`):\n\n"
            f"• **Temperature ({temperature})**: Controls randomness. Values near 0.0 (e.g. 0.2) make the model deterministic, ideal for factual queries and data extraction. Higher values (e.g. 0.8+) encourage creative variance.\n"
            f"• **Top_P ({top_p})**: Nucleus sampling cutoff. If set to 0.9, only tokens comprising the top 90% probability mass are sampled.\n"
            f"• **Transformer Mechanism**: Generative models predict the next token based on self-attention vectors without changing model weights during prompt inference."
        )
    elif "hi" in query_lower or "hello" in query_lower:
        reply = (
            "Hello! I am your Microsoft Foundry AI Assistant. I can assist you with:\n"
            "• Testing system and user prompts with fine-grained parameter tuning (Temperature, Top_P)\n"
            "• Exploring Azure AI-901 workloads (Text Analysis, Speech, Computer Vision, Content Understanding)\n"
            "• Evaluating scenarios against the 6 Responsible AI Principles\n"
            "• Demonstrating autonomous tool-calling agents\n\n"
            "What would you like to explore today?"
        )
    else:
        # Structured general reasoning response
        prompt_style = f" (Configured with system instruction: '{system_prompt[:50]}...')" if system_prompt else ""
        reply = (
            f"Thank you for your prompt: \"{user_query}\"{prompt_style}.\n\n"
            f"From the perspective of Azure AI Foundry and the AI-901 framework, this request leverages the **{model}** model. "
            f"With temperature set to `{temperature}` and top_p at `{top_p}`, the model balances grounding with contextual depth.\n\n"
            f"Key Architectural Highlights:\n"
            f"• **Grounding**: Ensure your system prompt clearly sets the persona, constraints, and required output format.\n"
            f"• **Safety Boundaries**: Azure AI Content Safety actively filters harmful, hateful, or jailbreak attempts.\n"
            f"• **Token Efficiency**: Clear concise instructions reduce prompt token overhead and inference latency."
        )

    time.sleep(0.15)  # Realistic simulation delay
    elapsed = round((time.time() - start_time) * 1000, 1)
    
    prompt_toks = calculate_tokens(user_query + (system_prompt or ""))["estimated_tokens"]
    comp_toks = calculate_tokens(reply)["estimated_tokens"]

    return {
        "response": reply,
        "model": model,
        "provider": "Microsoft Foundry Local Inference Engine",
        "latency_ms": elapsed,
        "temperature": temperature,
        "top_p": top_p,
        "usage": {
            "prompt_tokens": prompt_toks,
            "completion_tokens": comp_toks,
            "total_tokens": prompt_toks + comp_toks
        },
        "status": "success"
    }
