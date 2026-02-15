# Modular Instructions (The Firewall)
We need two sets of instructions: one for the Views (to keep them dumb) and one for the Controllers (to guide them to Services).

- B. Controller Rules (The Logic Guardrail)
File: .github/instructions/controller-layer.md Target: Enforces that .ts files inside components/containers use Services, not direct APIs.

---
applyTo: ["src/components/**/index.ts", "src/containers/**/index.ts"]
---
## Controller Layer Rules
You are working in a **Controller File** (`controller.ts`).

## Responsibilities
- **Bridge:** You bridge the gap between the UI and the Services.
- **State Management:** Handle `useState`, `useReducer`, or Context logic here.
- **Service Orchestration:** Import reusable methods from `src/services/`.
- **Data Sync:** Prepare data for the sibling `index.tsx` view.

## Constraints
- **NO DIRECT FETCH:** Do not use `fetch` or `axios` here.
- **USE SERVICES:** All external data must come through `src/services/{{domain}}/index.ts`.
- **EXPORTS:** You must export functions/data cleanly for the sibling `.tsx` file