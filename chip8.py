import sys
import pygame
import random

def init_chip8():
    state={
        'memory':bytearray(4096), #memory for the chip8 interpreter(4kb ram)
        'v':bytearray(16), #16 8-bit registers (v0-vf)
        'i':0, #index register (used as a register for memory addresses and as a pointer)
        'pc':0x200, #program counter starts at 0x200 (tells cpu what instruction to execute next)
        'stack':[], #list of previous program counter values 
        'delay':0, #timer 
        'soundtimer':0, #sound timer
        'gfx':[0]*(64*32), #display buffer
        'draw':False, #flag to indicate if we need to redraw the screen
        'key':([0]*16) #keyboard taht displays 16 keys 0-F
        }
    font(state)
    return state

def font(state):
    '''
    displays the numbers and letters in hexadecimal (0-F)
    so to display 1 for example 
    0x20:  *
    0x60: **
    0x20:  *
    0x20:  *
    0x70: ***
    '''
    fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, #0 
        0x20, 0x60, 0x20, 0x20, 0x70, #1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
        0x90, 0x90, 0xF0, 0x10, 0x10, #4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
        0xF0, 0x10, 0x20, 0x40, 0x40, #7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
        0xF0, 0x90, 0xF0, 0x90, 0x90, #A 
        0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
        0xF0, 0x80, 0x80, 0x80, 0xF0, #C
        0xE0, 0x90, 0x90, 0x90, 0xE0, #D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
        0xF0, 0x80, 0xF0, 0x80, 0x80  #F
    ]
    #stores the fonset into memory starting at 0x50
    state['memory'][0x50:0x50 + len(fontset)] = fontset

def loadrom(state,filename): #function to load the rom into memory
    try:
        with open(filename, 'rb') as f: #opens the rom file in binary
            rom=f.read() #reads the rom file
            state['memory'][0x200:0x200+len(rom)]=rom #loads the rom into memory starting at 0x200
    except FileNotFoundError: #exceptioon handling
        print("file not found")
        sys.exit(1)
def updatetimer(state):
    if state['delay']>0:
        state['delay']-=1
    if state['soundtimer']>0:
        if state['soundtimer']==1:
            print("beep")
        state['soundtimer']-=1
