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


def test_bell_state_probabilities_on_local_simulator():
    pytest.importorskip("pennylane")
    result = run_circuit({
        "wires": 2,
        "gates": [
            {"gate": "H", "wires": [0]},
            {"gate": "CNOT", "wires": [0, 1]},
        ],
        "shots": None,
    })
    assert result["device"] == "default.qubit"
    assert result["measurement"] == "probabilities"
    assert result["probabilities"] == pytest.approx([0.5, 0.0, 0.0, 0.5], abs=1e-6)
