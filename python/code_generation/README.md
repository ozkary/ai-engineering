
# LLM Models and code generation

Large Language Model (LLM) refers to a class of AI models that are designed to understand and generate human-like text based on large amounts of training data. LLM can play a significant role when it comes to generating code by leveraging the language understanding and generative capabilities. Users can simply create text propmts with a user story format and provide enough context like technologies, requirements, and technial specifications, and the LLM model can generate code snippets to match what is requested by the prompt. 

## Generate code from user stories

In the Agile development methodology, user stories are used to capture requirements or a feature from the perspective of end user or customer. For code generation, developers can write user stories to capture the context, requirements and technical specification necessary to generate code. This user story can then be processed by the LLM models to generate the code. As an example, a user store could be written in this way:

```

As a data scientist, I want to generate code using the following technologies, requirements, and specifications:

Technologies: 
- Python

Requirements:
- Transform a data frame by consolidating the 'date' and 'time' columns into a date time field column named 'created'.

Specifications:
- Create a function with the name 'transform_data'
- Use pandas to perform the data transformation
- Load the data from a parameter with the CSV file path
- Save the resulting data frame to disk in Parquet format
- Return true if successful or false if is not
- For coding standards, use the guidelines outlined in the [PEP 8 style guide for Python](https://www.python.org/dev/peps/pep-0008/).
- Create a unit test for the `transform_data` function to verify its correctness. The unit test should cover different scenarios and assert the expected behavior of the function.

```

From this user story, we can see that the end user of the story is a data scientist who would like to generate Python code. The requirement is basically to transform two columns from a data frame into a date-time column. There is also additional technical specification written that provides more context to the AI model, so it is able to generate the code with the specifics including what coding standards to use. 

Let's take a look a python example to see how we can generate code from a user story:


## Configure app to access Azure OpenAI resource

Configuration for each language varies slightly, but both require the same parameters to be set. The necessary parameters are endpoint, key, and the name of your deployment, which is called the engine when sending your prompt to the model.

Add the library to your app, and set the required parameters for your client.

### Install the openai dependencies

```
$ pip install openai
```

### Add the openai environment configurations

Get the following configuration information:

> This example can run directly on the openai APIs or it can use a custom Azure openai resource.

- GitHub Repo API Token with write permissions to push comments to an issue
- Get an openai API key
- If you are using an Azure openai resource, get your custom end-point and deployment
  - The deployment should have the code-davinci-002 model

Set the linux environment variables with these commands:

```
$ echo export AZURE_OPENAI_KEY="openai-key-here" >> ~/.bashrc && source ~/.bashrc
$ echo export GITHUB_TOKEN="github-key-here" >> ~/.bashrc && source ~/.bashrc

# only set these variables when using your Azure openai resource

$ echo export AZURE_OPENAI_DEPLOYMENT="deployment-name" >> ~/.bashrc && source ~/.bashrc
$ echo export AZURE_OPENAI_ENDPOINT="https://YOUR-END-POINT.openai.azure.com/" >> ~/.bashrc && source ~/.bashrc

```

