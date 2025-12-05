# Why VLMs Fail?

Diagnostic tests for understanding why VLMs fail in game scenarios.

## Overview

This repository contains two complementary test suites that systematically evaluate VLM capabilities:

| Module | Focus | Games Used |
|--------|-------|------------|
| [**Perception**](./perception/README.md) | Visual perception accuracy | Gomoku, Chess, TicTacToe |
| [**Rule Following**](./rule_following/README.md) | Spatial & temporal reasoning | Chess |

## Project Structure

```
vlm_benchmark/
├── perception/              # Perception test suite
│   ├── tests/               # Test scripts (patch, density, resolution, richness)
│   ├── shared/              # Shared utilities & model configs
│   └── assets/              # Game assets (textures, pieces)
│
├── rule_following/          # Rule following test suite
│   ├── src/                 # Core modules (spatial, temporal, condition)
│   └── run/                 # Test runners
│
└── README.md                # This file
```

## Test Suites

### Perception Tests

Evaluates how visual factors affect VLM perception accuracy:

- **Patch Alignment** - Aligned vs offset image patches
- **Resolution** - Image resolution & patch divisibility  
- **Visual Richness** - 2D flat vs 3D rendered styles
- **Density** - Low/medium/high piece density

👉 [View detailed documentation](./perception/README.md)

### Rule Following Tests

Evaluates spatial and temporal reasoning with chess rules:

- **Spatial Test 0** - Pure spatial reasoning (no chess knowledge)
- **Spatial Test 1** - Chess movement rules for all piece types
- **Temporal Test 0** - Sequence understanding & state tracking
- **Temporal Test 1** - Time-dependent rules (en passant, castling)

👉 [View detailed documentation](./rule_following/README.md)

## Supported Models

Both test suites support multiple VLM providers:

- **Qwen-VL** (Alibaba DashScope)
- **Gemini / Gemma** (Google)
- **GLM-4V** (Zhipu AI)
- **Grok** (XAI)
- **Novita AI**
- Custom OpenAI-compatible endpoints

## Quick Start

### Installation

```bash
git clone <repo-url>
cd vlm_benchmark

# Install rule_following module
cd rule_following
pip install -e .
cd ..

# Install perception dependencies
cd perception
pip install -r requirements.txt
cd ..
```

### Configuration

Create `.env` files in each module directory with your API keys. See individual READMEs for details.

### Running Tests

```bash
# Perception tests
cd perception
python tests/density/run_chess_density_tests.py

# Rule following tests
cd rule_following
python run/run_spatial_test_0.py
```
