"""
claude_analyzer.py
Envía cada fallo a Claude API y recibe:
- Diagnóstico de causa raíz
- Fix sugerido
- Severidad
- Reporte ejecutivo listo para Jira
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
API_URL           = "https://api.anthropic.com/v1/messages"
MODEL             = "claude-sonnet-4-20250514"


SYSTEM_PROMPT = """Eres un experto en QA automation con 10 años de experiencia.
Cuando recibas el detalle de un test fallido, responde ÚNICAMENTE con un JSON válido
(sin backticks, sin texto adicional) con esta estructura exacta:

{
  "root_cause": "Descripción técnica concisa de la causa raíz (1-2 oraciones)",
  "severity": "critical|high|medium|low",
  "suggested_fix": "Pasos concretos para resolver el problema (máximo 3 pasos)",
  "jira_summary": "Título del bug para Jira (máximo 80 caracteres)",
  "jira_description": "Descripción completa del bug en formato Jira con secciones: *Ambiente*, *Pasos para reproducir*, *Resultado esperado*, *Resultado actual*, *Causa probable*, *Fix sugerido*",
  "labels": ["lista", "de", "labels", "para", "jira"],
  "priority": "Highest|High|Medium|Low"
}"""


def _build_user_prompt(failure: dict) -> str:
    detail = failure.get("failure_detail", {})
    steps  = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(detail.get("steps_before_failure", [])))

    return f"""Analiza este test fallido y genera el reporte:

TEST ID:     {failure['id']}
NOMBRE:      {failure['name']}
AMBIENTE:    {failure['env']}
ARCHIVO:     {failure['file']}
DURACIÓN:    {failure['duration_ms']}ms

ERROR TYPE:  {detail.get('error_type', 'Unknown')}
MENSAJE:     {detail.get('message', 'Sin mensaje')}

STACK TRACE:
{detail.get('stack_trace', 'No disponible')}

PASOS ANTES DEL FALLO:
{steps}
"""


async def _call_claude(session: aiohttp.ClientSession, failure: dict) -> Optional[dict]:
    """Llama a Claude API para un fallo individual."""
    payload = {
        "model":      MODEL,
        "max_tokens": 1000,
        "system":     SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": _build_user_prompt(failure)}
        ],
    }

    headers = {
        "Content-Type":      "application/json",
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }

    try:
        async with session.post(API_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                print(f"        ⚠ Claude API error {resp.status} para {failure['id']}")
                return None

            data = await resp.json()
            raw  = data["content"][0]["text"].strip()

            # Limpia posibles backticks si el modelo los incluye
            raw = raw.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(raw)

            return {**failure, "claude_analysis": analysis}

    except (json.JSONDecodeError, KeyError) as e:
        print(f"        ⚠ Error parseando respuesta de Claude para {failure['id']}: {e}")
        return None
    except Exception as e:
        print(f"        ⚠ Error inesperado para {failure['id']}: {e}")
        return None


async def analyze_failures(failures: list) -> list:
    """
    Analiza todos los fallos en paralelo con Claude API.
    Devuelve lista de fallos enriquecidos con el análisis.
    """
    if not ANTHROPIC_API_KEY:
        print("        ⚠ ANTHROPIC_API_KEY no configurada — usando análisis simulado")
        return _mock_analysis(failures)

    analyzed = []
    async with aiohttp.ClientSession() as session:
        tasks = [_call_claude(session, f) for f in failures]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r:
                analyzed.append(r)
                print(f"        ✓ {r['id']} — {r['claude_analysis']['severity'].upper()}: {r['claude_analysis']['root_cause'][:60]}...")

    return analyzed


def _mock_analysis(failures: list) -> list:
    """
    Análisis simulado para desarrollo sin API key.
    Útil para construir y testear el flujo completo primero.
    """
    mock_responses = {
        "TimeoutError": {
            "root_cause":        "El botón #submit-btn está deshabilitado en staging, probablemente por una feature flag o validación pendiente del lado del servidor.",
            "severity":          "high",
            "suggested_fix":     "1. Verificar feature flags en staging. 2. Revisar validaciones del form antes del submit. 3. Aumentar timeout a 60s como medida temporal.",
            "jira_summary":      "Submit button disabled unexpectedly in staging — login flow broken",
            "jira_description":  "*Ambiente:* Staging\n\n*Pasos para reproducir:*\n1. Ir a /login\n2. Ingresar credenciales válidas\n3. Intentar hacer click en Submit\n\n*Resultado esperado:* Login exitoso\n\n*Resultado actual:* Timeout 30s — botón disabled\n\n*Causa probable:* Feature flag activo en staging deshabilitando el submit\n\n*Fix sugerido:* Revisar feature flags y validaciones previas al submit",
            "labels":            ["login", "staging", "timeout", "blocker"],
            "priority":          "High",
        },
        "AssertionError": {
            "root_cause":        "El endpoint GET /api/products retorna 500 con DB_CONNECTION_FAILED, indicando problema de conectividad con la base de datos en staging.",
            "severity":          "critical",
            "suggested_fix":     "1. Revisar logs del servidor de base de datos en staging. 2. Verificar connection pool y credenciales de DB. 3. Reiniciar servicio de API si el pool está saturado.",
            "jira_summary":      "API /products returns 500 DB_CONNECTION_FAILED in staging",
            "jira_description":  "*Ambiente:* Staging\n\n*Pasos para reproducir:*\n1. Hacer GET /api/products?category=electronics con auth válida\n\n*Resultado esperado:* 200 OK con lista de productos\n\n*Resultado actual:* 500 Internal Server Error — DB_CONNECTION_FAILED\n\n*Causa probable:* Problema de conectividad con DB en staging\n\n*Fix sugerido:* Revisar connection pool y logs de DB",
            "labels":            ["api", "database", "staging", "critical"],
            "priority":          "Highest",
        },
        "ElementNotFound": {
            "root_cause":        "La URL /products/undefined sugiere que el ID de categoría no se está resolviendo correctamente, generando una URL inválida y una página 404.",
            "severity":          "medium",
            "suggested_fix":     "1. Revisar el manejo de parámetros de categoría en el frontend. 2. Verificar que los IDs de categoría existen en staging. 3. Agregar manejo de errores para IDs inválidos.",
            "jira_summary":      "Product category filter generates /products/undefined — 404 error",
            "jira_description":  "*Ambiente:* Staging\n\n*Pasos para reproducir:*\n1. Ir a /products\n2. Aplicar filtro category=electronics\n\n*Resultado esperado:* Grid de productos filtrados\n\n*Resultado actual:* Redirección a /products/undefined — Error 404\n\n*Causa probable:* ID de categoría no se resuelve correctamente\n\n*Fix sugerido:* Revisar resolución de parámetros de categoría",
            "labels":            ["frontend", "routing", "404", "products"],
            "priority":          "Medium",
        },
    }

    result = []
    for f in failures:
        error_type = f.get("failure_detail", {}).get("error_type", "AssertionError")
        analysis   = mock_responses.get(error_type, mock_responses["AssertionError"])
        enriched   = {**f, "claude_analysis": analysis}
        result.append(enriched)
        print(f"        ✓ {f['id']} [MOCK] — {analysis['severity'].upper()}: {analysis['root_cause'][:60]}...")

    return result
