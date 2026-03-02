# Code Performance Checklist

A quick-reference checklist for identifying and fixing performance issues in
Python-based AI/ML and NLP applications.

## How to Use
1. Work through each section systematically.
2. For each item, check whether it applies to your code.
3. Fix issues and re-check before marking as complete.
4. Focus on high-impact changes first (see the triage score below).

## Triage Score
Rank optimization candidates before you start:
```python
# frequency: calls per request or per day
# latency_ms: current cost per call
# memory_mb: expected average memory reduction
# effort_days: estimated implementation effort
score = (frequency * latency_ms + 50 * memory_mb) / max(effort_days, 0.5)
# Higher score = higher priority
```

## Stop Optimization Criteria
Stop further optimization if **all** of the following are true:
1. p95 latency improvement would be < 5 %
2. Memory reduction < 10 MB steady-state
3. Complexity would significantly increase
4. No user-visible SLA improvement expected

Use this checklist when reviewing code for performance issues.

---

## 🎯 Algorithm & Data Structures

### Time Complexity
- [ ] Are nested loops necessary? (Potential O(n²) or worse)
- [ ] Can hash tables/sets replace linear searches? (O(n) → O(1))
- [ ] Are there redundant computations that could be cached?
- [ ] Is the algorithm the most efficient for the use case?

### Data Structure Selection
- [ ] Lists used for membership testing? (Consider sets/dicts)
- [ ] Frequent insertions/deletions at start? (Consider deque)
- [ ] Need sorted data with fast insertion? (Consider heapq or SortedDict)
- [ ] Key-value pairs with ordering? (Consider OrderedDict)

---

## 🐍 Python-Specific Issues

### Common Anti-patterns
- [ ] String concatenation in loops? (Use `''.join()`)
- [ ] List creation when generator would work? (Memory efficiency)
- [ ] Regular loops instead of list comprehensions?
- [ ] Global variable lookups in hot loops? (Cache as local)
- [ ] Function calls in loop conditions? (Evaluate once before loop)
- [ ] Index-based loops where direct iteration (`for x in items`) would be simpler/faster?

### Built-in Usage
- [ ] Manual implementations instead of built-ins? (sum, min, max, any, all)
- [ ] Reinventing the wheel? (Check itertools, collections, functools)
- [ ] Using third-party libraries when standard library suffices?

### Examples to Catch
```python
# ❌ String concatenation in loop
result = ""
for item in items:
    result += str(item)

# ❌ List when generator works
values = [expensive_func(x) for x in huge_list]
total = sum(values)

# ❌ Global lookup in loop
for i in range(n):
    result = math.sqrt(i)  # math looked up each iteration

# ❌ Index-based loop when index is not needed
for i in range(len(items)):
    process(items[i])

# ✅ Direct iteration
for item in items:
    process(item)

# ✅ Generator expression
total = sum(expensive_func(x) for x in huge_list)

# ✅ Cache module reference outside loop
sqrt = math.sqrt
for i in range(n):
    result = sqrt(i)
```

---

## 🤖 ML/AI Code

### Model Performance
- [ ] Are predictions batched? (vs. one-at-a-time)
- [ ] Using appropriate precision? (float32 vs float64)
- [ ] Model quantized for inference? (If applicable)
- [ ] Unnecessary model loading? (Load once, reuse)
- [ ] GPU utilized when available?

### Data Processing
- [ ] NumPy vectorization used? (vs. Python loops)
- [ ] Pandas operations vectorized? (vs. iterrows/apply)
- [ ] Data loaded efficiently? (Lazy loading, streaming)
- [ ] Appropriate data types? (category, int32 vs int64)

### Examples to Catch
```python
# ❌ Item-by-item prediction
for item in dataset:
    pred = model.predict([item])

# ✅ Batch prediction
preds = model.predict(dataset)

# ❌ Python loop over NumPy array
result = []
for val in array:
    result.append(val * 2)

# ✅ Vectorized NumPy operation
result = array * 2
```

---

## ⚡ Concurrency & Parallelism

### Thread/Process Safety
- [ ] CPU-bound tasks use multiprocessing? (GIL blocks threads)
- [ ] I/O-bound tasks use asyncio or threads?
- [ ] Thread pools sized appropriately for workload?

### Examples to Catch
```python
# ❌ Thread for CPU-bound work (GIL limits parallelism)
for data in cpu_intensive_data:
    t = threading.Thread(target=process, args=(data,))
    t.start()  # GIL prevents true parallelism

# ❌ Sequential I/O operations
for url in urls:
    data = requests.get(url).json()  # Could be concurrent

# ✅ ProcessPoolExecutor for CPU-bound work
with ProcessPoolExecutor() as pool:
    results = list(pool.map(process, cpu_intensive_data))

# ✅ ThreadPoolExecutor for I/O-bound work
with ThreadPoolExecutor() as pool:
    results = list(pool.map(fetch, urls))
```

---

## 📝 NLP & Text Processing

### Text Processing
- [ ] Regex patterns compiled once? (Not in loops)
- [ ] Batch processing for NLP pipelines?
- [ ] Efficient tokenization? (Using compiled libraries)
- [ ] String operations optimized?

### Document Processing
- [ ] Large documents streamed? (vs. loading entirely)
- [ ] Embeddings computed in batches?
- [ ] Vector storage optimized? (FAISS, efficient formats)
- [ ] Caching for repeated computations?

### Examples to Catch
```python
# ❌ Dynamic regex compilation in loop
for text in texts:
    pattern = re.compile(build_pattern(config))
    matches = pattern.findall(text)

# ✅ Compile once and reuse
pattern = re.compile(build_pattern(config))
for text in texts:
    matches = pattern.findall(text)

# ❌ Sequential document processing
docs = [nlp(text) for text in texts]  # No batching

# ❌ Inefficient embeddings
embeddings = []
for doc in docs:
    emb = model.encode(doc)  # One at a time
    embeddings.append(emb)

# ✅ Batch processing
embeddings = model.encode(docs)  # All at once
```

---

## 🎨 Code Structure

### Function Design
- [ ] Functions doing too much? (Could be split)
- [ ] Expensive operations repeated? (Could cache results)
- [ ] Unnecessary work in hot paths?
- [ ] Early returns to avoid unnecessary computation?

### Imports & Initialization
- [ ] Expensive imports in hot paths?
- [ ] Heavy initialization in loops?
- [ ] Lazy loading where appropriate?

