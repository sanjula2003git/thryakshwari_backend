from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



app = FastAPI(title="Thryakshwari API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your Vercel domain
    allow_methods=["*"],
    allow_headers=["*"],
)


from google import genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY,
                     api_version="v1")

doc_store = {}


class QueryRequest(BaseModel):
    doc_id: str
    query: str


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not (
        file.content_type.startswith("application/pdf")
        or file.content_type.startswith("text/")
        or file.content_type.startswith("image/")
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()

    doc_id = str(abs(hash(file.filename)))

    doc_store[doc_id] = {
        "filename": file.filename,
        "content": content,
        "mime_type": file.content_type,
    }

    return {
        "doc_id": doc_id,
        "message": "Document processed successfully"
    }


@app.post("/query")
async def query_document(request: QueryRequest):
    if request.doc_id not in doc_store:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = doc_store[request.doc_id]

    prompt = (
        "Using the provided document, answer the following question clearly:\n\n"
        f"Question: {request.query}"
    )

    response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=prompt
)

    return {"answer": response.text}




