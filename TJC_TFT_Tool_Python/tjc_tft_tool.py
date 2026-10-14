#!/usr/bin/env python3
"""
tjc_tft_tool.py — Extraction et remplacement des images d'un fichier tjc.tft
(écran TJC 3,2" de l'Ender 3 V3 SE, série « T1 »).

  Extraire : python tjc_tft_tool.py extract tjc.tft dossier_images
  Recréer  : python tjc_tft_tool.py pack tjc.tft dossier_images nouveau.tft
  Vérifier : python tjc_tft_tool.py check nouveau.tft
  Crédits  : python tjc_tft_tool.py version
  Langue   : ajouter --lang en ou --lang fr (par défaut : langue du système)

  [EN] Extract and replace the images of the Ender-3 V3 SE display file (tjc.tft).
       Same commands as above; add --lang en for English messages.
       "pack" starts from the original tjc.tft and only replaces modified images,
       which must keep EXACTLY their original size.

Principe du « pack » : on part du tjc.tft d'origine (pages, code, polices, interpréteur)
et on ne remplace que les images modifiées. Une image doit garder EXACTEMENT ses dimensions.
Les images non modifiées sont recopiées telles quelles, octet pour octet.

Dépendances : pip install pillow numpy

  ╔══════════════════════════════════════════════════════════════════════╗
  ║  Cet outil n'existerait pas sans le travail de rétro-ingénierie de : ║
  ║                                                                      ║
  ║     CLARK SCHEFF (0xD34D)   et   MAX ZUIDBERG (projet UNUF)          ║
  ║                                                                      ║
  ║  Merci à eux. — Thank you both.                                      ║
  ╚══════════════════════════════════════════════════════════════════════╝

Copyright (C) 2026 Mamadou Bâ Neige

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details (file COPYING, or
<https://www.gnu.org/licenses/>).

Crédits :
  - CLARK SCHEFF (0xD34D) — algorithme de déchiffrement de l'en-tête 2 des fichiers tjc.tft
    et format RLE des images (scripts publiés sous licence GPLv3).
  - MAX ZUIDBERG et le projet UNUF (TFTTool, nxt-doc) — documentation du format TFT
    Nextion/TJC et algorithme de CRC, réimplémenté ici (TFTTool est sous licence MPL 2.0).
  - Encodeur RLE fidèle au compilateur TJC, CRC de la zone ressources et reconstruction
    du fichier : Mamadou Bâ Neige, 2026.

Ce logiciel n'est affilié ni à Creality, ni à TJC (Taojingchi), ni à Nextion.
Ender 3 V3 SE est une marque de Creality. Utilisation à vos propres risques :
conservez toujours le fichier tjc.tft d'origine.
"""
__version__ = "1.0"
__author__ = "Mamadou Bâ Neige"
import os, locale

# ---------------------------------------------------------------- langue / language
LANG = "fr"

def _detect_lang():
    for v in (os.environ.get("LANG", ""), (locale.getlocale()[0] or "")):
        v = v.lower()
        if v.startswith("fr") or v.startswith("french"): return "fr"
        if v: return "en"
    return "fr"

def set_lang(lang):
    global LANG
    LANG = "en" if str(lang).lower().startswith("en") else "fr"

# Contributeurs mis en avant / featured contributors : (nom, pseudonyme ou projet, apport, licence)
CREDITS_LIST = [
    ("Clark Scheff", "0xD34D",
     {"fr": "Déchiffrement de l'en-tête 2 des fichiers tjc.tft et format RLE des images",
      "en": "Decryption of header 2 of tjc.tft files and RLE image format"}, "GPLv3"),
    ("Max Zuidberg", {"fr": "projet UNUF — TFTTool, nxt-doc", "en": "UNUF project — TFTTool, nxt-doc"},
     {"fr": "Documentation du format TFT Nextion/TJC et algorithme de CRC",
      "en": "Documentation of the Nextion/TJC TFT format and CRC algorithm"}, "MPL 2.0"),
]

