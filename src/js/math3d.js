/**
 * math3d.js — матрицы поворота row-major 3x3 (mRotX/Y/Z, mMul) и трансформация
 * локальной точки в мировую (mApply). ВАЖНО: mApply возвращает общий переиспользуемый
 * массив tc без аллокаций — не сохраняйте ссылку между вызовами!
 * Доступ: window.WOF.math3d.*
 */
(function(G){
'use strict';

/* ---------- матрицы ---------- */
function mRotY(a){ const c = Math.cos(a), s = Math.sin(a); return [c,0,s, 0,1,0, -s,0,c]; }
function mRotX(a){ const c = Math.cos(a), s = Math.sin(a); return [1,0,0, 0,c,-s, 0,s,c]; }
function mRotZ(a){ const c = Math.cos(a), s = Math.sin(a); return [c,-s,0, s,c,0, 0,0,1]; }
function mMul(a, b){
  return [
    a[0]*b[0]+a[1]*b[3]+a[2]*b[6], a[0]*b[1]+a[1]*b[4]+a[2]*b[7], a[0]*b[2]+a[1]*b[5]+a[2]*b[8],
    a[3]*b[0]+a[4]*b[3]+a[5]*b[6], a[3]*b[1]+a[4]*b[4]+a[5]*b[7], a[3]*b[2]+a[4]*b[5]+a[5]*b[8],
    a[6]*b[0]+a[7]*b[3]+a[8]*b[6], a[6]*b[1]+a[7]*b[4]+a[8]*b[7], a[6]*b[2]+a[7]*b[5]+a[8]*b[8]
  ];
}
const _tc = [0,0,0];
function mApply(m, x, y, z){
  _tc[0] = m[0]*x + m[1]*y + m[2]*z;
  _tc[1] = m[3]*x + m[4]*y + m[5]*z;
  _tc[2] = m[6]*x + m[7]*y + m[8]*z;
  return _tc;
}


G.math3d = { mRotX, mRotY, mRotZ, mMul, mApply, tc: _tc };
})(window.WOF);
