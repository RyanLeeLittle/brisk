import pygame
import sys
import random
import time
import os
import asyncio

# 게임 초기화
pygame.init()

# 화면 설정
width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("벽돌 깨기 게임")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE]

# 한글 폰트 설정
def get_font(size):
    # Windows 시스템 폰트 경로
    font_path = None
    
    # Windows 시스템 폰트 경로에서 한글 지원 폰트 찾기
    if os.name == 'nt':  # Windows
        try:
            font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            possible_fonts = [
                'malgun.ttf',           # 맑은 고딕
                'gulim.ttc',            # 굴림
                'dotum.ttc',            # 돋움
                'batang.ttc',           # 바탕
                'HMFMPYUN.TTF',         # HY 명조
                'H2GTRM.TTF',           # 한컴 고딕
                'H2MJRE.TTF',           # 한컴 명조
                'arial.ttf'             # Arial (한글 지원 안 될 수 있음)
            ]
            
            for font_file in possible_fonts:
                full_path = os.path.join(font_dir, font_file)
                if os.path.exists(full_path):
                    font_path = full_path
                    break
        except:
            pass
    
    # 폰트 파일을 찾은 경우 TTF 폰트 로드
    if font_path:
        try:
            return pygame.font.Font(font_path, size)
        except:
            pass
    
    # 시스템 폰트 찾지 못하면 기본 폰트 사용
    return pygame.font.SysFont(None, size)  # 영어만 표시 가능

# 대체 텍스트 정의 (한글 표시가 안 되는 경우)
TEXT_GAME_OVER = "게임 오버!"
TEXT_GAME_WIN = "게임 승리!"
TEXT_RESTART = "다시 시작"
TEXT_QUIT = "게임 종료"
TEXT_SCORE = "점수:"
TEXT_LIVES = "목숨:"
TEXT_SPEED = "속도:"
TEXT_TIME = "경과 시간:"
TEXT_FINAL_SCORE = "최종 점수:"
TEXT_SELECT = "다음 중 선택하세요:"

# 폰트 테스트를 위한 함수
def render_text(text, font, color):
    try:
        return font.render(text, True, color)
    except:
        # 한글 렌더링 실패 시 영어로 대체
        if text == TEXT_GAME_OVER:
            return font.render("Game Over!", True, color)
        elif text == TEXT_GAME_WIN:
            return font.render("You Win!", True, color)
        elif text == TEXT_RESTART:
            return font.render("Restart", True, color)
        elif text == TEXT_QUIT:
            return font.render("Quit", True, color)
        elif text.startswith(TEXT_SCORE):
            return font.render("Score: " + text[3:], True, color)
        elif text.startswith(TEXT_LIVES):
            return font.render("Lives: " + text[3:], True, color)
        elif text.startswith(TEXT_SPEED):
            return font.render("Speed: " + text[3:], True, color)
        elif text.startswith(TEXT_TIME):
            return font.render("Time: " + text[5:], True, color)
        elif text.startswith(TEXT_FINAL_SCORE):
            return font.render("Final Score: " + text[6:], True, color)
        elif text == TEXT_SELECT:
            return font.render("Select one:", True, color)
        else:
            return font.render(text, True, color)

