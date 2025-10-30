"""
Spatial Test 0: Pure Spatial Reasoning
Tests basic spatial understanding without chess rules
"""

import os
from typing import List, Dict
from datetime import datetime
from ..data_structures import TestResult, save_results
from ..board_generator import ChessBoardGenerator
from .test_0_generator import SpatialTest0Generator


class SpatialTest0:
    """Test 0: Pure spatial understanding (no chess rules)"""

    def __init__(self,
                 base_output_dir: str = "./output/spatial_test_0",
                 n_cases_per_type: int = 10,
                 seed: int = 42,
                 auto_timestamp: bool = True):
        """
        Initialize Spatial Test 0

        Args:
            base_output_dir: Base directory for output files
            n_cases_per_type: Number of cases per test type
            seed: Random seed for reproducibility
            auto_timestamp: If True, append timestamp to output directory
        """
        # Create timestamped output directory
        if auto_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = f"{base_output_dir}_{timestamp}"
        else:
            self.output_dir = base_output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.board_gen = ChessBoardGenerator()
        self.test_cases = []
        self.n_cases_per_type = n_cases_per_type
        self.seed = seed

    def generate_test_cases(self) -> List[Dict]:
        """Generate test cases automatically"""
        print(
            f"\nGenerating test cases (n_per_type={self.n_cases_per_type}, seed={self.seed})")
        print("="*60)

        generator = SpatialTest0Generator(seed=self.seed)
        cases = generator.generate_all(n_per_type=self.n_cases_per_type)

        self.test_cases = cases
        return cases

    def create_test_images(self):
        """Generate images for all test cases"""
        print(f"\nCreating test images...")
        print("="*60)

        for i, case in enumerate(self.test_cases, 1):
            if "pieces" in case:
                img = self.board_gen.create_board_with_pieces(
                    pieces=case["pieces"],
                    highlighted_squares=case["squares"]
                )
            else:
                img = self.board_gen.create_empty_board(
                    highlighted_squares=case["squares"]
                )

            img_path = os.path.join(self.output_dir, f"{case['case_id']}.png")
            img.save(img_path)
            case["image_path"] = img_path

            if i % 10 == 0 or i == len(self.test_cases):
                print(f"  Progress: {i}/{len(self.test_cases)} images created")

        print(f"✓ All {len(self.test_cases)} images created\n")

    def generate_prompt(self, case: Dict) -> str:
        """Generate test prompt"""
        return f"""Look at this chess board.

Question: {case['question']}

Answer with one word: yes, no, or unknown"""

    def run_test(self, model_client, save_results_flag: bool = True) -> List[TestResult]:
        """Run the test"""
        results = []

        print(f"{'='*60}")
        print("Running Spatial Test 0: Pure Spatial Reasoning")
        print(f"{'='*60}\n")

        for i, case in enumerate(self.test_cases, 1):
            print(
                f"[{i}/{len(self.test_cases)}] Testing {case['case_id']}...", end=" ")

            prompt = self.generate_prompt(case)

            try:
                response = model_client.query(prompt, case["image_path"])
                model_answer = self._extract_answer(response)
                correct = (model_answer.lower() == case["expected"].lower())

                print(
                    f"{'✓' if correct else '✗'} (Expected: {case['expected']}, Got: {model_answer})")

            except Exception as e:
                print(f"✗ Error: {e}")
                model_answer = "error"
                correct = False
                response = str(e)

            result = TestResult(
                test_type="spatial",
                test_layer=0,
                case_id=case["case_id"],
                question=case["question"],
                expected_answer=case["expected"],
                model_response=response,
                correct=correct,
                image_paths=[case["image_path"]],
                model_name=model_client.model_name
            )
            results.append(result)

        # Calculate and display statistics
        self._print_results_summary(results)

        if save_results_flag:
            output_file = os.path.join(self.output_dir, "test_0_results.json")
            save_results(results, output_file)

        return results

    def _print_results_summary(self, results: List[TestResult]):
        """Print detailed results summary"""
        accuracy = sum(r.correct for r in results) / len(results)

        print(f"\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(
            f"Overall Accuracy: {accuracy:.2%} ({sum(r.correct for r in results)}/{len(results)})")

        # Calculate accuracy by test type
        print(f"\nAccuracy by test type:")
        type_results = {}

        for result in results:
            # Find corresponding case
            case = next(
                (c for c in self.test_cases if c['case_id'] == result.case_id), None)
            if case:
                case_type = case.get('type', 'unknown')
                subtype = case.get('subtype', '')
                key = f"{case_type}" if not subtype else f"{case_type}_{subtype}"

                if key not in type_results:
                    type_results[key] = {'correct': 0, 'total': 0}
                type_results[key]['total'] += 1
                if result.correct:
                    type_results[key]['correct'] += 1

        for case_type in sorted(type_results.keys()):
            stats = type_results[case_type]
            acc = stats['correct'] / stats['total']
            print(
                f"  {case_type:20s}: {acc:5.1%} ({stats['correct']:2d}/{stats['total']:2d})")

        print(f"{'='*60}\n")

    def _extract_answer(self, response: str) -> str:
        """Extract answer from model response"""
        response_lower = response.lower().strip()

        if "yes" in response_lower[:20]:
            return "yes"
        elif "no" in response_lower[:20]:
            return "no"
        else:
            return "unknown"
