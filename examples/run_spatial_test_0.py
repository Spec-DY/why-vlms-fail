"""
Run Spatial Test 0 with automatic generation
Each run creates a new timestamped folder
"""

from src.model_client import DummyModelClient, ClaudeModelClient, NovitaModelClient
from src.spatial.test_0_pure_ability import SpatialTest0
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def main():
    """
    Run Spatial Test 0 with automatic test case generation

    Each run creates a new folder with timestamp:
    ./output/spatial_test_0_YYYYMMDD_HHMMSS/
    """

    print("\n" + "="*60)
    print("SPATIAL TEST 0: AUTOMATIC TEST GENERATION")
    print("="*60)

    # ===== Configuration =====

    N_CASES_PER_TYPE = 15    # Number of cases per test type
    SEED = 42                 # Random seed for reproducibility

    # Choose model client
    MODEL_TYPE = "dummy"     # Options: "dummy", "claude", "novita"

    # ===== Setup Test =====

    test0 = SpatialTest0(
        base_output_dir="./output/spatial_test_0",
        n_cases_per_type=N_CASES_PER_TYPE,
        seed=SEED,
        auto_timestamp=True  # Automatically add timestamp to folder name
    )

    print(f"\nOutput directory: {test0.output_dir}")
    print(f"Configuration:")
    print(f"  - Cases per type: {N_CASES_PER_TYPE}")
    print(f"  - Random seed: {SEED}")
    print(f"  - Model: {MODEL_TYPE}")

    # ===== Generate Test Cases =====

    cases = test0.generate_test_cases()
    print(f"\n✓ Generated {len(cases)} test cases")

    # Show case type distribution
    type_counts = {}
    for case in cases:
        case_type = case.get('type', 'unknown')
        subtype = case.get('subtype', '')
        key = f"{case_type}" if not subtype else f"{case_type}_{subtype}"
        type_counts[key] = type_counts.get(key, 0) + 1

    print("\nTest case distribution:")
    for case_type in sorted(type_counts.keys()):
        count = type_counts[case_type]
        print(f"  {case_type:20s}: {count:3d} cases")

    # ===== Create Test Images =====

    test0.create_test_images()

    # ===== Setup Model Client =====

    print(f"{'='*60}")
    print("MODEL SETUP")
    print("="*60)

    if MODEL_TYPE == "dummy":
        model_client = DummyModelClient()
        print("✓ Using Dummy Model (random answers for testing)\n")

    elif MODEL_TYPE == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        model_client = ClaudeModelClient(api_key=api_key)
        print(f"✓ Using Claude: {model_client.model_name}\n")

    elif MODEL_TYPE == "novita":
        api_key = os.getenv("NOVITA_API_KEY")
        if not api_key:
            raise ValueError("NOVITA_API_KEY not found in environment")
        model_client = NovitaModelClient(api_key=api_key, stream=False)
        print(f"✓ Using Novita: {model_client.model_name}\n")

    else:
        raise ValueError(f"Unknown model type: {MODEL_TYPE}")

    # ===== Run Test =====

    results = test0.run_test(model_client)

    # ===== Final Summary =====

    print(f"✓ Test completed!")
    print(f"\nAll results saved in:")
    print(f"  {test0.output_dir}/")
    print(f"\nContents:")
    print(f"  - {len(cases)} test images (PNG)")
    print(f"  - test_0_results.json")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
