from decimal import Decimal
from settlement import split_equally, compute_net_balances, minimize_settlements


def test_middleman_is_removed():
    # Arun -> naman 500, naman -> manav 500  ==>  Arun -> manav 500
    debts = [("Arun", "naman", 500), ("naman", "manav", 500)]
    balances = compute_net_balances(debts)
    assert balances["naman"] == 0
    result = minimize_settlements(balances)
    assert len(result) == 1
    assert result[0]["from"] == "Arun" and result[0]["to"] == "manav"


def test_split_never_loses_a_paisa():
    debts = split_equally("Arun", 100, ["Arun", "naman", "manav"])
    # naman + manav owe 100 - Arun's own share (33.34)
    assert sum(d[2] for d in debts) == Decimal("66.66")


def test_balances_sum_to_zero():
    debts = [("A", "B", 70), ("B", "C", 20), ("C", "A", 5)]
    assert sum(compute_net_balances(debts).values()) == 0


if __name__ == "__main__":
    test_middleman_is_removed()
    test_split_never_loses_a_paisa()
    test_balances_sum_to_zero()
    print("All tests passed")
