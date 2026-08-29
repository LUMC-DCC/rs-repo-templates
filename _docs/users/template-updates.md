# Template updates

Generated repositories retain their template relationship through
`.copier-answers.yml`. Commit that file and do not edit it manually.

## Apply a release

Start from a clean Git working tree, use the same prepared generator environment
as initial generation, and run:

```bash
copier check-update
copier update --trust
```

`check-update` reports whether a newer compatible tagged release is available.
`update` reuses recorded answers and prompts for any new questions. Pass a
reviewed `--vcs-ref` when your institution pins a specific release.

The template contains finalization tasks, so trust is required. Confirm that
`.copier-answers.yml` points to the expected LUMC-DCC repository before running
an update.

## Review the result

Copier compares the old template, the project, and the new template. It keeps
project-only files, preserves intentional deletions, and merges edits to
generated files when possible. If both the project and template changed the
same lines, normal conflict markers may remain.

1. Review `git status` and `git diff`.
2. Resolve every `<<<<<<<`, `=======`, and `>>>>>>>` block.
3. Run the generated project's local checks and tests.
4. Commit the updated answers file together with the reviewed changes.

The generated pre-commit configuration checks for unresolved conflict markers.
It does not decide which side of a conflict is correct.

Change template answers through `copier update --trust`, interactively or with
the calling service's structured data. Do not use `copier recopy` for routine
updates: it renders directly over the project without the same three-way update
comparison. Do not change `template_type` during an update; changing language
scaffolds requires a deliberate project migration.
