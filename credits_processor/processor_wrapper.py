"""
A wrapper for processor blackbox in order to test the code
"""


from uuid import uuid4
from models import ReportRow
from typing import List


report: List[ReportRow] = []


class ProcessorWrapper:
    @staticmethod
    def download_report():
        return report

    @staticmethod
    def perform_transaction(src_bank_account, dst_bank_account, amount, direction):
        transaction_id = str(uuid4())
        report.append(ReportRow(transaction_id=transaction_id, is_successful=True))
        return transaction_id


class PerformTransactionError(Exception):
    def __init__(self):
        super().__init__("The transaction failed because of an error in the black box!")
