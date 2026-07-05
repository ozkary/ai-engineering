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
namespace CodeGeneration.Services.GitHub;

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text.Json;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Text;

/// <summary>
/// GitHub API service
/// </summary>
internal class GitHubService
{
    private const string RepoUrl = "https://api.github.com/repos/";
    private const string IssuesRoute = "issues";
    private const string CommentsRoute = "comments";

    const string UserAgent = "Ozkary OpenAI V1.0.0";

    private static string BuildQueryString(Dictionary<string, string> parameters)
    {
        var queryString = new List<string>();
        foreach (var parameter in parameters)
        {
            queryString.Add($"{Uri.EscapeDataString(parameter.Key)}={Uri.EscapeDataString(parameter.Value)}");
        }
        return string.Join("&", queryString);
    }

    /// <summary>
    /// Get issues from a GitHub repository
    /// </summary>
    /// <param name="route">The GitHub repository route</param>
    /// <param name="params">The GitHub API parameters</param>
    /// <param name="accessToken">The GitHub access token</param>
    /// <returns>A list of issues</returns>
    /// <exception cref="ArgumentNullException">Thrown when the access token is null or empty</exception>
    /// <exception cref="HttpRequestException">Thrown when the request fails</exception>
    /// <exception cref="JsonException">Thrown when the response body can't be parsed</exception>
    /// <exception cref="InvalidOperationException">Thrown when the response is not successful</exception>
    /// <exception cref="Exception">Thrown when an unknown error occurs</exception>
    /// <remarks>
    /// See the GitHub API documentation for more information:
    /// https://docs.github.com/en/rest/reference/issues#list-repository-issues
    /// </remarks>
   public static async Task<List<Issue>> GetIssues(string route, Parameter @params, string? accessToken)
    {
        if (String.IsNullOrEmpty(accessToken)){
            throw new ArgumentNullException(nameof(accessToken));
        }

        // Set up HttpClient and authentication if needed
        using (HttpClient httpClient = new HttpClient())
        {
            if (!string.IsNullOrEmpty(accessToken))
            {
                Console.WriteLine("Setting up authentication for GitHub API request");
                // httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);
                httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}");
                httpClient.DefaultRequestHeaders.Add("User-Agent",UserAgent);

            }

            // Send the API request
            string apiUrl = $"{RepoUrl}{route}/{IssuesRoute}";

            Console.WriteLine($"Sending request to {apiUrl}");

            var apiParams = new Dictionary<string, string>
            {
                { "labels", @params.Label },
                { "state", @params.State }
            };

            var queryString = BuildQueryString(apiParams);
            HttpResponseMessage response = await httpClient.GetAsync(apiUrl + "?" + queryString);

            List<Issue> issuesList = new List<Issue>();             

            if (response.IsSuccessStatusCode)
            {
                // Parse the response body                                  
                string responseBody = await response.Content.ReadAsStringAsync();
                if (!String.IsNullOrEmpty(responseBody)){
                    List<Issue>? issues = JsonSerializer.Deserialize<List<Issue>>(responseBody);
                    if (issues != null){
                        issuesList.AddRange(issues);
                    }         
                    Console.WriteLine($"Issues found: {issuesList.Count}");
                }                                              
            }
            else
            {
                Console.WriteLine($"Error getting the issues: {response.StatusCode} - {response.ReasonPhrase}");
            }

            return issuesList;
        }
    }        

    public static async Task<bool> PostIssueComment(string repo, int issueId, string comment, string accessToken) {
        // Set up HttpClient and authentication if needed
        using (HttpClient httpClient = new HttpClient())
        {
            if (!string.IsNullOrEmpty(accessToken))
            {
                httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}");
                httpClient.DefaultRequestHeaders.Add("User-Agent",UserAgent);
            }

            // Send the API request
            string apiUrl = $"{RepoUrl}{repo}/{IssuesRoute}/{issueId}/{CommentsRoute}";

            Console.WriteLine($"Sending request to {apiUrl}");

            // var body = new Dictionary<string, string>
            // {
            //     { "body", comment }
            // };

            // Create the json comment payload
            var payload = new
            {
                body = comment
            };

            string jsonPayload = JsonSerializer.Serialize(payload);

            // Set the Content-Type header and create the StringContent object
            StringContent stringContent = new StringContent(jsonPayload, Encoding.UTF8, "application/json");                        
            HttpResponseMessage response = await httpClient.PostAsync(apiUrl, stringContent);

            if (response.IsSuccessStatusCode)
            {
                return true;
            }
            else
            {
                Console.WriteLine($"Error: {response.StatusCode} - {response.ReasonPhrase}");
                return false;
            }
        }

    }
}