def L(x):
    """Renvoie la version dans la langue courante d'un texte simple ou bilingue."""
    return x[LANG] if isinstance(x, dict) else x

MSG = {
 "fr": {
  "copyright": "Copyright © 2026 Mamadou Bâ Neige — licence GNU GPL v3 ou ultérieure",
  "disclaimer": "Logiciel non affilié à Creality, TJC ou Nextion. Ender-3 V3 SE est une marque de Creality.\n"
                "Fourni SANS AUCUNE GARANTIE. Conservez toujours le fichier tjc.tft d'origine.",
  "gratitude": "AVEC LA GRATITUDE DE L'AUTEUR ENVERS",
  "license": "licence",
  "not_t1": "Ce fichier n'est pas un .tft TJC de série T1 (format non pris en charge).",
  "crc_h1": "CRC en-tête 1", "crc_h2": "CRC en-tête 2", "crc_res": "CRC ressources",
  "crc_file": "CRC fichier", "size": "Taille fichier",
  "ok": "OK", "error": "ERREUR", "read": "lu", "calc": "calculé",
  "extracted": "{n} images extraites dans {d}",
  "dim_line": "image {i}: {w}x{h} au lieu de {ew}x{eh}",
  "dim_error": "Dimensions incorrectes, rien n'a été écrit :",
  "report": "Bilan des {n} image(s) modifiée(s) (variation de taille, + = plus lourde) :",
  "report_line": "  image {i:4d} ({w}x{h}) : {a:7d} -> {b:7d} octets  ({g:+d})",
  "report_more": "  … et {n} autre(s)", "report_total": "  Total : {t:+d} octets",
  "overflow": "Les images modifiées dépassent l'espace disponible de {o} octets (marge d'origine : {m} octets). "
              "Simplifiez les images (moins de dégradés/bruit) pour qu'elles se compressent mieux.",
  "replaced": "{n} image(s) remplacée(s) : {lst}",
  "margin": "Marge restante dans la zone ressources : {m} octets",
  "written": "Fichier écrit : {p}",
  "consistent": "Fichier cohérent.", "inconsistent": "Fichier INCOHÉRENT.",
 },
 "en": {
  "copyright": "Copyright © 2026 Mamadou Bâ Neige — GNU GPL v3 or later",
  "disclaimer": "Not affiliated with Creality, TJC or Nextion. Ender-3 V3 SE is a trademark of Creality.\n"
                "Provided WITHOUT ANY WARRANTY. Always keep the original tjc.tft file.",
  "gratitude": "WITH THE AUTHOR'S GRATITUDE TO",
  "license": "license",
  "not_t1": "This file is not a TJC T1-series .tft (unsupported format).",
  "crc_h1": "Header 1 CRC", "crc_h2": "Header 2 CRC", "crc_res": "Resources CRC",
  "crc_file": "File CRC", "size": "File size",
  "ok": "OK", "error": "ERROR", "read": "read", "calc": "computed",
  "extracted": "{n} images extracted to {d}",
  "dim_line": "image {i}: {w}x{h} instead of {ew}x{eh}",
  "dim_error": "Wrong dimensions, nothing was written:",
  "report": "Report for {n} modified image(s) (size change, + = heavier):",
  "report_line": "  image {i:4d} ({w}x{h}) : {a:7d} -> {b:7d} bytes  ({g:+d})",
  "report_more": "  … and {n} more", "report_total": "  Total: {t:+d} bytes",
  "overflow": "The modified images exceed the available space by {o} bytes (original margin: {m} bytes). "
              "Simplify the images (fewer gradients/noise) so that they compress better.",
  "replaced": "{n} image(s) replaced: {lst}",
  "margin": "Remaining margin in the resources area: {m} bytes",
  "written": "File written: {p}",
  "consistent": "File is consistent.", "inconsistent": "File is INCONSISTENT.",
 },
}

