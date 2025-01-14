# Smart Charts with AI-Powered Analysis

Smart Charts are revolutionizing data visualization by integrating AI-powered analysis. Beyond just plotting points, AI models can examine charts and their source data, identifying patterns, correlations, and potential issues you might miss. This deeper understanding unlocks a new level of insight and allows for more impactful data storytelling.

## Enhancing Data Visualization with AI

Smart Charts go beyond static displays by incorporating AI-driven analysis. By providing the underlying data along with the chart specifications, the LLM can:

- Identify Patterns and Trends: Uncover hidden patterns, correlations, and trends within the data that might be missed with traditional visual inspection.
- Generate Narrative Descriptions: Provide descriptive summaries and explanations of the observed patterns, making the insights easily accessible and understandable.
- Offer Predictive Analysis: Extrapolate from existing data to provide potential future outcomes, assisting in forecasting and planning.
- Answer Data-Driven Questions: Interact with the chart by asking natural language questions about the data. The AI can analyze the chart information and provide insightful answers.
- Suggest Chart Improvements: Receive recommendations for enhancing chart design and presentation for clearer communication and greater impact.
- Handle Complex Data: Effectively analyze and visualize complex, multi-dimensional data sets, revealing relationships and simplifying data interpretation.

## How it Works

- Smart Charts empower you to analyze data directly through natural language. By providing chart data and using natural language prompts, you can leverage the power of AI to gain valuable insights. The process generally follows these steps:
- Data Input: Provide the chart data to the system. This could include the underlying dataset used to create the chart, or the chart data itself. Various formats may be supported.
- Natural Language Prompt: Use natural language to ask questions about the chart data or request specific analyses. For example, you might ask "What are the key trends shown in this chart?" or "Is there a correlation between X and Y?".
- AI Analysis: The Smart Chart system passes both the chart data and the natural language prompt to a powerful LLM.
- Insight Generation: The LLM analyzes the chart data based on the provided prompt and generates relevant insights, explanations, and answers.
- Output and Interaction: The system presents the AI-generated insights in a user-friendly format. You can then interact further, refining your questions, requesting additional analyses, or exploring different perspectives on the data.

### Natutal Language Prompt

```bash

We are looking at a control chart measuring Curvature with this manufacturing data:
- Chart type: control chart
- Title: Control Chart Curvature
- Data: 2.46500, 2.48264, 2.33946, 2.49329, 2.47381, 2.51052, 2.55349, 2.57180, 2.50244, 2.54224, 2.42397, 2.51731, 2.48566, 2.46540, 2.41195, 2.50511, 2.50874, 2.50971, 2.51141, 2.51870, 2.52401, 2.57402, 2.50954, 2.51335, 2.50230, 2.50134, 2.50521, 2.56598, 2.46970, 2.49726, 2.51617, 2.54323, 2.51564, 2.43012, 2.48256, 2.52122, 2.49765, 2.49505, 2.55414, 2.57439, 2.55458, 2.51878, 2.44513, 2.59572, 2.57067, 2.44636, 2.50303, 2.61462, 2.42037, 2.52236
- Upper limit: 2.65635
- Lower limit: 2.35473

We are plotting a numeric series with value and control limits. Analyze the provided chart data to answer the question.

Can you tell us the purpose of this chart, and if our data results, specifically considering the provided data points and limits, show that there is an action item for us?
```

## Getting Started

This section will be filled with instructions on how to use smart charts, along with examples and code snippets.

### Code Samples

- [Python](../../python/smart_charts/):