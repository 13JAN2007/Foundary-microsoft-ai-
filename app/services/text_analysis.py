"""
Text Analysis Service
Aligned with AI-901 Exam Objective:
"Identify common AI workloads: text analysis techniques (keyword extraction,
entity detection, sentiment analysis, summarization); implement lightweight application with text analysis."
"""

from typing import Dict, List, Any, Optional
import re
import json
from collections import Counter
from app.config import settings

POSITIVE_WORDS = {
    "good", "great", "excellent", "superb", "outstanding", "exceptional", "positive", "success", "successful",
    "milestone", "approved", "completed", "benefit", "best", "effective", "strong", "reliable", "secure",
    "delighted", "recommend", "complies", "compliant", "profit", "gain", "upgrade", "valuable", "perfect"
}

NEGATIVE_WORDS = {
    "bad", "poor", "fail", "failed", "failure", "error", "bug", "issue", "concern", "risk", "risks",
    "vulnerability", "bias", "biased", "hallucination", "hallucinate", "penalty", "violation", "violate",
    "unreliable", "unsafe", "insecure", "breach", "reject", "rejected", "discrepancy", "damage", "harm"
}

def split_into_sentences(text: str) -> List[str]:
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw_sentences if s.strip() and len(s.strip()) > 5]

def analyze_sentiment(text: str) -> Dict[str, Any]:
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", text)]
    total_words = max(1, len(words))
    
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    
    diff = pos_count - neg_count
    polarity = round(max(-1.0, min(1.0, diff / max(2, pos_count + neg_count))), 3) if (pos_count + neg_count) > 0 else 0.0
    subjectivity = round(min(1.0, (pos_count + neg_count) / max(5, total_words * 0.15)), 3)
    
    if polarity > 0.1:
        sentiment = "Positive"
        badge = "success"
    elif polarity < -0.1:
        sentiment = "Negative"
        badge = "danger"
    else:
        sentiment = "Neutral"
        badge = "secondary"

    sentences = split_into_sentences(text)
    sentences_analysis = []
    for s in sentences[:5]:
        s_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", s)]
        s_pos = sum(1 for w in s_words if w in POSITIVE_WORDS)
        s_neg = sum(1 for w in s_words if w in NEGATIVE_WORDS)
        s_p = round((s_pos - s_neg) / max(1, s_pos + s_neg), 2) if (s_pos + s_neg) > 0 else 0.0
        sentences_analysis.append({
            "sentence": s,
            "polarity": s_p,
            "label": "Positive" if s_p > 0.1 else ("Negative" if s_p < -0.1 else "Neutral")
        })

    confidence = round(min(0.99, max(0.65, 0.6 + abs(polarity) * 0.35)), 2)

    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "badge": badge,
        "confidence": confidence,
        "sentence_breakdown": sentences_analysis
    }

def extract_entities(text: str) -> List[Dict[str, Any]]:
    entities = []

    # 1. Emails
    for m in re.finditer(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text):
        entities.append({"text": m.group(), "category": "EMAIL", "confidence": 0.99, "start": m.start(), "end": m.end()})

    # 2. Currency / Money
    for m in re.finditer(r"[\$€£₹]\s?[\d,]+(?:\.\d{2})?|\b[\d,]+(?:\.\d{2})?\s?(?:USD|EUR|GBP|INR|dollars)\b", text, re.IGNORECASE):
        entities.append({"text": m.group(), "category": "MONEY", "confidence": 0.95, "start": m.start(), "end": m.end()})

    # 3. Dates
    for m in re.finditer(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", text, re.IGNORECASE):
        entities.append({"text": m.group(), "category": "DATE", "confidence": 0.92, "start": m.start(), "end": m.end()})

    # 4. Known Organizations & Tech Products
    known_orgs = ["Microsoft", "Azure", "Contoso", "Google", "Amazon", "OpenAI", "Foundry", "Chandigarh University", "Pearson"]
    for org in known_orgs:
        for m in re.finditer(rf"\b{re.escape(org)}\b", text, re.IGNORECASE):
            entities.append({"text": m.group(), "category": "ORGANIZATION", "confidence": 0.94, "start": m.start(), "end": m.end()})

    # 5. Known Locations
    known_locs = ["Redmond", "Washington", "Gharuan", "Chandigarh", "Mohali", "Punjab", "USA", "India"]
    for loc in known_locs:
        for m in re.finditer(rf"\b{re.escape(loc)}\b", text, re.IGNORECASE):
            entities.append({"text": m.group(), "category": "LOCATION", "confidence": 0.90, "start": m.start(), "end": m.end()})

    # 6. Persons
    for m in re.finditer(r"\b(?:Dr\.|Prof\.|Mr\.|Ms\.)?\s?[A-Z][a-z]+ [A-Z][a-z]+\b", text):
        name = m.group().strip()
        if not any(e["text"].lower() == name.lower() for e in entities):
            entities.append({"text": name, "category": "PERSON", "confidence": 0.88, "start": m.start(), "end": m.end()})

    unique_entities = []
    seen = set()
    for e in entities:
        key = (e["text"].lower(), e["category"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    return unique_entities

def extract_keyphrases(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    stopwords = set([
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "is", "are", "was", "were", "be", "been", "this", "that", "it", "as", "our", "all", "we",
        "shall", "not", "have", "has", "had", "will", "would", "can", "could", "may", "per"
    ])

    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text) if w.lower() not in stopwords]
    counts = Counter(words)

    words_all = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]
    bigrams = []
    for i in range(len(words_all) - 1):
        w1, w2 = words_all[i].lower(), words_all[i+1].lower()
        if w1 not in stopwords and w2 not in stopwords:
            bigrams.append(f"{words_all[i].capitalize()} {words_all[i+1].capitalize()}")

    bigram_counts = Counter(bigrams)

    combined = []
    for phrase, count in bigram_counts.most_common(top_n):
        combined.append({
            "phrase": phrase,
            "frequency": count,
            "relevance_score": round(min(1.0, 0.5 + count * 0.15), 2)
        })

    if len(combined) < top_n:
        for word, count in counts.most_common(top_n - len(combined)):
            cap = word.capitalize()
            if not any(c["phrase"].lower() == word for c in combined):
                combined.append({
                    "phrase": cap,
                    "frequency": count,
                    "relevance_score": round(min(0.85, 0.35 + count * 0.1), 2)
                })

    return combined[:top_n]

def summarize_text(text: str, max_sentences: int = 3) -> Dict[str, Any]:
    sentences = split_into_sentences(text)
    if len(sentences) <= max_sentences:
        summary_sentences = sentences
    else:
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]
        freq = Counter(words)

        scored = []
        for idx, s in enumerate(sentences):
            s_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", s)]
            score = sum(freq.get(w, 0) for w in s_words) / (len(s_words) + 1)
            if idx == 0 or idx == len(sentences) - 1:
                score *= 1.3
            scored.append((score, idx, s))

        scored.sort(reverse=True, key=lambda x: x[0])
        top_selected = sorted(scored[:max_sentences], key=lambda x: x[1])
        summary_sentences = [s[2] for s in top_selected]

    summary_text = " ".join(summary_sentences)
    bullet_points = [f"• {s}" for s in summary_sentences]

    word_count_orig = len(text.split())
    word_count_summary = len(summary_text.split())
    reduction = round((1 - (word_count_summary / max(1, word_count_orig))) * 100, 1)

    return {
        "summary": summary_text,
        "bullet_points": bullet_points,
        "original_word_count": word_count_orig,
        "summary_word_count": word_count_summary,
        "compression_ratio": f"{reduction}% reduction"
    }