def tr(key, **kw):
    return MSG[LANG][key].format(**kw)

# Compatibilité / compatibility
COPYRIGHT = MSG["fr"]["copyright"]
DISCLAIMER = MSG["fr"]["disclaimer"]
def credits_text():
    return "\n".join(f"{n} ({L(a)}) — {L(c)} ({l})" for n, a, c, l in CREDITS_LIST)
CREDITS = credits_text()
import os, re, struct, sys
import numpy as np
from PIL import Image
import zlib

# ---------------------------------------------------------------- CRC Nextion/TJC
# CRC-32 (poly 0x04C11DB7, init 0xFFFFFFFF, non réfléchi) où chaque OCTET est
# traité comme un mot de 32 bits (séries T0/K0/T1).
# Calcul via zlib (bibliothèque standard) : un CRC non réfléchi s'obtient à partir du CRC
# réfléchi de zlib en inversant l'ordre des bits des octets en entrée et du résultat.
_BITREV = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))

def _mpeg(b):
    r = zlib.crc32(bytes(b).translate(_BITREV), 0) ^ 0xFFFFFFFF   # registre brut, init 0xFFFFFFFF
    return int(f"{r:032b}"[::-1], 2)

def ncrc(b):
    a = np.zeros(len(b) * 4, dtype=np.uint8)
    a[3::4] = np.frombuffer(bytes(b), dtype=np.uint8)
    return _mpeg(a.tobytes())

# ---------------------------------------------------------------- en-tête 2 (chiffré)
_NONCE = struct.pack("III", 0x92930F5E, 0x924F6584, 0xFBAD3BBF)
_KEY = struct.pack("II", 0x582659B6, 0xBD829C9C)
M = 0xFFFFFFFF

def _keystream(nwords, size=200):
    """Paramètres de chiffrement de chaque mot (indépendants des données)."""
    nb = bytearray(_NONCE); out = []
    for k in range(nwords):
        wi = 4 * k; kb = _KEY[k % len(_KEY)]
        s1, s2, s3 = struct.unpack("III", nb)
        nb[0:4] = struct.pack("I", (s1 << 1) & M); nb[size & 3] = ((kb ^ 0xBC) + nb[size & 3]) & 0xFF
        n1 = struct.unpack("III", nb)[0]
        nb[4:8] = struct.pack("I", (s2 << 2) & M); b = 3 - (kb & 3); nb[4 + b] = ((kb ^ 0x58) + nb[4 + b]) & 0xFF
        n2 = struct.unpack("III", nb)[1]
        nn = ~(((n1 + n2) ^ s3) + wi + 8) & M
        nn2 = (nn + s3) & M
        nb[8:12] = struct.pack("I", (s3 << 3) & M); nb[8 + b] = ((kb ^ 0x7A) + nb[8 + b]) & 0xFF
        r1a = (s2 + s3 + n1) & M; ra = (r1a + s2) & M
        r1b = ((s3 << (kb & 7)) + s1 + s2) & M; rb = (r1b + s1) & M
        out.append((nn2, nn, ra, r1a, rb, r1b))
    return out

_KS = _keystream(50)

def h2_decrypt(raw):
    out = []
    for k, (w,) in enumerate(struct.iter_unpack("<I", raw)):
        a, b, c, d, e, f = _KS[k]
        w = ((w - a) & M) ^ b; w = ((w - c) & M) ^ d; w = ((w - e) & M) ^ f
        out.append(w)
    return out

def h2_encrypt(words):
    out = bytearray()
    for k, w in enumerate(words):
        a, b, c, d, e, f = _KS[k]
        w = ((w ^ f) + e) & M; w = ((w ^ d) + c) & M; w = ((w ^ b) + a) & M
        out += struct.pack("<I", w)
    return bytes(out)

