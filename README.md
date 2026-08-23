# 🔬 CODEX — AI Code Review Bot

> Paste code. Get a scored, categorised, actionable review in seconds — powered by Google Gemini.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?style=flat-square)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange?style=flat-square)](https://aistudio.google.com)

## Overview
CODEX reviews code across 8 dimensions: bugs, security, performance, style, best practices, test coverage, documentation, and complexity. Returns a 0–100 quality score, letter grade, categorised issues by severity, and suggested refactors.

## Supported Languages
Python · JavaScript · TypeScript · Java · C++ · Go · Rust · SQL · Bash

## Features
- **Scored reviews** — 0–100 quality score + letter grade (A+→F)
- **Severity tagging** — Critical / Warning / Info / Good
- **Configurable focus** — choose which dimensions to review
- **Strictness levels** — Lenient → Senior Engineer
- **Refactor suggestions** — improved code snippets for critical issues
- **JSON export** — full review downloadable as structured JSON
- **Review history** — all past reviews logged in session

## Quick Start
```bash
git clone https://github.com/<your-username>/code-review-bot.git
cd code-review-bot
pip install -r requirements.txt
streamlit run app.py
```

## Design
Dark terminal aesthetic · Space Grotesk + Space Mono · Cyan/Purple/Green severity colours

## Author
**Abdurrahman Abdulazeez** · abdulitz95@gmail.com · Kaduna, Nigeria

## License
MIT
