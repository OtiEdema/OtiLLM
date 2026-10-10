"""Backend protocol and factory for fair JAIR system comparisons."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Protocol


@dataclass
class GenerationResult:
    text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_seconds: Optional[float] = None
    api_cost: Optional[float] = None
    raw: Optional[Dict] = None


class ModelBackend(Protocol):
    name: str
    def generate(self, prompt: str, *, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> GenerationResult: ...


class TransformersBackend:
    """Pinned local Hugging Face backend for publication experiments."""

    def __init__(self, model: str, revision: str | None = None, device_map: str = "auto", enable_thinking: bool = False, temperature: float = 0.0, max_tokens: int = 256):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise RuntimeError("Install transformers, torch and accelerate for the publication backend.") from e
        self.torch = torch
        self.name = f"{model}@{revision or 'main'}"
        self.model_id = model
        self.revision = revision
        self.enable_thinking = enable_thinking
        self.default_temperature = float(temperature)
        self.default_max_tokens = int(max_tokens)
        self.tokenizer = AutoTokenizer.from_pretrained(model, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            revision=revision,
            dtype="auto",
            device_map=device_map,
        )

    def generate(self, prompt: str, *, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> GenerationResult:
        from time import perf_counter

        temperature = self.default_temperature if temperature is None else float(temperature)
        max_tokens = self.default_max_tokens if max_tokens is None else int(max_tokens)

        messages = [{"role": "user", "content": prompt}]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking,
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        input_tokens = int(model_inputs.input_ids.shape[-1])

        do_sample = temperature > 0
        kwargs = {
            "max_new_tokens": max_tokens,
            "do_sample": do_sample,
        }
        if do_sample:
            kwargs["temperature"] = temperature
            kwargs["top_p"] = 0.8
        else:
            kwargs["temperature"] = None
            kwargs["top_p"] = None
            kwargs["top_k"] = None

        start = perf_counter()
        with self.torch.inference_mode():
            generated_ids = self.model.generate(**model_inputs, **kwargs)
        latency = perf_counter() - start

        output_ids = generated_ids[0][input_tokens:]
        output_tokens = int(output_ids.shape[-1])
        answer = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        return GenerationResult(
            text=answer,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_seconds=latency,
            api_cost=0.0,
            raw={"model": self.name, "enable_thinking": self.enable_thinking},
        )


class UnconfiguredBackend:
    name = "unconfigured"
    def generate(self, prompt: str, *, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> GenerationResult:
        raise RuntimeError(
            "No publication model backend is configured. Set the exact provider/model, "
            "archive its parameters, and then enable model-based systems."
        )


class SmokeBackend:
    """Deterministic backend for pipeline tests only; never use for paper results."""
    name = "smoke-test-backend"
    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> GenerationResult:
        p = prompt.lower()
        if "pride and prejudice" in p:
            text = "Jane Austen"
        elif "capital of japan" in p:
            text = "Tokyo"
        else:
            text = "Insufficient evidence."
        return GenerationResult(text=text, input_tokens=None, output_tokens=None, latency_seconds=0.0, api_cost=0.0)


def load_backend(config_path: str):
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    kind = cfg.get("kind", "unconfigured")
    if kind == "smoke":
        return SmokeBackend()
    if kind == "transformers":
        return TransformersBackend(
            model=cfg["model"],
            revision=cfg.get("revision"),
            device_map=cfg.get("device_map", "auto"),
            enable_thinking=bool(cfg.get("enable_thinking", False)),
            temperature=float(cfg.get("temperature", 0.0)),
            max_tokens=int(cfg.get("max_tokens", 256)),
        )
    if kind == "unconfigured":
        return UnconfiguredBackend()
    raise RuntimeError(
        f"Backend kind {kind!r} is not implemented in the publication branch. "
        "Add a provider adapter only after the exact model/version is selected."
    )
