import re,sys,json,math
import xml.etree.ElementTree as ET
SRC=sys.argv[1]; OUT=sys.argv[2]
names={2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen'}
TOK=re.compile(r'([MmLlHhVvCcSsZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)')
def flatten(d,n=6):
    subs=[];cur=[];x=y=0;sx=sy=0;cmd=None;px=py=None
    toks=[(a,b) for a,b in TOK.findall(d)]
    i=0
    def num():
        nonlocal i
        v=float(toks[i][1]); i+=1; return v
    while i<len(toks):
        if toks[i][0]:
            cmd=toks[i][0]; i+=1
            if cmd in 'Zz':
                if cur: cur.append((sx,sy)); subs.append(cur); cur=[]
                x,y=sx,sy; px=py=None
                continue
        c=cmd
        if c in 'Mm':
            nx,ny=num(),num()
            if c=='m': nx+=x; ny+=y
            if cur: subs.append(cur)
            cur=[(nx,ny)]; x,y=nx,ny; sx,sy=x,y; cmd='L' if c=='M' else 'l'; px=py=None
        elif c in 'Ll':
            nx,ny=num(),num()
            if c=='l': nx+=x; ny+=y
            x,y=nx,ny; cur.append((x,y)); px=py=None
        elif c in 'Hh':
            nx=num(); x = x+nx if c=='h' else nx; cur.append((x,y)); px=py=None
        elif c in 'Vv':
            ny=num(); y = y+ny if c=='v' else ny; cur.append((x,y)); px=py=None
        elif c in 'CcSs':
            if c in 'Cc':
                x1,y1,x2,y2,x3,y3=[num() for _ in range(6)]
                if c=='c': x1+=x;y1+=y;x2+=x;y2+=y;x3+=x;y3+=y
            else:
                x2,y2,x3,y3=[num() for _ in range(4)]
                if c=='s': x2+=x;y2+=y;x3+=x;y3+=y
                if px is None: x1,y1=x,y
                else: x1,y1=2*x-px,2*y-py
            for k in range(1,n+1):
                t=k/n;u=1-t
                cur.append((u*u*u*x+3*u*u*t*x1+3*u*t*t*x2+t*t*t*x3, u*u*u*y+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3))
            px,py=x2,y2; x,y=x3,y3
        else:
            i+=1
    if cur: subs.append(cur)
    return subs
def simplify(pts,eps):
    if len(pts)<3: return pts
    if math.hypot(pts[0][0]-pts[-1][0],pts[0][1]-pts[-1][1])<1e-6 and len(pts)>3:
        far=max(range(len(pts)),key=lambda k:math.hypot(pts[k][0]-pts[0][0],pts[k][1]-pts[0][1]))
        a=simplify(pts[:far+1],eps); b=simplify(pts[far:],eps)
        return a[:-1]+b
    def rdp(a,b):
        ax,ay=pts[a];bx,by=pts[b];dx=bx-ax;dy=by-ay;L=math.hypot(dx,dy) or 1e-9
        m=0;mi=-1
        for k in range(a+1,b):
            d=abs((pts[k][0]-ax)*dy-(pts[k][1]-ay)*dx)/L
            if d>m:m=d;mi=k
        if m>eps: return rdp(a,mi)[:-1]+rdp(mi,b)
        return [pts[a],pts[b]]
    return rdp(0,len(pts)-1)
def pts_attr(s):
    v=[float(t) for t in re.findall(r'-?\d*\.?\d+(?:[eE][-+]?\d+)?',s)]
    return list(zip(v[0::2],v[1::2]))
def shapes(el):
    t=el.tag.split('}')[1]
    g=el.get
    if t=='rect':
        x,y,w,h=float(g('x',0)),float(g('y',0)),float(g('width')),float(g('height'))
        return [[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]]
    if t=='line': return [[(float(g('x1')),float(g('y1'))),(float(g('x2')),float(g('y2')))]]
    if t=='polyline': return [pts_attr(g('points'))]
    if t=='polygon':
        p=pts_attr(g('points')); return [p+[p[0]]] if p else []
    if t=='path': return flatten(g('d',''))
    return []
FILL={'#0089CF':'w','#A1CEE6':'w','#95D0E7':None,'#E5CC93':'s','#F79520':'b'}
out={}
for n,nm in names.items():
    root=ET.parse(f'{SRC}/deck-{nm}.svg').getroot()
    hull=None;cab=[];lines=[];fills=[]
    def walk(el,skip):
        global hull
        tag=el.tag.split('}')[1]
        if tag in('font','text'): return
        i=el.get('id','')
        if tag=='g' and (i.startswith('TEXT') or i.startswith('ICONS') or i.startswith('ROOM_')): skip=True
        if tag!='g' and tag!='svg':
            if i.startswith('IDP-Deck'):
                hull=(hull or [])+[h for h in flatten(el.get('d'),8) if len(h)>3]
            elif re.match(r'R\d+$',i):
                ps=[p for s in shapes(el) for p in s]
                xs=[p[0] for p in ps];ys=[p[1] for p in ps]
                cab.append((int(i[1:]),min(xs),min(ys),max(xs),max(ys)))
            elif not skip:
                f=el.get('fill','none')
                for s in shapes(el):
                    if len(s)<2: continue
                    k=FILL.get(f)
                    if k and len(s)>3: fills.append((k,simplify(s,0.12)))
                    else: lines.append(simplify(s,0.12))
        for c in el:
            if c.tag.split('}')[1]=='path' and el.get('id','').startswith('IDP-Deck'): continue
            walk(c,skip)
    walk(root,False)
    xs=[p[0] for h in hull for p in h];ys=[p[1] for h in hull for p in h]
    cx=(min(xs)+max(xs))/2
    r=lambda v:round(v,1)
    hull=[simplify(h,0.15) for h in hull]
    # drop lines that are tiny
    L2=[]
    for s in lines:
        ln=sum(math.hypot(s[k+1][0]-s[k][0],s[k+1][1]-s[k][1]) for k in range(len(s)-1))
        if ln<1.2: continue
        L2.append([c for p in s for c in (r(p[0]-cx),r(p[1]))])
    out[n]={'y0':r(min(ys)),'y1':r(max(ys)),'hw':r((max(xs)-min(xs))/2),
            'hull':[[c for p in h for c in (r(p[0]-cx),r(p[1]))] for h in hull],
            'cab':[[c[0],r(c[1]-cx),r(c[2]),r(c[3]-c[1]),r(c[4]-c[2])] for c in sorted(cab)],
            'ln':L2,'fl':[[k,[c for p in s for c in (r(p[0]-cx),r(p[1]))]] for k,s in fills]}
    print(n,'hull pts',[len(h) for h in hull],'cabins',len(cab),'lines',len(L2),'fills',len(fills),'y',out[n]['y0'],out[n]['y1'],'hw',out[n]['hw'])
js=json.dumps(out,separators=(',',':'))
open(OUT,'w').write(js); print('bytes',len(js))
