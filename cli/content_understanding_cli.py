"""
Azure Content Understanding Client (CLI Version)
Aligned with Week 4 Day 3-4:
"Extracting information from documents and forms, images, audio and video
using Azure Content Understanding in Foundry Tools."
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.content_understanding import extract_document_information, extract_audio_video_information

def main():
    print("=" * 70)
    print(" AZURE CONTENT UNDERSTANDING EXTRACTION (AI-901)")
    print(" Author: Arnav Sharma | Chandigarh University")
    print("=" * 70)

    print("\n--- [PART 1: INVOICE / FORM EXTRACTION] ---")
    doc_res = extract_document_information()
    fields = doc_res["extracted_fields"]

    print(f"Document Type: {doc_res['document_type']}")
    print(f"Model: {doc_res['model_used']}")
    print("-" * 50)
    print(f"Invoice Number: {fields['invoice_number']['value']} (Conf: {fields['invoice_number']['confidence']})")
    print(f"Vendor:         {fields['vendor']['value']}")
    print(f"Customer:       {fields['customer']['value']}")
    print(f"Due Date:       {fields['due_date']['value']}")
    print(f"Subtotal:       {fields['subtotal']['value']}")
    print(f"Tax:            {fields['tax']['value']}")
    print(f"Discount:       {fields['discount']['value']}")
    print(f"Total Due:      {fields['total_amount']['value']}")
    print(f"Validation:     {doc_res['validation']['status']} ({doc_res['validation']['formula']})")

    print("\nItemized Line Items:")
    for itm in doc_res["line_items"]:
        print(f" • [{itm['item']}] {itm['description']} (Qty: {itm['qty']} @ ${itm['unit_price']:.2f} = ${itm['total']:.2f})")

    print("\n--- [PART 2: AUDIO / VIDEO MEETING EXTRACTION] ---")
    audio_res = extract_audio_video_information()
    print(f"Audio Service:    {audio_res['service']}")
    print(f"Duration:         {audio_res['duration']}")
    print(f"Speakers:         {', '.join(audio_res['speakers_detected'])}")
    print(f"Overall Tone:     {audio_res['overall_sentiment']}")

    print("\nExtracted Action Items:")
    for act in audio_res["action_items"]:
        print(f" • [{act['speaker']}]: {act['action']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
