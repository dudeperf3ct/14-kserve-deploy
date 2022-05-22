import os

from fastapi import FastAPI
from mangum import Mangum

from project import classifier_router

stage = os.environ.get("STAGE", None)
openapi_prefix = f"/{stage}" if stage else "/"

app = FastAPI(title="Sentiment Classifier App", root_path=openapi_prefix)
app.include_router(classifier_router.router)


@app.get("/")
async def root():
    return "Sentiment Classifier (0 -> Negative and 1 -> Positive)"


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    return "dummy check! Classifier is all ready to go!"


handler = Mangum(app)
