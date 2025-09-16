from fastapi import FastAPI

from api.beans import router as beans_router
from db.database import init_db, get_db_path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins= [
    "http://localhost" #default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def health():
    return {"status": "ok", "db": str(get_db_path())}

app.include_router(beans_router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("backend.main:app",host="0.0.0.0",port=8000,reload=True)