class Game:
    def __init__(self):
        # 패들 설정
        self.paddle_width, self.paddle_height = 100, 20
        self.paddle_x = (width - self.paddle_width) // 2
        self.paddle_y = height - self.paddle_height - 10
        self.paddle_speed = 8

        # 공 설정
        self.ball_radius = 10
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_base_speed = 5  # 기본 속도
        self.ball_speed_multiplier = 1.0  # 속도 배율
        self.ball_max_speed_multiplier = 2.0  # 최대 속도 배율
        self.ball_dx = self.ball_base_speed
        self.ball_dy = -self.ball_base_speed
        self.speed_increase_interval = 10  # 10초마다 속도 증가
        self.last_speed_increase = time.time()  # 마지막 속도 증가 시간

        # 벽돌 설정
        self.brick_width, self.brick_height = 80, 30
        self.brick_rows = 5
        self.brick_cols = 10
        self.brick_gap = 5
        self.bricks = []

        # 게임 변수
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.font = get_font(36)
        self.small_font = get_font(28)
        self.game_start_time = time.time()  # 게임 시작 시간

        # 버튼 설정
        self.button_width, self.button_height = 200, 50
        self.restart_button = pygame.Rect((width // 2) - self.button_width - 20, height // 2 + 60, self.button_width, self.button_height)
        self.quit_button = pygame.Rect((width // 2) + 20, height // 2 + 60, self.button_width, self.button_height)

        # 초기 벽돌 생성
        self.initialize_bricks()

    # 벽돌 초기화 함수
    def initialize_bricks(self):
        self.bricks = []
        for i in range(self.brick_rows):
            for j in range(self.brick_cols):
                brick_x = j * (self.brick_width + self.brick_gap)
                brick_y = 50 + i * (self.brick_height + self.brick_gap)
                color = COLORS[i % len(COLORS)]
                brick = {
                    'rect': pygame.Rect(brick_x, brick_y, self.brick_width, self.brick_height),
                    'color': color,
                    'hits': 1
                }
                self.bricks.append(brick)

    # 게임 리셋 함수
    def reset_game(self):
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_speed_multiplier = 1.0  # 속도 배율 초기화
        self.ball_dx = random.choice([-1, 1]) * self.ball_base_speed * self.ball_speed_multiplier
        self.ball_dy = -self.ball_base_speed * self.ball_speed_multiplier
        self.paddle_x = (width - self.paddle_width) // 2
        self.paddle_y = height - self.paddle_height - 10
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.lives = 3
        self.last_speed_increase = time.time()  # 마지막 속도 증가 시간 초기화
        self.game_start_time = time.time()  # 게임 시작 시간 초기화
        self.initialize_bricks()

    # 현재 공의 속도를 계산하는 함수
    def get_ball_speed(self):
        speed = ((self.ball_dx ** 2 + self.ball_dy ** 2) ** 0.5)  # 피타고라스 정리로 실제 속도 계산
        return round(speed, 1)

    # 게임 상태 업데이트 함수
    def update(self):
        if self.game_over or self.game_won:
            return

        current_time = time.time()

        # 시간 경과에 따른 공 속도 증가
        if current_time - self.last_speed_increase > self.speed_increase_interval and self.ball_speed_multiplier < self.ball_max_speed_multiplier:
            self.ball_speed_multiplier += 0.1  # 10% 속도 증가
            self.ball_speed_multiplier = min(self.ball_speed_multiplier, self.ball_max_speed_multiplier)  # 최대값 제한
            
            # 현재 방향 유지하면서 속도만 증가
            ball_speed = self.get_ball_speed()
            direction_x = self.ball_dx / ball_speed
            direction_y = self.ball_dy / ball_speed
            
            # 새로운 속도 적용
            new_speed = self.ball_base_speed * self.ball_speed_multiplier
            self.ball_dx = direction_x * new_speed
            self.ball_dy = direction_y * new_speed
            
            self.last_speed_increase = current_time

        # 키 입력 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.paddle_x > 0:
            self.paddle_x -= self.paddle_speed
        if keys[pygame.K_RIGHT] and self.paddle_x < width - self.paddle_width:
            self.paddle_x += self.paddle_speed

        # 공 이동
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # 벽 충돌 처리
        if self.ball_x <= self.ball_radius or self.ball_x >= width - self.ball_radius:
            self.ball_dx *= -1
        if self.ball_y <= self.ball_radius:
            self.ball_dy *= -1

        # 패들 충돌 처리
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height)
        if (self.ball_y + self.ball_radius >= self.paddle_y and 
            self.ball_y - self.ball_radius <= self.paddle_y + self.paddle_height and
            self.ball_x >= self.paddle_x and self.ball_x <= self.paddle_x + self.paddle_width):
            # 패들 위치에 따라 반사각 조절
            relative_intersection = (self.paddle_x + self.paddle_width / 2) - self.ball_x
            normalized_intersection = relative_intersection / (self.paddle_width / 2)
            angle = normalized_intersection * 0.8
            speed = self.get_ball_speed()
            self.ball_dx = -angle * speed
            self.ball_dy = -abs(self.ball_dy)  # 항상 위로 튕기게

        # 벽돌 충돌 처리
        for brick in self.bricks[:]:
            if brick['rect'].collidepoint(self.ball_x, self.ball_y):
                self.ball_dy *= -1
                brick['hits'] -= 1
                if brick['hits'] <= 0:
                    self.bricks.remove(brick)
                    self.score += 10
                break

        # 바닥에 공이 떨어졌을 때
        if self.ball_y >= height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # 공 위치 리셋
                self.ball_x = width // 2
                self.ball_y = height // 2
                # 방향은 랜덤하게, 속도는 현재 배율 유지
                self.ball_dx = random.choice([-1, 1]) * self.ball_base_speed * self.ball_speed_multiplier
                self.ball_dy = -self.ball_base_speed * self.ball_speed_multiplier
                # 패들 위치 리셋
                self.paddle_x = (width - self.paddle_width) // 2

        # 모든 벽돌을 깼는지 확인
        if len(self.bricks) == 0:
            self.game_won = True

    # 게임 그리기 함수
    def draw(self):
        screen.fill(BLACK)
        
        current_time = time.time()
        
        if self.game_over or self.game_won:
            if self.game_over:
                text = render_text(TEXT_GAME_OVER, self.font, RED)
            else:
                text = render_text(TEXT_GAME_WIN, self.font, GREEN)
            
            # 게임 결과와 점수 표시
            score_text = render_text(f"{TEXT_FINAL_SCORE} {self.score}", self.font, WHITE)
            instruction_text = render_text(TEXT_SELECT, self.small_font, WHITE)
            
            # 텍스트 위치 조정
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 80))
            screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 - 30))
            screen.blit(instruction_text, (width // 2 - instruction_text.get_width() // 2, height // 2 + 20))
            
            # 버튼 그리기
            pygame.draw.rect(screen, GREEN, self.restart_button)
            pygame.draw.rect(screen, RED, self.quit_button)
            
            # 버튼 텍스트
            restart_text = render_text(TEXT_RESTART, self.font, BLACK)
            quit_text = render_text(TEXT_QUIT, self.font, BLACK)
            
            # 버튼 텍스트 위치 조정
            screen.blit(restart_text, (self.restart_button.centerx - restart_text.get_width() // 2, 
                                      self.restart_button.centery - restart_text.get_height() // 2))
            screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width() // 2, 
                                   self.quit_button.centery - quit_text.get_height() // 2))
        else:
            # 벽돌 그리기
            for brick in self.bricks:
                pygame.draw.rect(screen, brick['color'], brick['rect'])
            
            # 패들 그리기
            pygame.draw.rect(screen, WHITE, (self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height))
            
            # 공 그리기
            pygame.draw.circle(screen, WHITE, (int(self.ball_x), int(self.ball_y)), self.ball_radius)
            
            # 게임 정보 표시
            score_text = render_text(f"{TEXT_SCORE} {self.score}", self.font, WHITE)
            lives_text = render_text(f"{TEXT_LIVES} {self.lives}", self.font, WHITE)
            speed_text = render_text(f"{TEXT_SPEED} {self.get_ball_speed():.1f}", self.font, YELLOW)
            elapsed_text = render_text(f"{TEXT_TIME} {int(current_time - self.game_start_time)}초", self.small_font, WHITE)
            
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (width - 100, 10))
            screen.blit(speed_text, (10, 50))
            screen.blit(elapsed_text, (10, 90))

    # 이벤트 처리 함수
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.reset_game()
            
            # 마우스 클릭 처리 (게임 오버 또는 승리 상태에서만)
            if event.type == pygame.MOUSEBUTTONDOWN and (self.game_over or self.game_won):
                mouse_pos = event.pos
                if self.restart_button.collidepoint(mouse_pos):
                    self.reset_game()
                elif self.quit_button.collidepoint(mouse_pos):
                    return False
        return True

# 메인 게임 루프 (비동기 함수로 변경)
async def main():
    game = Game()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
        
        # asyncio가 동작할 수 있게 제어권을 잠시 양보
        await asyncio.sleep(0)
    
    pygame.quit()

# Pygbag에서 요구하는 비동기 방식으로 게임 시작
asyncio.run(main()) 