def analyze_with_gemini_if_available(text: str) -> Optional[Dict[str, Any]]:
    has_gemini = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)
    if not has_gemini:
        return None

    sys_prompt = (
        "You are an expert NLP Text Analytics engine aligned with Microsoft Azure AI Language & AI-901 objectives.\n"
        "Analyze the provided input text and return strictly valid JSON matching this schema:\n"
        "{\n"
        '  "sentiment": {\n'
        '    "sentiment": "Positive" | "Negative" | "Neutral",\n'
        '    "polarity": float between -1.0 and 1.0,\n'
        '    "subjectivity": float between 0.0 and 1.0,\n'
        '    "badge": "success" | "danger" | "secondary",\n'
        '    "confidence": float between 0.0 and 1.0,\n'
        '    "sentence_breakdown": [{"sentence": str, "polarity": float, "label": "Positive"|"Negative"|"Neutral"}]\n'
        '  },\n'
        '  "entities": [\n'
        '    {"text": str, "category": "ORGANIZATION"|"PERSON"|"LOCATION"|"DATE"|"MONEY"|"EMAIL"|"TECH"|"EVENT", "confidence": float}\n'
        '  ],\n'
        '  "keyphrases": [\n'
        '    {"phrase": str, "frequency": int, "relevance_score": float}\n'
        '  ],\n'
        '  "summary": {\n'
        '    "summary": str,\n'
        '    "bullet_points": [str],\n'
        '    "original_word_count": int,\n'
        '    "summary_word_count": int,\n'
        '    "compression_ratio": str\n'
        '  }\n'
        "}\n"
    )

    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
        gemini_candidates = [
            "gemini-flash-latest",
            "gemini-3-flash-preview",
            "gemini-flash-lite-latest",
            "gemini-3.1-flash-lite",
            "gemini-2.5-flash"
        ]
        for m in gemini_candidates:
            try:
                resp = client.models.generate_content(
                    model=m,
                    contents=f"{sys_prompt}\n\nAnalyze this text:\n\"\"\"{text}\"\"\""
                )
                if resp and resp.text:
                    raw = resp.text.strip()
                    if raw.startswith("```"):
                        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
                    data = json.loads(raw)
                    data["engine"] = f"Google Gemini Live Cloud AI ({m})"
                    return data
            except Exception as model_err:
                err_str = str(model_err)
                if "getaddrinfo failed" in err_str or "11001" in err_str:
                    print("[Network Offline] Google Gemini unreachable for NLP text analysis. Using local engine.")
                    break
                continue
    except Exception as e:
        print(f"Gemini NLP initialization error: {e}")

    return None

def run_comprehensive_text_analysis(text: str) -> Dict[str, Any]:
    # 1. Try Gemini API first when key is configured
    gemini_result = analyze_with_gemini_if_available(text)
    if gemini_result:
        return gemini_result

    # 2. Local Fallback Engine
    return {
        "sentiment": analyze_sentiment(text),
        "entities": extract_entities(text),
        "keyphrases": extract_keyphrases(text, top_n=8),
        "summary": summarize_text(text, max_sentences=3),
        "engine": "Local NLP Text Analysis Engine (Offline)"
    }
