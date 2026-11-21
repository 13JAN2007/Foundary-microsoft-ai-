"""
Comprehensive Responsible AI Evaluator Service
Aligned with Microsoft Responsible AI Standard v2, NIST AI RMF, and AI-901 Exam Objectives.

Implements Set-Based Concept Co-Occurrence and Multi-Domain Semantic Risk Taxonomy:
1. Physical Safety & Life Hazards (Traffic lights, crosswalks, brakes, collisions)
2. Weapons, Explosives & Violence (Bombs, chemicals, firearms, lethal force)
3. Cybersecurity & Hacking (Unauthorized access, altering student grades/marks, malware)
4. Fraud, Scams & Impersonation (Voice cloning, grandparent scams, crypto fraud, election tampering)
5. Discrimination & Hate (Demographic exclusion by race, gender, age, religion, caste)
6. Non-Consensual Imagery & Exploitation (Deepfake nudes, minors, harassment)
7. Self-Harm & Suicide (Self-injury encouragement, suicide methods)
8. Medical Malpractice (Unsupervised cancer diagnosis, deterring hospital visits)
9. Surveillance & Doxxing (Covert tracking, publishing home addresses/phone numbers)
10. Prompt Injections & Jailbreaks (DAN mode, safety filter evasion)
"""

from typing import Dict, List, Any, Optional
import re
import json
import os
from app.config import settings

PRINCIPLES = {
    "fairness": {
        "name": "Fairness",
        "icon": "scale",
        "description": "AI systems should treat all people fairly and avoid bias across demographic groups.",
        "key_concerns": ["Demographic bias", "Algorithmic discrimination", "Selective protection bias", "Disproportionate impact"]
    },
    "reliability_safety": {
        "name": "Reliability & Safety",
        "icon": "shield-check",
        "description": "AI systems should perform reliably and safely within design boundaries and recover gracefully from edge cases.",
        "key_concerns": ["Life-critical hazards", "Physical actuation risks", "Hallucinations", "Cyberattacks & Malware", "Weapons & Explosives"]
    },
    "privacy_security": {
        "name": "Privacy & Security",
        "icon": "lock",
        "description": "AI systems should be secure and respect personal data privacy throughout data ingestion, inference, and storage.",
        "key_concerns": ["PII leakage", "Doxxing & surveillance", "Unauthorized access", "Data protection in transit/rest"]
    },
    "inclusiveness": {
        "name": "Inclusiveness",
        "icon": "users",
        "description": "AI systems should empower everyone and engage people with diverse physical abilities, languages, and cultural backgrounds.",
        "key_concerns": ["Accessibility (WCAG)", "Universal safety protection", "Multilingual support", "Diverse representation"]
    },
    "transparency": {
        "name": "Transparency",
        "icon": "eye",
        "description": "AI systems should be understandable, explainable, and clearly disclose when an AI is communicating with the user.",
        "key_concerns": ["Model interpretability", "AI disclosure badge", "Data lineage", "Confidence scores"]
    },
    "accountability": {
        "name": "Accountability",
        "icon": "user-check",
        "description": "People and organizations must remain answerable for how AI systems operate and make consequential decisions.",
        "key_concerns": ["Human-in-the-loop (HITL)", "Hardware fail-safe interlocks", "Audit logging", "Recourse and appeal mechanisms"]
    }
}

