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
