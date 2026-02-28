from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from rag_pipeline import create_vectorstore, create_rag_chain

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

print(" Building vector database (first time may take 30-60 seconds)...")

vectorstore = create_vectorstore()
rag_chain = create_rag_chain(vectorstore)

print(" RAG system ready!")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask", response_class=HTMLResponse)
async def ask_question(request: Request, question: str = Form(...)):

    response = rag_chain({"query": question})

    answer = response["result"]
    sources = response["source_documents"]

    source_list = "\n".join(
        [doc.metadata.get("source", "Unknown") for doc in sources]
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": answer,
        "sources": source_list
    })