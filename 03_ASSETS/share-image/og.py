import sys,json
from playwright.sync_api import sync_playwright
v=json.loads(sys.argv[1]); out=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1200,'height':630},device_scale_factor=1)
    pg.goto('file://'+sys.argv[3]); pg.evaluate("document.fonts.ready")
    for k,val in v.items(): pg.evaluate(f"document.getElementById('c').style.setProperty('--{k}','{val}')")
    pg.wait_for_timeout(800)
    print(pg.evaluate("()=>{const r=e=>{const b=document.querySelector(e).getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)]};return {mary:r('.mary'),josh:r('.josh'),k:r('.k'),w:r('.w'),font:document.fonts.check('800 20px Teachers')}}"))
    pg.locator('#c').screenshot(path=out); b.close()
