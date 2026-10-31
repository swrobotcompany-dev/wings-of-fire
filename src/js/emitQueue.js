/**
 * emitQueue.js — очередь рендера кадра: список боксов RBOX и теней SHAD.
 * Эмиттеры (emitters.js/render.js) наполняют их, render сортирует и рисует.
 * Доступ: window.WOF.emitQueue.{ RBOX, SHAD, emitBox, emitParts, shadow }
 */
(function(G){
'use strict';
const M3 = G.math3d;    // матрицы поворотов
const CAM = G.camera;   // позиция камеры для отсечения по дальности

/* ---------- очередь рендера ---------- */
const RBOX = [], SHAD = [];
function emitBox(cx, cy, cz, ex, ey, ez, col, m, glow){
  const dx = cx - CAM.camX, dy = cy - CAM.camY, dz = cz - CAM.camZ;
  const d2 = dx*dx + dy*dy + dz*dz;
  if(d2 > 46000) return;
  RBOX.push({ cx, cy, cz, ex, ey, ez, col, m: m || null, glow: !!glow, d2 });
}
function emitParts(px, py, pz, yaw, parts){
  const m = M3.mRotY(yaw);
  for(let i = 0; i < parts.length; i++){
    const p = parts[i];
    M3.mApply(m, p[0], p[1], p[2]);
    emitBox(px + M3.tc[0], py + M3.tc[1], pz + M3.tc[2], p[3], p[4], p[5], p[6], m, p[7]);
  }
}
function shadow(x, z, r, h){ SHAD.push({ x, z, r, h }); }


G.emitQueue = { RBOX, SHAD, emitBox, emitParts, shadow };
})(window.WOF);
