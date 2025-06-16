"""
Text processing utilities for keyword extraction and similarity calculations.
"""
import re
import logging
from typing import List, Union
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

def ensure_nltk_data():
    """
    Ensure all required NLTK data is downloaded.
    Provides better error handling and logging.
    """
    required_data = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger'
    }
    
    for name, path in required_data.items():
        try:
            nltk.data.find(path)
            logger.debug(f"NLTK data '{name}' already downloaded")
        except LookupError:
            try:
                logger.info(f"Downloading NLTK data: {name}")
                nltk.download(name, quiet=True)
                logger.info(f"Successfully downloaded NLTK data: {name}")
            except Exception as e:
                logger.error(f"Failed to download NLTK data '{name}': {str(e)}")
                raise RuntimeError(f"Failed to download required NLTK data: {name}") from e

# Initialize NLTK data
ensure_nltk_data()

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using basic NLP techniques.
    
    Args:
        text: The text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    keywords = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in stop_words and len(token) > 2
    ]
    
    # Get most common words
    word_freq = Counter(keywords)
    return [word for word, _ in word_freq.most_common(max_keywords)]

def calculate_similarity(text1: Union[str, List[str]], text2: Union[str, List[str]]) -> float:
    """
    Calculate similarity between two texts or lists of keywords using Jaccard similarity.
    
    Args:
        text1: First text or list of keywords
        text2: Second text or list of keywords
        
    Returns:
        Similarity score between 0 and 1
    """
    # Convert strings to keywords if needed
    if isinstance(text1, str):
        text1 = extract_keywords(text1)
    if isinstance(text2, str):
        text2 = extract_keywords(text2)
    
    # Convert to sets
    set1 = set(text1)
    set2 = set(text2)
    
    if not set1 or not set2:
        return 0.0
        
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0