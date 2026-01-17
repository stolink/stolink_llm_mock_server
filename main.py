import asyncio
from fastapi import FastAPI, Request

app = FastAPI()

i = 0

@app.get("/")
async def root():
    return {"message": "LLM Mock Server is running"}


@app.api_route("/llm", methods=["POST"])
async def catch_all(request: Request):
    global i
    """
    모든 POST 요청에 대해 2분 대기 후 더미 응답을 반환합니다.
    """
    print("Request received at /llm")
    
    # 필요하다면 요청 본문을 읽어서 로그를 찍거나 응답에 포함할 수 있습니다.
    body = await request.json()
    print(f"Request body: {body}" + str(i))
    i += 1

    await asyncio.sleep(120)
    
    return {
        "status": "success",
        "message": "Mock LLM response after 2 minutes",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
