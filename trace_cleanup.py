#!/usr/bin/env python3
"""
Trace cleanup utility for the Client Health Chatbot
This script helps manage and clean up old trace files based on configuration settings.
"""

import os
import json
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import config
from trace import ConversationTracer

def cleanup_old_traces(max_age_days: int = None, dry_run: bool = False) -> Dict[str, int]:
    """Clean up traces older than specified days"""
    if max_age_days is None:
        max_age_days = config.TRACE_SETTINGS.get("max_trace_age_days", 30)
    
    tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"])
    sessions = tracer.list_all_sessions()
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    
    deleted_count = 0
    kept_count = 0
    error_count = 0
    
    print(f"Cleaning up traces older than {max_age_days} days...")
    print(f"Cutoff date: {cutoff_date.isoformat()}")
    print(f"{'DRY RUN - ' if dry_run else ''}Found {len(sessions)} total sessions")
    print("-" * 60)
    
    for session in sessions:
        try:
            session_date = datetime.fromisoformat(session["start_time"].replace('Z', '+00:00'))
            
            if session_date < cutoff_date:
                print(f"{'[DRY RUN] Would delete' if dry_run else 'Deleting'}: {session['session_id'][:8]} ({session_date.strftime('%Y-%m-%d %H:%M')})")
                
                if not dry_run:
                    if tracer.delete_trace(session["session_id"]):
                        deleted_count += 1
                    else:
                        error_count += 1
                        print(f"  ERROR: Failed to delete {session['session_id'][:8]}")
                else:
                    deleted_count += 1
            else:
                kept_count += 1
                
        except Exception as e:
            error_count += 1
            print(f"ERROR processing session {session.get('session_id', 'unknown')[:8]}: {e}")
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Sessions {'that would be ' if dry_run else ''}deleted: {deleted_count}")
    print(f"  Sessions kept: {kept_count}")
    print(f"  Errors: {error_count}")
    
    return {
        "deleted": deleted_count,
        "kept": kept_count,
        "errors": error_count
    }

def get_trace_statistics() -> Dict:
    """Get comprehensive statistics about traces"""
    tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"])
    sessions = tracer.list_all_sessions()
    
    if not sessions:
        return {"total_sessions": 0}
    
    total_events = 0
    total_requests = 0
    total_responses = 0
    total_errors = 0
    oldest_session = None
    newest_session = None
    
    companies_analyzed = set()
    categories_assigned = []
    
    for session in sessions:
        session_date = datetime.fromisoformat(session["start_time"].replace('Z', '+00:00'))
        
        if oldest_session is None or session_date < oldest_session:
            oldest_session = session_date
        if newest_session is None or session_date > newest_session:
            newest_session = session_date
        
        total_events += session["event_count"]
        
        # Load full trace for detailed stats
        trace = tracer.load_trace(session["session_id"])
        if trace:
            for event in trace.events:
                if event.event_type == "user_request":
                    total_requests += 1
                    company = event.content.get("company_name")
                    if company:
                        companies_analyzed.add(company)
                elif event.event_type == "bot_response":
                    total_responses += 1
                    evaluation = event.content.get("evaluation", {})
                    category = evaluation.get("category")
                    if category:
                        categories_assigned.append(category)
                elif event.event_type == "error":
                    total_errors += 1
    
    # Calculate category distribution
    category_distribution = {}
    for category in categories_assigned:
        category_distribution[category] = category_distribution.get(category, 0) + 1
    
    return {
        "total_sessions": len(sessions),
        "total_events": total_events,
        "total_requests": total_requests,
        "total_responses": total_responses,
        "total_errors": total_errors,
        "unique_companies": len(companies_analyzed),
        "companies_analyzed": list(companies_analyzed),
        "category_distribution": category_distribution,
        "oldest_session": oldest_session.isoformat() if oldest_session else None,
        "newest_session": newest_session.isoformat() if newest_session else None,
        "date_range_days": (newest_session - oldest_session).days if oldest_session and newest_session else 0
    }

def export_all_traces(output_file: str = None) -> str:
    """Export all traces to a single JSON file"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"all_traces_{timestamp}.json"
    
    tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"])
    sessions = tracer.list_all_sessions()
    
    all_traces = []
    for session in sessions:
        trace = tracer.load_trace(session["session_id"])
        if trace:
            all_traces.append({
                "session_id": trace.session_id,
                "start_time": trace.start_time,
                "end_time": trace.end_time,
                "events": [
                    {
                        "event_id": event.event_id,
                        "timestamp": event.timestamp,
                        "event_type": event.event_type,
                        "content": event.content,
                        "metadata": event.metadata
                    }
                    for event in trace.events
                ],
                "summary": trace.summary
            })
    
    export_data = {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_sessions": len(all_traces),
        "traces": all_traces
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"Exported {len(all_traces)} traces to {output_file}")
    return output_file

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Manage conversation traces for the Client Health Chatbot")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old trace files")
    cleanup_parser.add_argument("--days", type=int, default=None, 
                              help="Maximum age of traces to keep (default from config)")
    cleanup_parser.add_argument("--dry-run", action="store_true", 
                              help="Show what would be deleted without actually deleting")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show trace statistics")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export all traces")
    export_parser.add_argument("--output", type=str, default=None,
                             help="Output file name (default: auto-generated)")
    
    args = parser.parse_args()
    
    if args.command == "cleanup":
        cleanup_old_traces(max_age_days=args.days, dry_run=args.dry_run)
    
    elif args.command == "stats":
        stats = get_trace_statistics()
        print("Trace Statistics")
        print("=" * 50)
        
        for key, value in stats.items():
            if key == "companies_analyzed" and len(value) > 10:
                print(f"{key}: {len(value)} companies (showing first 10: {', '.join(value[:10])}...)")
            elif key == "category_distribution":
                print(f"{key}:")
                for cat, count in value.items():
                    print(f"  {cat}: {count}")
            else:
                print(f"{key}: {value}")
    
    elif args.command == "export":
        export_all_traces(args.output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
