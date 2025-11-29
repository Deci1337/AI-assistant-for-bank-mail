"""API routes for analytics and dashboard data."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from ..storage import storage

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_db():
    """Dummy dependency for compatibility."""
    return None


@router.get("/overview")
def get_overview(
    days: int = Query(7, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get overview statistics."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    threads = storage.get_threads_in_period(start_date, end_date)
    messages = storage.get_messages_in_period(start_date, end_date)
    
    # Total threads
    total_threads = len(threads)
    
    # Total messages
    total_messages = len(messages)
    
    # Incoming vs Outgoing
    incoming_count = len([m for m in messages if m["message_type"] == "incoming"])
    outgoing_count = len([m for m in messages if m["message_type"] == "outgoing"])
    
    # Threads with directives
    threads_with_directives = len([t for t in threads if t.get("extra_directives")])
    
    # Average response time in seconds
    avg_response_time_seconds = 0.0
    generation_times = [
        m["generation_time_seconds"] 
        for m in messages 
        if m["message_type"] == "outgoing" and m.get("generation_time_seconds") and m["generation_time_seconds"] > 0
    ]
    
    if generation_times:
        avg_response_time_seconds = round(sum(generation_times) / len(generation_times), 2)
    
    return {
        "period_days": days,
        "total_threads": total_threads,
        "total_messages": total_messages,
        "incoming_messages": incoming_count,
        "outgoing_messages": outgoing_count,
        "threads_with_directives": threads_with_directives,
        "avg_response_time_seconds": avg_response_time_seconds,
    }


@router.get("/messages-by-day")
def get_messages_by_day(
    days: int = Query(7, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get message count grouped by day."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    messages = storage.get_messages_in_period(start_date, end_date)
    
    # Organize by date
    by_date = {}
    for msg in messages:
        date_str = msg["created_at"].date().isoformat()
        if date_str not in by_date:
            by_date[date_str] = {"date": date_str, "incoming": 0, "outgoing": 0}
        by_date[date_str][msg["message_type"]] += 1
    
    # Sort by date
    data = sorted(by_date.values(), key=lambda x: x["date"])
    
    return {
        "data": data,
        "period_days": days
    }


@router.get("/threads-by-context")
def get_threads_by_context(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get thread count grouped by company context."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    threads = storage.get_threads_in_period(start_date, end_date)
    
    # Count by context
    by_context = {}
    threads_without_context = 0
    
    for thread in threads:
        context_id = thread.get("company_context_id")
        if context_id:
            context = storage.get_context(context_id)
            if context:
                context_name = context["name"]
                by_context[context_name] = by_context.get(context_name, 0) + 1
        else:
            threads_without_context += 1
    
    data = [{"name": name, "count": count} for name, count in by_context.items()]
    
    if threads_without_context > 0:
        data.append({"name": "Без контекста", "count": threads_without_context})
    
    return {
        "data": data,
        "period_days": days
    }


@router.get("/threads-growth")
def get_threads_growth(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get cumulative thread growth over time."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    threads = storage.get_threads_in_period(start_date, end_date)
    
    # Count by date
    by_date = {}
    for thread in threads:
        date_str = thread["created_at"].date().isoformat()
        by_date[date_str] = by_date.get(date_str, 0) + 1
    
    # Calculate cumulative
    cumulative = 0
    data = []
    for date_str in sorted(by_date.keys()):
        count = by_date[date_str]
        cumulative += count
        data.append({
            "date": date_str,
            "daily": count,
            "cumulative": cumulative
        })
    
    return {
        "data": data,
        "period_days": days
    }


@router.get("/top-threads")
def get_top_threads(
    limit: int = Query(10, description="Количество топ переписок"),
    days: int = Query(30, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get top threads by message count."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    threads = storage.get_threads_in_period(start_date, end_date)
    
    # Count messages per thread
    thread_data = []
    for thread in threads:
        messages = storage.get_thread_messages(thread["id"])
        thread_data.append({
            "id": thread["id"],
            "subject": thread["subject"],
            "message_count": len(messages),
            "created_at": thread["created_at"].isoformat(),
            "updated_at": thread["updated_at"].isoformat(),
        })
    
    # Sort by message count and limit
    data = sorted(thread_data, key=lambda x: x["message_count"], reverse=True)[:limit]
    
    return {
        "data": data,
        "limit": limit,
        "period_days": days
    }


@router.get("/directives-usage")
def get_directives_usage(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Any = None
) -> Dict:
    """Get statistics about directives usage."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    threads = storage.get_threads_in_period(start_date, end_date)
    
    total_threads = len(threads)
    threads_with_directives = len([t for t in threads if t.get("extra_directives")])
    threads_with_custom_prompt = len([t for t in threads if t.get("custom_prompt")])
    
    usage_percentage = round((threads_with_directives / total_threads * 100) if total_threads > 0 else 0, 2)
    
    return {
        "total_threads": total_threads,
        "threads_with_directives": threads_with_directives,
        "threads_with_custom_prompt": threads_with_custom_prompt,
        "directives_usage_percentage": usage_percentage,
        "period_days": days
    }

