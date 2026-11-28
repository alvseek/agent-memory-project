# Project Context Template

template_version: 2026-11-29-02-10

Use the body below for both backends. For a Markdown file, prepend the file header. For a DB record, pass the project, theme, description (`content_summary`) and tags as record fields and the template version as a separate argument. Do not put the file header or template version in the DB body.

**Markdown file header only:**

```markdown
---
project: "[project-name]"
tags: [tag1, tag2, tag3]
description: "[Brief description of what this context file covers]"
created: "YYYY-MM-DD"
---

# [Theme Title]
```

**Entry body:**

```markdown
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
