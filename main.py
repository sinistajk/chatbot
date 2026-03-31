from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = Anthropic()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://chatbot-puce-five-76.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_relevant_chunks(question):
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=question
    )
    question_embedding = embedding_response.data[0].embedding

    results = supabase.rpc("match_documents", {
        "query_embedding": question_embedding,
        "match_count": 3
    }).execute()

    return results.data

@app.get("/")
def home():
    return {"message": "My chatbot backend is alive!"}

@app.get("/messages")
def get_messages():
    response = supabase.table("messages").select("*").order("created_at").execute()
    return {"messages": response.data}

@app.post("/chat")
def chat(user_message: str):
    try:
        chunks = get_relevant_chunks(user_message)

        context = "\n\n".join([
            f"Source: {chunk['metadata']}\n{chunk['content']}"
            for chunk in chunks
        ])

        augmented_message = f"""Use the following information to answer the question. 
Only use the provided information, and if the answer isn't in the information, say so.

Information:
{context}

Question: {user_message}"""

        supabase.table("messages").insert({"role": "user", "content": user_message}).execute()

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": augmented_message}
            ]
        )
        ai_response = response.content[0].text

        supabase.table("messages").insert({"role": "assistant", "content": ai_response}).execute()

        return {"response": ai_response}
    except Exception as e:
        return {"error": str(e)}