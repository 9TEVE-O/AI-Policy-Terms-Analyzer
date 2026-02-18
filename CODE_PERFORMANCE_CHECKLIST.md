@@ -18,75 +18,79 @@ Use this checklist when reviewing code for performance issues.
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

# ❌ Function call in condition
for i in range(len(items)):  # len() called every iteration
# ❌ Index-based loop when index is not needed
for i in range(len(items)):
    process(items[i])

# ✅ Direct iteration
for item in items:
    process(item)
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

@@ -225,53 +229,59 @@ for data in cpu_intensive_data:
    t.start()  # GIL prevents true parallelism

# ❌ Sequential I/O operations
for url in urls:
    data = requests.get(url).json()  # Could be concurrent
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
# ❌ Regex compilation in loop
# ❌ Dynamic regex compilation in loop
for text in texts:
    pattern = re.compile(build_pattern(config))
    matches = pattern.findall(text)

# ✅ Compile once and reuse
pattern = re.compile(build_pattern(config))
for text in texts:
    matches = re.findall(r'\b\w+\b', text)  # Pattern compiled each time
    matches = pattern.findall(text)

# ❌ Sequential document processing
docs = [nlp(text) for text in texts]  # No batching

# ❌ Inefficient embeddings
embeddings = []
for doc in docs:
    emb = model.encode(doc)  # One at a time
    embeddings.append(emb)
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
