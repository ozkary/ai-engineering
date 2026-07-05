# Specification: UI Timeline Progress & Correction Rail
## Project: Agent for Good - Heart Disease Risk Assessment

### 1. Objective
To define the layout and behavioral specifications for the Timeline Progress Rail. This docked panel provides structural grouping, real-time response feedback, and direct jump-correction capabilities.

---

### 2. Grouping & Classification Tiers

The 16 features required by the risk model are categorized into three structured blocks:

1. **Demographics:**
   * Biological sex (`sex`)
   * Age Category (`age_category`)
   * Body Mass Index (`bmi`)
2. **Lifestyle Factors:**
   * Smoking status (`smoking`)
   * Alcohol drinking (`alcohol_drinking`)
   * Physical activity (`physical_activity`)
   * General health (`gen_health`)
   * Physical health days (`physical_health`)
   * Mental health days (`mental_health`)
   * Average sleep hours (`sleep_time`)
3. **Medical History:**
   * Stroke history (`stroke`)
   * Diabetes history (`diabetic`)
   * Serious difficulty walking (`diff_walking`)
   * Asthma history (`asthma`)
   * Kidney disease history (`kidney_disease`)
   * Skin cancer history (`skin_cancer`)

---

### 3. Visual State Representation

For each of the 16 features, the timeline rail displays:
* **Active State:** The item is currently selected. Renders with an active color token (`indigo-600` badge and text) and displays an "Active" badge.
* **Answered State:** The item contains a valid response. Renders with a checked circle (`emerald-500` node indicator), displays a "Done" check badge, and displays the user's selected/calculated value.
* **Pending State:** The item has not been answered. Displays with grey styling (`text-slate-400`, `border-slate-300` node indicator) and is disabled for direct navigation click interaction.

---

### 4. Direct Navigation Jump (Correction Event)

* **Interactive Elements:** Already-answered items and the active question are fully interactive buttons.
* **Correction Handoff:** Clicking an answered item fires the direct navigation jump `jumpToQuestion(key)` event on the agent loop, transitioning the center panel questionnaire directly to that question.
* **State Updates:** Upon jumping, the center panel form field pre-populates with the previously entered response, allowing the user to inspect or modify their data immediately.
