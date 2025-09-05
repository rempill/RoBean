from fastapi import FastAPI
from backend.api.beans import router as beans_router

app = FastAPI()
app.include_router(beans_router)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("backend.main:app",host="0.0.0.0",port=8000,reload=True)