# ---------------------------------------------------------------- images RLE
def rle_decode(chunk, w, h):
    if chunk[0] == 0:
        return bytes(chunk[20:20 + w * h * 2])
    end = struct.unpack_from("<I", chunk, 4)[0]
    out = bytearray(); p = 20
    while p < end:
        counts = struct.unpack_from("<I", chunk, p)[0]; p += 4
        if counts & 0xF == 0xF:                          # 8 pixels bruts
            out += chunk[p:p + 16]; p += 16; continue
        for i in range(8):
            out += chunk[p:p + 2] * ((counts >> (4 * i)) & 0xF); p += 2
    return bytes(out[:w * h * 2])

def _encode_band(px, buf):
    runs = []
    for v in px:
        if runs and runs[-1][0] == v: runs[-1][1] += 1
        else: runs.append([v, 1])
    groups = []; ri = 0; rem = runs[0][1] if runs else 0; cn = []; cc = []
    def flush():
        c = cc + list(struct.unpack("<8H", buf[0]))[len(cc):]
        buf[0] = struct.pack("<8H", *c); w = 0
        for i, x in enumerate(cn): w |= x << (4 * i)
        groups.append((w, buf[0], sum(cn)))
    while ri < len(runs):
        if not cn:
            look = []; rj = ri; r = rem
            while len(look) < 8 and rj < len(runs):
                look.append(r); rj += 1
                if rj < len(runs): r = runs[rj][1]
            if len(look) == 8 and all(x == 1 for x in look):
                buf[0] = struct.pack("<8H", *[runs[ri + k][0] for k in range(8)])
                groups.append((0x1111111F, buf[0], 8))
                ri += 8; rem = runs[ri][1] if ri < len(runs) else 0
                continue
        take = min(rem, 14 if not cn else 15)
        cn.append(take); cc.append(runs[ri][0]); rem -= take
        if rem == 0:
            ri += 1; rem = runs[ri][1] if ri < len(runs) else 0
        if len(cn) == 8:
            flush(); cn = []; cc = []
    if cn: flush()
    return groups

def rle_encode(raw, w, h):
    """Encode comme le compilateur TJC ; image stockée brute si la compression n'est pas rentable."""
    px = struct.unpack("<%dH" % (w * h), raw)
    body = bytearray(); bands = []; buf = [bytes(16)]
    for y in range(0, h, 4):                              # bandes de 4 lignes
        g = _encode_band(px[y * w:min(h, y + 4) * w], buf)
        bands.append((20 + len(body), [x[2] for x in g]))
        for wd, cb, _ in g: body += struct.pack("<I", wd) + cb
    end = 20 + len(body)
    tbl = bytearray(); lists = bytearray(); base = end + 8 * len(bands)
    for off, counts in bands:                             # index des bandes
        tbl += struct.pack("<II", off, base + len(lists)); lists += bytes(counts)
    comp = struct.pack("<II", 4, end) + bytes(12) + body + tbl + lists
    unc = bytes(20) + raw
    return comp if len(comp) < len(unc) else unc

# ---------------------------------------------------------------- conversions couleur
def rgb565_to_img(raw, w, h):
    a = np.frombuffer(raw, dtype="<u2").reshape(h, w).astype(np.uint32)
    r = ((a >> 11) & 31) * 255 // 31; g = ((a >> 5) & 63) * 255 // 63; b = (a & 31) * 255 // 31
    return Image.fromarray(np.dstack([r, g, b]).astype(np.uint8), "RGB")

def img_to_rgb565(img):
    a = np.asarray(img.convert("RGB"), dtype=np.uint32)
    r = (a[..., 0] * 31 + 127) // 255; g = (a[..., 1] * 63 + 127) // 255; b = (a[..., 2] * 31 + 127) // 255
    return ((r << 11) | (g << 5) | b).astype("<u2").tobytes()

# ---------------------------------------------------------------- structure du fichier
RES_START = 0x10000          # début de la zone « ressources » (table des sections)

