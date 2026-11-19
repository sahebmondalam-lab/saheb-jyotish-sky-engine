# Use it from AI assistants / AI অ্যাসিস্ট্যান্ট থেকে ব্যবহার / AI असिस्टेंट से उपयोग

Goal: you give an AI the repository link, it installs the engine, and then for any date or birth details it answers
from exact calculation instead of guessing. The credit "Saheb Jyotish Sky Engine by Saheb Mondal" travels with every answer.

## What works where (honest summary)

| Kind of AI | What works |
|---|---|
| **Coding/agent tools with a shell** (Claude Code, Codex CLI, Cursor/Windsurf agents, Gemini CLI, Cline and similar) | Paste the one-line prompt below. They clone the repo, read `AGENTS.md`, run the commands. |
| **Apps that support MCP servers** (Claude Desktop, Claude Code, Cursor, VS Code, Gemini CLI, Codex CLI and others) | Add the MCP server once (below). The AI then calls `jyotish_kundli`, `jyotish_sky`, `jyotish_panchang` as tools. |
| **Chat-only AIs with no code or tool access** (including regular ChatGPT/Grok/Gemini chat windows) | They cannot install anything from a link. Run the command yourself and paste the JSON or text report into the chat; the AI can then explain it in any language. |
| **Remote connectors** (some chat apps accept only a public HTTPS MCP URL) | Not included yet. This server speaks MCP over stdio (local). A hosted HTTP version is a possible future addition. |

Each product changes its settings often; if a step below differs, check that product's MCP documentation. The server itself follows the standard MCP stdio protocol.

## 1. One-line prompt (any AI that can run commands)

> Install and use https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine — read its AGENTS.md first. Then tell me my kundli: born YYYY-MM-DD at HH:MM in <city>.

## 2. MCP server (recommended)

Install once (needs Python 3.9+):

```bash
pip install git+https://github.com/sahebmondalam-lab/saheb-jyotish-sky-engine
```

Then register the command `jyotish` with the argument `mcp`.

**Claude Code**
```bash
claude mcp add saheb-jyotish-sky-engine -- jyotish mcp
```
(Inside a clone of this repo, the included `.mcp.json` also works: it runs `python3 -m jyotish mcp`.)

**Claude Desktop, Cursor, VS Code, Windsurf, Cline, Gemini CLI** — add to the MCP servers JSON of that app:
```json
{
  "mcpServers": {
    "saheb-jyotish-sky-engine": { "command": "jyotish", "args": ["mcp"] }
  }
}
```

**Codex CLI** (`~/.codex/config.toml`):
```toml
[mcp_servers.saheb-jyotish-sky-engine]
command = "jyotish"
args = ["mcp"]
```

If `jyotish` is not found, use the full path of the command, or `python3` with args `["-m", "jyotish", "mcp"]` and run it from a clone of the repository.

Tools exposed: `jyotish_kundli`, `jyotish_sky`, `jyotish_panchang`, `jyotish_day_events`, `jyotish_hindu_calendar`, `jyotish_festivals`, `jyotish_age`, `jyotish_places`. The server also sends the AI its rules
(never compute from memory, ask for missing birth details, credit the author, forecasts are tradition not science).

## 3. Skill for Claude

`skills/saheb-jyotish-sky-engine/SKILL.md` is a ready skill: copy the folder into your Claude skills directory
(for Claude Code: `~/.claude/skills/`), and Claude will use the engine whenever you ask about a kundli, nakshatra, panchang or the sky on a date.

## 4. Try it by hand

```bash
python3 -m jyotish kundli --date 1995-08-15 --time 14:30 --place kolkata --json
python3 -m jyotish sky --date 2026-11-16 --time 10:00 --place kolkata --lang all
```

## What the engine does not do
- It does not know "what happened in the world on that day"; it knows the sky. Use a separate source for news/history.
- Valid for 1800–2050. Details: [ACCURACY.md](ACCURACY.md).
- Readings and forecasts are traditional interpretation, not proven science.
