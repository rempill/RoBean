from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from api.beans import router as beans_router
from db.database import get_db_path

app: FastAPI = FastAPI()

origins: list[str] = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    origins.append(frontend_url)
    origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok", "db": str(get_db_path())}


app.include_router(beans_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
