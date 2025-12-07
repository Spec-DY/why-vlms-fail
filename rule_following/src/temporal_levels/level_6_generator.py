"""
Level 6 Generator: Castling + Temporal History + Check Rules
测试王车易位的时序规则：
1. 王/车是否移动过（即使移回原位也不能易位）
2. 三条Check约束（in/through/into）

预测性问题：给定历史状态序列，问能否进行易位
"""

import random
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict


class Level6Generator:
    """Generate Level 6 test cases - castling with temporal history"""

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
                'path_squares': ['f1', 'g1'],
                'king_temp_moves': ['d1', 'f1'],  # 王可以临时移动到的格子
                'rook_temp_moves': ['g1', 'f1'],  # 车可以临时移动到的格子
                'question_text': 'Can white castle kingside?'
            },
            'white_queenside': {
                'king_start': 'e1', 'king_end': 'c1',
                'rook_start': 'a1', 'rook_end': 'd1',
                'in_sq': 'e1', 'through_sq': 'd1', 'into_sq': 'c1',
                'color': 'white',
                'king_symbol': 'K', 'rook_symbol': 'R',
                'path_squares': ['b1', 'c1', 'd1'],
                'king_temp_moves': ['d1', 'f1'],
                'rook_temp_moves': ['b1', 'c1'],
                'question_text': 'Can white castle queenside?'
            },
            'black_kingside': {
                'king_start': 'e8', 'king_end': 'g8',
                'rook_start': 'h8', 'rook_end': 'f8',
                'in_sq': 'e8', 'through_sq': 'f8', 'into_sq': 'g8',
                'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['f8', 'g8'],
                'king_temp_moves': ['d8', 'f8'],
                'rook_temp_moves': ['g8', 'f8'],
                'question_text': 'Can black castle kingside?'
            },
            'black_queenside': {
                'king_start': 'e8', 'king_end': 'c8',
                'rook_start': 'a8', 'rook_end': 'd8',
                'in_sq': 'e8', 'through_sq': 'd8', 'into_sq': 'c8',
                'color': 'black',
                'king_symbol': 'k', 'rook_symbol': 'r',
                'path_squares': ['b8', 'c8', 'd8'],
                'king_temp_moves': ['d8', 'f8'],
                'rook_temp_moves': ['b8', 'c8'],
                'question_text': 'Can black castle queenside?'
            }
        }

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

    def _get_piece_symbol(self, piece_type: str, color: str) -> str:
        symbols = {
            ('rook', 'white'): 'R', ('rook', 'black'): 'r',
            ('bishop', 'white'): 'B', ('bishop', 'black'): 'b',
            ('knight', 'white'): 'N', ('knight', 'black'): 'n',
            ('queen', 'white'): 'Q', ('queen', 'black'): 'q',
            ('pawn', 'white'): 'P', ('pawn', 'black'): 'p'
        }
        return symbols.get((piece_type, color), 'p')

    def _symbol_to_type(self, symbol: str) -> str:
        type_map = {
            'R': 'rook', 'r': 'rook',
            'B': 'bishop', 'b': 'bishop',
            'N': 'knight', 'n': 'knight',
            'Q': 'queen', 'q': 'queen',
            'K': 'king', 'k': 'king',
            'P': 'pawn', 'p': 'pawn'
        }
        return type_map.get(symbol, 'pawn')

    def _get_path_squares(self, from_sq: str, to_sq: str) -> List[str]:
        from_f, from_r = self._square_to_coords(from_sq)
        to_f, to_r = self._square_to_coords(to_sq)
        df, dr = to_f - from_f, to_r - from_r
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
        for sq in self._get_path_squares(from_sq, to_sq):
            if sq in occupied:
                return False
        return True

    def _can_attack(self, from_sq: str, to_sq: str, piece_type: str) -> bool:
        from_f, from_r = self._square_to_coords(from_sq)
        to_f, to_r = self._square_to_coords(to_sq)
        df, dr = abs(to_f - from_f), abs(to_r - from_r)
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
        if not self._can_attack(from_sq, to_sq, piece_type):
            return False
        if piece_type == 'knight':
            return True
        return self._is_path_clear(from_sq, to_sq, occupied)

    def _get_attacker_positions(self, target_sq: str, attacker_type: str,
                                forbidden: Set[str], occupied: Set[str]) -> List[str]:
        target_f, target_r = self._square_to_coords(target_sq)
        positions = []
        if attacker_type in ['rook', 'queen']:
            for f in range(8):
                if f != target_f:
                    sq = self._coords_to_square(f, target_r)
                    if sq and sq not in forbidden and self._is_path_clear(sq, target_sq, occupied):
                        positions.append(sq)
            for r in range(8):
                if r != target_r:
                    sq = self._coords_to_square(target_f, r)
                    if sq and sq not in forbidden and self._is_path_clear(sq, target_sq, occupied):
                        positions.append(sq)
        if attacker_type in ['bishop', 'queen']:
            for d in range(1, 8):
                for df, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    sq = self._coords_to_square(
                        target_f + df * d, target_r + dr * d)
                    if sq and sq not in forbidden and self._is_path_clear(sq, target_sq, occupied):
                        positions.append(sq)
        if attacker_type == 'knight':
            for df, dr in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                sq = self._coords_to_square(target_f + df, target_r + dr)
                if sq and sq not in forbidden:
                    positions.append(sq)
        return positions

    def _get_non_attacking_square(self, critical_squares: List[str],
                                  forbidden: Set[str], piece_type: str,
                                  occupied: Set[str]) -> Optional[str]:
        for _ in range(100):
            sq = self._random_square()
            if sq in forbidden:
                continue
            attacks = False
            for c_sq in critical_squares:
                if self._can_attack_with_clear_path(sq, c_sq, piece_type, occupied):
                    attacks = True
                    break
            if not attacks:
                return sq
        return None

    def _get_knight_moves(self, square: str, forbidden: Set[str]) -> List[str]:
        """获取骑士从某格可以移动到的所有格子"""
        f, r = self._square_to_coords(square)
        moves = []
        for df, dr in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            sq = self._coords_to_square(f + df, r + dr)
            if sq and sq not in forbidden:
                moves.append(sq)
        return moves

    def _get_legal_start_positions(self, end_sq: str, piece_type: str,
                                   forbidden: Set[str], occupied: Set[str],
                                   critical_squares: List[str]) -> List[str]:
        """
        获取棋子能够合法移动到end_sq的所有起始位置
        要求：
        1. 从起始位置到end_sq的移动符合该棋子的移动规则
        2. 移动路径畅通（骑士除外）
        3. 起始位置不在forbidden中
        4. 从起始位置不能攻击任何关键格（确保初始状态是安全的）
        """
        end_f, end_r = self._square_to_coords(end_sq)
        positions = []

        if piece_type == 'knight':
            # 骑士：L形移动，可以跳过棋子
            for df, dr in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                sq = self._coords_to_square(end_f + df, end_r + dr)
                if sq and sq not in forbidden:
                    # 检查从这个位置是否能攻击关键格
                    attacks_critical = False
                    for c_sq in critical_squares:
                        if self._can_attack(sq, c_sq, 'knight'):
                            attacks_critical = True
                            break
                    if not attacks_critical:
                        positions.append(sq)

        elif piece_type == 'rook':
            # 车：沿直线移动
            # 水平方向
            for f in range(8):
                if f != end_f:
                    sq = self._coords_to_square(f, end_r)
                    if sq and sq not in forbidden:
                        # 检查路径是否畅通
                        if self._is_path_clear(sq, end_sq, occupied):
                            # 检查从这个位置是否能攻击关键格
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'rook', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)
            # 垂直方向
            for r in range(8):
                if r != end_r:
                    sq = self._coords_to_square(end_f, r)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, end_sq, occupied):
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'rook', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)

        elif piece_type == 'bishop':
            # 象：沿对角线移动
            for d in range(1, 8):
                for df, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    sq = self._coords_to_square(end_f + df * d, end_r + dr * d)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, end_sq, occupied):
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'bishop', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)

        elif piece_type == 'queen':
            # 后：沿直线或对角线移动
            # 水平
            for f in range(8):
                if f != end_f:
                    sq = self._coords_to_square(f, end_r)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, end_sq, occupied):
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'queen', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)
            # 垂直
            for r in range(8):
                if r != end_r:
                    sq = self._coords_to_square(end_f, r)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, end_sq, occupied):
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'queen', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)
            # 对角线
            for d in range(1, 8):
                for df, dr in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    sq = self._coords_to_square(end_f + df * d, end_r + dr * d)
                    if sq and sq not in forbidden:
                        if self._is_path_clear(sq, end_sq, occupied):
                            attacks_critical = False
                            for c_sq in critical_squares:
                                if self._can_attack_with_clear_path(sq, c_sq, 'queen', occupied):
                                    attacks_critical = True
                                    break
                            if not attacks_critical:
                                positions.append(sq)

        return positions

    # ==================== VALID CASES ====================

    def _generate_valid_case(self, case_num: int) -> Optional[Dict]:
        """
        Valid: 其他棋子移动，王车未动
        State 1: 初始（王车原位 + 其他棋子）
        State 2: 其他棋子移动（王车不动）
        State 3: 其他棋子再移动（王车仍不动）
        Answer: Yes
        """
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        critical_squares = [config['in_sq'],
                            config['through_sq'], config['into_sq']]

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        # 添加一个会移动的骑士（不攻击关键格）
        moving_piece_color = config['color']  # 同色棋子移动

        knight_sq = self._get_non_attacking_square(
            critical_squares, forbidden, 'knight', occupied
        )
        if not knight_sq:
            return None

        knight_symbol = 'N' if moving_piece_color == 'white' else 'n'
        self._add_piece_to_counts('knight', moving_piece_color, piece_counts)
        forbidden.add(knight_sq)
        occupied.add(knight_sq)

        # 找骑士的移动目标（也不能攻击关键格）
        knight_moves = self._get_knight_moves(knight_sq, forbidden)
        valid_knight_targets = []
        for target in knight_moves:
            test_occupied = (occupied - {knight_sq}) | {target}
            attacks = False
            for c_sq in critical_squares:
                if self._can_attack_with_clear_path(target, c_sq, 'knight', test_occupied):
                    attacks = True
                    break
            if not attacks:
                valid_knight_targets.append(target)

        if len(valid_knight_targets) < 2:
            return None

        knight_target_1 = valid_knight_targets[0]

        # 从target_1再找一个移动目标
        forbidden_2 = forbidden | {knight_target_1}
        knight_moves_2 = self._get_knight_moves(
            knight_target_1, forbidden_2 - {knight_sq})
        valid_knight_targets_2 = []
        for target in knight_moves_2:
            test_occupied = (occupied - {knight_sq}) | {target}
            attacks = False
            for c_sq in critical_squares:
                if self._can_attack_with_clear_path(target, c_sq, 'knight', test_occupied):
                    attacks = True
                    break
            if not attacks:
                valid_knight_targets_2.append(target)

        if not valid_knight_targets_2:
            return None

        knight_target_2 = random.choice(valid_knight_targets_2)

        # 添加额外的静态棋子
        extra_pieces = {}
        for _ in range(random.randint(1, 2)):
            for _ in range(50):
                p_type = random.choice(['bishop', 'knight'])
                p_color = random.choice(['white', 'black'])
                if not self._can_add_piece(p_type, p_color, piece_counts):
                    continue
                sq = self._get_non_attacking_square(
                    critical_squares, forbidden, p_type, occupied)
                if sq:
                    extra_pieces[sq] = self._get_piece_symbol(p_type, p_color)
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(p_type, p_color, piece_counts)
                    break

        # 构建3个states
        base_pieces = {
            config['king_start']: config['king_symbol'],
            config['rook_start']: config['rook_symbol'],
            **extra_pieces
        }

        state1 = {**base_pieces, knight_sq: knight_symbol}
        state2 = {**base_pieces, knight_target_1: knight_symbol}
        state3 = {**base_pieces, knight_target_2: knight_symbol}

        return {
            "case_id": f"L6_valid_{case_num}",
            "type": "castling_temporal",
            "subtype": "valid_other_moved",
            "castling_type": castling_type,
            "invalid_reason": None,
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": config['question_text'],
            "expected": "yes",
            "reasoning": "King and rook have not moved; only other pieces moved"
        }

    # ==================== INVALID: KING MOVED ====================

    def _generate_king_moved_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 王移动过再移回
        State 1: 王在原位
        State 2: 王移动到临时位置
        State 3: 王移回原位
        Answer: No (王已移动过)
        """
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        # 王的临时移动位置
        king_temp = random.choice(config['king_temp_moves'])

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares | {king_temp}

        # 添加额外棋子
        extra_pieces = {}
        critical_squares = [config['in_sq'],
                            config['through_sq'], config['into_sq']]

        for _ in range(random.randint(1, 2)):
            for _ in range(50):
                p_type = random.choice(['bishop', 'knight'])
                p_color = random.choice(['white', 'black'])
                if not self._can_add_piece(p_type, p_color, piece_counts):
                    continue
                sq = self._get_non_attacking_square(
                    critical_squares, forbidden, p_type, occupied)
                if sq:
                    extra_pieces[sq] = self._get_piece_symbol(p_type, p_color)
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(p_type, p_color, piece_counts)
                    break

        base_pieces = {
            config['rook_start']: config['rook_symbol'],
            **extra_pieces
        }

        state1 = {config['king_start']: config['king_symbol'], **base_pieces}
        state2 = {king_temp: config['king_symbol'], **base_pieces}
        state3 = {config['king_start']: config['king_symbol'], **base_pieces}

        return {
            "case_id": f"L6_king_moved_{case_num}",
            "type": "castling_temporal",
            "subtype": "invalid_king_moved",
            "castling_type": castling_type,
            "invalid_reason": "king_moved",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": config['question_text'],
            "expected": "no",
            "reasoning": f"King moved from {config['king_start']} to {king_temp} and back; castling rights lost"
        }

    # ==================== INVALID: ROOK MOVED ====================

    def _generate_rook_moved_case(self, case_num: int) -> Optional[Dict]:
        """
        Invalid: 车移动过再移回
        State 1: 车在原位
        State 2: 车移动到临时位置
        State 3: 车移回原位
        Answer: No (车已移动过)
        """
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        # 车的临时移动位置
        rook_temp = random.choice(config['rook_temp_moves'])

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares | {rook_temp}

        extra_pieces = {}
        critical_squares = [config['in_sq'],
                            config['through_sq'], config['into_sq']]

        for _ in range(random.randint(1, 2)):
            for _ in range(50):
                p_type = random.choice(['bishop', 'knight'])
                p_color = random.choice(['white', 'black'])
                if not self._can_add_piece(p_type, p_color, piece_counts):
                    continue
                sq = self._get_non_attacking_square(
                    critical_squares, forbidden, p_type, occupied)
                if sq:
                    extra_pieces[sq] = self._get_piece_symbol(p_type, p_color)
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(p_type, p_color, piece_counts)
                    break

        base_pieces = {
            config['king_start']: config['king_symbol'],
            **extra_pieces
        }

        state1 = {config['rook_start']: config['rook_symbol'], **base_pieces}
        state2 = {rook_temp: config['rook_symbol'], **base_pieces}
        state3 = {config['rook_start']: config['rook_symbol'], **base_pieces}

        return {
            "case_id": f"L6_rook_moved_{case_num}",
            "type": "castling_temporal",
            "subtype": "invalid_rook_moved",
            "castling_type": castling_type,
            "invalid_reason": "rook_moved",
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []},
                {"pieces": state3, "squares": []}
            ],
            "question": config['question_text'],
            "expected": "no",
            "reasoning": f"Rook moved from {config['rook_start']} to {rook_temp} and back; castling rights lost"
        }

    # ==================== INVALID: CHECK VIOLATION ====================

    def _generate_check_violation_case(self, case_num: int, violation_type: str) -> Optional[Dict]:
        """
        Invalid: 对方棋子移动到攻击位置
        State 1: 初始（无威胁）
        State 2: 对方棋子移动到攻击关键格的位置
        Answer: No (违反check规则)

        关键：攻击者从初始位置到最终位置的移动必须符合棋子规则
        """
        castling_type = random.choice(list(self.castling_configs.keys()))
        config = self.castling_configs[castling_type]

        piece_counts = {}
        self._add_piece_to_counts('king', config['color'], piece_counts)
        self._add_piece_to_counts('rook', config['color'], piece_counts)

        target_map = {
            'in': config['in_sq'],
            'through': config['through_sq'],
            'into': config['into_sq']
        }
        target_sq = target_map[violation_type]

        occupied = {config['king_start'], config['rook_start']}
        path_squares = set(config['path_squares'])
        forbidden = occupied | path_squares

        attacker_color = 'black' if config['color'] == 'white' else 'white'
        critical_squares = [config['in_sq'],
                            config['through_sq'], config['into_sq']]

        # 尝试不同的攻击者类型
        attacker_types = ['rook', 'bishop', 'knight', 'queen']
        random.shuffle(attacker_types)

        attacker_start = None
        attacker_final = None
        attacker_type = None

        for a_type in attacker_types:
            if not self._can_add_piece(a_type, attacker_color, piece_counts):
                continue

            # 找攻击者的最终位置（能攻击目标格）
            final_positions = self._get_attacker_positions(
                target_sq, a_type, forbidden, occupied)
            if not final_positions:
                continue

            random.shuffle(final_positions)

            for final_pos in final_positions:
                # 找合法的起始位置（能移动到final_pos，且不攻击关键格）
                forbidden_for_start = forbidden | {final_pos}
                start_positions = self._get_legal_start_positions(
                    final_pos, a_type, forbidden_for_start, occupied, critical_squares
                )

                if start_positions:
                    attacker_start = random.choice(start_positions)
                    attacker_final = final_pos
                    attacker_type = a_type
                    break

            if attacker_start:
                break

        if not attacker_start or not attacker_final:
            return None

        self._add_piece_to_counts(attacker_type, attacker_color, piece_counts)
        attacker_symbol = self._get_piece_symbol(attacker_type, attacker_color)
        forbidden.add(attacker_start)
        forbidden.add(attacker_final)
        occupied.add(attacker_start)

        # 添加额外棋子（确保不阻挡攻击者的移动路径和攻击射线）
        extra_pieces = {}
        non_targeted = [sq for sq in critical_squares if sq != target_sq]

        # 获取攻击者的移动路径（Start → Final）
        attacker_move_path = set(self._get_path_squares(
            attacker_start, attacker_final))

        # 获取攻击者的攻击射线（Final → Target）
        # 骑士不需要，因为骑士攻击不会被阻挡
        if attacker_type != 'knight':
            attacker_fire_line = set(
                self._get_path_squares(attacker_final, target_sq))
        else:
            attacker_fire_line = set()

        # 合并所有需要保护的路径
        protected_squares = attacker_move_path | attacker_fire_line

        for _ in range(random.randint(1, 2)):
            for _ in range(50):
                p_type = random.choice(['bishop', 'knight'])
                p_color = random.choice(['white', 'black'])
                if not self._can_add_piece(p_type, p_color, piece_counts):
                    continue

                # 不能放在攻击者的移动路径或攻击射线上
                forbidden_extra = forbidden | protected_squares
                sq = self._get_non_attacking_square(
                    non_targeted, forbidden_extra, p_type, occupied)
                if sq:
                    extra_pieces[sq] = self._get_piece_symbol(p_type, p_color)
                    forbidden.add(sq)
                    occupied.add(sq)
                    self._add_piece_to_counts(p_type, p_color, piece_counts)
                    break

        base_pieces = {
            config['king_start']: config['king_symbol'],
            config['rook_start']: config['rook_symbol'],
            **extra_pieces
        }

        state1 = {attacker_start: attacker_symbol, **base_pieces}
        state2 = {attacker_final: attacker_symbol, **base_pieces}

        violation_name = {'in': 'in_check',
                          'through': 'through_check', 'into': 'into_check'}

        return {
            "case_id": f"L6_check_{violation_type}_{case_num}",
            "type": "castling_temporal",
            "subtype": f"invalid_{violation_name[violation_type]}",
            "castling_type": castling_type,
            "invalid_reason": violation_name[violation_type],
            "states": [
                {"pieces": state1, "squares": []},
                {"pieces": state2, "squares": []}
            ],
            "question": config['question_text'],
            "expected": "no",
            "reasoning": f"Enemy {attacker_type} moved from {attacker_start} to {attacker_final}, attacking {target_sq}; violates {violation_name[violation_type]} rule"
        }

    # ==================== GENERATE ALL ====================

    def generate_all(self, n_cases: int = 100, valid_ratio: float = 0.20) -> List[Dict]:
        """生成所有 Level 6 测试案例"""
        all_cases = []

        n_valid = int(n_cases * valid_ratio)
        n_invalid = n_cases - n_valid

        # 分配无效案例类型
        # 50% 时序违规（王/车移动过），50% check违规
        n_temporal = n_invalid // 2
        n_check = n_invalid - n_temporal

        n_king_moved = n_temporal // 2
        n_rook_moved = n_temporal - n_king_moved

        n_in_check = n_check // 3
        n_through_check = n_check // 3
        n_into_check = n_check - n_in_check - n_through_check

        # ========== Valid cases ==========
        print(
            f"Generating {n_valid} VALID cases (other pieces moved, king/rook stayed)...")
        valid_gen = 0
        for _ in range(n_valid * 10):
            if valid_gen >= n_valid:
                break
            case = self._generate_valid_case(valid_gen + 1)
            if case:
                all_cases.append(case)
                valid_gen += 1
        print(f"  ✓ Generated {valid_gen} valid cases")

        # ========== Invalid: King moved ==========
        print(
            f"Generating {n_king_moved} INVALID cases (king moved and returned)...")
        king_gen = 0
        for _ in range(n_king_moved * 10):
            if king_gen >= n_king_moved:
                break
            case = self._generate_king_moved_case(king_gen + 1)
            if case:
                all_cases.append(case)
                king_gen += 1
        print(f"  ✓ Generated {king_gen} king-moved cases")

        # ========== Invalid: Rook moved ==========
        print(
            f"Generating {n_rook_moved} INVALID cases (rook moved and returned)...")
        rook_gen = 0
        for _ in range(n_rook_moved * 10):
            if rook_gen >= n_rook_moved:
                break
            case = self._generate_rook_moved_case(rook_gen + 1)
            if case:
                all_cases.append(case)
                rook_gen += 1
        print(f"  ✓ Generated {rook_gen} rook-moved cases")

        # ========== Invalid: Check violations ==========
        print(f"Generating check violation cases...")

        in_gen = 0
        for _ in range(n_in_check * 10):
            if in_gen >= n_in_check:
                break
            case = self._generate_check_violation_case(in_gen + 1, 'in')
            if case:
                all_cases.append(case)
                in_gen += 1
        print(f"  ✓ Generated {in_gen} in-check cases")

        through_gen = 0
        for _ in range(n_through_check * 10):
            if through_gen >= n_through_check:
                break
            case = self._generate_check_violation_case(
                through_gen + 1, 'through')
            if case:
                all_cases.append(case)
                through_gen += 1
        print(f"  ✓ Generated {through_gen} through-check cases")

        into_gen = 0
        for _ in range(n_into_check * 10):
            if into_gen >= n_into_check:
                break
            case = self._generate_check_violation_case(into_gen + 1, 'into')
            if case:
                all_cases.append(case)
                into_gen += 1
        print(f"  ✓ Generated {into_gen} into-check cases")

        # ========== Shuffle ==========
        random.shuffle(all_cases)

        # ========== Stats ==========
        stats = defaultdict(int)
        for case in all_cases:
            stats[case['subtype']] += 1

        print(f"\n✓ Total generated: {len(all_cases)} Level 6 test cases")
        print(f"  Breakdown:")
        for subtype, count in sorted(stats.items()):
            print(f"    {subtype}: {count} ({count/len(all_cases)*100:.1f}%)")

        return all_cases
