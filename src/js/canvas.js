/**
 * canvas.js — холст игры: создание <canvas id="game">, контекст, размеры окна.
 * Доступ: window.WOF.canvas.{ el, ctx, W, H, W2, H2, DPR, resize }
 */
(function(G){
'use strict';

const el = document.createElement('canvas');
el.id = 'game';
document.body.prepend(el);
const ctx = el.getContext('2d');
let W = 0, H = 0, W2 = 0, H2 = 0, DPR = 1;

function resize(){
  DPR = Math.min(window.devicePixelRatio || 1, 1.5);
  W = innerWidth; H = innerHeight; W2 = W / 2; H2 = H / 2;
  el.width = W * DPR; el.height = H * DPR;
  el.style.width = W + 'px'; el.style.height = H + 'px';
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
addEventListener('resize', resize);
resize();

G.canvas = { el, ctx, get W(){return W;}, get H(){return H;},
             get W2(){return W2;}, get H2(){return H2;}, get DPR(){return DPR;}, resize };
})(window.WOF);
