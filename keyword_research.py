import requests 
import pandas as pd
import os 
import time 
import json 
from collections import Counter 
from dotenv import load_dotenv 

load_dotenv()

class KeywordResearchTool:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.serper_key = os.getenv("SERPER_KEY")
        
        if not self.serpapi_key and not self.serper_key:
            print("Warning: No API keys found. Will use fallback keyword generation method.")
            
    def get_keywords_from_serpapi(self, query, limit=5):
        if not self.serpapi_key:
            print("SerpAPI key not found.")
            return []
        
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "device": "desktop",
            "gl": "us",
            "hl": "en",
            "location": "United States"
        }
        
        try: 
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            related_searches = []
            if "related_searches" in data:
                related_searches = [item["query"] for item in data["related_searches"]]
                
                questions = []
                if "related_questions" in data:
                    questions = [item["question"] for item in data["related_questions"]]
                    
                    keywords = related_searches + questions
                    return keywords[:limit]
                
        except Exception as e:
            print(f"Error fetching keywords from SerpAPI: {str(e)}")
            return []
        
    def get_keywords_from_serper(self, query, limit=5):
        if not self.serper_key:
            print("Serper API key not found.")
            return []
        
        url = "https://serpapi.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "gl": "us",
            "hl": "en"
        }
        
        try: 
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            related_searches = []
            if "related_searches" in data:
                related_searches = [item for item in data["peopleAlsoAsk"]]
                
            keywords = related_searches + questions
            return keywords[:limit]
        
        except Exception as e:
            print(f"Error fetching keywords from Serper API: {str(e)}")
            return []
        
    def generate_keywords_fallback(self, product_name, product_category):
        
        patterns = [
            f"best {product_name}",
            f"top {product_name} {product_category}",
            f"{product_name} review",
            f"affordable {product_name}",
            f"{product_name} vs",
            f"how to choose {product_name}",
            f"{product_name} for beginners",
            f"{product_name} features",
            f"{product_name} buying guide",
            f"{product_category} {product_name} comparison"
        ]
        
        keywords = [kw for kw in patterns if len(kw) < 60]
        
        return keywords[:5]
    
    def analyze_text_for_keywords(self, text):
        common_words = set([
            "and", "the", "to", "a", "of", "for", "in", "with", "on", "is", "that", "this",
            "it", "by", "from", "or", "as", "an", "at", "be", "are", "you", "your", "has",
            "have", "had", "was", "were", "will", "would", "could", "should", "can"
        ])
        
        cleaned_text = text.lower() 
        for char in ".,!?;:()[]{}\"'":
            cleaned_text = cleaned_text.replace(char, " ")
            
        words = cleaned_text.split()
        filtered_words = [word for word in words if word not in common_words and len(word) > 3]
        
        word_counts = Counter(filtered_words)
        
        bigrams = []
        for i in range(len(filtered_words) - 1):
            bigrams.append(f"{filtered_words[i]} {filtered_words[i+1]}")
            
        bigram_counts = Counter(bigrams)
        
        top_words = [word for word, count in word_counts.most_common(5)]
        top_bigrams = [bigram for bigram, count in bigram_counts.most_common(5)]
        
        return top_words + top_bigrams 
    
    def research_keywords_for_product(self, product, use_api=True):
        print(f"Researching keywords for: {product['name']}")
        
        product_name = ''.join(product['name'].split()[:4])
        category = product['category']
        search_query = f"{product_name} {category}"
        
        keywords = []
        
        if use_api and (self.serpapi_key or self.serper_key):
            if self.serpapi_key:
                serpapi_keywords = self.get_keywords_from_serpapi(search_query)
                if serpapi_keywords:
                    keywords.extend(serpapi_keywords)
                    
            if self.serper_key and len(keywords) < 5:
                serper_keywords = self.get_keywords_from_serper(search_query)
                if serper_keywords:
                    keywords.extend(serper_keywords)
                    
        if len(keywords) < 3:
            fallback_keywords = self.generate_keywords_fallback(product_name, category)
            keywords.extend(fallback_keywords)
            
            if 'name' in product:
                extracted_keywords = self.analyze_text_for_keywords(product['name'])
                keywords.extend(extracted_keywords)
                
        unique_keywords = list(dict.fromkeys(keywords))
        final_keywords = unique_keywords[:4]
        
        print(f"Selected keywords: {final_keywords}")
        return final_keywords
    
    def research_keywords_for_products(self, products, output_file="data/product_keywords.csv"):
        results = []
        
        for product in products:
            keywords = self.research_keywords_for_product(product)
            
            product_with_keywords = product.copy()
            product_with_keywords['keywords'] = ', '.join(keywords)
            results.append(product_with_keywords)
            
            time.sleep(1)
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Saved product keywords to {output_file}")
        
        return results 
    
if __name__ == "__main__":
    try:
        products_df = pd.read_csv("data/trending_products.csv")
        products = products_df.to_dict(orient='records')
        
        keyword_tool = KeywordResearchTool()
        products_with_keywords = keyword_tool.research_keywords_for_products(products)
        
        print(f"Added keywords to {len(products_with_keywords)} products")
        
    except Exception as e:
        print(f"Error in keyword research: {str(e)}")