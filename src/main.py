from fastapi import FastAPI

from routes import summary
app = FastAPI()
app.include_router(summary.router)
