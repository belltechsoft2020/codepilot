#!/bin/bash
# CodePilot RunPod 환경 설정
# RTX PRO 6000 (96GB VRAM)
set -euo pipefail

echo "=== CodePilot RunPod Setup ==="

# 1. 시스템 패키지
echo "[1/5] 시스템 패키지 설치..."
apt-get update -qq && apt-get install -y -qq git tmux htop

# 2. Python 패키지
echo "[2/5] Python 패키지 설치..."
pip install --upgrade pip
pip install vllm httpx rich click pyyaml huggingface-hub[cli]

# 3. 모델 다운로드
echo "[3/5] 모델 다운로드..."
echo "  30B 모델 다운로드 중..."
huggingface-cli download belltechsoft/Qwen3-Coder-30B-A3B-Instruct \
    --local-dir /workspace/models/Qwen3-Coder-30B-A3B-Instruct

echo "  80B 모델 다운로드 중..."
huggingface-cli download belltechsoft/Qwen3-Coder-Next \
    --local-dir /workspace/models/Qwen3-Coder-Next

# 4. 프로젝트 설정
echo "[4/5] CodePilot 설치..."
cd /workspace
if [ ! -d "codepilot" ]; then
    mkdir codepilot
fi

# config.yaml 생성
cat > /workspace/codepilot/config.yaml << 'YAML'
llm:
  base_url: http://localhost:8000/v1
  active_model: 30b
  models:
    30b: /workspace/models/Qwen3-Coder-30B-A3B-Instruct
    80b: /workspace/models/Qwen3-Coder-Next
  max_tokens: 8192
  temperature: 0.3

safety:
  confirm_file_write: true
  confirm_delete: true
  command_timeout: 30
  blocked_commands:
    - "rm -rf /"
    - "mkfs"
    - "dd if="

agent:
  max_iterations: 15
YAML

# 5. vLLM 시작 (30B 기본)
echo "[5/5] vLLM 서빙 시작 (30B)..."
tmux new-session -d -s vllm "bash /workspace/codepilot/scripts/serve_30b.sh /workspace/models/Qwen3-Coder-30B-A3B-Instruct"

echo ""
echo "=== 설정 완료 ==="
echo "  vLLM: tmux attach -t vllm"
echo "  실행: cd /workspace/codepilot && codepilot chat"
echo "  모델 전환: /model 80b (세션 내)"
echo ""
echo "  GPU 상태: nvidia-smi"
echo "  vLLM 확인: curl http://localhost:8000/v1/models"
