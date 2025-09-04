from __future__ import annotations

from typing import Dict, List

AI_KEYWORDS: List[str] = [
    "artificial intelligence",
    "AI",
    "machine learning",
    "ML",
    "deep learning",
    "NLP",
    "natural language processing",
    "LLM",
    "large language model",
    "computer vision",
    "generative",
    "reinforcement learning",
]

CYBER_KEYWORDS: List[str] = [
    "cybersecurity",
    "information security",
    "infosec",
    "SOC",
    "security analyst",
    "threat",
    "incident response",
    "security engineer",
    "penetration test",
    "red team",
    "blue team",
    "SIEM",
]


CATEGORIES: Dict[str, List[str]] = {
    "ai": AI_KEYWORDS,
    "cyber": CYBER_KEYWORDS,
}

