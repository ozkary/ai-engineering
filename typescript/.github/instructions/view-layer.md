
# Modular Instructions (The Firewall)
We need two sets of instructions: one for the Views (to keep them dumb) and one for the Controllers (to guide them to Services).

- A. View Rules (The UI Guardrail)
File: .github/instructions/view-layer.md Target: Enforces that .tsx files are purely visual.

---
applyTo: "src/**/*.tsx"
---
## UI View Rules
You are working in a **View File** (`index.tsx`).

## Strict Constraints
1. **NO LOGIC:** Do not write complex state logic or data fetching here.
2. **NO EXTERNAL IMPORTS:** You are **forbidden** from importing directly from `src/services` or `src/apis`.
3. **CONTROLLER BINDING:** You must import your logic from the sibling `./controller.ts` file.

## Expected Pattern
```javascript
import { use{{Feature}}Controller } from './index';

export const {{Feature}}View = () => {
  const { data, handleSave } = use{{Feature}}Controller();
  return <div onClick={handleSave}>{data}</div>;
};
```