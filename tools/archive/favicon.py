"""Tryptamine favicon generator (indole + C3 ethylamine), skeletal formula."""
import math, cairosvg, pathlib
S = pathlib.Path("/workspace/newsletter/site")
c30, s30 = math.cos(math.radians(30)), 0.5
R = 1/(2*math.sin(math.radians(36)))
cx = c30 + 1/(2*math.tan(math.radians(36)))
def pol(c, r, a): return (c[0]+r*math.cos(math.radians(a)), c[1]+r*math.sin(math.radians(a)))
A = {"C3a": (c30, .5), "C4": (0, 1), "C5": (-c30, .5), "C6": (-c30, -.5), "C7": (0, -1), "C7a": (c30, -.5)}
pc = (cx, 0)
A["N1"] = pol(pc, R, -72); A["C2"] = pol(pc, R, 0); A["C3"] = pol(pc, R, 72)
A["Ca"] = pol(A["C3"], 1, 72); A["Cb"] = pol(A["Ca"], 1, 12); A["Nam"] = pol(A["Cb"], 1, 72)
BONDS = [("C3a","C4"),("C4","C5"),("C5","C6"),("C6","C7"),("C7","C7a"),("C7a","C3a"),
         ("C7a","N1"),("N1","C2"),("C2","C3"),("C3","C3a"),("C3","Ca"),("Ca","Cb"),("Cb","Nam")]
DOUBLE = {("C4","C5"):(0,0),("C6","C7"):(0,0),("C7a","C3a"):(0,0),("C2","C3"):pc}
LABELLED = {"N1","Nam"}
def build(mode):
    # mode: full (N-H + NH2 text), mid (N letters), small (N dots)
    gap = {"full": .30, "mid": .30, "small": 0}[mode]
    sw = {"full": .13, "mid": .27, "small": .36}[mode]
    xs = [p[0] for p in A.values()]; ys = [p[1] for p in A.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if mode == "full": x1 += .55; y0 -= .75; y1 += .25
    elif mode == "mid": y1 += .25; x1 += .25; y0 -= .25
    else: x1 += .1; y1 += .1; y0 -= .1
    pad = 6.5
    sc = (64-2*pad)/max(x1-x0, y1-y0)
    ox = 32 - sc*(x0+x1)/2; oy = 32 + sc*(y0+y1)/2
    T = lambda p: (ox+sc*p[0], oy-sc*p[1])
    def seg(a, b):
        pa, pb = A[a], A[b]; d = math.dist(pa, pb); ux, uy = (pb[0]-pa[0])/d, (pb[1]-pa[1])/d
        ga = gap if a in LABELLED else 0; gb = gap if b in LABELLED else 0
        return (pa[0]+ux*ga, pa[1]+uy*ga), (pb[0]-ux*gb, pb[1]-uy*gb)
    L = []
    for a, b in BONDS:
        p, q = seg(a, b); (X1, Y1), (X2, Y2) = T(p), T(q)
        L.append(f'<line x1="{X1:.2f}" y1="{Y1:.2f}" x2="{X2:.2f}" y2="{Y2:.2f}"/>')
        if (a, b) in DOUBLE and mode == "full":
            ctr = DOUBLE[(a, b)]; p, q = A[a], A[b]; m = ((p[0]+q[0])/2, (p[1]+q[1])/2)
            d = math.dist(m, ctr); vx, vy = (ctr[0]-m[0])/d*.2, (ctr[1]-m[1])/d*.2
            k = .17
            p2 = (p[0]+(q[0]-p[0])*k+vx, p[1]+(q[1]-p[1])*k+vy); q2 = (q[0]+(p[0]-q[0])*k+vx, q[1]+(p[1]-q[1])*k+vy)
            (X1, Y1), (X2, Y2) = T(p2), T(q2)
            L.append(f'<line x1="{X1:.2f}" y1="{Y1:.2f}" x2="{X2:.2f}" y2="{Y2:.2f}"/>')
    txt = []
    acc = "#7fb2e5"
    if mode == "small":
        for n in LABELLED:
            X, Y = T(A[n]); txt.append(f'<circle cx="{X:.2f}" cy="{Y:.2f}" r="{sc*.2:.2f}" fill="{acc}"/>')
    else:
        fs = sc*(.55 if mode == "full" else .62)
        f = f'font-family="Arial,Helvetica,sans-serif" font-weight="700" fill="{acc}" text-anchor="middle"'
        X, Y = T(A["N1"]); txt.append(f'<text x="{X:.2f}" y="{Y+fs*.36:.2f}" font-size="{fs:.2f}" {f}>N</text>')
        if mode == "full": txt.append(f'<text x="{X:.2f}" y="{Y+fs*1.32:.2f}" font-size="{fs:.2f}" {f}>H</text>')
        X, Y = T(A["Nam"]); txt.append(f'<text x="{X:.2f}" y="{Y+fs*.36:.2f}" font-size="{fs:.2f}" {f}>N</text>')
        if mode == "full":
            txt.append(f'<text x="{X+fs*.72:.2f}" y="{Y+fs*.36:.2f}" font-size="{fs:.2f}" {f}>H</text>')
            txt.append(f'<text x="{X+fs*1.22:.2f}" y="{Y+fs*.62:.2f}" font-size="{fs*.62:.2f}" {f}>2</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Tryptamine</title>'
            f'<rect width="64" height="64" rx="13" fill="#11161b"/>'
            f'<g stroke="#e6e9ec" stroke-width="{sc*sw:.2f}" stroke-linecap="round" stroke-linejoin="round">{"".join(L)}</g>{"".join(txt)}</svg>')
if __name__ == "__main__":
    full, mid, small = build("full"), build("mid"), build("small")
    (S/"favicon.svg").write_text(mid)
    cairosvg.svg2png(bytestring=full.encode(), write_to="/workspace/newsletter/favicon-preview.png", output_width=512, output_height=512)
    cairosvg.svg2png(bytestring=full.encode(), write_to=str(S/"apple-touch-icon.png"), output_width=180, output_height=180)
    cairosvg.svg2png(bytestring=mid.encode(), write_to=str(S/"favicon-32.png"), output_width=32, output_height=32)
    cairosvg.svg2png(bytestring=small.encode(), write_to=str(S/"favicon-16.png"), output_width=16, output_height=16)
    # zoomed previews of the small sizes for checking
    from PIL import Image
    for n in ("favicon-32", "favicon-16"):
        Image.open(S/f"{n}.png").resize((256, 256), Image.NEAREST).save(f"/workspace/newsletter/{n}-zoom.png")
