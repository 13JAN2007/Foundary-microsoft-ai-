"""
AI-901 Certification Exam Simulation Engine
Aligned with official Microsoft Learn Study Guide for Exam AI-901:
Microsoft Azure AI Fundamentals (Skills measured as of April 15, 2026).
Passing threshold: 700 / 1000 points.
Domain 1: Identify AI concepts and capabilities (40–45%)
Domain 2: Implement AI solutions by using Microsoft Foundry (55–60%)
"""

from typing import Dict, List, Any, Optional

EXAM_QUESTIONS = [
    # Domain 1: Responsible AI
    {
        "id": "q1",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Principles of Responsible AI",
        "question": "A financial company develops an AI model for credit card limit approvals. When audited, the model is found to approve significantly lower limits for female applicants with identical credit scores and income as male applicants. Which principle of Responsible AI is violated?",
        "options": [
            "Fairness",
            "Inclusiveness",
            "Reliability & Safety",
            "Accountability"
        ],
        "correct_answer": 0,
        "explanation": "Fairness dictates that AI systems should treat all people fairly and avoid discrimination based on demographic attributes such as gender, race, or religion."
    },
    {
        "id": "q2",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Principles of Responsible AI",
        "question": "An autonomous drone delivery system fails to navigate safely during heavy rainstorms, causing repeated package collisions with urban obstacles. Which Responsible AI principle does this failure primarily highlight?",
        "options": [
            "Transparency",
            "Reliability & Safety",
            "Inclusiveness",
            "Privacy & Security"
        ],
        "correct_answer": 1,
        "explanation": "Reliability and Safety requires AI systems to perform dependably within their intended parameters and handle edge cases (such as harsh weather) safely without causing harm."
    },
    {
        "id": "q3",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Principles of Responsible AI",
        "question": "A hospital deploys a patient triage assistant that does not display confidence scores or provide any reasoning for its suggested emergency diagnoses. Which Responsible AI principle is neglected?",
        "options": [
            "Inclusiveness",
            "Transparency",
            "Fairness",
            "Privacy & Security"
        ],
        "correct_answer": 1,
        "explanation": "Transparency requires that AI systems be understandable and explainable to users and stakeholders, including disclosing model confidence and reasoning."
    },
    {
        "id": "q4",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Principles of Responsible AI",
        "question": "Which Responsible AI principle states that designated human beings and organizations must remain answerable for the operation and outcomes of an AI system?",
        "options": [
            "Accountability",
            "Fairness",
            "Transparency",
            "Inclusiveness"
        ],
        "correct_answer": 0,
        "explanation": "Accountability establishes that humans must design, monitor, and remain answerable for AI system decisions and their societal consequences."
    },
    {
        "id": "q5",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Principles of Responsible AI",
        "question": "A public web application incorporates high-contrast color modes, keyboard shortcuts, and full screen-reader accessibility for visually impaired citizens. Which Responsible AI principle does this practice fulfill?",
        "options": [
            "Inclusiveness",
            "Reliability & Safety",
            "Accountability",
            "Privacy & Security"
        ],
        "correct_answer": 0,
        "explanation": "Inclusiveness ensures that AI applications empower and engage people of all physical capabilities, backgrounds, and languages."
    },

    # Domain 1: How Generative AI Models Work & Workloads
    {
        "id": "q6",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "AI Model Components & Configurations",
        "question": "How do generative Large Language Models (LLMs) based on the Transformer architecture produce text responses?",
        "options": [
            "By looking up pre-written responses in a static relational database.",
            "By predicting the most probable next token sequentially based on the context of preceding tokens.",
            "By retraining neural network weights in real-time during every user inference request.",
            "By converting English sentences into SQL queries."
        ],
        "correct_answer": 1,
        "explanation": "Generative models produce responses autoregressively: predicting the next token one at a time using probability distributions shaped by attention mechanisms."
    },
    {
        "id": "q7",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "AI Model Components & Configurations",
        "question": "You need an AI model to generate structured JSON data from contracts with maximum factual consistency and zero creative hallucinations. Which temperature parameter configuration is most appropriate?",
        "options": [
            "Temperature = 1.8",
            "Temperature = 0.0 to 0.2",
            "Temperature = 1.0",
            "Temperature = -1.0"
        ],
        "correct_answer": 1,
        "explanation": "Low temperature values (0.0 to 0.2) force the model to be deterministic and pick the highest-probability tokens, minimizing hallucinations and variability."
    },
    {
        "id": "q8",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "AI Model Components & Configurations",
        "question": "What is the role of the 'Top_P' (nucleus sampling) parameter when querying a deployed language model?",
        "options": [
            "It sets the maximum number of seconds the model is allowed to compute.",
            "It restricts the model to sample only from the smallest set of top tokens whose cumulative probability exceeds P.",
            "It sets the maximum number of character tokens the user can submit.",
            "It controls the learning rate of the neural network backpropagation."
        ],
        "correct_answer": 1,
        "explanation": "Top_P (nucleus sampling) pools only the tokens that account for the top P probability mass, filtering out unlikely long-tail tokens."
    },
    {
        "id": "q9",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Common AI Workloads",
        "question": "A customer feedback platform reads survey responses and categorizes each as Positive, Neutral, or Negative. Which text analysis technique is this?",
        "options": [
            "Keyphrase extraction",
            "Named Entity Recognition (NER)",
            "Sentiment analysis",
            "Semantic segmentation"
        ],
        "correct_answer": 2,
        "explanation": "Sentiment analysis assesses the emotional tone, polarity, and subjective attitude expressed in text."
    },
    {
        "id": "q10",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "Common AI Workloads",
        "question": "An enterprise wants to identify company names, product codes, geographic locations, and dates from unstructured emails. Which NLP capability should they use?",
        "options": [
            "Optical Flow Tracking",
            "Named Entity Recognition (NER)",
            "Speech Synthesis",
            "Phonetic Tokenization"
        ],
        "correct_answer": 1,
        "explanation": "Named Entity Recognition (NER) identifies and tags real-world entities into predefined categories such as PERSON, ORGANIZATION, LOCATION, and DATE."
    },

    # Domain 2: Implementing AI Solutions with Microsoft Foundry
    {
        "id": "q11",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Generative AI Apps & Agents",
        "question": "In Microsoft Foundry, what is the primary role of a 'System Prompt' (or system message)?",
        "options": [
            "To provide user-submitted questions during chat sessions.",
            "To set the persistent persona, operational guidelines, constraints, and output format for the model.",
            "To compile Python source code into machine bytecode.",
            "To bill the Azure subscription for token usage."
        ],
        "correct_answer": 1,
        "explanation": "A system message instructs the model on who it is, how it should behave, what tone or format to adopt, and safety boundaries to adhere to."
    },
    {
        "id": "q12",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Generative AI Apps & Agents",
        "question": "What is the key difference between a standard generative chat completion and a Microsoft Foundry AI Agent?",
        "options": [
            "An AI Agent can perceive environments, utilize tools/functions, and perform multi-step goal-directed reasoning.",
            "An AI Agent cannot use Large Language Models.",
            "An AI Agent operates without any system prompt.",
            "An AI Agent only runs on local smartphones."
        ],
        "correct_answer": 0,
        "explanation": "Agents expand standard LLM chat by leveraging tool calling (e.g. databases, APIs, calculators) and autonomous multi-step reasoning loops to achieve specific goals."
    },
    {
        "id": "q13",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Generative AI Apps & Agents",
        "question": "You are writing a lightweight Python client using the Microsoft Foundry SDK to call a deployed chat model. Which method or client structure is used to submit conversational history?",
        "options": [
            "Passing an array of message objects containing 'role' (system, user, assistant) and 'content'.",
            "Uploading a compiled C++ binary DLL.",
            "Writing the query to a local Windows Registry key.",
            "Pinging the DNS server using UDP."
        ],
        "correct_answer": 0,
        "explanation": "Conversational clients send an array of JSON message objects with specified roles ('system', 'user', 'assistant') and text content to the model endpoint."
    },
    {
        "id": "q14",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Solutions for Text and Speech",
        "question": "Which Azure AI Foundry service enables converting spoken audio into real-time text transcripts and generating natural-sounding synthesized speech voices?",
        "options": [
            "Azure AI Speech",
            "Azure Blob Storage",
            "Azure Event Hubs",
            "Azure Cosmos DB"
        ],
        "correct_answer": 0,
        "explanation": "Azure AI Speech provides Speech-to-Text (transcription), Text-to-Speech (neural voice synthesis), and real-time voice translation."
    },
    {
        "id": "q15",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Computer Vision & Image Generation",
        "question": "You upload a photograph of an automobile engine and prompt the model: 'What component is disconnected near the battery terminal?' Which type of model capability enables this?",
        "options": [
            "Multimodal Model (e.g., GPT-4o)",
            "Text-only SLM",
            "Speech Synthesis Neural Engine",
            "K-Means Clustering"
        ],
        "correct_answer": 0,
        "explanation": "Multimodal models (such as GPT-4o) accept both image pixels and text prompts concurrently to reason and answer visual questions."
    },
    {
        "id": "q16",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Computer Vision & Image Generation",
        "question": "Which generative model available in the Microsoft Foundry catalog is specifically designed to create novel high-resolution visual artwork from textual descriptions?",
        "options": [
            "DALL-E 3",
            "Whisper Large v3",
            "BERT Base Uncased",
            "Text-Embedding-Ada-002"
        ],
        "correct_answer": 0,
        "explanation": "DALL-E 3 is a diffusion-based generative model tailored for creating original images and illustrations from detailed text prompts."
    },
    {
        "id": "q17",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Information Extraction",
        "question": "An accounts department receives thousands of scanned PDF invoices each month. Which Microsoft Foundry service is purpose-built to extract key-value fields such as Vendor, Invoice Total, Line Items, and Tax without manual template building?",
        "options": [
            "Azure Content Understanding (Document/Invoice Prebuilt Model)",
            "Azure Virtual Network Gateway",
            "Azure Front Door",
            "Azure Key Vault"
        ],
        "correct_answer": 0,
        "explanation": "Azure Content Understanding provides prebuilt and customizable models to extract structured key-value pairs, tables, and entities from documents, invoices, and receipts."
    },
    {
        "id": "q18",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Information Extraction",
        "question": "You have a two-hour recording of a board meeting. You need speaker labels (diarization), time-stamped text, and bulleted decisions. Which feature in Azure Content Understanding / Foundry Tools delivers this?",
        "options": [
            "Audio & Video Content Understanding with Speaker Diarization",
            "Network Security Group (NSG) flow logs",
            "Azure Data Share",
            "Azure Redis Cache"
        ],
        "correct_answer": 0,
        "explanation": "Audio and video Content Understanding processes media streams to produce diarized transcripts, timestamp markers, and semantic summaries."
    },
    {
        "id": "q19",
        "domain": "Domain 1: AI Concepts & Capabilities",
        "subdomain": "AI Model Components & Configurations",
        "question": "A developer wants to deploy a lightweight model on resource-constrained edge devices for rapid text classification at lowest possible cost. Which model family in Microsoft Foundry is best suited?",
        "options": [
            "Microsoft Phi-3.5 Mini / Small Language Models (SLMs)",
            "Full Frontier GPT-4o 128k",
            "DALL-E 3 Ultra",
            "Azure Video Indexer Enterprise"
        ],
        "correct_answer": 0,
        "explanation": "Microsoft's Phi-3.5 family of Small Language Models (SLMs) offers state-of-the-art efficiency, low memory footprint, and low latency for edge deployments."
    },
    {
        "id": "q20",
        "domain": "Domain 2: Microsoft Foundry Implementation",
        "subdomain": "Generative AI Apps & Agents",
        "question": "What is the passing score required to earn the Microsoft Certified: Azure AI Fundamentals credential in the AI-901 examination?",
        "options": [
            "700 out of 1000",
            "500 out of 1000",
            "900 out of 1000",
            "60% percentile rank"
        ],
        "correct_answer": 0,
        "explanation": "The official passing score for Microsoft certification exam AI-901 is 700 on a scaled scoring scale of 1000."
    }
]

