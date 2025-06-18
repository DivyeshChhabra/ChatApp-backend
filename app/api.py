# Importing Python Libraries.
import uuid
# Importing FastAPI Libraries.
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth.auth_bearer import JWTBearer

from .model import ConversationRequest

from workflow import graph


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to Platform!"}


@app.post("/api/v1/chat/{chat_id}", dependencies=[Depends(JWTBearer())])
async def graph_stream(chat_id: str, request: ConversationRequest):
    body = request.body

    chat_id = chat_id if chat_id != '1' else uuid.uuid4()

    run_id = str(uuid.uuid4())
    config = {"run_id": run_id, "configurable": {"thread_id": chat_id}}

    user_input = {
        "initial_question": body
    }

    for update in graph.stream(
        user_input,
        config=config,
        stream_mode="updates",
    ):
        if "get_answer" in update:
            response = update['get_answer']['answer']
            return response