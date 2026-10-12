# Project Context Template

template_version: 2026-10-12-18-18

The structure of a project-context entry. Storage-agnostic: the markdown backend writes it to the scope directory as `[theme].md`; the DB backend passes it as the `content` of a `create_context_entry` or `update_context_entry` call. Copy the fenced block below and fill its placeholders.

```markdown
---
project: "[project-name]"
tags: [tag1, tag2, tag3]
description: "[Brief description of what this context file covers]"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# [Theme Title]

## **PURPOSE**
[Brief description of what this context file covers and when to use it]

## **QUICK REFERENCE**
[Key commands, URLs, credentials locations, or cheat sheet — the stuff you need fast]

## **DETAILS**
[Detailed knowledge content organized by sub-topics]

### [Sub-topic 1]
[Content]

### [Sub-topic 2]
[Content]

## **SOURCES**
[Where this knowledge came from — documentation links, team decisions, discovery sessions]
```
