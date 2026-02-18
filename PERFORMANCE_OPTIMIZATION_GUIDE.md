diff --git a/PERFORMANCE_OPTIMIZATION_GUIDE.md b/PERFORMANCE_OPTIMIZATION_GUIDE.md
index a9a521f1bb8dffa6209b198e4bdd63ce7f81e3f8..d279df1337a04aef9c4c7a2591aa3d12ddaedda1 100644
--- a/PERFORMANCE_OPTIMIZATION_GUIDE.md
+++ b/PERFORMANCE_OPTIMIZATION_GUIDE.md
@@ -1,46 +1,61 @@
 # Code Performance Optimization Guide
 
 A comprehensive guide for identifying and improving slow or inefficient code, with focus on AI/ML, NLP, and document intelligence systems.
 
 ## Table of Contents
 1. [Performance Profiling](#performance-profiling)
 2. [Algorithm Optimization](#algorithm-optimization)
 3. [Python-Specific Optimizations](#python-specific-optimizations)
 4. [ML/AI Performance Optimization](#mlai-performance-optimization)
 5. [Database & I/O Optimization](#database--io-optimization)
 6. [Memory Management](#memory-management)
 7. [Concurrency & Parallelism](#concurrency--parallelism)
 8. [NLP & Document Processing](#nlp--document-processing)
 
 ---
 
 ## Performance Profiling
 
 ### Identify Bottlenecks First
 Before optimizing, always measure and identify actual bottlenecks.
 
+### Prioritize by Impact, Not Preference
+Use a simple score to rank optimization opportunities before implementation.
+
+```python
+# frequency: calls per request or per day
+# latency_ms: current cost per call
+# memory_mb: expected average memory reduction
+# effort_days: estimated implementation effort
+score = (frequency * latency_ms + 50 * memory_mb) / max(effort_days, 0.5)
+
+# Higher score = higher priority
+```
+
+This helps teams avoid low-value micro-optimizations and focus on improvements that affect user-visible SLAs.
+
 #### Python Profiling Tools
 ```python
 # cProfile - Standard profiler
 import cProfile
 import pstats
 
 profiler = cProfile.Profile()
 profiler.enable()
 # Your code here
 profiler.disable()
 stats = pstats.Stats(profiler)
 stats.sort_stats('cumulative')
 stats.print_stats(20)  # Top 20 slowest functions
 
 # line_profiler - Line-by-line profiling
 # Install: pip install line-profiler
 # Usage: @profile decorator and run with kernprof
 @profile
 def slow_function():
     # Your code
     pass
 
 # memory_profiler - Memory usage
 from memory_profiler import profile
 
