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

### Prioritize by Impact, Not Preference
Use a simple score to rank optimization opportunities before implementation.

```python
# frequency: calls per request or per day
# latency_ms: current cost per call
# memory_mb: expected average memory reduction
# effort_days: estimated implementation effort
score = (frequency * latency_ms + 50 * memory_mb) / max(effort_days, 0.5)

# Higher score = higher priority
```

This helps teams avoid low-value micro-optimizations and focus on improvements that affect user-visible SLAs.

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

# line_profiler - Line-by-line profiling (optional, developer-only; not required to run the analyzer)
# Optional install for developers: pip install line-profiler
# Usage: @profile decorator and run with kernprof
@profile
def slow_function():
    # Your code
    pass

# memory_profiler - Memory usage (optional, developer-only; not required to run the analyzer)
# Optional install for developers: pip install memory-profiler
from memory_profiler import profile

@profile
def memory_heavy_function():
    # Your code
    pass
```

#### Simple Timing
```python
import time

start = time.perf_counter()
# Code to measure
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed * 1000:.2f}ms")
```

---

## Algorithm Optimization

### Time Complexity
Choose algorithms with lower big-O complexity for frequently called code paths.

```python
# ❌ O(n) membership test on a list
items_list = [1, 2, 3, ...]
if target in items_list:  # Scans entire list
    pass

# ✅ O(1) membership test on a set
items_set = {1, 2, 3, ...}
if target in items_set:
    pass

# ❌ O(n²) nested loop
for a in items:
    for b in items:
        if a == b:
            process(a, b)

# ✅ O(n) with a set/dict
seen = set()
for a in items:
    if a in seen:
        process(a, a)
    seen.add(a)
```

### Caching / Memoization
```python
from functools import lru_cache

# ✅ Cache results of expensive pure functions
@lru_cache(maxsize=512)
def expensive_computation(n: int) -> int:
    return sum(i * i for i in range(n))
```

---

## Python-Specific Optimizations

### String Building
```python
# ❌ Quadratic string concatenation
result = ""
for item in items:
    result += str(item)

# ✅ Linear join
result = "".join(str(item) for item in items)
```

### Generators vs. Lists
```python
# ❌ Materialize entire list just to sum it
values = [expensive_func(x) for x in huge_list]
total = sum(values)

# ✅ Stream through generator — O(1) memory
total = sum(expensive_func(x) for x in huge_list)
```

### Direct Iteration
```python
# ❌ Index-based loop when index is not needed
for i in range(len(items)):
    process(items[i])

# ✅ Direct iteration (clearer and often faster)
for item in items:
    process(item)

# ✅ Use enumerate when the index is needed
for i, item in enumerate(items):
    process_with_index(i, item)
```

### Local Variable Caching in Hot Loops
```python
# ❌ Module attribute looked up on every iteration
for i in range(n):
    result = math.sqrt(i)

# ✅ Cache the reference before the loop
sqrt = math.sqrt
for i in range(n):
    result = sqrt(i)
```

---

## ML/AI Performance Optimization

### Batch Predictions
```python
# ❌ One prediction per sample
predictions = []
for sample in dataset:
    pred = model.predict([sample])
    predictions.append(pred)

# ✅ Batched prediction
predictions = model.predict(dataset)
```

### Lazy / Streaming Data Loading
```python
# ❌ Load entire dataset into memory
data = [load(path) for path in file_paths]

# ✅ Use a generator to stream files
def data_generator(file_paths):
    for path in file_paths:
        yield load(path)
```

---

## Database & I/O Optimization

### Batch DB Operations
```python
# ❌ One INSERT per row
for record in records:
    cursor.execute("INSERT INTO t VALUES (?)", record)

# ✅ Single bulk INSERT
cursor.executemany("INSERT INTO t VALUES (?)", records)
```

### Connection Pooling
Reuse database connections instead of opening a new connection for each query.

---

## Memory Management

### Avoid Unnecessary Copies
```python
# ❌ Full copy just for read access
data_copy = data[:]
process(data_copy)

# ✅ Pass the original if mutation is not needed
process(data)
```

### Use `__slots__` for Memory-Tight Classes
```python
class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

---

## Concurrency & Parallelism

### CPU-Bound vs. I/O-Bound
- **CPU-bound**: use `multiprocessing.ProcessPoolExecutor` (bypasses the GIL).
- **I/O-bound**: use `concurrent.futures.ThreadPoolExecutor` or `asyncio`.

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# ✅ CPU-bound parallelism
with ProcessPoolExecutor() as pool:
    results = list(pool.map(cpu_task, data))

# ✅ I/O-bound concurrency
with ThreadPoolExecutor() as pool:
    results = list(pool.map(fetch_url, urls))
```

---

## NLP & Document Processing

### Pre-Compile Regex Patterns
```python
# ❌ Dynamic compilation inside a loop
for text in texts:
    pattern = re.compile(build_pattern(config))
    matches = pattern.findall(text)

# ✅ Compile once, reuse many times
pattern = re.compile(build_pattern(config))
for text in texts:
    matches = pattern.findall(text)
```

### Avoid Redundant String Lowercasing
When multiple methods need a case-insensitive view of the same text, compute
`.lower()` once and pass the result rather than recomputing it in each method.

```python
# ❌ Two O(n) lowercase operations on the same string
def analyze(self, text):
    techs = self.detect_technologies(text)   # calls text.lower() internally
    gcp   = self.extract_gcp_info(text)      # calls text.lower() internally again

# ✅ Compute once and share
def analyze(self, text):
    text_lower = text.lower()                # single O(n) operation
    techs = self.detect_technologies(text, text_lower)
    gcp   = self.extract_gcp_info(text, text_lower)
```

### Batch NLP Processing
```python
# ❌ Process documents one by one
docs = [nlp(text) for text in texts]

# ✅ Use the pipeline's built-in batching
docs = list(nlp.pipe(texts, batch_size=64))
```

### Batch Embeddings
```python
# ❌ Encode one document at a time
embeddings = [model.encode(doc) for doc in docs]

# ✅ Encode all at once
embeddings = model.encode(docs)
```

 
