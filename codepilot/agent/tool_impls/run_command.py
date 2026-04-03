from __future__ import annotations

import subprocess


def run_command(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += result.stderr

        if not output.strip():
            output = "(출력 없음)"

        if result.returncode != 0:
            output += f"\n[종료 코드: {result.returncode}]"

        # 출력 크기 제한
        if len(output) > 10000:
            output = output[:10000] + f"\n\n... (출력이 10,000자를 초과하여 잘림)"

        return output

    except subprocess.TimeoutExpired:
        return f"[오류] 명령 실행 시간 초과 ({timeout}초)"
    except Exception as e:
        return f"[오류] 명령 실행 실패: {e}"
