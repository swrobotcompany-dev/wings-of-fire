#!/usr/bin/env python3
"""Извлечение сегментов исходного HTML в tmp/ для последующей ручной разметки."""
import os

ROOT = '/workspace'
SRC = os.path.join(ROOT, 'Qwen_html_20261010_w6p7ub4fi.html')
lines = open(SRC, encoding='utf-8').read().split('\n')

def seg(a, b):
    return '\n'.join(lines[a-1:b])

os.makedirs(os.path.join(ROOT, 'tmp'), exist_ok=True)

SEGS = {
  'css':          seg(9, 167),
  'body':         seg(171, 296),
  'boot':         seg(299, 307),
  'helpers':      seg(311, 325),
  'canvas':       seg(327, 340),
  'terrain_h':    seg(342, 353),
  'camera':       seg(355, 383),
  'math':         seg(385, 402),
  'emitq':        seg(404, 420),
  'colors':       seg(422, 441),
  'save':         seg(443, 504),
  'state':        seg(506, 536),
  'spawn':        seg(538, 613),
  'structures':   seg(615, 751),
  'particles':    seg(753, 787),
  'audio':        seg(789, 863),
  'ui':           seg(865, 978),
  'input':        seg(980, 1039),
  'combat':       seg(1041, 1268),
  'hud':          seg(1270, 1292),
  'daynight':     seg(1294, 1321),
  'update':       seg(1323, 1861),
  'renderTerrain':seg(1863, 1942),
  'emitters':     seg(1944, 2145),
  'render':       seg(2147, 2351),
  'loop':         seg(2353, 2398),
  'icons':        seg(2400, 2444),
}

for k, v in SEGS.items():
    with open(os.path.join(ROOT, 'tmp', k + '.txt'), 'w', encoding='utf-8') as f:
        f.write(v + '\n')

print('written', len(SEGS), 'segments')
