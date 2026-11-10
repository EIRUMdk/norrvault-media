import json, subprocess, sys, os
from playwright.sync_api import sync_playwright

no = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'full'  # 'stills' or 'full'
ideas = json.load(open('/home/claude/norrvault-carousel/ideas.json')) + json.load(open('/home/claude/norrvault-reel/extra-ideas.json'))
idea = next(i for i in ideas if i['no'] == no)
out = f'/home/claude/norrvault-reel/out/{no}'
os.makedirs(out, exist_ok=True)
FPS = 30
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.add_init_script(f'window.IDEA={json.dumps(idea)};')
    pg.goto('file:///home/claude/norrvault-reel/reel.html')
    pg.wait_for_selector('body[data-ready="1"]')
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(500)
    if mode == 'stills':
        for t in [float(x) for x in sys.argv[3].split(',')]:
            pg.evaluate(f'render({t})')
            pg.screenshot(path=f'{out}/still-{t}.jpg', type='jpeg', quality=85)
    else:
        scenes = pg.evaluate('window.SCENES')
        files = []
        for si, (a, e) in enumerate(scenes):
            tmp = f'{out}/scene{si}.tmp.mp4'
            fin = f'{out}/scene{si}.mp4'
            ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
            n = round((e - a) * FPS)
            for f in range(n):
                pg.evaluate(f'render({a + f / FPS})')
                ff.stdin.write(pg.screenshot(type='jpeg', quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                os.rename(tmp, fin); files.append(fin)
            else:
                sys.exit('ffmpeg failed scene %d' % si)
        lst = f'{out}/list.txt'
        open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', f'{out}/norrvault-reel-{no}.mp4'])
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '26.6', '-i', f'{out}/norrvault-reel-{no}.mp4', '-frames:v', '1', '-q:v', '2', f'{out}/norrvault-reel-{no}-cover.jpg'])
    b.close()
