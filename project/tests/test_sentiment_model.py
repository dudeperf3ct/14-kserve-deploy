import pytest
import torch

from project.sentiment.model import SentimentBertModel


def test_load_model():
    classifier = SentimentBertModel("distilbert-base-uncased-finetuned-sst-2-english")
    assert classifier.model is not None


def test_load_tokenizer():
    classifier = SentimentBertModel("distilbert-base-uncased-finetuned-sst-2-english")
    assert classifier.tokenizer is not None


def test_model_input_shape():
    classifier = SentimentBertModel("distilbert-base-uncased-finetuned-sst-2-english")
    text = "this is positive sentence!"
    inputs = classifier.tokenizer(text, return_tensors="pt")
    input_id = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    assert input_id.shape == attention_mask.shape


def test_model_output_shape():
    classifier = SentimentBertModel("distilbert-base-uncased-finetuned-sst-2-english")
    text = "this is positive sentence!"
    inputs = classifier.tokenizer(text, return_tensors="pt")
    input_id = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    with torch.no_grad():
        outputs = classifier.model(input_id, attention_mask)
    out_logits = outputs.logits
    assert out_logits.shape == torch.Size([1, 2])


@pytest.mark.parametrize(
    "text, key, score",
    [("i like you", "pos_score", 0.98), ("i hate you", "neg_score", 0.98)],
)
def test_predictions(text, key, score):
    classifier = SentimentBertModel("distilbert-base-uncased-finetuned-sst-2-english")
    assert classifier.predict(text=text)[key] >= score
