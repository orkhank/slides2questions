from typing import Literal, Optional
import transformers
import torch
import functools


@functools.lru_cache(maxsize=1)
def get_llama_pipeline() -> transformers.pipelines.TextGenerationPipeline:
    model_id = "meta-llama/Meta-Llama-3-8B"
    return transformers.pipeline(  # type: ignore
        "text-generation",
        model=model_id,
        model_kwargs={
            "torch_dtype": torch.bfloat16,
            "quantization_config": {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.bfloat16,
            },
        },
        device_map="auto",
    )


@functools.lru_cache(maxsize=1)
def get_gemma_pipeline() -> transformers.pipelines.TextGenerationPipeline:
    model = "google/gemma-1.1-2b-it"
    return transformers.pipeline(  # type: ignore
        "text-generation",
        model=model,
        model_kwargs={
            "torch_dtype": torch.bfloat16,
            "quantization_config": {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.bfloat16,
            },
        },
        device_map="auto",
    )


def get_gemma_response(
    input_text: str,
    *,
    max_new_tokens: int = 99999,
    temperature: float = 0.7,
    top_k: int = 50,
    top_p: float = 0.95,
    do_sample: bool = True,
    streamer: Optional[Literal["TextStreamer"]] = None,
    **kwargs,
) -> str:
    pipeline = get_gemma_pipeline()

    messages = [
        {"role": "user", "content": input_text},
    ]
    prompt = pipeline.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    outputs = pipeline(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        streamer=transformers.TextStreamer(pipeline.tokenizer) if streamer else None,
    )
    return outputs[0]["generated_text"][len(prompt) :]
