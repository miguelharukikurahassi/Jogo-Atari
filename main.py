# main.py
import js
from js import document, window
from pyodide.ffi import create_proxy

def main():
    canvas = document.getElementById("gameCanvas")
    
    if canvas:
        ctx = canvas.getContext("2d")
        
        # Fundo do espaço
        ctx.fillStyle = "#080808"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        # Dicionário com um contador para sabermos quando os 2 assets terminaram de baixar
        loaded = {"count": 0}

        def on_load(evt):
            loaded["count"] += 1
            if loaded["count"] == 2:
                # Quando ambas carregarem, desenhamos!
                
                # A Nave (tamanho 60x60px) centralizada na parte de baixo da tela
                ship_w, ship_h = 60, 60
                x_nave = (canvas.width / 2) - (ship_w / 2)
                y_nave = canvas.height - 80
                ctx.drawImage(ship_img, x_nave, y_nave, ship_w, ship_h)
                
                # Desenhando uma "tropa de teste" com vários Aliens de Space Invaders
                alien_w, alien_h = 50, 50
                for col in range(5):
                    # Espaçados em colunas
                    x_alien = 180 + col * 90
                    # Fileira superior
                    ctx.drawImage(alien_img, x_alien, 80, alien_w, alien_h)
                    # Fileira inferior
                    ctx.drawImage(alien_img, x_alien, 150, alien_w, alien_h)
                
                ctx.font = "24px Courier New"
                ctx.fillStyle = "#00FF00"
                ctx.textAlign = "center"
                ctx.fillText("Assets Gráficos Carregados com Sucesso!", canvas.width / 2, 350)
                ctx.font = "16px Courier New"
                ctx.fillText("(Faça um novo Commit pelo GitHub Desktop e espere 5 minutos)", canvas.width / 2, 400)
                
                print("Novos gráficos 8-bit de naves e aliens desenhados no canvas!")

        # Pyodide: create_proxy cria uma ponte entre essa função Python e os 'Event Listeners' do navegador do JS
        on_load_proxy = create_proxy(on_load)

        # Carregando imagem da nave do jogador
        ship_img = window.Image.new()
        ship_img.onload = on_load_proxy
        ship_img.src = "./assets/player.png"
        
        # Carregando imagem do alienígena
        alien_img = window.Image.new()
        alien_img.onload = on_load_proxy
        alien_img.src = "./assets/alien.png"

    else:
        print("Erro: Canvas não achado.")

main()
