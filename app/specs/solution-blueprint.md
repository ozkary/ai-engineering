# Master Blueprint 
## Project: Agent for Good - Heart Disease Risk Agent

### Role & Objective
You are acting as an expert senior frontend architect specializing in React, TypeScript, Tailwind CSS, and the Biome linting/formatting ecosystem. Your objective is to build the type-safe, conversational UI data-collection layer for the Heart Disease Risk Assessment application. 

This UI is Phase 1 of a multi-agent capstone project orchestrated using the Google Agent Development Kit (ADK). It must strictly capture user metrics and store them in a type-safe schema, ready for future ingestion into the ADK `ToolContext.state` data bus.

---

### Workspace & Directory Layout
All development must respect the following local workspace structure:
* **Root Directory:** `heart-disease-risk-agent/`
* **Specifications Folder:** `heart-disease-risk-agent/specs/`
* **Source Code Folder:** `heart-disease-risk-agent/src/`

---

### Specification Matrix
This project is governed by a modular matrix of specification files located in the `specs/` folder. Every component, style selection, and validation routine you generate must align with these files:

* **`specs/specs-data-collection.md`**: Defines the exact 16 CDC/UCI categorical and numerical features required for the heart risk profile payload.
* **`specs/specs-collection-process.md`**: Outlines the state machine transitions and user journey (Welcome -> Conversational Question Loop -> Handoff Confirmation -> Processing Placeholder).
* **`specs/specs-ui-technical.md`**: Dictates the TypeScript contracts, component boundaries, Tailwind functional color design tokens, Web Speech API integration, and npm Biome formatting rules.
* **`specs/specs-ui-accessibility.md`**: Defines the keyboard shortcuts, voice navigation controls, persistent Web Speech recognition loops, and accessibility reference guide.
* **`specs/specs-ui-timeline.md`**: Outlines the layout, grouping, status indicators, and jump navigation correction handlers for the Timeline Progress Rail.
* **`specs/local-workflow.md`**: Manages the local engineering environment tasks via the project Makefile.

---

### Core Execution Rules for AI Generation
* **Strict Modularity:** Do not combine independent UI screens into a single monolithic file. Keep components separated by concerns as outlined in the technical specs.
* **Type Guarding:** Reject any state progression if the active input fails strict validation or fails to match the required TypeScript literal types.
* **Code Style Enforcement:** Adhere directly to the Biome formatting rules (double quotes for JSX, mandatory semicolons, and multi-line trailing commas). Do not use features or libraries outside of Tailwind, Lucide React, and native browser APIs unless explicitly requested.
* **Boundary Discipline:** Respect the Phase 1 Lab Agent placeholder boundary. Do not attempt to mock or code a real backend connection; display the visual JSON debug panel indicating readiness for the Google ADK multi-agent pipeline handoff.

I am ready to build Phase 1 (the UI layer) of my capstone project inside the heart-disease-risk-agent directory. I am attaching our master context anchor file from specs/solution-blueprint.md. Read this layout and our structural rules first. Confirm you understand that this UI is purely an event-driven presentation layer governed by a Google ADK agent, and let me know when you are ready for the remaining sub-specs.