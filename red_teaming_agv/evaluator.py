
class EvaluatorAgent:
    def evaluate(self, target_str: str, response: str) -> bool:
        target_words = set(target_str.split())

        response_words = set(response.split())

        return target_words.issubset(response_words)