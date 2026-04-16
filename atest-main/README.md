# DND World Simulation Studio

A long-term desktop application for procedural Dungeons & Dragons world creation, simulation, and campaign management.

## Architecture Overview

- `app/ui` — PySide6 desktop interface, page navigation, maps, forms, and editor widgets.
- `app/core` — application orchestration, startup context, use cases, and command services.
- `app/domain` — business entities, rule definitions, simulation systems, event engine, map graph model, and relationship logic.
- `app/data` — persistence layer with SQLite, JSON import/export, snapshots, and migrations.
- `app/infra` — PDF export, logging, filesystem helpers, and application settings.

## Phase 1: Foundation

1. Define full project architecture.
2. Create domain model classes for world structure, entities, NPCs, relationships, and events.
3. Establish SQLite schema and initialization strategy.
4. Scaffold JSON package/serialization support.
5. Build minimal PySide6 application shell.

## Phase 2: Persistence and Export

1. Implement generic repository layer and SQLite-backed repositories.
2. Build world-level import/export and persistence services.
3. Add snapshot manager scaffolding.
4. Wire UI shell to persistence context.

## Phase 3: Hierarchical World State and Navigation

1. Create repositories for continents, empires, kingdoms, regions, and settlements.
2. Expand JSON export/import to include full hierarchical world state.
3. Implement snapshot creation and restore via persisted state packages.
4. Add dashboard and navigation UI pages in the desktop shell.
