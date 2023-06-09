﻿/*
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
using System;
using CodeGeneration.Services.GitHub;
using CodeGeneration.Services.Openai;

namespace CodeGeneration {

class Program
{
 
    // Get environment variables
    private static readonly string openaiApiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_KEY") ?? String.Empty;    
    private static readonly string openaiBase = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT") ?? String.Empty;       
    private static readonly string openaiEngine = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? String.Empty;           

    // GitHub API endpoint and authentication headers    
    private static readonly string githubToken = Environment.GetEnvironmentVariable("GITHUB_TOKEN") ?? String.Empty;

    /// <summary>
    /// Process a GitHub issue by label.
    /// </summary>
    public static async Task ProcessIssueByLabel(string repo, string label)
    {
        try
        {
            // Get the issues from the repo
            var @params = new Parameter { Label = label, State = "open" };              
            List<Issue> issues = await GitHubService.GetIssues(repo, @params, githubToken);
            if (issues != null)
            {
                foreach (var issue in issues)
                {
                    // Generate code using OpenAI
                    Console.WriteLine($"Generating code from GitHub issue: {issue.title} to {openaiBase}");
                    OpenAIService openaiService = new OpenAIService(openaiApiKey, openaiBase, openaiEngine);
                    string generatedCode = await openaiService.Create(issue.body ?? String.Empty);

                    if (!string.IsNullOrEmpty(generatedCode))
                    {
                        // Post a comment with the generated code to the GitHub issue
                        string comment = $"Generated code:\n\n```{generatedCode}\n```";
                        bool commentPosted = await GitHubService.PostIssueComment(repo, issue.number, comment, githubToken);

                        if (commentPosted)
                        {
                            Console.WriteLine("Code generated and posted as a comment on the GitHub issue.");
                        }
                        else
                        {
                            Console.WriteLine("Failed to post the comment on the GitHub issue.");
                        }
                    }
                    else
                    {
                        Console.WriteLine("Failed to generate code from the GitHub issue.");
                    }
                }
            }
            else
            {
                Console.WriteLine("Failed to retrieve the GitHub issue.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }


    /// <summary>
    /// Main method.    
    /// </summary>    
    /// <example>
    /// dotnet run --repo ozkary/ai-engineering --label user-story
    /// </example>
    /// <param name="args">The command-line arguments.</param>
    /// <returns>The task.</returns>
    /// <remarks>
    /// The command-line arguments are:
    /// --repo: The GitHub repository in the format owner/repo.
    /// --label: The GitHub issue label.
    /// </remarks>
    /// <exception cref="ArgumentException">Thrown when the arguments are invalid.</exception>    
    static void Main(string[] args)
    {
       if (args.Length < 4)
        {
            Console.WriteLine("Invalid arguments. Usage: dotnet run --repo <repository> --label <issue_label>");
            return;
        }

        string repo = String.Empty;
        string label = String.Empty;

        // read the arguments
        for (int i = 0; i < args.Length; i += 2)
        {
            string option = args[i];
            string value = args[i + 1];

            switch (option)
            {
                case "--repo":
                    repo = value;
                    break;
                case "--label":
                    label = value;
                    break;
                default:
                    Console.WriteLine($"Invalid argument: {option}");
                    return;
            }
        }

        if (String.IsNullOrEmpty(repo) || String.IsNullOrEmpty(label))
        {
            Console.WriteLine("Invalid arguments. Usage: dotnet run --repo <repository> --label <issue_label>");
            return;
        }

        Task task = ProcessIssueByLabel(repo, label);
        task.Wait();  // Block the execution until the task completes
    }
}

}