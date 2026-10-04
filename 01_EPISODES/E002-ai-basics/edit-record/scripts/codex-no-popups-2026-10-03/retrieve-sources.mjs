import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";
const root=process.cwd();
const work=path.join(root,"01_EPISODES/E001-ai-basics/edit/codex-no-popups-2026-10-03");
const items=[
 ["1fycZY0Em45E8XyCIYdAwifX-cq6P0wEj",path.join(work,"inputs/episode-001-published.mp4"),"181624da06b3255f393fb3dbbe36bfe9f154e9c83fef32fcb5a9ebb6aeb3e87d"],
 ["1z1Zdo2TLCzsOCx2oRYdi83cI9YeGGhE_",path.join(work,"inputs/episode-001-original-raw.mp4"),"9f58d3a39c91ce4499fd3215355ddc9873051e6e32a5b26a6c73ce05caf93107"],
 ["17AmIjcA2hbtamuGWVJSkVYIUGOrLiskU",path.join(root,"01_EPISODES/E002-make-ai-useful/edit/codex-no-popups-audit-2026-10-03/episode-002-published.mp4"),"2d0de694425b1e13523a6a52a4895a1accb994d7b763434f7838b7c53753e858"]
];
function findUrl(v){
 if(v&&typeof v==="object"){
  if(v.s3url)return v.s3url;
  for(const child of Object.values(v)){const found=findUrl(child);if(found)return found;}
 }
}
await Promise.all(items.map(async([id,target,expected])=>{
 if(fs.existsSync(target))throw new Error("Preserving existing file: "+target);
 const result=await execute("GOOGLEDRIVE_DOWNLOAD_FILE",{fileId:id});
 const url=findUrl(result);
 if(!url)throw new Error("No download URL; response keys: "+Object.keys(result));
 const response=await fetch(url);
 if(!response.ok)throw new Error("Download HTTP "+response.status);
 fs.mkdirSync(path.dirname(target),{recursive:true});
 await pipeline(Readable.fromWeb(response.body),fs.createWriteStream(target,{flags:"wx"}));
 const hash=crypto.createHash("sha256");
 for await(const chunk of fs.createReadStream(target))hash.update(chunk);
 const actual=hash.digest("hex");
 if(actual!==expected)throw new Error("Checksum mismatch for "+id);
 console.log(JSON.stringify({path:target,bytes:fs.statSync(target).size,sha256Verified:true}));
}));
