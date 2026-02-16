
export interface GovernanceFilesData {
  global: string,
  scaffold: string,
  viewLayer: string,
  controllerLayer: string,
}

export const GOVERNANCE_FILES: GovernanceFilesData = {
    global: `# Repository Architecture Standards
  - **Naming:** UI Folders = PascalCase; Logic Files = camelCase.
  - **Pattern:** Controller (controller.ts) + View (index.tsx) separation.
  - **Stack:** TypeScript, Tailwind, Hooks only.`,

    viewLayer: `  ---
  applyTo: "src/**/*.tsx"
  ---
  # UI View Rules
  1. **NO LOGIC:** Do not use useEffect or complex state here.
  2. **NO SERVICES:** Import only from ./index (The Controller).
  3. **ONLY RENDER:** Receive props/data from Controller.`,

    controllerLayer: `  ---
  applyTo: ["src/**/controller.ts"]
  ---
  # Controller Logic Rules
  1. **Responsibility:** Bridge UI and Services.
  2. **NO FETCH:** Use src/services/ for data.
  3. **EXPORTS:** Export hooks and handlers for the View.`,

    scaffold: `# Scaffold Vertical Slice
  I need to generate a complete vertical slice.
  **Feature Name:** {{featureName}} (PascalCase)

  Generate 4 layers using Folder-as-Namespace:
  1. API: src/apis/{{camelCase}}/index.ts
  2. Service: src/services/{{camelCase}}/index.ts
  3. Component: src/components/{{PascalCase}}/index.tsx
  4. Container: src/containers/{{PascalCase}}/index.tsx`
  };

  