"""
Azure AI Foundry Suite - Main FastAPI Application
Based on Industrial Internship Report AI-901 by Arnav Sharma
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.services.responsible_ai import PRINCIPLES, PREDEFINED_SCENARIOS, evaluate_custom_scenario
from app.services.text_analysis import run_comprehensive_text_analysis
from app.services.foundry_chat import FOUNDRY_MODELS, calculate_tokens, generate_foundry_chat_response
from app.services.foundry_agent import run_foundry_agent, TOOLS_REGISTRY
from app.services.multimodal_vision import PRESET_IMAGES, analyze_image_multimodal, generate_visual_artwork
from app.services.content_understanding import extract_document_information, extract_audio_video_information
from app.services.capstone_assistant import capstone_assistant
from app.services.exam_engine import get_exam_questions, grade_exam_submission

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Interactive Microsoft Azure AI Fundamentals (AI-901) & Microsoft Foundry Solution Suite"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
base_dir = os.path.dirname(__file__)
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# --- Pydantic Request Models ---
class EvaluateScenarioRequest(BaseModel):
    scenario_text: str

class TextAnalysisRequest(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: str
    content: str

class FoundryChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 800
    system_prompt: Optional[str] = None

class TokenCalcRequest(BaseModel):
    text: str

class AgentRequest(BaseModel):
    goal: str

class VisionAnalyzeRequest(BaseModel):
    image_data: Optional[str] = None
    preset_id: Optional[str] = "sample_invoice"
    question: Optional[str] = None

class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "Photorealistic"
    aspect_ratio: str = "16:9"

class DocumentExtractRequest(BaseModel):
    text: Optional[str] = None

class AudioExtractRequest(BaseModel):
    transcript: Optional[str] = None

class CapstoneQueryRequest(BaseModel):
    question: str

class ExamSubmitRequest(BaseModel):
    answers: Dict[str, int]


# --- Web Page Route ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "author": settings.AUTHOR,
        "institution": settings.INSTITUTION,
        "principles": PRINCIPLES,
        "models": FOUNDRY_MODELS,
        "tools": TOOLS_REGISTRY,
        "preset_images": PRESET_IMAGES
    })


# --- API Routes ---
@app.get("/api/status")
async def api_status():
    return {
        "status": "online",
        "author": settings.AUTHOR,
        "project": settings.PROJECT_NAME,
        "has_live_azure_endpoint": bool(settings.AZURE_OPENAI_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_gemini_key": bool(settings.GEMINI_API_KEY)
    }

# 1. Responsible AI
@app.get("/api/responsible-ai/principles")
async def get_principles():
    return {"principles": PRINCIPLES}

@app.get("/api/responsible-ai/scenarios")
async def get_scenarios():
    return {"scenarios": PREDEFINED_SCENARIOS}

@app.post("/api/responsible-ai/evaluate")
async def evaluate_scenario(req: EvaluateScenarioRequest):
    return evaluate_custom_scenario(req.scenario_text)

# 2. Text Analysis
@app.post("/api/text-analysis/analyze")
async def analyze_text_route(req: TextAnalysisRequest):
    return run_comprehensive_text_analysis(req.text)

# 3. Foundry Chat & Tokens
@app.get("/api/foundry/models")
async def get_models():
    return {"models": FOUNDRY_MODELS}

@app.post("/api/foundry/calculate-tokens")
async def calc_tokens_route(req: TokenCalcRequest):
    return calculate_tokens(req.text)

@app.post("/api/foundry/chat")
async def chat_route(req: FoundryChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    return generate_foundry_chat_response(
        messages=msgs,
        model=req.model,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
        system_prompt=req.system_prompt
    )

# 4. Foundry Agent
@app.get("/api/foundry/tools")
async def get_agent_tools():
    return {"tools": TOOLS_REGISTRY}

@app.post("/api/foundry/agent")
async def run_agent_route(req: AgentRequest):
    return run_foundry_agent(req.goal)

# 5. Multimodal Vision & Image Generation
@app.get("/api/vision/presets")
async def get_vision_presets():
    return {"presets": PRESET_IMAGES}

@app.post("/api/vision/analyze")
async def analyze_vision_route(req: VisionAnalyzeRequest):
    return analyze_image_multimodal(
        image_data=req.image_data,
        image_preset_id=req.preset_id,
        question=req.question
    )

@app.post("/api/vision/generate")
async def generate_artwork_route(req: ImageGenRequest):
    return generate_visual_artwork(
        prompt=req.prompt,
        style=req.style,
        aspect_ratio=req.aspect_ratio
    )

# 6. Azure Content Understanding
@app.post("/api/content-understanding/document")
async def extract_document_route(req: DocumentExtractRequest):
    return extract_document_information(req.text)

@app.post("/api/content-understanding/audio")
async def extract_audio_route(req: AudioExtractRequest):
    return extract_audio_video_information(req.transcript)

# 7. Capstone Assistant
@app.post("/api/capstone/query")
async def capstone_query_route(req: CapstoneQueryRequest):
    return capstone_assistant.query_document(req.question)

@app.post("/api/capstone/load")
async def capstone_load_route(req: DocumentExtractRequest):
    doc = capstone_assistant.load_document(req.text)
    return {"status": "document_loaded", "document": doc}

# 8. AI-901 Practice Exam
@app.get("/api/exam/questions")
async def exam_questions_route():
    return {"questions": get_exam_questions()}

@app.post("/api/exam/submit")
async def exam_submit_route(req: ExamSubmitRequest):
    return grade_exam_submission(req.answers)
