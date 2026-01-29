from enum import Enum


class ReasonCode(str, Enum):
    HIGH_TRANSACTION_VELOCITY = "high_transaction_velocity"
    UNUSUAL_AMOUNT = "unusual_transaction_amount"

    DISTRESS_LANGUAGE = "distress_language_detected"
    REPEAT_COMPLAINT = "repeat_complaint"
    MISLEADING_INFORMATION = "misleading_information"

    ACCOUNT_BEHAVIOR_CHANGE = "account_behavior_change"