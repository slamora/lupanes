# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in any of the repositories inside this folder.

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Test-Driven Development (TDD)
- **RED**: Write a failing test FIRST that specifies the required behavior
- **GREEN**: Write MINIMAL code to make the test pass (no more, no less)
- **REFACTOR**: Clean up while keeping tests green
- NEVER write implementation code before the corresponding test exists
- Each implementation iteration follows: Test → Code → Refactor
- For bug fixes: write a test that reproduces the bug, then fix it
- Skip TDD only for trivial changes (typos, comments, formatting)

### 5. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 6. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 7. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Conventional Commits

ALL commits MUST follow the Conventional Commits specification (https://www.conventionalcommits.org/):

**Format**: `<branch-identifier> <type>[optional scope]: <description>`

Where `<branch-identifier>` is the branch name prefix (e.g., SCF-2996, SCF-3452). Always extract this from the current branch name automatically.

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc (no code change)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance (deps, tooling, config)
- `ci`: CI/CD changes

**Rules**:
- Use lowercase for type and description
- Description is imperative mood ("add" not "added" or "adds")
- No period at end of description
- Keep description under 30 characters
- There should be no body
- Footer for breaking changes: `BREAKING CHANGE: description`

**Examples**:
- `SCF-2996 feat(auth): add OAuth2 login flow`
- `SCF-2996 fix(api): handle null response in user endpoint`
- `SCF-2352 test(checkout): add integration tests for payment flow`
- `SCF-3696 refactor: extract validation logic to separate module`

**Co-Authors**:
- Only add Co-Authored-By trailer if explicitly requested by the user
- When adding co-authors, use one of these approved emails:
  - pslaulhe@gmail.com
  - santiago@ribaguifi.com
  - santiago@teal.coop
  
- Format: `Co-Authored-By: Name <email>`
- Do NOT add Claude as a co-author

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
