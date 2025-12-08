
"""
Standard Temporal Level
A generic class to handle any temporal level by injecting the specific generator.
Supports two modes: 'predictive' (default) and 'explicit'
"""

from typing import List, Dict, Type, Literal
from .temporal_level_base import TemporalLevelBase

# Predictive generators (default)
from .level_1_generator import Level1Generator
from .level_2_generator import Level2Generator
from .level_3_generator import Level3Generator
from .level_4_generator import Level4Generator
from .level_5_generator import Level5Generator
from .level_6_generator import Level6Generator

# Explicit generators
from .level_1_generator_explicit import Level1Generator as Level1GeneratorExplicit
from .level_2_generator_explicit import Level2Generator as Level2GeneratorExplicit
from .level_3_generator_explicit import Level3Generator as Level3GeneratorExplicit
from .level_4_generator_explicit import Level4Generator as Level4GeneratorExplicit
from .level_5_generator_explicit import Level5Generator as Level5GeneratorExplicit
from .level_6_generator_explicit import Level6Generator as Level6GeneratorExplicit


# Generator mapping
_GENERATORS = {
    'predictive': {
        1: Level1Generator,
        2: Level2Generator,
        3: Level3Generator,
        4: Level4Generator,
        5: Level5Generator,
        6: Level6Generator,
    },
    'explicit': {
        1: Level1GeneratorExplicit,
        2: Level2GeneratorExplicit,
        3: Level3GeneratorExplicit,
        4: Level4GeneratorExplicit,
        5: Level5GeneratorExplicit,
        6: Level6GeneratorExplicit,
    }
}

Mode = Literal['predictive', 'explicit']


class StandardTemporalLevel(TemporalLevelBase):
    """
    A generic implementation for Temporal Levels.
    Supports two modes: 'predictive' (default) and 'explicit'
    """

    def __init__(self,
                 level: int,
                 generator_class: Type = None,
                 mode: Mode = 'predictive',
                 base_output_dir: str = None,
                 n_cases: int = 100,
                 seed: int = 42,
                 auto_timestamp: bool = True,
                 rate_limit_requests: int = 0,
                 rate_limit_pause: int = 0,
                 **generator_kwargs):
        """
        Initialize Standard Temporal Level

        Args:
            level: Level number (1-6)
            generator_class: Custom generator class (overrides mode if provided)
            mode: 'predictive' (default) or 'explicit'
            base_output_dir: Output directory
            n_cases: Number of test cases
            seed: Random seed
            auto_timestamp: Append timestamp to output dir
            rate_limit_requests: Rate limiting config
            rate_limit_pause: Rate limiting pause seconds
            **generator_kwargs: Extra arguments for generator
        """
        if base_output_dir is None:
            base_output_dir = f"./output/temporal_level_{level}"

        super().__init__(
            level=level,
            base_output_dir=base_output_dir,
            n_cases=n_cases,
            seed=seed,
            auto_timestamp=auto_timestamp,
            rate_limit_requests=rate_limit_requests,
            rate_limit_pause=rate_limit_pause
        )

        # Use provided generator_class, otherwise select based on mode
        if generator_class is not None:
            self.generator_class = generator_class
        else:
            if mode not in _GENERATORS:
                raise ValueError(
                    f"Unknown mode: {mode}. Use 'predictive' or 'explicit'")
            if level not in _GENERATORS[mode]:
                raise ValueError(f"Level {level} not supported")
            self.generator_class = _GENERATORS[mode][level]

        self.mode = mode
        self.generator_kwargs = generator_kwargs

    def generate_test_cases(self) -> List[Dict]:
        """Generate test cases using the selected generator class"""
        print(
            f"\nGenerating Level {self.level} test cases (mode={self.mode}, n_cases={self.n_cases}, seed={self.seed})")
        print("=" * 60)

        generator = self.generator_class(
            seed=self.seed, **self.generator_kwargs)
        cases = generator.generate_all(n_cases=self.n_cases)

        for case in cases:
            case.update(self.verification_gen.generate_verification(case))

        self.test_cases = cases
        return cases


# ============ Backward-compatible aliases ============

def _create_level_class(level: int):
    """Create backward-compatible level class with mode support"""

    class _TemporalLevelN(StandardTemporalLevel):
        def __init__(self,
                     base_output_dir: str = None,
                     n_cases: int = 100,
                     seed: int = 42,
                     auto_timestamp: bool = True,
                     rate_limit_requests: int = 0,
                     rate_limit_pause: int = 0,
                     mode: Mode = 'predictive'):
            super().__init__(
                level=level,
                mode=mode,
                base_output_dir=base_output_dir,
                n_cases=n_cases,
                seed=seed,
                auto_timestamp=auto_timestamp,
                rate_limit_requests=rate_limit_requests,
                rate_limit_pause=rate_limit_pause
            )

    _TemporalLevelN.__name__ = f"TemporalLevel{level}"
    _TemporalLevelN.__qualname__ = f"TemporalLevel{level}"
    return _TemporalLevelN


TemporalLevel1 = _create_level_class(1)
TemporalLevel2 = _create_level_class(2)
TemporalLevel3 = _create_level_class(3)
TemporalLevel4 = _create_level_class(4)
TemporalLevel5 = _create_level_class(5)
TemporalLevel6 = _create_level_class(6)
