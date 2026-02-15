# React ViCSA Boilerplate

## Introduction

This repository demonstrates a highly modular React architecture based on the **ViCSA Pattern (View, Controller, Service, API)**, defined by [Oscar Garcia (ozkary)](https://www.ozkary.com).

The primary goal of this architecture is to achieve strict **Separation of Concerns (SoC)** while enabling **Repository‑Driven AI Governance**. We aim to establish an **AI Agentic Approach**, where governance tasks—such as scaffolding, architectural enforcement, and code auditing—are delegated to specialized AI agents. By standardizing the code structure, we provide these agents with a robust and predictable environment to operate effectively.

---

## The ViCSA Pattern

The application is structured into **Vertical Slices**, where each feature is self‑contained. Within each slice, code is divided into four strict layers using a **Folder‑as‑Namespace** approach:

### **V — View (`src/components/{Feature}/index.tsx`)**
- Pure UI components  
- Contains **no logic**  
- Renders only the data provided by the Controller  

### **C — Controller (`src/components/{Feature}/controller.ts`)**
- The “Brain” of the component  
- Manages state (Hooks)  
- Handles user events  
- Orchestrates calls to the Service layer  

### **S — Service (`src/services/{feature}/index.ts`)**
- Reusable business logic and data transformation  
- Isolates the **What** (business rules) from the **How** (UI)  

### **A — API (`src/apis/{feature}/index.ts`)**
- Pure data access layer  
- Responsible solely for network communication and endpoint definitions  

---

## Architecture Tree

```
src/
├── apis/
│   └── salesDashboard/        (camelCase: Endpoints)
│       └── index.ts
├── services/
│   └── salesDashboard/        (camelCase: Business Logic)
│       └── index.ts
├── components/
│   └── SalesDashboard/        (PascalCase: UI Feature)
│       ├── controller.ts      (Controller: State & Logic)
│       └── index.tsx          (View: Pure Render)
└── containers/
    └── Main/                  (PascalCase: Page/Layout)
        ├── controller.ts      (Controller: Page Logic)
        └── index.tsx          (View: Page Assembly)
```


---

## AI Agentic Governance Framework

This architecture is designed to be **AI‑Readable**. The `.github` folder transforms the repository into an **Intelligence Engine**. Instead of a generic assistant, we define specialized agents for different governance tasks.

---

## Core GitHub Configuration Files

### **global: `copilot-instructions.md` (System Prompt)**
- Acts as the System Prompt for the entire repo  
- Enforces global rules (e.g., “Use PascalCase for UI folders, camelCase for Logic files.”)

### **context: `instructions/*.md` (The Guardrails)**

#### `view-layer.md`
- Active when editing `.tsx` files  
- Prevents logic leakage by blocking `useEffect` or API calls in the UI  

#### `controller-layer.md`
- Active when editing `controller.ts`  
- Enforces that controllers must use Services, never raw fetch calls  

### **tools: `prompts/new-module.md` (The Scaffolder Agent)**
- Implements the `/new-module` slash command  
- Generates the entire ViCSA vertical slice instantly  
- Applies correct naming conventions automatically  

### **agents: `agents/arch-auditor.md` (The Auditor Agent)**
- Reviews code before PRs  
- Ensures strict layer separation  
- Verifies Views do not import APIs directly  

---

## Getting Started

To generate a new feature using this pattern with Copilot:

1. Open Copilot Chat  
2. Type: `/new-module featureName:UserProfile`


The AI will generate the API, Service, Controller, and View files following the ViCSA standard.

---

## Community & Updates

If you find this architecture useful, please **Star** this repository to receive notifications about new features and updates to the governance patterns.


