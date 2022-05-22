from fastapi import APIRouter, Query
from starlette.responses import JSONResponse

from project.sentiment.model import SentimentBertModel

router = APIRouter()
classifier = SentimentBertModel("model/")


@router.post("/classify")
async def predict_sentiment(input_text: str = Query(..., min_length=2)):
    out_dict = classifier.predict(input_text)
    return JSONResponse(out_dict)
