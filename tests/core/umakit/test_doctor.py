"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

from umakit.doctor import format_diagnostics, run_diagnostics


def test_doctor_runs_without_crashing():
    checks, failures = run_diagnostics()
    assert isinstance(checks, list)
    assert isinstance(failures, int)
    assert len(checks) > 0
    for c in checks:
        assert "name" in c
        assert "status" in c
        assert c["status"] in ("ok", "fail", "warn", "skip")


def test_doctor_format_output():
    checks, _ = run_diagnostics()
    output = format_diagnostics(checks)
    assert "UMAKit Environment Diagnostic" in output
    assert isinstance(output, str)
    assert len(output) > 0


def test_doctor_with_nonexistent_model():
    checks, _ = run_diagnostics(model_path="/nonexistent/model.pt")
    model_check = [c for c in checks if c["name"] == "Model file"]
    assert len(model_check) == 1
    assert model_check[0]["status"] == "warn"
