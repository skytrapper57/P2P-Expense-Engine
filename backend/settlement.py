"""
settlement.py - the core "Graph Cleansing" engine of the P2P Expense Engine.

Pipeline:  expenses -> debts -> net balances -> minimized settlements
"""
from decimal import Decimal, ROUND_DOWN

CENT = Decimal("0.01")


def split_equally(paid_by, amount, participants):
    """
    Split one expense equally among participants.
    Returns a list of debts: (debtor, creditor, amount).

    Example: Arun paid 100 for [Arun, naman, manav]
      -> naman owes Arun 33.34, manav owes Arun 33.33
      (Arun's own share is not a debt - she owes herself nothing.)
    """
    amount = Decimal(str(amount))
    n = len(participants)

    share = (amount / n).quantize(CENT, rounding=ROUND_DOWN)  # 33.33
    leftover = amount - share * n                             # 0.01
    extra_cents = int(leftover / CENT)                        # how many people pay +0.01

    debts = []
    for i, person in enumerate(participants):
        person_share = share + (CENT if i < extra_cents else Decimal("0"))
        if person != paid_by:
            debts.append((person, paid_by, person_share))
    return debts


def compute_net_balances(debts):
    """
    Net balance per person.
      positive -> the group owes them money
      negative -> they owe the group money
    """
    balances = {}
    for debtor, creditor, amount in debts:
        amount = Decimal(str(amount))
        balances[debtor] = balances.get(debtor, Decimal("0")) - amount
        balances[creditor] = balances.get(creditor, Decimal("0")) + amount
    return balances


def minimize_settlements(balances):
    """
    Greedy cash-flow algorithm (FR-13).
    Repeatedly: biggest debtor pays biggest creditor min(their amounts).
    Each payment settles at least one person fully, so for n people
    with non-zero balances it needs at most n-1 payments.
    """
    balances = dict(balances)  # copy, so we don't change the caller's data
    settlements = []

    while True:
        debtor = min(balances, key=balances.get)    # most negative
        creditor = max(balances, key=balances.get)  # most positive

        if balances[debtor] == 0 or balances[creditor] == 0:
            break  # everyone is settled

        pay = min(-balances[debtor], balances[creditor])
        settlements.append({"from": debtor, "to": creditor, "amount": pay})

        balances[debtor] += pay
        balances[creditor] -= pay

    return settlements


def settle_expenses(expenses):
    """
    expenses: list of dicts like
      {"paid_by": "Arun", "amount": 1200, "participants": ["Arun", "naman"]}
    Returns (net_balances, settlements).
    """
    all_debts = []
    for e in expenses:
        all_debts += split_equally(e["paid_by"], e["amount"], e["participants"])

    balances = compute_net_balances(all_debts)
    return balances, minimize_settlements(balances)


if __name__ == "__main__":
    demo = [
        {"paid_by": "Arun", "amount": 1200, "participants": ["Arun", "naman", "manav"]},
        {"paid_by": "naman", "amount": 600, "participants": ["naman", "manav"]},
    ]
    balances, settlements = settle_expenses(demo)
    print("Balances:", {k: str(v) for k, v in balances.items()})
    for s in settlements:
        print(f"{s['from']} pays {s['to']} Rs {s['amount']}")
