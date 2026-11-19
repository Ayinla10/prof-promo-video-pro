# Studying reference videos (TikTok / Reels / YouTube links)

Clients often say "make it like these". Study them **before** proposing concepts — viewing in the browser is enough,
no download needed.

1. Open the link in the built-in browser (`navigate`). Wait ~2.5 s for the player.
2. Inject a frame-grid sampler and draw evenly spaced frames into one canvas overlay:

```js
window.__grab = async function(start, end, n, cols){
  const v=document.querySelector('video'); v.pause(); v.muted=true;
  const W=300, H=Math.round(W*v.videoHeight/v.videoWidth), rows=Math.ceil(n/cols);
  let c=document.getElementById('__grid'); if(c) c.remove(); c=document.createElement('canvas'); c.id='__grid'; document.body.appendChild(c);
  c.width=W*cols; c.height=(H+14)*rows; c.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#000;width:613px';
  const ctx=c.getContext('2d');
  for(let i=0;i<n;i++){ const t=start+(end-start)*i/(n-1);
    await new Promise(r=>{v.onseeked=r; v.currentTime=t;}); await new Promise(r=>setTimeout(r,250));
    const x=(i%cols)*W, y=Math.floor(i/cols)*(H+14); ctx.drawImage(v,x,y+14,W,H);
    ctx.fillStyle='#ff0'; ctx.font='12px sans-serif'; ctx.fillText(t.toFixed(1)+'s',x+4,y+11); }
  return 'ok'; };
const v=document.querySelector('video'); ({d:v.duration,w:v.videoWidth,h:v.videoHeight})
```
3. `await __grab(0, duration, 12, 3)` (landscape) or `(…, 12, 6)` (portrait), wait 3–4 s, then screenshot / zoom.
   Re-sample dense windows (0.25 s apart) around transitions you want to understand.
4. Write down, per reference: ground & palette, the hero (character / object), type treatment, transitions,
   recurring devices (pills, wheels, orbiting cards, inline icons), pace, sound. Then a one-line **lesson** each.
5. Present the analysis as a short table + "the lesson I'm taking", then the concepts that apply it to the client.

Typical findings that work: light canvases with brand-colour glow blobs behind fluted glass; words inside gradient
pills; floating 3D-ish icons/cards orbiting a phone or a word; a selector wheel of features; a cute round character
with eyes that squashes, splats and reacts (it carries the story); big numbers inside circles; marker scribbles;
typed domain as the end card; sound on every move.

Rights: reference videos are for *learning*, never for copying. Do not recreate a specific video's characters,
artwork or sequences; build the client's own versions of the general techniques.
