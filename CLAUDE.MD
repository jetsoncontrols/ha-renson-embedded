# CLAUDE.MD

## Project Overview

This is the `ha-renson-embedded` project - a Home Assistant integration.

## Purpose

To provide Home Assistant cover entities that control a Renson Pergola motorized roof

## Architecture

Python client that communicates over REST to the built in web service on the device

## Key Technologies

- **Python 3.12+** - Primary language
- **aiohttp** - Async HTTP client for REST API communication
- **asyncio** - Asynchronous I/O for non-blocking operations
- **Home Assistant** - Smart home automation platform
- **pytest** - Testing framework with async support (pytest-asyncio)
- **dataclasses** - Configuration management (RensonConfig)
- **JWT** - JSON Web Token authentication
- **HTTPS/SSL** - Secure communication (self-signed certificates)

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

### Running Tests

```bash
# Run all tests
pytest tests/

# Run all tests with verbose output
pytest tests/ -v

# Run all tests with print statements visible
pytest tests/ -v -s

# Run specific test file
pytest tests/test_client.py

# Run specific test class or method
pytest tests/test_client.py::TestRensonClient::test_login
```

### Test Architecture

- **Session-scoped authentication**: One login per test session, reused across tests
- **Rate limiting protection**: 2-second delays between lifecycle tests to avoid HTTP 429
- **Test configuration**: `tests/test_config.json` (gitignored, contains device credentials)
- **Fixtures**: Defined in `tests/conftest.py`
  - `authenticated_client`: Shared authenticated client for all tests
  - `rate_limit_delay`: Prevents rate limiting on individual login tests
  - `test_config`, `renson_host`, `renson_user_type`, `renson_password`: Config access

### Test Organization

- **TestRensonClient**: Tests using shared authenticated session (fast, 7 tests)
- **TestRensonClientLifecycle**: Tests authentication behavior (3 tests with delays)

## Deployment

Deployed via public github repo, HACS custom repository

## Important Notes for Claude

### Project Structure

```
custom_components/renson_embedded/
├── api/                      # API client layer
│   ├── __init__.py          # Exports: RensonClient, RensonConfig
│   ├── client.py            # REST API client with JWT authentication
│   └── config.py            # RensonConfig dataclass
├── __init__.py              # Integration setup/teardown
├── config_flow.py           # Configuration flow UI
├── const.py                 # Constants
├── cover.py                 # Cover entity implementation
├── manifest.json            # Integration metadata
└── strings.json             # UI strings
```

### API Client

- **RensonConfig**: Dataclass with host, user_type, password, port, verify_ssl, timeout
- **RensonClient**: Manages session lifecycle (login, operations, logout)
- **Authentication**: POST /api/v1/authenticate with JWT token response
- **Device specifics**:
  - Self-signed SSL certificates (verify_ssl=False)
  - Rate limits authentication requests (429 Too Many Requests)
  - User types: "user", "professional", "renson technician"
  - No server-side logout endpoint (token is client-side only)

### Key Patterns

- **Session management**: Log in once, perform multiple operations, log out when done
- **Configuration**: Always use RensonConfig dataclass, never pass individual params
- **Testing**: Use authenticated_client fixture for most tests, avoid repeated logins
- **Import handling**: Client uses try/except for relative imports to support both HA and tests

---

_This file helps Claude Code understand your project better. Update it with relevant context about your codebase._
