# Annotation Analytics Plan

## 1. Purpose and scope

This project adds annotation analytics to CVAT. The first deliverable is a
server-backed count of annotations grouped by label for one task. The result
will be displayed in the CVAT web interface as a graph, with explicit handling
for empty data and failed requests.

The implementation will be contained in a new Django application named
`test`, as required by the assessment. Existing CVAT authentication,
permissions, annotation storage, API conventions, frontend components, and
event infrastructure will be reused rather than replaced.

The work is intentionally incremental. The API and basic page are the
acceptance gate; live updates and additional grouping are added only after that
path is correct and testable.

## 2. Repository and system research

Before changing code, inspect the checked-out CVAT commit and record the
following in the implementation notes:

- The exact commit SHA, branch, operating system, CPU, and available RAM.
- The backend application and URL registration patterns used by existing
  Django/DRF endpoints.
- The frontend route, API client, query/cache, chart, notification, and
  WebSocket/event patterns already used by CVAT.
- The permission helper or policy used by the task detail endpoint.
- The annotation models and relationships used to resolve:
  `Task -> Job/segment -> annotation -> Label`.
- The event emitted when annotations are created, updated, or deleted.

The expected data model must be verified from the checked-out source rather
than assumed. In particular, confirm the concrete shape/tag/track models,
whether counts should include shapes, tracks, and tags, and how track keyframes
are represented. The initial contract will document the selected annotation
types and will not silently mix incompatible definitions.

Useful external references for this investigation:

