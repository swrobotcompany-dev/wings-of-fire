/**
 * camera.js — виртуальная камера: базис (forward/right/up), установка (setCam)
 * и проекция точки мира в экранные координаты (proj -> G.camera.p = {x,y,z}).
 * Доступ: window.WOF.camera.{ setCam, proj, p, focal, camX..camUz }
 */
(function(G){
'use strict';
const CV = G.canvas;   // размеры окна

/* ---------- камера ---------- */
let camX = 0, camY = 30, camZ = -19;
let camRx = 1, camRy = 0, camRz = 0, camUx = 0, camUy = 1, camUz = 0, camFx = 0, camFy = 0, camFz = 1;
let focal = 500;
function setCam(px, py, pz, tx, ty, tz, fov){
  camX = px; camY = py; camZ = pz;
  let fx = tx - px, fy = ty - py, fz = tz - pz;
  const fl = Math.hypot(fx, fy, fz) || 1;
  fx /= fl; fy /= fl; fz /= fl;
  camFx = fx; camFy = fy; camFz = fz;
  let rx = -fz, rz = fx;
  const rl = Math.hypot(rx, rz) || 1;
  rx /= rl; rz /= rl;
  camRx = rx; camRy = 0; camRz = rz;
  camUx = -rz * fy; camUy = rz * fx - rx * fz; camUz = rx * fy;
  focal = CV.H2 / Math.tan(fov * Math.PI / 360);
}
const _p = { x:0, y:0, z:0 };
function proj(x, y, z){
  const dx = x - camX, dy = y - camY, dz = z - camZ;
  const vz = dx * camFx + dy * camFy + dz * camFz;
  if(vz < 0.35) return false;
  const vx = dx * camRx + dy * camRy + dz * camRz;
  const vy = dx * camUx + dy * camUy + dz * camUz;
  _p.x = CV.W2 + vx * focal / vz;
  _p.y = CV.H2 - vy * focal / vz;
  _p.z = vz;
  return true;
}


G.camera = {
  setCam, proj, p: _p,
  get focal(){ return focal; },
  get camX(){ return camX; }, get camY(){ return camY; }, get camZ(){ return camZ; },
  get camFx(){ return camFx; }, get camFy(){ return camFy; }, get camFz(){ return camFz; },
  get camRx(){ return camRx; }, get camRy(){ return camRy; }, get camRz(){ return camRz; },
  get camUx(){ return camUx; }, get camUy(){ return camUy; }, get camUz(){ return camUz; },
};
})(window.WOF);
