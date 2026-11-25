"""Builds the week's 16-second text videos (1080x1920) from the card text below.
Free, local: Chrome renders each card to PNG, ffmpeg cross-fades them.
Usage: python3 build.py [T004 T005 ...]   Output: out/<id>.mp4 + out/<id>-cardN.png
Edit the text here, re-run, re-upload. Founding count lives in FOUNDING_LEFT."""
import asyncio, subprocess, sys, os
from playwright.async_api import async_playwright
FOUNDING_LEFT = 197   # re-check on the site before every use
CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;background:#0a1f3c;color:#fff;font-family:"Inter Display","Inter",sans-serif;overflow:hidden}
.top{position:absolute;left:84px;top:120px;font-size:24px;letter-spacing:3px;font-weight:700;color:#93a4bd}
.c{position:absolute;left:84px;right:84px;top:300px;height:1000px;display:flex;flex-direction:column;justify-content:center}
h1{font-size:96px;line-height:1.08;font-weight:800;letter-spacing:-2px}
h2{font-size:80px;line-height:1.1;font-weight:800;letter-spacing:-1.5px}
.y{color:#fbbf24}.g{color:#34d399}.r{color:#fb7185}
.sub{margin-top:36px;font-size:40px;line-height:1.3;color:#e2e8f0;font-weight:500}
.tag{align-self:flex-start;background:#fbbf24;color:#0a1f3c;font-weight:800;font-size:26px;letter-spacing:2px;padding:12px 20px;border-radius:8px;margin-bottom:36px}
.rows{margin-top:56px}.row{display:flex;justify-content:space-between;align-items:baseline;font-size:46px;font-weight:700;padding:30px 0;border-bottom:2px solid #1e3a5f}
.row span:last-child{color:#34d399}.row.dim span:last-child{color:#93a4bd}
ol{list-style:none}ol li{display:flex;gap:28px;font-size:58px;line-height:1.18;font-weight:700;margin-bottom:56px}
ol li b{color:#fbbf24;min-width:60px}
.lab{font-size:30px;letter-spacing:3px;font-weight:800;margin-bottom:14px}
.pair{font-size:66px;line-height:1.14;font-weight:800;margin-bottom:64px}
.big{font-size:260px;font-weight:800;color:#fbbf24;line-height:1;letter-spacing:-6px}
.btn{align-self:flex-start;margin-top:56px;background:#fbbf24;color:#0a1f3c;font-weight:800;font-size:44px;padding:26px 36px;border-radius:14px}
.k{font-size:64px;font-weight:800;color:#fbbf24;margin-bottom:16px}
.line{font-size:72px;font-weight:800;line-height:1.15;margin-bottom:44px}"""
END = """<h2>Coaches &amp; consultants: <span class="y">0% commission.</span></h2>
<div class="sub">Standard card processing applies. Free to join. Founding Members get Elite Pro free forever.</div>
<div class="btn">mytruenorthconsultants.com</div>"""
V = {
"T004": ["""<h1>Should clients find you by <span class="y">who pays the most</span>… or by <span class="g">who fits best?</span></h1>""",
 """<h2>On TrueNorth, <span class="g">fit comes first.</span></h2><div class="rows">
 <div class="row"><span>Strong match</span><span>75%+</span></div>
 <div class="row"><span>Good match</span><span>60–74%</span></div>
 <div class="row dim"><span>Below 60%</span><span>Not shown in AI Match</span></div></div>""",
 """<h2>Paid plans are listed first <span class="g">only inside the same 10-point band.</span></h2>
 <div class="sub">Fit decides the band. It’s all on our public How We Rank page.</div>"""],
"T005": ["""<h1><span class="y">5 things</span> consultants are glad they stopped doing</h1>""",
 """<ol><li><b>1.</b><span>Giving away 20% of every booking</span></li><li><b>2.</b><span>Bidding against other pros just to be seen</span></li><li><b>3.</b><span>Letting a platform stand between them and their client’s payment</span></li></ol>""",
 """<ol><li><b>4.</b><span>Getting ranked by who pays, not who fits</span></li><li><b>5.</b><span>Waiting for “someday” to build their client base</span></li></ol>"""],
"T006": ["""<h1><span class="r">Year 0 coach</span></h1><div class="sub">vs</div><h1 style="margin-top:36px"><span class="g">Year 5 coach</span></h1>""",
 """<div class="lab r">YEAR 0</div><div class="pair">Shrugs at a 20% cut.</div><div class="lab g">YEAR 5</div><div class="pair">Knows that’s $12,000 a year on $5K a month.</div>""",
 """<div class="lab r">YEAR 0</div><div class="pair">Pays to be seen.</div><div class="lab g">YEAR 5</div><div class="pair">Wants to be matched on fit.</div>"""],
"T007": ["""<div class="tag">SMALL BUSINESS SATURDAY</div><h1><span class="g">Free</span> expert help worth knowing about</h1>""",
 """<div class="k">SCORE</div><div class="sub" style="margin-top:0;margin-bottom:72px">Free mentoring from a network of 10,000+ volunteer business experts.</div>
 <div class="k">SBDCs, Women’s Business Centers &amp; VBOCs</div><div class="sub" style="margin-top:0">SBA partners offering free or low-cost counseling and training near you.</div>""",
 """<h2>Find yours by ZIP code at <span class="y">sba.gov/local-assistance</span></h2><div class="sub">Need a specialist after that? That’s what consultants are for.</div>"""],
"T008": ["""<div class="tag">BUILDING IN PUBLIC · WEEK 1</div><h1>We’re building a coach &amp; consultant marketplace that takes <span class="y">0%</span> commission.</h1>""",
 f"""<div class="big">{FOUNDING_LEFT}</div><h2>of 200 founding spots left.</h2><div class="sub">Founding Members get Elite Pro free forever. Never reopened.</div>""",
 """<div class="line"><span class="g">0%</span> commission.</div><div class="line">Ranked by <span class="g">fit</span>.</div><div class="line">Paid to your own <span class="g">Stripe</span> account.</div><div class="sub">Standard card processing applies.</div>"""],
}
DUR=[4.0,4.5,4.0,3.5]; F=0.4
async def main(ids):
    os.makedirs('out',exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        for i in ids:
            cards=V[i]+[END]
            for n,c in enumerate(cards,1):
                await pg.set_content(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="top">TRUENORTH CONSULTANTS · COACH &amp; CONSULTANT MARKETPLACE</div><div class="c">{c}</div>')
                await pg.wait_for_timeout(300)
                ov=await pg.evaluate("(()=>{const c=document.querySelector('.c');return [c.scrollHeight,c.clientHeight,c.scrollWidth,c.clientWidth]})()")
                assert ov[0]<=ov[1] and ov[2]<=ov[3], (i,n,ov)
                await pg.screenshot(path=f'out/{i}-card{n}.png')
            cmd=['ffmpeg','-y','-loglevel','error']
            for n,d in enumerate(DUR,1): cmd+=['-loop','1','-t',str(d+(F if n<4 else 0)),'-i',f'out/{i}-card{n}.png']
            cmd+=['-f','lavfi','-t','16','-i','anullsrc=r=44100:cl=stereo']
            off=0; fc=''; prev='0:v'
            for n in range(1,4):
                off+=DUR[n-1]; fc+=f'[{prev}][{n}:v]xfade=transition=fade:duration={F}:offset={off}[x{n}];'; prev=f'x{n}'
            fc+=f'[{prev}]fps=30,format=yuv420p[v]'
            cmd+=['-filter_complex',fc,'-map','[v]','-map','4:a','-c:v','libx264','-crf','18','-c:a','aac','-b:a','96k','-t','16','-movflags','+faststart',f'out/{i}.mp4']
            subprocess.run(cmd,check=True); print('built',i)
        await b.close()
asyncio.run(main(sys.argv[1:] or list(V)))
