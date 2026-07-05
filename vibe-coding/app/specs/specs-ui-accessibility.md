# Specification: UI Accessibility (TypeScript & React)
## Project: Agent for Good - Heart Disease Risk Assessment

### 1. Objective
To define the accessibility and multi-modal navigation specification for the Heart Disease Risk Assessment Portal, ensuring compliance with rapid keyboard navigation, hands-free voice control capability, and standard mouse click interactions.

---

### 2. Keyboard Navigation & Hotkeys

To facilitate swift and accessible data collection, global keyboard event listeners are active during the questioning step:

* **[Space] (Spacebar):** Triggers the navigation "Continue" to advance to the next question.
  * *Condition:* Only triggered if a valid option is selected or entered (`canContinue` is true).
  * *Default Prevention:* Prevents default browser page scrolling.
* **[Y] / [y]:** Selects the "Yes" option for binary select-type questions.
* **[N] / [n]:** Selects the "No" option for binary select-type questions.
* **[M] / [m]:** Selects the "Male" option on the biological sex question.
* **[F] / [f]:** Selects the "Female" option on the biological sex question.
* **[Backspace] / [Left Arrow]:** Navigates backward to the previous question (equivalent to clicking "Back").
  * *Condition:* Only active if the user is not on the first question.
  * *Default Prevention:* Bypassed when the cursor is focused inside an input field (`<input>` or `<textarea>`) to allow standard text editing and caret movement.

---

### 3. Voice Command & Input Navigation

The application integrates Speech-to-Text (via standard Web Speech API) to offer persistent, hands-free navigation and intake:

* **Persistent Listening State:**
  * Enabled by clicking the microphone button next to the active question.
  * Once turned on, the listener remains active (`voiceEnabled` preference is true) across all screen transitions.
  * It automatically restarts a new browser `SpeechRecognition` session after an answer is parsed or when a navigation transition is completed.
* **Voice Action Commands:**
  * **"Next" / "Continue" / "Go Next":** Automates navigation to the next question.
  * **"Back" / "Go Back":** Automates navigation to the previous question.
  * **"Restart" / "Start Again" / "Reset":** Instantly resets the questionnaire, starting the user back at Question 1.
* **Direct Input Translation:**
  * If the microphone is active and the spoken text is not one of the navigation commands above, it parses the string for answers:
    * *Numeric / BMI Inputs:* Extracts the first numeric float/integer from the transcription.
    * *Select Options:* Computes fuzzy matches against available question options (e.g. speaking "Borderline" matches "No, borderline diabetes").

---

### 4. Accessibility Options Reference Panel

An "Accessibility Options" help guide is permanently docked on the right side of the screen as a presentational sidebar on desktop views (`lg:block w-80`), displaying formatting and lists for both Voice Navigation commands and Keyboard shortcuts to assist the user.
