from __future__ import annotations

import pytest

from assayflux.diagnostics.model import SecurityError
from assayflux.quantum import run_circuit


def test_quantum_circuit_rejects_invalid_wire_count():
    with pytest.raises(SecurityError):
        run_circuit({"wires": 0, "gates": []})


def test_quantum_circuit_rejects_unknown_gate_before_loading_optional_dependency():
    with pytest.raises(SecurityError):
        run_circuit({"wires": 1, "gates": [{"gate": "EXEC", "wires": [0]}]})


def test_quantum_circuit_rejects_out_of_range_wires():
    with pytest.raises(SecurityError):
        run_circuit({"wires": 1, "gates": [{"gate": "H", "wires": [1]}]})
