"""
QA Intelligence System — Orchestrator principal
Ejecuta tests con Playwright, analiza fallos con Claude API,
genera reporte ejecutivo y crea bugs en Jira automáticamente.
"""

import asyncio
import argparse
from datetime import datetime
from playwright_runner import run_tests
from claude_analyzer import analyze_failures
from jira_reporter import create_jira_bugs


async def main(env: str, suite: str):
    print(f"\n{'='*55}")
    print(f"  QA Intelligence System")
    print(f"  Entorno: {env.upper()} | Suite: {suite.upper()}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    # PASO 1: Ejecutar tests con Playwright
    print("[ 1/3 ] Ejecutando tests con Playwright...")
    results = await run_tests(env=env, suite=suite)

    total   = results["summary"]["total"]
    passed  = results["summary"]["passed"]
    failed  = results["summary"]["failed"]

    print(f"        Total: {total} | Passed: {passed} | Failed: {failed}\n")

    if failed == 0:
        print("✅ Todos los tests pasaron. No se generan bugs.")
        return

    # PASO 2: Analizar fallos con Claude API
    print("[ 2/3 ] Analizando fallos con Claude AI...")
    analyzed = await analyze_failures(results["failures"])
    print(f"        {len(analyzed)} fallo(s) analizados.\n")

    # PASO 3: Crear bugs en Jira con descripción generada por IA
    print("[ 3/3 ] Creando bugs en Jira...")
    created = await create_jira_bugs(analyzed, env=env)

    print(f"\n{'='*55}")
    print(f"  Resumen final")
    print(f"  Bugs creados en Jira: {len(created)}")
    for bug in created:
        print(f"  → {bug['key']}: {bug['summary']}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Intelligence System")
    parser.add_argument("--env",   default="staging",     choices=["staging", "prod"])
    parser.add_argument("--suite", default="smoke",        choices=["full", "smoke", "regression"])
    args = parser.parse_args()

    asyncio.run(main(env=args.env, suite=args.suite))