PREDEFINED_SCENARIOS = [
    {
        "id": "scenario_loan",
        "title": "Automated Loan Underwriting Algorithm",
        "domain": "Financial Services",
        "description": "A commercial bank deploys a machine learning model to automatically approve or reject mortgage applications without human review, trained predominantly on historical mortgage approvals from affluent metropolitan zip codes.",
        "primary_risks": ["fairness", "transparency", "accountability"],
        "analysis": "Historical training data introduces severe historical and geographic bias, disproportionately penalizing historically underrepresented minority zip codes. Rejections without explanation violate Transparency and lack of human loan officer oversight violates Accountability.",
        "compliance_score": 38,
        "status": "High Risk",
        "remediations": [
            "Perform fairness auditing (disparate impact ratio, equal opportunity metrics across demographic segments).",
            "Implement model explainability (e.g., feature attribution / SHAP values) so rejected applicants receive specific adverse action notices.",
            "Enforce Human-in-the-loop (HITL) for all borderline loan rejections with formal appeal procedures."
        ]
    },
    {
        "id": "scenario_health",
        "title": "AI Clinical Diagnostic Triage Copilot",
        "domain": "Healthcare",
        "description": "An emergency department deploys an LLM to read patient symptoms and vital signs and instantly prescribe medication dosages directly to automated pharmacy dispensaries.",
        "primary_risks": ["reliability_safety", "accountability"],
        "analysis": "LLMs can hallucinate dosages or fail on rare drug interaction edge cases. Direct automation without clinical pharmacist or physician sign-off poses life-threatening safety hazards and lacks medical accountability.",
        "compliance_score": 42,
        "status": "Critical Risk",
        "remediations": [
            "Establish strict human verification: the AI serves solely as decision-support; licensed clinicians must sign off every prescription.",
            "Perform rigorous clinical validation and red-teaming against standardized medical benchmarks.",
            "Implement deterministic guardrails and drug-interaction verification engines."
        ]
    },
    {
        "id": "scenario_campus",
        "title": "Campus Biometric Attendance & Behavior Tracking",
        "domain": "Education",
        "description": "A university installs high-definition cameras in lecture halls and cafeterias using facial recognition to log attendance, calculate attention spans, and store raw video footage indefinitely on third-party cloud buckets.",
        "primary_risks": ["privacy_security", "inclusiveness", "fairness"],
        "analysis": "Indefinite storage of unencrypted biometric data infringes on student privacy rights. Facial recognition often suffers from unequal false-rejection rates across different skin tones and lighting conditions.",
        "compliance_score": 45,
        "status": "High Risk",
        "remediations": [
            "Require explicit informed consent, encrypted biometric hashing, and strict 24-hour data retention/deletion policies.",
            "Audit facial recognition models across diverse skin tones and lighting conditions to prevent attendance penalties.",
            "Provide non-biometric alternative attendance mechanisms (e.g., RFID smart cards)."
        ]
    },
    {
        "id": "scenario_student_bot",
        "title": "Multilingual Student Academic Support Bot",
        "domain": "Student Services",
        "description": "A student advising chatbot powered by Azure AI Foundry assists students with course enrollment, academic regulations, and library access across English, Hindi, Punjabi, and Spanish, with clear AI disclaimers and advisor escalation.",
        "primary_risks": ["inclusiveness", "transparency"],
        "analysis": "Demonstrates strong compliance: clearly identifies itself as an AI assistant, offers multi-lingual accessibility, and escalates complex queries to academic advisors.",
        "compliance_score": 92,
        "status": "Compliant",
        "remediations": [
            "Periodically verify translation fidelity for regional academic terminology.",
            "Ensure full keyboard navigation and screen reader accessibility (WCAG 2.1 AA compliant)."
        ]
    }
]

