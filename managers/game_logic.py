import random
from config import MIN_NUMBER, MAX_NUMBER

class GameLogic:
    def __init__(self, data_manager):
        self.dm = data_manager
        state = self.dm.load()
        self.history = state.get("history", [])
        self.current_number = state.get("current_number")
        
        # Ensure consistency
        self.available_numbers = [
            n for n in range(MIN_NUMBER, MAX_NUMBER + 1)
            if n not in self.history
        ]

    def get_next_number(self):
        if not self.available_numbers:
            return None
        
        # Fairness Bias Logic
        candidates = self._get_fair_candidates()
        
        target = random.choice(candidates)
        
        # Update state immediately
        self.history.append(target)
        self.available_numbers.remove(target)
        self.current_number = target
        
        self.dm.save(self.history, self.current_number)
        return target

    def _get_fair_candidates(self):
        """
        Returns a filtered list of candidates if bias logic is triggered,
        otherwise returns all available numbers.
        """
        all_candidates = self.available_numbers
        if not all_candidates: return []
        
        # 1. Analyze Distributions from HISTORY
        ones_counts = {i: 0 for i in range(10)} # 0-9
        tens_counts = {i: 0 for i in range(8)}  # 0-7 (00s to 70s)
        interval_counts = {i: 0 for i in range(5)} # 0-4 (1-15, 16-30, ..., 61-75)
        
        for num in self.history:
            # Ones (Last Digit)
            ones_counts[num % 10] += 1
            
            # Tens (Range)
            # 1-9 -> 0, 10-19 -> 1, ..., 70-75 -> 7
            tens_idx = 0 if num < 10 else num // 10
            tens_counts[tens_idx] += 1
            
            # 15-step Intervals (Range)
            # 1-15 -> 0, 16-30 -> 1, ..., 61-75 -> 4
            # (num - 1) // 15
            int_idx = (num - 1) // 15
            if 0 <= int_idx <= 4:
                interval_counts[int_idx] += 1
            
        # 2. Calculate Gaps
        def get_gap_info(counts):
            vals = list(counts.values())
            min_v = min(vals)
            max_v = max(vals)
            gap = max_v - min_v
            # Find which keys are lagging (min_v)
            targets = [k for k, v in counts.items() if v == min_v]
            return gap, targets

        ones_gap, ones_targets = get_gap_info(ones_counts)
        tens_gap, tens_targets = get_gap_info(tens_counts)
        interval_gap, interval_targets = get_gap_info(interval_counts)
        
        BIAS_THRESHOLD = 4
        BIAS_PROBABILITY = 0.45 # 45% chance to intervene
        
        # 3. Probability Check
        if random.random() > BIAS_PROBABILITY:
             return all_candidates

        target_mode = None # 'ones' or 'tens' or 'interval' or None
        
        # 4. Determine Priority (Largest Gap Wins)
        current_max_gap = -1
        
        # Check Ones
        if ones_gap >= BIAS_THRESHOLD:
            current_max_gap = ones_gap
            target_mode = 'ones'
            
        # Check Tens
        if tens_gap >= BIAS_THRESHOLD:
            if tens_gap > current_max_gap:
                current_max_gap = tens_gap
                target_mode = 'tens'
        
        # Check Intervals
        if interval_gap >= BIAS_THRESHOLD:
            if interval_gap > current_max_gap:
                current_max_gap = interval_gap
                target_mode = 'interval'
            
        # 5. Apply Filter
        filtered = []
        if target_mode == 'ones':
            filtered = [n for n in all_candidates if (n % 10) in ones_targets]
            
        elif target_mode == 'tens':
            filtered = []
            for n in all_candidates:
                t_idx = 0 if n < 10 else n // 10
                if t_idx in tens_targets:
                    filtered.append(n)
                    
        elif target_mode == 'interval':
            filtered = []
            for n in all_candidates:
                i_idx = (n - 1) // 15
                if i_idx in interval_targets:
                    filtered.append(n)
        
        # If filter yielded results, use them. 
        # If empty (e.g. all numbers in that group already taken), fallback to full list.
        if filtered:
            return filtered
            
        return all_candidates

    def reset_game(self):
        self.history = []
        self.current_number = None
        self.available_numbers = list(range(MIN_NUMBER, MAX_NUMBER + 1))
        self.dm.save(self.history, self.current_number)

    def calculate_animation_path(self, target_num, steps=20):
        """
        Returns a list of numbers leading up to the target.
        Logic described in spec: backtrack N steps from target.
        """
        path = []
        # Create a virtual wheel 1-75
        current_idx = target_num # 1-based
        
        # Backtrack 'steps' times
        start_idx = current_idx - steps
        
        # Generate sequence
        for i in range(start_idx, current_idx + 1):
            # Normalize to 1-75 range handling loop
            # (i-1) % 75 + 1 handles the 1-based wrapping correctly
            # e.g. if i=0 -> -1%75=74 -> +1 = 75. Correct.
            # e.g. if i=76 -> 75%75=0 -> +1 = 1. Correct.
            normalized = (i - 1) % MAX_NUMBER + 1
            path.append(normalized)
            
        return path
