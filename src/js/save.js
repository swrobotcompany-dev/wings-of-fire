/**
 * save.js — профиль игрока (localStorage), каталог окрасов SKINS, апгрейды UPGRADES,
 * формулы производных характеристик (flameDPS/speedMul/maxHpCalc/ammoMaxCalc/rechargeMax)
 * и перекраска дракона applyDragonColors (пишет в colors.DC).
 * Доступ: window.WOF.save.*
 */
(function(G){
'use strict';

/* ---------- сохранение ---------- */
const SAVE_KEY = 'wof_save_v1';
const save = {
  sparks:0, owned:['obsidian'], skin:'obsidian',
  custom:{ body:'#3a4049', wing:'#4a515c', crest:'#5f6773', horn:'#6a7280', eye:'#ffb703',
           hornsBig:false, spikes:true, blade:false, bigWings:true },
  up:{ flame:0, speed:0, armor:0, ammo:0, wisp:0, magnet:0, totem:0 }
};
try{
  const s = JSON.parse(localStorage.getItem(SAVE_KEY));
  if(s && typeof s === 'object'){
    if(typeof s.sparks === 'number') save.sparks = s.sparks;
    if(Array.isArray(s.owned) && s.owned.length) save.owned = s.owned;
    if(typeof s.skin === 'string') save.skin = s.skin;
    if(s.custom) Object.assign(save.custom, s.custom);
    if(s.up) Object.assign(save.up, s.up);
  }
}catch(e){}
function persist(){ try{ localStorage.setItem(SAVE_KEY, JSON.stringify(save)); }catch(e){} }

const SKINS = [
  {id:'obsidian', name:'Обсидиан', price:0,   body:'#3a4049', wing:'#4a515c', crest:'#5f6773', horn:'#6a7280', eye:'#ffb703'},
  {id:'ash',      name:'Пепельный', price:30, body:'#7d838c', wing:'#8f959e', crest:'#a5abb4', horn:'#c2c7cd', eye:'#ffd166'},
  {id:'crimson',  name:'Багровый', price:60,  body:'#6e2730', wing:'#8a3440', crest:'#a4453f', horn:'#d8c2a8', eye:'#ffd166'},
  {id:'lapis',    name:'Лазурит', price:90,   body:'#2f4f8f', wing:'#3f63b0', crest:'#6fa3d8', horn:'#d0dbe8', eye:'#8fe3ff'},
  {id:'emerald',  name:'Изумруд', price:120,  body:'#2f6b45', wing:'#3f8a5a', crest:'#7fc98a', horn:'#d9e8c8', eye:'#b0ff70'},
  {id:'gold',     name:'Золотой', price:200,  body:'#8a6a1f', wing:'#b08a2a', crest:'#ffd166', horn:'#fff3b0', eye:'#ff9f43'},
  {id:'ghost',    name:'Призрак', price:300,  body:'#c9d4da', wing:'#dde6ea', crest:'#f2f6f8', horn:'#ffffff', eye:'#9fd8ff'},
  {id:'ember',    name:'Уголь и пламя', price:450, body:'#1c1e24', wing:'#2a2d36', crest:'#ff6b35', horn:'#3a3f47', eye:'#ff4d00'}
];
const UPGRADES = [
  {id:'flame', name:'Пламя',   desc:'+5 урона огня за уровень', base:25},
  {id:'speed', name:'Скорость',desc:'+10% скорости за уровень', base:20},
  {id:'armor', name:'Броня',   desc:'+25 макс. здоровья за уровень', base:30},
  {id:'ammo',  name:'Арсенал', desc:'+3 шара и −1с перезарядка за уровень', base:35},
  {id:'wisp',  name:'Спутник', desc:'Огненный дух сам атакует врагов поблизости', base:150, max:1},
  {id:'magnet',name:'Магнит',  desc:'Притягивает искры и еду рядом с драконом', base:80, max:1},
  {id:'totem', name:'Тотем возрождения', desc:'Один раз спасает от смерти (можно несколько)', base:120, max:9}
];
const flameDPS    = () => 10 + save.up.flame * 5;
const speedMul    = () => 1 + save.up.speed * .1;
const maxHpCalc   = () => 100 + save.up.armor * 25;
const ammoMaxCalc = () => 15 + save.up.ammo * 3;
const rechargeMax = () => Math.max(5, 10 - save.up.ammo);

const DC = G.colors.DC;
function currentSkinColors(){
  if(save.skin === 'custom') return save.custom;
  return SKINS.find(s => s.id === save.skin) || SKINS[0];
}
function applyDragonColors(){
  const c = currentSkinColors();
  const b = WOF.helpers.cssToRgb(c.body), w = WOF.helpers.cssToRgb(c.wing);
  DC.body = b;
  DC.dark = [b[0]*.6|0, b[1]*.6|0, b[2]*.6|0];
  DC.light = [Math.min(255,b[0]*1.3)|0, Math.min(255,b[1]*1.3)|0, Math.min(255,b[2]*1.3)|0];
  DC.wing = w;
  DC.wingTip = [w[0]*.6|0, w[1]*.6|0, w[2]*.6|0];
  DC.crest = WOF.helpers.cssToRgb(c.crest);
  DC.horn = WOF.helpers.cssToRgb(c.horn);
  DC.eye = WOF.helpers.cssToRgb(c.eye);
}
applyDragonColors();


G.save = { SAVE_KEY, save, persist, SKINS, UPGRADES,
           flameDPS, speedMul, maxHpCalc, ammoMaxCalc, rechargeMax,
           currentSkinColors, applyDragonColors };
})(window.WOF);
