"""Optional local quantum simulator adapter backed by PennyLane.

This adapter deliberately supports a small, validated circuit schema rather than
executing arbitrary Python. PennyLane is imported lazily and is an optional extra.
"""
from __future__ import annotations

from typing import Any

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError

_MAX_WIRES = 16
_MAX_SHOTS = 100_000
_MAX_GATES = 1_000
_SINGLE_WIRE = {"I", "X", "Y", "Z", "H", "Hadamard", "PauliX", "PauliY", "PauliZ"}
_TWO_WIRE = {"CNOT", "CX", "CZ", "SWAP"}
_ROTATIONS = {"RX", "RY", "RZ"}


def list_devices() -> list[dict[str, Any]]:
    """Report the supported local simulator without probing hardware."""
    try:
        import pennylane as qml
    except ImportError as exc:
        raise RuntimeErrorAF(
            "Quantum support is not installed",
            details="Install AssayFlux with its optional quantum dependency on Python 3.12+.",
            suggestion="Install the 'quantum' extra, then retry.",
        ) from exc
    return [{
        "name": "default.qubit",
        "provider": "pennylane",
        "kind": "local-simulator",
        "available": True,
        "pennylane_version": getattr(qml, "__version__", "unknown"),
    }]


def run_circuit(circuit: dict[str, Any]) -> dict[str, Any]:
    """Run a validated circuit on PennyLane's local default.qubit simulator.

    Circuit schema: {"wires": 2, "gates": [{"gate": "H", "wires": [0]}],
    "shots": null}. Measurements return the computational-basis probabilities.
    """
    if not isinstance(circuit, dict):
        raise SecurityError("Quantum circuit must be a JSON object")
    wires = circuit.get("wires")
    gates = circuit.get("gates", [])
    shots = circuit.get("shots")
    if not isinstance(wires, int) or isinstance(wires, bool) or not 1 <= wires <= _MAX_WIRES:
        raise SecurityError(f"Quantum wire count must be an integer from 1 to {_MAX_WIRES}")
    if not isinstance(gates, list) or len(gates) > _MAX_GATES:
        raise SecurityError(f"Quantum gates must be a list with at most {_MAX_GATES} entries")
    if shots is not None and (
        not isinstance(shots, int) or isinstance(shots, bool) or not 1 <= shots <= _MAX_SHOTS
    ):
        raise SecurityError(f"Shots must be null or an integer from 1 to {_MAX_SHOTS}")

    validated: list[tuple[str, list[int], list[float]]] = []
    for index, item in enumerate(gates):
        if not isinstance(item, dict):
            raise SecurityError(f"Gate {index} must be an object")
        name = item.get("gate")
        target_wires = item.get("wires")
        params = item.get("params", [])
        if not isinstance(name, str) or name not in _SINGLE_WIRE | _TWO_WIRE | _ROTATIONS:
            raise SecurityError(f"Unsupported quantum gate at index {index}")
        expected = 2 if name in _TWO_WIRE else 1
        if (
            not isinstance(target_wires, list) or len(target_wires) != expected
            or any(not isinstance(w, int) or isinstance(w, bool) or not 0 <= w < wires for w in target_wires)
            or len(set(target_wires)) != len(target_wires)
        ):
            raise SecurityError(f"Invalid wire targets for gate {index}")
        if not isinstance(params, list) or (len(params) != 1 if name in _ROTATIONS else len(params) != 0):
            raise SecurityError(f"Invalid parameters for gate {index}")
        if any(not isinstance(p, (int, float)) or isinstance(p, bool) for p in params):
            raise SecurityError(f"Gate parameters must be numeric at index {index}")
        validated.append((name, target_wires, [float(p) for p in params]))

    try:
        import pennylane as qml
    except ImportError as exc:
        raise RuntimeErrorAF(
            "Quantum support is not installed",
            details="PennyLane is an optional dependency and requires Python 3.12+.",
            suggestion="Install the 'quantum' extra in a Python 3.12+ environment.",
        ) from exc

    device = qml.device("default.qubit", wires=wires, shots=shots)

    @qml.qnode(device)
    def circuit_node():
        for name, target_wires, params in validated:
            operation = {
                "I": qml.Identity, "X": qml.PauliX, "PauliX": qml.PauliX,
                "Y": qml.PauliY, "PauliY": qml.PauliY, "Z": qml.PauliZ,
                "PauliZ": qml.PauliZ, "H": qml.Hadamard, "Hadamard": qml.Hadamard,
                "CNOT": qml.CNOT, "CX": qml.CNOT, "CZ": qml.CZ, "SWAP": qml.SWAP,
                "RX": qml.RX, "RY": qml.RY, "RZ": qml.RZ,
            }[name]
            operation(*params, wires=target_wires)
        return qml.probs(wires=range(wires))

    try:
        probabilities = circuit_node()
        values = probabilities.tolist()
    except Exception as exc:
        raise RuntimeErrorAF(
            "Quantum circuit execution failed",
            details=type(exc).__name__,
            suggestion="Check the circuit schema and local simulator installation.",
        ) from exc
    return {
        "provider": "pennylane",
        "device": "default.qubit",
        "wires": wires,
        "shots": shots,
        "measurement": "probabilities",
        "probabilities": [float(value) for value in values],
        "metadata": {"gate_count": len(validated), "simulator": "local"},
    }
