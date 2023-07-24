from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
from models import Advance, Credit, TransactionsCredits, Direction, ReportRow, Debit, TransactionsDebits,\
    ProcessedDebit
from credits_processor.consts.endpoints import PERFORM_ADVANCE, GET_CREDITS, GET_TRANSACTIONS_CREDITS, DOWNLOAD_REPORT,\
    UPDATE_REPORT, GET_DEBITS, GET_TRANSACTIONS_DEBITS, INSERT_DEBIT, GET_PROCESSED_DEBITS, INSERT_PROCESSED_DEBIT
from credits_processor.consts.config import SYSTEM_BANK_ACCOUNT_ID
from credits_processor.processor_wrapper import ProcessorWrapper, PerformTransactionError, report
from config import DATETIME_FORMAT

app = FastAPI()

client_credits: List[Credit] = []
transactions_credits: List[TransactionsCredits] = []
debits: List[Debit] = []
transactions_debits: List[TransactionsDebits] = []
processed_debits: List[ProcessedDebit] = []


@app.post(f"/{PERFORM_ADVANCE}")
def perform_advance(advance: Advance):
    current_datetime = datetime.now()
    credit = Credit(acc_id=advance.dst_bank_account, amount=advance.amount,
                    creation_datetime=current_datetime.strftime(DATETIME_FORMAT))
    transaction_id = ProcessorWrapper.perform_transaction(SYSTEM_BANK_ACCOUNT_ID, advance.dst_bank_account,
                                                          advance.amount, Direction.CREDIT.value)
    try:
        transaction_credit = TransactionsCredits(transaction_id=transaction_id, credit_id=credit.id,
                                                 creation_datetime=current_datetime.strftime(DATETIME_FORMAT))
        transactions_credits.append(transaction_credit)
        client_credits.append(credit)
        return {"message": f"Transaction of {advance.amount} for {advance.dst_bank_account} scheduled."}
    except PerformTransactionError as e:
        raise HTTPException(status_code=500, detail='There was a problem with processing the credit!')


@app.get(f"/{GET_TRANSACTIONS_CREDITS}")
def get_transactions_credits():
    return transactions_credits


@app.get(f"/{GET_TRANSACTIONS_DEBITS}")
def get_transactions_debits():
    return transactions_debits


@app.get(f"/{GET_CREDITS}")
def get_credits():
    return client_credits


@app.get(f"/{DOWNLOAD_REPORT}")
def download_report():
    return report


@app.post(f"/{UPDATE_REPORT}")
def update_report(report_row: ReportRow):
    report.append(report_row)


@app.get(f"/{GET_DEBITS}")
def get_debits():
    return debits


@app.post(f"/{INSERT_DEBIT}")
def insert_debit(debit: Debit):
    debits.append(debit)


@app.get(f"/{GET_PROCESSED_DEBITS}")
def get_processed_debits():
    return processed_debits


@app.post(f"/{INSERT_PROCESSED_DEBIT}")
def insert_processed_debit(debit: Debit):
    processed_debit = ProcessedDebit(id=debit.id)
    processed_debits.append(processed_debit)

