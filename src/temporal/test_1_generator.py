"""
Automated test case generator for Temporal Test 1
Temporal rule following - En Passant and Castling
"""

import random
from typing import List, Dict, Tuple


class TemporalTest1Generator:
    """Generate temporal rule following test cases"""

    def __init__(self, seed: int = 42):
        """
        Initialize generator

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8']

    def _random_file(self) -> str:
        """Get random file"""
        return random.choice(self.files)

    def _random_square(self) -> str:
        """Generate random square"""
        return random.choice(self.files) + random.choice(self.ranks)

    def _adjacent_files(self, file: str) -> List[str]:
        """Get adjacent files"""
        file_idx = self.files.index(file)
        adjacent = []
        if file_idx > 0:
            adjacent.append(self.files[file_idx - 1])
        if file_idx < 7:
            adjacent.append(self.files[file_idx + 1])
        return adjacent

    def _square_to_coords(self, square: str) -> Tuple[int, int]:
        """Convert square name to coordinates (0-7, 0-7)"""
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        return (file, rank)

    def _coords_to_square(self, file: int, rank: int) -> str:
        """Convert coordinates to square name"""
        if 0 <= file < 8 and 0 <= rank < 8:
            return chr(ord('a') + file) + str(rank + 1)
        return None

    def _distribute_cases(self, total: int, n_types: int) -> List[int]:
        """
        Distribute total cases across n_types
        Tries to balance evenly
        """
        if total == 0:
            return [0] * n_types

        base = total // n_types
        remainder = total % n_types
        counts = [base] * n_types
        for i in range(remainder):
            counts[i] += 1
        return counts

    # ============= Type 1: En Passant Rule Judgment =============

    def generate_en_passant_rule_tests(self, n_cases: int = 10) -> List[Dict]:
        """
        Generate en passant rule judgment tests
        2 states: Check if en passant is possible

        Args:
            n_cases: Total number of cases
        """
        cases = []
        n_pos = n_cases // 2
        n_neg = n_cases - n_pos

        # Positive cases: Black pawn moved 2 squares from rank 7 to rank 5
        for i in range(n_pos):
            # Random setup for white pawn at rank 5
            white_file = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            white_sq = white_file + '5'

            # Black pawn on adjacent file
            adjacent = self._adjacent_files(white_file)
            if adjacent:
                black_file = random.choice(adjacent)
            else:
                black_file = 'b' if white_file == 'a' else 'g'

            black_start = black_file + '7'
            black_end = black_file + '5'
            capture_sq = black_file + '6'

            cases.append({
                "case_id": f"en_passant_rule_pos_{i+1}",
                "type": "en_passant_rule",
                "subtype": "valid",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_end: 'p'}, "squares": []}
                ],
                "label": "These are consecutive board states (State 2 immediately follows State 1)",
                "question": f"Can white capture the black pawn en passant?",
                "expected": "yes",
                "reasoning": f"Black pawn moved 2 squares from {black_start} to {black_end}"
            })

        # Negative cases
        neg_type_1 = n_neg // 2  # Only moved 1 square
        neg_type_2 = n_neg - neg_type_1  # Not adjacent

        # Negative Type 1: Black pawn only moved 1 square
        for i in range(neg_type_1):
            white_file = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            white_sq = white_file + '5'

            adjacent = self._adjacent_files(white_file)
            if adjacent:
                black_file = random.choice(adjacent)
            else:
                black_file = 'b' if white_file == 'a' else 'g'

            # Pawn only moved 1 square (from 6 to 5)
            black_start = black_file + '6'
            black_end = black_file + '5'
            capture_sq = black_file + '6'

            cases.append({
                "case_id": f"en_passant_rule_neg_{i+1}",
                "type": "en_passant_rule",
                "subtype": "moved_one_square",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_end: 'p'}, "squares": []}
                ],
                "label": "These are consecutive states",
                "question": f"Can white capture the black pawn en passant?",
                "expected": "no",
                "reasoning": f"Black pawn only moved 1 square from {black_start} to {black_end}"
            })

        # Negative Type 2: Pawns not adjacent
        for i in range(neg_type_2):
            white_file = random.choice(['a', 'b', 'c', 'd'])
            white_sq = white_file + '5'

            # Black pawn 2+ files away
            black_file_idx = self.files.index(
                white_file) + random.choice([2, 3, 4])
            if black_file_idx >= 8:
                black_file_idx = self.files.index(
                    white_file) - random.choice([2, 3])
            black_file = self.files[black_file_idx]

            black_start = black_file + '7'
            black_end = black_file + '5'
            capture_sq = black_file + '6'

            cases.append({
                "case_id": f"en_passant_rule_neg_{neg_type_1 + i + 1}",
                "type": "en_passant_rule",
                "subtype": "not_adjacent",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_end: 'p'}, "squares": []}
                ],
                "label": "These are consecutive states",
                "question": f"Can white capture the black pawn en passant?",
                "expected": "no",
                "reasoning": f"White pawn at {white_sq} is not adjacent to black pawn at {black_end}"
            })

        return cases

    # ============= Type 1: Castling Rule Judgment =============

    def generate_castling_rule_tests(self, n_cases: int = 10) -> List[Dict]:
        """
        Generate castling rule judgment tests
        2-3 states: Check if castling is possible

        Negative types (6 kinds):
        1. king_moved - King has moved before
        2. rook_moved - Rook has moved before
        3. path_blocked - Pieces blocking the path
        4. in_check - King is currently in check
        5. through_check - King would pass through attacked square
        6. into_check - King would land on attacked square

        Args:
            n_cases: Total number of cases
        """
        cases = []
        n_pos = n_cases // 2
        n_neg = n_cases - n_pos

        # Positive cases: Can castle
        for i in range(n_pos):
            # Randomly choose kingside or queenside
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                rook_sq = 'h1'
            else:
                rook_sq = 'a1'

            cases.append({
                "case_id": f"castling_rule_pos_{i+1}",
                "type": "castling_rule",
                "subtype": f"valid_{side}",
                "states": [
                    {"pieces": {'e1': 'K', rook_sq: 'R'}, "squares": []},
                    {"pieces": {'e1': 'K', rook_sq: 'R'}, "squares": []}
                ],
                "label": "King and Rook have never moved. Path is clear and safe.",
                "question": f"Can white castle {side}?",
                "expected": "yes",
                "reasoning": f"All conditions met, can castle {side}"
            })

        # Negative cases: Distribute across 6 failure types
        neg_types = [
            'king_moved',
            'rook_moved',
            'path_blocked',
            'in_check',
            'through_check',
            'into_check'
        ]
        neg_counts = self._distribute_cases(n_neg, len(neg_types))

        neg_idx = 0

        # Type 1: King moved
        for i in range(neg_counts[0]):
            side = random.choice(['kingside', 'queenside'])
            rook_sq = 'h1' if side == 'kingside' else 'a1'

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "king_moved",
                "states": [
                    {"pieces": {'e1': 'K', rook_sq: 'R'}, "squares": []},
                    {"pieces": {'e2': 'K', rook_sq: 'R'},
                        "squares": []},  # King moved
                    {"pieces": {'e1': 'K', rook_sq: 'R'},
                        "squares": []}   # King returned
                ],
                "label": "States shown in chronological order",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": "King has moved (even though it returned to original position)"
            })
            neg_idx += 1

        # Type 2: Rook moved
        for i in range(neg_counts[1]):
            side = random.choice(['kingside', 'queenside'])
            rook_sq = 'h1' if side == 'kingside' else 'a1'
            rook_temp = 'h2' if side == 'kingside' else 'a2'

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "rook_moved",
                "states": [
                    {"pieces": {'e1': 'K', rook_sq: 'R'}, "squares": []},
                    {"pieces": {'e1': 'K', rook_temp: 'R'},
                        "squares": []},  # Rook moved
                    {"pieces": {'e1': 'K', rook_sq: 'R'},
                        "squares": []}     # Rook returned
                ],
                "label": "States shown in chronological order",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": "Rook has moved"
            })
            neg_idx += 1

        # Type 3: Path blocked
        for i in range(neg_counts[2]):
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                blocking_sq = random.choice(['f1', 'g1'])
                blocker_piece = random.choice(['N', 'B'])
                pieces = {'e1': 'K', 'h1': 'R', blocking_sq: blocker_piece}
            else:
                blocking_sq = random.choice(['b1', 'c1', 'd1'])
                blocker_piece = random.choice(['N', 'B', 'Q'])
                pieces = {'e1': 'K', 'a1': 'R', blocking_sq: blocker_piece}

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "path_blocked",
                "states": [
                    {"pieces": pieces, "squares": []},
                    {"pieces": pieces, "squares": []}
                ],
                "label": "King and Rook have never moved",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": f"Path is blocked by piece at {blocking_sq}"
            })
            neg_idx += 1

        # Type 4: In check (out of check)
        for i in range(neg_counts[3]):
            side = random.choice(['kingside', 'queenside'])
            rook_sq = 'h1' if side == 'kingside' else 'a1'

            # Place attacking piece (black Rook on e-file to check King)
            attacker_sq = 'e8'

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "in_check",
                "states": [
                    {"pieces": {'e1': 'K', rook_sq: 'R',
                                attacker_sq: 'r'}, "squares": []},
                    {"pieces": {'e1': 'K', rook_sq: 'R',
                                attacker_sq: 'r'}, "squares": []}
                ],
                "label": "King and Rook have never moved",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": "King is currently in check (cannot castle out of check)"
            })
            neg_idx += 1

        # Type 5: Through check ⭐ ENHANCED
        for i in range(neg_counts[4]):
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                # Black Bishop on c4 attacks f1 (King passes through f1)
                attacker_sq = 'c4'
                attacker_piece = 'b'
                attacked_sq = 'f1'
                rook_sq = 'h1'
            else:
                # Black Rook on d8 attacks d1 (King passes through d1)
                attacker_sq = 'd8'
                attacker_piece = 'r'
                attacked_sq = 'd1'
                rook_sq = 'a1'

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "through_check",
                "states": [
                    {"pieces": {
                        'e1': 'K',
                        rook_sq: 'R',
                        attacker_sq: attacker_piece
                    }, "squares": []},
                    {"pieces": {
                        'e1': 'K',
                        rook_sq: 'R',
                        attacker_sq: attacker_piece
                    }, "squares": []}
                ],
                "label": "King and Rook have never moved",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": f"King would pass through {attacked_sq} which is under attack"
            })
            neg_idx += 1

        # Type 6: Into check ⭐ NEW
        for i in range(neg_counts[5]):
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                # Black Rook on g8 would attack King at g1 (final position)
                attacker_sq = 'g8'
                attacker_piece = 'r'
                final_king_sq = 'g1'
                rook_sq = 'h1'
            else:
                # Black Bishop on f4 would attack King at c1 (final position)
                attacker_sq = 'f4'
                attacker_piece = 'b'
                final_king_sq = 'c1'
                rook_sq = 'a1'

            cases.append({
                "case_id": f"castling_rule_neg_{neg_idx + 1}",
                "type": "castling_rule",
                "subtype": "into_check",
                "states": [
                    {"pieces": {
                        'e1': 'K',
                        rook_sq: 'R',
                        attacker_sq: attacker_piece
                    }, "squares": []},
                    {"pieces": {
                        'e1': 'K',
                        rook_sq: 'R',
                        attacker_sq: attacker_piece
                    }, "squares": []}
                ],
                "label": "King and Rook have never moved",
                "question": f"Can white castle {side}?",
                "expected": "no",
                "reasoning": f"After castling, King would be at {final_king_sq} which is under attack"
            })
            neg_idx += 1

        return cases

    # ============= Type 2: En Passant Event Recognition =============

    def generate_en_passant_event_tests(self, n_cases: int = 10) -> List[Dict]:
        """
        Generate en passant event recognition tests
        3 states showing complete en passant sequence
        Multiple choice questions

        Args:
            n_cases: Total number of cases
        """
        cases = []
        n_standard = int(n_cases * 0.7)  # 70% standard cases
        n_confuser = n_cases - n_standard  # 30% confuser cases

        # Standard en passant cases
        for i in range(n_standard):
            white_file = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            white_sq = white_file + '5'

            adjacent = self._adjacent_files(white_file)
            if adjacent:
                black_file = random.choice(adjacent)
            else:
                black_file = 'b'

            black_start = black_file + '7'
            black_mid = black_file + '5'
            capture_sq = black_file + '6'

            cases.append({
                "case_id": f"en_passant_event_pos_{i+1}",
                "type": "en_passant_event",
                "subtype": "en_passant",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_mid: 'p'}, "squares": []},
                    # Black pawn captured
                    {"pieces": {capture_sq: 'P'}, "squares": []}
                ],
                "label": "States shown in chronological order",
                "question": "What happened in this sequence?",
                "options": {
                    "A": "Castling",
                    "B": "En passant capture",
                    "C": "Regular capture (not en passant)",
                    "D": "None of the above"
                },
                "expected": "B",
                "reasoning": "White pawn performed en passant capture"
            })

        # Confuser cases - split between regular capture and no capture
        confuser_regular = n_confuser // 2
        confuser_no_capture = n_confuser - confuser_regular

        # Confuser Type 1: Regular diagonal capture (not en passant)
        for i in range(confuser_regular):
            white_file = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            white_sq = white_file + '5'

            adjacent = self._adjacent_files(white_file)
            if adjacent:
                black_file = random.choice(adjacent)
            else:
                black_file = 'b'

            black_start = black_file + '6'  # Only 1 square away from start
            black_mid = black_file + '5'
            capture_sq = black_file + '5'

            cases.append({
                "case_id": f"en_passant_event_confuser_{i+1}",
                "type": "en_passant_event",
                "subtype": "regular_capture",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_mid: 'p'}, "squares": []},
                    {"pieces": {capture_sq: 'P'}, "squares": []}  # Regular capture
                ],
                "label": "States shown in chronological order",
                "question": "What happened in this sequence?",
                "options": {
                    "A": "Castling",
                    "B": "En passant capture",
                    "C": "Regular capture (not en passant)",
                    "D": "None of the above"
                },
                "expected": "C",
                "reasoning": "Regular diagonal capture, pawn only moved 1 square"
            })

        # Confuser Type 2: No capture (pawn just advanced)
        for i in range(confuser_no_capture):
            white_file = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
            white_sq = white_file + '5'
            white_advanced = white_file + '6'

            adjacent = self._adjacent_files(white_file)
            if adjacent:
                black_file = random.choice(adjacent)
            else:
                black_file = 'b'

            black_start = black_file + '7'
            black_mid = black_file + '5'

            cases.append({
                "case_id": f"en_passant_event_confuser_{confuser_regular + i + 1}",
                "type": "en_passant_event",
                "subtype": "no_capture",
                "states": [
                    {"pieces": {white_sq: 'P', black_start: 'p'}, "squares": []},
                    {"pieces": {white_sq: 'P', black_mid: 'p'}, "squares": []},
                    {"pieces": {white_advanced: 'P', black_mid: 'p'},
                        "squares": []}  # White advanced
                ],
                "label": "States shown in chronological order",
                "question": "What happened in this sequence?",
                "options": {
                    "A": "En passant capture",
                    "B": "Regular capture",
                    "C": "White pawn advanced, no capture",
                    "D": "Castling"
                },
                "expected": "C",
                "reasoning": "White pawn just advanced, no capture occurred"
            })

        return cases

    # ============= Type 2: Castling Event Recognition =============

    def generate_castling_event_tests(self, n_cases: int = 10) -> List[Dict]:
        """
        Generate castling event recognition tests
        2-4 states showing complete castling sequence or confusers
        Multiple choice questions

        Args:
            n_cases: Total number of cases
        """
        cases = []
        n_standard = int(n_cases * 0.7)
        n_confuser = n_cases - n_standard

        # Standard castling cases
        for i in range(n_standard):
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                state_before = {"pieces": {
                    'e1': 'K', 'h1': 'R'}, "squares": []}
                state_after = {"pieces": {'g1': 'K', 'f1': 'R'}, "squares": []}
                options = {
                    "A": "Castling kingside",
                    "B": "Castling queenside",
                    "C": "King and Rook moved separately",
                    "D": "Invalid position"
                }
                expected = "A"
            else:
                state_before = {"pieces": {
                    'e1': 'K', 'a1': 'R'}, "squares": []}
                state_after = {"pieces": {'c1': 'K', 'd1': 'R'}, "squares": []}
                options = {
                    "A": "Castling kingside",
                    "B": "Castling queenside",
                    "C": "King and Rook moved separately",
                    "D": "None of the above"
                }
                expected = "B"

            cases.append({
                "case_id": f"castling_event_pos_{i+1}",
                "type": "castling_event",
                "subtype": side,
                "states": [state_before, state_after],
                "label": "White just moved",
                "question": "What happened?",
                "options": options,
                "expected": expected,
                "reasoning": f"Castling {side} occurred"
            })

        # Confuser cases: Separate moves
        for i in range(n_confuser):
            side = random.choice(['kingside', 'queenside'])

            if side == 'kingside':
                cases.append({
                    "case_id": f"castling_event_confuser_{i+1}",
                    "type": "castling_event",
                    "subtype": "separate_moves",
                    "states": [
                        {"pieces": {'e1': 'K', 'h1': 'R'}, "squares": []},
                        {"pieces": {'f1': 'K', 'h1': 'R'},
                            "squares": []},  # King moved
                        {"pieces": {'g1': 'K', 'h1': 'R'},
                            "squares": []},  # King moved again
                        {"pieces": {'g1': 'K', 'f1': 'R'},
                            "squares": []}   # Rook moved
                    ],
                    "label": "Four states shown in chronological order",
                    "question": "Was this castling?",
                    "options": {
                        "A": "Yes, castling occurred",
                        "B": "No, King and Rook moved separately",
                        "C": "No, only King moved",
                        "D": "Cannot determine"
                    },
                    "expected": "B",
                    "reasoning": "King and Rook moved in separate turns, not castling"
                })
            else:
                cases.append({
                    "case_id": f"castling_event_confuser_{i+1}",
                    "type": "castling_event",
                    "subtype": "separate_moves",
                    "states": [
                        {"pieces": {'e1': 'K', 'a1': 'R'}, "squares": []},
                        {"pieces": {'d1': 'K', 'a1': 'R'},
                            "squares": []},  # King moved
                        {"pieces": {'c1': 'K', 'a1': 'R'},
                            "squares": []},  # King moved again
                        {"pieces": {'c1': 'K', 'd1': 'R'},
                            "squares": []}   # Rook moved
                    ],
                    "label": "Four states shown in chronological order",
                    "question": "Was this castling?",
                    "options": {
                        "A": "Yes, castling occurred",
                        "B": "No, King and Rook moved separately",
                        "C": "No, only King moved",
                        "D": "Cannot determine"
                    },
                    "expected": "B",
                    "reasoning": "Pieces moved separately"
                })

        return cases

    # ============= Type 3: Direct Movement Validation =============

    def generate_direct_movement_tests(self, n_cases: int = 10) -> List[Dict]:
        """
        Generate direct movement validation tests
        Tests: Did piece move directly according to its rules?

        Args:
            n_cases: Total number of cases (distributed across 3 piece types)
        """
        cases = []
        piece_types = ['knight', 'bishop', 'rook']
        cases_per_piece = n_cases // len(piece_types)
        remainder = n_cases % len(piece_types)

        for idx, piece_type in enumerate(piece_types):
            n_piece_cases = cases_per_piece + (1 if idx < remainder else 0)

            # Distribution within each piece type
            n_valid_direct = int(n_piece_cases * 0.5)
            n_valid_not_direct = int(n_piece_cases * 0.3)
            n_invalid = n_piece_cases - n_valid_direct - n_valid_not_direct

            # Generate cases for this piece type
            if piece_type == 'knight':
                cases.extend(self._generate_knight_direct_tests(
                    n_valid_direct, n_valid_not_direct, n_invalid))
            elif piece_type == 'bishop':
                cases.extend(self._generate_bishop_direct_tests(
                    n_valid_direct, n_valid_not_direct, n_invalid))
            else:  # rook
                cases.extend(self._generate_rook_direct_tests(
                    n_valid_direct, n_valid_not_direct, n_invalid))

        return cases

    def _generate_knight_direct_tests(self, n_valid_direct: int, n_valid_not_direct: int, n_invalid: int) -> List[Dict]:
        """Generate direct movement tests for Knight"""
        cases = []
        case_counter = {"valid": 0, "indirect": 0, "invalid": 0}

        # Valid direct moves
        for i in range(n_valid_direct):
            start_sq = self._random_square()
            # Generate valid L-shape move
            end_sq = self._get_knight_move(start_sq)

            if end_sq:
                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["valid"] += 1
                cases.append({
                    "case_id": f"knight_direct_valid_{case_counter['valid']}",
                    "type": "direct_movement",
                    "subtype": "valid_direct",
                    "piece": "knight",
                    "states": [
                        {"pieces": {start_sq: 'N'}, "squares": []},
                        {"pieces": {end_sq: 'N'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "yes",
                    "reasoning": f"Valid L-shape move from {start_sq} to {end_sq}"
                })

        # Valid move but not direct
        for i in range(n_valid_not_direct):
            start_sq = self._random_square()
            # Find a square 2 L-moves away
            intermediate_sq = self._get_knight_move(start_sq)
            if intermediate_sq:
                end_sq = self._get_knight_move(intermediate_sq)
                if end_sq and end_sq != start_sq:
                    question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                    case_counter["indirect"] += 1
                    cases.append({
                        "case_id": f"knight_direct_indirect_{case_counter['indirect']}",
                        "type": "direct_movement",
                        "subtype": "valid_not_direct",
                        "piece": "knight",
                        "states": [
                            {"pieces": {start_sq: 'N'}, "squares": []},
                            {"pieces": {end_sq: 'N'}, "squares": []}
                        ],
                        "label": "There were intermediate moves between these states",
                        "question": question,
                        "expected": "no",
                        "reasoning": f"Knight moved via intermediate square {intermediate_sq}"
                    })

        # Invalid move pattern
        for i in range(n_invalid):
            start_sq = self._random_square()
            f, r = self._square_to_coords(start_sq)

            # Straight line (invalid for knight)
            direction = random.choice(['vertical', 'horizontal'])
            if direction == 'vertical':
                end_sq = self._coords_to_square(f, min(7, r + 2))
            else:
                end_sq = self._coords_to_square(min(7, f + 2), r)

            if end_sq:
                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["invalid"] += 1
                cases.append({
                    "case_id": f"knight_direct_invalid_{case_counter['invalid']}",
                    "type": "direct_movement",
                    "subtype": "invalid_pattern",
                    "piece": "knight",
                    "states": [
                        {"pieces": {start_sq: 'N'}, "squares": []},
                        {"pieces": {end_sq: 'N'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "no",
                    "reasoning": "Knight cannot move in straight line"
                })

        return cases

    def _generate_bishop_direct_tests(self, n_valid_direct: int, n_valid_not_direct: int, n_invalid: int) -> List[Dict]:
        """Generate direct movement tests for Bishop"""
        cases = []
        case_counter = {"valid": 0, "indirect": 0, "invalid": 0}

        # Valid direct moves
        for i in range(n_valid_direct):
            start_sq = self._random_square()
            f, r = self._square_to_coords(start_sq)

            # Generate valid diagonal move (2-4 squares away)
            distance = random.randint(2, 4)
            direction = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            end_f = f + direction[0] * distance
            end_r = r + direction[1] * distance

            if 0 <= end_f < 8 and 0 <= end_r < 8:
                end_sq = self._coords_to_square(end_f, end_r)

                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["valid"] += 1
                cases.append({
                    "case_id": f"bishop_direct_valid_{case_counter['valid']}",
                    "type": "direct_movement",
                    "subtype": "valid_direct",
                    "piece": "bishop",
                    "states": [
                        {"pieces": {start_sq: 'B'}, "squares": []},
                        {"pieces": {end_sq: 'B'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "yes",
                    "reasoning": f"Valid diagonal move from {start_sq} to {end_sq}"
                })

        # Valid but not direct
        for i in range(n_valid_not_direct):
            start_sq = 'c1'
            end_sq = 'f4'

            question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

            case_counter["indirect"] += 1
            cases.append({
                "case_id": f"bishop_direct_indirect_{case_counter['indirect']}",
                "type": "direct_movement",
                "subtype": "valid_not_direct",
                "piece": "bishop",
                "states": [
                    {"pieces": {start_sq: 'B'}, "squares": []},
                    {"pieces": {end_sq: 'B'}, "squares": []}
                ],
                "label": "There were intermediate moves between these states",
                "question": question,
                "expected": "no",
                "reasoning": "Bishop made stops along the diagonal"
            })

        # Invalid pattern
        for i in range(n_invalid):
            start_sq = self._random_square()
            f, r = self._square_to_coords(start_sq)

            # Straight line (invalid for bishop)
            direction = random.choice(['vertical', 'horizontal'])
            if direction == 'vertical':
                end_sq = self._coords_to_square(f, min(7, r + 3))
            else:
                end_sq = self._coords_to_square(min(7, f + 3), r)

            if end_sq:
                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["invalid"] += 1
                cases.append({
                    "case_id": f"bishop_direct_invalid_{case_counter['invalid']}",
                    "type": "direct_movement",
                    "subtype": "invalid_pattern",
                    "piece": "bishop",
                    "states": [
                        {"pieces": {start_sq: 'B'}, "squares": []},
                        {"pieces": {end_sq: 'B'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "no",
                    "reasoning": "Bishop cannot move in straight line"
                })

        return cases

    def _generate_rook_direct_tests(self, n_valid_direct: int, n_valid_not_direct: int, n_invalid: int) -> List[Dict]:
        """Generate direct movement tests for Rook"""
        cases = []
        case_counter = {"valid": 0, "indirect": 0, "invalid": 0}

        # Valid direct moves
        for i in range(n_valid_direct):
            start_sq = self._random_square()
            f, r = self._square_to_coords(start_sq)

            # Generate valid straight move
            if random.choice([True, False]):  # Vertical
                distance = random.randint(2, 5)
                direction = random.choice([1, -1])
                end_r = r + direction * distance
                end_f = f
            else:  # Horizontal
                distance = random.randint(2, 5)
                direction = random.choice([1, -1])
                end_f = f + direction * distance
                end_r = r

            if 0 <= end_f < 8 and 0 <= end_r < 8:
                end_sq = self._coords_to_square(end_f, end_r)

                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["valid"] += 1
                cases.append({
                    "case_id": f"rook_direct_valid_{case_counter['valid']}",
                    "type": "direct_movement",
                    "subtype": "valid_direct",
                    "piece": "rook",
                    "states": [
                        {"pieces": {start_sq: 'R'}, "squares": []},
                        {"pieces": {end_sq: 'R'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "yes",
                    "reasoning": f"Valid straight move from {start_sq} to {end_sq}"
                })

        # Valid but not direct
        for i in range(n_valid_not_direct):
            start_sq = 'a1'
            end_sq = 'a8'

            question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

            case_counter["indirect"] += 1
            cases.append({
                "case_id": f"rook_direct_indirect_{case_counter['indirect']}",
                "type": "direct_movement",
                "subtype": "valid_not_direct",
                "piece": "rook",
                "states": [
                    {"pieces": {start_sq: 'R'}, "squares": []},
                    {"pieces": {end_sq: 'R'}, "squares": []}
                ],
                "label": "There were intermediate moves between these states",
                "question": question,
                "expected": "no",
                "reasoning": "Rook made intermediate moves along the file"
            })

        # Invalid pattern
        for i in range(n_invalid):
            start_sq = self._random_square()
            f, r = self._square_to_coords(start_sq)

            # Diagonal move (invalid for rook)
            end_f = min(7, f + 2)
            end_r = min(7, r + 2)
            end_sq = self._coords_to_square(end_f, end_r)

            if end_sq:
                question = """Can this piece move directly from its State 1 position to its State 2 position according to its chess movement rules?
