import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.ai_modules.drill_map_ai.module import DrillMapAIModule
from app.api.drill_map import router as drill_map_router

drill_ai_module = DrillMapAIModule()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化
    try:
        if not drill_ai_module.init_done:
            await drill_ai_module.async_init()
            drill_ai_module.init_done = True
        print("AI 模組初始化完成")
    except Exception as e:
        print(f"AI 模組初始化失敗: {e}")
        raise
    
    yield


# init_lock = asyncio.Lock()
# @app.on_event("startup")
# async def startup_event():
#     async with init_lock:
#         if not drill_ai_module.init_done:
#             await drill_ai_module.async_init()
#             drill_ai_module.init_done = True

app = FastAPI(
    title="AI Services Center", 
    description="A collection of AI modules for various tasks",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(drill_map_router)

def get_drill_ai_module():
    return drill_ai_module

@app.get("/", summary="Root Endpoint", description="Welcome message for the AI Services Center")
async def root():
    return {"message": "Welcome to the AI Services Center"}