class TFT:
    def __init__(self, data):
        self.d = bytearray(data)
        if self.d[0x15] != 100:
            raise SystemExit(tr("not_t1"))
        self.h2 = h2_decrypt(bytes(self.d[0xC8:0x18C]))
        self.pic_start = self.h2[8]; self.font_start = self.h2[12]; self.npics = self.h2[15]
        self.res_size = struct.unpack_from("<I", self.d, 0x40)[0]
        self.res_end = RES_START + self.res_size
        self.nsect = struct.unpack_from("<I", self.d, 0x38)[0]
        self.sections = [list(struct.unpack_from("<III", self.d, RES_START + 12 * i)) for i in range(self.nsect)]
        self.pic_sec = next(i for i, s in enumerate(self.sections) if RES_START + s[0] == self.pic_start)
        self.font_sec = next(i for i, s in enumerate(self.sections) if RES_START + s[0] == self.font_start)

    def entries(self):
        return [list(struct.unpack_from("<4BIIHHII", self.d, self.pic_start + 24 * i)) for i in range(self.npics)]

    def chunk(self, e):
        return bytes(self.d[self.pic_start + e[5]:self.pic_start + e[5] + e[8]])

    def check(self):
        d = self.d; ok = True
        tests = [(tr("crc_h1"), struct.unpack_from("<I", d, 0xC4)[0], ncrc(d[:0xC4])),
                 (tr("crc_h2"), struct.unpack_from("<I", d, 0x18C)[0], ncrc(d[0xC8:0x18C])),
                 (tr("crc_res"), struct.unpack_from("<I", d, 0x44)[0], ncrc(d[RES_START:self.res_end])),
                 (tr("crc_file"), struct.unpack_from("<I", d, len(d) - 4)[0],
                  ncrc(d[:-4]) ^ (d[0x03] ^ d[0x2E] ^ d[0x3C])),
                 (tr("size"), struct.unpack_from("<I", d, 0x3C)[0], len(d))]
        for name, stored, calc in tests:
            good = stored == calc; ok &= good
            print(f"  {name:16s}: {tr('ok') if good else tr('error')} "
                  f"({tr('read')} 0x{stored:08x}, {tr('calc')} 0x{calc:08x})")
        return ok

def cmd_extract(tft_path, outdir):
    t = TFT(open(tft_path, "rb").read()); os.makedirs(outdir, exist_ok=True)
    for e in t.entries():
        idx, w, h = e[4], e[6], e[7]
        rgb565_to_img(rle_decode(t.chunk(e), w, h), w, h).save(os.path.join(outdir, f"{idx:04d}_{w}x{h}.png"))
    print(tr("extracted", n=t.npics, d=outdir))

