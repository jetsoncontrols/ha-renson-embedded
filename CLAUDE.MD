# CLAUDE.MD

## Project Overview

This is the `ha-renson-embedded` project - a Home Assistant integration.

## Purpose

To provide Home Assistant cover entities that control a Renson Pergola motorized roof

## Architecture

Python client that communicates over REST to the built in web service on the device

## Key Technologies

Python, Scrapy, Async, Asyncio

## Development Guidelines

### Git Commit Practices

**IMPORTANT: Always commit working code before making major changes.**

Follow these practices when working on this codebase:

1. **Commit Before Major Changes**
   - Create a git commit before implementing significant new features
   - Commit before refactoring existing code
   - Commit before making breaking changes
   - This creates a safe rollback point if issues arise

2. **Commit Message Format**
   - Use clear, descriptive commit messages
   - Start with a verb in present tense (e.g., "Add", "Update", "Fix", "Refactor")
   - Keep the first line under 72 characters
   - Add detailed description in the body if needed

3. **When to Commit**
   - After completing a logical unit of work
   - Before switching to a different task
   - Before making experimental or risky changes
   - At natural breakpoints in development

4. **What to Commit**
   - Only commit working, tested code
   - Never commit broken code
   - Exclude test configuration files with credentials (`tests/test_config.json`)
   - Include all related changes in a single commit

## Testing Strategy

<!-- Describe how to run tests and what testing approaches are used -->

## Deployment

Deployed via public github repo, HACS custom repository

## Important Notes for Claude

<!-- Add specific context, gotchas, or important considerations when working on this codebase -->

---

_This file helps Claude Code understand your project better. Update it with relevant context about your codebase._
