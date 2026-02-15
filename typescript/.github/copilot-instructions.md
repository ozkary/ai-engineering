# Global Guardrails
File: .github/copilot-instructions.md Goal: Define the "Areas" and the "Controller Pattern" globally

## Repository Architecture & Standards

### Directory Structure
This project is strictly divided into four **Areas**:
- `src/apis`: Core network configuration and base clients.
- `src/services`: Business logic and cross-cutting concerns (Caching, Transformers).
- `src/containers`: Page-level orchestration.
- `src/components`: Reusable UI elements.

### Technology Stack
- **Language:** TypeScript (`.ts`, `.tsx`) exclusively.
- **Styling:** Tailwind CSS exclusively.
- **Components:** Functional Components with Arrow Functions.
- **State:** Use Hooks (`useState`, `useEffect`) only. Class components are forbidden.

### Naming Conventions
- **UI Feature Folders:** MUST be **PascalCase** (e.g., `src/containers/SalesDashboard/`).
- **Files:** MUST be **camelCase** (e.g., `cache.ts`, `userAuth.ts`, `apiClient.ts`).
- **Exceptions:**
  - Feature entry points must use `index.ts` (Controller) and `index.tsx` (View).
  - Classes and Interfaces must be **PascalCase**. 

### The View-Controller Pattern
Every feature in **containers** and **components** must use the **Folder-as-Namespace** pattern:
- **The View:** `src/{{area}}/{{featureName}}/index.tsx`
  - *Role:* Pure UI rendering.
  - *Rule:* Must act as a "Dumb Component."
- **The Controller:** `src/{{area}}/{{featureName}}/index.ts`
  - *Role:* Logic, State Management, and Service orchestration.
  - *Rule:* Acts as the "Brain" for the View. 

### Data Flow Hierarchy
- **Data Flow:**
  - **View** (`.tsx`) calls **Controller** (`.ts`).
  - **Controller** (`.ts`) calls **Services** (`src/services`).
  - **Services** (`src/services`) call **Core API** (`src/apis/index.ts`).
