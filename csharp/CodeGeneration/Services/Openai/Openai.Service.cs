namespace CodeGeneration.Services.Openai {
    using System;
    using System.Collections.Generic;    
    using Azure.AI.OpenAI;
    using Azure;

    /// <summary>
    /// OpenAI API service
    /// </summary>
    internal class OpenAIService
    {
        private string apiKey;
        private string engine;
        private string endPoint;
        private float temperature;
        private int maxTokens;
        private int n;
        private string stop;

        /// <summary>
        /// OpenAI client
        /// </summary>
        private OpenAIClient? client;

        public OpenAIService(string apiKey, string endPoint, string engine = "text-davinci-003", float temperature = 0.5f, int maxTokens = 350, int n = 1, string stop = "")
        {
            // Configure the OpenAI client with your API key and endpoint                 
            client = new OpenAIClient(new Uri(endPoint), new AzureKeyCredential(apiKey));
            this.apiKey = apiKey;
            this.endPoint = endPoint;            
            this.engine = engine;
            this.temperature = temperature;
            this.maxTokens = maxTokens;
            this.n = n;
            this.stop = stop;                
        }

        /// <summary>
        /// Create a completion from a prompt
        /// </summary>
        public async Task<string> Create(string prompt)
        {     
            var result = String.Empty;

            if (!String.IsNullOrEmpty(prompt) && client != null)
            {
                              
                Response<Completions> completionsResponse = await client.GetCompletionsAsync(engine, prompt);
                
                Console.WriteLine(completionsResponse);
                result = completionsResponse.Value.Choices[0].Text.Trim();                
                Console.WriteLine(result);
            }

            return result;            
        }
    }
}