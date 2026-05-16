/* AsrNaam — Shared search-matcher module.
   Exposes window.ASR_MATCHER = { lev, score }.
   Single source of truth for Levenshtein + tier-scoring used by both:
   - asr-search.js  (per-page /names/ search dropdown)
   - asr-enhance.js (global Cmd-K overlay + homepage live suggestions)

   Score buckets (lower is better, 999 = no match):
     -1  exact match
      0  exact-prefix
      1  substring
      2  partial-word (>=3-char head shared either direction)
    3+d  prefix-Levenshtein <=3
    7+d  whole-token Levenshtein <=2
*/
(function(){
  function lev(a, b, maxDist){
    if(a===b) return 0;
    var la=a.length, lb=b.length;
    if(Math.abs(la-lb)>maxDist) return maxDist+1;
    var prev=new Array(lb+1), cur=new Array(lb+1);
    for(var j=0;j<=lb;j++) prev[j]=j;
    for(var i=1;i<=la;i++){
      cur[0]=i;
      var rowMin=cur[0];
      var ca=a.charCodeAt(i-1);
      for(var j2=1;j2<=lb;j2++){
        var cost=(ca===b.charCodeAt(j2-1))?0:1;
        var v=Math.min(prev[j2]+1, cur[j2-1]+1, prev[j2-1]+cost);
        cur[j2]=v;
        if(v<rowMin) rowMin=v;
      }
      if(rowMin>maxDist) return maxDist+1;
      var tmp=prev; prev=cur; cur=tmp;
    }
    return prev[lb];
  }

  function score(token, q){
    if(token===q) return -1;
    if(token.indexOf(q)===0) return 0;
    if(token.indexOf(q)>=0) return 1;
    if(q.length>=3 && token.length>=3){
      for(var pl = Math.min(q.length, 6); pl>=3; pl--){
        if(token.indexOf(q.slice(0, pl))>=0){ return 2; }
      }
      for(var pl2 = Math.min(token.length, 6); pl2>=3; pl2--){
        if(q.indexOf(token.slice(0, pl2))>=0){ return 2; }
      }
    }
    if(q.length>=3){
      var headLen = Math.min(token.length, q.length + 2);
      var head = token.slice(0, headLen);
      var dp = lev(head, q, 3);
      if(dp<=3) return 3 + dp;
    }
    var d = lev(token, q, 2);
    if(d<=2) return 7 + d;
    return 999;
  }

  window.ASR_MATCHER = { lev: lev, score: score };
})();
