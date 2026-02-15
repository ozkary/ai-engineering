# Prompt Library (The Scaffolder)
File: .github/prompts/new-module.md 
Goal: Automate the creation of the specific Controller/View pair.

# Create New Module
I need to generate a complete vertical slice for a new feature.
**Feature Name:** {{featureName}} (PascalCase, e.g., "Dashboard")

Please generate the code blocks for these 4 layers using our **Folder-as-Namespace** pattern. 
*Note: Logic folders must be camelCase. UI folders must be PascalCase.*

---

### API Layer
**File:** `src/apis/{{featureName (camelCase)}}/index.ts`
- **Role:** Define specific endpoints.
- **Code:** Import `coreClient` from `src/apis/index.ts`. Export async functions.

### Service Layer
**File:** `src/services/{{featureName (camelCase)}}/index.ts`
- **Role:** Business logic and data transformation.
- **Code:** Import the API from step 1. Export the service object/functions.

### Component Layer
**Folder:** `src/components/{{featureName}}/`
- **File:** `controller.ts` (Controller): Logic and State only.
- **File:** `index.tsx` (View): Pure UI. Imports Controller.

### Container Layer
**Folder:** `src/containers/{{featureName}}/`
- **File:** `controller.ts` (Controller): Imports `{{featureName}}` Service (from step 2) and Component (from step 3).
- **File:** `index.tsx` (View): The main Page assembly.

### **Style:** Use TypeScript interfaces for all Props.