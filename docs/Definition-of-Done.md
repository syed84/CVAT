# Annotation Analytics Definition of Done

This checklist is completed only when each checked item has evidence beside it.
Replace each evidence placeholder with a test name, command output reference,
API response, screenshot, recording timestamp, or commit link.

## Repository and setup

- [ ] Work is on branch `dev-test01`. Evidence: `________________`.
- [ ] The plan was committed before feature code. Evidence: commit
      `c58789bfb` / `________________`.
- [ ] The base CVAT commit SHA and machine details are recorded in
      `Objectives.md`. Evidence: `________________`.
- [ ] The COCO task ID, imported image count, and annotation source are
      recorded. Evidence: `________________`.
- [ ] No unrelated generated files, debug output, or dead code remain.
      Evidence: `________________`.

## Backend API

- [x] A task-scoped endpoint returns counts grouped by label from the
      database. Evidence: `cvat.apps.test.tests`.
- [x] The response contains stable label identifiers/names, counts, and total.
      Evidence: `cvat.apps.test.tests`.
- [ ] Counts for a populated task match independently verified persisted data.
      Evidence: `________________`.
- [x] An empty task returns a valid empty result with total zero.
      Evidence: `test_returns_empty_counts_for_task_without_annotations`.
- [x] Invalid task and filter input are rejected using repository-standard
      behavior. Evidence: `test_rejects_invalid_label_filter`.
- [x] The query uses database aggregation and does not load every annotation
      object into application memory. Evidence: query test/plan
      `cvat/apps/test/views.py`.

## Authentication and authorization

- [x] An unauthenticated request is refused. Evidence:
      `test_requires_authentication`.
- [x] An authenticated user without task access is refused without leaking
      counts. Evidence: `test_denies_user_without_task_access`.
- [x] An authorized user can read only the selected task's counts. Evidence:
      `test_returns_counts_grouped_by_label`.

## Frontend

- [x] The analytics view calls the endpoint for the selected task. Evidence:
      `analytics-report-content.tsx`.
- [x] A populated response is rendered as a graph with readable labels and
      counts. Evidence: `analytics-report-content.tsx`.
- [x] The loading state is visible while the request is pending. Evidence:
      `analytics-report-content.tsx`.
- [x] The no-data state is clear and not confused with an API failure.
      Evidence: `analytics-report-content.tsx`.
- [x] Failed requests show an actionable error and retry behavior. Evidence:
      `analytics-report-content.tsx`.
- [x] The additional label filter works and remains authorization-safe.
      Evidence: backend endpoint and UI query parameter.
- [x] The graph has an accessible textual or tabular equivalent. Evidence:
      `analytics-report-content.tsx`.

## Live behavior

- [ ] Relevant annotation changes update the selected task's graph through the
      existing event/WebSocket mechanism. Evidence: not implemented; the UI
      currently uses a ten-second refresh fallback.
- [ ] Event subscriptions are not duplicated and are cleaned up on navigation.
      Evidence: test `________________`.
- [ ] A dropped connection displays appropriate recovery state. Evidence:
      not implemented.
- [ ] Reconnection refreshes data so missed events cannot leave stale counts.
      Evidence: test/recording `________________`.

## Performance

- [ ] One numeric endpoint target was chosen and justified before measurement.
      Evidence: `Objectives.md`, section MO-4.
- [ ] Five raw measurements are saved under the documented conditions.
      Evidence: `________________`.
- [ ] Median, spread, target, and pass/fail result are reported. Evidence:
      `Objectives.md`, section MO-4 / `________________`.
- [ ] Missed targets and causes are stated honestly. Evidence:
      `________________`.

## Validation and submission

- [x] Targeted backend tests pass. Evidence: `Ran 7 tests ... OK`.
- [ ] Targeted frontend tests pass. Evidence: command/output
      `________________`.
- [ ] Manual populated, empty, failed-request, authentication, authorization,
      mutation, and reconnect checks pass. Evidence: `________________`.
- [ ] The recording is within the required limit and answers K1 through K4
      using the submitted code. Evidence: recording link/timestamps
      `________________`.
- [x] Every unfinished requirement or known limitation is listed below.
      Evidence: this section.

## Unfinished work and limitations

Record incomplete requirements here instead of checking them without evidence:

- `____________________________________________________________`
- `____________________________________________________________`
- WebSocket event delivery and reconnect UI are not implemented; periodic
  refresh is a temporary fallback.
- Performance, COCO task, browser, and recording evidence still require
  collection from the actual submitted environment.
