# 01 Environment setup

- **Date:** 2026-11-06
- **Goal:** a working GPU Python environment outside iCloud Drive, registered as a Jupyter kernel.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Python 3.12 is installed through the `py` launcher. Plain `python` is only the Microsoft Store alias, and there is no conda.
  > [...] venv in `C:\Users\medo\venvs\aivis` (`py -3.12 -m venv`), and the Hugging Face cache in its default `~/.cache/huggingface`.
  > Install PyTorch with CUDA 12.6 wheels (`--index-url https://download.pytorch.org/whl/cu126`; not cu128, the driver is too old).



## How it was verified
- `torch 2.14.1+cu126`, `torch.cuda.is_available() == True`, device "NVIDIA GeForce RTX 3070 Ti Laptop GPU", a matrix multiply on the GPU runs.
- Kernel registered as `aivis` ("Python 3.12 (aivis)").
- Scoring all 5,794 test images against 238 prompts in fp32 takes about 55 s and peaks at 1.7 GB of VRAM (batch 256), well under 8 GB.
- Our scorer (text and image features computed once, then `logit_scale * cos`) matches CLIP's own `model(**inputs).logits_per_image` to 5.7e-6 (fp32) on 16 test images. In fp16 the difference is 0.016, so **we use fp32** (fast enough, exact).
- rembg (U^2-Net, CPU): about 0.4 s per image, so all 5,794 masks take about 40 min. It runs once in the background and is cached.