def get_exam_questions() -> List[Dict[str, Any]]:
    """Returns the question bank for client display without revealing answers directly."""
    public_questions = []
    for q in EXAM_QUESTIONS:
        public_questions.append({
            "id": q["id"],
            "domain": q["domain"],
            "subdomain": q["subdomain"],
            "question": q["question"],
            "options": q["options"]
        })
    return public_questions

def grade_exam_submission(user_answers: Dict[str, int]) -> Dict[str, Any]:
    """
    Grades user answers against the AI-901 standard, calculates score out of 1000,
    computes domain breakdowns, and returns question-by-question rationales.
    """
    total_q = len(EXAM_QUESTIONS)
    correct_count = 0
    
    domain_stats = {
        "Domain 1: AI Concepts & Capabilities": {"correct": 0, "total": 0},
        "Domain 2: Microsoft Foundry Implementation": {"correct": 0, "total": 0}
    }
    
    review_details = []
    
    for q in EXAM_QUESTIONS:
        qid = q["id"]
        domain = q["domain"]
        domain_stats[domain]["total"] += 1
        
        user_choice = user_answers.get(qid)
        is_correct = (user_choice == q["correct_answer"])
        
        if is_correct:
            correct_count += 1
            domain_stats[domain]["correct"] += 1
            
        review_details.append({
            "id": qid,
            "question": q["question"],
            "domain": domain,
            "options": q["options"],
            "user_choice": user_choice,
            "correct_choice": q["correct_answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    # Scaled score out of 1000
    percentage = (correct_count / max(1, total_q))
    scaled_score = round(percentage * 1000)
    passed = scaled_score >= 700

    # Domain breakdown percentages
    domain_breakdown = {}
    for d_name, d_val in domain_stats.items():
        pct = round((d_val["correct"] / max(1, d_val["total"])) * 100, 1)
        domain_breakdown[d_name] = {
            "correct": d_val["correct"],
            "total": d_val["total"],
            "percentage": pct,
            "status": "Proficient" if pct >= 70 else "Review Recommended"
        }

    return {
        "candidate_name": "Arnav Sharma",
        "exam_title": "AI-901: Microsoft Azure AI Fundamentals",
        "total_questions": total_q,
        "correct_answers": correct_count,
        "scaled_score": scaled_score,
        "passing_threshold": 700,
        "passed": passed,
        "domain_breakdown": domain_breakdown,
        "review_details": review_details
    }
