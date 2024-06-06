# Import library pygame dan modul random
import pygame
import random
import json

# Inisialisasi pygame dan mixer
pygame.init()
pygame.mixer.init()

# Lebar dan tinggi layar game, frame per detik, dan timer
WIDTH = 700
HEIGHT = 670
fps = 60
timer = pygame.time.Clock()

# Font untuk teks besar dan kecil
huge_font = pygame.font.Font('assets/Terserah.ttf', 42)
font = pygame.font.Font('assets/Terserah.ttf', 24)

# Pengaturan layar game
pygame.display.set_caption('Penguins Can\'t Fly!')
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# Daftar warna latar belakang
backgrounds = [(102, 178, 255), (153, 204, 255), (0, 0, 0)]  # Contoh warna latar belakang baru
# Batas score untuk mengubah latar belakang
background_change_score = 200

# Variabel status permainan
game_over = False
game_over_menu = False
show_menu = True
game_paused = False
last_saved_score = 0
selected_menu_item = 0  # Indeks item menu yang dipilih (0: Mulai Game, 1: Keluar)
selected_game_over_item = 0  # Indeks item menu game over yang dipilih (0: Mulai Ulang, 1: Kembali ke Menu)
selected_pause_item = 0  # Indeks item menu save game yang dipilih (0: Save Game, 1: Lanjutkan)

# Koordinat awal awan dan gambar awan
clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
cloud_images = []
for i in range(1, 4):
    img = pygame.image.load(f'assets/clouds/cloud{i}.png')
    cloud_images.append(img)

# Variabel player
player_x = 240
player_y = 40
penguin = pygame.transform.scale(pygame.image.load('assets/penguin1.png'), (55, 60))
direction = -1
y_speed = 0
gravity = 0.3
x_speed = 4
x_direction = 0
original_x_speed = x_speed
original_y_speed = y_speed
original_gravity = gravity
# Variabel skor
score = 0
total_distance = 0
file = open('high_scores.txt', 'r')
read = file.readlines()
first_high = int(read[0])
high_score = first_high

# Gambar musuh (shark)
shark = pygame.transform.scale(pygame.image.load('assets/jetpack_shark.png'), (300, 200))
enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]

