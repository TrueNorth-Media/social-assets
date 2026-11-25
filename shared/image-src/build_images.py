"""Rebuilt week 1 stills with corrected wording. python3 build_images.py -> ../week1-images/"""
import asyncio
from playwright.async_api import async_playwright
B='*{box-sizing:border-box;margin:0;padding:0}body{background:#0a1f3c;color:#fff;font-family:"Inter Display","Inter",sans-serif;overflow:hidden;position:relative}.y{color:#fbbf24}.btn{display:inline-block;background:#fbbf24;color:#0a1f3c;font-weight:800;border-radius:12px}'
PIN=f"""<style>{B}body{{width:1000px;height:1500px;padding:110px 90px}}
h1{{font-size:84px;line-height:1.05;font-weight:800;letter-spacing:-2px;margin-bottom:90px}}
.s{{display:flex;gap:44px;margin-bottom:70px}}.n{{font-size:96px;font-weight:800;color:#fbbf24;line-height:.95;min-width:70px}}
.t{{font-size:48px;font-weight:800;margin-bottom:10px}}.d{{font-size:33px;line-height:1.3;color:#dbe4f0}}
.btn{{position:absolute;left:90px;right:90px;bottom:110px;text-align:center;font-size:42px;padding:30px}}
.f{{position:absolute;left:90px;bottom:54px;font-size:22px;color:#93a4bd;font-weight:600}}</style>
<h1>How TrueNorth works for coaches &amp; consultants</h1>
<div class="s"><div class="n">1</div><div><div class="t">Create your profile</div><div class="d">Free to list. 0% commission on bookings.</div></div></div>
<div class="s"><div class="n">2</div><div><div class="t">Get matched on fit</div><div class="d">Clients see you when you’re a strong or good match.</div></div></div>
<div class="s"><div class="n">3</div><div><div class="t">Get paid directly</div><div class="d">Clients pay you straight to your own Stripe account. Standard card processing applies.</div></div></div>
<div class="btn">mytruenorthconsultants.com</div><div class="f">TrueNorth Consultants · coach &amp; consultant marketplace</div>"""
SLIDE=f"""<style>{B}body{{width:1080px;height:1350px}}.c{{position:absolute;left:96px;right:96px;top:360px}}
h1{{font-size:82px;line-height:1.08;font-weight:800;letter-spacing:-1.5px}}p{{margin-top:40px;font-size:42px;line-height:1.38;color:#dbe4f0}}
.btn{{margin-top:48px;font-size:42px;padding:28px 34px}}.f{{position:absolute;left:96px;bottom:74px;font-size:27px;color:#93a4bd;font-weight:600}}
.dots{{position:absolute;right:96px;bottom:80px;display:flex;gap:12px}}.dots i{{width:13px;height:13px;border-radius:50%;background:#33507a}}.dots i:last-child{{background:#fbbf24}}</style>
<div class="c"><h1>Find all four by ZIP code at <span class="y">sba.gov/local-assistance</span></h1>
<p>Need a specialist beyond that? TrueNorth Consultants is a marketplace for coaches and consultants, ranked by fit.</p>
<div class="btn">mytruenorthconsultants.com</div></div>
<div class="f">TrueNorth Consultants · coach &amp; consultant marketplace</div><div class="dots"><i></i><i></i><i></i><i></i><i></i><i></i></div>"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        for html,w,h,o in((PIN,1000,1500,'T008-pin.png'),(SLIDE,1080,1350,'T007-slide6.png')):
            pg=await b.new_page(viewport={'width':w,'height':h}); await pg.set_content('<!doctype html><meta charset="utf-8">'+html); await pg.wait_for_timeout(300)
            await pg.screenshot(path='../week1-images/'+o)
        await b.close()
asyncio.run(main())
