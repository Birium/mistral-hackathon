from pydantic import BaseModel


class CostDetails(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


class ModelConfig:
    def __init__(
        self,
        model_id: str,
        input_price_per_m: float,
        output_price_per_m: float,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        self.model_id = model_id
        self.input_price_per_m = input_price_per_m
        self.output_price_per_m = output_price_per_m
        self.base_url = base_url

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> CostDetails:
        input_cost = (prompt_tokens / 1_000_000) * self.input_price_per_m
        output_cost = (completion_tokens / 1_000_000) * self.output_price_per_m
        return CostDetails(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
        )


# Fast model for MVP — cheap and supports tool calling
DEFAULT_MODEL = ModelConfig(
    model_id="google/gemini-3-flash-preview",
    input_price_per_m=0.50,
    output_price_per_m=3.0,
)