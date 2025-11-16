---
allowed-tools: SlashCommand, Task
description: Complete plan and build workflow - creates plan then implements it
argument-hint: [implementation_request]
model: sonnet
---

# Purpose

This workflow orchestrates a complete implementation cycle by chaining two specialized commands: planning and building. It ensures implementations are well-planned and properly executed.

## Variables

USER_PROMPT: $1
USE_SUBAGENTS: true

## Instructions

- This is a sequential workflow that must be executed from top to bottom without stopping
- Each step produces outputs that feed into the next step
- Both commands must complete before the workflow is considered done
- If any step fails, report the failure and stop the workflow
- **IMPORTANT**: DO NOT STOP in between steps. Complete every step in the workflow before stopping.
- If `USE_SUBAGENTS` is true, wrap each SlashCommand with Task tool and provide complete context in each Task prompt
- When running steps in isolated subagents, pass all necessary context and information each step needs to succeed
- Each subagent is stateless - ensure you provide complete instructions and file paths in each Task prompt to properly run each SlashCommand

## Workflow

> Run the workflow in order, top to bottom. DO NOT STOP in between steps. Complete every step in the workflow before stopping.

1. **Run Planning**
   - If `USE_SUBAGENTS = true`: Task(subagent_type="general-purpose", prompt="Execute /plan with the following request: [USER_PROMPT]. Return the path to the generated plan file.")
   - If `USE_SUBAGENTS = false`: SlashCommand(`/plan [USER_PROMPT]`)
   - Creates implementation plan based on user requirements
   - Outputs the path to the generated plan file in specs/ directory, `[path_to_plan]`

2. **Run Build**
   - If `USE_SUBAGENTS = true`: Task(subagent_type="general-purpose", prompt="Execute /build with the plan file at [path_to_plan]. Implement all changes specified in the plan. Return a build completion report.")
   - If `USE_SUBAGENTS = false`: SlashCommand(`/build [path_to_plan]`)
   - Executes the implementation based on the plan from step 1
   - Makes all necessary code changes
   - Returns a build completion report

3. **Report** the complete workflow execution based on the `Report` section

4. IMPORTANT: **Continue** with the remaining workflow from your system prompt. (Push, Pull Request, etc.)

## Report

Provide a comprehensive workflow summary:

### Workflow Summary
- User request processed
- Both steps completed successfully

### Step 1: Planning
- Plan file path: [path_to_plan]
- Key planning decisions made
- Components identified

### Step 2: Build
- Files created/modified
- Implementation changes
- Build status and any issues encountered

### Final Status
✅ Complete plan and build workflow finished
- Plan created and executed
- Code implemented
