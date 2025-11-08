import requests
import time
from typing import Dict, List, Optional
from tqdm import tqdm
import json

class GitHubGraphQLClient:
    def __init__(self, api_key_manager):
        self.api_key_manager = api_key_manager
        self.base_url = "https://api.github.com/graphql"
        
    def execute_query(self, query: str, variables: Dict = None, retry_count: int = 0) -> Dict:
        """Execute GraphQL query with automatic key rotation and better error handling"""
        headers = {
            "Authorization": f"Bearer {self.api_key_manager.get_current_key()}",
            "Content-Type": "application/json"
        }
        
        max_retries = 5
        
        if retry_count >= max_retries:
            raise Exception(f"Max retries ({max_retries}) exceeded")
        
        try:
            response = requests.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
                headers=headers,
                timeout=60  # Increased timeout
            )
            
            # Handle different status codes
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON response, retrying...")
                    time.sleep(5)
                    return self.execute_query(query, variables, retry_count + 1)
                
                # Check rate limit
                if "data" in data and data["data"] and "rateLimit" in data["data"]:
                    rate_limit = data["data"]["rateLimit"]
                    remaining = rate_limit["remaining"]
                    reset_at = rate_limit["resetAt"]
                    
                    print(f"  📊 Rate limit: {remaining} remaining")
                    self.api_key_manager.update_rate_limit(remaining, reset_at)
                    
                    if self.api_key_manager.should_switch_key(remaining):
                        self.api_key_manager.switch_to_next_key()
                
                # Check for GraphQL errors
                if "errors" in data:
                    error_msg = str(data["errors"])
                    if "rate limit" in error_msg.lower():
                        print(f"⚠️ Rate limit in response, switching key...")
                        self.api_key_manager.switch_to_next_key()
                        time.sleep(2)
                        return self.execute_query(query, variables, retry_count + 1)
                    elif "timeout" in error_msg.lower():
                        print(f"⚠️ Query timeout, retrying with smaller batch...")
                        time.sleep(5)
                        return None  # Signal to reduce batch size
                    else:
                        print(f"⚠️ GraphQL errors: {data['errors']}")
                
                return data
                
            elif response.status_code == 401:
                print(f"❌ Authentication failed, switching key...")
                self.api_key_manager.switch_to_next_key()
                return self.execute_query(query, variables, retry_count + 1)
                
            elif response.status_code == 403:
                print(f"⚠️ Rate limit (403), switching key...")
                self.api_key_manager.switch_to_next_key()
                time.sleep(2)
                return self.execute_query(query, variables, retry_count + 1)
                
            elif response.status_code in [502, 503, 504]:
                # Gateway errors - GitHub is having issues
                print(f"⚠️ GitHub server error ({response.status_code}), waiting and retrying...")
                wait_time = min(60, 10 * (retry_count + 1))  # Progressive backoff
                time.sleep(wait_time)
                return self.execute_query(query, variables, retry_count + 1)
                
            else:
                print(f"❌ Unexpected status {response.status_code}")
                time.sleep(5)
                return self.execute_query(query, variables, retry_count + 1)
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Request timeout, retrying...")
            time.sleep(10)
            return self.execute_query(query, variables, retry_count + 1)
            
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error: {e}, retrying...")
            time.sleep(10)
            return self.execute_query(query, variables, retry_count + 1)
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(5)
            return self.execute_query(query, variables, retry_count + 1)
    
    def search_repos_simple_query(self, search_query: str, batch_size: int = 20, after_cursor: str = None) -> str:
        """Simplified query without README (fetch separately)"""
        after = f', after: "{after_cursor}"' if after_cursor else ""
        
        return f"""
        query {{
            rateLimit {{
                remaining
                resetAt
            }}
            search(
                query: "{search_query}"
                type: REPOSITORY
                first: {batch_size}
                {after}
            ) {{
                repositoryCount
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    ... on Repository {{
                        id
                        name
                        nameWithOwner
                        description
                        primaryLanguage {{
                            name
                        }}
                        repositoryTopics(first: 20) {{
                            nodes {{
                                topic {{
                                    name
                                }}
                            }}
                        }}
                        stargazerCount
                        forkCount
                        createdAt
                        updatedAt
                        url
                        defaultBranchRef {{
                            name
                        }}
                    }}
                }}
            }}
        }}
        """
    
    def get_readme_query(self, owner: str, name: str) -> str:
        """Separate query to fetch README"""
        return f"""
        query {{
            repository(owner: "{owner}", name: "{name}") {{
                readme: object(expression: "HEAD:README.md") {{
                    ... on Blob {{
                        text
                    }}
                }}
                readmeLower: object(expression: "HEAD:readme.md") {{
                    ... on Blob {{
                        text
                    }}
                }}
                readmeUpper: object(expression: "HEAD:README.MD") {{
                    ... on Blob {{
                        text
                    }}
                }}
                readmeRst: object(expression: "HEAD:README.rst") {{
                    ... on Blob {{
                        text
                    }}
                }}
            }}
        }}
        """