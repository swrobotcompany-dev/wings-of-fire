/**
 * terrain.js — рельеф мира: value-noise и функция высоты земли groundH(x, z).
 * WL — уровень воды.
 * Доступ: window.WOF.terrain.{ vnoise, groundH, WL }
 */
(function(G){
'use strict';

/* ---------- рельеф: карта высот ---------- */
function vnoise(x, z){
  const xi = Math.floor(x), zi = Math.floor(z);
  const xf = x - xi, zf = z - zi;
  const u = xf*xf*(3-2*xf), v = zf*zf*(3-2*zf);
  const a = WOF.helpers.hash2(xi, zi), b = WOF.helpers.hash2(xi+1, zi), c = WOF.helpers.hash2(xi, zi+1), d2 = WOF.helpers.hash2(xi+1, zi+1);
  return a + (b-a)*u + (c-a)*v + (a-b-c+d2)*u*v;
}
function groundH(x, z){
  return vnoise(x/30, z/30)*7 + vnoise(x/11+100, z/11+100)*2.2 - 2.6;
}
const WL = -0.9; // уровень воды


G.terrain = { vnoise, groundH, WL };
})(window.WOF);
