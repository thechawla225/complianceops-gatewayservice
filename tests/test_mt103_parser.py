import pytest
from fastapi import HTTPException
from app.services.mt103_parser import parse_mt103

VALID_MT103 = """
:20:REF20260831001
:32A:260831USD1000,00
:50K:ACME EXPORTS LTD
:52A:BARCGB22
:59:EXAMPLE TRADING CO
:57A:DEUTDEFF
:70:INVOICE 4471
"""


def test_parses_full_message():
    tx = parse_mt103(VALID_MT103)
    assert tx.endToEndId == "REF20260831001"
    assert tx.debtor.name == "ACME EXPORTS LTD"
    assert tx.debtor.agentBic == "BARCGB22"
    assert tx.creditor.name == "EXAMPLE TRADING CO"
    assert tx.creditor.agentBic == "DEUTDEFF"
    assert tx.instructedAmount.amount == "1000.00"
    assert tx.instructedAmount.currency == "USD"
    assert tx.remittanceInformation == "INVOICE 4471"


def test_optional_tags_can_be_absent():
    minimal = ":20:REF1\n:32A:260831USD500,5\n:50K:PAYER\n:59:PAYEE"
    tx = parse_mt103(minimal)
    assert tx.debtor.agentBic is None
    assert tx.creditor.agentBic is None
    assert tx.remittanceInformation is None
    assert tx.instructedAmount.amount == "500.50"


def test_missing_required_tag_raises_400():
    missing_creditor = ":20:REF1\n:32A:260831USD1000,00\n:50K:PAYER"
    with pytest.raises(HTTPException) as exc_info:
        parse_mt103(missing_creditor)
    assert exc_info.value.status_code == 400
    assert "59" in exc_info.value.detail


def test_unrecognized_line_raises_400():
    garbled = ":20:REF1\nNOT A TAG LINE\n:32A:260831USD1000,00\n:50K:PAYER\n:59:PAYEE"
    with pytest.raises(HTTPException) as exc_info:
        parse_mt103(garbled)
    assert exc_info.value.status_code == 400


def test_malformed_amount_raises_400():
    bad_amount = ":20:REF1\n:32A:not-an-amount\n:50K:PAYER\n:59:PAYEE"
    with pytest.raises(HTTPException) as exc_info:
        parse_mt103(bad_amount)
    assert exc_info.value.status_code == 400
    assert "32A" in exc_info.value.detail