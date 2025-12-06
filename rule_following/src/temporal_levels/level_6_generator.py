"""
Level 6 Generator: Castling + 3 Check Rules (修改版)
测试王车易位的所有3条将军约束
包含有效和无效案例，迫使模型检查所有条件
"""

import random
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict


class Level6Generator:
    """Generate Level 6 test cases - castling with all 3 check rules"""

    PIECE_LIMITS = {
        'king': 1,
        'queen': 1,
        'rook': 2,
        'bishop': 2,
        'knight': 2
    }

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8']

        self.castling_configs = {
            'white_kingside': {
                'king_start': 'e1', 'king_end': 'g1',
                'rook_start': 'h1', 'rook_end': 'f1',
                'in_sq': 'e1', 'through_sq': 'f1', 'into_sq': 'g1',
                'color': 'white',
                'king_symbol': 'K', 'rook_symbol': 'R',
                'path_squares': ['f1', 'g1']
            },
            'white_queenside': {
                'king_start': 'e1', 'king_end': 'c1',
                'rook_start': 'a1', 'rook_end': 'd1',
                'in_sq': 'e1', 'through_sq': 'd1', 'into_sq': 'c1',
                'color': 'white',
                'king_symbol': 'K', 'rook_symbol': 'R',
                'path_squares': ['b1', 'c1', 'd1']
            },
            'black_kingside': {
                'king_start': 'e8', 'king_end': 'g8',
                'rook_start': 'h8', 'rook_end': 'f8',
                'in_sq': 'e8', 'through_sq': 'f8', 'into_sq': 'g8',
                'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['f8', 'g8']
            },
            'black_queenside': {
                'king_start': 'e8', 'king_end': 'c8',
                'rook_start': 'a8', 'rook_end': 'd8',
                'in_sq': 'e8', 'through_sq': 'd8', 'into_sq': 'c8',
                'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['b8', 'c8', 'd8']
            }
        }

        # 7种违规组合
        self.violation_combinations = [
            ['in'],
            ['through'],
            ['into'],
            ['in', 'through'],
            ['in', 'into'],
            ['through', 'into'],
            ['in', 'through', 'into']
        ]

    def _random_square(self) -> str:
        return random.choice(self.files) + random.choice(self.ranks)

    def _square_to_coords(self, square: str) -> Tuple[int, int]:
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        return (file, rank)

    def _coords_to_square(self, file: int, rank: int) -> Optional[str]:
        if 0 <= file < 8 and 0 <= rank < 8:
            return chr(ord('a') + file) + str(rank + 1)
        return None

    def _can_add_piece(self, piece_type: str, color: str, piece_counts: Dict) -> bool:
        key = (piece_type, color)
        current = piece_counts.get(key, 0)
        limit = self.PIECE_LIMITS.get(piece_type, 2)
        return current < limit

    def _add_piece_to_counts(self, piece_type: str, color: str, piece_counts: Dict):
        key = (piece_type, color)
        piece_counts[key] = piece_counts.get(key, 0) + 1

    def _get_attacker_symbol(self, attacker_type: str, color: str) -> str:
        symbols = {
            ('rook', 'white'): 'R', ('rook', 'black'): 'r',
            ('bishop', 'white'): 'B', ('bishop', 'black'): 'b',
            ('knight', 'white'): 'N', ('knight', 'black'): 'n',
            ('queen', 'white'): 'Q', ('queen', 'black'): 'q'
        }
        return symbols.get((attacker_type, color), 'p')

    def _get_path_squares(self, from_sq: str, to_sq: str) -> List[str]:
        """获取两点之间的所有格子（不包含端点）"""
        from_f, from_r = self._square_to_coords(from_sq)
        to_f, to_r = self._square_to_coords(to_sq)

        df = to_f - from_f
        dr = to_r - from_r

        step_f = 0 if df == 0 else (1 if df > 0 else -1)
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)

        if not ((df == 0 and dr != 0) or (dr == 0 and df != 0) or (abs(df) == abs(dr) and df != 0)):
            return []

        path = []
        curr_f, curr_r = from_f + step_f, from_r + step_r

        while (curr_f, curr_r) != (to_f, to_r):
            sq = self._coords_to_square(curr_f, curr_r)
            if sq:
                path.append(sq)
            curr_f += step_f
            curr_r += step_r

        return path

    def _is_path_clear(self, from_sq: str, to_sq: str, occupied: Set[str]) -> bool:
        path_squares = self._get_path_squares(from_sq, to_sq)
        for sq in path_squares:
            if sq in occupied:
                return False
        return True

    def _can_attack(self, from_sq: str, to_sq: str, piece_type: str) -> bool:
        """检查棋子几何上是否能攻击目标"""
        from_f, from_r = self._square_to_coords(from_sq)
        to_f, to_r = self._square_to_coords(to_sq)

        df = abs(to_f - from_f)
        dr = abs(to_r - from_r)

        if piece_type == 'rook':
            return (df == 0 and dr > 0) or (dr == 0 and df > 0)
        elif piece_type == 'bishop':
            return df == dr and df > 0
        elif piece_type == 'queen':
            return (df == 0 and dr > 0) or (dr == 0 and df > 0) or (df == dr and df > 0)
        elif piece_type == 'knight':
            return (df == 2 and dr == 1) or (df == 1 and dr == 2)
        return False

    def _can_attack_with_clear_path(self, from_sq: str, to_sq: str,
                                    piece_type: str, occupied: Set[str]) -> bool:
        """检查棋子是否能攻击目标（考虑路径阻挡）"""
        if not self._can_attack(from_sq, to_sq, piece_type):
            return False
        if piece_type == 'knight':
            return True
        return self._is_path_clear(from_sq, to_sq, occupied)

    def _get_attacker_positions(self, target_sq: str, attacker_type: str,
                                forbidden: Set[str], occupied: Set[str]) -> List[str]:
        """获取攻击者可以攻击目标的所有位置"""
        target_f, target_r = self._square_to_coords(target_sq)
        positions = []

        if attacker_type == 'rook' or attacker_type == 'queen':
            for f in range(8):
                if f != target_f:
                    sq = self._coords_to_square(f, target_r)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, target_sq, occupied):
                            positions.append(sq)
            for r in range(8):
                if r != target_r:
                    sq = self._coords_to_square(target_f, r)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, target_sq, occupied):
                            positions.append(sq)

        if attacker_type == 'bishop' or attacker_type == 'queen':
            for d in range(1, 8):
                for df, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    sq = self._coords_to_square(
                        target_f + df * d, target_r + dr * d)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, target_sq, occupied):
                            positions.append(sq)

        if attacker_type == 'knight':
            for df, dr in [(2, 1), (2, -1), (-2, 1), (-2, -1),
                           (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                sq = self._coords_to_square(target_f + df, target_r + dr)
                if sq and sq not in forbidden:
                    positions.append(sq)

        return positions

    def _get_non_attacking_square(self, critical_squares: List[str],
                                  forbidden: Set[str], piece_type: str,
                                  occupied: Set[str]) -> Optional[str]:
        """获取一个不攻击任何关键格子的位置"""
        for _ in range(100):
            sq = self._random_square()
            if sq in forbidden:
                continue

            attacks_critical = False
            for critical_sq in critical_squares:
                if self._can_attack_with_clear_path(sq, critical_sq, piece_type, occupied):
                    attacks_critical = True
                    break

            if not attacks_critical:
                return sq
        return None

    # ========== 新增：有效案例生成 ==========

    def _generate_valid_case(self, case_num: int) -> Optional[Dict]:
        """
        生成有效的王车易位案例
        所有3条规则都必须满足：
        1. 王不在将军中 (in_sq 不被攻击)
        2. 王经过的格子不被攻击 (through_sq 不被攻击)
        3. 王到达的格子不被攻击 (into_sq 不被攻击)
        """
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        # 所有3个关键格子都不能被攻击
        critical_squares = [config['in_sq'],
                            config['through_sq'], config['into_sq']]

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        extra_pieces = {}

        # 添加2-3个额外棋子，但都不能攻击关键格子
        n_extra = random.randint(2, 3)
        for _ in range(n_extra):
            for attempt in range(50):
                piece_type = random.choice(
                    ['knight', 'bishop', 'rook', 'queen'])
                piece_color = random.choice(['white', 'black'])

                if not self._can_add_piece(piece_type, piece_color, piece_counts):
                    continue

                # 找一个不攻击任何关键格子的位置
                sq = self._get_non_attacking_square(
                    critical_squares, forbidden, piece_type, occupied
                )

                if sq:
                    symbol = self._get_attacker_symbol(piece_type, piece_color)
                    extra_pieces[sq] = symbol
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(
                        piece_type, piece_color, piece_counts)
                    break

        # 最终验证：确保没有棋子攻击关键格子
        for sq, symbol in extra_pieces.items():
            piece_type = self._symbol_to_type(symbol)
            for critical_sq in critical_squares:
                if self._can_attack_with_clear_path(sq, critical_sq, piece_type, occupied - {sq}):
                    return None  # 验证失败，重新生成

        state1_pieces = {
            config['king_start']: config['king_symbol'],
            config['rook_start']: config['rook_symbol'],
            **extra_pieces
        }

        state2_pieces = {
            config['king_end']: config['king_symbol'],
            config['rook_end']: config['rook_symbol'],
            **extra_pieces
        }

        return {
            "case_id": f"L6_{castling_type}_valid_{case_num}",
            "type": "castling_full_constraints",
            "subtype": "valid",
            "castling_type": castling_type,
            "rules_checked": ['in', 'through', 'into'],  # 所有3条规则都检查
            "violation_details": {
                'in_check': False,
                'through_check': False,
                'into_check': False
            },
            "states": [
                {"pieces": state1_pieces, "squares": []},
                {"pieces": state2_pieces, "squares": []}
            ],
            "question": "Is this castling move legal?",
            "expected": "yes",
            "reasoning": "All 3 check rules satisfied: king not in check, doesn't pass through check, doesn't end in check"
        }

    def _symbol_to_type(self, symbol: str) -> str:
        """符号转棋子类型"""
        type_map = {
            'R': 'rook', 'r': 'rook',
            'B': 'bishop', 'b': 'bishop',
            'N': 'knight', 'n': 'knight',
            'Q': 'queen', 'q': 'queen',
            'K': 'king', 'k': 'king',
            'P': 'pawn', 'p': 'pawn'
        }
        return type_map.get(symbol, 'pawn')

    def _generate_invalid_case(self, case_num: int, violations: List[str]) -> Optional[Dict]:
        """生成无效的王车易位案例（原有逻辑）"""
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        attacker_color = 'black' if config['color'] == 'white' else 'white'

        target_map = {
            'in': config['in_sq'],
            'through': config['through_sq'],
            'into': config['into_sq']
        }

        violation_details = {
            'in_check': 'in' in violations,
            'through_check': 'through' in violations,
            'into_check': 'into' in violations
        }

        extra_pieces = {}
        attacker_positions = {}

        # 放置攻击者
        for violation in violations:
            target_sq = target_map[violation]
            placed = False
            piece_order = ['knight', 'rook', 'bishop', 'queen']
            random.shuffle(piece_order)

            for attacker_type in piece_order:
                if placed:
                    break

                if not self._can_add_piece(attacker_type, attacker_color, piece_counts):
                    continue

                positions = self._get_attacker_positions(
                    target_sq, attacker_type, forbidden, occupied
                )

                if positions:
                    random.shuffle(positions)
                    for pos in positions:
                        test_occupied = occupied | {pos}
                        if self._can_attack_with_clear_path(pos, target_sq, attacker_type,
                                                            test_occupied - {pos}):
                            symbol = self._get_attacker_symbol(
                                attacker_type, attacker_color)
                            extra_pieces[pos] = symbol
                            attacker_positions[pos] = (
                                target_sq, attacker_type)
                            forbidden.add(pos)
                            occupied.add(pos)
                            self._add_piece_to_counts(
                                attacker_type, attacker_color, piece_counts)
                            placed = True
                            break

            if not placed:
                return None

        # 填充非攻击棋子
        all_critical = [config['in_sq'],
                        config['through_sq'], config['into_sq']]
        non_violated_squares = [target_map[v] for v in [
            'in', 'through', 'into'] if v not in violations]

        while len(extra_pieces) < 3:
            placed = False
            for _ in range(50):
                piece_type = random.choice(['knight', 'bishop'])
                piece_color = random.choice(['white', 'black'])

                if not self._can_add_piece(piece_type, piece_color, piece_counts):
                    continue

                sq = self._get_non_attacking_square(
                    non_violated_squares, forbidden, piece_type, occupied
                )

                if sq:
                    blocks_attacker = False
                    for attacker_pos, (target_sq, attacker_type) in attacker_positions.items():
                        if attacker_type != 'knight':
                            path = self._get_path_squares(
                                attacker_pos, target_sq)
                            if sq in path:
                                blocks_attacker = True
                                break

                    if not blocks_attacker:
                        symbol = self._get_attacker_symbol(
                            piece_type, piece_color)
                        extra_pieces[sq] = symbol
                        forbidden.add(sq)
                        occupied.add(sq)
                        self._add_piece_to_counts(
                            piece_type, piece_color, piece_counts)
                        placed = True
                        break

            if not placed:
                break

        # 最终验证
        for attacker_pos, (target_sq, attacker_type) in attacker_positions.items():
            check_occupied = occupied - {attacker_pos}
            if not self._can_attack_with_clear_path(attacker_pos, target_sq, attacker_type, check_occupied):
                return None

        state1_pieces = {
            config['king_start']: config['king_symbol'],
            config['rook_start']: config['rook_symbol'],
            **extra_pieces
        }

        state2_pieces = {
            config['king_end']: config['king_symbol'],
            config['rook_end']: config['rook_symbol'],
            **extra_pieces
        }

        violated_rules = [k for k, v in violation_details.items() if v]
        reasoning = f"Violates: {', '.join(violated_rules)}"

        return {
            "case_id": f"L6_{castling_type}_invalid_{case_num}",
            "type": "castling_full_constraints",
            "subtype": "invalid",
            "castling_type": castling_type,
            "rules_violated": len(violations),
            "violation_details": violation_details,
            "states": [
                {"pieces": state1_pieces, "squares": []},
                {"pieces": state2_pieces, "squares": []}
            ],
            "question": "Is this castling move legal?",
            "expected": "no",
            "reasoning": reasoning
        }

    def generate_all(self, n_cases: int = 100, valid_ratio: float = 1.00) -> List[Dict]:
        """
        生成所有 Level 6 测试案例

        Args:
            n_cases: 总案例数
            valid_ratio: 有效案例比例
        """
        all_cases = []

        # 计算有效和无效案例数量
        n_valid = int(n_cases * valid_ratio)
        n_invalid = n_cases - n_valid

        # ========== 生成有效案例 ==========
        print(
            f"Generating {n_valid} VALID castling cases (all 3 rules must be checked)...")

        valid_generated = 0
        valid_attempts = 0
        max_valid_attempts = n_valid * 20

        while valid_generated < n_valid and valid_attempts < max_valid_attempts:
            valid_attempts += 1
            case = self._generate_valid_case(valid_generated + 1)
            if case:
                all_cases.append(case)
                valid_generated += 1

        print(f"  ✓ Generated {valid_generated} valid cases")

        # ========== 生成无效案例 ==========
        print(
            f"Generating {n_invalid} INVALID castling cases (7 violation combinations)...")

        cases_per_combo = n_invalid // 7
        remainder = n_invalid % 7

        invalid_counter = 0
        for combo_idx, violations in enumerate(self.violation_combinations):
            n_combo_cases = cases_per_combo + \
                (1 if combo_idx < remainder else 0)
            combo_name = '+'.join(violations)

            generated = 0
            attempts = 0
            max_attempts = n_combo_cases * 10

            while generated < n_combo_cases and attempts < max_attempts:
                attempts += 1
                case = self._generate_invalid_case(
                    invalid_counter + 1, violations)
                if case:
                    all_cases.append(case)
                    invalid_counter += 1
                    generated += 1

            print(f"  ✓ [{combo_name}]: {generated} cases")

        # ========== 打乱顺序 ==========
        random.shuffle(all_cases)

        # ========== 统计 ==========
        stats = defaultdict(int)
        for case in all_cases:
            if case['subtype'] == 'valid':
                stats['valid'] += 1
            else:
                stats[case['rules_violated']] += 1

        print(f"\n✓ Total generated: {len(all_cases)} Level 6 test cases")
        print(
            f"  Valid: {stats['valid']} ({stats['valid']/len(all_cases)*100:.1f}%)")
        print(
            f"  Invalid: {len(all_cases) - stats['valid']} ({(len(all_cases) - stats['valid'])/len(all_cases)*100:.1f}%)")
        print(f"  By rules violated:")
        for n_rules in [1, 2, 3]:
            if stats[n_rules] > 0:
                print(
                    f"    {n_rules} rule(s): {stats[n_rules]} ({stats[n_rules]/len(all_cases)*100:.1f}%)")

        return all_cases
