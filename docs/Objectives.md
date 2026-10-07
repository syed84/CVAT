# Annotation Analytics Objectives

These objectives define measurable outcomes for the annotation analytics
feature. Results must be collected from the submitted implementation and
recorded with raw evidence; estimates and unverified values are not evidence.

## Environment record

Complete this section before collecting measurements:

- CVAT commit SHA: `8367a143687fc6785201401515c59f53dbc3d1e7`
- Operating system: `Microsoft Windows 11 Pro`
- CPU: `11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz`
- RAM: `7.6 GB`
- Browser and version: `Chrome (VS Code integrated browser; exact build not exposed)`
- Docker/Compose versions: `Docker 29.8.2 / Compose 5.5.1`
- Dataset/task ID: `not a COCO task; available local task is 1 (test)`
- Number of imported images: `not recorded; no COCO import was performed`
- Annotation types included: `____________________________`

## MO-1 — Correct database-backed counts

**What is measured:** Whether the task annotation-count endpoint returns one
correct row per label and the correct total for a populated task.

**How it is measured:** Compare the endpoint response with an independently
verified count from the persisted CVAT annotation records. Test at least two
labels and record the request, response, task ID, and verification method.

**Target:** Every tested label and the total match the independent count.

**Conditions:** Authenticated user with task access; populated sample task;
same database state for both measurements.

**Evidence:** API response, independent count output, and test command or
database query saved in the Definition of Done.

## MO-2 — Access control

**What is measured:** Whether the endpoint protects annotation aggregates with
CVAT authentication and task-level authorization.

**How it is measured:** Make the same request unauthenticated, as an
authenticated user without access, and as an authorized user.

**Target:** The first two requests are refused with CVAT's standard error
behavior, and only the authorized request returns counts.

**Conditions:** The task exists and contains annotations; the users and their
permissions are recorded.

**Evidence:** Redacted request/response status output and automated test
results.

## MO-3 — Usable frontend states

**What is measured:** Whether the analytics UI correctly represents loading,
success, empty, and request-failure states.

**How it is measured:** Exercise the page with a populated task, an empty task,
and a controlled failed request. Verify the visible state and retry behavior.

**Target:** All four states are represented without browser-console errors, and
the error state can recover through retry.

**Conditions:** Supported browser, running local CVAT stack, and the submitted
frontend code.

**Evidence:** Component/integration test output plus screenshots or recording
timestamps.

## MO-4 — Endpoint latency

**What is measured:** Time from sending an authenticated annotation-count
request to receiving the complete successful response.

**How it is measured:** Run the identical request five times against the same
task and database state. Record every raw duration, median, and spread. State
whether measurements are cold-cache or warm-cache; do not mix conditions.

**Target:** Set a justified numeric target before measurement:
`Median of 5 runs <= 500 ms` for the local development stack. This is a
usability target for a grouped database query, not a production capacity
claim.

**Conditions:** The environment record above, local Docker stack, fixed task
size, fixed request parameters, and no intentional concurrent load.

**Evidence:** The exact command or procedure, raw five-run output, calculation,
and pass/fail conclusion.

Recorded test evidence (Django test client, test database, 2026-10-07):

```text
17.60, 12.19, 9.93, 11.06, 12.31 ms
median=12.19 ms; spread=max-min=7.67 ms; target=500 ms; PASS
```

## MO-5 — Live consistency

**What is measured:** Whether the graph reflects relevant annotation changes
and recovers after a connection interruption.

**How it is measured:** Add, edit, and delete an annotation for the selected
task; then interrupt and restore the WebSocket/network connection and repeat a
refresh-triggering change.

**Target:** The graph reaches the current server count after each mutation and
after reconnection, without duplicate updates or stale data.

**Conditions:** Authenticated authorized user, selected task, active SSE event
transport, and browser developer tools available.

**Evidence:** Automated event/reconnect tests plus a manual demonstration
reference.

## Measurement rules

- Record raw observations, not only a conclusion.
- Include task size and machine details with every performance result.
- Do not claim an objective is met when the required evidence is missing.
- If an objective is missed, record the result and cause rather than changing
  the target after measurement.
