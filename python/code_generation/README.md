
# LLM Models and code generation

Large Language Model (LLM) refers to a class of AI models that are designed to understand and generate human-like text based on large amounts of training data. LLM can play a significant role when it comes to generating code by leveraging the language understanding and generative capabilities. Users can simply create text propmts with a user story format and provide enough context like technologies, requirements, and technial specifications, and the LLM model can generate code snippets to match what is requested by the prompt. 

 ![ozkary generate code from github user story](./images/../../../images/ozkary-openai-user-story-flow.png)

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

### Install the OpenAI dependencies

```
$ pip install OpenAI
```

### Add the OpenAI environment configurations

Get the following configuration information:

> This example can run directly on the OpenAI APIs or it can use a custom Azure OpenAI resource.

- GitHub Repo API Token with write permissions to push comments to an issue
- Get an OpenAI API key
- If you are using an Azure OpenAI resource, get your custom end-point and deployment
  - The deployment should have the code-davinci-002 model

Set the linux environment variables with these commands:

```
$ echo export AZURE_OpenAI_KEY="OpenAI-key-here" >> ~/.bashrc && source ~/.bashrc
$ echo export GITHUB_TOKEN="github-key-here" >> ~/.bashrc && source ~/.bashrc

# only set these variables when using your Azure OpenAI resource

$ echo export AZURE_OpenAI_DEPLOYMENT="deployment-name" >> ~/.bashrc && source ~/.bashrc
$ echo export AZURE_OpenAI_ENDPOINT="https://YOUR-END-POINT.OpenAI.azure.com/" >> ~/.bashrc && source ~/.bashrc

```
### Describe the code

The code should run this workflow:

- Get a list of open GitHub issues with the label user-story
- Each issue content is sent to the OpenAI API to generate the code
- The generated code is posted as a comment on the user-story for the developers to review
  
> The following code uses a simple API call implementation for the GitHub and OpenAI APIs. Use the code from this repo: - [LLM Code Generation](https://github.com/ozkary/ai-engineering/tree/main/python/code_generation)

```

def process_issue_by_label(repo: str, label: str):
    
    try:    
        # get the issues from the repo
        issues = GitHubService.get_issues(repo=repo, label=label, access_token=github_token)
        if issues is not None:
            
            for issue in issues:                                
                # Generate code using OpenAI            
                print(f'Generating code from GitHub issue: {issue.title}')
                openai_service = OpenAIService(api_key=openai_api_key, engine=openai_api_deployment, end_point=openai_api_base)
                generated_code = openai_service.create(issue.body)
                
                if generated_code is not None:            
                    # Post a comment with the generated code to the GitHub issue
                    comment = f'Generated code:\n\n```{generated_code}\n```'                    
                    comment_posted = GitHubService.post_issue_comment(repo,  issue.id, comment, access_token=github_token)
                    
                    if comment_posted:
                        print('Code generated and posted as a comment on the GitHub issue.')
                    else:
                        print('Failed to post the comment on the GitHub issue.')
                else:
                    print('Failed to generate code from the GitHub issue.')
        else:
            print('Failed to retrieve the GitHub issue.')
    except Exception as ex:
        print(f"Error:  {ex}")

```
### Run the code

After configuring your environment, we can run the code from a terminal by typing the following command:

> Make sure to enter your repo name and label your issues with either user-story or any other label you would rather use.
>
```
# python3 gen_code_from_issue.py --repo ozkary/ai-engineering --label user-story
```

After running the code successfully, we should be able to see the generated code as a comment on the GitHub issue.
