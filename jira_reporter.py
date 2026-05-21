"""
jira_reporter.py
Crea bugs en Jira automáticamente con el análisis generado por Claude.
"""

import os
import asyncio
import aiohttp
import base64
from typing import Optional


JIRA_BASE_URL  = os.getenv("JIRA_BASE_URL",  "https://tu-empresa.atlassian.net")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL",     "")
JIRA_TOKEN     = os.getenv("JIRA_TOKEN",     "")
JIRA_PROJECT   = os.getenv("JIRA_PROJECT",   "QA")

SEVERITY_TO_PRIORITY = {
    "critical": "Highest",
    "high":     "High",
    "medium":   "Medium",
    "low":      "Low",
}


def _get_auth_header() -> str:
    credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    return "Basic " + base64.b64encode(credentials.encode()).decode()


def _build_jira_payload(failure: dict, env: str) -> dict:
    analysis = failure.get("claude_analysis", {})
    priority = analysis.get("priority", "Medium")

    return {
        "fields": {
            "project":     {"key": JIRA_PROJECT},
            "issuetype":   {"name": "Bug"},
            "summary":     f"[{env.upper()}] {analysis.get('jira_summary', failure['name'])}",
            "description": analysis.get("jira_description", "Sin descripción"),
            "priority":    {"name": priority},
            "labels":      analysis.get("labels", ["automated-qa"]) + ["qa-intelligence", env],
            "customfield_10016": _severity_to_story_points(analysis.get("severity", "medium")),
        }
    }


def _severity_to_story_points(severity: str) -> int:
    return {"critical": 8, "high": 5, "medium": 3, "low": 1}.get(severity, 3)


async def _create_single_bug(
    session: aiohttp.ClientSession,
    failure: dict,
    env: str
) -> Optional[dict]:
    """Crea un bug individual en Jira."""
    url     = f"{JIRA_BASE_URL}/rest/api/3/issue"
    payload = _build_jira_payload(failure, env)
    headers = {
        "Authorization": _get_auth_header(),
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                analysis = failure.get("claude_analysis", {})
                return {
                    "key":      data["key"],
                    "id":       data["id"],
                    "summary":  payload["fields"]["summary"],
                    "priority": payload["fields"]["priority"]["name"],
                    "severity": analysis.get("severity", "medium"),
                    "url":      f"{JIRA_BASE_URL}/browse/{data['key']}",
                }
            else:
                body = await resp.text()
                print(f"        ⚠ Jira error {resp.status} para {failure['id']}: {body[:100]}")
                return None

    except Exception as e:
        print(f"        ⚠ Error creando bug para {failure['id']}: {e}")
        return None


async def create_jira_bugs(analyzed_failures: list, env: str) -> list:
    """
    Crea bugs en Jira para todos los fallos analizados.
    Si no hay credenciales, simula la creación (modo demo).
    """
    if not JIRA_TOKEN or not JIRA_EMAIL:
        print("        ⚠ Credenciales Jira no configuradas — usando modo simulado")
        return _mock_jira_creation(analyzed_failures, env)

    created = []
    async with aiohttp.ClientSession() as session:
        tasks   = [_create_single_bug(session, f, env) for f in analyzed_failures]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r:
                created.append(r)
                print(f"        ✓ Creado {r['key']} [{r['priority']}] — {r['summary'][:55]}...")

    return created


def _mock_jira_creation(failures: list, env: str) -> list:
    """Simula creación de bugs en Jira para desarrollo y demos."""
    import random
    created = []

    for i, f in enumerate(failures, start=1):
        analysis = f.get("claude_analysis", {})
        key      = f"{JIRA_PROJECT}-{random.randint(100, 999)}"
        summary  = f"[{env.upper()}] {analysis.get('jira_summary', f['name'])}"

        bug = {
            "key":      key,
            "id":       str(1000 + i),
            "summary":  summary,
            "priority": analysis.get("priority", "Medium"),
            "severity": analysis.get("severity", "medium"),
            "url":      f"{JIRA_BASE_URL}/browse/{key}",
        }
        created.append(bug)
        print(f"        ✓ [MOCK] {key} [{bug['priority']}] — {summary[:55]}...")

    return created
