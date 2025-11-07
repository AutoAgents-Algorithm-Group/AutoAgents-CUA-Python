from fastapi import FastAPI
from pydantic import BaseModel

from autoagents_cua.client import ChatClient
from 

class ChatRequest(BaseModel):
    message: str
    model: str

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/chat")
def chat(request: ChatRequest):
    llm = ChatClient(
        client_config=ClientConfig(
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        ),
        model_config=ModelConfig(
            name=request.model,
            temperature=0.0
        ),
        enable_token_tracking=True
    )
    result = llm.invoke(request.message)
    return StreamingResponse(result)