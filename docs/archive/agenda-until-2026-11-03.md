# Design record: agenda

> This is the final English version of the agenda. The index of discussions and plans continues in [README.md](../README.md) (Japanese).

How the DB was shaped, step by step, between the project maintainer and Claude. This file is the current summary; the record of each discussion is in [archive/](./), one file per date.

Rules for these notes:

- Every discussion is archived in `archive/<date>.md`. This file only summarises where things stand.
- **An item is closed only when it states the question, its background, the decision, and a clear, logical reason for the decision.**
- Decisions here do not change the DB by themselves. Changes are made only when the maintainer asks for them.

Last updated: 2026-11-03 (final)

## Open

- Remove the last `provisional` rows (values without any public source): find a primary source, else the secondary listing that named the value, else empty the cell. See [archive/2026-11-02.md](./2026-11-02.md).

## Postponed

| Item | Why postponed |
|---|---|
| Free tag column | Easy to add, but sits badly with "every value has a source". May be used in `local/` |
| Name (database or hub, a wiki) | Can be changed any time |
| Sustainability: can the DB be run without the maintainer? | The repository and the maintenance skill are meant to make it possible |
| Corrections from dataset authors (for example GitHub issues) | After public release |
| Help from many people (readers who check a source and report back) | After public release |
| Automatic periodic checking of values against sources; a test at registration | After the structure settles; token cost to be estimated |
| Finding stale values (days since last check) | Everything is recent now |

## Continuing questions

Questions that have no final answer and are met again while maintaining the DB.

- When to give a fact its own column and when to leave it in free text (the balance between a bloated table and an unsearchable one). Today: a column only if it applies to many datasets and is used to filter; otherwise free text with a source; start with free text and promote to a column when many datasets repeat it.
- Design for AI, whose tokens are limited: avoid repeating the same investigation; a yardstick when comparing designs.

## Closed

The decisions, with questions, backgrounds and reasons, are in [archive/2026-10-31.md](./2026-10-31.md), [archive/2026-11-01.md](./2026-11-01.md) and [archive/2026-11-02.md](./2026-11-02.md). In short: the DB is a tertiary source that creates no facts (R-1 and onward in the earlier notes are superseded by them); sources are documents with a publisher and a type; values are decided by evidence rows and disagreement is kept; the implementation contributes four things through the recipe readme's `## The data` section; project decisions live in `local/`; a label set has one basis; a person's check is recorded only through a merged pull request; `unknown` means the whole document was read.
