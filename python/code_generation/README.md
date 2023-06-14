
Configure app to access Azure OpenAI resource
Configuration for each language varies slightly, but both require the same parameters to be set. The necessary parameters are endpoint, key, and the name of your deployment, which is called the engine when sending your prompt to the model.

Add the library to your app, and set the required parameters for your client.

Python

$ pip install python-dotenv
$ pip install openai

# Add OpenAI library
import openai

openai.api_key = '<YOUR_API_KEY>'
openai.api_base =  '<YOUR_ENDPOINT_NAME>' 
openai.api_type = 'azure' # Necessary for using the OpenAI library with Azure OpenAI
openai.api_version = '2022-12-01' # This likely will change with future releases

deployment_name = '<YOUR_DEPLOYMENT_NAME>' # SDK calls this "engine", but naming
                                           # it "deployment_name" for clarity



echo export AZURE_OPENAI_KEY="key-here" >> ~/.bashrc && source ~/.bashrc

echo export AZURE_OPENAI_DEPLOYMENT="depTextDavinci003" >> ~/.bashrc && source ~/.bashrc

echo export AZURE_OPENAI_ENDPOINT="https://ozkary.openai.azure.com/" >> ~/.bashrc && source ~/.bashrc


echo export GITHUB_TOKEN="github-key-here" >> ~/.bashrc && source ~/.bashrc

