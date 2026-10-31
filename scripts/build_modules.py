#!/usr/bin/env python3
"""
Сборка модулей src/js/*.js из сегментов tmp/*.txt.
Читает сегменты, вырезает объявления верхнего уровня и оформляет их как
подмодули единого namespace WOF (объект G).
"""
import os, re

ROOT = '/workspace'
TMP = os.path.join(ROOT, 'tmp')
OUT = os.path.join(ROOT, 'src', 'js')
os.makedirs(OUT, exist_ok=True)


def read(name):
    with open(os.path.join(TMP, name + '.txt'), encoding='utf-8') as f:
        return f.read()


def find_decl(text, start):
    """Возвращает (kind, name, decl_end, body_end) для объявления, начинающегося в start."""
    m = re.match(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*', text[start:])
    if m:
        name = m.group(1)
        i = start + m.end()
        depth = 0
        in_str = None
        prev = ''
        while i < len(text):
            c = text[i]
            if in_str:
                if c == '\\':
                    i += 2
                    continue
                if c == in_str and prev != '\\':
                    in_str = None
            else:
                if c in '\'"':
                    in_str = c
                elif c in '([{':
                    depth += 1
                elif c in ')]}':
                    depth -= 1
                elif c == '/' and i + 1 < len(text) and text[i+1] == '/':
                    j = text.find('\n', i)
                    i = j - 1 if j != -1 else len(text)
                elif c == '/' and i + 1 < len(text) and text[i+1] == '*':
                    j = text.find('*/', i)
                    i = (j + 1) if j != -1 else len(text)
                elif depth == 0 and c == ';':
                    return ('value', name, i + 1)
                elif depth == 0 and c == '\n':
                    nxt = text[i+1:i+80].lstrip()
                    if not nxt or nxt[0] in '+-*/?.,;:)]}=' or nxt.startswith('//'):
                        i += 1
                        continue
                    return ('value', name, i)
            prev = c
            i += 1
        return ('value', name, len(text))
    m = re.match(r'function\s+([A-Za-z_$][\w$]*)', text[start:])
    if m:
        name = m.group(1)
        i = text.index('{', start)
        depth = 0
        j = i
        while j < len(text):
            c = text[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return ('func', name, j + 1)
            j += 1
    raise ValueError('not a declaration at offset %d: %r' % (start, text[start:start+60]))


def extract(text, names):
    """Вырезает объявления `names` из текста. Возвращает (found{имя:код}, rest)."""
    found = {}
    spans = []
    for name in names:
        m = re.search(r'^\s*(?:const|let|var|function)\s+' + re.escape(name) + r'\b',
                      text, re.M)
        assert m, 'declaration not found: ' + name
        line_start = text.rfind('\n', 0, m.start()) + 1
        # захватываем предшествующий однострочный комментарий /* ---------- ... */
        prev_line_end = line_start
        kind, nm, end = find_decl(text, m.start())
        assert nm == name
        # не тянем за собой trailing-комментарии вида "/* ---------- след. секция */"
        tail = text[end:]
        cm = re.match(r'\s*/\*\s*-+\s*[^*]*\*/', tail)
        if cm and '----------' in cm.group(0):
            pass  # комментарий относится к следующей секции — не включаем
        spans.append((line_start, end))
        found[name] = text[line_start:end].rstrip()
    spans.sort(reverse=True)
    lines = list(text.split('\n'))
    for a, b in spans:
        la = text.count('\n', 0, a)
        lb = text.count('\n', 0, b - 1)  # последняя строка блока
        del lines[la:lb + 1]
    rest = '\n'.join(lines)
    rest = re.sub(r'\n{3,}', '\n\n', rest).strip('\n')
    return found, rest


def write_file(name, content):
    """Запись модуля с нормализацией отступов/пустых строк."""
    content = content.strip('\n') + '\n'
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(content)


def rewrite_refs(code, mapping):
    for old, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        code = re.sub(r'(?<![\w$.])' + re.escape(old) + r'(?![\w$])', new, code)
    return code


def module(title, exports_code, extra='', footer=''):
    parts = [
        '/**\n * %s\n */\n' % title,
        '(function(){\n',
        exports_code.rstrip() + '\n',
    ]
    if extra.strip():
        parts.append('\n' + extra.strip() + '\n')
    if footer.strip():
        parts.append('\n' + footer.strip() + '\n')
    parts.append('})();\n')
    return ''.join(parts)


# ===========================================================================
# helpers.js — $, rnd, hash2, clamp, h2r, cssToRgb → WOF.helpers
# ===========================================================================
write_file('helpers.js', r"""
/**
 * helpers.js — мелкие утилиты: доступ к DOM ($), случайные числа (rnd),
 * хеш-шум (hash2), clamp, конвертеры цветов (h2r, cssToRgb).
 * Доступ: window.WOF.helpers.*
 */
(function(WOF){
'use strict';

const $ = id => document.getElementById(id);
const rnd = Math.random;
function hash2(x, y){
  let h = Math.imul(x, 374761393) + Math.imul(y, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const h2r = hex => [hex >> 16 & 255, hex >> 8 & 255, hex & 255];
const cssToRgb = str => {
  const n = parseInt(str.slice(1), 16);
  return [n >> 16 & 255, n >> 8 & 255, n & 255];
};

WOF.helpers = { $, rnd, hash2, clamp, h2r, cssToRgb };
})(window.WOF);
""")
H = {k: 'WOF.helpers.%s' % k for k in ['$', 'rnd', 'hash2', 'clamp', 'h2r', 'cssToRgb']}

# ===========================================================================
# canvas.js — cvs, ctx, W/H/W2/H2/DPR, resize() → WOF.canvas
# ===========================================================================
open(os.path.join(OUT, 'canvas.js'), 'w').write('''/**
 * canvas.js — холст игры: создание <canvas id="game">, контекст, размеры окна.
 * Доступ: window.WOF.canvas.{ el, ctx, W, H, W2, H2, DPR, resize }
 */
(function(G){
'use strict';
const canvasEl = document.createElement('canvas');
canvasEl.id = 'game';
document.body.prepend(canvasEl);
const ctx = canvasEl.getContext('2d');
let W = 0, H = 0, W2 = 0, H2 = 0, DPR = 1;
function resize(){
  DPR = Math.min(window.devicePixelRatio || 1, 1.5);
  W = innerWidth; H = innerHeight; W2 = W / 2; H2 = H / 2;
  canvasEl.width = W * DPR; canvasEl.height = H * DPR;
  canvasEl.style.width = W + 'px'; canvasEl.style.height = H + 'px';
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
addEventListener('resize', resize);
resize();

G.canvas = { el: canvasEl, ctx, get W(){return W;}, get H(){return H;},
             get W2(){return W2;}, get H2(){return H2;}, get DPR(){return DPR;}, resize };
})(window.WOF);
''')

# ===========================================================================
# terrain.js — vnoise, groundH, WL (+ ссылка на helpers.hash2)
# ===========================================================================
seg = read('terrain_h')
seg = rewrite_refs(seg, H)
open(os.path.join(OUT, 'terrain.js'), 'w').write('''/**
 * terrain.js — рельеф: шум и функция высоты земли groundH(x, z), уровень воды WL.
 * Доступ: window.WOF.terrain.{ vnoise, groundH, WL }
 */
(function(G){
'use strict';
''' + seg + '''

G.terrain = { vnoise, groundH, WL };
})(window.WOF);
''')

# ===========================================================================
# camera.js — cam*, focal, setCam, _p, proj
# ===========================================================================
seg = read('camera')
seg = rewrite_refs(seg, {'W2': 'CV.W2', 'H2': 'CV.H2'})
seg = seg.replace('_p.x = CV.W2()', '_p.x = CV.W2()')
open(os.path.join(OUT, 'camera.js'), 'w').write('''/**
 * camera.js — виртуальная камера: базис, проекция точек мира на экран (proj).
 * Доступ: window.WOF.camera.{ setCam, proj, p, focal, ... }
 */
(function(G){
'use strict';
const CV = G.canvas;   // размеры окна
''' + seg + '''

G.camera = {
  setCam, proj, p: _p,
  get focal(){ return focal; },
  get camX(){ return camX; }, get camY(){ return camY; }, get camZ(){ return camZ; },
  get camFx(){ return camFx; }, get camFy(){ return camFy; }, get camFz(){ return camFz; },
  get camRx(){ return camRx; }, get camRy(){ return camRy; }, get camRz(){ return camRz; },
  get camUx(){ return camUx; }, get camUy(){ return camUy; }, get camUz(){ return camUz; },
};
})(window.WOF);
''')

# ===========================================================================
# math3d.js — mRotY/mRotX/mRotZ/mMul/_tc/mApply
# ===========================================================================
seg = read('math')
open(os.path.join(OUT, 'math3d.js'), 'w').write('''/**
 * math3d.js — матрицы поворота (row-major 3x3) и применение к точкам.
 * Внимание: mApply возвращает ОБЩИЙ массив _tc (переиспользуется без аллокаций).
 * Доступ: window.WOF.math3d.*
 */
(function(G){
'use strict';
''' + seg + '''

G.math3d = { mRotX, mRotY, mRotZ, mMul, mApply, tc: _tc };
})(window.WOF);
''')

# ===========================================================================
# emitQueue.js — RBOX, SHAD, emitBox, emitParts, shadow
# ===========================================================================
seg = read('emitq')
seg = rewrite_refs(seg, {'mRotY': 'M3.mRotY', 'mApply': 'M3.mApply', '_tc': 'M3.tc',
                         'camX': 'CAM.camX', 'camY': 'CAM.camY', 'camZ': 'CAM.camZ'})
seg = seg.replace('const dx = cx - CAM.camX', 'const dx = cx - CAM.camX')
open(os.path.join(OUT, 'emitQueue.js'), 'w').write('''/**
 * emitQueue.js — очередь рендера: боксы (RBOX) и тени (SHAD), собираемые эмиттерами.
 * Доступ: window.WOF.emitQueue.{ RBOX, SHAD, emitBox, emitParts, shadow }
 */
(function(G){
'use strict';
const M3 = G.math3d;   // матрицы
const CAM = G.camera;  // позиция камеры (для дальности отсечения)
''' + seg + '''

G.emitQueue = { RBOX, SHAD, emitBox, emitParts, shadow };
})(window.WOF);
''')

# ===========================================================================
# colors.js — C, DC
# ===========================================================================
seg = read('colors')
seg = rewrite_refs(seg, {'h2r': 'WOF.helpers.h2r'})
open(os.path.join(OUT, 'colors.js'), 'w').write('''/**
 * colors.js — палитра мира C (RGB-массивы) и текущие цвета дракона DC
 * (пересчитываются save.applyDragonColors при смене окраса).
 * Доступ: window.WOF.colors.{ C, DC }
 */
(function(G){
'use strict';
''' + seg + '''

G.colors = { C, DC };
})(window.WOF);
''')

# ===========================================================================
# save.js — SAVE_KEY, save, persist, SKINS, UPGRADES, формулы, currentSkinColors, applyDragonColors
# ===========================================================================
seg = read('save')
seg = rewrite_refs(seg, H)
seg = seg.replace('const DC = {', 'G.colors.DC.length = 0;\nconst _DC = G.colors.DC;')  # не используется
# applyDragonColors пишет в общий массив цветов из colors.js
seg = seg.replace('function currentSkinColors(){', 'const DC = G.colors.DC;\nfunction currentSkinColors(){')
open(os.path.join(OUT, 'save.js'), 'w').write('''/**
 * save.js — профиль игрока: localStorage-сохранение, окрасы (SKINS), прокачка (UPGRADES),
 * производные параметры (flameDPS, speedMul, maxHpCalc, ammoMaxCalc, rechargeMax)
 * и перекраска дракона (applyDragonColors).
 * Доступ: window.WOF.save.*
 */
(function(G){
'use strict';
''' + seg + '''

G.save = { SAVE_KEY, save, persist, SKINS, UPGRADES,
           flameDPS, speedMul, maxHpCalc, ammoMaxCalc, rechargeMax,
           currentSkinColors, applyDragonColors };
// применяем сохранённую окраску сразу (colors.js уже загружен)
applyDragonColors();
})(window.WOF);
''')

# ===========================================================================
# state.js — всё игровое состояние + списки сущностей
# ===========================================================================
seg = read('state')
seg = rewrite_refs(seg, dict(H, **{'maxHpCalc': 'SV.maxHpCalc', 'ammoMaxCalc': 'SV.ammoMaxCalc'}))
seg = seg.replace('let keys = {};', 'const keys = {};   // сбрасывается через clearKeys(), а не переприсваиванием')
open(os.path.join(OUT, 'state.js'), 'w').write('''/**
 * state.js — изменяемое игровое состояние: время, флаги, дракон d, боевые таймеры,
 * камера-орбиты, а также пулы сущностей (embers/humans/animals/crows/fireballs/...).
 * Доступ: window.WOF.state.*
 */
(function(G){
'use strict';
const SV = G.save;   // апгрейды влияют на стартовые значения hp/ammo
''' + seg + '''

G.state = {
  t,
  started,
  paused,
  burning,
  sparks,
  d, keys,
  hp,
  invulnT,
  damageFlash,
  healFlash,
  relAlt,
  dead,
  deathT,
  deadShown,
  ammo,
  rechargeT,
  fbCd,
  denyT,
  hbT,
  stamina,
  boostHeld,
  novaCd,
  rollT,
  rollCd,
  rollDir,
  ROLL_DUR, ROLL_CD,
  wispA,
  wispCd,
  combo,
  comboT,
  comboHideT,
  nf,
  phaseLabel,
  stormTimer,
  stormWarned,
  stormActive,
  stormT,
  meteorSpT,
  camYaw,
  camPitch,
  camDragging,
  CAM_DIST, CAM_SENS, CAM_PITCH_MIN, CAM_PITCH_MAX,
  eOrb,
  fovCur,
  animalKills,
  humanKills,
  shake,
  emberTimer,
  crackleT,
  flashI,
  shopOpen,
  editorOpen,
  uiOpen,
  embers, humans, animals, drops, crows, spears, boulders, meteors, islands, rings,
  fireballs, campfires,
  golem,
};
})(window.WOF);
''')

print('part 1 done')
