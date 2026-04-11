import os

import click
from rich.console import Console
from rich.markdown import Markdown

from codepilot.config import load_config
from codepilot.cli.display import (
    print_tool_call, print_tool_result, print_confirm_prompt,
    print_model_status, print_help,
)

console = Console()


@click.command()
@click.option("--model", default=None, help="시작 모델 (30b 또는 80b)")
@click.option("--workdir", default=None, help="작업 디렉토리")
def chat(model, workdir):
    """대화형 코딩 어시스턴트를 시작합니다."""
    cfg = load_config()

    if model:
        cfg.llm.active_model = model
    if workdir:
        os.chdir(workdir)

    console.print("[bold]CodePilot[/bold] - 대화형 코딩 어시스턴트")
    console.print(f"작업 디렉토리: {os.getcwd()}")

    # LLM 클라이언트
    from codepilot.llm.client import LLMClient
    model_id = cfg.llm.models.get(cfg.llm.active_model, cfg.llm.active_model)
    llm = LLMClient(
        base_url=cfg.llm.base_url,
        model=model_id,
        max_tokens=cfg.llm.max_tokens,
        temperature=cfg.llm.temperature,
    )
    print_model_status(cfg.llm.active_model, model_id)

    # 도구 등록
    from codepilot.agent.tools import ToolRegistry
    from codepilot.agent.tool_impls.file_read import read_file
    from codepilot.agent.tool_impls.file_write import write_file, undo_last_write
    from codepilot.agent.tool_impls.file_edit import edit_file, undo_last_edit
    from codepilot.agent.tool_impls.file_search import search_files
    from codepilot.agent.tool_impls.file_list import list_files
    from codepilot.agent.tool_impls.run_command import run_command

    registry = ToolRegistry()
    registry.register("read_file", read_file)
    registry.register("write_file", write_file)
    registry.register("edit_file", edit_file)
    registry.register("search_files", search_files)
    registry.register("list_files", list_files)
    registry.register("run_command", run_command)

    # Agent
    from codepilot.agent.core import Agent
    agent = Agent(
        llm=llm,
        tools=registry,
        safety=cfg.safety,
        max_iterations=cfg.agent.max_iterations,
        on_tool_call=lambda name, args: print_confirm_prompt(name, args),
        on_tool_result=lambda name, result, elapsed: print_tool_result(name, result, elapsed),
    )

    history: list[dict] = []
    console.print("질문을 입력하세요. /help로 명령 목록 확인\n")

    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]").strip()
            user_input = user_input.encode("utf-8", errors="replace").decode("utf-8")
        except (EOFError, KeyboardInterrupt):
            console.print("\n종료합니다.")
            break

        if not user_input:
            continue

        # 슬래시 명령 처리
        if user_input.startswith("/"):
            handled = _handle_command(user_input, cfg, llm, registry, history, undo_last_write, undo_last_edit)
            if handled == "quit":
                break
            continue

        # Agent 실행
        try:
            answer = agent.run(user_input, history=history)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": answer})
            console.print()
            console.print(Markdown(answer))
            console.print()
        except Exception as e:
            console.print(f"[red]오류: {e}[/red]")

    llm.close()


def _handle_command(cmd, cfg, llm, registry, history, undo_write, undo_edit):
    parts = cmd.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    if command in ("/quit", "/exit"):
        console.print("종료합니다.")
        return "quit"

    elif command == "/clear":
        history.clear()
        console.print("[dim]대화 기록이 초기화되었습니다.[/dim]")

    elif command == "/history":
        if not history:
            console.print("[dim]대화 기록이 없습니다.[/dim]")
        else:
            for msg in history:
                role = msg["role"]
                content = msg["content"][:80]
                console.print(f"[dim]{role}: {content}...[/dim]")

    elif command == "/model":
        if arg and arg in cfg.llm.models:
            cfg.llm.active_model = arg
            model_id = cfg.llm.models[arg]
            llm.switch_model(model_id)
            print_model_status(arg, model_id)
        else:
            model_id = cfg.llm.models.get(cfg.llm.active_model, "")
            print_model_status(cfg.llm.active_model, model_id)
            console.print(f"  사용 가능: {', '.join(cfg.llm.models.keys())}")

    elif command == "/tools":
        tools = registry.list_tools()
        console.print(f"[bold]사용 가능 도구:[/bold] {', '.join(tools)}")

    elif command == "/cd":
        if arg:
            try:
                os.chdir(os.path.expanduser(arg))
                console.print(f"작업 디렉토리: {os.getcwd()}")
            except Exception as e:
                console.print(f"[red]오류: {e}[/red]")
        else:
            console.print(f"사용법: /cd <path>")

    elif command == "/pwd":
        console.print(os.getcwd())

    elif command == "/undo":
        result1 = undo_write()
        result2 = undo_edit()
        if "없습니다" not in result1:
            console.print(result1)
        elif "없습니다" not in result2:
            console.print(result2)
        else:
            console.print("[dim]되돌릴 변경 사항이 없습니다.[/dim]")

    elif command == "/help":
        print_help()

    else:
        console.print(f"[dim]알 수 없는 명령: {command}. /help로 확인[/dim]")

    return None
