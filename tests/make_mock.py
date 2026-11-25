from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, glob
fp = (glob.glob("/usr/share/fonts/**/LiberationSerif-Regular.ttf", recursive=True) or glob.glob("/usr/share/fonts/**/*Serif*.ttf", recursive=True))[0]
f = ImageFont.truetype(fp, 22); fb = ImageFont.truetype(fp.replace("Regular","Bold") if "Regular" in fp else fp, 24)
W,H=900,700; im=Image.new("RGB",(W,H),(236,226,198)); d=ImageDraw.Draw(im)
y=30
def street(t):
    global y; d.text((W//2-len(t)*7,y),t,font=fb,fill=(40,30,25)); y+=40
def row(n,name):
    global y; d.text((40,y),n,font=f,fill=(40,30,25)); d.text((140,y),name,font=f,fill=(40,30,25)); y+=32
street("CHOWRINGHEE ROAD.")
row("1","Bengal Club ......... club")
row("4, 5 & 6","Mockridge & Co. ....... general drapers")
row("9","Hall, J. T. ....... photographer")
row("12A","Dass, R. N. ....... jeweller")
street("CLIVE STREET.")
row("3","Eastern Jute Mills Agency ....... merchants")
row("14/2","Roy & Sons ....... booksellers")
row("21","Pereira, M. ....... tailor")
im=im.rotate(1.2,expand=False,fillcolor=(236,226,198),resample=Image.BICUBIC)
a=np.array(im).astype(int)+np.random.normal(0,14,(H,W,3)); im=Image.fromarray(np.clip(a,0,255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.7))
im.save("mock_page.png")
