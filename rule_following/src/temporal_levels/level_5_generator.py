"""
Level 5 Generator: Castling + 2 Check Rules (Enhanced)
增加干扰项：
1. "看似攻击但被阻挡"的棋子
2. 更复杂的棋盘布局
"""

import random
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict


class Level5Generator:
    """Generate Level 5 test cases - castling with 2 check rules (enhanced)"""

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
                'through_sq': 'f1', 'color': 'white',
                'king_symbol': 'K', 'rook_symbol': 'R',
                'path_squares': ['f1', 'g1']
            },
            'white_queenside': {
                'king_start': 'e1', 'king_end': 'c1',
                'rook_start': 'a1', 'rook_end': 'd1',
                'through_sq': 'd1', 'color': 'white',
                'king_symbol': 'K', 'rook_symbol': 'R',
                'path_squares': ['b1', 'c1', 'd1']
            },
            'black_kingside': {
                'king_start': 'e8', 'king_end': 'g8',
                'rook_start': 'h8', 'rook_end': 'f8',
                'through_sq': 'f8', 'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['f8', 'g8']
            },
            'black_queenside': {
                'king_start': 'e8', 'king_end': 'c8',
                'rook_start': 'a8', 'rook_end': 'd8',
                'through_sq': 'd8', 'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['b8', 'c8', 'd8']
            }
        }

        self.check_combinations = [
            ['in', 'through'],
            ['in', 'into'],
            ['through', 'into']
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

    # ========== 新增：路径相关函数 ==========

    def _get_path_squares(self, from_sq: str, to_sq: str) -> List[str]:
        """获取两点之间的所有格子（不包含端点）"""
        from_f, from_r = self._square_to_coords(from_sq)
        to_f, to_r = self._square_to_coords(to_sq)

        df = to_f - from_f
        dr = to_r - from_r

        # 计算步进方向
        step_f = 0 if df == 0 else (1 if df > 0 else -1)
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)

        # 检查是否是有效的直线/对角线
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
        """检查路径是否畅通"""
        path_squares = self._get_path_squares(from_sq, to_sq)
        for sq in path_squares:
            if sq in occupied:
                return False
        return True

    def _can_attack(self, from_sq: str, to_sq: str, piece_type: str) -> bool:
        """检查棋子几何上是否能攻击目标（不考虑阻挡）"""
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
        # 马不受阻挡
        if piece_type == 'knight':
            return True
        return self._is_path_clear(from_sq, to_sq, occupied)

    def _get_attacker_positions_with_clear_path(self, target_sq: str, attacker_type: str,
                                                forbidden: Set[str], occupied: Set[str]) -> List[str]:
        """获取可以实际攻击目标的位置（路径畅通）"""
        target_f, target_r = self._square_to_coords(target_sq)
        positions = []

        if attacker_type in ['rook', 'queen']:
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

        if attacker_type in ['bishop', 'queen']:
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

    # ========== 新增：干扰棋子生成 ==========

    def _place_blocked_attacker(self, target_sq: str, forbidden: Set[str],
                                occupied: Set[str], piece_counts: Dict,
                                attacker_color: str) -> Optional[Tuple[str, str, str, str]]:
        """
        放置一个"看似攻击但被阻挡"的棋子
        返回: (attacker_sq, attacker_symbol, blocker_sq, blocker_symbol) 或 None
        """
        # 只用车、象、后（马不能被阻挡）
        for _ in range(50):
            attacker_type = random.choice(['rook', 'bishop', 'queen'])

            if not self._can_add_piece(attacker_type, attacker_color, piece_counts):
                continue

            target_f, target_r = self._square_to_coords(target_sq)

            # 找一个几何上能攻击但需要路径的位置
            candidate_positions = []

            if attacker_type in ['rook', 'queen']:
                # 水平方向，距离 >= 2
                for f in range(8):
                    if abs(f - target_f) >= 2:
                        sq = self._coords_to_square(f, target_r)
                        if sq and sq not in forbidden and sq not in occupied:
                            candidate_positions.append((sq, 'horizontal'))
                # 垂直方向
                for r in range(8):
                    if abs(r - target_r) >= 2:
                        sq = self._coords_to_square(target_f, r)
                        if sq and sq not in forbidden and sq not in occupied:
                            candidate_positions.append((sq, 'vertical'))

            if attacker_type in ['bishop', 'queen']:
                # 对角线方向，距离 >= 2
                for d in range(2, 8):
                    for df, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        sq = self._coords_to_square(
                            target_f + df * d, target_r + dr * d)
                        if sq and sq not in forbidden and sq not in occupied:
                            candidate_positions.append((sq, 'diagonal'))

            if not candidate_positions:
                continue

            random.shuffle(candidate_positions)

            for attacker_sq, direction in candidate_positions:
                # 获取攻击路径上的格子
                path = self._get_path_squares(attacker_sq, target_sq)
                if not path:
                    continue

                # 选择一个路径上的格子放置阻挡棋子
                valid_blocker_squares = [
                    sq for sq in path if sq not in forbidden and sq not in occupied]
                if not valid_blocker_squares:
                    continue

                blocker_sq = random.choice(valid_blocker_squares)

                # 阻挡棋子可以是任意颜色的马或兵
                blocker_color = random.choice(['white', 'black'])
                blocker_type = random.choice(['knight', 'pawn'])

                if not self._can_add_piece(blocker_type, blocker_color, piece_counts):
                    blocker_type = 'pawn' if blocker_type == 'knight' else 'knight'
                    if not self._can_add_piece(blocker_type, blocker_color, piece_counts):
                        continue

                attacker_symbol = self._get_attacker_symbol(
                    attacker_type, attacker_color)
                if blocker_type == 'knight':
                    blocker_symbol = 'N' if blocker_color == 'white' else 'n'
                else:
                    blocker_symbol = 'P' if blocker_color == 'white' else 'p'

                return (attacker_sq, attacker_symbol, blocker_sq, blocker_symbol,
                        attacker_type, attacker_color, blocker_type, blocker_color)

        return None

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

    # ========== 有效案例生成 ==========

    def _generate_valid_case(self, case_num: int) -> Optional[Dict]:
        """生成有效的易位案例（添加被阻挡的干扰攻击者）"""
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]
        check_combo = random.choice(self.check_combinations)

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        critical_squares = [config['king_start'],
                            config['through_sq'], config['king_end']]

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        extra_pieces = {}
        attacker_color = 'black' if config['color'] == 'white' else 'white'

        # ===== 新增：添加 1-2 个"看似攻击但被阻挡"的干扰棋子 =====
        n_blocked_attackers = random.randint(1, 2)
        blocked_attacker_info = []

        for _ in range(n_blocked_attackers):
            # 选择一个关键格子作为"虚假目标"
            fake_target = random.choice(critical_squares)

            result = self._place_blocked_attacker(
                fake_target, forbidden, occupied, piece_counts, attacker_color
            )

            if result:
                (attacker_sq, attacker_symbol, blocker_sq, blocker_symbol,
                 attacker_type, att_color, blocker_type, blk_color) = result

                extra_pieces[attacker_sq] = attacker_symbol
                extra_pieces[blocker_sq] = blocker_symbol
                forbidden.add(attacker_sq)
                forbidden.add(blocker_sq)
                occupied.add(attacker_sq)
                occupied.add(blocker_sq)
                self._add_piece_to_counts(
                    attacker_type, att_color, piece_counts)
                self._add_piece_to_counts(
                    blocker_type, blk_color, piece_counts)
                blocked_attacker_info.append({
                    'attacker': attacker_sq,
                    'blocker': blocker_sq,
                    'target': fake_target
                })

        # 添加一些普通的非攻击棋子填充
        while len(extra_pieces) < 4:
            for _ in range(50):
                piece_type = random.choice(['knight', 'bishop'])
                piece_color = random.choice(['white', 'black'])

                if not self._can_add_piece(piece_type, piece_color, piece_counts):
                    continue

                sq = self._get_non_attacking_square(
                    critical_squares, forbidden, piece_type, occupied)
                if sq:
                    symbol = self._get_attacker_symbol(piece_type, piece_color)
                    extra_pieces[sq] = symbol
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(
                        piece_type, piece_color, piece_counts)
                    break
            else:
                break

        # 最终验证：确保没有棋子实际攻击关键格子
        for sq, symbol in extra_pieces.items():
            piece_type = self._symbol_to_type(symbol)
            for critical_sq in critical_squares:
                test_occupied = occupied - {sq}
                if self._can_attack_with_clear_path(sq, critical_sq, piece_type, test_occupied):
                    return None  # 验证失败

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

        reasoning = "All castling conditions met"
        if blocked_attacker_info:
            blocked_desc = [f"piece at {info['attacker']} is blocked by {info['blocker']}"
                            for info in blocked_attacker_info]
            reasoning += f" (Note: {'; '.join(blocked_desc)})"

        return {
            "case_id": f"L5_valid_{case_num}",
            "type": "castling_with_constraints",
            "subtype": "valid",
            "castling_type": castling_type,
            "check_rules_tested": check_combo,
            "has_blocked_attackers": len(blocked_attacker_info) > 0,
            "states": [
                {"pieces": state1_pieces, "squares": []},
                {"pieces": state2_pieces, "squares": []}
            ],
            "question": "Is this castling move legal?",
            "expected": "yes",
            "reasoning": reasoning
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

    # ========== 无效案例生成 ==========

    def _generate_invalid_case(self, case_num: int, check_combo: List[str],
                               violation_type: str) -> Optional[Dict]:
        """生成无效案例（真实攻击者 + 被阻挡的干扰攻击者）"""
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        # 确定攻击目标
        attack_targets = []
        violation_details = []

        if violation_type == 'first' or violation_type == 'both':
            rule = check_combo[0]
            if rule == 'in':
                attack_targets.append(config['king_start'])
                violation_details.append('in_check')
            elif rule == 'through':
                attack_targets.append(config['through_sq'])
                violation_details.append('through_check')
            elif rule == 'into':
                attack_targets.append(config['king_end'])
                violation_details.append('into_check')

        if violation_type == 'second' or violation_type == 'both':
            rule = check_combo[1]
            if rule == 'in':
                attack_targets.append(config['king_start'])
                violation_details.append('in_check')
            elif rule == 'through':
                attack_targets.append(config['through_sq'])
                violation_details.append('through_check')
            elif rule == 'into':
                attack_targets.append(config['king_end'])
                violation_details.append('into_check')

        attack_targets = list(set(attack_targets))
        violation_details = list(set(violation_details))

        attacker_color = 'black' if config['color'] == 'white' else 'white'

        extra_pieces = {}
        real_attacker_positions = {}  # 记录真实攻击者位置

        # ===== 放置真实攻击者 =====
        for target in attack_targets:
            placed = False
            for _ in range(50):
                attacker_type = random.choice(
                    ['rook', 'bishop', 'knight', 'queen'])

                if not self._can_add_piece(attacker_type, attacker_color, piece_counts):
                    continue

                positions = self._get_attacker_positions_with_clear_path(
                    target, attacker_type, forbidden, occupied
                )
                if positions:
                    pos = random.choice(positions)
                    symbol = self._get_attacker_symbol(
                        attacker_type, attacker_color)
                    extra_pieces[pos] = symbol
                    real_attacker_positions[pos] = (target, attacker_type)
                    forbidden.add(pos)
                    occupied.add(pos)
                    self._add_piece_to_counts(
                        attacker_type, attacker_color, piece_counts)
                    placed = True
                    break

            if not placed:
                return None

        # ===== 新增：添加 1-2 个"看似攻击但被阻挡"的干扰棋子 =====
        # 选择一个没有被真实攻击的关键格子作为虚假目标
        all_critical = [config['king_start'],
                        config['through_sq'], config['king_end']]
        non_targeted = [sq for sq in all_critical if sq not in attack_targets]

        n_blocked_attackers = random.randint(1, 2)

        for _ in range(n_blocked_attackers):
            if not non_targeted:
                break

            fake_target = random.choice(non_targeted)

            result = self._place_blocked_attacker(
                fake_target, forbidden, occupied, piece_counts, attacker_color
            )

            if result:
                (attacker_sq, attacker_symbol, blocker_sq, blocker_symbol,
                 attacker_type, att_color, blocker_type, blk_color) = result

                # 确保阻挡棋子不会阻挡真实攻击者的路径
                blocks_real_attacker = False
                for real_pos, (real_target, real_type) in real_attacker_positions.items():
                    if real_type != 'knight':
                        path = self._get_path_squares(real_pos, real_target)
                        if blocker_sq in path or attacker_sq in path:
                            blocks_real_attacker = True
                            break

                if not blocks_real_attacker:
                    extra_pieces[attacker_sq] = attacker_symbol
                    extra_pieces[blocker_sq] = blocker_symbol
                    forbidden.add(attacker_sq)
                    forbidden.add(blocker_sq)
                    occupied.add(attacker_sq)
                    occupied.add(blocker_sq)
                    self._add_piece_to_counts(
                        attacker_type, att_color, piece_counts)
                    self._add_piece_to_counts(
                        blocker_type, blk_color, piece_counts)

        # 填充普通棋子
        while len(extra_pieces) < 5:
            placed = False
            for _ in range(50):
                piece_type = random.choice(['knight', 'bishop'])
                piece_color = random.choice(['white', 'black'])

                if not self._can_add_piece(piece_type, piece_color, piece_counts):
                    continue

                non_target_critical = [
                    sq for sq in all_critical if sq not in attack_targets]
                sq = self._get_non_attacking_square(
                    non_target_critical, forbidden, piece_type, occupied)

                if sq:
                    # 确保不阻挡真实攻击者
                    blocks_real = False
                    for real_pos, (real_target, real_type) in real_attacker_positions.items():
                        if real_type != 'knight':
                            path = self._get_path_squares(
                                real_pos, real_target)
                            if sq in path:
                                blocks_real = True
                                break

                    if not blocks_real:
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

        # 最终验证：确保真实攻击者仍然能攻击目标
        for real_pos, (real_target, real_type) in real_attacker_positions.items():
            test_occupied = occupied - {real_pos}
            if not self._can_attack_with_clear_path(real_pos, real_target, real_type, test_occupied):
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

        reasoning = f"Violates: {', '.join(violation_details)}"

        return {
            "case_id": f"L5_invalid_{case_num}",
            "type": "castling_with_constraints",
            "subtype": "invalid",
            "castling_type": castling_type,
            "check_rules_tested": check_combo,
            "violation_details": violation_details,
            "states": [
                {"pieces": state1_pieces, "squares": []},
                {"pieces": state2_pieces, "squares": []}
            ],
            "question": "Is this castling move legal?",
            "expected": "no",
            "reasoning": reasoning
        }

    def generate_all(self, n_cases: int = 100) -> List[Dict]:
        """生成所有 Level 5 测试案例"""
        all_cases = []

        n_valid = int(n_cases * 0.20)
        n_invalid = n_cases - n_valid

        print(f"Generating valid castling cases (with blocked attackers as distractors)...")

        valid_generated = 0
        valid_attempts = 0
        max_valid_attempts = n_valid * 10

        while valid_generated < n_valid and valid_attempts < max_valid_attempts:
            valid_attempts += 1
            case = self._generate_valid_case(valid_generated + 1)
            if case:
                all_cases.append(case)
                valid_generated += 1

        print(f"  ✓ Generated {valid_generated} valid cases")

        print(f"Generating invalid castling cases...")

        cases_per_combo = n_invalid // 3
        remainder = n_invalid % 3

        invalid_count = 0
        for combo_idx, check_combo in enumerate(self.check_combinations):
            n_combo_cases = cases_per_combo + \
                (1 if combo_idx < remainder else 0)

            n_first = n_combo_cases // 3
            n_second = n_combo_cases // 3
            n_both = n_combo_cases - n_first - n_second

            combo_name = f"[{check_combo[0]}, {check_combo[1]}]"

            for i in range(n_first):
                for _ in range(10):
                    case = self._generate_invalid_case(
                        invalid_count + 1, check_combo, 'first')
                    if case:
                        all_cases.append(case)
                        invalid_count += 1
                        break

            for i in range(n_second):
                for _ in range(10):
                    case = self._generate_invalid_case(
                        invalid_count + 1, check_combo, 'second')
                    if case:
                        all_cases.append(case)
                        invalid_count += 1
                        break

            for i in range(n_both):
                for _ in range(10):
                    case = self._generate_invalid_case(
                        invalid_count + 1, check_combo, 'both')
                    if case:
                        all_cases.append(case)
                        invalid_count += 1
                        break

            print(f"  ✓ Generated cases for combo {combo_name}")

        # 统计有多少案例包含被阻挡的攻击者
        n_with_blocked = sum(1 for c in all_cases if c.get(
            'has_blocked_attackers', False))

        print(f"\n✓ Total generated: {len(all_cases)} Level 5 test cases")
        print(
            f"  Valid: {valid_generated} ({valid_generated/len(all_cases)*100:.1f}%)")
        print(
            f"  Invalid: {invalid_count} ({invalid_count/len(all_cases)*100:.1f}%)")
        print(f"  With blocked attackers (distractors): {n_with_blocked}")

        return all_cases
