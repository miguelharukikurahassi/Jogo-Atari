import js
from js import document, window
from pyodide.ffi import create_proxy

# 1. Configuração do Canvas
canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

# 2. Estado do Teclado (para podermos apertar várias teclas ao mesmo tempo)
keys = {}

def keydown(evt):
    keys[evt.code] = True
    # Previne que a barra de espaço role a página para baixo
    if evt.code == "Space" or evt.code == "ArrowUp":
        evt.preventDefault()
    
    # O tiro acontece no exato momento que a tecla abaixa
    if evt.code == "Space":
        player.shoot()

def keyup(evt):
    keys[evt.code] = False

# Criamos a ponte e adicionamos ao documento
on_keydown_proxy = create_proxy(keydown)
on_keyup_proxy = create_proxy(keyup)
document.addEventListener("keydown", on_keydown_proxy)
document.addEventListener("keyup", on_keyup_proxy)


# 3. Lógica do Tiro
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 15
        self.speed = 10

    def update(self):
        self.y -= self.speed

    def draw(self):
        ctx.fillStyle = "#00FFFF" # Tiros cyan
        ctx.fillRect(self.x, self.y, self.w, self.h)


# 4. Lógica do Jogador
class Player:
    def __init__(self):
        self.w = 50
        self.h = 50
        self.x = (canvas.width / 2) - (self.w / 2)
        self.y = canvas.height - 70
        self.speed = 5
        self.bullets = []

    def update(self):
        # Movimentação
        if keys.get("ArrowLeft", False) or keys.get("KeyA", False):
            self.x -= self.speed
        if keys.get("ArrowRight", False) or keys.get("KeyD", False):
            self.x += self.speed
            
        # Barreiras nas bordas da tela
        if self.x < 0: 
            self.x = 0
        if self.x + self.w > canvas.width: 
            self.x = canvas.width - self.w
            
        # Atualizar posição dos tiros
        for b in self.bullets:
            b.update()
            
        # Destruir tiros que saíram da tela para economizar memória
        self.bullets = [b for b in self.bullets if b.y > 0]

    def shoot(self):
        # Permite no máximo 3 tiros na tela ao mesmo tempo (Clássico Space Invaders!)
        if len(self.bullets) < 3:
            # Cria o tiro centrado na nave
            self.bullets.append(Bullet(self.x + (self.w / 2) - 2, self.y))

    def draw(self, img):
        # Desenha os tiros primeiro (ficam pra trás)
        for b in self.bullets:
            b.draw()
        # Desenha a nave
        if img:
            ctx.drawImage(img, self.x, self.y, self.w, self.h)


# 5. Tropa de Aliens
class AlienSwarm:
    def __init__(self):
        self.aliens = []
        self.w = 40
        self.h = 40
        
        # Grid inicial: 4 linhas e 8 colunas de aliens
        for row in range(4):
            for col in range(8):
                self.aliens.append({"x": 80 + col * 60, "y": 60 + row * 60})
                
        self.direction = 1   # 1 para Direita, -1 para Esquerda
        self.speed = 1.0     # Velocidade atual
        self.game_over = False

    def update(self):
        if not self.aliens: 
            return
            
        hit_edge = False
        
        # Move cada alien e verifica limites da tela
        for a in self.aliens:
            a["x"] += self.speed * self.direction
            # Se a tropa bater na borda da tela...
            if a["x"] + self.w > canvas.width - 20 or a["x"] < 20:
                hit_edge = True
                
        # Inverte e desce a tropa se bateu
        if hit_edge:
            self.direction *= -1
            self.speed += 0.1 # Acelera gradualmente conforme chegam perto!
            for a in self.aliens:
                a["y"] += 30
                # Verifica a condição de derrota (aliens bateram nos escudos invisiveis embaixo)
                if a["y"] + self.h >= player.y:
                    self.game_over = True

    def draw(self, img):
        if img:
            for a in self.aliens:
                ctx.drawImage(img, a["x"], a["y"], self.w, self.h)


# 6. Inicializando as Variáveis de Jogo
player = Player()
swarm = AlienSwarm()
assets = {"loaded": 0, "player": window.Image.new(), "alien": window.Image.new()}


# Sistema de Colisão Simples (AABB)
def check_collisions():
    surviving_aliens = []
    
    for a in swarm.aliens:
        hit = False
        # Para cada alien, olhamos os tiros
        for b in player.bullets:
            # Fórmula de Colisão de 2 Retângulos
            if (b.x < a["x"] + swarm.w and
                b.x + b.w > a["x"] and
                b.y < a["y"] + swarm.h and
                b.y + b.h > a["y"]):
                
                # Houve Colisão!
                hit = True
                player.bullets.remove(b) # Destrói a rajada
                break # Para a verificação pra esse alien (pois ele já morreu)
                
        # Se não foi atingido, ele sobrevive para o proximo frame
        if not hit:
            surviving_aliens.append(a)
            
    swarm.aliens = surviving_aliens


# 7. Loop Principal de Desenho/Simulação
def game_loop(time_stamp):
    # Fundo do Cosmos
    ctx.fillStyle = "#050510"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    if swarm.game_over:
        ctx.fillStyle = "#FF0000"
        ctx.font = "50px Courier New"
        ctx.textAlign = "center"
        ctx.fillText("GAME OVER", canvas.width/2, canvas.height/2)
        return

    if len(swarm.aliens) == 0:
        ctx.fillStyle = "#00FF00"
        ctx.font = "50px Courier New"
        ctx.textAlign = "center"
        ctx.fillText("VOCÊ VENCEU!", canvas.width/2, canvas.height/2)
        return
        
    # Updates Matemáticos
    player.update()
    swarm.update()
    check_collisions()
    
    # Desenhos no Canvas
    player.draw(assets["player"])
    swarm.draw(assets["alien"])
    
    # Placar Superior
    ctx.fillStyle = "#FFF"
    ctx.font = "20px Courier New"
    ctx.textAlign = "left"
    ctx.fillText(f"Invasores Restantes: {len(swarm.aliens)}", 20, 30)

    # Re-agenda o loop (isso evita travas e usa a frequência natural da tela 60 FPS)
    window.requestAnimationFrame(proxy_game_loop)


# A ponte pro JS do loop
proxy_game_loop = create_proxy(game_loop)

# 8. Start do Jogo após o Loading das Imagens
def on_asset_loaded(evt):
    assets["loaded"] += 1
    # Quando as 2 imagens carregam, disparamos a máquina
    if assets["loaded"] == 2:
        game_loop(0)

proxy_on_load = create_proxy(on_asset_loaded)

assets["player"].onload = proxy_on_load
assets["player"].src = "assets/player.png"

assets["alien"].onload = proxy_on_load
assets["alien"].src = "assets/alien.png"