- Answer 'yes' if this is a valid single move for this piece
- Answer 'no' if this requires multiple moves or violates the piece's rules
- Answer 'unknown' if you cannot determine"""

                case_counter["invalid"] += 1
                cases.append({
                    "case_id": f"rook_direct_invalid_{case_counter['invalid']}",
                    "type": "direct_movement",
                    "subtype": "invalid_pattern",
                    "piece": "rook",
                    "states": [
                        {"pieces": {start_sq: 'R'}, "squares": []},
                        {"pieces": {end_sq: 'R'}, "squares": []}
                    ],
                    "label": "These are consecutive states",
                    "question": question,
                    "expected": "no",
                    "reasoning": "Rook cannot move diagonally"
                })

        return cases

    # ============= Helper Methods =============

    def _get_knight_move(self, square: str) -> str:
        """Get a random valid knight move from square"""
        f, r = self._square_to_coords(square)
        l_moves = [
            (f+2, r+1), (f+2, r-1), (f-2, r+1), (f-2, r-1),
            (f+1, r+2), (f+1, r-2), (f-1, r+2), (f-1, r-2)
        ]
        valid_moves = [(nf, nr)
                       for nf, nr in l_moves if 0 <= nf < 8 and 0 <= nr < 8]

        if valid_moves:
            end_f, end_r = random.choice(valid_moves)
            return self._coords_to_square(end_f, end_r)
        return None

    # ============= Main Generation =============

    def generate_all(self, n_per_type: int = 10) -> List[Dict]:
        """
        Generate comprehensive Temporal Test 1 suite

        Args:
            n_per_type: Number of cases per main type

        Returns:
            List of test case dictionaries
        """
        all_cases = []

        print(f"Generating En Passant rule tests...")
        en_passant_cases = self.generate_en_passant_rule_tests(n_per_type)
        all_cases.extend(en_passant_cases)
        print(f"  Generated {len(en_passant_cases)} en passant rule cases")

        print(f"Generating Castling rule tests...")
        castling_cases = self.generate_castling_rule_tests(n_per_type)
        all_cases.extend(castling_cases)
        print(f"  Generated {len(castling_cases)} castling rule cases")

        print(f"Generating En Passant event recognition tests...")
        en_passant_event_cases = self.generate_en_passant_event_tests(
            n_per_type)
        all_cases.extend(en_passant_event_cases)
        print(
            f"  Generated {len(en_passant_event_cases)} en passant event cases")

        print(f"Generating Castling event recognition tests...")
        castling_event_cases = self.generate_castling_event_tests(n_per_type)
        all_cases.extend(castling_event_cases)
        print(f"  Generated {len(castling_event_cases)} castling event cases")

        print(f"Generating Direct Movement validation tests...")
        direct_movement_cases = self.generate_direct_movement_tests(n_per_type)
        all_cases.extend(direct_movement_cases)
        print(
            f"  Generated {len(direct_movement_cases)} direct movement cases")

        print(f"\n✓ Total generated: {len(all_cases)} test cases")

        return all_cases
