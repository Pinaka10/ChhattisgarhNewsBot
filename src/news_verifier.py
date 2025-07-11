#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News Verifier for Chhattisgarh News Bot
Verifies news using Hindi-BERT and cross-source validation
"""

import logging
import json
import re
from datetime import datetime
import pytz
from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)

class NewsVerifier:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        self.today = datetime.now(self.ist).date()
        
        # Load Hindi-BERT model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("google/muril-base-cased")
            self.model = AutoModel.from_pretrained("google/muril-base-cased")
            logger.info("Hindi-BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Hindi-BERT model: {e}")
            self.tokenizer = None
            self.model = None
        
        # Opinion keywords to filter out
        self.opinion_keywords = [
            'चाहिए', 'कथित', 'विचार', 'राय', 'मानना', 'लगता', 'संभावना',
            'अनुमान', 'अटकल', 'संदेह', 'शायद', 'हो सकता', 'माना जा रहा',
            'सूत्रों के अनुसार', 'अफवाह', 'दावा', 'आरोप'
        ]
        
        # News categories for importance ranking
        self.category_weights = {
            'crime': ['अपराध', 'गिरफ्तार', 'हत्या', 'चोरी', 'ठगी', 'फ्रॉड', 'पुलिस', 'सीबीआई'],
            'politics': ['नीति', 'सरकार', 'मुख्यमंत्री', 'मंत्री', 'विधायक', 'चुनाव', 'राजनीति'],
            'accident': ['दुर्घटना', 'हादसा', 'मौत', 'घायल', 'अस्पताल', 'एम्बुलेंस'],
            'development': ['विकास', 'परियोजना', 'योजना', 'निर्माण', 'सड़क', 'पुल', 'अस्पताल'],
            'weather': ['मौसम', 'बारिश', 'तूफान', 'बाढ़', 'सूखा', 'अलर्ट'],
            'health': ['स्वास्थ्य', 'बीमारी', 'डॉक्टर', 'इलाज', 'वैक्सीन', 'अस्पताल'],
            'education': ['शिक्षा', 'स्कूल', 'कॉलेज', 'परीक्षा', 'छात्र', 'शिक्षक']
        }

    def get_text_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for text"""
        if not self.tokenizer or not self.model:
            # Fallback to simple text similarity
            return np.array([hash(text) % 1000])
        
        try:
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors="pt", 
                                  truncation=True, max_length=512, padding=True)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].numpy()
            
            return embedding.flatten()
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return np.array([hash(text) % 1000])

    def extract_key_elements(self, article: Dict) -> Dict:
        """Extract key elements (who, what, where, when) from article"""
        title = article.get('title', '')
        body = article.get('body', '')
        text = f"{title} {body}"
        
        elements = {
            'who': [],
            'what': [],
            'where': [],
            'when': []
        }
        
        # Extract locations (where)
        location_patterns = [
            r'(रायपुर|बिलासपुर|दुर्ग|भिलाई|कोरबा|राजनांदगांव|जगदलपुर|अंबिकापुर)',
            r'(छत्तीसगढ़|बस्तर|सरगुजा|दंतेवाड़ा|नारायणपुर|बीजापुर|सुकमा)',
            r'(\w+पुर|\w+गढ़|\w+नगर|\w+बाद)'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            elements['where'].extend(matches)
        
        # Extract people/organizations (who)
        who_patterns = [
            r'(मुख्यमंत्री|मंत्री|विधायक|सांसद|कलेक्टर|एसपी)',
            r'(पुलिस|सीबीआई|ईडी|आईटी|प्रशासन)',
            r'([A-Za-z\s]+\s(?:सिंह|शर्मा|वर्मा|गुप्ता|अग्रवाल))'
        ]
        
        for pattern in who_patterns:
            matches = re.findall(pattern, text)
            elements['who'].extend(matches)
        
        # Extract events (what)
        what_patterns = [
            r'(गिरफ्तार|हत्या|चोरी|ठगी|दुर्घटना|हादसा)',
            r'(योजना|परियोजना|निर्माण|उद्घाटन|शुरुआत)',
            r'(बैठक|सम्मेलन|कार्यक्रम|समारोह)'
        ]
        
        for pattern in what_patterns:
            matches = re.findall(pattern, text)
            elements['what'].extend(matches)
        
        # Extract time (when) - look for dates
        when_patterns = [
            r'(\d{1,2}\s(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर))',
            r'(आज|कल|परसों|बीते\s\w+|गुजरे\s\w+)'
        ]
        
        for pattern in when_patterns:
            matches = re.findall(pattern, text)
            elements['when'].extend(matches)
        
        return elements

    def calculate_similarity(self, article1: Dict, article2: Dict) -> float:
        """Calculate similarity between two articles"""
        # Get embeddings
        text1 = f"{article1.get('title', '')} {article1.get('body', '')}"
        text2 = f"{article2.get('title', '')} {article2.get('body', '')}"
        
        emb1 = self.get_text_embedding(text1)
        emb2 = self.get_text_embedding(text2)
        
        # Calculate cosine similarity
        if len(emb1.shape) == 1:
            emb1 = emb1.reshape(1, -1)
        if len(emb2.shape) == 1:
            emb2 = emb2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        
        # Also check key elements similarity
        elements1 = self.extract_key_elements(article1)
        elements2 = self.extract_key_elements(article2)
        
        element_similarity = 0
        total_elements = 0
        
        for key in elements1:
            if elements1[key] and elements2[key]:
                common = set(elements1[key]) & set(elements2[key])
                total = set(elements1[key]) | set(elements2[key])
                if total:
                    element_similarity += len(common) / len(total)
                    total_elements += 1
        
        if total_elements > 0:
            element_similarity /= total_elements
        
        # Combine similarities
        final_similarity = (similarity * 0.7) + (element_similarity * 0.3)
        
        return final_similarity

    def is_opinion_piece(self, article: Dict) -> bool:
        """Check if article is an opinion piece"""
        text = f"{article.get('title', '')} {article.get('body', '')}".lower()
        
        opinion_count = sum(1 for keyword in self.opinion_keywords 
                          if keyword.lower() in text)
        
        # If more than 2 opinion keywords, likely an opinion piece
        return opinion_count > 2

    def categorize_article(self, article: Dict) -> Tuple[str, float]:
        """Categorize article and return importance score"""
        text = f"{article.get('title', '')} {article.get('body', '')}".lower()
        
        category_scores = {}
        
        for category, keywords in self.category_weights.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'general', 1.0
        
        # Get category with highest score
        best_category = max(category_scores, key=category_scores.get)
        
        # Calculate importance score
        importance_weights = {
            'crime': 3.0,
            'accident': 2.8,
            'politics': 2.5,
            'development': 2.0,
            'health': 1.8,
            'weather': 1.5,
            'education': 1.3,
            'general': 1.0
        }
        
        importance = importance_weights.get(best_category, 1.0)
        
        return best_category, importance

    def verify_with_sources(self, articles: List[Dict]) -> List[Dict]:
        """Verify articles by cross-referencing with multiple sources"""
        verified_articles = []
        
        # Group articles by similarity
        article_groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if i in processed:
                continue
            
            group = [article1]
            processed.add(i)
            
            for j, article2 in enumerate(articles[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self.calculate_similarity(article1, article2)
                
                if similarity > 0.8:  # High similarity threshold
                    group.append(article2)
                    processed.add(j)
            
            if len(group) >= 3:  # At least 3 sources
                article_groups.append(group)
        
        # Process verified groups
        for group in article_groups:
            # Select best article from group (longest content, most recent)
            best_article = max(group, key=lambda x: (
                len(x.get('body', '')),
                x.get('timestamp', '')
            ))
            
            # Add verification info
            best_article['verified'] = True
            best_article['source_count'] = len(group)
            best_article['sources'] = [art['source'] for art in group]
            
            # Categorize and score
            category, importance = self.categorize_article(best_article)
            best_article['category'] = category
            best_article['importance'] = importance
            
            verified_articles.append(best_article)
        
        return verified_articles

    async def verify_news(self, raw_articles: List[Dict]) -> List[Dict]:
        """Main verification function"""
        logger.info(f"Starting verification of {len(raw_articles)} articles")
        
        # Filter out opinion pieces
        factual_articles = [
            article for article in raw_articles 
            if not self.is_opinion_piece(article)
        ]
        
        logger.info(f"Filtered to {len(factual_articles)} factual articles")
        
        # Verify with cross-source validation
        verified_articles = self.verify_with_sources(factual_articles)
        
        logger.info(f"Verified {len(verified_articles)} articles")
        
        # Sort by importance and recency
        verified_articles.sort(
            key=lambda x: (x.get('importance', 1.0), x.get('timestamp', '')),
            reverse=True
        )
        
        # Select top 6-8 articles
        final_articles = verified_articles[:8]
        
        logger.info(f"Selected {len(final_articles)} final articles")
        
        # Save verification results
        with open(f'verified_news_{self.today}.json', 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, ensure_ascii=False, indent=2)
        
        return final_articles