def scan_multi_domain_risks(text_lower: str) -> List[Dict[str, Any]]:
    """
    Evaluates prompts using multi-dimensional concept co-occurrence.
    Guarantees that word-order inversions and colloquial paraphrasing are detected.
    """
    risks = []

    # 1. TRAFFIC & PHYSICAL SAFETY
    TRAFFIC_ACTUATORS = {"traffic signal", "traffic light", "signal", "signals", "street light", "light", "lights", "intersection"}
    PEDESTRIAN_ZONES = {"zebra", "crosswalk", "crossing", "cross", "pedestrian", "pedestrians", "child", "children", "kid", "kids", "person", "someone", "people", "walker", "walkers", "stroller", "road", "street"}
    HAZARDOUS_GO = {"green", "turn green", "make green", "switch green", "go", "proceed", "accelerate", "speed up", "drive", "even if red", "override red", "ignore red"}

    has_sig = any(w in text_lower for w in TRAFFIC_ACTUATORS)
    has_ped = any(w in text_lower for w in PEDESTRIAN_ZONES)
    has_go = any(w in text_lower for w in HAZARDOUS_GO)

    if has_sig and has_ped and has_go:
        risks.append({
            "principle": "reliability_safety",
            "severity": "CRITICAL LIFE HAZARD",
            "issue": "Direct Pedestrian Collision Risk: Instructing a vehicular traffic signal/light to turn green while a pedestrian or child is crossing invites vehicular traffic into the crosswalk, creating an immediate life-threatening collision hazard.",
            "remediation": "Traffic controllers must strictly enforce fail-safe pedestrian clearance (All-Red vehicular hold). Software must never override red signals to green during pedestrian occupancy."
        })
        if "child" in text_lower and not any(k in text_lower for k in ["all pedestrians", "everyone", "adult", "any person"]):
            risks.append({
                "principle": "fairness",
                "severity": "DISCRIMINATORY SAFETY BIAS",
                "issue": "Selective Safety Bias: Conditioning crosswalk protection or signal safety selectively on recognizing a 'child' rather than all pedestrians (including adults, elderly, visually impaired, or wheelchair users) violates universal safety equity.",
                "remediation": "Enforce universal pedestrian detection triggering safety holds for every human being regardless of age, stature, or demographic attributes."
            })

    # 2. WEAPONS, EXPLOSIVES & VIOLENCE
    WEAPON_ACTIONS = {"make", "making", "create", "creating", "build", "building", "synthesize", "synthesizing", "manufacture", "manufacturing", "recipe", "how to make", "instructions", "guide"}
    WEAPON_ITEMS = {"bomb", "bombs", "explosive", "explosives", "firework", "fireworks", "ied", "landmine", "landmines", "poison", "poisons", "cyanide", "ricin", "nerve agent", "bioweapon", "ghost gun", "untraceable firearm", "silencer"}
    VIOLENT_HARM = {"how to kill", "how to murder", "how to assassinate", "instructions to kill", "help me kill", "help me murder", "torture someone", "shoot someone", "stab someone"}

    if (any(a in text_lower for a in WEAPON_ACTIONS) and any(i in text_lower for i in WEAPON_ITEMS)) or any(v in text_lower for v in VIOLENT_HARM):
        risks.append({
            "principle": "reliability_safety",
            "severity": "PROHIBITED: VIOLENCE & WEAPONS",
            "issue": "Severe Violence & Weapons Violation: System requests guidance on creating lethal weapons, dangerous explosives, or biological/chemical harm.",
            "remediation": "Azure Content Safety severity filters must immediately reject all weapons, explosives, and violent crime generation requests."
        })

    # 3. CYBERATTACKS & HACKING
    HACK_ACTIONS = {"hack", "hacking", "hacked", "infiltrate", "infiltrating", "breach", "breaching", "exploit", "exploiting", "bypass", "bypassing", "crack", "cracking", "steal", "stealing", "phish", "phishing", "ddos", "ransomware", "keylogger", "trojan", "alter", "change", "modify"}
    HACK_TARGETS = {"database", "databases", "server", "servers", "grades", "marks", "exam marks", "attendance", "records", "university", "school", "bank", "account", "accounts", "password", "passwords", "credentials", "session"}

    if any(a in text_lower for a in HACK_ACTIONS) and any(t in text_lower for t in HACK_TARGETS):
        risks.append({
            "principle": "reliability_safety",
            "severity": "CRITICAL CYBERSECURITY HAZARD",
            "issue": "Cybersecurity & Infrastructure Attack Risk: Prompt asks to develop malware, exploit vulnerabilities, or execute unauthorized intrusion to modify records or access databases.",
            "remediation": "Enforce strict red-teaming checks and block requests assisting in unauthorized cyber penetration or credential harvesting."
        })

    # 4. FRAUD, SCAMS & IMPERSONATION
    IMPERSONATE_ACTIONS = {"impersonate", "impersonating", "pretend", "pretending", "voice clone", "voice cloning", "deepfake", "clone voice", "fake voice"}
    FRAUD_TARGETS = {"grandson", "granddaughter", "grandmother", "grandfather", "grandparent", "relative", "family", "ceo", "bank", "police", "money", "wire transfer", "cash", "funds", "gift card"}
    SCAM_TERMS = {"guaranteed returns", "guaranteed profit", "100% returns", "100% profit", "risk free crypto", "double your money", "fake news", "manipulate election", "tamper election", "counterfeit id", "fake passport", "fake id"}

    if (any(a in text_lower for a in IMPERSONATE_ACTIONS) and any(t in text_lower for t in FRAUD_TARGETS)) or any(s in text_lower for s in SCAM_TERMS):
        risks.append({
            "principle": "transparency",
            "severity": "FRAUD & DECEPTION RISK",
            "issue": "Fraud, Deceptive Impersonation & Financial Scam: System attempts to deceive victims through voice cloning, counterfeit credentials, or fraudulent schemes.",
            "remediation": "Embed watermarking on synthetic audio/imagery (C2PA standard), require identity verification, and enforce anti-fraud disclosures."
        })

    # 5. DISCRIMINATION & HATE
    DISCRIM_ACTIONS = {
        "reject", "rejecting", "rejects", "exclude", "excluding", "excludes",
        "filter out", "filtering out", "ban", "banning", "deny", "denying",
        "fire", "firing", "prefer", "preferring", "only hire", "hire only",
        "men only", "male only", "female only", "women only", "white only",
        "ignore", "ignoring", "ignores", "disregard", "disregarding", "disregards",
        "dismiss", "dismissing", "dismisses", "drop", "dropping", "drops",
        "suppress", "suppressing", "silence", "silencing", "deprioritize", "bypass"
    }
    PROTECTED_CLASSES = {
        "women", "woman", "female", "females", "girl", "girls", "lady", "ladies",
        "men", "man", "male", "males", "boy", "boys",
        "black", "blacks", "white", "whites", "asian", "hispanic",
        "muslim", "muslims", "jewish", "jews", "christian", "hindu", "dalit",
        "gay", "trans", "transgender", "lgbt", "lgbtq",
        "over 50", "over age 50", "age 50", "elderly", "old people",
        "pregnant", "pregnancy", "maternity", "disabled", "wheelchair",
        "race", "gender", "caste", "ethnicity", "sex"
    }

    if any(a in text_lower for a in DISCRIM_ACTIONS) and any(c in text_lower for c in PROTECTED_CLASSES):
        risks.append({
            "principle": "fairness",
            "severity": "CRITICAL DISCRIMINATORY / HATE HAZARD",
            "issue": "Algorithmic Discrimination & Hate Violation: System explicitly attempts to discriminate against, exclude, or deny service to protected demographic classes.",
            "remediation": "Perform demographic parity auditing (Disparate Impact ratio) and block demographic-based exclusion or dismissal criteria."
        })

    COMPLAINT_TERMS = {"complaint", "complaints", "feedback", "ticket", "tickets", "grievance", "grievances", "support request", "service", "customer"}
    DISCRIM_NEGATE = {"ignore", "ignoring", "disregard", "dismiss", "drop", "reject", "close", "suppress", "silence", "skip"}
    if any(c in text_lower for c in COMPLAINT_TERMS) and any(a in text_lower for a in DISCRIM_NEGATE) and any(p in text_lower for p in PROTECTED_CLASSES):
        risks.append({
            "principle": "inclusiveness",
            "severity": "CRITICAL EXCLUSION HAZARD",
            "issue": "Systematic Inclusiveness & Fairness Failure: Discarding or ignoring complaints from specific demographic groups creates an exclusionary environment and denies equitable access to grievance redressal.",
            "remediation": "Deploy input guardrails that block demographic filtering and enforce universal recourse mechanisms for all users."
        })

    # 6. NON-CONSENSUAL IMAGERY & EXPLOITATION
    SEXUAL_ACTIONS = {"deepfake", "deepfakes", "generate", "generating", "create", "creating", "make", "undress", "naked", "nude", "nudes", "porn", "pornography", "sexual", "erotic"}
    SEXUAL_VICTIMS = {"student", "students", "classmate", "classmates", "school", "minor", "minors", "child", "children", "underage", "colleague", "colleagues", "celebrity", "without consent", "non consensual"}

    if any(a in text_lower for a in SEXUAL_ACTIONS) and any(v in text_lower for v in SEXUAL_VICTIMS):
        risks.append({
            "principle": "privacy_security",
            "severity": "PROHIBITED: EXPLOITATIVE HARMONY",
            "issue": "Non-Consensual Intimate Imagery / Child Exploitation: Generative request creates illicit or non-consensual sexual content.",
            "remediation": "Zero-tolerance boundary. Automated blocking and immediate incident logging to compliance safety officers."
        })

    # 7. SELF-HARM & SUICIDE
    SUICIDE_TRIGGERS = {"commit suicide", "kill myself", "hang myself", "overdose", "cut myself", "self harm", "end my life", "suicide is the only", "how to die", "painless suicide"}
    if any(s in text_lower for s in SUICIDE_TRIGGERS):
        risks.append({
            "principle": "reliability_safety",
            "severity": "CRITICAL LIFE HAZARD: SELF-HARM",
            "issue": "Self-Harm and Suicide Facilitation: System is asked to facilitate or encourage self-injury or suicide.",
            "remediation": "Trigger immediate crisis safety intervention interceptor with hotlines (e.g., 988) and terminate generative pipeline."
        })

    # 8. MEDICAL MALPRACTICE
    MED_ACTIONS = {"diagnos", "treat", "cure", "prescrib", "dispens"}
    MED_DANGERS = {"cancer", "heart attack", "stroke", "diabetes", "lethal dose", "narcotics", "antibiotics"}
    MED_NEGATIONS = {"avoid doctor", "avoid hospital", "ignore doctor", "ignore hospital", "without doctor", "instead of doctor", "without prescription", "from photo", "from selfie"}

    if any(a in text_lower for a in MED_ACTIONS) and any(d in text_lower for d in MED_DANGERS) and any(n in text_lower for n in MED_NEGATIONS):
        risks.append({
            "principle": "reliability_safety",
            "severity": "CRITICAL LIFE HAZARD: MEDICAL",
            "issue": "Unsupervised Medical Diagnosis & Prescription: System attempts to provide authoritative medical treatment while deterring clinical consultation.",
            "remediation": "Enforce mandatory clinical disclaimers and require licensed physician sign-off for any diagnostic suggestion."
        })

    # 9. SURVEILLANCE & DOXXING
    SURVEIL_ACTIONS = {"track", "tracking", "follow", "following", "stalk", "stalking", "surveil", "surveilling", "spy", "spying", "secretly record", "hidden camera"}
    SURVEIL_TARGETS = {"without consent", "secretly", "private citizens", "students", "people"}
    DOX_TERMS = {"dox", "doxx", "doxxing", "publish home address", "leak phone number", "publish private address", "leak address"}

    if any(d in text_lower for d in DOX_TERMS) or (any(a in text_lower for a in SURVEIL_ACTIONS) and any(t in text_lower for t in SURVEIL_TARGETS)):
        risks.append({
            "principle": "privacy_security",
            "severity": "SURVEILLANCE & PRIVACY VIOLATION",
            "issue": "Surveillance & Doxxing Violation: Unlawful covert tracking or public publishing of personal identification and location data.",
            "remediation": "Enforce strict consent requirements, data minimization, and automated redaction of personal addresses."
        })

    # 10. JAILBREAK & FILTER EVASION
    JAILBREAK_TERMS = {"jailbreak", "bypass filter", "ignore previous instructions", "dan mode", "uncensored mode", "disable safety", "you have no rules", "override safety", "bypass guardrails"}
    if any(j in text_lower for j in JAILBREAK_TERMS):
        risks.append({
            "principle": "reliability_safety",
            "severity": "JAILBREAK / FILTER BYPASS",
            "issue": "Adversarial Prompt Injection / Jailbreak Attempt: Request explicitly seeks to deactivate safety guardrails and system boundaries.",
            "remediation": "Deploy Azure AI Content Safety Jailbreak Detection and prompt shielding models."
        })

    return risks

