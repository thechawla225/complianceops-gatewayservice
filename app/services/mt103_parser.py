
import re
from fastapi import HTTPException
from app.schemas.transaction import * 
 
TAG_PATTERN = re.compile(r"^:([0-9]{2}[A-Z]?):(.*)$")
AMOUNT_TAG_PATTERN = re.compile(r"^\d{6}([A-Z]{3})([\d,]+)$")
REQUIRED_TAGS = {"20", "32A", "50K", "59"}
 
 
def parse_mt103(raw_text: str) -> Transaction:
    tags: dict[str, str] = {}
 
    for line in raw_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = TAG_PATTERN.match(line)
        if not match:
            raise HTTPException(status_code=400, detail=f"unrecognized MT103 line: {line!r}")
        tag, value = match.group(1), match.group(2).strip()
        tags[tag] = value
 
    missing = REQUIRED_TAGS - tags.keys()
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"MT103 message missing required tag(s): {', '.join(sorted(missing))}",
        )
 
    return Transaction(
        endToEndId=tags["20"],
        debtor=Debtor(name=tags["50K"], agentBic=tags.get("52A")),
        creditor=Creditor(name=tags["59"], agentBic=tags.get("57A")),
        instructedAmount=_parse_amount_tag(tags["32A"]),
        remittanceInformation=tags.get("70"),
    )
 
 
def _parse_amount_tag(raw: str) -> InstructedAmount:
    match = AMOUNT_TAG_PATTERN.match(raw)
    if not match:
        raise HTTPException(
            status_code=400,
            detail=f"malformed :32A: value: {raw!r} (expected YYMMDDCCCAMOUNT, e.g. 260831USD1000,00)",
        )
    currency, amount_raw = match.groups()
    whole, _, frac = amount_raw.replace(",", ".").partition(".")
    frac = (frac + "00")[:2]
    return InstructedAmount(amount=f"{whole}.{frac}", currency=currency)
 