# Specification: UI Technical & Component Architecture (TypeScript)
## Project: Agent for Good - Frontend UI (React, TypeScript & Firebase)

### Objective
To outline the technical constraints, type definitions, state management, and component boundaries for the React + TypeScript application. This guarantees a type-safe, modular layout built for rapid deployment on Firebase Hosting.

#### Agent Synchronization Loop & State Mapping
To support the agent-driven architecture, the React frontend must mirror the state pushed by the Google ADK Data Agent. The event interface relies on this basic reactive state contract:

```typescript
export interface AgentUIState {
  currentQuestionText: string;      // Sent by agent (Renders in main panel)
  targetFeatureKey: string;          // Sent by agent (e.g., 'bmi', 'smoking')
  expectedInputType: 'text' | 'number' | 'select'; 
  selectOptions?: string[];          // Sent by agent if type is 'select'
  isFirstQuestion: boolean;          // Controls [ Back ] disabled state
  isLastQuestion: boolean;           // Switches [ Continue ] to [ Continue to Analysis ]
}

// User Action Events sent back to the Agent
const handleNavigationEvent = (direction: 'next' | 'back', currentInputValue: any) => {
  // Fire event to Google ADK Data Agent to compute the next state block
};
```

Create a core class to for the Agent instance of the SDK. The base class will be used by all the agents in this solution. This can enable us to implement cross cutting concerns on the core classes thus creating a clear separation of concern and abstraction layer.

---

### Technology Stack & Packages
* **Framework:** React 18+ with Vite (TypeScript Template)
* **Styling Framework:** Tailwind CSS
* **Icons:** Lucide React
* **Deployment:** Firebase Hosting

### Design System & Theme Layout (Tailwind CSS)

To ensure an accessible, professional healthcare interface, the UI must strictly utilize the following functional color tokens:

#### A. Core Palette
* **Primary / Trust Color:** `Slate Blue` (`bg-slate-900`, `text-slate-900`, `indigo-600` for primary interactive elements). Represents stability, medical professionalism, and clarity.
* **Background Canvas:** `Off-White / Light Gray` (`bg-slate-50`). Keeps the focus entirely on the single question panel without eye strain.
* **Card Surface:** `Pure White` (`bg-white`) with a soft, modern drop shadow (`shadow-sm`) to elevate the question interface.

#### B. Semantic & Validation Colors
* **Success / Complete:** `Emerald Green` (`text-emerald-600`, `bg-emerald-50`). Used for completed checkboxes, the progress bar fill, and the data validation success message.
* **Warning / Attention:** `Amber Yellow` (`text-amber-600`, `bg-amber-50`). Used for optional clarifications or borderline data entries (e.g., borderline diabetes selections).
* **Alert / Error:** `Rose Red` (`text-rose-600`, `bg-rose-50`). Used for invalid inputs, numbers out of bounds (e.g., typing 45 days for a 30-day health window), or missing selections.

#### C. Active Interactive States
* **Focus State:** Interactive text fields, dropdown buttons, or microphone buttons should use an explicit `ring-2 ring-indigo-500` outline when focused or active to ensure high accessibility.

---



### Type Definitions & Schemas

To prevent runtime errors during the data handoff, strict TypeScript interfaces must govern the form data and application states.

