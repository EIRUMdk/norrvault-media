import json, subprocess, sys, os
from playwright.sync_api import sync_playwright
sys.path.insert(0, '/home/claude/norrvault-reel')
from specs import SPECS, build
rid = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'full'
ideas = json.load(open('/home/claude/norrvault-carousel/ideas.json')) + json.load(open('/home/claude/norrvault-reel/extra-ideas.json'))
spec = SPECS[rid]
idea = next(i for i in ideas if i['no'] == spec['vault'])
reel = build(spec, idea)
out = f'/home/claude/norrvault-reel/out2/{rid}'
os.makedirs(out, exist_ok=True)
FPS = 30
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.add_init_script(f'window.REEL={json.dumps(reel)};')
    pg.goto('file:///home/claude/norrvault-reel/reel2.html')
    pg.wait_for_selector('body[data-ready="1"]')
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(500)
    if mode == 'stills':
        for t in [float(x) for x in sys.argv[3].split(',')]:
            pg.evaluate(f'render({t})')
            pg.screenshot(path=f'{out}/still-{t}.jpg', type='jpeg', quality=85)
    else:
        total = 36.0
        tmp = f'{out}/raw.mp4'
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
        for f in range(round(total * FPS)):
            pg.evaluate(f'render({f / FPS})')
            ff.stdin.write(pg.screenshot(type='jpeg', quality=90))
        ff.stdin.close()
        if ff.wait() != 0: sys.exit('ffmpeg failed')
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', f'{out}/reel-{rid}.mp4'])
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '26.6', '-i', f'{out}/reel-{rid}.mp4', '-frames:v', '1', '-q:v', '2', f'{out}/reel-{rid}-cover.jpg'])
    b.close()
