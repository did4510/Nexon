import os
import logging
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import openai
from typing import List, Dict, Optional, Tuple

# Initialize logging
logger = logging.getLogger("nexon.ai")

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon.zip')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('stopwords')

class AIFeatures:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze the sentiment of a text message"""
        try:
            scores = self.sia.polarity_scores(text)
            return {
                "compound": scores["compound"],
                "positive": scores["pos"],
                "negative": scores["neg"],
                "neutral": scores["neu"]
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"compound": 0, "positive": 0, "negative": 0, "neutral": 1}

    async def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        try:
            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            keywords = [word for word in tokens if word not in self.stop_words and word.isalnum()]
            return list(set(keywords))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            return []

    async def suggest_kb_articles(self, text: str, kb_articles: List[Dict]) -> List[Dict]:
        """Suggest relevant knowledge base articles based on text content"""
        try:
            # Extract keywords from the text
            text_keywords = await self.extract_keywords(text)
            
            # Score each article based on keyword matches
            scored_articles = []
            for article in kb_articles:
                article_keywords = await self.extract_keywords(article["content"])
                score = len(set(text_keywords) & set(article_keywords))
                if score > 0:
                    scored_articles.append({
                        "article": article,
                        "score": score
                    })
            
            # Sort by score and return top matches
            return sorted(scored_articles, key=lambda x: x["score"], reverse=True)[:3]
        except Exception as e:
            logger.error(f"Error in KB article suggestion: {e}")
            return []

    async def generate_ticket_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of the ticket conversation"""
        try:
            # Combine all messages into a single text
            conversation = "\n".join([f"{msg['author']}: {msg['content']}" for msg in messages])
            
            # Use OpenAI to generate a summary
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes support ticket conversations."},
                    {"role": "user", "content": f"Please provide a concise summary of this support ticket conversation:\n\n{conversation}"}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in ticket summary generation: {e}")
            return "Error generating summary"

    async def suggest_macros(self, text: str, macros: List[Dict]) -> List[Dict]:
        """Suggest relevant macros based on ticket content"""
        try:
            # Extract keywords from the text
            text_keywords = await self.extract_keywords(text)
            
            # Score each macro based on keyword matches
            scored_macros = []
            for macro in macros:
                macro_keywords = await self.extract_keywords(macro["content"])
                score = len(set(text_keywords) & set(macro_keywords))
                if score > 0:
                    scored_macros.append({
                        "macro": macro,
                        "score": score
                    })
            
            # Sort by score and return top matches
            return sorted(scored_macros, key=lambda x: x["score"], reverse=True)[:3]
        except Exception as e:
            logger.error(f"Error in macro suggestion: {e}")
            return []

    async def detect_missing_info(self, text: str, category: str) -> List[str]:
        """Detect missing crucial information based on ticket category"""
        try:
            # Define required information by category
            required_info = {
                "Technical Support": ["device", "os", "error message", "steps to reproduce"],
                "Billing Support": ["invoice number", "payment method", "transaction id"],
                "Account Issues": ["username", "email", "account id"],
                "Bug Report": ["steps to reproduce", "expected behavior", "actual behavior"]
            }
            
            # Get required info for the category
            category_requirements = required_info.get(category, [])
            
            # Check for missing information
            missing_info = []
            for requirement in category_requirements:
                if requirement.lower() not in text.lower():
                    missing_info.append(requirement)
            
            return missing_info
        except Exception as e:
            logger.error(f"Error in missing info detection: {e}")
            return []

    async def analyze_ticket_priority(self, text: str, category: str) -> Tuple[str, float]:
        """Analyze ticket priority based on content and category"""
        try:
            # Get sentiment scores
            sentiment = await self.analyze_sentiment(text)
            
            # Define priority factors
            priority_factors = {
                "sentiment": abs(sentiment["compound"]),  # Strong emotions (positive or negative)
                "urgency_keywords": len([word for word in text.lower().split() 
                                      if word in ["urgent", "critical", "emergency", "asap"]]),
                "category_weight": {
                    "Technical Support": 0.8,
                    "Billing Support": 0.6,
                    "Account Issues": 0.7,
                    "Bug Report": 0.5
                }.get(category, 0.5)
            }
            
            # Calculate priority score
            priority_score = (
                priority_factors["sentiment"] * 0.4 +
                priority_factors["urgency_keywords"] * 0.3 +
                priority_factors["category_weight"] * 0.3
            )
            
            # Determine priority level
            if priority_score > 0.7:
                priority = "High"
            elif priority_score > 0.4:
                priority = "Medium"
            else:
                priority = "Low"
            
            return priority, priority_score
        except Exception as e:
            logger.error(f"Error in priority analysis: {e}")
            return "Medium", 0.5

# Create singleton instance
ai_features = AIFeatures() 