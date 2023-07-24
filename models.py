from pydantic import BaseModel
from uuid import uuid4
from enum import Enum


class Credit(BaseModel):
    id: str = str(uuid4())
    acc_id: str
    amount: float
    creation_datetime: str


class Advance(BaseModel):
    dst_bank_account: str
    amount: float


class TransactionsCredits(BaseModel):
    transaction_id: str
    credit_id: str
    creation_datetime: str


class TransactionsDebits(BaseModel):
    transaction_id: str
    debit_id: str
    creation_datetime: str


class Direction(Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'


class ReportRow(BaseModel):
    transaction_id: str
    is_successful: bool


class Debit(BaseModel):
    id: str = str(uuid4())
    credit_id: str
    amount: float
    due_date: str


class ProcessedDebit(BaseModel):
    id: str
