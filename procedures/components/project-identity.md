+++
format_version = 2
id = "project-identity"
kind = "component"
title = "project-identity"
description = "Resolve the project name for a selected directory."
+++

Run `git rev-parse --show-toplevel` in the selected directory. If it is inside a repository, use the repository name from `git remote get-url origin`, removing a trailing `.git` (for example, `asgard-deploy.git` → `asgard-deploy`). If there is no `origin`, use the repository root’s folder name. Outside Git, use the selected directory’s folder name.
