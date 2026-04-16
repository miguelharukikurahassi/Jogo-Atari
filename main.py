import js
from js import document, window
from pyodide.ffi import create_proxy
import random

canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

keys = {}
def keydown(evt):
    keys[evt.code] = True
    if evt.code in ["Space", "ArrowUp", "ArrowDown"]:
        evt.preventDefault()
        
    # Lógica de Restart! Se o jogo acabou e apertarmos Enter, nós reiniciamos tudo!
    if (game_state["game_over"] or game_state["victory"]) and evt.code == "Enter":
        restart_game()

def keyup(evt):
    keys[evt.code] = False

document.addEventListener("keydown", create_proxy(keydown))
document.addEventListener("keyup", create_proxy(keyup))

# Estado Global do Jogo
game_state = {
    "wave": 1,
    "max_waves": 3,
    "score": 0,
    "game_over": False,
    "victory": False,
    "items": []
}

class Bullet:
    def __init__(self, x, y, dx=0, dy=-10, color="#00FFFF"):
        self.x = x
        self.y = y
        self.w = 5
        self.h = 16
        self.dx = dx
        self.dy = dy
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        ctx.fillStyle = self.color
        ctx.fillRect(self.x, self.y, self.w, self.h)

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 20
        self.h = 20
        self.speed = 2.5
        self.type = random.choice(["machine_gun", "spread", "speed"])
        self.colors = {"machine_gun": "#FF2222", "spread": "#22FF22", "speed": "#2222FF"}
        
    def update(self):
        self.y += self.speed
        
    def draw(self):
        ctx.save()
        ctx.fillStyle = self.colors[self.type]
        ctx.beginPath()
        ctx.arc(self.x + 10, self.y + 10, 10, 0, 6.28)
        ctx.fill()
        
        ctx.fillStyle = "#FFF"
        ctx.font = "bold 12px Arial"
        ctx.textAlign = "center"
        if self.type == "machine_gun": ctx.fillText("M", self.x + 10, self.y + 14)
        elif self.type == "spread": ctx.fillText("S", self.x + 10, self.y + 14)
        else: ctx.fillText("V", self.x + 10, self.y + 14)
        ctx.restore()

class Player:
    def __init__(self):
        self.w = 60
        self.h = 60
        self.x = (canvas.width / 2) - (self.w / 2)
        self.y = canvas.height - 80
        self.speed = 5.5
        self.bullets = []
        
        self.weapon = "normal" 
        self.shoot_timer = 0 

    def update(self):
        if keys.get("ArrowLeft", False) or keys.get("KeyA", False): self.x -= self.speed
        if keys.get("ArrowRight", False) or keys.get("KeyD", False): self.x += self.speed
            
        if self.x < 0: self.x = 0
        if self.x + self.w > canvas.width: self.x = canvas.width - self.w
            
        for b in self.bullets: b.update()
        self.bullets = [b for b in self.bullets if b.y > 0] 
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        if keys.get("Space", False) and self.shoot_timer <= 0:
            self.shoot()

    def shoot(self):
        if self.weapon == "normal":
            if len(self.bullets) < 3:
                self.bullets.append(Bullet(self.x + self.w/2 - 2, self.y))
                self.shoot_timer = 15
        elif self.weapon == "machine_gun": 
            self.bullets.append(Bullet(self.x + self.w/2 - 2, self.y, color="#FF4444"))
            self.shoot_timer = 6
        elif self.weapon == "spread": 
            if len(self.bullets) < 12:
                self.bullets.append(Bullet(self.x + self.w/2 - 2, self.y, dx=0, color="#44FF44"))
                self.bullets.append(Bullet(self.x + self.w/2 - 2, self.y, dx=-3, color="#44FF44"))
                self.bullets.append(Bullet(self.x + self.w/2 - 2, self.y, dx=3, color="#44FF44"))
                self.shoot_timer = 20

    def draw(self, img):
        for b in self.bullets: b.draw()
        if img: ctx.drawImage(img, self.x, self.y, self.w, self.h)


class AlienSwarm:
    def __init__(self, wave):
        self.aliens = []
        self.w = 50
        self.h = 50
        self.direction = 1
        self.speed = 0.5 + (wave * 0.4) 
        
        for row in range(4):
            for col in range(8):
                alien_type = "normal"
                hp = 1
                if wave >= 2 and row == 3:
                    alien_type = "tank"
                    hp = 4
                if wave >= 3 and row == 0:
                    alien_type = "fast"
                
                self.aliens.append({
                    "x": 80 + col * 70, "y": 60 + row * 60, 
                    "type": alien_type, "hp": hp
                })

    def update(self):
        if not self.aliens: return
        hit_edge = False
        
        for a in self.aliens:
            dx = self.speed * self.direction
            if a["type"] == "fast": dx *= 1.8 
            a["x"] += dx
            
            if a["x"] + self.w > canvas.width - 20 or a["x"] < 20:
                hit_edge = True
                
        if hit_edge:
            self.direction *= -1
            self.speed += 0.15
            for a in self.aliens:
                a["y"] += 35
                if a["y"] + self.h >= player.y:
                    game_state["game_over"] = True

    def draw(self, img):
        if not img: return
        for a in self.aliens:
            ctx.save()
            if a["type"] == "tank":
                ctx.translate(a["x"] + self.w/2, a["y"] + self.h/2)
                ctx.scale(1.2, 1.2)
                ctx.filter = "hue-rotate(90deg) brightness(1.5)"
                ctx.drawImage(img, -self.w/2, -self.h/2, self.w, self.h)
            elif a["type"] == "fast":
                ctx.translate(a["x"], a["y"])
                ctx.filter = "hue-rotate(220deg)" 
                ctx.drawImage(img, 0, 0, self.w, self.h)
            else:
                ctx.translate(a["x"], a["y"])
                ctx.drawImage(img, 0, 0, self.w, self.h)
            ctx.restore()


