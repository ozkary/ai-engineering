For both SDKs covered in this unit, you need the endpoint and a key from your Azure OpenAI resource, and the name you gave for your deployed model. In the following code snippets, the following placeholders are used:

Placeholder name	Value
YOUR_ENDPOINT_NAME	This base endpoint is found in the Keys & Endpoint section in the Azure portal. It's the base endpoint of your resource, such as https://sample.openai.azure.com/.
YOUR_API_KEY	Keys are found in the Keys & Endpoint section in the Azure portal. You can use either key for your resource.
YOUR_DEPLOYMENT_NAME	This deployment name is the name provided when you deployed your model in the Azure OpenAI Studio.
Install libraries
First, install the client library for your preferred language. The C# SDK is a .NET adaptation of the REST APIs and built specifically for Azure OpenAI, however it can be used to connect to Azure OpenAI resources or non-Azure OpenAI endpoints. The Python SDK is built and maintained by OpenAI.

Console

$ dotnet new sln -n CodeGeneration

$ dotnet new console --use-program-main

$ dotnet new classlib -n .Services -o services

$ dotnet add package Azure.AI.OpenAI --prerelease

$ dotnet add package Azure.Identity

$ dotnet sln add <path-to-project-or-folder>

$ dotnet sln add CodeGeneration.csproj

$ dotnet build

$ dotnet run

Configure app to access Azure OpenAI resource
Configuration for each language varies slightly, but both require the same parameters to be set. The necessary parameters are endpoint, key, and the name of your deployment, which is called the engine when sending your prompt to the model.

Add the library to your app, and set the required parameters for your client.

C#

Copy
// Add OpenAI library
using Azure.AI.OpenAI;

// Define parameters and initialize the client
string endpoint = "<YOUR_ENDPOINT_NAME>";
string key = "<YOUR_API_KEY>";
string deploymentName = "<YOUR_DEPLOYMENT_NAME>"; //SDK calls this "engine", but naming
                                                  // it "deploymentName" for clarity

OpenAIClient client = new OpenAIClient(new Uri(endpoint), new AzureKeyCredential(key));
Call Azure OpenAI resource
Once you've configured your connection to Azure OpenAI, send your prompt to one of the available endpoints of Completion, ChatCompletion, or Embedding.

C#

Copy
string prompt = "What is Azure OpenAI?";

Response<Completions> completionsResponse = client.GetCompletions(deploymentName, prompt);
string completion = completionsResponse.Value.Choices[0].Text;
Console.WriteLine($"Chatbot: {completion}");
If using ChatCompletion, sending the prompt is formed differently.

C#

Copy
// Build completion options object
ChatCompletionsOptions chatCompletionsOptions = new ChatCompletionsOptions()
{
    Messages = 
    {
        new ChatMessage(ChatRole.System, "You are a helpful AI bot."), 
        new ChatMessage(ChatRole.User, "What is Azure OpenAI?")
    }
};

// Send request to Azure OpenAI model
ChatCompletions chatCompletionsResponse = client.GetChatCompletions(
    deploymentName, 
    chatCompletionsOptions);

ChatMessage completion = chatCompletionsResponse.Choices[0].Message;
Console.WriteLine($"Chatbot: {completion.Content}");
The response object contains several values, such as total_tokens and finish_reason. The completion from the response object will be similar to the following completion: