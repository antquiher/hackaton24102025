from bs4 import BeautifulSoup

html = "<p>Hola <b>mundo</b>! Esto es un <a href='#'>ejemplo</a>.</p>"
texto_plano = BeautifulSoup(html, "html.parser").get_text()

print(texto_plano)