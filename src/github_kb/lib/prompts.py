SYSTEM_PROMPT = """
You are a senior software engineer inspecting a GitHub repository.

The repository files are the source of truth.
Always explore the repository before answering.
Use the tools to inspect the directory tree, list directories, search code and read files.
Do not invent files, endpoints, behaviours or architecture that you cannot verify from the code.
Whenever possible, mention file paths in your answer so the user can verify your findings quickly.
If the repository does not provide enough evidence, say so clearly.

When auditing code:
- prioritize bugs, security issues, behavioural regressions and missing tests
- order the findings from most severe to least severe
- keep the explanation concise but concrete

When explaining a project:
- describe the execution flow
- name the important modules and responsibilities
- call out assumptions or uncertainty
"""


def build_audit_prompt(*, focus: str | None = None) -> str:
    if focus:
        return (
            "Perform a code audit of this repository. "
            f"Give extra attention to: {focus}. "
            "List findings ordered by severity, include concrete evidence from the files you inspected, "
            "and finish with a short summary of the main risks."
        )

    return (
        "Perform a code audit of this repository. "
        "List findings ordered by severity, include concrete evidence from the files you inspected, "
        "and finish with a short summary of the main risks."
    )


def build_endpoints_prompt() -> str:
    return (
        "Inspect the repository and list the API endpoints you can verify from the code. "
        "For each endpoint include the HTTP method, path, handler/controller file and a short description. "
        "If the project is not an API, say so clearly."
    )


def build_explain_prompt(*, topic: str | None = None) -> str:
    if topic:
        return (
            f"Explain how this repository works, focusing on {topic}. "
            "Describe the main execution flow, the most important modules, and how data moves through the system."
        )

    return (
        "Explain how this repository works. "
        "Describe the main execution flow, the most important modules, and how data moves through the system."
    )
