import asyncio
from fastapi import FastAPI, Request

app = FastAPI()

i = 0

# 각 에이전트별 Mock 응답 스키마
MOCK_RESPONSES = {
    # Identity Agent
    "identity": {
        "characters": []
    },
    # Appearance Agent
    "appearance": {
        "characters": []
    },
    # Personality Agent
    "personality": {
        "characters": []
    },
    # Relations Agent (CharacterRelationsResult)
    "relations": {
        "characters": []
    },
    # Setting Agent
    "setting": {
        "settings": [
            {
                "name": "Unknown Location",
                "type": "location",
                "description": "Mock setting",
                "attributes": {}
            }
        ]
    },
    # Event Agent
    "event": {
        "events": []
    },
    # Relationship Analysis Agent
    "relationship": {
        "relationships": [],
        "neo4j_edges": []
    },
    # Consistency Agent
    "consistency": {
        "overall_score": 100,
        "requires_reextraction": False,
        "conflicts": [],
        "warnings": []
    },
    # Default fallback
    "default": {
        "result": "mock response"
    }
}


def detect_agent_type(body: dict) -> str:
    """요청 본문에서 에이전트 타입을 추론"""
    # Gemini API 형식에서 프롬프트 추출
    try:
        contents = body.get("contents", [])
        prompt_text = ""
        for content in contents:
            parts = content.get("parts", [])
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    prompt_text += part["text"].lower()
                elif isinstance(part, str):
                    prompt_text += part.lower()
        
        # 키워드 기반 에이전트 탐지
        if "identity" in prompt_text or "이름" in prompt_text and "캐릭터" in prompt_text:
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
    print("root test")
    return {"message": "LLM Mock Server is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.api_route("/llm", methods=["POST"])
async def mock_llm(request: Request):
    global i
    
    body = await request.json()
    agent_type = detect_agent_type(body)
    
    print(f"[{i}] Detected agent: {agent_type}")
    i += 1
    
    # 2분 대기 (벤치마크용)
    await asyncio.sleep(120)
    
    # Gemini API 응답 형식으로 반환
    mock_content = MOCK_RESPONSES.get(agent_type, MOCK_RESPONSES["default"])
    
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": str(mock_content).replace("'", '"').replace("True", "true").replace("False", "false")
                        }
                    ],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)