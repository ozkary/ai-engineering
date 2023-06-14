#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  Generate code from a GitHub issue example
#


import argparse
import os
import sys

# Add the project's root directory to the Python path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

from services.github.github_service import GitHubService
from services.openai.openai_service import OpenAIService

# Set up OpenAI API credentials
openai_api_key = os.getenv("AZURE_OPENAI_KEY")
openai_api_base = os.getenv("AZURE_OPENAI_ENDPOINT")    # custom endpoint
openai_api_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")            # this will change based on your deployment

# GitHub API endpoint and authentication headers
github_username = os.getenv("GITHUB_USERNAME")
github_token = os.getenv("GITHUB_TOKEN")

# Main function to process an issue and generate code
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

if __name__ == '__main__':
    """main entry point with argument parser"""
    os.system('clear')
    print('Processing code generation from GitHub issues...')
    parser = argparse.ArgumentParser(description='Process GitHub issues.')
    
    parser.add_argument('--repo', required=True, help='Repository path ozkary/ai-engineering')
    parser.add_argument('--label', required=True, help='Issue label')            
    args = parser.parse_args()
    repo = str(args.repo)
    label = str(args.label)
    process_issue_by_label(repo, label)
    
# Example usage: process a specific issue
# repo = 'ozkary/ai-engineering'
# tag = 'user-story'
# process_issue_by_tag(repo, tag)
# python3 gen_code_from_issue.py --repo ozkary/ai-engineering --label user-story
