# Specification: UI & Conversational Process Flow
## Project: Agent for Good - Data Collection Agent

### Objective
To define the step-by-step user journey, layout requirements, and state-transitions for the Data Collection Agent interface. The user must experience a highly focused, one-question-at-a-time flow that ensures zero Friction and clean data capture.

### Agent-Driven UI Governance (System Override)
This UI process is entirely governed by an external Google ADK Data Agent. Instead of managing hardcoded question indices or step counters in React, the frontend operates as a reactive event listener and state-renderer:

* **Agent Output (State Blueprint):** The agent determines the conversational pacing, dictates the active question text, defines the required input type (text, number, select options), and provides the current validation rules.
* **UI Navigation Events:** Clicking **[ Continue ]** or **[ Back ]** does not increment a local loop. Instead, these actions fire state events back to the Data Agent. The agent processes the input, validates it, updates its internal context, and pushes the next question state payload down to the UI.
---

### User Journey & UI States

The application moves through four distinct operational states:

#### State 1: Welcome & Security Assurance (Intro)
* **Agent Behavior:** The agent welcomes the user and clearly explains the purpose of the app (Heart Disease Risk Assessment).
* **Security Disclaimer:** The agent explicitly states: *"For your privacy and security, no Personally Identifiable Information (PII) is collected or stored."*
* **UI Action:** A prominent **"Start Assessment"** button is displayed.

#### State 2: Conversational Data Gathering (Question Loop)
Once started, the application loops through the 16 required features one by one.
* **Layout Requirements:**
  * **Header:** Displays the application title and a subtle progress indicator (e.g., "Question 4 of 16" or a progress bar).
  * **Main Panel:** Displays the specific question generated or mapped by the Data Collection Agent.
  * **Input Zone (Center):** A clean text input field or dynamic selector tailored to the question (e.g., dropdown brackets for age).
  * **Voice Input Option:** A microphone icon button allows the user to speak their answer instead of typing.
  * **Navigation Controls:** Standard **[ Back ]** and **[ Continue ]** buttons placed predictably at the bottom to control pacing.

#### State 3: Collection Completion & Handoff Preparation
* **Trigger:** Reached immediately after the 16th data point is collected and validated.
* **Agent Behavior:** The UI transitions to a summary confirmation view.
* **Message:** *"We have securely compiled your profile and are ready to submit it for laboratory risk analysis."*
* **UI Action:** Display a single **"Continue to Analysis"** button.

#### State 4: Processing & Model Execution
* **Trigger:** Triggered when the user clicks "Continue to Analysis" in State 3.
* **UI Action:** The input fields vanish, and a **Processing/Loading Animation** takes over the main panel.
* **Handoff Action:** Behind the scenes, the Data Collection Agent hands the validated JSON payload off to the **Lab Execution Agent**.

For this initial UI phase, logging the finalized `HeartDiseaseFormData` JSON object to the browser console (`console.log`) is sufficient to prove successful data capture.

---

### Core Process Rules

1. **State Preservation:** If a user clicks **[ Back ]**, the previously entered value must remain populated in the input field. They should not have to re-enter or re-speak data.
2. **Dynamic Formatting:** If the agent asks for BMI and the user chooses to input Height/Weight instead, the screen should dynamically offer two sub-fields before calculating the final float value and advancing.
3. **Voice to Text:** The microphone button must trigger browser-native Web Speech API (or Firebase-compatible alternative) to transcribe speech into the central input text box.