# Declarando e Instanciando Classes Iniciais
player = Player()
swarm = None
assets = {"loaded": 0, "player": window.Image.new(), "alien": window.Image.new()}

def check_collisions():
    global swarm
    surviving_aliens = []
    
    for a in swarm.aliens:
        hit = False
        for b in list(player.bullets):
            w = swarm.w * (1.2 if a["type"] == "tank" else 1.0)
            h = swarm.h * (1.2 if a["type"] == "tank" else 1.0)
            
            if b.x < a["x"] + w and b.x + b.w > a["x"] and b.y < a["y"] + h and b.y + b.h > a["y"]:
                hit = True
                player.bullets.remove(b)
                a["hp"] -= 1
                
                if a["hp"] <= 0:
                    score_pts = 10 if a["type"] == "normal" else (30 if a["type"]=="tank" else 20)
                    game_state["score"] += score_pts
                    
                    if random.random() < 0.15:
                        game_state["items"].append(PowerUp(a["x"], a["y"]))
                break
                
        if a["hp"] > 0: surviving_aliens.append(a)
    swarm.aliens = surviving_aliens
    
    for item in list(game_state["items"]):
        if item.x < player.x + player.w and item.x + item.w > player.x and item.y < player.y + player.h and item.y + item.h > player.y:
            if item.type == "speed": player.speed = 10.0
            else: player.weapon = item.type
            game_state["items"].remove(item)

# Função para Ressuscitar o Jogo (Restart System)
def restart_game():
    global player, swarm
    
    game_state["wave"] = 1
    game_state["score"] = 0
    game_state["game_over"] = False
    game_state["victory"] = False
    game_state["items"] = []
    
    player = Player()
    swarm = AlienSwarm(1)
    
    # Chama o Loop da Morte de volta a vida!
    window.requestAnimationFrame(proxy_game_loop)


def game_loop(time_stamp):
    global swarm
    
    ctx.fillStyle = "rgba(5, 5, 16, 0.5)"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    if game_state["game_over"]:
        ctx.fillStyle = "rgba(255, 0, 0, 0.7)"
        ctx.fillRect(0, canvas.height/2 - 60, canvas.width, 140)
        ctx.fillStyle = "#FFF"
        ctx.font = "bold 50px Courier New"
        ctx.textAlign = "center"
        ctx.fillText("TERRA DESTRUÍDA", canvas.width/2, canvas.height/2)
        ctx.font = "20px Courier New"
        ctx.fillText("> Pressione [ENTER] para Tentar Novamente <", canvas.width/2, canvas.height/2 + 50)
        return

    if game_state["victory"]:
        ctx.fillStyle = "rgba(0, 255, 0, 0.7)"
        ctx.fillRect(0, canvas.height/2 - 60, canvas.width, 160)
        ctx.fillStyle = "#FFF"
        ctx.font = "bold 50px Courier New"
        ctx.textAlign = "center"
        ctx.fillText("UNIVERSO SALVO!", canvas.width/2, canvas.height/2 - 10)
        ctx.font = "bold 25px Courier New"
        ctx.fillText(f"Score Final: {game_state['score']}", canvas.width/2, canvas.height/2 + 30)
        ctx.font = "20px Courier New"
        ctx.fillText("> Pressione [ENTER] para Jogar Novamente <", canvas.width/2, canvas.height/2 + 70)
        return
        
    if len(swarm.aliens) == 0:
        if game_state["wave"] < game_state["max_waves"]:
            game_state["wave"] += 1
            swarm = AlienSwarm(game_state["wave"]) 
            player.bullets.clear()
        else:
            game_state["victory"] = True
            return

    player.update()
    swarm.update()
    for i in game_state["items"]: i.update()
    game_state["items"] = [i for i in game_state["items"] if i.y < canvas.height]
    check_collisions()
    
    player.draw(assets["player"])
    swarm.draw(assets["alien"])
    for i in game_state["items"]: i.draw()
    
    ctx.fillStyle = "#FFF"
    ctx.font = "18px Courier New"
    ctx.textAlign = "left"
    ctx.fillText(f"Horda: {game_state['wave']}/{game_state['max_waves']}", 20, 30)
    ctx.textAlign = "right"
    ctx.fillText(f"Score: {game_state['score']}", canvas.width - 20, 30)

    window.requestAnimationFrame(proxy_game_loop)

proxy_game_loop = create_proxy(game_loop)

def on_asset_loaded(evt):
    assets["loaded"] += 1
    if assets["loaded"] == 2: 
        global swarm
        swarm = AlienSwarm(game_state["wave"])
        game_loop(0)

proxy_on_load = create_proxy(on_asset_loaded)
assets["player"].onload = proxy_on_load
assets["player"].src = "assets/player.png"
assets["alien"].onload = proxy_on_load
assets["alien"].src = "assets/alien.png"
