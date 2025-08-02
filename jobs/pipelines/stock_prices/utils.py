from typing import Optional


class ChangeUtils:
    def compute_change_percentage(self, current_value: float, last_value: float) -> Optional[float]:
        if current_value and last_value:
            return ((float(current_value) - float(last_value)) / float(last_value)) * 100.0
        return None
