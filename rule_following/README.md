# VLM Rule Following Test

A comprehensive testing framework for evaluating Vision Language Models (VLMs) on spatial and temporal reasoning abilities using chess scenarios.

## 📋 Overview

This project systematically tests VLMs through generated chess board images to evaluate their capabilities in:

- **Spatial Reasoning**: Board position recognition, relative directions, diagonal relationships, etc.
- **Rule Understanding**: Chess rules application (piece movements, en passant, castling, etc.)
- **Temporal Reasoning**: Tracking piece movement sequences and understanding state changes
- **Rule Complexity Ladder**: Testing model accuracy with increasing constraints

Each test includes a **verification mechanism** to ensure the model can correctly recognize the board before testing its reasoning abilities.

## ✨ Key Features

### 🎯 Test Suites
#### Diagnostic Matrix

|                | **Rule Free**              | **Rule Based**              |
|----------------|----------------------------|-----------------------------|
| **Single State**  | Spatial Test 0  | Spatial Test 1  |
| **Multi States** | Temporal Test 0 | Temporal Test 1 |

---
#### Rule Complexity Ladder

Six levels of increasing complexity from Level 1 to Level 6

| Mode | Description |
|------|-------------|
| **Explicit** | Rules are explicitly provided in context; model must understand and apply them |
| **Predictive** | Rules are not given; model must infer rules from examples |


## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Spec-DY/why-vlms-fail.git
cd rule_following

# Install in development mode
pip install -e .
```

### 🔌 Multi-Model Support

Supports any OpenAI-compatible API
Model support added:
- **DashScope**
- **Novita AI**
- **XAI**
- **Custom endpoints** (easily extensible)
- **Dummy Model** (for testing the framework)

### Configuration

Create a `.env` file in the project root:

```env
# For DashScope
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen3-vl-8b-thinking
DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1

# For Novita AI
NOVITA_API_KEY=your_api_key_here
NOVITA_BASE_URL=https://api.novita.ai/openai
NOVITA_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# For XAI (Grok)
XAI_API_KEY=your_api_key_here
XAI_MODEL=grok-4-fast-reasoning
XAI_BASE_URL=https://api.x.ai/v1
```

### Example of Running Diagnostic Matrix Tests

```bash
# Run Spatial Test 0
python run/run_spatial_test_0.py

# Run Temporal Test 1
python run/run_temporal_test_1.py

# Run Rule Complexity Ladder
python run/run_temporal_levels.py -all -m novita
```

### Customizing Test Parameters in Temporal/Spatial Test 0 & 1

Edit the configuration section in each run file:

```python
# In examples/run_spatial_test_0.py
N_CASES_PER_TYPE = 18      # Number of cases per test type
SEED = 57                  # Random seed for reproducibility
MODEL_TYPE = "xai"         # Options: "dummy", "dashscope", "novita", "xai"
RATE_LIMIT_REQUESTS = 0    # Number of requests before pausing
RATE_LIMIT_PAUSE = 0       # Pause duration in seconds
```

## 🔧 Adding New Models

Extend the `OpenAICompatibleModelClient` class:

```python
class YourModelClient(OpenAICompatibleModelClient):
    DEFAULT_BASE_URL = "https://api.yourservice.com/v1"
    ENV_API_KEY = "YOUR_API_KEY"
    ENV_BASE_URL = "YOUR_BASE_URL"
    ENV_MODEL = "YOUR_MODEL"
    SERVICE_NAME = "YourService"
```

Add to `.env`:

```env
YOUR_API_KEY=your_key
YOUR_MODEL=your_model_name
```

## 🛠️ Advanced Usage in Diagnostic Matrix Tests

### Rate Limiting

For API rate limits, configure pause intervals:

```python
test = SpatialTest1(
    rate_limit_requests=50,  # Pause after 50 requests
    rate_limit_pause=60      # Wait 60 seconds
)
```

### Batch Testing Multiple Models

```python
models = ["dashscope", "novita", "xai"]
for model_type in models:
    model_client = create_client(model_type)
    results, stats = test.run_test(model_client)
    # Results auto-saved to separate directories
```

## Rule Complexity Ladder

---

#### 1\. Run Specific Levels

If you only want to test specific levels (e.g., Level 1 and Level 4):

```bash
python run/run_temporal_levels.py -l 1 4 --model xai
```

_(Note: Use `-l` followed by the level numbers separated by spaces)_

---

## ⚙️ Available Arguments

| Argument                | Short | Type         | Default        | Description                                                                                              |
| :---------------------- | :---- | :----------- | :------------- | :------------------------------------------------------------------------------------------------------- |
| **`--levels`**          | `-l`  | `int` (list) | `None`         | Specific level numbers to run (e.g., `-l 1 2 3`). Mutually exclusive with `--all`.                       |
| **`--all`**             |       | `flag`       | `False`        | Run all available levels (currently 1-4). Mutually exclusive with `--levels`.                            |
| **`--model`**           | `-m`  | `str`        | `dummy`      | Model client to use. Options: `dummy`, `novita`, `dashscope`, `xai`, `sf`, `google`.                     |
| **`--n-cases`**         | `-n`  | `int`        | `None`         | Number of test cases to generate per level. If not set, uses the level's default (usually 60-100).       |
| **`--seed`**            | `-s`  | `int`        | `42`           | Random seed for reproducibility of test case generation.                                                 |
| **`--output`**          | `-o`  | `str`        | `"./output"`   | Base directory for saving output results.                                                                |
| **`--dummy-pass-rate`** |       | `float`      | `0.8`          | **Only for `dummy` model.** Probability (0.0-1.0) that the dummy model passes the verification question. |
| **`--rate-limit`**      |       | `int`        | `0`            | Number of requests to process before pausing. `0` means no limit.                                        |
| **`--rate-pause`**      |       | `int`        | `0`            | Duration in seconds to pause when the rate limit is reached.                                             |
| **`--mode`**            |       | `str`        | `predictive` | Choose between `predictive` or `explicit`.                                                               |

---
