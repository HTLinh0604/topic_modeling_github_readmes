import json
import os
from typing import List, Dict
from datetime import datetime

class Config:
    # Danh sách 50 topics theo 10 nhóm
    TOPICS = {
        "AI_DataScience": ["machine-learning", "deep-learning", "artificial-intelligence", "data-science", "nlp"],
        "WebDevelopment": ["web", "frontend", "backend", "javascript", "react"],
        "MobileDevelopment": ["android", "ios", "flutter", "react-native", "swift"],
        "DevOpsCloud": ["devops", "docker", "kubernetes", "aws", "ci-cd"],
        "DatabasesDataEng": ["sql", "database", "nosql", "mongodb", "postgresql"],
        "SecurityCrypto": ["security", "cybersecurity", "penetration-testing", "cryptography", "malware"],
        "ProgrammingLangs": ["python", "java", "cplusplus", "go", "rust"],
        "SystemsInfra": ["linux", "operating-system", "distributed-systems", "networking", "compiler"],
        "EmergingTech": ["blockchain", "web3", "cryptocurrency", "robotics", "ar"],
        "SoftwareEngTools": ["testing", "github-actions", "vscode-extension", "automation", "monitoring"]
    }
    
    # Flatten topics list
    ALL_TOPICS = [topic for topics in TOPICS.values() for topic in topics]
    
    # GitHub API Keys - Thêm keys của bạn vào đây
    API_KEYS = [
        "key1",  # Key 1
        "key2",  # Key 2
        "key3"
        # Thêm nhiều keys nếu cần
    ]
    
    # Crawl settings
    REPOS_PER_TOPIC = 2000
    UNIQUE_REPOS_PER_TOPIC = 1000
    REPOS_PER_SORT = 500
    
    # File paths
    CHECKPOINT_FILE = "checkpoint.json"
    CSV_FILE = "github_repos.csv"
    README_FILE = "readme_data.jsonl"
    CRAWLED_REPOS_FILE = "crawled_repos.json"
    
    # Rate limit threshold
    RATE_LIMIT_THRESHOLD = 100

class APIKeyManager:
    def __init__(self, keys: List[str]):
        self.keys = keys
        self.current_index = 0
        self.rate_limits = {}
        
    def get_current_key(self):
        if not self.keys:
            raise ValueError("No API keys configured")
        return self.keys[self.current_index]
    
    def switch_to_next_key(self):
        """Switch to next API key"""
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(f"🔄 Switched to API key #{self.current_index + 1}")
        return self.get_current_key()
    
    def update_rate_limit(self, remaining: int, reset_at: str):
        """Update rate limit info for current key"""
        self.rate_limits[self.get_current_key()] = {
            "remaining": remaining,
            "reset_at": reset_at
        }
        
    def should_switch_key(self, remaining: int) -> bool:
        """Check if should switch to next key"""
        return remaining <= Config.RATE_LIMIT_THRESHOLD