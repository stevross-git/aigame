import time
import threading
from collections import defaultdict
from typing import Dict, List

class PerformanceProfiler:
    """
    Detailed performance profiler to identify bottlenecks
    """
    
    def __init__(self):
        self.enabled = False  # PERFORMANCE FIX: Disable profiler completely
        self.timings = defaultdict(list)
        self.current_timers = {}
        self.frame_count = 0
        self.total_frame_time = 0
        self.log_interval = 30  # Log every 30 frames for faster feedback
        self.max_history = 1000
        
    def start_timer(self, name: str):
        """Start timing a specific operation"""
        if not self.enabled:
            return
        self.current_timers[name] = time.perf_counter()
    
    def end_timer(self, name: str):
        """End timing and record the duration"""
        if not self.enabled or name not in self.current_timers:
            return
        
        duration = time.perf_counter() - self.current_timers[name]
        self.timings[name].append(duration * 1000)  # Convert to milliseconds
        
        # Keep only recent history
        if len(self.timings[name]) > self.max_history:
            self.timings[name] = self.timings[name][-self.max_history:]
        
        del self.current_timers[name]
    
    def time_operation(self, name: str):
        """Context manager for timing operations"""
        return TimingContext(self, name)
    
    def log_frame_complete(self, frame_time: float):
        """Log completion of a frame"""
        if not self.enabled:
            return
            
        self.frame_count += 1
        self.total_frame_time += frame_time
        
        if self.frame_count % self.log_interval == 0:
            self._print_performance_report()
    
    def _print_performance_report(self):
        """Print detailed performance report"""
        if not self.timings:
            return
        
        # Also write to file for easier debugging
        log_content = []
        log_content.append("\n" + "="*80)
        log_content.append(f"🔍 PERFORMANCE REPORT - Frame {self.frame_count}")
        log_content.append("="*80)
            
        print("\n" + "="*80)
        print(f"🔍 PERFORMANCE REPORT - Frame {self.frame_count}")
        print("="*80)
        
        # Calculate average FPS
        avg_frame_time = self.total_frame_time / self.frame_count
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        fps_line = f"📊 Average FPS: {avg_fps:.1f} (Avg Frame Time: {avg_frame_time*1000:.1f}ms)"
        print(fps_line)
        log_content.append(fps_line)
        
        # Sort timings by average duration (worst first)
        sorted_timings = []
        for name, times in self.timings.items():
            if times:
                avg_time = sum(times[-self.log_interval:]) / len(times[-self.log_interval:])
                max_time = max(times[-self.log_interval:])
                min_time = min(times[-self.log_interval:])
                sorted_timings.append((name, avg_time, max_time, min_time, len(times[-self.log_interval:])))
        
        sorted_timings.sort(key=lambda x: x[1], reverse=True)
        
        slowest_header = f"\n🐌 SLOWEST OPERATIONS (Last {self.log_interval} frames):"
        print(slowest_header)
        log_content.append(slowest_header)
        
        divider = "-" * 80
        print(divider)
        log_content.append(divider)
        
        table_header = f"{'Operation':<30} {'Avg (ms)':<10} {'Max (ms)':<10} {'Min (ms)':<10} {'Count':<8}"
        print(table_header)
        log_content.append(table_header)
        
        print(divider)
        log_content.append(divider)
        
        for name, avg_time, max_time, min_time, count in sorted_timings[:15]:  # Top 15 slowest
            table_row = f"{name:<30} {avg_time:>8.2f} {max_time:>8.2f} {min_time:>8.2f} {count:>6}"
            print(table_row)
            log_content.append(table_row)
        
        # Identify potential issues
        issues_header = "\n⚠️  POTENTIAL ISSUES:"
        print(issues_header)
        log_content.append(issues_header)
        
        issues_divider = "-" * 40
        print(issues_divider)
        log_content.append(issues_divider)
        
        for name, avg_time, max_time, min_time, count in sorted_timings:
            if avg_time > 5.0:  # More than 5ms average
                issue_line = f"❌ {name}: {avg_time:.1f}ms avg (VERY SLOW)"
                print(issue_line)
                log_content.append(issue_line)
            elif avg_time > 2.0:  # More than 2ms average
                issue_line = f"⚠️  {name}: {avg_time:.1f}ms avg (SLOW)"
                print(issue_line)
                log_content.append(issue_line)
            elif max_time > 10.0:  # Occasional spikes
                issue_line = f"💥 {name}: {max_time:.1f}ms max spike"
                print(issue_line)
                log_content.append(issue_line)
        
        print("="*80 + "\n")
        
        # Write to file for easier debugging
        log_content.append("="*80 + "\n")
        try:
            with open("/tmp/performance_log.txt", "a") as f:
                f.write("\n".join(log_content) + "\n")
        except Exception as e:
            print(f"Failed to write performance log: {e}")
    
    def get_timing_summary(self) -> Dict:
        """Get current timing summary"""
        summary = {}
        for name, times in self.timings.items():
            if times:
                recent_times = times[-60:]  # Last 60 measurements
                summary[name] = {
                    'avg': sum(recent_times) / len(recent_times),
                    'max': max(recent_times),
                    'min': min(recent_times),
                    'count': len(recent_times)
                }
        return summary

class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, profiler: PerformanceProfiler, name: str):
        self.profiler = profiler
        self.name = name
    
    def __enter__(self):
        self.profiler.start_timer(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.end_timer(self.name)

# Global profiler instance
profiler = PerformanceProfiler()