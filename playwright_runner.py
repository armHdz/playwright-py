"""
playwright_runner.py
Ejecuta los tests de Playwright y devuelve resultados estructurados.
"""

import json
import subprocess
import tempfile
import os
from datetime import datetime


# Tests de ejemplo — en tu proyecto real estos son tus archivos .spec.py
#SUITES = {
#    "smoke": [
#        {"id": "TC-001", "name": "Login con credenciales válidas",         "file": "tests/auth/test_login.py"},
#        {"id": "TC-002", "name": "Carga de página principal",              "file": "tests/home/test_home.py"},
#        {"id": "TC-003", "name": "Búsqueda de producto",                   "file": "tests/search/test_search.py"},
#    ],
#    "regression": [
#        {"id": "TC-010", "name": "Flujo completo de checkout",             "file": "tests/checkout/test_checkout.py"},
#        {"id": "TC-011", "name": "Actualización de perfil de usuario",     "file": "tests/profile/test_profile.py"},
#        {"id": "TC-012", "name": "Filtros de búsqueda avanzada",           "file": "tests/search/test_filters.py"},
#        {"id": "TC-013", "name": "Notificaciones por email",               "file": "tests/notifications/test_email.py"},
#    ],
#    "full": [],  # Combina smoke + regression
#}
#SUITES["full"] = SUITES["smoke"] + SUITES["regression"]

SUITES = {
    "smoke": [
        {"id": "TC-001", "name": "Login válido",        "file": "tests/test_login.py"},
        {"id": "TC-002", "name": "Signup usuario nuevo", "file": "tests/test_signup.py"},
        {"id": "TC-003", "name": "Home page carga",      "file": "tests/test_categories.py"},
    ],
    "regression": [
        {"id": "TC-010", "name": "Agregar al carrito",   "file": "tests/test_cart.py"},
        {"id": "TC-011", "name": "Flujo checkout",       "file": "tests/test_checkout.py"},
        {"id": "TC-012", "name": "Formulario contacto",  "file": "tests/test_contact.py"},
    ],
}
SUITES["full"] = SUITES["smoke"] + SUITES["regression"]


async def run_tests(env: str, suite: str) -> dict:
    """
    Ejecuta la suite de tests y devuelve un dict con:
    - summary: total, passed, failed
    - failures: lista de fallos con detalle para Claude
    - passed_tests: lista de tests exitosos
    """
    test_cases = SUITES.get(suite, SUITES["smoke"])
    failures   = []
    passed     = []

    for tc in test_cases:
        result = run_single_test_real(tc, env)

        if result["status"] == "FAILED":
            failures.append(result)
        else:
            passed.append(result)

    return {
        "summary": {
            "total":      len(test_cases),
            "passed":     len(passed),
            "failed":     len(failures),
            "env":        env,
            "suite":      suite,
            "timestamp":  datetime.now().isoformat(),
        },
        "failures":     failures,
        "passed_tests": passed,
    }


#def _run_single_test(tc: dict, env: str) -> dict:
#    """
#    Aquí va tu lógica real de Playwright.
#    Por ahora simula resultados realistas para desarrollo/demo.
#    Reemplaza con: subprocess.run(["pytest", tc["file"], "--json-report"])
#    """
#    import random
    # En modo demo, simula ~40% de fallos para probar el sistema
#    status = "FAILED" if random.random() < 0.4 else "PASSED"

#    base = {
#        "id":     tc["id"],
#        "name":   tc["name"],
#        "file":   tc["file"],
#        "env":    env,
#        "status": status,
#        "duration_ms": random.randint(800, 4500),
#    }

#    if status == "FAILED":
        # Simula errores reales comunes en Playwright
#        error_samples = [
#            {
#                "error_type": "TimeoutError",
#                "message":    "Timeout 30000ms exceeded waiting for locator('#submit-btn')",
#                "stack_trace": (
#                    "TimeoutError: Timeout 30000ms exceeded.\n"
#                    f"  at {tc['file']}:47\n"
#                    "  Call log:\n"
#                    "  - waiting for locator('#submit-btn')\n"
#                    "  - locator resolved to <button disabled id='submit-btn'>Submit</button>"
#                ),
#                "screenshot": f"screenshots/{tc['id']}_failure.png",
#                "steps_before_failure": [
#                    "Navigate to /login",
#                    "Fill email field",
#                    "Fill password field",
#                    "Click submit button → TIMEOUT",
#                ],
#            },
#            {
#                "error_type": "AssertionError",
#                "message":    "Expected '200' but received '500' for GET /api/products",
#                "stack_trace": (
#                    f"AssertionError at {tc['file']}:82\n"
#                    "  Expected: status_code == 200\n"
#                    "  Actual:   status_code == 500\n"
#                    "  Response body: {'error': 'Internal Server Error', 'code': 'DB_CONNECTION_FAILED'}"
#                ),
#                "screenshot": f"screenshots/{tc['id']}_failure.png",
#                "steps_before_failure": [
#                    "Set auth headers",
#                    "GET /api/products?category=electronics",
#                    "Assert status 200 → FAILED (got 500)",
#                ],
#            },
#            {
#                "error_type": "ElementNotFound",
#                "message":    "Element '.product-card' not found after 10s",
#                "stack_trace": (
#                    f"Error at {tc['file']}:61\n"
#                    "  Locator('.product-card') returned 0 elements\n"
#                    "  Page title at failure: 'Error 404 – Page not found'\n"
#                    "  Current URL: https://staging.app.com/products/undefined"
#                ),
#                "screenshot": f"screenshots/{tc['id']}_failure.png",
#                "steps_before_failure": [
#                    "Navigate to /products",
#                    "Apply filter: category=electronics",
#                    "Wait for product grid → NOT FOUND",
#                ],
#            },
#        ]
#        base["failure_detail"] = random.choice(error_samples)
#
#    return base


# ─── USO REAL (descomentar para producción) ───────────────────────────────────

def run_single_test_real(tc: dict, env: str) -> dict:
    """Ejecuta un test real con pytest + playwright y captura el resultado."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        report_path = f.name

    cmd = [
        "pytest", tc["file"],
        "--json-report", f"--json-report-file={report_path}",
        "-v", "--tb=short",
        f"--base-url=https://{env}.tuapp.com",
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    with open(report_path) as f:
        report = json.load(f)

    os.unlink(report_path)
    test = report["tests"][0]

    result = {
        "id":          tc["id"],
        "name":        tc["name"],
        "file":        tc["file"],
        "env":         env,
        "status":      "PASSED" if test["outcome"] == "passed" else "FAILED",
        "duration_ms": int(test["duration"] * 1000),
    }
    if result["status"] == "FAILED":
        result["failure_detail"] = {
            "error_type":  test.get("call", {}).get("longrepr", "")[:50],
            "message":     test.get("call", {}).get("longrepr", ""),
            "stack_trace": test.get("call", {}).get("longrepr", ""),
         }
    return result