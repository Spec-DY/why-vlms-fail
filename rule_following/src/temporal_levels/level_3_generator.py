"""
Level 3 Generator: En Passant Basic (Temporal Version)
测试吃过路兵的3个基本条件：
1. 被吃的兵从起始位置出发
2. 被吃的兵双步移动
3. 两个兵相邻

增加时序追踪要素：
- 干扰棋子移动
- 多个兵的混淆
"""

import random
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict


class Level3Generator:
    """Generate Level 3 test cases - en passant with temporal tracking"""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8']

    def _adjacent_files(self, file: str) -> List[str]:
        """Get adjacent files"""
        file_idx = self.files.index(file)
        adjacent = []
        if file_idx > 0:
            adjacent.append(self.files[file_idx - 1])
        if file_idx < 7:
            adjacent.append(self.files[file_idx + 1])
        return adjacent

    def _get_knight_moves(self, square: str, forbidden: Set[str]) -> List[str]:
        """获取骑士的所有合法移动目标"""
        f = ord(square[0]) - ord('a')
        r = int(square[1]) - 1
        moves = []
        for df, dr in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            new_f, new_r = f + df, r + dr
            if 0 <= new_f < 8 and 0 <= new_r < 8:
                sq = chr(ord('a') + new_f) + str(new_r + 1)
                if sq not in forbidden:
                    moves.append(sq)
        return moves

    def _get_safe_knight_position(self, forbidden: Set[str]) -> Optional[str]:
        """找一个安全的骑士位置"""
        for _ in range(100):
            f = random.choice(self.files)
            r = random.choice(self.ranks)
            sq = f + r
            if sq not in forbidden:
                # 确保骑士有地方可以移动
                moves = self._get_knight_moves(sq, forbidden)
                if moves:
                    return sq
        return None

    # ==================== VALID: ALL CONDITIONS MET ====================

    def _generate_valid_case(self, case_num: int) -> Optional[Dict]:
        """
        Valid: 所有条件满足，带干扰骑士
        State 1: 白兵在位，黑兵在起始位置，白骑士在某处
        State 2: 白骑士移动（白方走棋）
        State 3: 黑兵双步移动（黑方走棋）
        Answer: Yes（轮到白方，可以吃过路兵）

        修复：
        1. 保护过路兵目标格（Rank 6）
        2. 强制使用白骑士，确保走子顺序正确（白→黑→白问）
        """
        black_file = random.choice(['b', 'c', 'd', 'e', 'f', 'g'])
        black_start = black_file + '7'
        black_end = black_file + '5'

        # 修复1：计算过路兵落点（Rank 6）
        ep_target_sq = black_file + '6'

        adjacent = self._adjacent_files(black_file)
        white_file = random.choice(adjacent)
        white_sq = white_file + '5'

        # 修复2：将落点加入禁区
        forbidden = {white_sq, black_start, black_end, ep_target_sq}

        # 修复3：强制使用白骑士，确保走子顺序：白骑士移动 → 黑兵移动 → 轮到白方
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            black_start: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            black_start: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            black_end: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_valid_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "all_conditions_met",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {black_end} en passant?",
            "expected": "yes",
            "reasoning": f"Black pawn just moved 2 squares from {black_start} to {black_end}, white pawn at {white_sq} is adjacent, capture square {ep_target_sq} is clear"
        }

    # ==================== INVALID: NOT FROM START ====================

    def _generate_not_from_start_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 黑兵不是从起始位置出发
        State 1: 黑兵在rank 6（不是7），白骑士在某处
        State 2: 白骑士移动
        State 3: 黑兵移动到rank 5
        Answer: No（不是从起始位置双步移动）
        """
        black_file = random.choice(['b', 'c', 'd', 'e', 'f', 'g'])
        black_start = black_file + '6'  # 从第6行开始（不是起始位置）
        black_end = black_file + '5'

        # 虽然无效，但仍保护目标格
        ep_target_sq = black_file + '6'  # 注意：这里和black_start重合，但概念上是目标格

        adjacent = self._adjacent_files(black_file)
        white_file = random.choice(adjacent)
        white_sq = white_file + '5'

        forbidden = {white_sq, black_start, black_end}

        # 使用白骑士确保走子顺序正确
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            black_start: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            black_start: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            black_end: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_not_from_start_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "not_from_start",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {black_end} en passant?",
            "expected": "no",
            "reasoning": f"Black pawn was not on starting rank (started from {black_start}, not rank 7)"
        }

    # ==================== INVALID: MOVED ONE SQUARE ====================

    def _generate_moved_one_square_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 黑兵只移动了1格
        State 1: 黑兵在rank 7，白骑士在某处
        State 2: 白骑士移动
        State 3: 黑兵只移动到rank 6（不是5）
        Answer: No（只移动了1格）
        """
        black_file = random.choice(['b', 'c', 'd', 'e', 'f', 'g'])
        black_start = black_file + '7'
        black_end = black_file + '6'  # 只移动1格

        # 保护目标格（虽然这里是无效案例）
        ep_target_sq = black_file + '6'

        adjacent = self._adjacent_files(black_file)
        white_file = random.choice(adjacent)
        white_sq = white_file + '5'

        # black_end 和 ep_target_sq 重合，所以forbidden包含它就行
        forbidden = {white_sq, black_start, black_end}

        # 使用白骑士
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            black_start: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            black_start: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            black_end: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_one_square_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "moved_one_square",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {black_end} en passant?",
            "expected": "no",
            "reasoning": f"Black pawn only moved 1 square from {black_start} to {black_end}"
        }

    # ==================== INVALID: NOT ADJACENT ====================

    def _generate_not_adjacent_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 白兵和黑兵不相邻
        State 1: 黑兵在rank 7，白兵在不相邻的列，白骑士在某处
        State 2: 白骑士移动
        State 3: 黑兵双步移动
        Answer: No（不相邻）
        """
        black_file = random.choice(['a', 'b', 'c', 'd'])
        black_start = black_file + '7'
        black_end = black_file + '5'

        # 保护目标格
        ep_target_sq = black_file + '6'

        # 选择不相邻的列
        black_file_idx = self.files.index(black_file)
        non_adjacent = [f for i, f in enumerate(
            self.files) if abs(i - black_file_idx) >= 2]

        if not non_adjacent:
            return None

        white_file = random.choice(non_adjacent)
        white_sq = white_file + '5'

        forbidden = {white_sq, black_start, black_end, ep_target_sq}

        # 使用白骑士
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            black_start: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            black_start: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            black_end: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_not_adjacent_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "not_adjacent",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {black_end} en passant?",
            "expected": "no",
            "reasoning": f"White pawn at {white_sq} is not adjacent to black pawn at {black_end}"
        }

    # ==================== INVALID: MULTI-PAWN CONFUSION ====================

    def _generate_multi_pawn_confusion_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 多个兵混淆 - 双步移动的兵和被询问的兵不是同一个

        修复走子顺序：
        State 1: 黑兵A已在c5（暗示历史上双步移动过，但那是"之前"的事），黑兵B在e6，白骑士在某处
        State 2: 白骑士移动（白方走棋）
        State 3: 黑兵B移动到e5（黑方走棋，只移动1格）

        问：能否吃黑兵B（在e5）？→ No（黑兵B只移动了1格）

        注意：虽然兵A之前双步移动过，但由于已经过了很多步，吃兵A的权利早已过期
        """
        white_file = random.choice(['c', 'd', 'e', 'f'])
        white_sq = white_file + '5'

        adjacent = self._adjacent_files(white_file)
        if len(adjacent) < 2:
            return None

        # 黑兵A：已经在c5（历史上双步移动过，但权利已过期）
        pawn_a_file = adjacent[0]
        pawn_a_sq = pawn_a_file + '5'  # 已经在第5行

        # 黑兵A的目标格（如果要吃的话），需要保护
        ep_target_a = pawn_a_file + '6'

        # 黑兵B：从e6移动到e5（只移动1格，这个我们要问）
        pawn_b_file = adjacent[1]
        pawn_b_start = pawn_b_file + '6'
        pawn_b_end = pawn_b_file + '5'

        # 黑兵B的目标格
        ep_target_b = pawn_b_file + '6'  # 和pawn_b_start重合

        forbidden = {white_sq, pawn_a_sq,
                     pawn_b_start, pawn_b_end, ep_target_a}

        # 白骑士
        knight_symbol = 'N'
        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            pawn_a_sq: 'p',
            pawn_b_start: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            pawn_a_sq: 'p',
            pawn_b_start: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            pawn_a_sq: 'p',
            pawn_b_end: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_confusion_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "multi_pawn_confusion",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {pawn_b_end} en passant?",
            "expected": "no",
            "reasoning": f"The pawn at {pawn_b_end} only moved 1 square from {pawn_b_start}; en passant requires a double-step move"
        }

    # ==================== INVALID: WRONG PAWN DOUBLE STEPPED ====================

    def _generate_wrong_pawn_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 问的是没有刚刚双步移动的那个兵

        State 1: 白兵在d5，黑兵A在c7，黑兵B在e5（早已在那里），白骑士
        State 2: 白骑士移动（白方走棋）
        State 3: 黑兵A双步移动到c5（黑方走棋）

        问：能否吃黑兵B（在e5）？→ No（黑兵B不是刚刚双步移动的）

        走子顺序：白方 → 黑方 → 轮到白方提问
        """
        white_file = random.choice(['c', 'd', 'e', 'f'])
        white_sq = white_file + '5'

        adjacent = self._adjacent_files(white_file)
        if len(adjacent) < 2:
            return None

        # 黑兵A：双步移动（这个刚刚移动，可以被吃，但我们不问这个）
        pawn_a_file = adjacent[0]
        pawn_a_start = pawn_a_file + '7'
        pawn_a_end = pawn_a_file + '5'
        ep_target_a = pawn_a_file + '6'

        # 黑兵B：早已在e5（我们问这个，答案是No）
        pawn_b_file = adjacent[1]
        pawn_b_sq = pawn_b_file + '5'
        ep_target_b = pawn_b_file + '6'

        forbidden = {white_sq, pawn_a_start, pawn_a_end,
                     pawn_b_sq, ep_target_a, ep_target_b}

        # 白骑士
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            pawn_a_start: 'p',
            pawn_b_sq: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            pawn_a_start: 'p',
            pawn_b_sq: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            pawn_a_end: 'p',
            pawn_b_sq: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_wrong_pawn_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "wrong_pawn_asked",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {pawn_b_sq} en passant?",
            "expected": "no",
            "reasoning": f"The pawn at {pawn_b_sq} did not just make a double-step move; the pawn at {pawn_a_end} did"
        }

    # ==================== VALID: CORRECT PAWN IDENTIFIED ====================

    def _generate_correct_pawn_case(self, case_num: int) -> Optional[Dict]:
        """
        Valid: 有多个兵，但问的是正确的那个（刚刚双步移动的）

        State 1: 白兵在d5，黑兵A在c7，黑兵B在e5（早已在那里），白骑士
        State 2: 白骑士移动（白方走棋）
        State 3: 黑兵A双步移动到c5（黑方走棋）

        问：能否吃黑兵A（在c5）？→ Yes（黑兵A刚刚双步移动）
        """
        white_file = random.choice(['c', 'd', 'e', 'f'])
        white_sq = white_file + '5'

        adjacent = self._adjacent_files(white_file)
        if len(adjacent) < 2:
            return None

        # 黑兵A：双步移动（我们问这个，答案是Yes）
        pawn_a_file = adjacent[0]
        pawn_a_start = pawn_a_file + '7'
        pawn_a_end = pawn_a_file + '5'
        ep_target_a = pawn_a_file + '6'

        # 黑兵B：早已在e5（干扰）
        pawn_b_file = adjacent[1]
        pawn_b_sq = pawn_b_file + '5'
        ep_target_b = pawn_b_file + '6'

        forbidden = {white_sq, pawn_a_start, pawn_a_end,
                     pawn_b_sq, ep_target_a, ep_target_b}

        # 白骑士
        knight_symbol = 'N'

        knight_start = self._get_safe_knight_position(forbidden)
        if not knight_start:
            return None

        forbidden.add(knight_start)
        knight_moves = self._get_knight_moves(knight_start, forbidden)
        if not knight_moves:
            return None

        knight_end = random.choice(knight_moves)

        state1 = {
            white_sq: 'P',
            pawn_a_start: 'p',
            pawn_b_sq: 'p',
            knight_start: knight_symbol
        }

        state2 = {
            white_sq: 'P',
            pawn_a_start: 'p',
            pawn_b_sq: 'p',
            knight_end: knight_symbol
        }

        state3 = {
            white_sq: 'P',
            pawn_a_end: 'p',
            pawn_b_sq: 'p',
            knight_end: knight_symbol
        }

        return {
            "case_id": f"L3_correct_pawn_{case_num}",
            "type": "en_passant_temporal",
            "subtype": "correct_pawn_identified",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": f"Can white capture the black pawn at {pawn_a_end} en passant?",
            "expected": "yes",
            "reasoning": f"The pawn at {pawn_a_end} just moved 2 squares from {pawn_a_start}; capture square {ep_target_a} is clear"
        }

    # ==================== GENERATE ALL ====================

    def generate_all(self, n_cases: int = 100) -> List[Dict]:
        """生成所有 Level 3 测试案例"""
        all_cases = []

        # 分配比例
        # Valid: 30% (basic valid + correct pawn identified)
        # Invalid: 70%
        n_valid_basic = int(n_cases * 0.15)
        n_valid_correct = int(n_cases * 0.15)
        n_invalid = n_cases - n_valid_basic - n_valid_correct

        # Invalid 分配
        n_not_from_start = n_invalid // 5
        n_one_square = n_invalid // 5
        n_not_adjacent = n_invalid // 5
        n_confusion = n_invalid // 5
        n_wrong_pawn = n_invalid - n_not_from_start - \
            n_one_square - n_not_adjacent - n_confusion

        print(f"Generating valid cases (basic)...")
        valid_basic_count = 0
        for _ in range(n_valid_basic * 10):
            if valid_basic_count >= n_valid_basic:
                break
            case = self._generate_valid_case(valid_basic_count + 1)
            if case:
                all_cases.append(case)
                valid_basic_count += 1
        print(f"  ✓ Generated {valid_basic_count} valid basic cases")

        print(f"Generating valid cases (correct pawn)...")
        valid_correct_count = 0
        for _ in range(n_valid_correct * 10):
            if valid_correct_count >= n_valid_correct:
                break
            case = self._generate_correct_pawn_case(valid_correct_count + 1)
            if case:
                all_cases.append(case)
                valid_correct_count += 1
        print(f"  ✓ Generated {valid_correct_count} correct pawn cases")

        print(f"Generating invalid cases...")

        # Not from start
        not_start_count = 0
        for _ in range(n_not_from_start * 10):
            if not_start_count >= n_not_from_start:
                break
            case = self._generate_not_from_start_case(not_start_count + 1)
            if case:
                all_cases.append(case)
                not_start_count += 1
        print(f"  ✓ Generated {not_start_count} not_from_start cases")

        # Moved one square
        one_sq_count = 0
        for _ in range(n_one_square * 10):
            if one_sq_count >= n_one_square:
                break
            case = self._generate_moved_one_square_case(one_sq_count + 1)
            if case:
                all_cases.append(case)
                one_sq_count += 1
        print(f"  ✓ Generated {one_sq_count} moved_one_square cases")

        # Not adjacent
        not_adj_count = 0
        for _ in range(n_not_adjacent * 10):
            if not_adj_count >= n_not_adjacent:
                break
            case = self._generate_not_adjacent_case(not_adj_count + 1)
            if case:
                all_cases.append(case)
                not_adj_count += 1
        print(f"  ✓ Generated {not_adj_count} not_adjacent cases")

        # Multi-pawn confusion
        confusion_count = 0
        for _ in range(n_confusion * 10):
            if confusion_count >= n_confusion:
                break
            case = self._generate_multi_pawn_confusion_case(
                confusion_count + 1)
            if case:
                all_cases.append(case)
                confusion_count += 1
        print(f"  ✓ Generated {confusion_count} multi_pawn_confusion cases")

        # Wrong pawn asked
        wrong_count = 0
        for _ in range(n_wrong_pawn * 10):
            if wrong_count >= n_wrong_pawn:
                break
            case = self._generate_wrong_pawn_case(wrong_count + 1)
            if case:
                all_cases.append(case)
                wrong_count += 1
        print(f"  ✓ Generated {wrong_count} wrong_pawn_asked cases")

        # 打乱顺序
        random.shuffle(all_cases)

        # 统计
        stats = defaultdict(int)
        for case in all_cases:
            stats[case['subtype']] += 1

        total_valid = valid_basic_count + valid_correct_count
        total_invalid = len(all_cases) - total_valid

        print(f"\n✓ Total generated: {len(all_cases)} Level 3 test cases")
        print(
            f"  Valid: {total_valid} ({total_valid/len(all_cases)*100:.1f}%)")
        print(
            f"  Invalid: {total_invalid} ({total_invalid/len(all_cases)*100:.1f}%)")
        print(f"  Breakdown:")
        for subtype, count in sorted(stats.items()):
            print(f"    {subtype}: {count} ({count/len(all_cases)*100:.1f}%)")

        return all_cases
