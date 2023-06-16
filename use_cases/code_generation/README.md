# Introduction

Large Language Model (LLM) refers to a class of AI models that are designed to understand and generate human-like text based on large amounts of training data. LLM can play a significant role when it comes to generating code by leveraging the language understanding and generative capabilities. Users can simply create text prompts with a user story format and provide enough context like technologies, requirements, and technical specifications, and the LLM model can generate code snippets to match what is requested by the prompt. 

> Note that LLM-generated code may not always be perfect, and developers should manually review and validate the generated code to ensure its correctness, efficiency, and adherence to coding standards.

## Benefits of LLM for code generation

When it comes to generating code, LLMs can be used in various ways:

- Code completion: LLMs can assist developers by suggesting code completions as they write code. By providing a partial code snippet or a description of the desired functionality, developers can prompt the LLM to generate the remaining code, saving time and reducing manual effort.

- Code synthesis: LLMs can synthesize code based on high-level descriptions or requirements. Developers can provide natural language specifications or user stories, and the LLM can generate code that implements the desired functionality. This can be particularly useful in the early stages of development or when exploring different approaches to solve a problem.

- Code refactoring: LLMs can help with code refactoring by suggesting improvements or alternative implementations. By analyzing existing code snippets or code bases, LLMs can generate refactored versions that follow best practices, optimize performance, or enhance readability.

- Documentation generation: LLMs can assist in generating code documentation or comments. Developers can provide descriptions of functions, classes, or code blocks, and the LLM can generate the corresponding documentation or comments that describe the code's purpose and usage.

- Code translation: LLMs can be utilized for translating code snippets between different programming languages. By providing a code snippet in one programming language, developers can prompt the LLM to generate the equivalent code in another programming language.

## Prompt Engineering

Prompt engineering is the process of designing and optimizing prompts to better utilize LLMs. Well described prompts can help the AI models better understand the context and generate more accurate responses. It is also helpful to provide some labels or expected results as examples, as this help the AI models evaluate its responses and provide more accurate results.

### Improve Code Completeness

Due to some of the API configuration, the generated code may be incomplete. To improve the completeness of the generated code when using the API, you can experiment with the following:

- Simplify or shorten your prompt to ensure it fits within the token limit
- Split your prompt into multiple API calls if it exceeds the response length limit
- Try refining and iterating on your prompt to provide clearer instructions to the model
- Experiment with different temperature and max tokens settings to influence the output

