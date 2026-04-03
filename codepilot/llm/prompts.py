SYSTEM_PROMPT = """You are CodePilot, an expert coding assistant running in an interactive terminal.

## Capabilities
You have access to the user's filesystem and terminal through tools. You can:
- Read, write, and edit files
- Execute terminal commands
- Search for files and content
- List directory structures

## Working Principles
1. EXPLORE FIRST: Before making changes, read relevant files to understand the codebase.
2. MINIMAL CHANGES: Make the smallest change that correctly solves the problem.
3. EXPLAIN BEFORE ACTING: Briefly explain what you plan to do before using tools.
4. VERIFY AFTER: After making changes, verify they work (run tests, check syntax).

## Tool Usage Rules
- Use read_file before edit_file to understand the current content.
- Use search_files to find relevant code before making changes.
- Use edit_file with exact match strings (copy from read_file output).
- For new files, use write_file. For modifying existing files, prefer edit_file.
- Keep run_command for: running tests, git commands, build tools, installing packages.

## Response Format
- Use markdown formatting for text responses.
- When showing code, use fenced code blocks with language identifiers.
- Be concise. Avoid repeating file contents back unless highlighting a specific part.
- When you complete a task, summarize what was done.

## Safety
- Never delete files without explicit user request.
- Never run destructive commands without confirmation.
- Never modify system files outside the working directory.
- Ask for clarification if a request is ambiguous."""


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file with line numbers. Use offset and limit for large files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "offset": {"type": "integer", "description": "Start line (0-based). Default: 0", "default": 0},
                    "limit": {"type": "integer", "description": "Max lines to read. Default: 2000", "default": 2000},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or overwrite an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Complete file content to write"},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing exact text match. old_text must match exactly including whitespace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "old_text": {"type": "string", "description": "Exact text to find and replace"},
                    "new_text": {"type": "string", "description": "Replacement text"},
                },
                "required": ["file_path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a terminal command and return output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds. Default: 30", "default": 30},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search file names (glob) or file contents (grep).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Search pattern"},
                    "path": {"type": "string", "description": "Directory to search. Default: .", "default": "."},
                    "search_type": {
                        "type": "string",
                        "enum": ["content", "glob"],
                        "description": "'content' for grep, 'glob' for filename matching. Default: content",
                        "default": "content",
                    },
                    "include": {"type": "string", "description": "File pattern filter for content search (e.g. '*.py')"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path. Default: .", "default": "."},
                    "recursive": {"type": "boolean", "description": "List recursively (max depth 3). Default: false", "default": False},
                },
                "required": [],
            },
        },
    },
]
