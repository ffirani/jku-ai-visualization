"""CLIP as a black box: images + prompts in, image-text logits out.

`ClipScorer.logits(images, prompts)` returns exactly what CLIPModel's
`logits_per_image` returns (logit_scale * cosine similarity). To avoid
re-encoding the same prompts for every batch, text and image features are
computed once per call inside this function and multiplied right away. The
feature vectors never leave this function: they are not stored, plotted or
projected (that would be Phase II). `check_equivalence()` verifies on real
images that the result matches `model(**inputs).logits_per_image`.
"""
from __future__ import annotations

import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor

from .config import MODEL_ID


class ClipScorer:
    def __init__(self, model_id: str = MODEL_ID, device: str | None = None, fp16: bool = True):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = torch.float16 if (fp16 and self.device == "cuda") else torch.float32
        self.model = CLIPModel.from_pretrained(model_id, torch_dtype=self.dtype).to(self.device).eval()
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self._text_cache: dict[tuple[str, ...], torch.Tensor] = {}

    @torch.no_grad()
    def _text(self, prompts: list[str]) -> torch.Tensor:
        key = tuple(prompts)
        if key not in self._text_cache:
            tok = self.processor.tokenizer(list(prompts), padding=True, return_tensors="pt").to(self.device)
            t = self.model.get_text_features(**tok)
            t = t if isinstance(t, torch.Tensor) else t.pooler_output
            self._text_cache[key] = t / t.norm(dim=-1, keepdim=True)
        return self._text_cache[key]

    @torch.no_grad()
    def logits(self, images, prompts: list[str], batch_size: int = 256) -> np.ndarray:
        """(n_images, n_prompts) float32 array of CLIP logits."""
        txt = self._text(prompts)
        scale = self.model.logit_scale.exp()
        out = []
        for i in range(0, len(images), batch_size):
            batch = [im.convert("RGB") for im in images[i:i + batch_size]]
            px = self.processor(images=batch, return_tensors="pt")["pixel_values"].to(self.device, self.dtype)
            v = self.model.get_image_features(pixel_values=px)
            v = v if isinstance(v, torch.Tensor) else v.pooler_output
            v = v / v.norm(dim=-1, keepdim=True)
            out.append((scale * v @ txt.T).float().cpu().numpy())
        return np.concatenate(out, axis=0) if out else np.zeros((0, len(prompts)), np.float32)

    def dataset_logits(self, ds, prompts: list[str], name: str, batch_size: int = 256,
                       cache_dir=None) -> np.ndarray:
        """Logits of every image in a HF dataset for `prompts`, cached as .npz (logits + prompts)."""
        from .config import CACHE_DIR
        path = (cache_dir or CACHE_DIR) / f"logits_{name}.npz"
        if path.exists():
            z = np.load(path, allow_pickle=False)
            if list(z["prompts"]) == list(prompts) and len(z["logits"]) == len(ds):
                return z["logits"]
        out = []
        for i in range(0, len(ds), batch_size):
            imgs = ds[i:i + batch_size]["image"]
            out.append(self.logits(imgs, prompts, batch_size=batch_size))
        logits = np.concatenate(out)
        np.savez(path, logits=logits, prompts=np.array(prompts))
        return logits

    def array_logits(self, arr, prompts: list[str], batch_size: int = 256) -> np.ndarray:
        """Logits for a uint8 (n, 224, 224, 3) array of canvases."""
        from PIL import Image
        out = []
        for i in range(0, len(arr), batch_size):
            imgs = [Image.fromarray(np.asarray(a)) for a in arr[i:i + batch_size]]
            out.append(self.logits(imgs, prompts, batch_size=batch_size))
        return np.concatenate(out) if out else np.zeros((0, len(prompts)), np.float32)

    @torch.no_grad()
    def check_equivalence(self, images, prompts: list[str]) -> float:
        """Max abs difference to the model's own forward pass (logits_per_image)."""
        inp = self.processor(text=list(prompts), images=[im.convert("RGB") for im in images],
                             return_tensors="pt", padding=True).to(self.device)
        inp["pixel_values"] = inp["pixel_values"].to(self.dtype)
        ref = self.model(**inp).logits_per_image.float().cpu().numpy()
        return float(np.abs(ref - self.logits(images, prompts)).max())
