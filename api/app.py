import asyncio
from fastapi import FastAPI
from ai_modules.drill_map_ai.module import DrillMapAIModule
from .api_route import router as drill_map_router

app = FastAPI(title="AI Services Center")

drill_ai_module = DrillMapAIModule()
init_lock = asyncio.Lock()
init_done = False

@app.on_event("startup")
async def startup_event():
    global init_done
    async with init_lock:
        if not init_done:
            await drill_ai_module.async_init()
            init_done = True

app.include_router(drill_map_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Services Center"}