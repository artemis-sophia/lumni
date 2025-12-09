# CLI Design Guidelines and Principles

This document compiles authoritative CLI design guidelines and best practices from industry sources including clig.dev, PatternFly CLI Handbook, and modern CLI development practices.

## Table of Contents

1. [Command Structure and Naming](#command-structure-and-naming)
2. [Help and Documentation](#help-and-documentation)
3. [Error Handling](#error-handling)
4. [Output Formatting](#output-formatting)
5. [Configuration and State Management](#configuration-and-state-management)
6. [User Experience Enhancements](#user-experience-enhancements)
7. [Accessibility Considerations](#accessibility-considerations)
8. [Security Practices](#security-practices)
9. [Testing and Quality Assurance](#testing-and-quality-assurance)
10. [Performance Considerations](#performance-considerations)
11. [References](#references)

---

## Command Structure and Naming

### Consistency
- **Use uniform verb-noun patterns**: Commands should follow predictable patterns like `app start`, `app stop`, `app status`
- **Group related commands**: Organize related functionalities under subcommands (e.g., `app user add`, `app user remove`)
- **Standard verbs**: Employ common verbs that users expect:
  - `list` - Display multiple items
  - `show` / `get` - Display a single item
  - `create` / `add` - Create new resources
  - `update` / `edit` - Modify existing resources
  - `delete` / `remove` - Remove resources
  - `start` / `stop` / `restart` - Control processes
  - `status` - Check current state

### Clarity
- **Short and memorable**: Keep command names concise but descriptive
- **Avoid abbreviations**: Unless they're universally understood (e.g., `ls`, `rm`)
- **Use kebab-case**: For multi-word commands (e.g., `show-key` not `showKey`)

### Examples
```bash
# Good
lumni start
lumni stop
lumni status
lumni usage show
lumni rates list
lumni providers list

# Avoid
lumni s
lumni st
lumni show-usage-stats
```

---

## Help and Documentation

### Comprehensive Help
- **Every command needs `--help`**: All commands and subcommands should support `--help` or `-h`
- **Detailed descriptions**: Include clear explanations of what each command does
- **Usage examples**: Provide practical examples in help text
- **Option descriptions**: Clearly explain what each option does and its default value

### Documentation Structure
- **Usage syntax**: Show the command structure clearly
- **Arguments**: List required and optional arguments
- **Options**: Document all flags and their purposes
- **Examples**: Include 2-3 real-world usage examples
- **Exit codes**: Document what exit codes mean

### Example Help Output
```bash
$ lumni start --help
Usage: lumni start [OPTIONS]

Start the Lumni API Gateway server

Options:
  --host TEXT          Host to bind to [default: 0.0.0.0]
  --port INTEGER        Port to bind to [default: 8000]
  --foreground / --background
                        Run in foreground or background [default: background]
  --reload              Enable auto-reload (development mode)
  --show-key            Show full unified API key
  --skip-selection      Skip provider/model selection
  --help                Show this message and exit

Examples:
  lumni start                    # Start in background
  lumni start --foreground      # Start in foreground
  lumni start --port 8080       # Start on custom port
  lumni start --reload          # Development mode with auto-reload
```

---

## Error Handling

### Error Messages
- **Clear and actionable**: Tell users what went wrong and how to fix it
- **Context-aware**: Include relevant context (file paths, values, etc.)
- **Avoid technical jargon**: Use language users understand
- **Suggest solutions**: When possible, provide next steps

### Exit Codes
Follow standard Unix exit code conventions:
- `0` - Success
- `1` - General error
- `2` - Misuse of shell command
- `126` - Command invoked cannot execute
- `127` - Command not found
- `128` - Invalid exit argument
- `130` - Script terminated by Ctrl+C

### Error Message Examples
```bash
# Bad
Error: Failed

# Good
Error: Configuration file not found at 'config.json'
  Run 'lumni settings menu' to create a configuration file
  Or specify a custom path with --config /path/to/config.json
```

### Validation
- **Validate early**: Check inputs before processing
- **Validate completely**: Check all constraints, not just the first one
- **Provide specific feedback**: Tell users exactly what's wrong

---

## Output Formatting

### Human vs Machine Readable
- **Support both formats**: Provide human-readable default output and machine-readable options (JSON, XML, YAML)
- **Use `--json` flag**: Allow users to get structured output for scripting
- **Consistent structure**: Maintain uniform output formats across commands

### Formatting Best Practices
- **Tables for lists**: Use tables for structured data
- **Colors for status**: Use colors to indicate success (green), warnings (yellow), errors (red)
- **Icons/symbols**: Use visual indicators (✓, ✗, ⚠) for quick scanning
- **Progress indicators**: Show progress bars or spinners for long operations
- **Whitespace**: Use appropriate spacing for readability

### Output Examples
```bash
# Human-readable (default)
$ lumni providers list
┌──────────┬─────────┬────────┐
│ Provider │ Status  │ Models │
├──────────┼─────────┼────────┤
│ openai   │ Enabled │ 5      │
│ anthropic│ Enabled │ 3      │
│ gemini   │ Disabled│ 2      │
└──────────┴─────────┴────────┘

# Machine-readable
$ lumni providers list --json
[
  {"provider": "openai", "status": "enabled", "models": 5},
  {"provider": "anthropic", "status": "enabled", "models": 3},
  {"provider": "gemini", "status": "disabled", "models": 2}
]
```

### Color Guidelines
- **Green**: Success, enabled, healthy
- **Yellow**: Warnings, degraded, pending
- **Red**: Errors, disabled, unhealthy
- **Blue**: Information, neutral status
- **Dim/Gray**: Secondary information, metadata

---

## Configuration and State Management

### Configuration Sources (Priority Order)
1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration files
4. Default values (lowest priority)

### Configuration Files
- **Sensible defaults**: Provide working defaults out of the box
- **Standard locations**: Use predictable paths:
  - `~/.config/appname/` (Linux/macOS)
  - `%APPDATA%\appname\` (Windows)
  - Project-local: `./config.json` or `./.appname/`
- **Documentation**: Clearly document all configuration options

### Environment Variables
- **Naming convention**: Use `APPNAME_OPTION_NAME` format (e.g., `LUNMI_API_KEY`)
- **Documentation**: List all supported environment variables in docs
- **Override capability**: Allow CLI flags to override env vars

### State Management
- **Predictable storage**: Store state in standard locations
- **PID files**: For process management, use standard locations
- **Log files**: Store logs in accessible, documented locations
- **Cache**: Use appropriate cache directories

---

## User Experience Enhancements

### Interactive Features
- **Interactive prompts**: For complex configurations, use interactive menus
- **Confirmation prompts**: For destructive operations, always confirm
- **Input validation**: Validate as users type when possible
- **Autocomplete**: Provide shell completion for commands and options

### Progress Feedback
- **Progress bars**: For operations with known duration
- **Spinners**: For indeterminate operations
- **Status messages**: Keep users informed during long operations
- **ETA**: When possible, show estimated time remaining

### User Feedback
- **Success messages**: Confirm successful operations
- **Warning messages**: Alert users to potential issues
- **Error messages**: Clearly indicate failures
- **Quiet mode**: Support `--quiet` flag for minimal output
- **Verbose mode**: Support `--verbose` flag for detailed output

### Examples
```bash
# Progress indicator
Starting server... [████████████████████] 100%

# Status message
✓ Server started successfully
  PID: 12345
  URL: http://localhost:8000
  Logs: ~/.lumni/logs/server.log

# Confirmation prompt
Are you sure you want to delete provider 'openai'? [y/N]:
```

---

## Accessibility Considerations

### Screen Reader Support
- **Clear output**: Use plain text descriptions, not just colors
- **Structured output**: Use consistent formatting that screen readers can parse
- **Alternative text**: Provide text alternatives for visual indicators

### Inclusive Design
- **Color-blind friendly**: Don't rely solely on color to convey information
- **Keyboard navigation**: Support full keyboard navigation in interactive modes
- **Clear labels**: Use descriptive labels for all interactive elements

### Output Accessibility
- **Text alternatives**: Always provide text alongside icons/symbols
- **Consistent structure**: Maintain predictable output structure
- **No assumptions**: Don't assume users can see colors or special characters

---

## Security Practices

### Sensitive Data Handling
- **Never log secrets**: Don't include passwords, API keys, or tokens in logs
- **Mask in output**: Show masked versions of sensitive data (e.g., `sk-...abcd`)
- **Secure storage**: Store sensitive data securely (encrypted when possible)
- **Environment variables**: Prefer env vars over config files for secrets

### Input Validation
- **Sanitize inputs**: Validate and sanitize all user inputs
- **Prevent injection**: Protect against command injection attacks
- **Type checking**: Validate data types and ranges
- **File permissions**: Set appropriate file permissions for config files

### Best Practices
- **Least privilege**: Request only necessary permissions
- **Secure defaults**: Use secure default configurations
- **Warnings**: Warn users about insecure configurations
- **Documentation**: Document security considerations

---

## Testing and Quality Assurance

### Testing Strategy
- **Unit tests**: Test individual commands and functions
- **Integration tests**: Test command interactions
- **End-to-end tests**: Test complete workflows
- **Error case testing**: Test error handling and edge cases

### Test Coverage
- **Happy paths**: Test normal operation
- **Error paths**: Test error conditions
- **Edge cases**: Test boundary conditions
- **Invalid inputs**: Test with malformed inputs

### Quality Checks
- **Linting**: Use linters to catch common issues
- **Type checking**: Use type checkers (mypy, pyright)
- **Code review**: Review CLI changes carefully
- **User testing**: Get feedback from real users

---

## Performance Considerations

### Startup Time
- **Lazy imports**: Import modules only when needed
- **Minimal dependencies**: Keep dependencies to a minimum
- **Fast initialization**: Avoid heavy operations at startup
- **Caching**: Cache expensive computations

### Operation Performance
- **Progress feedback**: Show progress for long operations
- **Cancellation**: Allow users to cancel long operations (Ctrl+C)
- **Timeouts**: Set reasonable timeouts for network operations
- **Parallel operations**: When possible, run operations in parallel

### Resource Usage
- **Memory efficiency**: Be mindful of memory usage
- **CPU efficiency**: Optimize CPU-intensive operations
- **Network efficiency**: Minimize network calls
- **Disk usage**: Be considerate of disk space

---

## Additional Best Practices

### Command Aliases
- **Common aliases**: Provide aliases for frequently used commands
- **Shortcuts**: Support common shortcuts (e.g., `ls` for `list`)

### Global Options
- **Consistent flags**: Use consistent flags across commands:
  - `--help` / `-h`: Show help
  - `--version` / `-v`: Show version
  - `--verbose`: Verbose output
  - `--quiet` / `-q`: Quiet output
  - `--json`: JSON output
  - `--config`: Config file path

### Version Management
- **Version command**: Always provide a `--version` flag
- **Version in help**: Include version in main help output
- **Semantic versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)

### Shell Completion
- **Bash completion**: Provide bash completion scripts
- **Zsh completion**: Provide zsh completion scripts
- **Fish completion**: Consider fish shell completion
- **Auto-install**: Offer to install completion during setup

### Logging
- **Structured logs**: Use structured logging for machine parsing
- **Log levels**: Support different log levels (DEBUG, INFO, WARN, ERROR)
- **Log rotation**: Implement log rotation for long-running processes
- **Separate streams**: Use stderr for errors, stdout for data

---

## Command Design Checklist

When designing a new command, ensure:

- [ ] Command name follows verb-noun pattern
- [ ] Command is grouped logically with related commands
- [ ] `--help` provides comprehensive information
- [ ] Help includes usage examples
- [ ] All options are documented
- [ ] Error messages are clear and actionable
- [ ] Exit codes follow conventions
- [ ] Output supports both human and machine formats
- [ ] Colors/icons have text alternatives
- [ ] Sensitive data is masked
- [ ] Input validation is comprehensive
- [ ] Progress feedback for long operations
- [ ] Confirmation for destructive operations
- [ ] Works in both interactive and non-interactive modes
- [ ] Tested with various inputs and edge cases

---

## References

### Authoritative Sources
1. **clig.dev** - Command Line Interface Guidelines
   - https://clig.dev/
   - Open-source guide to writing better command-line programs

2. **PatternFly CLI Handbook**
   - https://www.patternfly.org/developer-resources/cli-handbook/
   - Best practices for designing consistent and developer-friendly CLIs

3. **Modern CLI Development**
   - https://moderncli.dev/
   - Modern guide to command-line interface development

### Additional Resources
- **The Art of Command Line** - https://github.com/jlevy/the-art-of-command-line
- **12 Factor CLI Apps** - Principles for building modern CLI applications
- **Google Shell Style Guide** - https://google.github.io/styleguide/shellguide.html
- **Microsoft Command-Line Standards** - Industry best practices

### Tools and Libraries
- **Typer** - Modern Python CLI framework (used in this project)
- **Rich** - Rich text and beautiful formatting (used in this project)
- **Click** - Python package for creating command line interfaces
- **Cobra** - Go library for CLI applications
- **Commander.js** - Node.js command-line interfaces

---

## Implementation Notes for Lumni CLI

### Current Strengths
- ✅ Good command structure with subcommands
- ✅ Rich output formatting with tables and colors
- ✅ Interactive menus for complex operations
- ✅ Consistent error handling
- ✅ Help text for all commands
- ✅ Sensitive data masking (API keys)

### Areas for Enhancement
- [ ] Add `--json` output option to all list/show commands
- [ ] Add `--version` global flag
- [ ] Enable shell completion (Typer supports this)
- [ ] Add more usage examples in help text
- [ ] Add `--verbose` and `--quiet` global flags
- [ ] Add progress indicators for long operations
- [ ] Add command aliases for common operations
- [ ] Improve error messages with actionable suggestions

---

*Last updated: 2024*
*Based on industry best practices and authoritative CLI design guidelines*


