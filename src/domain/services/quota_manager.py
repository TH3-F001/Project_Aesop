from typing import Union


class QuotaManager:
    def __init__(self, max_quota: float, initial_spent_quota: float = 0):
        self._max_quota_set = False
        self.max_quota = max_quota
        self._spent_quota = initial_spent_quota

    @property
    def max_quota(self) -> float:
        """Get the maximum quota"""
        return self._max_quota

    @max_quota.setter
    def max_quota(self, value: float):
        """Set the maximum quota only if it hasn't been set before."""
        if not self._max_quota_set:
            self._max_quota = value
            self._max_quota_set = True
        else:
            raise ValueError('Max quota can only be set once to prevent inconsistencies. '
                             'Create a new QuotaManager to define a new max quota.')

    @property
    def spent_quota(self) -> float:
        """Get the amount of quota already spent."""
        return self._spent_quota

    def spend_quota(self, amount: float):
        """Spend a portion of the quota if possible."""
        if not self.can_spend_quota(amount):
            raise ValueError(f'You have insufficient quota remaining to spend the amount: {amount}')
        self._spent_quota += amount

    def reset_quota(self):
        """Resets spent quota to zero"""
        self._spent_quota = 0

    def can_spend_quota(self, expense: float) -> bool:
        """Check if the quota can be spent without exceeding the max quota."""
        return (self._spent_quota + expense) <= self._max_quota




