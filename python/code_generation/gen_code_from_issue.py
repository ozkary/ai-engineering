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

# import the custom services
from services.github.github_service import GitHubService
from services.factory_service import get_provider, Provider

# GitHub API endpoint and authentication headers
github_token = os.getenv("GITHUB_TOKEN")

# Main function to process an issue and generate code
def process_issue_by_label(repo: str, label: str, provider: Provider) -> None:
    
    try:            
        # get the issues from the repo
        issues = GitHubService.get_issues(repo=repo, label=label, access_token=github_token)
        if issues is not None:
            
            for issue in issues:                                
                # Generate code using OpenAI            
                print(f'Generating code from GitHub issue: {issue.title}')

                service = get_provider(provider)       

                if service is None:
                    print('The service was not created')
                    return

                generated_code = service.create(issue.body)
                
                if generated_code is not None:            
                    # Post a comment with the generated code to the GitHub issue
                    comment = f'${provider} Generated code:\n\n```{generated_code}\n```'                    
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
    parser.add_argument('--provider', required=True, help='AI Provider Name')            

    args = parser.parse_args()
    repo = str(args.repo)
    label = str(args.label)

    # map the provider string to the enum type, raise error if incorrect        
    provider = Provider.from_string(args.provider)
    process_issue_by_label(repo, label, provider)
    
# Example usage: process a specific issue
# repo = 'ozkary/ai-engineering'
# tag = 'user-story'
# process_issue_by_tag(repo, tag, provider)
# python3 gen_code_from_issue.py --repo ozkary/ai-engineering --label user-story --provider gemini

