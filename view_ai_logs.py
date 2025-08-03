#!/usr/bin/env python3
"""
AI Interaction Log Viewer - Command line tool to analyze AI interactions
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def load_log_file(log_file: Path) -> List[Dict]:
    """Load AI interaction log file"""
    interactions = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    interactions.append(json.loads(line.strip()))
        return interactions
    except Exception as e:
        print(f"Error loading log file: {e}")
        return []

def print_interaction_summary(interactions: List[Dict]):
    """Print summary statistics"""
    if not interactions:
        print("No interactions found.")
        return
    
    total = len(interactions)
    successful = sum(1 for i in interactions if i.get('success', True))
    cached = sum(1 for i in interactions if i.get('cached', False))
    
    providers = {}
    npcs = set()
    request_types = {}
    
    total_response_time = 0
    total_prompt_chars = 0
    total_response_chars = 0
    
    for interaction in interactions:
        provider = interaction.get('provider', 'unknown')
        providers[provider] = providers.get(provider, 0) + 1
        
        npcs.add(interaction.get('npc_name', 'unknown'))
        
        req_type = interaction.get('request_type', 'unknown')
        request_types[req_type] = request_types.get(req_type, 0) + 1
        
        total_response_time += interaction.get('response_time_ms', 0)
        total_prompt_chars += interaction.get('prompt_length', 0)
        total_response_chars += interaction.get('response_length', 0)
    
    print("🤖 AI INTERACTION LOG SUMMARY")
    print("=" * 50)
    print(f"📊 Total Interactions: {total}")
    print(f"✅ Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"❌ Failed: {total-successful} ({(total-successful)/total*100:.1f}%)")
    print(f"💾 Cached: {cached} ({cached/total*100:.1f}%)")
    print(f"⚡ Avg Response Time: {total_response_time/total:.1f}ms")
    print(f"👥 NPCs: {len(npcs)} ({', '.join(sorted(npcs))})")
    print(f"📝 Total Prompt Chars: {total_prompt_chars:,}")
    print(f"📤 Total Response Chars: {total_response_chars:,}")
    
    print("\n🔧 Providers Used:")
    for provider, count in sorted(providers.items()):
        print(f"   {provider}: {count} ({count/total*100:.1f}%)")
    
    print("\n📋 Request Types:")
    for req_type, count in sorted(request_types.items()):
        print(f"   {req_type}: {count} ({count/total*100:.1f}%)")

def print_detailed_interactions(interactions: List[Dict], limit: int = 10):
    """Print detailed view of recent interactions"""
    print(f"\n🔍 DETAILED INTERACTIONS (last {limit})")
    print("=" * 80)
    
    for interaction in interactions[-limit:]:
        timestamp = interaction.get('timestamp', 'unknown')
        npc_name = interaction.get('npc_name', 'unknown')
        req_type = interaction.get('request_type', 'unknown')
        provider = interaction.get('provider', 'unknown')
        response_time = interaction.get('response_time_ms', 0)
        success = interaction.get('success', True)
        cached = interaction.get('cached', False)
        
        status = "✅" if success else "❌"
        cache_indicator = "💾" if cached else "🔄"
        
        print(f"\n{status} {cache_indicator} [{timestamp}] {npc_name}")
        print(f"   Type: {req_type} | Provider: {provider} | Time: {response_time}ms")
        
        # Show prompt preview
        prompt = interaction.get('prompt', '')
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
        print(f"   Prompt: {prompt_preview}")
        
        # Show response
        response_parsed = interaction.get('response_parsed', {})
        if 'action' in response_parsed:
            action = response_parsed.get('action', 'unknown')
            dialogue = response_parsed.get('dialogue', '')
            emotion = response_parsed.get('emotion', '')
            
            print(f"   Response: Action={action}")
            if dialogue:
                dialogue_preview = dialogue[:50] + "..." if len(dialogue) > 50 else dialogue
                print(f"            Dialogue=\"{dialogue_preview}\"")
            if emotion:
                print(f"            Emotion={emotion}")
        
        if not success:
            error = interaction.get('error_message', 'Unknown error')
            print(f"   ❌ Error: {error}")

def filter_interactions(interactions: List[Dict], 
                       npc_name: Optional[str] = None,
                       request_type: Optional[str] = None,
                       provider: Optional[str] = None,
                       success_only: bool = False) -> List[Dict]:
    """Filter interactions based on criteria"""
    filtered = interactions
    
    if npc_name:
        filtered = [i for i in filtered if i.get('npc_name', '').lower() == npc_name.lower()]
    
    if request_type:
        filtered = [i for i in filtered if i.get('request_type', '').lower() == request_type.lower()]
    
    if provider:
        filtered = [i for i in filtered if i.get('provider', '').lower() == provider.lower()]
    
    if success_only:
        filtered = [i for i in filtered if i.get('success', True)]
    
    return filtered

def export_csv(interactions: List[Dict], output_file: str):
    """Export interactions to CSV format"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'npc_name', 'request_type', 'provider', 
                     'response_time_ms', 'success', 'cached', 'prompt_length', 
                     'response_length', 'action', 'dialogue', 'emotion']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for interaction in interactions:
            response_parsed = interaction.get('response_parsed', {})
            row = {
                'timestamp': interaction.get('timestamp', ''),
                'npc_name': interaction.get('npc_name', ''),
                'request_type': interaction.get('request_type', ''),
                'provider': interaction.get('provider', ''),
                'response_time_ms': interaction.get('response_time_ms', 0),
                'success': interaction.get('success', True),
                'cached': interaction.get('cached', False),
                'prompt_length': interaction.get('prompt_length', 0),
                'response_length': interaction.get('response_length', 0),
                'action': response_parsed.get('action', ''),
                'dialogue': response_parsed.get('dialogue', ''),
                'emotion': response_parsed.get('emotion', '')
            }
            writer.writerow(row)
    
    print(f"📁 Exported {len(interactions)} interactions to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="AI Interaction Log Viewer")
    parser.add_argument('log_file', nargs='?', help='Path to AI log file (JSONL format)')
    parser.add_argument('--npc', help='Filter by NPC name')
    parser.add_argument('--type', help='Filter by request type')
    parser.add_argument('--provider', help='Filter by provider')
    parser.add_argument('--success-only', action='store_true', help='Show only successful interactions')
    parser.add_argument('--limit', type=int, default=10, help='Limit detailed view (default: 10)')
    parser.add_argument('--export-csv', help='Export to CSV file')
    parser.add_argument('--latest', action='store_true', help='Use latest log file in logs/ai_interactions/')
    
    args = parser.parse_args()
    
    # Determine log file
    if args.latest:
        log_dir = Path('logs/ai_interactions')
        if log_dir.exists():
            log_files = list(log_dir.glob('ai_session_*.jsonl'))
            if log_files:
                log_file = max(log_files, key=lambda f: f.stat().st_mtime)
                print(f"📁 Using latest log file: {log_file}")
            else:
                print("❌ No AI log files found in logs/ai_interactions/")
                sys.exit(1)
        else:
            print("❌ Log directory not found: logs/ai_interactions/")
            sys.exit(1)
    elif args.log_file:
        log_file = Path(args.log_file)
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            sys.exit(1)
    else:
        print("❌ Please specify a log file or use --latest")
        parser.print_help()
        sys.exit(1)
    
    # Load interactions
    interactions = load_log_file(log_file)
    if not interactions:
        print("❌ No valid interactions found in log file")
        sys.exit(1)
    
    # Apply filters
    original_count = len(interactions)
    interactions = filter_interactions(
        interactions, 
        npc_name=args.npc,
        request_type=args.type,
        provider=args.provider,
        success_only=args.success_only
    )
    
    if len(interactions) != original_count:
        print(f"🔍 Filtered from {original_count} to {len(interactions)} interactions")
    
    # Print summary
    print_interaction_summary(interactions)
    
    # Print detailed view
    if interactions:
        print_detailed_interactions(interactions, args.limit)
    
    # Export if requested
    if args.export_csv:
        export_csv(interactions, args.export_csv)

if __name__ == '__main__':
    main()