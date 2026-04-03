import click

from codepilot.cli.commands.chat import chat


@click.group()
def cli():
    """CodePilot - 대화형 코딩 어시스턴트"""
    pass


cli.add_command(chat)


if __name__ == "__main__":
    cli()