def cmd_pack(tft_path, imgdir, out_path):
    t = TFT(open(tft_path, "rb").read()); d = t.d
    files = {}
    for f in os.listdir(imgdir):
        m = re.match(r"^(\d+)_", f)
        if m and f.lower().endswith(".png"): files[int(m.group(1))] = os.path.join(imgdir, f)
    ents = t.entries(); chunks = []; changed = []; errors = []; growth = []
    for e in ents:
        idx, w, h = e[4], e[6], e[7]; orig = t.chunk(e)
        if idx not in files:
            chunks.append(orig); continue
        img = Image.open(files[idx])
        if img.size != (w, h):
            errors.append(tr("dim_line", i=idx, w=img.size[0], h=img.size[1], ew=w, eh=h)); chunks.append(orig); continue
        raw = img_to_rgb565(img)
        if raw == rle_decode(orig, w, h):
            chunks.append(orig)                           # inchangée : copie à l'identique
        else:
            chunks.append(rle_encode(raw, w, h)); changed.append(idx)
            growth.append((len(chunks[-1]) - len(orig), idx, w, h, len(orig), len(chunks[-1])))
    if errors:
        raise SystemExit(tr("dim_error") + "\n  " + "\n  ".join(errors))

    # nouveau bloc d'images : table + données
    table_size = 24 * len(ents); blob = bytearray(); off = table_size
    for e, c in zip(ents, chunks):
        e[5], e[8] = off, len(c); off += len(c)
    for e in ents: blob += struct.pack("<4BIIHHII", *e)
    for c in chunks: blob += c

    fonts = bytes(d[t.font_start:t.font_start + t.sections[t.font_sec][1]])
    new_font_start = t.pic_start + len(blob)
    used_end = new_font_start + len(fonts)
    old_used_end = t.font_start + len(fonts)
    if growth:
        growth.sort(reverse=True)
        print(tr("report", n=len(growth)))
        for g, idx, w, h, a, b in growth[:15]:
            print(tr("report_line", i=idx, w=w, h=h, a=a, b=b, g=g))
        if len(growth) > 15: print(tr("report_more", n=len(growth) - 15))
        print(tr("report_total", t=sum(x[0] for x in growth)))
    if used_end > t.res_end:
        raise SystemExit(tr("overflow", o=used_end - t.res_end, m=t.res_end - old_used_end))
    region = bytearray(d[RES_START:t.pic_start]) + blob + fonts
    region += bytes(t.res_end - RES_START - len(region))  # remplissage par des zéros
    d[RES_START:t.res_end] = region

    # table des sections
    t.sections[t.pic_sec][1] = len(blob)
    t.sections[t.font_sec][0] = new_font_start - RES_START
    for i, s in enumerate(t.sections): struct.pack_into("<III", d, RES_START + 12 * i, *s)
    # en-tête 2 : adresse des polices, rechiffrement, CRC
    t.h2[12] = new_font_start
    d[0xC8:0x18C] = h2_encrypt(t.h2)
    struct.pack_into("<I", d, 0x18C, ncrc(d[0xC8:0x18C]))
    # en-tête 1 : CRC des ressources puis CRC de l'en-tête
    struct.pack_into("<I", d, 0x44, ncrc(d[RES_START:t.res_end]))
    struct.pack_into("<I", d, 0xC4, ncrc(d[:0xC4]))
    # CRC global du fichier
    struct.pack_into("<I", d, len(d) - 4, ncrc(d[:-4]) ^ (d[0x03] ^ d[0x2E] ^ d[0x3C]))

    open(out_path, "wb").write(d)
    print(tr("replaced", n=len(changed), lst=f"{changed[:20]}{' …' if len(changed) > 20 else ''}"))
    print(tr("margin", m=t.res_end - used_end))
    print(tr("written", p=out_path))
    TFT(bytes(d)).check()

def cmd_check(path):
    print(path); ok = TFT(open(path, "rb").read()).check()
    print(tr("consistent") if ok else tr("inconsistent"))

def cmd_version():
    bar = "═" * 72
    print(f"tjc_tft_tool {__version__}\n{tr('copyright')}\n\n{bar}\n  {tr('gratitude')}\n{bar}")
    for n, a, c, l in CREDITS_LIST:
        print(f"\n  ★ {n.upper()}  ({L(a)})\n    {L(c)}  [{tr('license')} {l}]")
    print(f"\n{bar}\n\n{tr('disclaimer')}")

if __name__ == "__main__":
    a = sys.argv[1:]
    set_lang(_detect_lang())
    if "--lang" in a:
        i = a.index("--lang")
        if i + 1 < len(a): set_lang(a[i + 1]); del a[i:i + 2]
        else: del a[i]
    if len(a) == 3 and a[0] == "extract": cmd_extract(a[1], a[2])
    elif len(a) == 4 and a[0] == "pack": cmd_pack(a[1], a[2], a[3])
    elif len(a) == 2 and a[0] == "check": cmd_check(a[1])
    elif len(a) == 1 and a[0] in ("version", "--version", "credits"): cmd_version()
    else: print(__doc__)
