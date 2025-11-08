import pandas as pd
import json
from collections import Counter
from typing import Dict, List, Tuple
from config import Config


class TaxonomyClassifier:
    def __init__(self):
        self.taxonomy = Config.TOPICS
        self.priority_order = [
            "AI_DataScience",
            "WebDevelopment", 
            "MobileDevelopment",
            "DevOpsCloud",
            "DatabasesDataEng",
            "SecurityCrypto",
            "ProgrammingLangs",
            "SystemsInfra",
            "EmergingTech",
            "SoftwareEngTools"
        ]
        
    def load_repos(self) -> pd.DataFrame:
        """Load repository data from CSV"""
        return pd.read_csv(Config.CSV_FILE)
    
    def analyze_topic_frequency(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze frequency of each topic"""
        topic_counter = Counter()
        
        for topics_str in df['topics'].dropna():
            topics = topics_str.split(';')
            topic_counter.update(topics)
        
        return dict(topic_counter)
    
    def classify_repository(self, topics_str: str) -> str:
        """Classify a repository into one category"""
        if pd.isna(topics_str) or not topics_str:
            return "Others"
        
        topics = set(topics_str.split(';'))
        category_scores = {}
        
        # Count topics per category
        for category, category_topics in self.taxonomy.items():
            score = sum(1 for topic in topics if topic in category_topics)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return "Others"
        
        # Find categories with max score
        max_score = max(category_scores.values())
        top_categories = [cat for cat, score in category_scores.items() if score == max_score]
        
        # If tie, use priority order
        if len(top_categories) > 1:
            for category in self.priority_order:
                if category in top_categories:
                    return category
        
        return top_categories[0] if top_categories else "Others"
    
    def classify_all_repos(self):
        """Classify all repositories and save results"""
        print("\n🏷️ Starting Taxonomy Classification")
        
        # Load data
        df = self.load_repos()
        print(f"📊 Loaded {len(df)} repositories")
        
        # Analyze topic frequency
        topic_freq = self.analyze_topic_frequency(df)
        print(f"\n📈 Top 20 most frequent topics:")
        for topic, count in sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  - {topic}: {count}")
        
        # Classify each repository
        df['category'] = df['topics'].apply(self.classify_repository)
        
        # Statistics
        category_counts = df['category'].value_counts()
        print(f"\n📊 Category distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  - {category}: {count} ({percentage:.1f}%)")
        
        # Save classified data
        output_file = "github_repos_classified.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Classified data saved to {output_file}")
        
        # Save category mapping
        category_mapping = {
            "taxonomy": self.taxonomy,
            "priority_order": self.priority_order,
            "statistics": category_counts.to_dict(),
            "topic_frequency": topic_freq
        }
        
        with open("taxonomy_mapping.json", 'w') as f:
            json.dump(category_mapping, f, indent=2)
        
        print("✅ Taxonomy mapping saved to taxonomy_mapping.json")
        
        return df