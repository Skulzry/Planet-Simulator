import pygame, math, os, subprocess, platform, copy, time
import tkinter as tk
from tkinter import filedialog

current_dir = os.getcwd()
saved_list = os.listdir(current_dir+'/Saved Sims')
os.chdir(os.getcwd()+'/Saved Sims')
file_list = sorted(saved_list, key=os.path.getctime)

print(file_list)
# 1 planet in list of planets: x, y, radius, colour, vx, vy, gravitational pull, stationary?
def PlanetInfo(i):
    print(saved_list[i%len(saved_list)])
    info = eval(open(current_dir + '/Saved Sims/' + saved_list[i%len(saved_list)], 'r').read())
    return info

def save_file_dialog_windows(saved_list):
    ps_command = (
        'Add-Type -AssemblyName System.Windows.Forms;'
        '$file = New-Object System.Windows.Forms.SaveFileDialog;'
        f'$file.InitialDirectory = "{current_dir}\\Saved Sims";'
        '$file.Filter = "Simulation files (*.sim)|*.sim";'
        '$result = $file.ShowDialog();'
        'if ($result -eq "OK") { $file.FileName }'
    )
    result = subprocess.run(['powershell', '-command', ps_command], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
    if result:
        print(f'\nSaved file as: {result}')
        return result
    else:
        print('\nNo file specified')
        return None

def save_file_dialog_mac(saved_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    current_dir = os.path.dirname(os.path.abspath(__file__))
    initial_dir = os.path.join(current_dir, "Saved Sims")
    file_path = filedialog.asksaveasfilename(initialdir=initial_dir, defaultextension=".sim", filetypes=[("Simulation files", "*.sim")])
    if file_path:
        print(f'\nSaved file as: {file_path}')
        return file_path
    else:
        print('\nNo file specified')
        return None

def save_file_dialog(saved_list):
    if platform.system() == 'Windows':
        return save_file_dialog_windows(saved_list)
    elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
        return save_file_dialog_mac(saved_list)

def easeInLerp(a, b, t):
    return (a * (1 - t) + b * t) * (1 - t) + b * t

def draw_planet(planet_info, trails):
    x = -planet_info[0] + (window.get_width() / 2)
    y = -planet_info[1] + (window.get_height() / 2)
    r = planet_info[2] * 2.4
    colour = planet_info[3]
    for i in range(0,len(trails)-1):
        pygame.draw.line(window, (255, 255, 255), (-trails[i][0] + (window.get_width() / 2), -trails[i][1] + (window.get_height() / 2)), (-trails[i+1][0] + (window.get_width() / 2), -trails[i+1][1] + (window.get_height() / 2)), round((i/(len(trails)-1))*(r/3.5)))
    pygame.draw.circle(canvas, colour, (x, y), r)    

run = True
menu = True

pygame.init()
window = pygame.display.set_mode((1000, 1000), pygame.SRCALPHA)
canvas = pygame.Surface((1000, 1000), pygame.SRCALPHA)
pygame.display.set_caption("Planet Sim")

font = pygame.font.Font(current_dir + '/Data/Fonts/font.ttf', 150)
title1 = font.render('PLANET', True, (255,255,255))
paused1 = font.render('PAUSED', True, (255,255,255))
font = pygame.font.Font(current_dir + '/Data/Fonts/font.ttf', 50)
title2 = font.render('SIMULATOR', True, (255,255,255))
font = pygame.font.Font(current_dir + '/Data/Fonts/font.ttf', 30)
title3 = font.render('Press Space To Start', True, (255,255,255))
paused2 = font.render('Press Escape to Continue', True, (255,255,255))

programIcon = pygame.image.load(current_dir + '/Data/Images/icon.png')
pygame.display.set_icon(programIcon)

def paused():
    pause = True
    #window.fill((0,0,0,125))
    pygame.draw.rect(canvas, pygame.Color(0,0,0,100), [0,0,1000,1000])
    window.blit(canvas, (0,0))
    window.blit(paused1, pygame.Rect((w/2-paused1.get_width()/2), (h/2-paused1.get_height()/2)-270, 564, 350))
    window.blit(paused2, pygame.Rect((w/2-paused2.get_width()/2), (h/2-paused2.get_height()/2)+320, 564, 350))
    pygame.display.update()
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = False
    return True

while menu & run:
    w = pygame.display.get_surface().get_width()
    h = pygame.display.get_surface().get_height()

    window.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                menu = False
    
    window.blit(title1, pygame.Rect((w/2-title1.get_width()/2), (h/2-title1.get_height()/2)-270, 564, 350))
    window.blit(title2, pygame.Rect((w/2-title2.get_width()/2), (h/2-title2.get_height()/2)-200, 564, 350))
    window.blit(title3, pygame.Rect((w/2-title3.get_width()/2), (h/2-title3.get_height()/2)+320, 564, 350))
    pygame.display.update()

planets = PlanetInfo(0)
#print(planets)

planetI = 0
prePlanetFocusedOn = 0  # Initialize prePlanetFocusedOn properly
planetsStatic = copy.deepcopy(planets)  # Create a deep copy of planets
easeInFromX = 0
easeInFromY = 0
SimInfo = None

wasToPop = []
fpsAverege = []
trails = []
for i in range(0,len(planets)):
    trails.append([])

planetFocusedOn = 0

prevTime = time.time()
dt = 0
t = 10

while run:
    for event in pygame.event.get():
        #elif event.type == pygame.VIDEORESIZE:
        #    pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE | pygame.DOUBLEBUF)
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            run = paused()
            prevTime = time.time()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = paused()
                prevTime = time.time()
            if event.key == pygame.K_MINUS:
                planetI -= 1
                planets = PlanetInfo(planetI)
                trails = []
                for i in range(0,len(planets)):
                    trails.append([])
                prePlanetFocusedOn = 0
                planetFocusedOn = 0
                easeInFromX = 0
                easeInFromY = 0
            elif event.key == pygame.K_EQUALS:
                planetI += 1
                planets = PlanetInfo(planetI)
                trails = []
                for i in range(0,len(planets)):
                    trails.append([])
                prePlanetFocusedOn = 0
                planetFocusedOn = 0
                easeInFromX = 0
                easeInFromY = 0

        keys = pygame.key.get_pressed()

        if not (keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]):
            if keys[pygame.K_RIGHT]:
                try:
                    if planetFocusedOn == 0:
                        t = 0
                        easeInFromX = easeInLerp(easeInFromX, planets[0][0], t)
                        easeInFromY = easeInLerp(easeInFromY, planets[0][1], t)
                    else:
                        if t > 1:
                            t = 1
                        easeInFromX = easeInLerp(easeInFromX, planets[int(planetFocusedOn) - 1][0], t)
                        easeInFromY = easeInLerp(easeInFromY, planets[int(planetFocusedOn) - 1][1], t)

                    if planetFocusedOn < len(planets):
                        planetFocusedOn += 1
                    else:
                        planetFocusedOn = 1
                    t = 0
                except:
                    planetFocusedOn = 1
            if keys[pygame.K_LEFT]:
                try:
                    if planetFocusedOn == 0:
                        t = 0
                        easeInFromX = easeInLerp(easeInFromX, planets[-1][0], t)
                        easeInFromY = easeInLerp(easeInFromY, planets[-1][1], t)
                    else:
                        if t > 1:
                            t = 1
                        easeInFromX = easeInLerp(easeInFromX, planets[int(planetFocusedOn) - 1][0], t)
                        easeInFromY = easeInLerp(easeInFromY, planets[int(planetFocusedOn) - 1][1], t)

                    if planetFocusedOn > 1:
                        planetFocusedOn -= 1
                    else:
                        planetFocusedOn = len(planets)
                    t = 0
                except:
                    planetFocusedOn = 1
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_s] and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    file_path = save_file_dialog(saved_list)

                    if file_path:
                        # Write to the file, creating it or replacing it if it already exists
                        try:
                            with open(file_path, 'w') as file:
                                file.write(str(planetsStatic))
                            print(f'File saved successfully: {file_path}')
                            saved_list = os.listdir(current_dir+'/Saved Sims')
                            file_list = sorted(saved_list, key=os.path.getctime)
                            print(file_list)
                        except Exception as e:
                            print(f'Error saving file: {e}')
                    else:
                        print('No file was saved')
                    
                    prevTime = time.time()

    w, h = pygame.display.get_surface().get_size()
    window.fill((0, 0, 0))
    canvas.fill((0, 0, 0, 0))
    
    pygame.time.Clock().tick(250)

    now = time.time()
    dt = now - prevTime
    prevTime = now
    #print(1/dt) #fps test
    fpsAverege.append(round(1/dt))
    pygame.display.set_caption(f"Planet Sim - {round(sum(fpsAverege)/len(fpsAverege))} FPS")
    if len(fpsAverege) > 100000 * dt:
        for i in range(0,round(len(fpsAverege)- (100000 * dt))):
            fpsAverege.pop(0)
    
    toPop = []
    
    # Constants
    G = 2500  # Adjusted gravitational constant for visible effect
    timestep = dt*10  # Adjusted timestep for the simulation

    # Update positions
    for planet in planets:
        if not planet[7]:  # Check if the planet is not stationary
            planet[0] += planet[4] * timestep
            planet[1] += planet[5] * timestep
    
    # Calculate gravitational force
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            # Avoid division by 0
            if planets[i][6] == 0:
                planets[i][6] = 1e-40
            if planets[j][6] == 0:
                planets[j][6] = 1e-40
            
            dx = planets[j][0] - planets[i][0]
            dy = planets[j][1] - planets[i][1]
            dist_squared = dx * dx + dy * dy
            distance = math.sqrt(dist_squared)
            
            force = G * planets[i][6] * planets[j][6] / dist_squared
            force_x = force * (dx / distance)
            force_y = force * (dy / distance)

            planets[i][4] += force_x / planets[i][6] * timestep
            planets[i][5] += force_y / planets[i][6] * timestep
            planets[j][4] -= force_x / planets[j][6] * timestep
            planets[j][5] -= force_y / planets[j][6] * timestep
            
            # Collision detection
            radius_i = planets[i][2] * 2.4
            radius_j = planets[j][2] * 2.4
            if distance < (radius_i + radius_j):
                if planets[i][2] >= planets[j][2]:  # Check if planet i is larger or equal to planet j
                    absorb_index = i
                    absorbed_index = j
                else:
                    absorb_index = j
                    absorbed_index = i

                # Absorb smaller planet into larger one
                total_mass = planets[absorb_index][6] + planets[absorbed_index][6]
                weighted_radius = planets[absorb_index][2] + planets[absorbed_index][2]
                weighted_color = (
                    (planets[absorb_index][3][0] * planets[absorb_index][6] + planets[absorbed_index][3][0] * planets[absorbed_index][6]) / total_mass,
                    (planets[absorb_index][3][1] * planets[absorb_index][6] + planets[absorbed_index][3][1] * planets[absorbed_index][6]) / total_mass,
                    (planets[absorb_index][3][2] * planets[absorb_index][6] + planets[absorbed_index][3][2] * planets[absorbed_index][6]) / total_mass
                )

                planets[absorb_index][2] = weighted_radius
                planets[absorb_index][6] = total_mass
                planets[absorb_index][3] = weighted_color

                toPop.append(absorbed_index)
                try:
                    testPopList = planets[:]
                    testPopList.pop(toPop[-1])
                    if int(planetFocusedOn) - 1 == abs(int(planetFocusedOn) - 1):
                        if int(planetFocusedOn) == absorbed_index + 1:
                            if t > 1:
                                t = 1
                            easeInFromX = easeInLerp(easeInFromX, planets[int(planetFocusedOn) - 1][0], t)
                            easeInFromY = easeInLerp(easeInFromY, planets[int(planetFocusedOn) - 1][1], t)
                            planetFocusedOn = testPopList.index(planets[absorb_index]) + 1
                            t = 0
                        else:
                            planetFocusedOn = testPopList.index(planets[int(planetFocusedOn) - 1]) + 1
                except Exception as e:
                    pass
                
                if absorbed_index < absorb_index:
                    absorb_index -= 1

    for i in range(len(toPop)):
        planets.pop(toPop[i])
        trails.pop(toPop[i])
        wasToPop.append(toPop[0])

    for i in range(0,len(trails)):
        trails[i].append((planets[i][0],planets[i][1]))
        if len(trails[i]) > 200:
            trails[i].pop(0)
    
    for i in range(len(planets)):
        planet = planets[i]
        trailsInfo = list(copy.deepcopy(trails[i]))
        try:
            if int(planetFocusedOn) - 1 == abs(int(planetFocusedOn) - 1):
                if t < 1:
                    planetInfo = [planet[0] - easeInLerp(easeInFromX, planets[int(planetFocusedOn) - 1][0], t), planet[1] - easeInLerp(easeInFromY, planets[int(planetFocusedOn) - 1][1], t), planet[2], planet[3], planet[4], planet[5], planet[6], planet[7]]
                    for j in range(0,len(trailsInfo)):
                        trailsInfo[j] = (trailsInfo[j][0] - easeInLerp(easeInFromX, planets[int(planetFocusedOn) - 1][0], t), trailsInfo[j][1] - easeInLerp(easeInFromY, planets[int(planetFocusedOn) - 1][1], t))
                else:
                    planetInfo = [planet[0] - planets[int(planetFocusedOn) - 1][0], planet[1] - planets[int(planetFocusedOn) - 1][1], planet[2], planet[3], planet[4], planet[5], planet[6], planet[7]]
                    for j in range(0,len(trailsInfo)):
                        trailsInfo[j] = (trailsInfo[j][0] - planets[int(planetFocusedOn) - 1][0], trailsInfo[j][1] - planets[int(planetFocusedOn) - 1][1])
            else:
                planetInfo = planet
        except Exception as e:
            planetInfo = planet
        draw_planet(planetInfo, trailsInfo)
    
    window.blit(canvas, (0,0))
    pygame.display.update()
    canvas.fill((0, 0, 0))

    t += 0.005*timestep*15

    if t > 1:
        prePlanetFocusedOn = planetFocusedOn

pygame.quit()