def emulatecycle(state):
    pc=state['pc']
    opcode=(state['memory'][pc]<<8)|state['memory'][pc+1]
    addr = opcode & 0x0FFF
    kk = opcode & 0x00FF
    n = opcode & 0x000F
    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4
    state['pc'] += 2
    if opcode & 0xF000 == 0x0000:
        if opcode == 0x00E0: 
            state['gfx'] = [0] * (64 * 32)
            state['draw'] = True
        elif opcode == 0x00EE: 
            state['pc'] = state['stack'].pop()
    elif opcode & 0xF000 == 0x1000: 
        state['pc'] = addr
    elif opcode & 0xF000 == 0x2000: 
        state['stack'].append(state['pc'])
        state['pc'] = addr
    elif opcode & 0xF000 == 0x3000:  
        if state['v'][x] == kk:
            state['pc'] += 2
    elif opcode & 0xF000 == 0x4000: 
        if state['v'][x] != kk:
            state['pc'] += 2
    elif opcode & 0xF000 == 0x5000: 
        if state['v'][x] == state['v'][y]:
            state['pc'] += 2
    elif opcode & 0xF000 == 0x6000: 
        state['v'][x] = kk
    elif opcode & 0xF000 == 0x7000: 
        state['v'][x] = (state['v'][x] + kk) & 0xFF
    elif opcode & 0xF000 == 0x8000:
        if n == 0x0:  
            state['v'][x] = state['v'][y]
        elif n == 0x1: 
            state['v'][x] |= state['v'][y]
        elif n == 0x2: 
            state['v'][x] &= state['v'][y]
        elif n == 0x3: 
            state['v'][x] ^= state['v'][y]
        elif n == 0x4:
            result = state['v'][x] + state['v'][y]
            state['v'][0xF] = 1 if result > 255 else 0
            state['v'][x] = result & 0xFF
        elif n == 0x5: 
            state['v'][0xF] = 1 if state['v'][x] > state['v'][y] else 0
            state['v'][x] = (state['v'][x] - state['v'][y]) & 0xFF
        elif n == 0x6: 
            state['v'][0xF] = state['v'][x] & 0x1
            state['v'][x] >>= 1
        elif n == 0x7: 
            state['v'][0xF] = 1 if state['v'][y] > state['v'][x] else 0
            state['v'][x] = (state['v'][y] - state['v'][x]) & 0xFF
        elif n == 0xE: 
            state['v'][0xF] = (state['v'][x] & 0x80) >> 7
            state['v'][x] <<= 1
            state['v'][x] &= 0xFF
    elif opcode & 0xF000 == 0x9000: 
        if state['v'][x] != state['v'][y]:
            state['pc'] += 2
    elif opcode & 0xF000 == 0xA000: 
        state['i'] = addr
    elif opcode & 0xF000 == 0xB000:  
        state['pc'] = addr + state['v'][0]
    elif opcode & 0xF000 == 0xC000:
        state['v'][x] = random.randint(0, 255) & kk
    elif opcode & 0xF000 == 0xD000:
        state['v'][0xF] = 0
        x_coord = state['v'][x] % 64
        y_coord = state['v'][y] % 32
        for row in range(n):
            sprite_byte = state['memory'][state['i'] + row]
            for col in range(8):
                if (sprite_byte & (0x80 >> col)) != 0:
                    if (x_coord + col < 64) and (y_coord + row < 32):
                        pixel_index = (x_coord + col) + ((y_coord + row) * 64)
                        if state['gfx'][pixel_index] == 1:
                            state['v'][0xF] = 1
                        state['gfx'][pixel_index] ^= 1
        state['draw'] = True
    elif opcode & 0xF000 == 0xE000:
        if kk == 0x9E: 
            if state['key'][state['v'][x]] != 0:
                state['pc'] += 2
        elif kk == 0xA1: 
            if state['key'][state['v'][x]] == 0:
                state['pc'] += 2
    elif opcode & 0xF000 == 0xF000:
        if kk == 0x07:
            state['v'][x] = state['delay']
        elif kk == 0x0A: 
            key_pressed = False
            for i in range(16):
                if state['key'][i] != 0:
                    state['v'][x] = i
                    key_pressed = True
            if not key_pressed:
                state['pc'] -= 2
        elif kk == 0x15: 
            state['delay'] = state['v'][x]
        elif kk == 0x18:
            state['soundtimer'] = state['v'][x]
        elif kk == 0x1E:
            state['i'] += state['v'][x]
        elif kk == 0x29:
            state['i'] = (state['v'][x] * 5) + 0x50
        elif kk == 0x33:
            num = state['v'][x]
            state['memory'][state['i']] = num // 100
            state['memory'][state['i'] + 1] = (num // 10) % 10
            state['memory'][state['i'] + 2] = num % 10
        elif kk == 0x55:
            for i in range(x + 1):
                state['memory'][state['i'] + i] = state['v'][i]
        elif kk == 0x65: 
            for i in range(x + 1):
                state['v'][i] = state['memory'][state['i'] + i]
def main():
    rompath=sys.argv[1]
    scale=15
    cycles=10
    chip8state=init_chip8()
    loadrom(chip8state,rompath)
    pygame.init()
    screenwid=64*scale
    screenheight=32*scale
    screen=pygame.display.set_mode((screenwid,screenheight))
    pygame.display.set_caption("chip8")
    clock=pygame.time.Clock()
    keymap = {pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,}
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.KEYDOWN:
                if event.key in keymap:
                    chip8state['key'][keymap[event.key]]=1
            if event.type==pygame.KEYUP:
                if event.key in keymap:
                    chip8state['key'][keymap[event.key]]=0
        for i in range(cycles):
            emulatecycle(chip8state)
        updatetimer(chip8state)
        if chip8state['draw']:
            screen.fill((0,0,0))
            for i in range(len(chip8state['gfx'])):
                if chip8state['gfx'][i]==1:
                    x=(i%64)*scale
                    y=(i//64)*scale
                    pygame.draw.rect(screen,(255,255,255),(x,y,scale,scale))
            pygame.display.flip()
            chip8state['draw']=False
        clock.tick(60)
    pygame.quit()
if __name__=='__main__':
    main()