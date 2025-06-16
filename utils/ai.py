"""
AI utilities for sentiment analysis, tag generation, and ticket summarization.
"""
from typing import List, Dict, Any, Tuple, Optional
import re
from textblob import TextBlob
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk
from datetime import datetime
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Common technical support keywords and their categories
TECH_KEYWORDS = {
    'error': 'error',
    'bug': 'bug',
    'crash': 'error',
    'failed': 'error',
    'not working': 'error',
    'broken': 'error',
    'help': 'assistance',
    'support': 'assistance',
    'how to': 'assistance',
    'problem': 'issue',
    'issue': 'issue',
    'login': 'account',
    'account': 'account',
    'password': 'account',
    'payment': 'billing',
    'billing': 'billing',
    'charge': 'billing',
    'refund': 'billing',
    'slow': 'performance',
    'performance': 'performance',
    'lag': 'performance',
    'loading': 'performance',
    'feature': 'feature',
    'suggestion': 'feature',
    'request': 'feature',
    'add': 'feature',
    'windows': 'platform',
    'mac': 'platform',
    'android': 'platform',
    'ios': 'platform',
    'linux': 'platform',
    'mobile': 'platform',
    'desktop': 'platform',
    'browser': 'platform'
}

def analyze_sentiment(text: str) -> Tuple[float, str]:
    """
    Analyze the sentiment of text and return a score and label.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (sentiment_score, sentiment_label)
        Score ranges from -1 (very negative) to 1 (very positive)
        Label is one of: 'very negative', 'negative', 'neutral', 'positive', 'very positive'
    """
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    
    # Map score to label
    if sentiment_score <= -0.6:
        label = 'very negative'
    elif sentiment_score <= -0.2:
        label = 'negative'
    elif sentiment_score <= 0.2:
        label = 'neutral'
    elif sentiment_score <= 0.6:
        label = 'positive'
    else:
        label = 'very positive'
        
    return sentiment_score, label

def generate_ticket_tags(text: str, category: str) -> List[str]:
    """
    Generate relevant tags for a ticket based on its content and category.
    
    Args:
        text: The ticket content to analyze
        category: The ticket category
        
    Returns:
        List of relevant tags
    """
    # Convert to lowercase for matching
    text = text.lower()
    
    # Start with category as a tag
    tags = {category.lower()}
    
    # Add platform tags
    platforms = ['windows', 'mac', 'android', 'ios', 'linux', 'mobile', 'desktop', 'browser']
    for platform in platforms:
        if platform in text:
            tags.add(platform)
    
    # Add tags based on technical keywords
    for keyword, tag_category in TECH_KEYWORDS.items():
        if keyword in text:
            tags.add(tag_category)
    
    # Add severity tag if found
    if any(word in text for word in ['urgent', 'critical', 'emergency', 'asap']):
        tags.add('high-priority')
    elif any(word in text for word in ['minor', 'small', 'trivial']):
        tags.add('low-priority')
    
    return sorted(list(tags))

def summarize_ticket(messages: List[Dict[str, Any]], max_sentences: int = 3) -> str:
    """
    Generate a concise summary of a ticket conversation.
    
    Args:
        messages: List of message dictionaries with 'content' and 'author' keys
        max_sentences: Maximum number of sentences in the summary
        
    Returns:
        A string summary of the conversation
    """
    # Combine all messages into one text
    full_text = ' '.join(msg['content'] for msg in messages)
    
    # Tokenize into sentences
    sentences = sent_tokenize(full_text)
    
    if not sentences:
        return "No content to summarize."
    
    # If we have fewer sentences than max_sentences, return all of them
    if len(sentences) <= max_sentences:
        return ' '.join(sentences)
    
    # Calculate sentence scores based on word frequency
    stop_words = set(stopwords.words('english'))
    word_freq = Counter()
    
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        word_freq.update(words)
    
    # Score sentences based on word frequency
    sentence_scores = []
    for sentence in sentences:
        score = 0
        words = word_tokenize(sentence.lower())
        words = [word for word in words if word.isalnum()]
        for word in words:
            score += word_freq[word]
        sentence_scores.append((score, sentence))
    
    # Get top sentences
    top_sentences = sorted(sentence_scores, reverse=True)[:max_sentences]
    
    # Sort sentences by their original order
    summary_sentences = []
    for sentence in sentences:
        if any(sentence == s[1] for s in top_sentences):
            summary_sentences.append(sentence)
        if len(summary_sentences) == max_sentences:
            break
    
    return ' '.join(summary_sentences)

