# Re-export schemas from driver_personal_details for backward compatibility
from .driver_personal_details import (
    DriverPersonalDetailsResponse,
    DriverSummaryResponse,
    DriversListResponse,
    DriverAnalyticsResponse,
    PersonalDataSchema,
    RideHistorySchema,
    WalletTransactionSchema,
    SubscriptionSchema
)

__all__ = [
    "DriverPersonalDetailsResponse",
    "DriverSummaryResponse", 
    "DriversListResponse",
    "DriverAnalyticsResponse",
    "PersonalDataSchema",
    "RideHistorySchema",
    "WalletTransactionSchema",
    "SubscriptionSchema"
]