```typescript
// Define acceptable literal types based on CDC/UCI requirements
export type SexType = 'Male' | 'Female' | '';
export type AgeCategoryType = '18-24' | '25-29' | '30-34' | '35-39' | '40-44' | '45-49' | '50-54' | '55-59' | '60-64' | '65-69' | '70-74' | '75-79' | '80 or older' | '';
export type YesNoType = 'Yes' | 'No' | '';
export type DiabeticType = 'Yes' | 'No' | 'No, borderline diabetes' | 'Yes (during pregnancy)' | '';
export type GenHealthType = 'Excellent' | 'Very good' | 'Good' | 'Fair' | 'Poor' | '';

// Core state schema for the collected patient features
export interface HeartDiseaseFormData {
  sex: SexType;
  age_category: AgeCategoryType;
  bmi: number | null;
  smoking: YesNoType;
  alcohol_drinking: YesNoType;
  stroke: YesNoType;
  diabetic: DiabeticType;
  physical_activity: YesNoType;
  gen_health: GenHealthType;
  diff_walking: YesNoType;
  asthma: YesNoType;
  kidney_disease: YesNoType;
  skin_cancer: YesNoType;
  physical_health: number | null;
  mental_health: number | null;
  sleep_time: number | null;
}

// Application State Machine Tiers
export type AppStepState = 'WELCOME' | 'QUESTIONING' | 'READY_TO_SUBMIT' | 'PROCESSING' | 'RESULTS';

// Structural Question Definition Mapping
export interface QuestionDefinition {
  key: keyof HeartDiseaseFormData;
  label: string;
  type: 'select' | 'text' | 'number' | 'bmi_calculator';
  options?: string[];
  validation: (value: any) => boolean;
}

```

### Component Structure & Type Contracts
Components must strictly type their props to maintain modular architectural boundaries:

App.tsx: Holds root reactive states:

step: AppStepState

formData: HeartDiseaseFormData

currentQuestionIndex: number

WelcomeScreen.tsx

Props: { onStart: () => void; }

QuestionCard.tsx

Props: { question: QuestionDefinition; value: any; onChange: (val: any) => void; }

Contains conditional sub-rendering for complex calculations (e.g., dynamic height/weight metric conversion fields if computing BMI).

SpeechToText.tsx

Props: { onTranscription: (text: string) => void; isListening: boolean; onToggleListen: () => void; }

Interfaces safe fallback wrappers for window.SpeechRecognition casting to support various modern browsers.

NavigationControls.tsx

Props: { onBack: () => void; onContinue: () => void; canBack: boolean; canContinue: boolean; }

LoadingSpinner.tsx: Stateless presentation loader component.

### Technical Processing & Validation Logic

#### Centralized Form Initial State

```typescript
export const initialFormData: HeartDiseaseFormData = {
  sex: '',
  age_category: '',
  bmi: null,
  smoking: '',
  alcohol_drinking: '',
  stroke: '',
  diabetic: '',
  physical_activity: '',
  gen_health: '',
  diff_walking: '',
  asthma: '',
  kidney_disease: '',
  skin_cancer: '',
  physical_health: null,
  mental_health: null,
  sleep_time: null
};
```
#### Direct In-Memory Type Guarding
The continuous execution block will reject progressing forward (canContinue = false) if type-casting fields fail validation rules (e.g., parsing strings to integers for sleep_time must result in a valid number between 1 and 24).

Upon transitioning into the READY_TO_SUBMIT phase, a type assertion check ensures that zero null or empty string values remain present inside the data payload.

### Phase 1 - Lab Agent Placeholder Implementation
* When the application transitions to `PROCESSING_PLACEHOLDER`, the UI must render a clean `<div className="border-2 border-dashed border-blue-400 bg-blue-50 p-6 rounded-lg text-center">` panel.
* Inside this panel, display a loading spinner alongside the message: 
  `"Data validation successful. Ready for Lab Agent handoff."`
* Print the formatted `HeartDiseaseFormData` JSON payload directly into a read-only `<pre>` block on the screen. This allows for immediate visual verification of data integrity during vibe coding iterations.

### Code Quality, Linting & Formatting (npm Ecosystem)
To ensure strict code quality and prevent runtime failures before the data is handed off to the backend agents, the project utilizes the npm ecosystem for automated code guardrails.

Tooling & Dependencies
Linter & Formatter: Biome (An all-in-one, blazing-fast tool for formatting and linting TypeScript and React/JSX assets).

Type Checker: Native TypeScript Compiler (tsc).

Package.json Scripts
The package.json inside heart-disease-risk-agent/ must expose the following unified scripts to interface with the local automation layer:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "biome lint ./src",
    "format": "biome format ./src --write",
    "check": "biome check --write ./src"
  }
}
```

- Create a make file that can enable our devops scripts to run the following:

```makefile
lint:
	npm run lint

format:
	npm run format

dev:
	npm run dev

build:
	npm run build
```
