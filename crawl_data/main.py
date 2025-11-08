#!/usr/bin/env python3
"""
GitHub Repository Crawler and Classifier
Main entry point for the crawling and classification pipeline
"""

import sys
import argparse
from datetime import datetime

def check_api_keys():
    """Check if API keys are configured"""
    if not Config.API_KEYS or all(key.startswith("ghp_xxx") for key in Config.API_KEYS):
        print("❌ Error: Please configure your GitHub API keys in config.py")
        print("   Replace 'ghp_xxxxxxxxxxxxxxxxxxxx' with your actual tokens")
        return False
    
    print(f"✅ Found {len(Config.API_KEYS)} API key(s)")
    return True

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository Crawler and Classifier')
    parser.add_argument('--crawl', action='store_true', help='Run the crawler')
    parser.add_argument('--classify', action='store_true', help='Run the classifier')
    parser.add_argument('--reset', action='store_true', help='Reset checkpoint and start fresh')
    
    args = parser.parse_args()
    
    if not args.crawl and not args.classify:
        print("Please specify --crawl or --classify (or both)")
        return
    
    # Check API keys
    if args.crawl and not check_api_keys():
        return
    
    # Reset if requested
    if args.reset:
        import os
        files_to_remove = [
            Config.CHECKPOINT_FILE,
            Config.CRAWLED_REPOS_FILE
        ]
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Removed {file}")
    
    # Run crawler
    if args.crawl:
        print("\n" + "="*50)
        print("🚀 STARTING GITHUB CRAWLER")
        print("="*50)
        print(f"⏰ Start time: {datetime.now()}")
        
        crawler = GitHubCrawler()
        crawler.crawl_all_topics()
        
        print(f"⏰ End time: {datetime.now()}")
    
    # Run classifier
    if args.classify:
        print("\n" + "="*50)
        print("🏷️ STARTING TAXONOMY CLASSIFIER")
        print("="*50)
        
        classifier = TaxonomyClassifier()
        classifier.classify_all_repos()
    
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    # Import all modules
    from config import Config, APIKeyManager
    from github_client import GitHubGraphQLClient
    from crawler import GitHubCrawler
    from taxonomy import TaxonomyClassifier
    import time
    
    main()