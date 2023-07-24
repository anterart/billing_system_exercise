import pytest
from models import Advance
import requests
from credits_processor.consts.endpoints import GET_CREDITS, GET_TRANSACTIONS_CREDITS, PERFORM_ADVANCE
from credits_processor.consts.config import SERVER_ADDRESS


@pytest.mark.parametrize("advance",
                         [
                            Advance(dst_bank_account="1", amount="12"),
                         ])
def test__flow(advance):
    response = requests.get(f'{SERVER_ADDRESS}/{GET_CREDITS}')
    stored_credits = response.json()
    assert len(stored_credits) == 0

    response = requests.get(f'{SERVER_ADDRESS}/{GET_TRANSACTIONS_CREDITS}')
    transactions_credits = response.json()
    assert len(transactions_credits) == 0

    response = requests.post(f'{SERVER_ADDRESS}/{PERFORM_ADVANCE}', json=advance.model_dump())

    response = requests.get(f'{SERVER_ADDRESS}/{GET_CREDITS}')
    stored_credits = response.json()
    assert len(stored_credits) == 1

    response = requests.get(f'{SERVER_ADDRESS}/{GET_TRANSACTIONS_CREDITS}')
    transactions_credits = response.json()
    assert len(transactions_credits) == 1


