"""GitHub API service."""
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  Github service
#

from requests import get, post
from typing import List
from services.github.github_types import Issue, Parameter

class GitHubService:
    
    repo_url = "https://api.github.com/repos/"
    issues_route = "issues"
    comments_route = "comments"

    # Send a request to the GitHub API to retrieve the issues from a repo
    @staticmethod
    def get_github_issues(route: str, params: Parameter = None, access_token: str = None) -> List[Issue]:
        
        # Set up authentication if needed        
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else None
        
        # Send the API request    
        api_url = f"{GitHubService.repo_url}{route}"

        print(f"Sending request to {api_url}")
        api_params = {
            "labels": params.label,
            "state": params.state
        }

        response = get(api_url, params=api_params, headers=headers)

        issues_list: List[Issue] = []

        if response.status_code == 200:
            issues = response.json()
            # Process the retrieved issues        
            for issue in issues:
                issues_list.append(Issue(id=issue['number'], title=issue['title'], body=issue['body']))     
        else:
            print(f"Error: {response.status_code} - {response.text}")           
        
        return issues_list    

    # Get issues from a repo
    @staticmethod
    def get_issues(repo: str, label: str, state: str = 'open', access_token: str = None) -> List[Issue]:
        """Get the repo issues."""    
        
        # Define the query parameters
        params = Parameter(label=label, state=state)       
        
        route = f"{repo}/{GitHubService.issues_route}"

        # Send the API request    
        issues_list = GitHubService.get_github_issues(route, params, access_token)
        
        return issues_list


    # get an issue by id
    @staticmethod
    def get_issue_by_id(repo: str, issue_number: str, access_token: str = None) -> Issue:
        """Get the repo issue by issue_number."""

        route = f"{repo}/{GitHubService.issues_route}/{issue_number}"
        
        issue = GitHubService.get_github_issues(route, params=None, access_token=access_token)

        return issue[0] if issue else None


    # post a comment to a GitHub issue
    @staticmethod
    def post_issue_comment(repo: str, issue_number: str, comment: str, access_token: str = None) -> bool:
        
        data = {'body': comment}
        route = f"{repo}/{GitHubService.issues_route}/{issue_number}/{GitHubService.comments_route}"
        print(f"Posting comment to {route}")
        # Set up authentication if needed        
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else None
        api_url = f"{GitHubService.repo_url}{route}"
        response = post(api_url, json=data, headers=headers)        
        
        if response.status_code == 201:
            return True
        else:
            return False