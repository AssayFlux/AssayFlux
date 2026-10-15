"""
Default language adapter loader for AssayFlux.

Registers all 30 supported language adapters.
An adapter is registered even if its external runtime
is unavailable; availability is checked separately.
"""

from functools import lru_cache

from assayflux.interop.registry import AdapterRegistry


@lru_cache(maxsize=1)
def get_default_registry() -> AdapterRegistry:
    """Create and cache the default adapter registry."""

    from assayflux.interop.adapters.python_adapter import PythonAdapter
    from assayflux.interop.adapters.javascript_adapter import JavaScriptAdapter
    from assayflux.interop.adapters.c_adapter import CAdapter
    from assayflux.interop.adapters.cpp_adapter import CppAdapter
    from assayflux.interop.adapters.java_adapter import JavaAdapter
    from assayflux.interop.adapters.rust_adapter import RustAdapter
    from assayflux.interop.adapters.typescript_adapter import TypeScriptAdapter
    from assayflux.interop.adapters.go_adapter import GoAdapter
    from assayflux.interop.adapters.kotlin_adapter import KotlinAdapter
    from assayflux.interop.adapters.csharp_adapter import CSharpAdapter
    from assayflux.interop.adapters.php_adapter import PHPAdapter
    from assayflux.interop.adapters.ruby_adapter import RubyAdapter
    from assayflux.interop.adapters.lua_adapter import LuaAdapter
    from assayflux.interop.adapters.perl_adapter import PerlAdapter
    from assayflux.interop.adapters.fortran_adapter import FortranAdapter
    from assayflux.interop.adapters.swift_adapter import SwiftAdapter
    from assayflux.interop.adapters.dart_adapter import DartAdapter
    from assayflux.interop.adapters.r_adapter import RAdapter
    from assayflux.interop.adapters.julia_adapter import JuliaAdapter
    from assayflux.interop.adapters.crystal_adapter import CrystalAdapter
    from assayflux.interop.adapters.scala_adapter import ScalaAdapter
    from assayflux.interop.adapters.elixir_adapter import ElixirAdapter
    from assayflux.interop.adapters.erlang_adapter import ErlangAdapter
    from assayflux.interop.adapters.haskell_adapter import HaskellAdapter
    from assayflux.interop.adapters.ocaml_adapter import OCamlAdapter
    from assayflux.interop.adapters.fsharp_adapter import FSharpAdapter
    from assayflux.interop.adapters.zig_adapter import ZigAdapter
    from assayflux.interop.adapters.nim_adapter import NimAdapter
    from assayflux.interop.adapters.d_adapter import DAdapter
    from assayflux.interop.adapters.cobol_adapter import COBOLAdapter

    registry = AdapterRegistry()

    adapters = (
        PythonAdapter(),
        JavaScriptAdapter(),
        CAdapter(),
        CppAdapter(),
        JavaAdapter(),
        RustAdapter(),
        TypeScriptAdapter(),
        GoAdapter(),
        KotlinAdapter(),
        CSharpAdapter(),
        PHPAdapter(),
        RubyAdapter(),
        LuaAdapter(),
        PerlAdapter(),
        FortranAdapter(),
        SwiftAdapter(),
        DartAdapter(),
        RAdapter(),
        JuliaAdapter(),
        CrystalAdapter(),
        ScalaAdapter(),
        ElixirAdapter(),
        ErlangAdapter(),
        HaskellAdapter(),
        OCamlAdapter(),
        FSharpAdapter(),
        ZigAdapter(),
        NimAdapter(),
        DAdapter(),
        COBOLAdapter(),
    )

    for adapter in adapters:
        registry.register(adapter)

    return registry


def get_adapter(language: str):
    """Retrieve an adapter by language name."""
    return get_default_registry().get(language)


def available_languages() -> tuple[str, ...]:
    """Return the languages whose runtimes are available."""
    return get_default_registry().available_languages()