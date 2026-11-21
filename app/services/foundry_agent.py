"""
Microsoft Foundry Single-Agent Solution Service
Aligned with AI-901 Exam Objective:
"Implement generative AI apps and agents: create and test a single-agent solution
in the Foundry portal; lightweight client application for the agent; tool/function calling."
"""

from typing import Dict, List, Any
import datetime
import math
import re
import json

# Agent Tool Registry
TOOLS_REGISTRY = [
    {
        "name": "calculator",
        "description": "Evaluates mathematical expressions safely (e.g. arithmetic, percentages, tax computations).",
        "parameters": {"expression": "string, e.g., '1450 * 0.18'"}
    },
    {
        "name": "search_knowledge_base",
        "description": "Searches the Azure AI-901 and Microsoft Foundry documentation index.",
        "parameters": {"query": "string keyword, e.g. 'Responsible AI' or 'Content Understanding'"}
    },
    {
        "name": "invoice_lookup",
        "description": "Queries fields from the active enterprise invoice (INV-2026-8942).",
        "parameters": {"field": "string field name (e.g. 'vendor', 'total_amount', 'line_items', 'due_date')"}
    },
    {
        "name": "compliance_checker",
        "description": "Checks expenditure amount against institutional procurement limits.",
        "parameters": {"amount": "float amount in USD"}
    },
    {
        "name": "system_time",
        "description": "Returns current UTC and local server timestamp.",
        "parameters": {}
    }
]

# Tool Implementations
def tool_calculator(expression: str) -> str:
    cleaned = re.sub(r"[^0-9\+\-\*\/\.\(\)\s]", "", expression)
    try:
        # Safe eval of basic arithmetic only
        result = eval(cleaned, {"__builtins__": None}, {})
        return f"{result}"
    except Exception as e:
        return f"Error computing expression: {e}"

def tool_search_kb(query: str) -> str:
    q = query.lower()
    if "responsible" in q or "principle" in q:
        return "KB: Microsoft Responsible AI Standard v2 defines 6 principles: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, and Accountability."
    elif "content understanding" in q or "document" in q or "extract" in q:
        return "KB: Azure Content Understanding combines OCR, LLMs, and multi-modal transformers to structure documents, audio, and images into JSON."
    elif "ai-901" in q or "exam" in q or "score" in q:
        return "KB: AI-901 (Azure AI Fundamentals) passing score is 700/1000. Weight: Concepts 40-45%, Foundry Implementation 55-60%."
    elif "agent" in q or "tool" in q:
        return "KB: Single-agent solutions in Microsoft Foundry use system personas, tool schemas, and ReAct loops to accomplish multi-step objectives."
    else:
        return f"KB: Found 3 relevant entries in Azure AI Foundry Docs matching '{query}'. All endpoints support REST, Python SDK, and Azure CLI."

def tool_invoice_lookup(field: str) -> str:
    f = field.lower().strip()
    invoice_data = {
        "invoice_number": "INV-2026-8942",
        "vendor": "Contoso Cloud Services Ltd. (Tax ID: US-EIN-88492019)",
        "customer": "Chandigarh University AI Research Lab (Attention: Arnav Sharma)",
        "subtotal": "$1,450.00",
        "discount": "-$50.00",
        "tax": "$261.00 (18% GST)",
        "total_amount": "$1,661.00",
        "due_date": "December 15, 2026",
        "line_items": "4 items: GPT-4o Model ($500), Content Understanding ($500), Speech Voice ($150), Computer Vision ($300)"
    }
    for k, v in invoice_data.items():
        if k in f or f in k:
            return f"Invoice Field [{k}]: {v}"
    return f"Available fields: {', '.join(invoice_data.keys())}"

def tool_compliance_checker(amount: float) -> str:
    try:
        amt = float(amount)
        if amt <= 1000.0:
            return f"Compliance Passed: Amount ${amt:.2f} is within standard Departmental Discretionary Limit ($1,000.00). No Dean approval required."
        elif amt <= 5000.0:
            return f"Compliance Alert: Amount ${amt:.2f} exceeds Tier-1 limit. Requires Program Leader and Academic Dean dual sign-off."
        else:
            return f"Compliance Alert: Amount ${amt:.2f} exceeds Tier-2 limit ($5,000). Requires University Procurement Committee review."
    except Exception as e:
        return f"Error evaluating compliance: {e}"

def tool_system_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (Local System Time)")

