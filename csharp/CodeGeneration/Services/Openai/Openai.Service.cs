/*
  * 
 * The MIT License (MIT)
 * 
 * Copyright (c) [2023] [oscar garcia]
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * Author: oscar garcia - ozkary
 */

namespace CodeGeneration.Services.Openai {
    using System;    
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

                // var options = new CompletionsOptions
                // {
                //     MaxTokens = this.maxTokens,
                //     Temperature = this.temperature,
                //     Prompts = new string[] { prompt }                    
                // };
                              
                Response<Completions> completionsResponse = await client.GetCompletionsAsync(engine, prompt);
                // Response<Completions> completionsResponse = await client.GetCompletionsAsync(engine, options);
                
                Console.WriteLine(completionsResponse);
                result = completionsResponse.Value.Choices[0].Text.Trim();                
                Console.WriteLine(result);
            }

            return result;            
        }
    }
}