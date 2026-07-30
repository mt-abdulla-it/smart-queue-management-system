"""
Priority Queue Triage & Anti-Starvation Engine.

Manages dynamic weight recalculation and queue reordering based on
triage priority levels and elapsed waiting time to prevent token starvation.
"""
from datetime import datetime
from django.utils import timezone
from typing import List
from apps.queues.models import QueueToken


class PriorityQueueManager:
    """Calculates weighted priority and manages queue reordering."""

    BASE_WEIGHTS = {
        QueueToken.TriageLevel.EMERGENCY: 100,
        QueueToken.TriageLevel.ELDERLY_DISABLED: 50,
        QueueToken.TriageLevel.PRIORITY: 30,
        QueueToken.TriageLevel.REGULAR: 10,
    }

    # Anti-starvation bonus: +5 priority weight for every 15 minutes waiting
    STARVATION_INTERVAL_MINUTES = 15
    STARVATION_BONUS_WEIGHT = 5

    @classmethod
    def calculate_effective_weight(cls, token: QueueToken) -> int:
        """
        Calculate effective priority weight incorporating base triage weight
        and anti-starvation age bonus.
        """
        base = cls.BASE_WEIGHTS.get(token.triage_level, 10)
        if token.is_priority and token.triage_level == QueueToken.TriageLevel.REGULAR:
            base = cls.BASE_WEIGHTS[QueueToken.TriageLevel.PRIORITY]

        now = timezone.now()
        minutes_waiting = max(0, int((now - token.booked_at).total_seconds() / 60))
        starvation_bonus = (minutes_waiting // cls.STARVATION_INTERVAL_MINUTES) * cls.STARVATION_BONUS_WEIGHT

        return base + starvation_bonus

    @classmethod
    def reorder_branch_queue(cls, branch_id: int, service_id: int, queue_date=None) -> List[QueueToken]:
        """
        Re-evaluates waiting tokens for a branch/service and updates positions dynamically.
        """
        if queue_date is None:
            queue_date = timezone.now().date()

        waiting_tokens = list(
            QueueToken.objects.filter(
                branch_id=branch_id,
                service_id=service_id,
                queue_date=queue_date,
                status=QueueToken.Status.WAITING
            )
        )

        # Sort tokens descending by effective weight, then ascending by booked_at timestamp
        sorted_tokens = sorted(
            waiting_tokens,
            key=lambda t: (-cls.calculate_effective_weight(t), t.booked_at)
        )

        # Update position ordering in database
        updated_tokens = []
        for index, token in enumerate(sorted_tokens, start=1):
            if token.position != index or token.priority_weight != cls.calculate_effective_weight(token):
                token.position = index
                token.priority_weight = cls.calculate_effective_weight(token)
                token.save(update_fields=['position', 'priority_weight'])
                updated_tokens.append(token)

        return sorted_tokens