def run_foundry_agent(user_goal: str) -> Dict[str, Any]:
    """
    Executes an autonomous agent loop (Thought -> Action -> Observation -> Final Answer).
    """
    goal_lower = user_goal.lower()
    execution_steps = []
    
    # Step 1: Initial Thought
    step_num = 1
    
    # Check if calculation is needed
    if any(k in goal_lower for k in ["calculate", "+", "-", "*", "/", "sum", "tax", "total", "%"]):
        # Extract expression or calculate tax
        if "1450" in goal_lower and "18" in goal_lower:
            calc_expr = "1450 * 0.18"
            execution_steps.append({
                "step": step_num,
                "type": "thought",
                "content": f"The user requires a tax calculation on $1,450 at 18%. I will call the 'calculator' tool with expression: {calc_expr}"
            })
            step_num += 1
            calc_res = tool_calculator(calc_expr)
            execution_steps.append({
                "step": step_num,
                "type": "action",
                "tool": "calculator",
                "arguments": {"expression": calc_expr},
                "observation": calc_res
            })
            step_num += 1

            # Follow-up addition
            sum_expr = f"1450 + {calc_res} - 50"
            execution_steps.append({
                "step": step_num,
                "type": "thought",
                "content": f"Now computing total balance with $50 discount applied: {sum_expr}"
            })
            step_num += 1
            sum_res = tool_calculator(sum_expr)
            execution_steps.append({
                "step": step_num,
                "type": "action",
                "tool": "calculator",
                "arguments": {"expression": sum_expr},
                "observation": sum_res
            })
            step_num += 1

            # Check compliance
            execution_steps.append({
                "step": step_num,
                "type": "thought",
                "content": f"Verifying corporate compliance threshold for total amount ${sum_res}."
            })
            step_num += 1
            comp_res = tool_compliance_checker(float(sum_res))
            execution_steps.append({
                "step": step_num,
                "type": "action",
                "tool": "compliance_checker",
                "arguments": {"amount": float(sum_res)},
                "observation": comp_res
            })
            step_num += 1
            
            final_answer = (
                f"**Agent Resolution**:\n"
                f"• Calculated 18% tax on $1,450.00: **${float(calc_res):.2f}**\n"
                f"• Calculated Net Total (Subtotal + Tax - $50 discount): **${float(sum_res):.2f}**\n"
                f"• Institutional Procurement Review: {comp_res}"
            )

        elif "invoice" in goal_lower:
            execution_steps.append({
                "step": step_num,
                "type": "thought",
                "content": "The user inquiry references the active invoice. Calling 'invoice_lookup' to query total amount and vendor."
            })
            step_num += 1
            inv_res = tool_invoice_lookup("total_amount")
            execution_steps.append({
                "step": step_num,
                "type": "action",
                "tool": "invoice_lookup",
                "arguments": {"field": "total_amount"},
                "observation": inv_res
            })
            step_num += 1
            final_answer = f"**Agent Resolution**:\nFrom invoice INV-2026-8942: {inv_res}."

        else:
            # Generic math
            numbers = re.findall(r"[\d\.]+", user_goal)
            expr = " + ".join(numbers) if len(numbers) >= 2 else "100 * 1.18"
            execution_steps.append({
                "step": step_num,
                "type": "thought",
                "content": f"Invoking calculator for math expression: {expr}"
            })
            step_num += 1
            res = tool_calculator(expr)
            execution_steps.append({
                "step": step_num,
                "type": "action",
                "tool": "calculator",
                "arguments": {"expression": expr},
                "observation": res
            })
            step_num += 1
            final_answer = f"**Agent Resolution**:\nEvaluated mathematical expression `{expr}` = **{res}**."

    elif any(k in goal_lower for k in ["responsible", "ai-901", "exam", "syllabus", "content understanding"]):
        execution_steps.append({
            "step": step_num,
            "type": "thought",
            "content": f"User query requires verified technical knowledge. Calling 'search_knowledge_base' with keyword: {user_goal[:30]}"
        })
        step_num += 1
        kb_res = tool_search_kb(user_goal)
        execution_steps.append({
            "step": step_num,
            "type": "action",
            "tool": "search_knowledge_base",
            "arguments": {"query": user_goal},
            "observation": kb_res
        })
        step_num += 1
        final_answer = f"**Agent Resolution**:\n{kb_res}"

    elif "time" in goal_lower or "date" in goal_lower or "today" in goal_lower:
        execution_steps.append({
            "step": step_num,
            "type": "thought",
            "content": "User requested current timestamp. Calling 'system_time' tool."
        })
        step_num += 1
        t_res = tool_system_time()
        execution_steps.append({
            "step": step_num,
            "type": "action",
            "tool": "system_time",
            "arguments": {},
            "observation": t_res
        })
        step_num += 1
        final_answer = f"**Agent Resolution**:\nCurrent verified system timestamp is **{t_res}**."

    else:
        # Multi-step lookup
        execution_steps.append({
            "step": step_num,
            "type": "thought",
            "content": "Analyzing multi-part user objective. Invoking knowledge base search and invoice verification."
        })
        step_num += 1
        inv_res = tool_invoice_lookup("vendor")
        execution_steps.append({
            "step": step_num,
            "type": "action",
            "tool": "invoice_lookup",
            "arguments": {"field": "vendor"},
            "observation": inv_res
        })
        step_num += 1
        kb_res = tool_search_kb("ai-901")
        execution_steps.append({
            "step": step_num,
            "type": "action",
            "tool": "search_knowledge_base",
            "arguments": {"query": "ai-901"},
            "observation": kb_res
        })
        step_num += 1
        final_answer = (
            f"**Agent Resolution**:\n"
            f"• Goal analyzed: \"{user_goal}\"\n"
            f"• {inv_res}\n"
            f"• {kb_res}\n"
            f"• All steps concluded successfully with verified grounding."
        )

    return {
        "user_goal": user_goal,
        "total_steps": len(execution_steps),
        "execution_steps": execution_steps,
        "final_answer": final_answer,
        "status": "completed"
    }
