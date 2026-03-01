from fastapi import FastAPI

app = FastAPI(title="My Awesome API")

@app.get("/")
def root():
    return {"message": "Hello from Backend!"}

@app.get("/health")
def health():
    return {"status": "ok"}