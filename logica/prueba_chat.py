problema = "probelema de prueba"
respuestas = ["respuesta 1", "respuesta 2", "respuesta 1", "respuesta 1", "respuesta 2"]

prompt = f"""
Dado el siguiente problema:
{problema}

Y estas 5 respuestas diferentes:
{chr(10).join([f"- {r}" for r in respuestas])}

Combina lo mejor de todas las respuestas en una sola versión más completa, 
precisa y bien redactada. No repitas información innecesaria.
"""

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)