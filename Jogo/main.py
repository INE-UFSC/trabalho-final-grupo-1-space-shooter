import pygame
import random
import os

from jogador import Jogador
from inimigo import Inimigo
from meteoro import Meteoro
from atirar import Atirar
from escudo import Escudo
from boost import Boost
from Sprites import *
from vida import Vida
from Som import *


pygame.init()


#definindo que minha janela tera a largura e altura especificada
WIN = pygame.display.set_mode((largura, altura))

#novo evento criado para aumentar a pontuação conforme passa o tempo
tempo = pygame.USEREVENT + 1
pygame.time.set_timer(tempo, 5000)

#fontes
fonte = pygame.font.Font(os.path.join(BASE_DIR, "assets", "levycrayola.TTF"), 50)
fonte_fim_de_jogo = pygame.font.Font(os.path.join(BASE_DIR, "assets", "levycrayola.TTF"), 60)

#cores
branco = (255,255,255)
preto = (0,0,0)

# Lista sons (se novos sprites de som forem criados, adicionar nesta lista =) )
lista_sons = [MUSICA_FIM, EXPLODIU, COLIDIU, MORTE]


class Main():
    def main(self, volume):
        run = True
        FPS = 60
        nivel = 1
        vidas = 5
        clock = pygame.time.Clock()
        parado = True

        # Pontuação para o próximo nível
        pontuacao_limite = 800

        #variáveis pro inimigo
        inimigos = []
        onda_de_inimigos = 0
        velocidade_inimigo = 2

        #variáveis pro meteoro
        meteoros = []
        velocidade_meteoro = 1

        #variáveis pro boost
        boosts = []
        onda_de_boost = 1
        velocidade_boost = 3

        #vidas
        vidas_a_captar = []
        onda_de_vida = 1
        velocidade_vida = 5

        #escudo
        escudos = []
        velocidade_escudo = 3
        onda_de_escudos = 1
        ativar_escudo = False
        TIMERESCUDO = pygame.USEREVENT
        pygame.time.set_timer(TIMERESCUDO, 0)

        # Saude
        height_barra = 10
        saude = 100

        # Lasers
        resfriamento_laser = 0
        tempo_resfriamento = 20
        velocidade_laser = 7
        lasers_inimigos = []
        lasers_jogador = []

        # Jogador
        movimento_jogador = 8
        jogador = Jogador(int(largura / 2 - WH_JOGADOR / 2), int(altura - 125), altura, largura, JOGADOR, JOGADOR_PARADO, ESCUDO_NO_JOGADOR, ESCUDO_NO_JOGADOR2, LASER_JOGADOR, saude)

        fim_de_jogo = False
        contador_fim_de_jogo = 0

        # Definindo volume
        for som in lista_sons:
            som.set_volume(volume)

        def desenhar_janela(pos_y):
            WIN.blit(PLANO_DE_FUNDO, (0, pos_y))
            WIN.blit(PLANO_DE_FUNDO, (0, pos_y - altura + 1))
            WIN.blit(PORTA, (574, 543))

            # mostrando textos na tela
            label_vidas = fonte.render(f"Vidas: {vidas}", True, preto)  # 1 - suavização de serrilhado
            label_nivel = fonte.render(f"Nivel: {nivel}", True, preto)
            label_pontuacao = fonte.render(f"{jogador.pontuacao}", True, preto)

            WIN.blit(label_vidas, (10, 10))
            WIN.blit(label_nivel, (largura - label_nivel.get_width() - 10, 10))
            WIN.blit(label_pontuacao, (10, 595))

            for inimigo in inimigos:
                inimigo.desenhar(WIN)

            for meteoro in meteoros:
                meteoro.desenhar(WIN)
            
            for laser_inimigo in lasers_inimigos:
                laser_inimigo.desenhar(WIN)

            for laser_jogador in lasers_jogador:
                laser_jogador.desenhar(WIN)

            for boost in boosts:
                boost.desenhar(WIN)

            for escudo in escudos:
                escudo.desenhar(WIN)

            for vida in vidas_a_captar:
                vida.desenhar(WIN)

            if ativar_escudo:
                jogador.desenhar_escudo(WIN)

            jogador.desenhar(WIN, height_barra, parado)

            if fim_de_jogo:
                pygame.mixer.music.stop()
                WIN.blit(EXPLOSAO, (jogador.x - 50, jogador.y-20))
                fim_de_jogo_label = fonte_fim_de_jogo.render("Aguarde", True, preto)
                WIN.blit(fim_de_jogo_label, (largura / 2 - fim_de_jogo_label.get_width() / 2,
                                             altura / 2 - fim_de_jogo_label.get_height() / 2))

            pygame.display.update() # sempre que for desenhar, devemos atualizar a tela colocando a "nova imagem" por cima das outras que estavam desenhadas
        pos_y = 0 #posicao inicial da tela de fundo
        
        while run:
            clock.tick(FPS)
            desenhar_janela(pos_y)
            pos_y += velocidade_inimigo/2  #tela de fundo se move sempre a metade da velocidade do inimigo
            
            if pos_y >= altura:
                pos_y = 0  #reseta posicao da tela de fundo

            if jogador.saude <= 0:
                if vidas >= 1:
                    jogador.saude = saude
                    vidas -= 1

            if vidas <= 0:
                fim_de_jogo = True
                contador_fim_de_jogo += 1

            # A pontuacao é retornada quando o jogador perde
            if fim_de_jogo:
                velocidade_inimigo = 0
                if contador_fim_de_jogo == FPS/60:
                    MORTE.play()
                elif contador_fim_de_jogo > FPS * 3:
                    MUSICA_FIM.play()
                    return True, jogador.pontuacao
                else:
                    continue

            # Subida de nivel, Velocidade do Inimigo, do Laser e do Meteoro
            if jogador.pontuacao >= pontuacao_limite:
                if nivel < 3:
                    if nivel == 1:
                        velocidade_meteoro += 1
                        pontuacao_limite = 1800
                    if nivel == 2:
                        pontuacao_limite = 3000
                    velocidade_inimigo += 0.5
                    velocidade_laser += 0.5
                elif nivel == 3:
                    pontuacao_limite = 4000
                    velocidade_inimigo += 0.5
                    velocidade_laser += 0.5
                    velocidade_meteoro += 1
                elif nivel == 4:
                    pontuacao_limite = 5000
                    velocidade_inimigo += 0.5
                    velocidade_laser += 0.5
                elif nivel > 4:
                    pontuacao_limite += pontuacao_limite * 0.3
                    velocidade_inimigo += 1
                    velocidade_laser += 1
                    velocidade_meteoro += 1
                nivel += 1
                #print("vel inimigo:", velocidade_inimigo)

            # lógica do inimigo
            if len(inimigos) == 0:
                onda_de_inimigos += 3

                for i in range(onda_de_inimigos):
                    inimigo = Inimigo(random.randrange(50, largura - 128),
                                      random.randrange(-8000 * (nivel / 5), -128),
                                      str(random.randrange(1, 4)), altura, largura, saude)  # ver depois sobre o -1500
                    inimigos.append(inimigo)

            for inimigo in inimigos[:]:
                inimigo.movimentar(velocidade_inimigo, inimigos)

                if random.randrange(0, 4 * FPS) == 1:
                    lasers_inimigos.append(Atirar.atirar(inimigo, altura, largura))

                if inimigo.colisao(jogador, inimigos):
                    COLIDIU.play()
                    if not ativar_escudo:
                        jogador.dano(15)

            # lógica de criação, remoção e movimento dos meteoros
            if len(meteoros) == 0:
                meteoro = Meteoro(-110, random.randrange(0, 400), altura, largura, METEORO)
                meteoros.append(meteoro)
                if nivel > 1:
                    meteoro2 = Meteoro(-510, random.randrange(-300, 250), altura, largura, METEORO)
                    meteoros.append(meteoro2)
                if nivel > 2:
                    meteoro3 = Meteoro(-910, random.randrange(-600, -50), altura, largura, METEORO)
                    meteoros.append(meteoro3)
                if nivel > 3:
                    meteoro4 = Meteoro(-1310, random.randrange(-1100, -400), altura, largura, METEORO)
                    meteoros.append(meteoro4)
                if nivel > 4:
                    meteoro6 = Meteoro(-1710, random.randrange(-1150, -550), altura, largura, METEORO)
                    meteoros.append(meteoro6)
                if nivel > 5:
                    meteoro5 = Meteoro(-1110, random.randrange(-700, -150), altura, largura, METEORO)
                    meteoros.append(meteoro5)
                if nivel > 6:
                    meteoro7 = Meteoro(-710, random.randrange(-600, 0), altura, largura, METEORO)
                    meteoros.append(meteoro7)

            for meteoro in meteoros[:]:
                meteoro.movimentar(velocidade_meteoro, meteoros)

                if meteoro.colisao(jogador, meteoros):
                    COLIDIU.play()
                    if not ativar_escudo:
                        jogador.dano(15)

            #logica boost
            if len(boosts) == 0:
                if random.randrange(0, 5000) == 9:
                    onda_de_boost += 1

                for i in range(onda_de_boost):
                    if random.randrange(0, 5000) == 9:
                        boost = Boost(-110, random.randrange(0, 400), altura, largura, BOOST)
                        boosts.append(boost)

            for boost in boosts[:]:
                boost.movimentar(velocidade_boost, boosts)

                if boost.colisao(jogador, boosts):
                    jogador.inc_pontuacao(1000)

            #lógica do escudo
            if len(escudos) == 0:
                onda_de_escudos += 1

                for i in range(onda_de_escudos):
                    if random.randrange(0, 5000) == 9:
                        escudo = Escudo(random.randrange(50, largura - 128), random.randrange(-8000 * (nivel / 5), -128), altura, largura, ESCUDO)  # ver depois sobre o -1500
                        escudos.append(escudo)

            for escudo in escudos[:]:
                escudo.movimentar(velocidade_escudo, escudos)

                if escudo.colisao(jogador, escudos):
                    pygame.time.set_timer(TIMERESCUDO, 4000)
                    ativar_escudo = True

            #lógica da vida
            if len(vidas_a_captar) == 0:
                onda_de_vida += 1

                for _ in range(onda_de_vida):
                    if random.randrange(0, 5000) == 9:
                        vida = Vida(random.randrange(50, largura - 128), random.randrange(-8000 * (nivel / 5), -128), altura, largura, VIDA)  # ver depois sobre o -1500
                        vidas_a_captar.append(vida)

            for vida in vidas_a_captar[:]:
                vida.movimentar(velocidade_vida, vidas_a_captar)

                if vida.colisao(jogador, vidas_a_captar):
                    if jogador.saude + 10 <= 90:
                        jogador.saude += 10
                    elif jogador.saude + 10 > 90 and jogador.saude + 10 < 100:
                        jogador.saude = 100

            # EVENTOS
            # vai passar por todos os eventos que ocorreram, 60 vezes por segundo
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # se clicar no botão de fechar, o while se encerra, ou seja, o jogo fecha
                    quit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not resfriamento_laser:
                        lasers_jogador.append(Atirar.atirar(jogador, altura, largura))
                        resfriamento_laser = 1
                
                if event.type == tempo:
                    jogador.inc_pontuacao(10)

                if event.type == TIMERESCUDO:
                    pygame.time.set_timer(TIMERESCUDO, 0)
                    ativar_escudo = False

                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                if 632 > mouse[0] > 593 and 629 > mouse[1] > 569:
                    if click[0] == 1:
                        return True, jogador.pontuacao

            teclas = pygame.key.get_pressed()  # retorna um dicioonário de todas as teclas e diz se estão pressionadas ou não

            # movimentos do jogador de acordo com a tecla pressionada
            parado = True
            if pygame.KEYDOWN:
                if teclas[pygame.K_a] and jogador.x - movimento_jogador > 0:  # esquerda
                    parado =jogador.movimentar(-movimento_jogador, 0)
                if teclas[pygame.K_d] and jogador.x + movimento_jogador + jogador.get_width() < largura:  # direita
                    parado =jogador.movimentar(movimento_jogador, 0)
                if teclas[pygame.K_w] and jogador.y - movimento_jogador > 0:  # cima
                    parado =jogador.movimentar(0, -movimento_jogador)
                if teclas[
                    pygame.K_s] and jogador.y + movimento_jogador + jogador.get_height() + 2 * height_barra < altura:  # baixo
                    parado = jogador.movimentar(0, movimento_jogador)

            for laser_inimigo in lasers_inimigos:
                laser_inimigo.movimentar(velocidade_laser, lasers_inimigos)
                if laser_inimigo.colisao(jogador, lasers_inimigos):
                    # Definir o som de quando o jogador tomar um dano de laser
                    if not ativar_escudo:
                        jogador.dano(15)

            # Resfriamento Laser
            if resfriamento_laser >= tempo_resfriamento:
                resfriamento_laser = 0
            elif resfriamento_laser > 0:
                resfriamento_laser += 1

            for laser_jogador in lasers_jogador:
                laser_jogador.movimentar(-velocidade_laser, lasers_jogador)
                for inimigo in inimigos:
                    if laser_jogador.colisao(inimigo, lasers_jogador):
                        EXPLODIU.play()
                        jogador.inc_pontuacao(100)
                        try:
                            inimigos.remove(inimigo)
                        except ValueError:
                            print("ValueError")
                            pass
                for meteoro in meteoros:
                    laser_jogador.colisao(meteoro, lasers_jogador)