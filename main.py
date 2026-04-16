# main.py
import js
from js import document, window

def main():
    # 1. Encontrar o canvas no HTML
    canvas = document.getElementById("gameCanvas")
    
    if canvas:
        # Obter o contexto 2D, que nos permite desenhar formas, imagens e textos na tela
        ctx = canvas.getContext("2d")
        
        # 2. Desenhar um fundo de teste
        ctx.fillStyle = "#050510"  # Um preto com leve toque de azul escuro (espaço)
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        # 3. Desenhar um "Alien" temporário (um quadrado de cor verde)
        # Mais tarde, no decorrer do projeto, usaremos as imagens da pasta /assets
        ctx.fillStyle = "#00FF00"
        ctx.fillRect(380, 200, 40, 40)
        
        # 4. Escrever um texto na tela para garantir que o Python tá rodando
        ctx.font = "24px Courier New"
        ctx.fillStyle = "#FFFFFF"
        ctx.textAlign = "center"
        ctx.fillText("Antigravity Engine Carregada!", canvas.width / 2, 350)
        
        ctx.font = "18px Courier New"
        ctx.fillStyle = "#AAAAAA"
        ctx.fillText("Aguardando inserção dos assets gráficos...", canvas.width / 2, 400)
        
        print("Space Invaders inicializado via PyScript WebAssembly com sucesso!")
    else:
        print("Erro Crítico: Canvas 'gameCanvas' não encontrado no index.html")

# Disparar a função principal
main()
