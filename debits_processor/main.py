from debits_processor.processor_wrapper import ProcessorWrapper
import requests
from credits_processor.consts.config import SERVER_ADDRESS
from credits_processor.consts.endpoints import GET_CREDITS, GET_TRANSACTIONS_CREDITS, INSERT_DEBIT, GET_DEBITS,\
    GET_TRANSACTIONS_DEBITS, GET_PROCESSED_DEBITS, INSERT_PROCESSED_DEBIT
import pandas as pd
from config import DEBITS_INTERVAL_DAYS, DEBITS_NUM, DATETIME_FORMAT, REPORT_TRANSACTIONS_TIME_WINDOW_DAYS
from models import Debit
from datetime import timedelta, datetime


def get_data_from_db(endpoint):
    response = requests.get(f'{SERVER_ADDRESS}/{endpoint}')
    data = response.json()
    data = pd.DataFrame.from_records(data)
    return data


def get_transactions_credits():
    return get_data_from_db(GET_TRANSACTIONS_CREDITS)


def get_transactions_debits():
    return get_data_from_db(GET_TRANSACTIONS_DEBITS)


def get_credits():
    return get_data_from_db(GET_CREDITS)


def get_debits():
    return get_data_from_db(GET_DEBITS)


def get_processed_debits():
    return get_data_from_db(GET_PROCESSED_DEBITS)


def get_successful_credits_ids(report):
    successful_transactions = report[report.is_successful]
    transactions_credits = get_transactions_credits()
    successful_credit_ids = successful_transactions.merge(transactions_credits, on='transaction_id').credit_id.tolist()
    stored_credits = get_credits()
    successful_credits = stored_credits[stored_credits.id.isin(successful_credit_ids)]
    return successful_credits


def get_credits_without_debits(credits_, debits):
    if len(debits) == 0:
        return credits_
    credits_with_debits = set(debits.credit_id.unique())
    credits_without_debits = credits_[~credits_.isin(credits_with_debits)]
    return credits_without_debits


def create_debits_from_credits(credits_):
    current_datetime = datetime.now()
    for _, credit in credits_.iterrows():
        debit_amount = credit.amount / DEBITS_NUM
        for debit_num in range(1, DEBITS_NUM + 1):
            due_date = (current_datetime + timedelta(days=DEBITS_INTERVAL_DAYS * debit_num)).strftime(DATETIME_FORMAT)
            debit = Debit(credit_id=credit.id, amount=debit_amount, due_date=due_date)
            requests.post(f"{SERVER_ADDRESS}/{INSERT_DEBIT}", json=debit.model_dump())


def get_old_debit_ids(transaction_debits, current_datetime):
    transaction_debits.creation_datetime = pd.to_datetime(transaction_debits.creation_datetime)
    datetime_limit = current_datetime - timedelta(days=REPORT_TRANSACTIONS_TIME_WINDOW_DAYS)
    df_filtered = transaction_debits[transaction_debits.creation_datetime < datetime_limit]
    return set(df_filtered.debit_id.tolist())


def get_timed_out_debits(report, current_datetime, debits, transactions_debits):
    old_debit_ids = get_old_debit_ids(transactions_debits, current_datetime)
    processed_transactions = get_processed_debits()
    processed_debits_ids = set(processed_transactions.id.tolist())
    reported_debits_ids = set(report.merge(transactions_debits, on='transaction_id').debit_id.tolist())
    timed_out_debit_ids = old_debit_ids - processed_debits_ids - reported_debits_ids
    timed_out_debits = debits[debits.id.isin(timed_out_debit_ids)]
    return timed_out_debits


def get_credits_last_due(debits):
    credits_ids_last_due = debits.groupby('credit_id').agg(last_due=('due', 'max')).reset_index()
    return credits_ids_last_due


def create_new_debits_from_timed_out_debits(report, current_datetime, debits, transactions_debits):
    timed_out_debits = get_timed_out_debits(report, current_datetime, debits, transactions_debits)
    credits_ids_last_due = get_credits_last_due(debits)
    timed_out_debits = timed_out_debits.merge(credits_ids_last_due, on='credit_id')
    timed_out_debits.due = pd.to_datetime(timed_out_debits.last_due)
    timed_out_debits.due = timed_out_debits.due + timedelta(days=DEBITS_INTERVAL_DAYS)
    timed_out_debits.due = timed_out_debits.due.apply(lambda x: x.strftime(DATETIME_FORMAT))
    for _, debit in timed_out_debits.iterrows():
        requests.post(f"{SERVER_ADDRESS}/{INSERT_DEBIT}", json=debit.model_dump())
        requests.post(f"{SERVER_ADDRESS}/{INSERT_PROCESSED_DEBIT}", json=debit.model_dump())


def process_debits_from_report(report, transaction_debits):
    """
    Go over debits in report.
    Add it to processed_debits
    If transaction for debit failed:
        Add new debit 1 week after the last debit of its credit
    :return:
    """
    pass


def perform_debit_transactions(debits, processed_debits, current_datetime):
    """
    Call processor to perform transaction for all debits with due_time before current_datetime and dont appear in
     processed_debits
    :param debits:
    :param processed_debits:
    :return:
    """

def main():
    current_datetime = datetime.now()
    report = ProcessorWrapper.download_report()
    debits = get_debits()
    transactions_debits = get_transactions_debits()
    successful_credits = get_successful_credits_ids(report)
    credits_without_debits = get_credits_without_debits(successful_credits, debits)
    create_debits_from_credits(credits_without_debits)
    create_new_debits_from_timed_out_debits(report, current_datetime, debits, transactions_debits)

    print()


if __name__ == "__main__":
    main()
