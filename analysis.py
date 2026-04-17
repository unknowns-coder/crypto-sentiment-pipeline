from transformers import pipeline


def create_sentiment_analyzer(model_name="ProsusAI/finbert"):
    return pipeline("sentiment-analysis", model=model_name)


def get_sentiment_score(headlines_list, analyzer):
    if not headlines_list:
        return "NEUTRAL", 0.0

    total_weighted_score = 0.0
    for headline in headlines_list:
        result = analyzer(headline)[0]
        label, confidence = result["label"], result["score"]

        if label == "POSITIVE":
            total_weighted_score += confidence
        elif label == "NEGATIVE":
            total_weighted_score -= confidence

    avg_mood = total_weighted_score / len(headlines_list)
    if avg_mood > 0.05:
        return "BULLISH", abs(avg_mood)
    if avg_mood < -0.05:
        return "BEARISH", abs(avg_mood)

    return "NEUTRAL", abs(avg_mood)
