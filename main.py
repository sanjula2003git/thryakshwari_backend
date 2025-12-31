from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

# --------------------
# App setup
# --------------------
app = FastAPI(title="Thryakshwari API")

# --------------------
# Groq client
# --------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)

# --------------------
# Temporary document store
# --------------------
doc_store = {}

class QueryRequest(BaseModel):
    doc_id: str
    query: str

# --------------------
# Upload endpoint
# --------------------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not (
        file.content_type.startswith("application/pdf")
        or file.content_type.startswith("text/")
        or file.content_type.startswith("image/")
    ):
        raise HTTPException(400, "Unsupported file type")

    content = await file.read()
    doc_id = str(hash(file.filename))

    doc_store[doc_id] = {
        "filename": file.filename,
        "content": content.decode(errors="ignore")
    }

    return {"doc_id": doc_id, "message": "Document uploaded successfully"}

# --------------------
# Query endpoint
# --------------------
@app.post("/query")
async def query_document(request: QueryRequest):
    if request.doc_id not in doc_store:
        raise HTTPException(404, "Document not found")

    document_text = doc_store[request.doc_id]["content"]

    prompt = f"""
Use the following document to answer the question.

DOCUMENT:
{document_text}

QUESTION:
{request.query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return {"answer": response.choices[0].message.content}








