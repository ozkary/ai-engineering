# Prompt Library (The Scaffolder)
File: `.github/prompts/new-service.md`
Goal: Automate the creation of a logic-heavy Service layer with an optional API layer.

# Create New Service
I need to generate a business logic layer and data transformation service.
**Command:** `/new-service:{{serviceName}} {{args}}`

Please generate the code blocks for the requested layers using our **Folder-as-Namespace** pattern. 
*Note: All folders and files in this layer must be camelCase.*

---

### Service Layer (Required)
**Folder:** `src/services/{{serviceName (camelCase)}}/`

**File:** `index.ts`
- **Role:** Business logic, data transformation, and state orchestration.
- **Dependencies:** If 'api' is present in {{args}}, import the corresponding API from `src/apis/{{serviceName (camelCase)}}/index.ts`.
- **Code:** Export a `{{serviceName}}Service` object or a set of named async functions. 

---

### API Layer (Optional)
*Condition: Generate only if 'api' is present in {{args}}.*

**Folder:** `src/apis/{{serviceName (camelCase)}}/index.ts`
- **Role:** Axios/Fetch endpoint definitions.
- **Code:** - Import `coreClient` from `src/apis/index.ts`.
  - Export async functions (e.g., `get{{serviceName (PascalCase)}}`, `update{{serviceName (PascalCase)}}`).
  - Define and export TypeScript interfaces for the Request and Response payloads.

---

### Style Guidelines
- **Naming:** Use **camelCase** for the folder name and the service object.
- **Typing:** Every service function must have explicitly defined return types (Promises).
- **Error Handling:** Include basic try/catch blocks within the service layer if data transformation is complex.
- **Clean Code:** Keep the API layer thin (only network concerns) and the Service layer focused on "how" the data is used.