# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
import csv

import requests

RS_URL = 'https://enter.tochka.com/sandbox/v2'

API_VERSION = 'v1.0'

ACCOUNT_ID = '40817810802000000008/044525104'

STATEMENT_ID = '58fc2a85-73ff-4c0c-9a9f-ca359267c8e4'

URL = f'{RS_URL}/open-banking/{API_VERSION}/accounts/{ACCOUNT_ID}/statements/{STATEMENT_ID}'

TOKEN = 'working_token'  # noqa: S105

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
}


def fetch_data(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_transactions(data: dict) -> list[dict]:
    transactions = []
    statements = data.get('Data', {}).get('Statement', [])

    for statement in statements:
        for transaction in statement.get('Transaction', []):
            transaction_id = transaction.get('transactionId')
            amount = transaction.get('Amount', {}).get('amount')
            currency = transaction.get('Amount', {}).get('currency')
            date = transaction.get('documentProcessDate')
            description = transaction.get('description')
            direction = transaction.get('creditDebitIndicator')

            if direction == 'Debit':
                counterparty = transaction.get('CreditorParty', {}).get('name')
            else:
                counterparty = transaction.get('DebtorParty', {}).get('name')

            transactions.append(
                {
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'currency': currency,
                    'date': date,
                    'counterparty': counterparty,
                    'transaction_description': description,
                    'transaction_direction': direction,
                }
            )

    return transactions


def write_to_csv(transactions: list[dict], filename: str) -> None:
    fieldnames = [
        'transaction_id',
        'amount',
        'currency',
        'date',
        'counterparty',
        'transaction_description',
        'transaction_direction',
    ]
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)


def main():
    data = fetch_data(URL)
    transactions = parse_transactions(data)
    write_to_csv(transactions, 'transactions.csv')


if __name__ == '__main__':
    main()
