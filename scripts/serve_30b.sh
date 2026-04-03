#!/bin/bash
# Qwen3-Coder-30B-A3B-Instruct 서빙 (BF16, RTX PRO 6000 96GB)
set -e

MODEL=${1:-"belltechsoft/Qwen3-Coder-30B-A3B-Instruct"}

echo "============================================================"
echo "  Qwen3-Coder-30B-A3B-Instruct 서빙"
echo "  모델: $MODEL"
echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
echo "============================================================"

python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --dtype bfloat16 \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.90 \
    --enforce-eager \
    --attention-backend FLASHINFER \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder \
    --port 8000 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    --no-enable-log-requests
