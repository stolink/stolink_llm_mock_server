import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

i = 0

MOCK_RESPONSES = {
    "identity": {"characters": []},
    "appearance": {"characters": []},
    "personality": {"characters": []},
    "relations": {"characters": []},
    "setting": {
        "settings": [{
            "name": "Unknown Location",
            "type": "location",
            "description": "Mock setting",
            "attributes": {}
        }]
    },
    "event": {"events": []},
    "relationship": {"relationships": [], "neo4j_edges": []},
    "consistency": {
        "overall_score": 100,
        "requires_reextraction": False,
        "conflicts": [],
        "warnings": []
    },
    "default": {"characters": []}
}


def detect_agent_type(body: dict) -> str:
    """요청 본문에서 에이전트 타입을 추론"""
    try:
        prompt_text = ""
        
        # ✅ AI 백엔드가 보내는 형식: {"messages": [{"role": "user", "content": "..."}]}
        messages = body.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict) and "content" in msg:
                prompt_text += msg["content"].lower()
        
        # Gemini API 형식도 지원 (fallback)
        contents = body.get("contents", [])
        for content in contents:
            parts = content.get("parts", [])
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    prompt_text += part["text"].lower()
                elif isinstance(part, str):
                    prompt_text += part.lower()
        
        print(f"[DEBUG] Prompt preview: {prompt_text[:200]}...")
        
        if "identity" in prompt_text or ("이름" in prompt_text and "캐릭터" in prompt_text):
            return "identity"
        elif "appearance" in prompt_text or "외모" in prompt_text or "visual" in prompt_text:
            return "appearance"
        elif "personality" in prompt_text or "성격" in prompt_text or "trait" in prompt_text:
            return "personality"
        elif "relationship" in prompt_text and "social network" in prompt_text:
            return "relationship"
        elif "relations" in prompt_text:
            return "relations"
        elif "setting" in prompt_text or "배경" in prompt_text or "location" in prompt_text:
            return "setting"
        elif "event" in prompt_text or "사건" in prompt_text:
            return "event"
        elif "consistency" in prompt_text or "conflict" in prompt_text or "일관성" in prompt_text:
            return "consistency"
    except Exception as e:
        print(f"Agent detection error: {e}")
    
    return "default"


@app.get("/")
async def root():
    return {"message": "LLM Mock Server is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.api_route("/llm", methods=["POST"])
async def mock_llm(request: Request):
    global i
    
    body = await request.json()
    agent_type = detect_agent_type(body)
    
    print(f"[{i}] Detected agent: {agent_type}")
    i += 1
    
    await asyncio.sleep(30)
    
    mock_content = MOCK_RESPONSES.get(agent_type, MOCK_RESPONSES["default"])
    
    # ✅ AI 백엔드가 기대하는 형식: {"content": "JSON 문자열"}
    return {
        "content": json.dumps(mock_content, ensure_ascii=False)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)