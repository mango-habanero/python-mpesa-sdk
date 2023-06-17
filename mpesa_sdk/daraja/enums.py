"""This module contains enums used in the M-Pesa API."""

# standard imports
import enum


class TransactionType(enum.Enum):
    """This class contains enums for transaction types."""

    CUSTOMER_BUY_GOODS_ONLINE = "CustomerBuyGoodsOnline"
    CUSTOMER_PAY_BILL_ONLINE = "CustomerPayBillOnline"


class CommandID(enum.Enum):
    """This class contains enums for command IDs."""

    BUSINESS_PAYMENT = "BusinessPayment"
    PROMOTION_PAYMENT = "PromotionPayment"
    SALARY_PAYMENT = "SalaryPayment"
    TRANSACTION_REVERSAL = "TransactionReversal"
    TRANSACTION_STATUS_QUERY = "TransactionStatusQuery"


class IdentifierType(enum.Enum):
    """This class contains enums for identifier types."""

    MSISDN = "1"
    TILL_NUMBER = "2"
    ORGANIZATION_SHORT_CODE = "4"
