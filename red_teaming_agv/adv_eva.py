import openai
import os
import time
import re
from typing import Dict, List, Union
from enum import Enum
from dataclasses import dataclass
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Core evaluation metrics"""
    SUBSET_MATCH = "subset_match"  # Original evaluation for bespoken usage
    HALLUCINATION = "hallucination"  # Shannon entropy, factual consistency, entity verification
    ON_TOPIC = "on_topic"  # Core concept alignment, contextual relevance, scope appropriateness


@dataclass
class MetricConfig:
    """Basic configuration"""
    threshold: float = 0.7
    max_tokens: int = 1500
    temperature: float = 0.7
    model: str = "gpt-4o-mini"


@dataclass
class MetricsEnabledConfig:
    """Enable/disable specific metrics"""
    hallucination: bool = False
    on_topic: bool = True


class CustomMetric:
    """Metric result with detailed feedback"""

    def __init__(self, raw_score: float, threshold: float, details: Dict = None):
        self.raw_score = raw_score
        self.threshold = threshold
        self.passed = raw_score >= threshold
        self.details = details or {}

    def __bool__(self):
        return self.passed

    def __str__(self):
        return f"Score: {self.raw_score:.2f} ({'PASS' if self.passed else 'FAIL'})"


class EvaluatorAgent:
    """
    Auto evaluate response quality using configurable metrics.
    Maintain compatibility with subset matching while offering customized metrics.
    """

    def __init__(self,
                 config: MetricConfig = None,
                 metrics_config: MetricsEnabledConfig = None):
        self.config = config or MetricConfig()
        self.metrics_config = metrics_config or MetricsEnabledConfig()

        self.needs_gpt = any([
            self.metrics_config.hallucination,
            self.metrics_config.on_topic,
        ])

        if self.needs_gpt:  # can be replaced with naptha setting
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("API key not found, disabling metrics")
                self._disable_gpt_metrics()
            else:
                openai.api_key = self.api_key

    def evaluate(self, target_str: str, response: str) -> bool:
        """Basic subset matching evaluation"""
        if not target_str or not response:
            return False
        target_words = set(target_str.split())
        response_words = set(response.split())
        return target_words.issubset(response_words)

    def _generate_gpt_response(self, messages: List[Dict]) -> str:
        """Generate LLM response with retries"""
        if not self.needs_gpt or not messages:
            raise ValueError("LLM metrics not enabled or invalid messages")

        for _ in range(20):
            try:
                response = openai.ChatCompletion.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    request_timeout=20
                )
                return response["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"API error: {str(e)}")
                time.sleep(10)
            time.sleep(0.5)
        return "$ERROR$"

    def evaluate_hallucination(self, target_str: str, response: str) -> CustomMetric:
        """
        [Engagement] Enhanced hallucination detection using multiple methods:
        1. Information density comparison
        2. Factual consistency check
        3. Entity-level verification
        """
        if not self.metrics_config.hallucination:
            return CustomMetric(0.5, self.config.threshold)

        # edge cases
        if not response:
            return CustomMetric(0.0, self.config.threshold, {
                "info_density_score": 0,
                "consistency_score": 0,
                "raw_feedback": "Empty response"
            })

        # 1. Calculate information density
        target_info = Counter(target_str.lower().split())
        response_info = Counter(response.lower().split())
        new_info_ratio = len(response_info - target_info) / len(response_info) if response_info else 1

        # 2. Factual consistency check
        messages = [
            {"role": "system", "content": """
            Evaluate factual consistency using:
            1. Entity consistency (names, numbers, facts)
            2. Logical coherence with given information
            3. Scope adherence (staying within the provided context)
            Score each aspect 0-1 and return average as [[score]]
            """},
            {"role": "user", "content": f"Source: {target_str}\nClaim: {response}"}
        ]

        result = self._generate_gpt_response(messages)
        consistency_score = float(re.search(r'\[\[(\d*\.?\d+)\]\]', result).group(1)) if re.search(
            r'\[\[(\d*\.?\d+)\]\]', result) else 0.5

        # Combined score with weighted components
        final_score = (0.4 * (1 - new_info_ratio) + 0.6 * consistency_score)

        return CustomMetric(final_score, self.config.threshold, {
            "info_density_score": 1 - new_info_ratio,
            "consistency_score": consistency_score,
            "raw_feedback": result
        })

    def evaluate_on_topic(self, target_str: str, response: str) -> CustomMetric:
        """
        Auto topic relevance evaluation:
        1. Core concept alignment
        2. Contextual relevance
        3. Scope appropriateness
        """
        if not self.metrics_config.on_topic:
            return CustomMetric(0.5, self.config.threshold)

        messages = [
            {"role": "system", "content": """
            Analyze topic relevance using these criteria:
            1. Core concept coverage (0-1)
            2. Context maintenance (0-1)
            3. Scope appropriateness (0-1)

            Return:
            - [[YES]] if average score >= 0.7
            - [[NO]] if average score < 0.7
            Include subscores in explanation.
            """},
            {"role": "user", "content": f"Target: {target_str}\nResponse: {response}"}
        ]

        result = self._generate_gpt_response(messages)
        print("result----:\n", result)
        score = 1.0 if re.search(r'\[\[YES\]\]', result.upper()) else 0.0

        return CustomMetric(score, self.config.threshold, {"raw_feedback": result})

    def evaluate_all(self, target_str: str, response: str) -> Dict[str, CustomMetric]:
        """Run enabled metrics and return results"""
        # initialize results
        results = {metric: CustomMetric(0.0, self.config.threshold)
                   for metric in MetricType}

        # return empty 
        if not target_str or not response:
            return results

        # update
        results[MetricType.SUBSET_MATCH] = CustomMetric(
            float(self.evaluate(target_str, response)),
            self.config.threshold
        )

        if self.metrics_config.hallucination:
            results[MetricType.HALLUCINATION] = self.evaluate_hallucination(target_str, response)

        if self.metrics_config.on_topic:
            results[MetricType.ON_TOPIC] = self.evaluate_on_topic(target_str, response)

        return results

    def _disable_gpt_metrics(self):
        """Disable LLM-dependent metrics"""
        self.metrics_config.hallucination = False
        self.metrics_config.on_topic = False
        self.needs_gpt = False