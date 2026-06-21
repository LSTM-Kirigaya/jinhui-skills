# Module Playbook

## Purpose

This file maps recurring admin needs into reusable module patterns. Use it when deciding what pages, APIs, and backend responsibilities a new module should have.

## 1. Feedback Work-Order Module

### Page shape

- list page with search, status filter, and pagination
- optional detail drawer or detail page
- status summary cards on overview page

### API family

- `GET /feedback`
- `GET /feedback/stats`
- `PATCH /feedback/:id/status`

### Service responsibilities

- load work orders
- validate status transitions
- store resolution notes
- optionally trigger user notification or reward follow-up

### Common extensions

- attachment preview
- source page or client info display
- trace or request correlation fields

## 2. Content Report / Review Module

### Page shape

- queue list page
- detail page with reported content snapshot
- review panel with resolution and destructive actions

### API family

- `GET /reports`
- `GET /reports/stats`
- `GET /reports/:id`
- `PATCH /reports/:id/status`
- optional `POST /reports/:id/delete-target`
- optional `DELETE /reports/:id`

### Service responsibilities

- resolve report status
- persist moderation notes
- coordinate deletion or cleanup of target content
- optionally message reporters or affected users

### Common extensions

- reward points for valid reports
- prebuilt copy actions for user IDs
- snapshot rendering for text and images

## 3. Dataset Benchmark Module

### Page shape

- dataset sample list
- sample create/edit modal
- benchmark run list
- benchmark run detail with per-sample results

### API family

- `GET /benchmark/datasets/batches`
- `GET /benchmark/datasets/samples`
- `GET /benchmark/datasets/samples/:id`
- `POST /benchmark/datasets/samples`
- `PATCH /benchmark/datasets/samples/:id`
- `DELETE /benchmark/datasets/samples/:id`
- `POST /benchmark/runs`
- `GET /benchmark/runs`
- `GET /benchmark/runs/:id`
- `POST /benchmark/runs/:id/cancel`

### Service responsibilities

- manage dataset metadata
- validate sample payloads
- create and track runs
- aggregate result summaries

### Common extensions

- batch names
- label types
- run comparison views
- cancellation and retry support

## 4. Resource Catalog A

Use this for resource entities with medium-sized editable schemas and rich filtering.

### Page shape

- searchable list
- detail or side editor
- create, update, delete actions

### API family

- `GET /resources-a`
- `GET /resources-a/:id`
- `POST /resources-a`
- `PATCH /resources-a/:id`
- `DELETE /resources-a/:id`

### Service responsibilities

- normalize searchable fields
- validate edit payloads
- manage activation or review states

### Common extensions

- image preview
- derived display name fields
- raw evidence or OCR text storage

## 5. Resource Catalog B

Use this for a second catalog with similar CRUD shape but different business rules.

### Page shape

- table + filters
- modal or page editor
- empty state and preview support

### API family

- `GET /resources-b`
- `GET /resources-b/:id`
- `POST /resources-b`
- `PATCH /resources-b/:id`
- `DELETE /resources-b/:id`

### Service responsibilities

- maintain catalog records
- validate review status
- coordinate with storage or secondary indexes if needed

### Common extensions

- publish/unpublish states
- imported source references
- bulk edits later

## 6. Rule Or Energy Library Module

Use this for editable policy tables, scoring libraries, conversion rules, or domain constants that need admin review.

### Page shape

- searchable list
- detail editor
- selective update operations rather than full CRUD if records are seeded

### API family

- `GET /rules`
- `GET /rules/:id`
- `PATCH /rules/:id`

### Service responsibilities

- validate numeric ranges
- preserve auditability for changes
- enforce review or activation rules

### Common extensions

- alias tables
- review status
- reason fields for edits

## Module Selection Heuristics

Choose module type by behavior, not by original business name:

- queue with status transitions -> feedback or report module
- editable business data with search -> resource catalog
- experimentation or comparison -> benchmark module
- curated constants or rule tables -> rule library

If a new need does not fit these patterns, design it as a new module family instead of forcing it into the wrong one.
