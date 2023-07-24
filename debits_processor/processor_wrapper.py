from uuid import uuid4
from models import ReportRow
import requests
from credits_processor.consts.endpoints import UPDATE_REPORT, DOWNLOAD_REPORT
from credits_processor.consts.config import SERVER_ADDRESS
import pandas as pd


class ProcessorWrapper:
    @staticmethod
    def download_report():
        response = requests.get(f"{SERVER_ADDRESS}/{DOWNLOAD_REPORT}")
        report = pd.DataFrame.from_records(response.json())
        return report

    @staticmethod
    def perform_transaction(src_bank_account, dst_bank_account, amount, direction):
        transaction_id = str(uuid4())
        report_row = ReportRow(transaction_id=transaction_id, is_successful=True)
        requests.post(f"/{UPDATE_REPORT}", json=report_row.model_dump())
        return transaction_id


class PerformTransactionError(Exception):
    def __init__(self):
        super().__init__("The transaction failed because of an error in the black box!")