def suggest_macro_response(
    ticket_content: str,
    available_macros: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Suggest the most relevant macro response for a ticket.
    
    Args:
        ticket_content: The ticket message content
        available_macros: List of macro dictionaries with 'name' and 'content' keys
        
    Returns:
        The ID of the most relevant macro, or None if no good match
    """
    if not available_macros:
        return None
    
    # Convert ticket content to lowercase for matching
    ticket_content = ticket_content.lower()
    
    # Calculate relevance scores for each macro
    macro_scores = []
    for macro in available_macros:
        score = 0
        macro_content = macro['content'].lower()
        
        # Check for keyword matches
        keywords = set(word_tokenize(macro_content)) - set(stopwords.words('english'))
        for keyword in keywords:
            if keyword in ticket_content:
                score += 1
        
        # Boost score for category matches
        if macro.get('category', '').lower() in ticket_content:
            score += 2
            
        macro_scores.append((score, macro['macro_id']))
    
    # Get the highest scoring macro
    macro_scores.sort(reverse=True)
    
    # Only suggest if we have a reasonable match
    if macro_scores and macro_scores[0][0] >= 2:
        return macro_scores[0][1]
    
    return None

def extract_key_details(text: str) -> Dict[str, str]:
    """
    Extract key details from ticket content like error codes, versions, etc.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary of extracted details
    """
    details = {}
    
    # Extract error codes (common formats)
    error_codes = re.findall(r'(?:error|code)[\s:]*([\w-]+)', text, re.I)
    if error_codes:
        details['error_codes'] = error_codes
    
    # Extract versions (common formats)
    versions = re.findall(r'v?(\d+\.\d+(?:\.\d+)?(?:-\w+)?)', text)
    if versions:
        details['versions'] = versions
    
    # Extract URLs
    urls = re.findall(r'https?://\S+', text)
    if urls:
        details['urls'] = urls
    
    # Extract email addresses
    emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    if emails:
        details['emails'] = emails
    
    # Extract IDs (common formats)
    ids = re.findall(r'(?:id|user|account)[\s:]*([\w-]{4,})', text, re.I)
    if ids:
        details['ids'] = ids
    
    return details

def analyze_common_issues(ticket_content: str) -> Dict[str, float]:
    """
    Analyze ticket content to identify common issues and their confidence scores.
    
    Args:
        ticket_content: The content of the ticket to analyze
        
    Returns:
        Dict mapping issue types to confidence scores (0-1)
    """
    # Common issue patterns and their regular expressions
    ISSUE_PATTERNS = {
        'login_problem': r'(?i)(can\'?t\s+log\s*in|login\s+(?:failed|error|problem)|password\s+(?:reset|problem|incorrect))',
        'connection_issue': r'(?i)(can\'?t\s+connect|connection\s+(?:failed|lost|problem)|disconnected|timeout)',
        'performance_problem': r'(?i)(slow|lag(?:ging)?|freeze|stuck|crash|performance\s+(?:issue|problem))',
        'error_message': r'(?i)(error\s+(?:message|code)|exception|failed\s+to|unable\s+to)',
        'feature_request': r'(?i)((?:new\s+)?feature\s+request|suggestion|would\s+(?:like|be\s+nice)\s+(?:to\s+have|if))',
        'bug_report': r'(?i)(bug|not\s+working|broken|incorrect\s+(?:behavior|behaviour)|unexpected)',
        'account_issue': r'(?i)(account\s+(?:problem|locked|suspended|banned)|can\'?t\s+access\s+(?:my\s+)?account)',
        'billing_problem': r'(?i)(payment|charge|refund|subscription|billing|invoice)',
        'data_loss': r'(?i)(lost\s+(?:data|progress|files)|missing\s+(?:data|files)|deleted|corrupted)',
        'update_problem': r'(?i)(update|upgrade|installation|version|patch)\s+(?:failed|error|problem|issue)'
    }
    
    # Initialize results
    results = {}
    
    # Calculate confidence scores based on pattern matches
    for issue_type, pattern in ISSUE_PATTERNS.items():
        matches = re.finditer(pattern, ticket_content)
        match_count = sum(1 for _ in matches)
        
        # Calculate confidence score (0-1)
        # More matches = higher confidence, but with diminishing returns
        confidence = 1 - (1 / (match_count + 1)) if match_count > 0 else 0
        
        if confidence > 0:
            results[issue_type] = round(confidence, 2)
    
    return results

def extract_key_information(ticket_content: str) -> Dict[str, str]:
    """
    Extract key information from ticket content.
    
    Args:
        ticket_content: The content of the ticket to analyze
        
    Returns:
        Dict containing extracted information
    """
    info = {
        'platform': None,
        'version': None,
        'error_code': None,
        'timestamp': None,
        'user_id': None
    }
    
    # Platform detection
    platform_patterns = {
        'windows': r'(?i)windows\s+(?:\d+|xp|vista|[78]|10|11)',
        'mac': r'(?i)mac\s*os|macos|osx',
        'linux': r'(?i)linux|ubuntu|debian|fedora|centos',
        'ios': r'(?i)ios\s+\d+|iphone|ipad',
        'android': r'(?i)android\s+\d+|android'
    }
    
    for platform, pattern in platform_patterns.items():
        if re.search(pattern, ticket_content):
            info['platform'] = platform
            break
    
    # Version number
    version_match = re.search(r'(?i)v?ersion\s*[:\s]\s*(\d+(?:\.\d+)*)', ticket_content)
    if version_match:
        info['version'] = version_match.group(1)
    
    # Error code
    error_match = re.search(r'(?i)error(?:\s+code)?[:\s]\s*([A-Z0-9-_]+)', ticket_content)
    if error_match:
        info['error_code'] = error_match.group(1)
    
    # Timestamp
    timestamp_match = re.search(r'(?i)(?:at|on)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)', ticket_content)
    if timestamp_match:
        info['timestamp'] = timestamp_match.group(1)
    
    # User ID
    user_id_match = re.search(r'(?i)(?:user|id)[:\s]\s*(\d{5,})', ticket_content)
    if user_id_match:
        info['user_id'] = user_id_match.group(1)
    
    return {k: v for k, v in info.items() if v is not None}

def generate_suggested_response(
    ticket_content: str,
    issue_analysis: Dict[str, float],
    key_info: Dict[str, str]
) -> Optional[str]:
    """
    Generate a suggested response based on ticket analysis.
    
    Args:
        ticket_content: The original ticket content
        issue_analysis: Results from analyze_common_issues
        key_info: Results from extract_key_information
        
    Returns:
        A suggested response or None if no good suggestion can be made
    """
    # Sort issues by confidence
    top_issues = sorted(issue_analysis.items(), key=lambda x: x[1], reverse=True)
    
    if not top_issues:
        return None
    
    # Get the most likely issue
    main_issue, confidence = top_issues[0]
    
    # Only suggest if we're reasonably confident
    if confidence < 0.5:
        return None
    
    # Template responses for common issues
    RESPONSE_TEMPLATES = {
        'login_problem': (
            "I understand you're having trouble logging in. Let's help you resolve this:\n\n"
            "1. First, please try clearing your browser cache and cookies\n"
            "2. Make sure caps lock is off when entering your password\n"
            "3. If you're still unable to log in, you can reset your password using the 'Forgot Password' link\n\n"
            "Let me know if you need help with any of these steps!"
        ),
        'connection_issue': (
            "I see you're experiencing connection issues. Let's try these steps:\n\n"
            "1. Check if you can access other websites/services\n"
            "2. Try restarting your router\n"
            "3. Clear your browser cache\n"
            "4. If possible, try connecting using a different network\n\n"
            "Which of these would you like me to guide you through?"
        ),
        'performance_problem': (
            "I understand you're experiencing performance issues. Let's improve this:\n\n"
            "1. Check your current system resources (CPU, Memory usage)\n"
            "2. Close any unnecessary background applications\n"
            "3. Clear temporary files and cache\n"
            "4. Make sure your system meets the minimum requirements\n\n"
            "Would you like me to help you check any of these?"
        ),
        'error_message': (
            "I see you've encountered an error. To help you better:\n\n"
            "1. Could you please provide a screenshot of the error?\n"
            "2. What were you doing when the error occurred?\n"
            "3. Has this happened before?\n\n"
            "This information will help us resolve the issue faster."
        ),
        'feature_request': (
            "Thank you for your feature suggestion! To help us evaluate it:\n\n"
            "1. Could you describe the specific use case for this feature?\n"
            "2. How would this feature benefit other users?\n"
            "3. Are there any existing workarounds you're currently using?\n\n"
            "Your input helps us improve our service!"
        ),
        'bug_report': (
            "Thank you for reporting this issue. To help us investigate:\n\n"
            "1. Could you provide steps to reproduce the problem?\n"
            "2. What is the expected behavior?\n"
            "3. What is the actual behavior you're seeing?\n"
            "4. Are there any error messages?\n\n"
            "This information will help us fix the issue more quickly."
        ),
        'account_issue': (
            "I understand you're having account-related issues. Let's help you:\n\n"
            "1. When did you first notice this problem?\n"
            "2. Have you received any error messages?\n"
            "3. Have you made any recent changes to your account?\n\n"
            "Please provide any additional details that might help us investigate."
        ),
        'billing_problem': (
            "I understand you're having billing-related concerns. Let me help:\n\n"
            "1. Could you specify the transaction date?\n"
            "2. Please check if the charge appears on your bank statement\n"
            "3. Have you received any confirmation emails?\n\n"
            "For security, please do not share full payment details in the ticket."
        ),
        'data_loss': (
            "I understand you're experiencing data loss. Let's try to recover it:\n\n"
            "1. When did you last see the data?\n"
            "2. Have you checked the trash/recycle bin?\n"
            "3. Do you have any recent backups?\n"
            "4. Have you made any changes before the data disappeared?\n\n"
            "Please provide as much detail as possible to help us investigate."
        ),
        'update_problem': (
            "I see you're having trouble with updates. Let's resolve this:\n\n"
            "1. What version are you currently running?\n"
            "2. Are you getting any specific error messages?\n"
            "3. Have you tried restarting after the update?\n"
            "4. Do you have enough disk space?\n\n"
            "Let me know and I'll guide you through the resolution."
        )
    }
    
    # Get the base template
    response = RESPONSE_TEMPLATES.get(main_issue)
    if not response:
        return None
    
    # Customize with extracted information
    if key_info:
        response += "\n\nI can see that:"
        if key_info.get('platform'):
            response += f"\n- You're using {key_info['platform'].title()}"
        if key_info.get('version'):
            response += f"\n- You're on version {key_info['version']}"
        if key_info.get('error_code'):
            response += f"\n- You're getting error code {key_info['error_code']}"
    
    return response

def analyze_sentiment(ticket_content: str) -> Tuple[str, float]:
    """
    Analyze the sentiment of ticket content.
    
    Args:
        ticket_content: The content to analyze
        
    Returns:
        Tuple of (sentiment, confidence) where sentiment is one of:
        'positive', 'negative', 'neutral'
    """
    # Sentiment word lists
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'helpful', 'perfect', 'thanks', 'thank', 'appreciate', 'pleased',
        'happy', 'love', 'awesome', 'best', 'satisfied', 'glad'
    }
    
    NEGATIVE_WORDS = {
        'bad', 'poor', 'terrible', 'horrible', 'awful', 'worst',
        'unhappy', 'disappointed', 'frustrating', 'useless', 'waste',
        'annoying', 'hate', 'problem', 'issue', 'error', 'bug', 'crash'
    }
    
    # Convert to lowercase and split into words
    words = re.findall(r'\w+', ticket_content.lower())
    
    # Count sentiment words
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    total_count = positive_count + negative_count
    
    if total_count == 0:
        return ('neutral', 0.5)
    
    # Calculate ratios
    positive_ratio = positive_count / total_count
    negative_ratio = negative_count / total_count
    
    # Determine sentiment
    if positive_ratio > negative_ratio:
        return ('positive', positive_ratio)
    elif negative_ratio > positive_ratio:
        return ('negative', negative_ratio)
    else:
        return ('neutral', 0.5)

def categorize_priority(
    ticket_content: str,
    sentiment: Tuple[str, float]
) -> Tuple[str, float]:
    """
    Categorize ticket priority based on content and sentiment.
    
    Args:
        ticket_content: The ticket content
        sentiment: Result from analyze_sentiment
        
    Returns:
        Tuple of (priority, confidence) where priority is one of:
        'low', 'medium', 'high', 'urgent'
    """
    # Priority indicators
    URGENT_PATTERNS = {
        r'(?i)urgent',
        r'(?i)emergency',
        r'(?i)critical',
        r'(?i)immediate',
        r'(?i)asap',
        r'(?i)production.*down',
        r'(?i)security.*breach',
        r'(?i)data.*breach'
    }
    
    HIGH_PATTERNS = {
        r'(?i)important',
        r'(?i)serious',
        r'(?i)significant',
        r'(?i)major',
        r'(?i)production.*issue',
        r'(?i)customer.*impact'
    }
    
    MEDIUM_PATTERNS = {
        r'(?i)moderate',
        r'(?i)minor',
        r'(?i)regular',
        r'(?i)normal',
        r'(?i)standard'
    }
    
    # Check for urgent patterns
    urgent_matches = sum(1 for pattern in URGENT_PATTERNS if re.search(pattern, ticket_content))
    high_matches = sum(1 for pattern in HIGH_PATTERNS if re.search(pattern, ticket_content))
    medium_matches = sum(1 for pattern in MEDIUM_PATTERNS if re.search(pattern, ticket_content))
    
    # Factor in sentiment
    sentiment_type, sentiment_conf = sentiment
    sentiment_factor = {
        'negative': 0.3,
        'neutral': 0.1,
        'positive': -0.1
    }.get(sentiment_type, 0)
    
    # Calculate priority scores
    urgent_score = (urgent_matches * 0.4) + sentiment_factor
    high_score = (high_matches * 0.3) + sentiment_factor
    medium_score = (medium_matches * 0.2) + sentiment_factor
    
    # Determine priority
    scores = {
        'urgent': urgent_score,
        'high': high_score,
        'medium': medium_score,
        'low': 0.1  # Base score for low priority
    }
    
    priority = max(scores.items(), key=lambda x: x[1])
    confidence = min(priority[1], 1.0)  # Cap confidence at 1.0
    
    return (priority[0], confidence) 