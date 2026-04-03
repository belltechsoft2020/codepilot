from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def print_tool_call(name: str, args: dict):
    if name == "run_command":
        detail = f"$ {args.get('command', '')}"
    elif name in ("read_file", "write_file", "edit_file"):
        detail = args.get("file_path", "")
    elif name == "search_files":
        detail = f"{args.get('search_type', 'content')}: {args.get('pattern', '')}"
    elif name == "list_files":
        detail = args.get("path", ".")
    else:
        detail = str(args)

    console.print(Panel(detail, title=f"[bold yellow]{name}[/bold yellow]", border_style="yellow", expand=False))


def print_tool_result(name: str, result: str, elapsed: float):
    truncated = result[:500] + "..." if len(result) > 500 else result
    console.print(f"[dim]  ({elapsed:.1f}s)[/dim]")


def print_confirm_prompt(name: str, args: dict) -> bool:
    print_tool_call(name, args)
    try:
        answer = console.input("[bold red]실행할까요? [Y/n] [/bold red]").strip().lower()
        return answer in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def print_model_status(alias: str, model_id: str):
    console.print(f"[bold cyan]모델:[/bold cyan] {alias} ({model_id})")


def print_help():
    table = Table(title="명령어", show_header=True)
    table.add_column("명령", style="cyan")
    table.add_column("설명")
    table.add_row("/quit", "종료")
    table.add_row("/clear", "대화 초기화")
    table.add_row("/model [30b|80b]", "모델 전환/확인")
    table.add_row("/tools", "사용 가능 도구")
    table.add_row("/cd <path>", "작업 디렉토리 변경")
    table.add_row("/pwd", "현재 디렉토리")
    table.add_row("/undo", "마지막 파일 변경 되돌리기")
    table.add_row("/help", "이 도움말")
    console.print(table)