# Suara dan musik
pygame.mixer.music.load('assets/music.mp3')
bounce = pygame.mixer.Sound('assets/bounce.mp3')
end_sound = pygame.mixer.Sound('assets/game_over.mp3')
meluncur = pygame.mixer.Sound('assets/wee.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(1)

# Variabel untuk partikel salju
snowflakes = []

snow_effect_active = False
snow_effect_start_score = 0  # Ganti dengan nilai yang diinginkan

# Kecepatan jatuh partikel salju yang lebih lambat
snowfall_speed = 1
# Interval waktu antara kemunculan partikel salju
snowflake_spawn_interval = 50  # Nilai ini mengontrol interval waktu (dalam frame)
# Timer untuk menghitung waktu antara kemunculan partikel salju
snowflake_timer = 0

# Fungsi menggambar awan di layar
def draw_clouds(cloud_list, images):
    platforms = []
    for j in range(len(cloud_list)):
        image = images[cloud_list[j][2] - 1]
        platform = pygame.rect.Rect((cloud_list[j][0] + 5, cloud_list[j][1] + 40), (120, 10))
        screen.blit(image, (cloud_list[j][0], cloud_list[j][1]))
        pygame.draw.rect(screen, 'grey', [cloud_list[j][0] + 5, cloud_list[j][1] + 40, 120, 3])
        platforms.append(platform)
    return platforms

# Fungsi menggambar player di layar
def draw_player(x_pos, y_pos, player_img, direc):
    if direc == -1:
        player_img = pygame.transform.flip(player_img, False, True)
    screen.blit(player_img, (x_pos, y_pos))
    player_rect = pygame.rect.Rect((x_pos + 7, y_pos + 40), (36, 10))
    # pygame.draw.rect(screen, 'green', player_rect, 3)
    return player_rect

# Fungsi menggambar musuh di layar
def draw_enemies(enemy_list, shark_img):
    enemy_rects = []
    for j in range(len(enemy_list)):
        enemy_rect = pygame.rect.Rect((enemy_list[j][0] + 40, enemy_list[j][1] + 50), (215, 70))
        # pygame.draw.rect(screen, 'orange', enemy_rect, 3)
        enemy_rects.append(enemy_rect)
        if enemy_list[j][2] == 1:
            screen.blit(shark_img, (enemy_list[j][0], enemy_list[j][1]))
        elif enemy_list[j][2] == -1:
            screen.blit(pygame.transform.flip(shark_img, 1, 0), (enemy_list[j][0], enemy_list[j][1]))
    return enemy_rects

# Fungsi menggerakkan musuh di layar
def move_enemies(enemy_list, current_score, is_paused):
    if is_paused:  # Jika permainan di-pause, set kecepatan musuh menjadi 0
        enemy_speed = 0
    else:
        enemy_speed = 2 + current_score // 15
    for j in range(len(enemy_list)):
        if enemy_list[j][2] == 1:
            if enemy_list[j][0] < WIDTH:
                enemy_list[j][0] += enemy_speed
            else:
                enemy_list[j][2] = -1
        elif enemy_list[j][2] == -1:
            if enemy_list[j][0] > -235:
                enemy_list[j][0] -= enemy_speed
            else:
                enemy_list[j][2] = 1
        if enemy_list[j][1] < -100:
            enemy_list[j][1] = random.randint(HEIGHT, HEIGHT + 500)
    return enemy_list

# Fungsi memperbarui objek di layar (awan, musuh)
def update_objects(cloud_list, play_y, enemy_list):
    lowest_cloud = 0
    update_speed = 10
    if play_y > 200:
        play_y -= update_speed
        for q in range(len(enemy_list)):
            enemy_list[q][1] -= update_speed
        for j in range(len(cloud_list)):
            cloud_list[j][1] -= update_speed
            if cloud_list[j][1] > lowest_cloud:
                lowest_cloud = cloud_list[j][1]
        if lowest_cloud < 750:
            num_clouds = random.randint(1, 2)
            if num_clouds == 1:
                x_pos = random.randint(0, WIDTH - 70)   
                y_pos = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type = random.randint(1, 3)
                cloud_list.append([x_pos, y_pos, cloud_type])
            else:
                x_pos = random.randint(0, WIDTH / 2 - 70)
                y_pos = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type = random.randint(1, 3)
                x_pos2 = random.randint(WIDTH / 2 + 70, WIDTH - 70)
                y_pos2 = random.randint(HEIGHT + 100, HEIGHT + 300)
                cloud_type2 = random.randint(1, 3)
                cloud_list.append([x_pos, y_pos, cloud_type])
                cloud_list.append([x_pos2, y_pos2, cloud_type2])
    return play_y, cloud_list, enemy_list

# Fungsi untuk membuat partikel salju
def create_snowflake():
    x_pos = random.randint(0, WIDTH)
    y_pos = random.randint(0, HEIGHT)
    return [x_pos, y_pos]

def draw_paused_screen():
    paused_text = pygame.font.Font('assets/Terserah.ttf', 50).render('Game Paused', True, 'white')
    screen.blit(paused_text, (200, 200))
    save_game_text = pygame.font.Font('assets/Terserah.ttf', 50).render('Save Game', True, 'lightgray' if selected_pause_item == 0 else 'white')
    back_to_game_text = pygame.font.Font('assets/Terserah.ttf', 50).render('Lanjutkan', True, 'lightgray' if selected_pause_item == 1 else 'white')
    screen.blit(save_game_text, (250, 300))
    screen.blit(back_to_game_text, (220, 400))

def save_game():
    global last_saved_score, show_menu, game_paused
    last_saved_score = score
    # Implementasi penyimpanan game di sini
    saved_game_data = {
        'player_x': player_x,
        'player_y': player_y,
        'direction': direction,
        'y_speed': y_speed,
        'score': last_saved_score,
        # Tambahkan data lain yang perlu disimpan
    }
    # Simpan data ke file atau media penyimpanan lainnya
    with open('saved_game_data.json', 'w') as file:
        json.dump(saved_game_data, file)

def load_game():
    global player_x, player_y, direction, y_speed, score
    try:
        with open('saved_game_data.json', 'r') as file:
            saved_game_data = json.load(file)
            player_x = saved_game_data['player_x']
            player_y = saved_game_data['player_y']
            direction = saved_game_data['direction']
            y_speed = saved_game_data['y_speed']
            score = saved_game_data['score']
        return True
    except FileNotFoundError:
        # Tidak ada data penyimpanan, kembalikan False
        print("Tidak ada data penyimpanan yang ditemukan.")
        return False

# Variabel kecepatan turun tambahan
y_speed_increase = 3
original_y_speed = 0  # Variabel untuk menyimpan kecepatan semula
deceleration_factor = 0.1 # Faktor perlambatan

# Loop utama program
run = True
while run:
    if score >= background_change_score:
        screen.fill(backgrounds[1])
    else:
        screen.fill(backgrounds[0])

    if score >= snow_effect_start_score and not snow_effect_active and player_y < HEIGHT / 2:
        snow_effect_active = True
    if snow_effect_active:
        snowflake_timer -= 1
        if snowflake_timer <= 0:
            if random.randint(0, 100) < snowflake_spawn_interval:
                x_pos = random.randint(0, WIDTH)
                y_pos = 0
                snowflakes.append([x_pos, y_pos])
                snowflake_timer = snowflake_spawn_interval

        for flake in snowflakes:
            flake[1] += snowfall_speed

    for flake in snowflakes:
        pygame.draw.circle(screen, (255, 255, 255), (flake[0], int(flake[1])), 5)

    snowflakes = [flake for flake in snowflakes if flake[1] < HEIGHT]

    timer.tick(fps)
    cloud_platforms = draw_clouds(clouds, cloud_images)
    player = draw_player(player_x, player_y, penguin, direction)
    enemy_boxes = draw_enemies(enemies, shark)
    enemies = move_enemies(enemies, score, game_paused)
    player_y, clouds, enemies = update_objects(clouds, player_y, enemies)

    for i in range(len(cloud_platforms)):
        if direction == -1 and player.colliderect(cloud_platforms[i]):
            y_speed *= -1
            if y_speed > -2:
                y_speed = -2
            bounce.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not game_over:
                if not game_paused and not show_menu and not game_over_menu:
                    game_paused = not game_paused
                    enemies = move_enemies(enemies, score, game_paused)
                if game_paused:
                    pygame.mixer.music.pause()
                    x_direction = 0
                    y_speed = 0
                    gravity = False
                else:
                    pygame.mixer.music.unpause()

            elif game_paused:
                if event.key == pygame.K_UP:
                    selected_pause_item = (selected_pause_item - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected_pause_item = (selected_pause_item + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_pause_item == 0: #save game
                        save_game()
                        show_menu = True
                        game_paused = False
                        x_speed = original_x_speed
                        gravity = original_gravity
                        pygame.mixer.music.play()
                    elif selected_pause_item == 1: #Lanjutkan
                        game_paused = False
                        x_speed = original_x_speed
                        gravity = original_gravity
                        pygame.mixer.music.unpause()

            elif show_menu and not game_over and not game_paused:
                if event.key == pygame.K_UP:
                  selected_menu_item = (selected_menu_item - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_menu_item = (selected_menu_item + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected_menu_item == 0:  # Mulai Game
                        player_x = 240
                        player_y = 40
                        direction = -1
                        y_speed = 0
                        x_direction = 0
                        score = 0
                        total_distance = 0
                        enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]
                        clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
                        show_menu = False
                        game_paused = False
                        pygame.mixer.music.play()
                    elif selected_menu_item == 1:  # Lanjut
                        if load_game():
                            show_menu = False
                            game_paused = False
                            pygame.mixer.music.play()
                    elif selected_menu_item == 2:  # Keluar
                        run = False
                        
            elif game_over:
                if event.key == pygame.K_UP:
                    selected_game_over_item = (selected_game_over_item - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected_game_over_item = (selected_game_over_item + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_game_over_item == 0:  # Mulai Ulang
                        game_over_menu = False
                        game_over = False
                        player_x = 240
                        player_y = 40
                        direction = -1
                        y_speed = 0
                        x_direction = 0
                        score = 0
                        total_distance = 0
                        enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]
                        clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
                        pygame.mixer.music.play()
                    elif selected_game_over_item == 1:  # Kembali ke Menu
                        game_over_menu = False
                        show_menu = True
                        game_over = False
                        player_x = 240
                        player_y = 40
                        direction = -1
                        y_speed = 0
                        x_direction = 0
                        score = 0
                        total_distance = 0
                        enemies = [[-234, random.randint(400, HEIGHT - 100), 1]]
                        clouds = [[200, 100, 1], [50, 330, 2], [350, 330, 3], [200, 670, 1]]
                        pygame.mixer.music.play()
                        
            elif not game_over and not game_paused:
                if event.key == pygame.K_LEFT:
                    x_direction = -1
                elif event.key == pygame.K_RIGHT:
                    x_direction = 1
                elif event.key == pygame.K_DOWN:
                    original_y_speed = y_speed
                    y_speed += y_speed_increase
                    meluncur.play()

        elif event.type == pygame.KEYUP:
            if not show_menu and not game_over and not game_paused:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_direction = 0
                elif event.key == pygame.K_DOWN:
                    y_speed = max(original_y_speed, y_speed - deceleration_factor)

    if game_paused:
        draw_paused_screen()
    else:
        if not game_over:
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                x_direction = -1
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                x_direction = 1
            elif pygame.key.get_pressed()[pygame.K_DOWN]:
                original_y_speed = y_speed

    if show_menu:
        screen.fill(backgrounds[0])
        title_text = pygame.font.Font('assets/Terserah.ttf', 50).render('Penguins Can\'t Fly!', True, 'white')
        screen.blit(title_text, (150, 90))
        menu_text1 = huge_font.render('Mulai Game', True, 'lightgray' if selected_menu_item == 0 else 'white')
        menu_text2 = huge_font.render('Lanjut', True, 'lightgray' if selected_menu_item == 1 else 'white')
        menu_text3 = huge_font.render('Keluar', True, 'lightgray' if selected_menu_item == 2 else 'white')
        screen.blit(menu_text1, (250, 300))
        screen.blit(menu_text2, (280, 400))
        screen.blit(menu_text3, (280, 500))
        if random.randint(0, 100) < 5:
            snowflakes.append(create_snowflake())
        for flake in snowflakes:
            flake[1] += snowfall_speed
        for flake in snowflakes:
            pygame.draw.circle(screen, (255, 255, 255), (flake[0], int(flake[1])), 5)
        snowflakes = [flake for flake in snowflakes if flake[1] < HEIGHT]
        pygame.display.flip()
        continue

    if game_over:
        if not game_over_menu:
            game_over_menu = True
            selected_game_over_item = 0 
        game_over_text = pygame.font.Font('assets/Terserah.ttf', 60).render('Game Over', True, 'white')
        restart_text = huge_font.render('Mulai Ulang', True, 'lightgray' if selected_game_over_item == 0 else 'white')
        menu_text = huge_font.render('Kembali ke Menu', True, 'lightgray' if selected_game_over_item == 1 else 'white')
        screen.blit(game_over_text, (220, 170))
        screen.blit(restart_text, (250, 300))
        screen.blit(menu_text, (210, 400))
        player_y = - 300
        y_speed = 0

    if y_speed < 10 and not game_over:
        y_speed += gravity
    player_y += y_speed
    if y_speed < 0:
        direction = 1
    else:
        direction = -1
    player_x += x_speed * x_direction
    if player_x > WIDTH:
        player_x = -30
    elif player_x < -50:
        player_x = WIDTH - 20

    for i in range(len(enemy_boxes)):
        if player.colliderect(enemy_boxes[i]) and not game_over:
            end_sound.play()
            game_over = True
            if score > first_high:
                file = open('high_scores.txt', 'w')
                write_score = str(score)
                file.write(write_score)
                file.close()
                first_high = score
            pygame.mixer.music.stop()

    total_distance += y_speed
    score = round(total_distance / 100)
    score_text = font.render(f'Score: {score}', True, 'black')
    screen.blit(score_text, (10, HEIGHT - 70))
    if score > high_score:
        high_score = score
    score_text2 = font.render(f'High Score: {high_score}', True, 'black')
    screen.blit(score_text2, (10, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()