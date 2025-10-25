import subprocess
import textwrap

prompt = "Explica por qué el cielo es azul."
respuestas = [
    "El cielo es azul por la dispersión de Rayleigh.",
    "Las moléculas del aire dispersan más la luz azul que la roja.",
    "La atmósfera filtra la luz, haciendo que el azul predomine.",
    "Debido a la dispersión de la luz solar en la atmósfera.",
    "La luz azul se dispersa más por su longitud de onda más corta."
]

contexto = "\n".join([f"Respuesta {i+1}: {r}" for i, r in enumerate(respuestas)])
instruccion = f"""Dado el siguiente prompt: '{prompt}'
y las siguientes 5 soluciones:
{contexto}
Elabora una respuesta final combinando las mejores ideas.
"""

resultado = subprocess.run(
    ["ollama", "run", "phi3:mini"],
    input=instruccion,
    text=True,
    capture_output=True
)

print(resultado.stdout)
