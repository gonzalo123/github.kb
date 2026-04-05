from github_kb.commands.chat import is_exit_command


def test_is_exit_command_accepts_common_exit_tokens() -> None:
    assert is_exit_command("exit")
    assert is_exit_command("/exit")
    assert is_exit_command(":q")


def test_is_exit_command_rejects_regular_questions() -> None:
    assert not is_exit_command("how does the github integration work?")
