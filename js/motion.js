/* Motion follows the content. No scroll interception, hidden text or external library. */
'use strict';
(() => {
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
 const reduce=matchMedia('(prefers-reduced-motion: reduce)'),fine=matchMedia('(hover: hover) and (pointer: fine)');
 const owned=new Set();let enabled=false,frame=0,seenRoots=new WeakSet();
 const header=$('.header'),hero=$('.hero');
 const progress=document.createElement('div');progress.className='reading-progress';progress.setAttribute('aria-hidden','true');header?.append(progress);
 const sections=$$('[data-motion-section],.ticker');
 function animate(el,frames,options={}){
  if(!enabled||!el?.animate)return null;
  const a=el.animate(frames,{duration:450,easing:'cubic-bezier(.22,1,.36,1)',...options});owned.add(a);
  const clear=()=>owned.delete(a);a.onfinish=clear;a.oncancel=clear;return a;
 }
 function refresh(){
  const next=!reduce.matches&&!document.hidden&&!document.body.classList.contains('motion-paused')&&!document.body.hasAttribute('data-a11y');
  enabled=next;document.body.dataset.motionState=enabled?'on':'off';
  if(!enabled){for(const a of owned)a.cancel();owned.clear();$$('[data-parallax]').forEach(el=>el.style.removeProperty('--parallax'));$$('.btn').forEach(el=>{el.style.removeProperty('--mx');el.style.removeProperty('--my');});if(hero){const f=$('.hero-photo-frame',hero);f?.style.removeProperty('--tilt-x');f?.style.removeProperty('--tilt-y');}}
  schedule();
 }
 function tick(){
  frame=0;const y=Math.max(0,window.scrollY),extent=Math.max(1,document.documentElement.scrollHeight-innerHeight);
  progress.style.transform=`scaleX(${Math.min(1,y/extent)})`;
  if(!enabled||innerWidth<900)return;
  // Read geometry as a batch, then write only transform-driving properties.
  const jobs=$$('[data-parallax]').map(el=>{const section=el.closest('[data-motion-section]');return {el,r:(section||el.parentElement).getBoundingClientRect(),max:Math.min(24,Number(el.dataset.parallax)||16)};});
  for(const {el,r,max}of jobs){if(r.bottom<0||r.top>innerHeight)continue;const t=Math.max(-1,Math.min(1,(innerHeight/2-r.top-r.height/2)/(innerHeight/2+r.height/2)));el.style.setProperty('--parallax',(t*max).toFixed(2)+'px');}
 }
 function schedule(){if(!frame)frame=requestAnimationFrame(tick);}
 window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule,{passive:true});
 document.addEventListener('visibilitychange',refresh);document.addEventListener('urfu:motion-preference',refresh);reduce.addEventListener('change',refresh);fine.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(document.body,{attributes:true,attributeFilter:['class','data-a11y']});
 refresh();
 const sectionObserver=new IntersectionObserver(entries=>{
  for(const e of entries)e.target.classList.toggle('is-in-view',e.isIntersecting);
 },{rootMargin:'60px 0px',threshold:0});sections.forEach(s=>sectionObserver.observe(s));
 // Entrances are brief position changes. Content is never transparent or withheld.
 const pendingEntrances=new Set();
 const entrance=new IntersectionObserver(entries=>{
  for(const e of entries){if(!e.isIntersecting)continue;entrance.unobserve(e.target);pendingEntrances.delete(e.target);if(enabled){const index=Number(e.target.dataset.motionOrder)||0;animate(e.target,[{transform:'translateY(20px)'},{transform:'translateY(0)'}],{duration:460,delay:Math.min(index%4*45,135)});}}
 },{rootMargin:'0px 0px 12% 0px',threshold:.02});
 function observeContent(root=document){
  const els=$$('.shortcut,.route-step,.section-head h2,.news-card,.help-banner,.page-hero h1,.page-hero .lead',root);
  // The first screen and at most twelve new program cards get movement.
  if(root!==document)els.push(...$$('.program-card,.card,.result',root).slice(0,12));
  els.forEach((el,i)=>{if(seenRoots.has(el))return;seenRoots.add(el);el.dataset.motionOrder=String(i);pendingEntrances.add(el);entrance.observe(el);});
 }
 observeContent();
 let mutationFrame=0;const dynamicRoots=$$('#catalog-list,#program-content,#institute-content,#quiz-results,#search-results');
 const contentObserver=new MutationObserver(()=>{if(mutationFrame)return;mutationFrame=requestAnimationFrame(()=>{mutationFrame=0;for(const el of pendingEntrances){if(!el.isConnected){entrance.unobserve(el);pendingEntrances.delete(el);}}dynamicRoots.forEach(observeContent);schedule();});});
 dynamicRoots.forEach(root=>contentObserver.observe(root,{childList:true}));
 if(enabled&&hero){
  $$('.headline-line',hero).forEach((el,i)=>animate(el,[{transform:'translateY(28px)'},{transform:'translateY(0)'}],{duration:700,delay:i*75}));
  animate($('.hero-photo-frame'),[{transform:'perspective(1000px) translateY(20px) rotate(1deg)'},{transform:'perspective(1000px) translateY(0) rotate(-3deg)'}],{duration:950,delay:50});
 }
 document.addEventListener('urfu:role-change',e=>{
  if(!hero)return;const wash=$('.role-wash',hero);
  if(enabled){
   if(wash){wash.style.backgroundColor=e.detail.previousColor;animate(wash,[{opacity:1},{opacity:0}],{duration:420});}
   $$('.headline-line',hero).forEach((el,i)=>animate(el,[{transform:'translateY(18px)'},{transform:'translateY(0)'}],{duration:480,delay:i*40}));
   $$('#role-shortcuts .shortcut').forEach((el,i)=>animate(el,[{transform:'translateY(10px)'},{transform:'translateY(0)'}],{duration:330,delay:i*25}));
  }
  schedule();
 });
 const score=$('#home-score');let scoreFrame=0;
 score?.addEventListener('input',()=>{if(scoreFrame||!enabled)return;scoreFrame=requestAnimationFrame(()=>{scoreFrame=0;const out=$('#score-value');for(const a of out.getAnimations())a.cancel();animate(out,[{transform:'translateY(-3px)'},{transform:'translateY(0)'}],{duration:180});});});
 // Magnetic response only for a mouse; keyboard focus remains in its real place.
 $$('.hero-actions .btn,.help-actions .btn,.route-section-bottom .btn').forEach(button=>{
  let box=null,pending=0,position={x:0,y:0};
  button.addEventListener('pointerenter',e=>{if(e.pointerType!=='mouse'||!fine.matches||!enabled)return;box=button.getBoundingClientRect();});
  button.addEventListener('pointermove',e=>{if(!box||!fine.matches||!enabled||e.pointerType!=='mouse')return;position={x:(e.clientX-box.left-box.width/2)*.1,y:(e.clientY-box.top-box.height/2)*.13};if(pending)return;pending=requestAnimationFrame(()=>{pending=0;button.style.setProperty('--mx',Math.max(-7,Math.min(7,position.x)).toFixed(2)+'px');button.style.setProperty('--my',Math.max(-5,Math.min(5,position.y)).toFixed(2)+'px');});});
  button.addEventListener('pointerleave',()=>{box=null;if(pending)cancelAnimationFrame(pending);pending=0;button.style.setProperty('--mx','0px');button.style.setProperty('--my','0px');});
  button.addEventListener('focus',()=>{button.style.setProperty('--mx','0px');button.style.setProperty('--my','0px');});
 });
 const visual=$('.hero-visual'),photoFrame=$('.hero-photo-frame');
 if(visual&&photoFrame){let box=null,pending=0,pointer={x:0,y:0};
  visual.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'&&fine.matches&&enabled&&innerWidth>=900)box=visual.getBoundingClientRect();});
  visual.addEventListener('pointermove',e=>{if(!box||!enabled||e.pointerType!=='mouse')return;pointer={x:(e.clientX-box.left)/box.width-.5,y:(e.clientY-box.top)/box.height-.5};if(pending)return;pending=requestAnimationFrame(()=>{pending=0;photoFrame.style.setProperty('--tilt-x',(-pointer.y*5).toFixed(2)+'deg');photoFrame.style.setProperty('--tilt-y',(pointer.x*5).toFixed(2)+'deg');});});
  visual.addEventListener('pointerleave',()=>{box=null;if(pending)cancelAnimationFrame(pending);pending=0;photoFrame.style.setProperty('--tilt-x','0deg');photoFrame.style.setProperty('--tilt-y','0deg');});
 }
 // Decorative loops freeze off-screen through IntersectionObserver and in hidden tabs.
 // A fallback is unnecessary for content visibility: all HTML is fully visible at rest.
 document.body.classList.add('motion-ready');schedule();
})();
