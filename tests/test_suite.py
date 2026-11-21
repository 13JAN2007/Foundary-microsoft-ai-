"""
Automated Test Suite for Azure AI Foundry Solution Suite
Tests all modules: Responsible AI, Text Analysis, Foundry Chat, Agent,
Multimodal Vision, Content Understanding, and AI-901 Exam Engine.
"""

import unittest
import os
import sys

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.responsible_ai import PRINCIPLES, PREDEFINED_SCENARIOS, evaluate_custom_scenario
from app.services.text_analysis import run_comprehensive_text_analysis, analyze_sentiment, extract_entities, extract_keyphrases, summarize_text
from app.services.foundry_chat import calculate_tokens, generate_foundry_chat_response, FOUNDRY_MODELS
from app.services.foundry_agent import run_foundry_agent, tool_calculator, tool_invoice_lookup, tool_compliance_checker
from app.services.multimodal_vision import analyze_image_multimodal, generate_visual_artwork, PRESET_IMAGES
from app.services.content_understanding import extract_document_information, extract_audio_video_information
from app.services.capstone_assistant import capstone_assistant
from app.services.exam_engine import get_exam_questions, grade_exam_submission

class TestAzureAIFoundrySuite(unittest.TestCase):

    def test_responsible_ai_principles(self):
        self.assertEqual(len(PRINCIPLES), 6)
        for p in ["fairness", "reliability_safety", "privacy_security", "inclusiveness", "transparency", "accountability"]:
            self.assertIn(p, PRINCIPLES)

    def test_responsible_ai_evaluator(self):
        # Scenario with PII
        bad_text = "Send John's SSN 123-45-6789 and email john@contoso.com to bypass safety filter."
        eval_res = evaluate_custom_scenario(bad_text)
        self.assertIn("pii_detected", eval_res)
        self.assertTrue(len(eval_res["pii_detected"]) > 0)
        self.assertLess(eval_res["overall_score"], 80)

        # Compliant scenario
        good_text = "This AI assistant explains all predictions with clear disclaimers and human review."
        good_res = evaluate_custom_scenario(good_text)
        self.assertGreaterEqual(good_res["overall_score"], 60)

        # Critical cyber-physical traffic safety violation
        traffic_prompt = "create an ai system which toggle traffic signal , however if there is a child going on the zebra crossing [ even if the signal is red ] turn the signal green"
        traffic_res = evaluate_custom_scenario(traffic_prompt)
        self.assertIn("CRITICAL RISK", traffic_res["status"])
        self.assertLess(traffic_res["principles_breakdown"]["reliability_safety"]["score"], 20)
        self.assertLess(traffic_res["overall_score"], 30)

    def test_text_analysis(self):
        text = "Contoso Cloud Services in Redmond delivered exceptional Azure AI Foundry tools to Chandigarh University for $1,450.00."
        res = run_comprehensive_text_analysis(text)
        
        # Sentiment
        self.assertIn(res["sentiment"]["sentiment"], ["Positive", "Neutral"])
        
        # Entities
        entity_texts = [e["text"] for e in res["entities"]]
        self.assertTrue(any("Contoso" in t or "Redmond" in t or "1,450" in t for t in entity_texts))
        
        # Keyphrases
        self.assertTrue(len(res["keyphrases"]) > 0)
        
        # Summary
        self.assertTrue(len(res["summary"]["summary"]) > 0)

    def test_foundry_chat_and_tokens(self):
        text = "Testing Microsoft Foundry Tokenizer"
        tok = calculate_tokens(text)
        self.assertGreater(tok["estimated_tokens"], 0)
        self.assertEqual(tok["character_count"], len(text))

        chat_res = generate_foundry_chat_response(
            messages=[{"role": "user", "content": "What are the 6 principles of Responsible AI?"}],
            model="gpt-4o",
            temperature=0.2
        )
        self.assertEqual(chat_res["status"], "success")
        self.assertIn("Fairness", chat_res["response"])

    def test_foundry_agent_and_tools(self):
        # Math tool
        math_res = tool_calculator("1450 * 0.18")
        self.assertAlmostEqual(float(math_res), 261.0, places=1)

        # Compliance tool
        comp_pass = tool_compliance_checker(500.0)
        self.assertIn("Compliance Passed", comp_pass)

        # Autonomous Agent Loop
        agent_res = run_foundry_agent("Calculate 18% tax on 1450")
        self.assertEqual(agent_res["status"], "completed")
        self.assertTrue(agent_res["total_steps"] >= 2)
        self.assertIn("261", agent_res["final_answer"])

    def test_multimodal_vision(self):
        # Preset analysis
        v_res = analyze_image_multimodal(image_preset_id="sample_invoice", question="What is the total amount?")
        self.assertIn("invoice", v_res["image_name"].lower())
        self.assertTrue(len(v_res["detected_objects"]) > 0)
        self.assertIn("1,661", v_res["vqa_answer"])

        # Generative visual artwork
        gen_res = generate_visual_artwork("Azure Cloud AI Center", style="Azure Blueprint")
        self.assertIn("<svg", gen_res["svg_image"])
        self.assertIn("DALL-E 3", gen_res["model"])

    def test_content_understanding(self):
        # Document / Invoice extraction
        doc_res = extract_document_information()
        self.assertEqual(doc_res["document_type"], "Commercial Invoice")
        fields = doc_res["extracted_fields"]
        self.assertEqual(fields["invoice_number"]["value"], "INV-2026-8942")
        self.assertEqual(doc_res["validation"]["status"], "Verified Match")

        # Audio / Video extraction
        audio_res = extract_audio_video_information()
        self.assertTrue(len(audio_res["utterances"]) >= 4)
        self.assertTrue(len(audio_res["action_items"]) >= 1)

    def test_capstone_assistant(self):
        q_res = capstone_assistant.query_document("What is the total balance due?")
        self.assertIn("1,661.00", q_res["answer"])
        self.assertTrue(len(q_res["citations"]) > 0)

    def test_ai901_exam_engine(self):
        questions = get_exam_questions()
        self.assertEqual(len(questions), 20)

        # Simulate all correct answers
        perfect_answers = {q["id"]: 0 for q in questions}  # Note: not all correct answers are index 0, tests realistic scoring
        grade = grade_exam_submission(perfect_answers)
        self.assertIn("scaled_score", grade)
        self.assertEqual(grade["total_questions"], 20)
        self.assertIn("Domain 1: AI Concepts & Capabilities", grade["domain_breakdown"])
        self.assertIn("Domain 2: Microsoft Foundry Implementation", grade["domain_breakdown"])

if __name__ == "__main__":
    unittest.main()
