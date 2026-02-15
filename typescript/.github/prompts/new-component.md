# Prompt Library (The Scaffolder)
File: `.github/prompts/new-component.md`
Goal: Automate the creation of a standalone UI Component with optional Service/API layers.

# Create New Component
I need to generate a new component following our **Folder-as-Namespace** pattern.
**Command:** `/new-component:{{componentName}} {{args}}`

Please generate the code blocks for the layers requested in the arguments (service, api). 
*Note: Logic folders must be camelCase. UI folders must be PascalCase.*

---

### Component Layer (Required)
**Folder:** `src/components/{{componentName (PascalCase)}}/`
- **File:** `controller.ts` (Controller): Logic and State only.
- **File:** `index.tsx` (View): Pure UI. Imports Controller.
---

### Service Layer (Optional)
*Condition: Generate only if 'service' is present in {{args}}.*

**File:** `src/services/{{componentName (camelCase)}}/index.ts`
- **Role:** Business logic and data transformation.
- **Code:** Import the API (if requested). Export a service object or functional exports.

---

### API Layer (Optional)
*Condition: Generate only if 'api' is present in {{args}}.*

**File:** `src/apis/{{componentName (camelCase)}}/index.ts`
- **Role:** Define specific endpoints.
- **Code:** Import `coreClient` from `src/apis/index.ts`. Export async functions with typed responses.

---

### Style Guidelines
- **Typing:** Use TypeScript interfaces for all Props and Data models.
- **Separation:** Logic stays in `controller.ts`, JSX stays in `index.tsx`.
- **Naming:** Components use PascalCase; Services/APIs use camelCase.