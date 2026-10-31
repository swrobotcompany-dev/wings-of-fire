/**
 * colors.js — палитра мира C (RGB-массивы для структур/животных/предметов)
 * и DC — текущие цвета дракона (их перезаписывает save.applyDragonColors).
 * Доступ: window.WOF.colors.{ C, DC }
 */
(function(G){
'use strict';

/* ---------- цвета мира ---------- */
const C = {
  stone:WOF.helpers.h2r(0x8a8f98), stoneD:WOF.helpers.h2r(0x6f7580), wood:WOF.helpers.h2r(0x6b4a2f), tip:WOF.helpers.h2r(0xcfd4da),
  leaf:WOF.helpers.h2r(0x5d9e5f), leafD:WOF.helpers.h2r(0x4d8a50), roof:WOF.helpers.h2r(0x9c4a3a),
  crystal:WOF.helpers.h2r(0x9ff0e4), straw:WOF.helpers.h2r(0xc9a15a), dark:WOF.helpers.h2r(0x2b3038),
  skin:WOF.helpers.h2r(0xd9a066), hair:WOF.helpers.h2r(0x3b2a1a),
  tunics:[WOF.helpers.h2r(0x7a5c3e), WOF.helpers.h2r(0x4a6b8a), WOF.helpers.h2r(0x5d7a4a)],
  tThrower:WOF.helpers.h2r(0x55606e), tChief:WOF.helpers.h2r(0x7a2e2e),
  wool:WOF.helpers.h2r(0xece8de), woolL:WOF.helpers.h2r(0xf7f4ec), sheepHead:WOF.helpers.h2r(0x4c4c55),
  cow:WOF.helpers.h2r(0x8a5a3c), patch:WOF.helpers.h2r(0xf0ece2), muzzle:WOF.helpers.h2r(0xd9c2a8), hornC:WOF.helpers.h2r(0xe6e0d2),
  chick:WOF.helpers.h2r(0xf2efe6), comb:WOF.helpers.h2r(0xe23b4e), beak:WOF.helpers.h2r(0xf4a23c), wingC:WOF.helpers.h2r(0xded9cc),
  legD:WOF.helpers.h2r(0x3a3a40), legC:WOF.helpers.h2r(0x4a3226),
  ember:WOF.helpers.h2r(0xffb703), emberGold:WOF.helpers.h2r(0xffd166), fireball:WOF.helpers.h2r(0xffd166),
  cloud:WOF.helpers.h2r(0xe2e6eb), crow:WOF.helpers.h2r(0x1a1c22), crowEye:WOF.helpers.h2r(0xff3b3b),
  grassTop:WOF.helpers.h2r(0xb7d7de), golemCore:WOF.helpers.h2r(0xffb703), meteor:WOF.helpers.h2r(0x8a4a2a),
  meatC:WOF.helpers.h2r(0xc98a4b), meatS:WOF.helpers.h2r(0xc94f4f), meatB:WOF.helpers.h2r(0xa03e3e), bone:WOF.helpers.h2r(0xf2efe6),
  wisp:WOF.helpers.h2r(0xffe08a), chest:WOF.helpers.h2r(0x8a6a3a), chestBand:WOF.helpers.h2r(0xd8b23c), pupil:WOF.helpers.h2r(0x14161a)
};
const DC = { body:[58,64,73], dark:[36,40,47], light:[76,83,94], wing:[74,81,92],
  wingTip:[48,53,61], crest:[95,103,115], horn:[106,114,128], eye:[255,183,3] };


G.colors = { C, DC };
})(window.WOF);
