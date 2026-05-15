# -*- conding:utf-8 -*-
"""
@author:
@license:
@software:
"""

from multiprocessing.pool import worker

from fastapi import FastAPI
from api.app_dataset import dataset_router
from api.app_model import model_router
from api.app_recommend import recommend_router
import uvicorn

app = FastAPI(title="dataset Project")

# 注册路由
app.include_router(dataset_router)
app.include_router(model_router)
app.include_router(recommend_router)


@app.get("/")
def root():
    return {"message": "Welcome to Dataset Project!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=28851,workers=1)



