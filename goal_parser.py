
import spacy
import re

nlp = spacy.load("en_core_web_sm")

def parse_goal(goal, deadline, daily_hours):
    doc = nlp(goal)

    keywords = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ("NOUN", "VERB", "PROPN")
        and not token.is_stop
    ]

    return {
        "goal": goal.strip(),
        "deadline": deadline,
        "daily_hours": float(daily_hours),
        "keywords": list(dict.fromkeys(keywords))
    }
