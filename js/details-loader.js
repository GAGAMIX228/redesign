'use strict';
window.detailReady = new Promise(resolve => {
 const id = new URLSearchParams(location.search).get('id');
 if (!window.URFU_DATA?.programs.some(p=>p.id===id)) {resolve();return;}
 const script=document.createElement('script');script.src='data/program-details/'+id+'.js';script.onload=resolve;script.onerror=resolve;document.head.append(script);
});
