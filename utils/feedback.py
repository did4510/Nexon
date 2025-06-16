"""
Feedback system utilities for handling ticket feedback and analytics.
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from database.models import TicketFeedback, Ticket, Guild
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

async def store_feedback(
    session: AsyncSession,
    ticket: Ticket,
    rating: int,
    comments: Optional[str] = None
) -> TicketFeedback:
    """
    Store feedback for a ticket.
    
    Args:
        session: Database session
        ticket: The ticket the feedback is for
        rating: Rating from 1-5
        comments: Optional feedback comments
        
    Returns:
        The created TicketFeedback instance
    """
    feedback = TicketFeedback(
        ticket_db_id=ticket.ticket_db_id,
        user_id=ticket.creator_id,
        rating=rating,
        comments=comments
    )
    
    session.add(feedback)
    await session.commit()
    return feedback

async def get_feedback_stats(
    session: AsyncSession,
    guild_id: str,
    days: Optional[int] = 30
) -> Dict[str, Any]:
    """
    Get feedback statistics for a guild.
    
    Args:
        session: Database session
        guild_id: The guild ID to get stats for
        days: Optional number of days to limit stats to
        
    Returns:
        Dictionary containing feedback statistics
    """
    query = session.query(TicketFeedback).join(Ticket)
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(TicketFeedback.submitted_at >= cutoff)
    
    query = query.filter(Ticket.guild_id == guild_id)
    feedbacks = await query.all()
    
    if not feedbacks:
        return {
            'total_feedback': 0,
            'average_rating': 0.0,
            'rating_distribution': {i: 0 for i in range(1, 6)},
            'feedback_rate': 0.0,
            'recent_comments': []
        }
    
    # Calculate statistics
    total = len(feedbacks)
    rating_sum = sum(f.rating for f in feedbacks)
    rating_dist = defaultdict(int)
    for f in feedbacks:
        rating_dist[f.rating] += 1
    
    # Get total tickets in period for feedback rate
    total_tickets = await session.query(func.count(Ticket.ticket_db_id))\
        .filter(Ticket.guild_id == guild_id)\
        .filter(Ticket.closed_at.isnot(None))
    if days:
        total_tickets = total_tickets.filter(Ticket.closed_at >= cutoff)
    total_tickets = await total_tickets.scalar()
    
    # Get recent comments
    recent_comments = [
        {
            'rating': f.rating,
            'comment': f.comments,
            'submitted_at': f.submitted_at
        }
        for f in sorted(
            [f for f in feedbacks if f.comments],
            key=lambda x: x.submitted_at,
            reverse=True
        )[:5]
    ]
    
    return {
        'total_feedback': total,
        'average_rating': rating_sum / total,
        'rating_distribution': dict(rating_dist),
        'feedback_rate': (total / total_tickets * 100) if total_tickets else 0,
        'recent_comments': recent_comments
    }

async def get_staff_feedback_stats(
    session: AsyncSession,
    guild_id: str,
    staff_id: str,
    days: Optional[int] = 30
) -> Dict[str, Any]:
    """
    Get feedback statistics for a specific staff member.
    
    Args:
        session: Database session
        guild_id: The guild ID
        staff_id: The staff member's ID
        days: Optional number of days to limit stats to
        
    Returns:
        Dictionary containing staff feedback statistics
    """
    query = session.query(TicketFeedback).join(Ticket)
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(TicketFeedback.submitted_at >= cutoff)
    
    query = query.filter(
        Ticket.guild_id == guild_id,
        Ticket.claimed_by_id == staff_id
    )
    
    feedbacks = await query.all()
    
    if not feedbacks:
        return {
            'total_feedback': 0,
            'average_rating': 0.0,
            'rating_distribution': {i: 0 for i in range(1, 6)},
            'feedback_rate': 0.0,
            'recent_comments': []
        }
    
    # Calculate statistics
    total = len(feedbacks)
    rating_sum = sum(f.rating for f in feedbacks)
    rating_dist = defaultdict(int)
    for f in feedbacks:
        rating_dist[f.rating] += 1
    
    # Get total tickets handled by staff member
    total_tickets = await session.query(func.count(Ticket.ticket_db_id))\
        .filter(
            Ticket.guild_id == guild_id,
            Ticket.claimed_by_id == staff_id,
            Ticket.closed_at.isnot(None)
        )
    if days:
        total_tickets = total_tickets.filter(Ticket.closed_at >= cutoff)
    total_tickets = await total_tickets.scalar()
    
    # Get recent comments
    recent_comments = [
        {
            'rating': f.rating,
            'comment': f.comments,
            'submitted_at': f.submitted_at,
            'ticket_id': f.ticket_db_id
        }
        for f in sorted(
            [f for f in feedbacks if f.comments],
            key=lambda x: x.submitted_at,
            reverse=True
        )[:5]
    ]
    
    return {
        'total_feedback': total,
        'average_rating': rating_sum / total,
        'rating_distribution': dict(rating_dist),
        'feedback_rate': (total / total_tickets * 100) if total_tickets else 0,
        'recent_comments': recent_comments
    }

async def get_category_feedback_stats(
    session: AsyncSession,
    guild_id: str,
    category_id: str,
    days: Optional[int] = 30
) -> Dict[str, Any]:
    """
    Get feedback statistics for a specific ticket category.
    
    Args:
        session: Database session
        guild_id: The guild ID
        category_id: The category ID
        days: Optional number of days to limit stats to
        
    Returns:
        Dictionary containing category feedback statistics
    """
    query = session.query(TicketFeedback).join(Ticket)
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(TicketFeedback.submitted_at >= cutoff)
    
    query = query.filter(
        Ticket.guild_id == guild_id,
        Ticket.category_db_id == category_id
    )
    
    feedbacks = await query.all()
    
    if not feedbacks:
        return {
            'total_feedback': 0,
            'average_rating': 0.0,
            'rating_distribution': {i: 0 for i in range(1, 6)},
            'feedback_rate': 0.0,
            'common_issues': []
        }
    
    # Calculate statistics
    total = len(feedbacks)
    rating_sum = sum(f.rating for f in feedbacks)
    rating_dist = defaultdict(int)
    for f in feedbacks:
        rating_dist[f.rating] += 1
    
    # Get total tickets in category
    total_tickets = await session.query(func.count(Ticket.ticket_db_id))\
        .filter(
            Ticket.guild_id == guild_id,
            Ticket.category_db_id == category_id,
            Ticket.closed_at.isnot(None)
        )
    if days:
        total_tickets = total_tickets.filter(Ticket.closed_at >= cutoff)
    total_tickets = await total_tickets.scalar()
    
    # Analyze common issues from comments
    comments = [f.comments for f in feedbacks if f.comments]
    common_issues = analyze_common_issues(comments)
    
    return {
        'total_feedback': total,
        'average_rating': rating_sum / total,
        'rating_distribution': dict(rating_dist),
        'feedback_rate': (total / total_tickets * 100) if total_tickets else 0,
        'common_issues': common_issues
    }

def analyze_common_issues(comments: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze feedback comments to identify common issues.
    
    Args:
        comments: List of feedback comments
        
    Returns:
        List of common issues with their frequency
    """
    # Simple keyword-based analysis
    issue_keywords = {
        'slow': 'Response Time',
        'wait': 'Response Time',
        'delayed': 'Response Time',
        'unclear': 'Communication',
        'confusing': 'Communication',
        'rude': 'Staff Behavior',
        'unhelpful': 'Staff Behavior',
        'resolved': 'Resolution',
        'solved': 'Resolution',
        'fixed': 'Resolution',
        'not working': 'Technical Issues',
        'error': 'Technical Issues',
        'bug': 'Technical Issues'
    }
    
    issue_counts = defaultdict(int)
    
    for comment in comments:
        comment = comment.lower()
        for keyword, category in issue_keywords.items():
            if keyword in comment:
                issue_counts[category] += 1
    
    # Convert to list and sort by frequency
    issues = [
        {'category': category, 'count': count}
        for category, count in issue_counts.items()
    ]
    return sorted(issues, key=lambda x: x['count'], reverse=True)