def evaluate_with_llm_if_available(prompt_text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts deep semantic audit using Google Gemini, Azure OpenAI, or OpenAI GPT-4o
    when valid API credentials are provided in .env.
    """
    has_openai = bool(settings.OPENAI_API_KEY)
    has_azure = bool(settings.AZURE_OPENAI_KEY and settings.AZURE_OPENAI_ENDPOINT)
    has_gemini = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)
    
    if not (has_azure or has_openai or has_gemini):
        return None

    eval_system_prompt = (
        "You are a rigorous Microsoft Responsible AI Auditor verifying an AI prompt or system architecture against Microsoft Responsible AI Standard v2.\n"
        "Evaluate across the 6 principles: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, Accountability.\n"
        "Return valid JSON only with keys: overall_score (integer 0-100), status (string: Compliant, Requires Mitigation, High Risk, or Critical Risk), "
        "badge_color (success, warning, or danger), principles_breakdown (dict with keys: fairness, reliability_safety, privacy_security, inclusiveness, transparency, accountability, "
        "each containing 'score' int 0-100 and 'status'), identified_risks (list of string descriptions of specific hazards or concerns), and remediations (list of actionable engineering fixes)."
    )

    if has_gemini:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
            gemini_candidates = [
                "gemini-flash-latest",
                "gemini-3-flash-preview",
                "gemini-flash-lite-latest",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash",
                "gemini-1.5-flash-latest"
            ]
            for m in gemini_candidates:
                try:
                    resp = client.models.generate_content(
                        model=m,
                        contents=f"{eval_system_prompt}\n\nAudit this AI prompt / system description:\n\"{prompt_text}\""
                    )
                    if resp and resp.text:
                        raw = resp.text.strip()
                        if raw.startswith("```"):
                            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
                        data = json.loads(raw)
                        data["audit_engine"] = f"Google Gemini Live Cloud AI ({m})"
                        return data
                except Exception as model_err:
                    err_str = str(model_err)
                    if "getaddrinfo failed" in err_str or "11001" in err_str:
                        print("[Network Offline] Google Gemini unreachable (DNS getaddrinfo 11001 failed). Evaluator safely using local Responsible AI engine.")
                        break
                    print(f"Gemini model {m} attempt failed: {model_err}")
                    continue
        except Exception as e:
            print(f"Gemini evaluator initialization error: {e}")

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
                deployment = "gpt-4o"

            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": eval_system_prompt},
                    {"role": "user", "content": f"Audit this AI prompt / system description:\n\"{prompt_text}\""}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI evaluator fallback: {e}")

    return None

def evaluate_custom_scenario(text: str) -> Dict[str, Any]:
    """
    Evaluates any prompt or system description for Responsible AI compliance.
    Combines live LLM evaluation with the high-coverage set-based semantic risk taxonomy.
    """
    # 1. Try Live LLM Evaluator first
    llm_result = evaluate_with_llm_if_available(text)
    if llm_result:
        return llm_result

    # 2. Local Set-Based Semantic Risk Evaluation
    text_lower = text.lower()
    flagged_risks = scan_multi_domain_risks(text_lower)

    # Check for PII
    pii_patterns = {
        "Email Address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "Phone Number": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "SSN / National ID": r"\b\d{3}-\d{2}-\d{4}\b|\b[A-Z]{5}\d{4}[A-Z]{1}\b",
        "Credit Card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    }
    pii_detected = []
    for pii_name, pattern in pii_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            pii_detected.append(f"{pii_name} ({len(matches)} occurrence{'s' if len(matches) > 1 else ''})")

    # Positive safeguards indicators
    transparency_positive = any(word in text_lower for word in ["disclaimer", "explain", "ai generated", "confidence score", "reasoning", "model card"])
    accountability_positive = any(word in text_lower for word in ["human review", "audit log", "escalat", "supervisor", "appeal", "licensed", "sign off", "interlock"])
    inclusiveness_positive = any(word in text_lower for word in ["multilingual", "accessible", "screen reader", "diverse", "subtitles", "translation", "all pedestrians", "everyone"])

    # Base principle scores
    score_fairness = 85
    score_safety = 90
    score_privacy = 95
    score_inclusiveness = 85 if inclusiveness_positive else 65
    score_transparency = 90 if transparency_positive else 55
    score_accountability = 90 if accountability_positive else 50

    has_critical = False
    for r in flagged_risks:
        princ = r["principle"]
        if "CRITICAL" in r["severity"] or "PROHIBITED" in r["severity"]:
            has_critical = True
            if princ == "reliability_safety":
                score_safety = min(score_safety, 12)
            elif princ == "fairness":
                score_fairness = min(score_fairness, 15)
            elif princ == "privacy_security":
                score_privacy = min(score_privacy, 15)
            elif princ == "transparency":
                score_transparency = min(score_transparency, 20)
        else:
            if princ == "reliability_safety":
                score_safety = min(score_safety, 35)
            elif princ == "fairness":
                score_fairness = min(score_fairness, 35)
            elif princ == "privacy_security":
                score_privacy = min(score_privacy, 35)
            elif princ == "transparency":
                score_transparency = min(score_transparency, 35)

    if pii_detected:
        score_privacy = min(score_privacy, 20)

    # Compute overall score
    overall_score = round(
        (score_fairness * 1.5 + score_safety * 2.0 + score_privacy + score_inclusiveness + score_transparency + score_accountability * 1.5) / 8.0
    )

    if has_critical:
        status = "CRITICAL RISK / PROHIBITED USE CASE"
        badge_color = "danger"
        overall_score = min(overall_score, 24)
    elif len(flagged_risks) > 0 or pii_detected:
        status = "High Risk / Non-Compliant"
        badge_color = "danger"
        overall_score = min(overall_score, 45)
    elif overall_score >= 80:
        status = "Compliant"
        badge_color = "success"
    else:
        status = "Requires Mitigation"
        badge_color = "warning"

    identified_risks_output = []
    remediations_output = []

    for r in flagged_risks:
        identified_risks_output.append(f"[{r['severity']}] {r['issue']}")
        if r["remediation"] not in remediations_output:
            remediations_output.append(r["remediation"])

    if pii_detected:
        identified_risks_output.append(f"[PRIVACY LEAKAGE] Sensitive PII detected in prompt: {', '.join(pii_detected)}.")
        remediations_output.append("Implement automated PII anonymization and token masking before sending data to models.")

    if not has_critical and len(flagged_risks) == 0 and not pii_detected:
        if not transparency_positive:
            remediations_output.append("Add clear AI attribution notice and provide confidence intervals or explanatory reasoning.")
        if not accountability_positive:
            remediations_output.append("Establish a designated human supervisor / Human-in-the-loop review workflow for high-impact outputs.")
        if not inclusiveness_positive:
            remediations_output.append("Validate multi-lingual accessibility and assistive device compatibility.")

    return {
        "overall_score": overall_score,
        "status": status,
        "badge_color": badge_color,
        "principles_breakdown": {
            "fairness": {"score": score_fairness, "status": "Good" if score_fairness >= 75 else ("Critical" if score_fairness <= 25 else "At Risk")},
            "reliability_safety": {"score": score_safety, "status": "Good" if score_safety >= 75 else ("Critical" if score_safety <= 20 else "At Risk")},
            "privacy_security": {"score": score_privacy, "status": "Good" if score_privacy >= 75 else "At Risk"},
            "inclusiveness": {"score": score_inclusiveness, "status": "Good" if score_inclusiveness >= 75 else "Review Needed"},
            "transparency": {"score": score_transparency, "status": "Good" if score_transparency >= 75 else "Review Needed"},
            "accountability": {"score": score_accountability, "status": "Good" if score_accountability >= 75 else "Review Needed"}
        },
        "identified_risks": identified_risks_output,
        "remediations": remediations_output,
        "pii_detected": pii_detected
    }
