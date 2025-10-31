"""
Generate verification questions for temporal test cases
To ensure the model can correctly recognize each board state before testing
"""

from typing import Dict, List


class TemporalVerificationGenerator:
    """Generate verification questions for temporal test cases"""

    @staticmethod
    def generate_verification(case: Dict) -> Dict:
        """
        Generate a verification question for a temporal test case

        Args:
            case: Test case dictionary with multiple states

        Returns:
            Dictionary with verification_question and verification_expected
        """
        states = case.get('states', [])

        if len(states) == 0:
            return {
                'verification_question': "Can you see chess board states in this image?",
                'verification_expected': "yes",
                'verification_keywords': ['yes', 'board']
            }

        # For temporal tests, verify the model can identify pieces in each state
        # We'll ask about a specific state

        if len(states) == 2:
            # Ask about both states
            state1_pieces = states[0].get('pieces', {})
            state2_pieces = states[1].get('pieces', {})

            if state1_pieces and state2_pieces:
                sq1 = list(state1_pieces.keys())[0]
                sq2 = list(state2_pieces.keys())[0]

                return {
                    'verification_question': f"In State 1, what square has a piece? In State 2, what square has a piece? (Answer with two squares separated by comma or space)",
                    'verification_expected': f"{sq1}, {sq2}",
                    'verification_keywords': [sq1, sq2]
                }

        elif len(states) == 3:
            # Ask about the last state
            state3_pieces = states[2].get('pieces', {})

            if state3_pieces:
                sq = list(state3_pieces.keys())[0]

                return {
                    'verification_question': f"In the most recent state (State 3), what square has the piece? (Answer with square name only, e.g., 'e4')",
                    'verification_expected': sq,
                    'verification_keywords': [sq]
                }

        # Default fallback
        return {
            'verification_question': "How many board states do you see?",
            'verification_expected': str(len(states)),
            'verification_keywords': [str(len(states))]
        }

    @staticmethod
    def check_verification_answer(response: str, case: Dict) -> bool:
        """
        Check if the model's verification response is correct

        Args:
            response: Model's response to verification question
            case: Test case dictionary with verification info

        Returns:
            True if verification passed, False otherwise
        """
        response_lower = response.lower().strip()

        # Remove common punctuation
        response_clean = response_lower.replace(".", "").replace(
            ",", "").replace("!", "").replace("?", "").replace("'", "")

        keywords = case.get('verification_keywords', [])

        # All keywords must appear in response
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in response_clean:
                return False

        return True
