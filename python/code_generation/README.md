
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



depTextDavinci003

https://ozkary-openai-dev.openai.azure.com/

f9f84189e47840efa5f2fa0cdaffcc15


echo export AZURE_OPENAI_KEY="f9f84189e47840efa5f2fa0cdaffcc15" >> ~/.bashrc && source ~/.bashrc

echo export AZURE_OPENAI_DEPLOYMENT="depTextDavinci003" >> ~/.bashrc && source ~/.bashrc

echo export AZURE_OPENAI_ENDPOINT="https://ozkary-openai-dev.openai.azure.com/" >> ~/.bashrc && source ~/.bashrc


echo export GITHUB_TOKEN="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" >> ~/.bashrc && source ~/.bashrc

