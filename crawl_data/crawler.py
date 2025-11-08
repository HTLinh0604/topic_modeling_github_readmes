import csv
import json
import os
import random
import time
from datetime import datetime
from typing import Set, Dict, List
from tqdm import tqdm
from config import Config, APIKeyManager
from github_client import GitHubGraphQLClient

class GitHubCrawler:
    def __init__(self):
        self.api_key_manager = APIKeyManager(Config.API_KEYS)
        self.client = GitHubGraphQLClient(self.api_key_manager)
        self.checkpoint = self.load_checkpoint()
        self.crawled_repos = self.load_crawled_repos()
        
    def load_checkpoint(self) -> Dict:
        """Load checkpoint from file"""
        if os.path.exists(Config.CHECKPOINT_FILE):
            with open(Config.CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        return {
            "current_topic_index": 0,
            "current_sort_index": 0, 
            "current_page": None,
            "repos_crawled_for_topic": 0,
            "batch_size": 20  # Start with smaller batch
        }
    
    def save_checkpoint(self):
        """Save checkpoint to file"""
        with open(Config.CHECKPOINT_FILE, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def load_crawled_repos(self) -> Set[str]:
        """Load set of already crawled repo IDs"""
        if os.path.exists(Config.CRAWLED_REPOS_FILE):
            with open(Config.CRAWLED_REPOS_FILE, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_crawled_repos(self):
        """Save crawled repo IDs"""
        with open(Config.CRAWLED_REPOS_FILE, 'w') as f:
            json.dump(list(self.crawled_repos), f)
    
    def is_english_readme(self, readme_text: str) -> bool:
        """Check if README is in English"""
        if not readme_text or len(readme_text) < 50:
            return False
        
        # Common English words to check
        english_indicators = ['the', 'is', 'and', 'to', 'of', 'in', 'for', 'with', 'this', 'that']
        text_lower = readme_text.lower()[:1000]
        
        english_count = sum(1 for word in english_indicators if f' {word} ' in text_lower)
        return english_count >= 3
    
    def fetch_readme(self, owner: str, repo_name: str) -> str:
        """Fetch README content separately"""
        try:
            query = self.client.get_readme_query(owner, repo_name)
            result = self.client.execute_query(query)
            
            if not result or "data" not in result:
                return None
                
            repo_data = result["data"].get("repository", {})
            
            # Try different README variations
            readme_text = None
            for key in ["readme", "readmeLower", "readmeUpper", "readmeRst"]:
                if repo_data.get(key) and repo_data[key].get("text"):
                    readme_text = repo_data[key]["text"]
                    break
                    
            return readme_text
            
        except Exception as e:
            print(f"  ⚠️ Error fetching README for {owner}/{repo_name}: {e}")
            return None
    
    def save_repo_to_csv(self, repo_data: Dict):
        """Save repository data to CSV"""
        file_exists = os.path.exists(Config.CSV_FILE)
        
        with open(Config.CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'repo_id', 'name', 'full_name', 'description', 'topics',
                'language', 'stars_count', 'forks_count', 'created_at',
                'updated_at', 'url'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(repo_data)
    
    def save_readme_to_jsonl(self, repo_id: str, full_name: str, readme_text: str):
        """Save README to JSONL file (append mode)"""
        with open(Config.README_FILE, 'a', encoding='utf-8') as f:
            json_line = json.dumps({
                'repo_id': repo_id,
                'full_name': full_name,
                'readme': readme_text,
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False)
            f.write(json_line + '\n')
    
    def build_search_query(self, topic: str, sort: str) -> str:
        """Build search query string"""
        # Base query with topic
        query_parts = [f'topic:{topic}']
        
        # Add language filter
        query_parts.append('language:English')
        
        # Add README requirement - using 'in:readme' to ensure README exists
        query_parts.append('in:readme')
        
        # Add sort-specific filters
        if sort == 'stars':
            query_parts.append('stars:>10')  # At least 10 stars
        elif sort == 'forks':
            query_parts.append('forks:>5')   # At least 5 forks
        elif sort == 'updated':
            query_parts.append('pushed:>2020-01-01')  # Updated after 2020
        
        # Sort mapping
        sort_map = {
            'stars': 'sort:stars-desc',
            'forks': 'sort:forks-desc',
            'updated': 'sort:updated-desc',
            'best-match': ''  # Default sort
        }
        
        query = ' '.join(query_parts)
        if sort_map.get(sort):
            query += ' ' + sort_map[sort]
            
        return query
    
    def crawl_repos_for_topic(self, topic: str, topic_index: int):
        """Crawl repositories for a specific topic"""
        print(f"\n📌 Crawling topic: {topic} ({topic_index + 1}/{len(Config.ALL_TOPICS)})")
        
        sort_options = ['stars', 'forks', 'updated', 'best-match']
        repos_per_sort = Config.REPOS_PER_SORT
        topic_repos = {}
        
        # Resume from checkpoint
        start_sort_index = self.checkpoint.get("current_sort_index", 0) if \
                          self.checkpoint.get("current_topic_index") == topic_index else 0
        
        for sort_index, sort_option in enumerate(sort_options[start_sort_index:], start_sort_index):
            print(f"\n  🔍 Sort by: {sort_option}")
            
            # Build search query
            search_query = self.build_search_query(topic, sort_option)
            print(f"  📝 Query: {search_query}")
            
            cursor = self.checkpoint.get("current_page") if \
                    self.checkpoint.get("current_topic_index") == topic_index and \
                    self.checkpoint.get("current_sort_index") == sort_index else None
            
            repos_crawled = 0
            has_next_page = True
            batch_size = self.checkpoint.get("batch_size", 20)
            consecutive_errors = 0
            
            pbar = tqdm(total=repos_per_sort, desc=f"  {sort_option}")
            
            while has_next_page and repos_crawled < repos_per_sort:
                try:
                    # Execute search query
                    query = self.client.search_repos_simple_query(search_query, batch_size, cursor)
                    result = self.client.execute_query(query)
                    
                    if not result:
                        # Reduce batch size if query failed
                        batch_size = max(5, batch_size // 2)
                        self.checkpoint["batch_size"] = batch_size
                        print(f"  ⚠️ Reducing batch size to {batch_size}")
                        consecutive_errors += 1
                        if consecutive_errors > 5:
                            print(f"  ❌ Too many errors, skipping {sort_option}")
                            break
                        time.sleep(10)
                        continue
                    
                    consecutive_errors = 0  # Reset on success
                    
                    if "data" not in result or not result["data"] or "search" not in result["data"]:
                        print(f"  ⚠️ No data returned for {topic} - {sort_option}")
                        break
                    
                    search_data = result["data"]["search"]
                    has_next_page = search_data["pageInfo"]["hasNextPage"]
                    cursor = search_data["pageInfo"]["endCursor"]
                    
                    # Process repositories
                    for repo in search_data["nodes"]:
                        if not repo:
                            continue
                        
                        repo_id = repo["id"]
                        
                        # Skip if already crawled
                        if repo_id in self.crawled_repos:
                            continue
                        
                        # Extract basic info
                        full_name = repo["nameWithOwner"]
                        owner, repo_name = full_name.split('/')
                        
                        # Extract topics
                        topics = []
                        if repo.get("repositoryTopics"):
                            for topic_node in repo["repositoryTopics"]["nodes"]:
                                if topic_node and topic_node.get("topic"):
                                    topics.append(topic_node["topic"]["name"])
                        
                        # Skip if no topics
                        if not topics:
                            continue
                        
                        # Fetch README separately with retry
                        readme_text = None
                        for attempt in range(3):
                            readme_text = self.fetch_readme(owner, repo_name)
                            if readme_text:
                                break
                            time.sleep(2)
                        
                        # Check README
                        if not readme_text or not self.is_english_readme(readme_text):
                            continue
                        
                        # Prepare repo data
                        repo_data = {
                            'repo_id': repo_id,
                            'name': repo["name"],
                            'full_name': full_name,
                            'description': repo.get("description", ""),
                            'topics': ";".join(topics),
                            'language': repo["primaryLanguage"]["name"] if repo.get("primaryLanguage") else "",
                            'stars_count': repo["stargazerCount"],
                            'forks_count': repo["forkCount"],
                            'created_at': repo["createdAt"],
                            'updated_at': repo["updatedAt"],
                            'url': repo["url"]
                        }
                        
                        # Save data
                        self.save_repo_to_csv(repo_data)
                        self.save_readme_to_jsonl(repo_id, full_name, readme_text)
                        
                        # Track progress
                        self.crawled_repos.add(repo_id)
                        topic_repos[repo_id] = repo_data
                        repos_crawled += 1
                        pbar.update(1)
                        
                        # Update checkpoint
                        self.checkpoint.update({
                            "current_topic_index": topic_index,
                            "current_sort_index": sort_index,
                            "current_page": cursor,
                            "repos_crawled_for_topic": len(topic_repos),
                            "batch_size": batch_size
                        })
                        
                        # Save periodically
                        if repos_crawled % 10 == 0:
                            self.save_checkpoint()
                            self.save_crawled_repos()
                        
                        if repos_crawled >= repos_per_sort:
                            break
                    
                    # Gradually increase batch size on success
                    if batch_size < 20 and consecutive_errors == 0:
                        batch_size = min(20, batch_size + 5)
                        self.checkpoint["batch_size"] = batch_size
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrupted by user. Saving checkpoint...")
                    self.save_checkpoint()
                    self.save_crawled_repos()
                    raise
                    
                except Exception as e:
                    print(f"\n  ❌ Error: {e}")
                    consecutive_errors += 1
                    if consecutive_errors > 5:
                        print(f"  ❌ Too many consecutive errors, moving to next sort option")
                        break
                    time.sleep(10)
                    continue
            
            pbar.close()
            
            # Save after each sort option
            self.save_checkpoint()
            self.save_crawled_repos()
        
        print(f"\n  📊 Total unique repos for {topic}: {len(topic_repos)}")
        
        # Reset for next topic
        self.checkpoint["current_sort_index"] = 0
        self.checkpoint["current_page"] = None
        self.checkpoint["batch_size"] = 20
        self.save_checkpoint()
        
        return topic_repos
    
    def crawl_all_topics(self):
        """Main crawling function"""
        print("🚀 Starting GitHub Repository Crawler")
        print(f"📋 Total topics to crawl: {len(Config.ALL_TOPICS)}")
        print(f"🔑 Available API keys: {len(Config.API_KEYS)}")
        
        start_topic_index = self.checkpoint.get("current_topic_index", 0)
        
        try:
            for i, topic in enumerate(Config.ALL_TOPICS[start_topic_index:], start_topic_index):
                self.crawl_repos_for_topic(topic, i)
                
                self.checkpoint["current_topic_index"] = i + 1
                self.save_checkpoint()
                self.save_crawled_repos()
                
                # Small break between topics
                if i < len(Config.ALL_TOPICS) - 1:
                    print("\n⏸️ Pausing between topics...")
                    time.sleep(5)
            
            print("\n✅ Crawling completed!")
            print(f"📊 Total unique repositories crawled: {len(self.crawled_repos)}")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Crawling stopped by user")
            print(f"📊 Progress saved. Crawled {len(self.crawled_repos)} repos so far.")
            print("ℹ️ Run again to resume from checkpoint.")