- [CVAT repository](https://github.com/cvat-ai/cvat)
- [CVAT REST API documentation](https://docs.cvat.ai/docs/api/)
- [CVAT architecture documentation](https://docs.cvat.ai/docs/administration/community/advanced/cvat-architecture/)
- [CVAT developer documentation](https://docs.cvat.ai/docs/api_sdk/)

## 3. Planned user-facing behavior

### 3.1 API contract

Add a task-scoped endpoint following the existing CVAT API naming and
authentication conventions. The final URL and serializer names will be aligned
with the source discovered during implementation; the planned resource is:

```text
GET /api/test/tasks/{task_id}/annotation-counts/
```

Successful response:

```json
{
  "task_id": 123,
  "group_by": "label",
  "counts": [
    {"label_id": 4, "label_name": "person", "count": 37},
    {"label_id": 7, "label_name": "car", "count": 12}
  ],
  "total": 49
}
```

Contract rules:

- Read counts from the database using a grouped query, not by downloading all
  annotations into Python.
- Return deterministic ordering, preferably descending count followed by label
  name or label ID.
- Return zero rows plus `total: 0` for a task with no supported annotations.
- Return a repository-standard 404/permission response for an inaccessible or
  nonexistent task without leaking task data.
- Return the repository-standard unauthenticated response when no login
  session/token is supplied.
- Validate the task identifier and reject unsupported query values explicitly.
- Define whether deleted, hidden, or outside-segment annotations are included.
  The implementation and tests must use the same definition.

### 3.2 Additional grouping/filter

Implement one useful extension after the plain label count is stable:

- `group_by=label` remains the default.
- Add a label filter such as `label_id=<id>` to show one class in isolation.

This choice is deliberately small and verifiable. It supports focused
investigation without changing the primary response shape or introducing a
second aggregation dimension. If CVAT already has a standard filter pattern,
reuse that pattern instead of inventing query syntax.

### 3.3 Frontend page

Add the smallest page or task-panel integration that fits the existing CVAT
navigation and permissions:

1. Load counts for the currently selected task.
2. Render a graph with one category per label and a visible count.
3. Show a clear empty state when the response contains no rows.
4. Show a clear retryable error state when the request fails.
5. Preserve loading and refresh states without displaying stale results as if
   they were current.
6. Keep labels readable and provide an accessible text/table equivalent for
   users who cannot interpret the graph alone.
7. Apply the additional label filter without bypassing server-side
   authorization.

The UI will use the existing CVAT API client, request state, notifications,
styling, and charting conventions wherever available.

### 3.4 Live updates and reconnect behavior

After the request/response page works, subscribe to the existing CVAT event
or WebSocket mechanism for annotation mutations affecting the selected task.

- Refresh or update counts only for relevant task events.
- Avoid duplicate subscriptions when navigating or re-rendering.
- Unsubscribe on page disposal.
- Display a non-blocking disconnected/reconnecting state.
- Reconnect using the existing client behavior and refresh counts after a
  successful reconnection so missed events cannot leave stale data.
- Prevent overlapping refreshes from causing an older response to overwrite a
  newer one.

If no suitable event exists, document that fact and use the least invasive
supported event integration rather than adding a parallel socket protocol.

## 4. Implementation sequence and gates

### Part A — Baseline and source mapping

- Confirm the branch and record the base commit SHA.
- Start CVAT with Docker Compose and verify login.
- Import the supplied COCO validation annotations into a task.
- Record the number of images used and confirm boxes are visible in a job.
- Map the backend, frontend, URL, permission, model, and event files.
- Commit this plan before feature code.

**Gate:** the local stack, sample task, and source map are reproducible.

### Part B — Backend application and query

- Create/register the `test` Django app according to CVAT conventions.
- Add a typed response serializer and a task-scoped view.
- Reuse CVAT's authentication and task-access permission checks.
- Implement one database aggregation query with the verified annotation
  relationships.
- Add stable ordering, empty results, filter validation, and explicit errors.
- Add backend tests for correctness, malformed input, authentication, and
  task authorization.

**Gate:** API counts match a known task and unauthorized requests are refused.

### Part C — Frontend graph

- Add the page/panel route or task integration.
- Add the API client method and typed response model.
- Render loading, success, empty, and failure states.
- Add the chosen label filter.
- Add component tests for each state and request behavior.

**Gate:** the page can be demonstrated using the imported sample task without
browser-console errors.

### Part D — Performance measurement

- Set one measurable endpoint objective before collecting results.
- Use the same task, authentication state, machine, Docker stack, and request
  shape for every run.
- Measure five runs, preserve raw output, report median and spread, and state
  whether the target was met.
- Include cold-cache versus warm-cache behavior only if both are explicitly
  labeled; do not combine them into one number.

**Gate:** another person can reproduce the measurement and reach the same
pass/fail decision.

### Part E — Live updates

- Identify the real annotation mutation event.
- Add task-scoped subscription and cleanup.
- Refresh after relevant events.
- Simulate a dropped connection and verify recovery plus resynchronization.

**Gate:** changing an annotation updates the graph, and reconnecting does not
leave it stale or duplicated.

### Part F — Evidence and review

- Run targeted backend, frontend, integration, and manual tests.
- Review the diff for dead code, debug output, commented-out blocks, and
  unrelated changes.
- Record unfinished requirements honestly.
- Update the separate objectives and definition-of-done documents after the
  implementation; do not fabricate measurements or links.
- Prepare a short recording that follows one request from the page through the
  API and database and back to the graph.

## 5. Detailed test strategy

### 5.1 Test data preparation

Use the supplied COCO 2017 validation images and
`annotations/instances_val2017.json`:

1. Start the CVAT services.
2. Create a task with a documented subset of the images.
3. Upload COCO 1.0 annotations through CVAT's normal import flow.
4. Open a job and confirm that labeled boxes are visible.
5. Record the task ID, image count, label names, and a few manually verified
   annotation totals.
6. Create a second task with no annotations for the empty-state tests.
7. Use two users: one with task access and one without task access.

Do not use a hand-written response fixture as the only test. At least one
verification must compare the endpoint to data actually stored by CVAT.

### 5.2 Backend unit and API tests

Cover these cases:

| Case | Expected evidence |
|---|---|
| One label with several annotations | Correct grouped count and total |
| Multiple labels | One deterministic row per label |
| No annotations | 200 response with empty counts and zero total |
| Label filter | Only the requested label is returned |
| Invalid task ID | Repository-standard validation/not-found response |
| Unauthenticated request | Repository-standard authentication failure |
| Authenticated user without task access | Permission denial with no count leak |
| Accessible task | Only that task's annotations are counted |
| Annotation mutation | Subsequent request reflects the new database state |
| Query efficiency | Query count/plan does not load every annotation object |

Where CVAT has existing permission fixtures and API test helpers, use them.
Assert response shape as well as values.

### 5.3 Frontend tests

Mock only the API/event boundary and test the component behavior:

- loading indicator appears while the request is pending;
- graph displays label names and counts on success;
- empty state appears for an empty response;
- error message and retry action appear for a failed request;
- retry replaces the error with current data;
- filter changes request parameters and updates the graph;
- inaccessible-task errors are not rendered as valid zero data;
- unmount removes the event listener/subscription;
- a live event refreshes the selected task only;
- reconnect triggers a refresh and does not duplicate updates.

### 5.4 Integration and manual acceptance tests

Run the complete path in a browser:

1. Log in as the authorized user.
2. Open the analytics view for the populated COCO task.
3. Compare visible values with the API response and database-backed
   verification.
4. Open the empty task and verify the empty state.
5. Stop or block the API request and verify the failure state and retry.
6. Log out and request the endpoint directly; verify refusal.
7. Log in as a user without task access; verify refusal in both API and UI.
8. Add, edit, and delete an annotation; verify the graph changes through the
   live event path.
9. Disconnect the browser's WebSocket/network, change an annotation, restore
   connectivity, and verify a resynchronized result.
10. Refresh and navigate away/back; verify there are no duplicate requests or
    subscriptions.

Capture request/response examples, screenshots or screen recording references,
and test command output as evidence in the completion documents.

### 5.5 Performance objective and measurement format

Use an endpoint objective that is measurable on the local stack, for example:

> For a populated sample task, the authenticated annotation-count endpoint
> returns a successful response within the selected latency target for the
> median of five identical runs, with the same Docker stack and database state.

The final objective must replace “selected latency target” with a justified
numeric target. Report:

- request command or browser procedure;
- task ID/data size and whether the run is cold or warm;
- CPU, RAM, operating system, and CVAT commit SHA;
- all five raw measurements;
- median and spread;
- target and pass/fail result;
- explanation of any outlier or missed target.

Do not report a single unrepeatable number.

## 6. Security and reliability boundaries

- Never accept a task ID as proof of access.
- Perform authorization before returning aggregate data.
- Do not expose labels or counts from another task in errors or logs.
- Use ORM parameters and existing serializers; never concatenate SQL.
- Bound or validate filter input.
- Avoid broad exception handling and silent zero-value fallbacks.
- Cancel or ignore stale frontend requests.
- Make WebSocket cleanup idempotent.
- Keep event-triggered refreshes task-scoped and rate-safe.

## 7. Decision record

### Chosen approach

Use a small task-scoped Django/DRF endpoint backed by a database aggregation,
then consume it from an existing CVAT frontend surface. Add one narrow label
filter and reuse CVAT's event transport for live refresh.

### Rejected approach

Do not compute counts in the browser by downloading all annotations. That
would duplicate server authorization logic, increase payload size, make
performance depend on the browser, and risk exposing annotations that the
caller should not receive. Do not introduce a separate WebSocket protocol when
CVAT already provides an event mechanism.

### Cost of the rejection

The backend query and event integration require learning CVAT's existing
models, permissions, and event conventions. The result is less code that is
specific to this feature, better authorization consistency, and a path that
can scale beyond the sample dataset.

## 8. Completion evidence checklist

- [ ] Plan committed before feature code.
- [ ] Base commit SHA, machine details, dataset/task ID, and image count
      recorded.
- [ ] API response and database-backed count comparison saved.
- [ ] Authentication and task-permission tests pass.
- [ ] Populated, empty, and failed-request UI states demonstrated.
- [ ] Additional filter demonstrated.
- [ ] Five raw performance runs, median, spread, and target reported.
- [ ] Annotation mutation updates the graph through WebSocket/event handling.
- [ ] Connection drop and recovery demonstrated.
- [ ] Unfinished requirements and known limitations listed.
- [ ] Objectives and Definition of Done documents updated with evidence.
- [ ] Recording stays within the required limit and answers K1-K4 using the
      submitted code.
