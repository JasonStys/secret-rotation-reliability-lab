"""Independent lease/policy boundary and fuzz/property tests; all values fictional. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: lease — line 31
# parameter: changes — line 31
# definition: test_number — line 51
# parameter: bad — line 51
# definition: test_secret — line 58
# parameter: bad — line 58
# definition: test_policy — line 76
# parameter: change — line 76
# definition: test_lease_contract — line 95
# parameter: change — line 95
# definition: test_lifetime_and_repr — line 101
# variable: value — line 103
# definition: test_expired_never_usable — line 118
# parameter: elapsed — line 118
# parameter: ttl — line 118
# definition: test_error_contract — line 123
# variable: args — line 125
# END CODE MAP

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rotation.contracts import Lease, Policy, ProviderError, number, secret


def lease(**changes):
    """Construct a bounded synthetic lease; callers change one field to exercise validation."""
    return Lease(
        **(
            {
                "lease_id": "database/creds/reader/fictional",
                "username": "fictional-user",
                "password": "fictional-password",
                "started_at": 100,
                "ttl": 10,
                "renewable": True,
            }
            | changes
        )
    )


@pytest.mark.parametrize(
    "bad", [True, False, None, "1", [], {}, float("nan"), float("inf"), -1, 101]
)
def test_number(bad):
    """Bool/type/nonfinite/out-of-bounds values cannot impersonate numeric policy settings."""
    with pytest.raises(ValueError):
        number(bad, 0, 100)


@pytest.mark.parametrize("bad", ["", "a\n", "é", "a b", "x" * 513, None, 7])
def test_secret(bad):
    """Malformed credential fields are rejected without echoing their content."""
    with pytest.raises(ValueError, match="invalid credential field"):
        secret(bad)


@pytest.mark.parametrize(
    "change",
    [
        {"attempts": True},
        {"attempts": 0},
        {"attempts": 4},
        {"refresh_fraction": 1},
        {"expiry_guard": 0},
        {"base_delay": -1},
        {"max_delay": 0.001},
    ],
)
def test_policy(change):
    """All policy fields enforce their independent retry/lifetime constraints."""
    with pytest.raises(ValueError):
        Policy(**change)


@pytest.mark.parametrize(
    "change",
    [
        {"lease_id": "sys/admin/id"},
        {"username": ""},
        {"password": "bad\r"},
        {"started_at": -1},
        {"ttl": True},
        {"ttl": 2},
        {"ttl": 3601},
        {"renewable": 1},
    ],
)
def test_lease_contract(change):
    """Unexpected namespaces and malformed provider fields fail closed."""
    with pytest.raises(ValueError):
        lease(**change)


def test_lifetime_and_repr():
    """Strict boundary, conservative guard, rollback and redacted representations are independent oracles."""
    value = lease()
    assert value.usable(100, 1) and value.usable(108.99, 1)
    assert not value.usable(109, 1) and not value.usable(99, 1)
    assert not value.refresh_due(105.9, Policy()) and value.refresh_due(106, Policy())
    assert value.refresh_due(99, Policy())
    assert "fictional-user" not in repr(value) and "fictional-password" not in repr(
        value
    )
    assert value.refresh_due(101, Policy(expiry_guard=9))


@given(
    st.integers(min_value=3, max_value=3600),
    st.floats(min_value=0, max_value=5000, allow_nan=False, allow_infinity=False),
)
def test_expired_never_usable(ttl, elapsed):
    """Property oracle: no nonnegative elapsed lifetime can cross the strict expiry guard."""
    assert lease(ttl=ttl).usable(100 + elapsed, 1) == (elapsed < ttl - 1)


def test_error_contract():
    """Only allowlisted transient failures can retry; raw messages cannot become log categories."""
    for args in [
        ("secret-content", False),
        ("denied", True),
        ("tls", True),
        ("invalid", True),
        ("unavailable", 1),
    ]:
        with pytest.raises(ValueError):
            ProviderError(*args)
    assert str(ProviderError("unavailable", True)) == "unavailable"
    assert number(3, 0, 4) == 3 and math.isfinite(number(2.5, 0, 4))
