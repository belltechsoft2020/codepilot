#!/bin/bash
# Qwen3-Coder-Next 서빙 (4bit 양자화, RTX PRO 6000 96GB)
set -e

MODEL=${1:-"belltechsoft/Qwen3-Coder-Next"}

echo "============================================================"
echo "  Qwen3-Coder-Next (80B) 서빙 - 4bit 양자화"
echo "  모델: $MODEL"
echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
echo "============================================================"

python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --quantization gptq \
    --dtype float16 \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.90 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8000 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    --disable-log-requests
