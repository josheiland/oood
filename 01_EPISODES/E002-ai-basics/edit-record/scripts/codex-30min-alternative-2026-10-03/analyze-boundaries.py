from pathlib import Path
import subprocess,json,wave
H=Path(__file__).resolve().parent
SOURCE=H.parent/'codex-no-popups-2026-10-03/episode-001-no-popups.mp4'
# Provisional boundaries. Final frame choices follow local audio re-transcription.
CUTS=[
('provider-repeat',104.8,140.6,'Repeated provider rankings and early open/closed setup','Provider/company list remains; open/closed is explained later.'),
('app-modes',253.88,312.9,'Detailed work modes, coding products and repeated app mapping','Keep the app/provider distinction; deeper product capabilities are Episode 2 territory.'),
('specialization',665.7,747.4,'Street-racing analogy and Harvey/OpenEvidence specialization','The core engine/app analogy and editable weights remain. Tradeoff: lose these concrete industry examples.'),
('jobs-and-access',1113.3,1288.0,'Extended jobs, learning-to-code and access/inequality tangent','Keep the full math disagreement and the coding-midterm story. Tradeoff: lose Mary’s access/equity argument.'),
('jobs-second-pass',1355.8,1499.05,'Second jobs/tasks pass, doctor/translation examples and overhype','Mary’s human-skills perspective remains immediately after this cut. Tradeoff: less discussion of who may lose work.'),
('market-economics',1601.2,1985.2,'AI business economics, NVIDIA setup, switching, permissions, open-model monetization','Retain open/closed definitions and on-prem/cloud explanation. Tradeoff: lose the longer business-model discussion; a good standalone future topic.'),
('safety-detour',2260.8,2508.23,'Sandbox escape, anthropomorphism, paperclips and balancing fear/optimism','Retain Dario/Anthropic’s safety positioning and commercial-pressure caveat. Tradeoff: lose a substantive safety conversation suited to the agents episode.'),
('openai-structure',2590.0,2650.3,'OpenAI nonprofit/for-profit and Elon funding/legal backstory','Sam’s introduction and personal impressions remain. Tradeoff: fewer details explaining the reputational tension.'),
('elon-business',2704.0,2756.2,'Elon business performance, Twitter/government cuts and respect debate','Keep the polarizing-personality exchange and personal ranking. Tradeoff: lose Josh’s business-case defense and Mary’s response.'),
('deepmind-org',2788.9,2817.1,'DeepMind acquisition/internal-organization clarification','Keep Demis’s role change, Gemini link and both hosts’ direct impressions.'),
('jensen-aside',2851.2,2874.0,'Jensen side question and ranking restart','Keep Mary’s Demis preference and proceed directly to the chosen leaders.'),
('demis-speculation',2885.5,2931.1,'Speculation about why Demis changed roles','Keep the personal impressions and final ranking; shorten the speculation and preserve the rapid-fire joke.')]
(H/'provisional-cuts.json').write_text(json.dumps([dict(id=i,start=a,end=b,title=t,reason=r) for i,a,b,t,r in CUTS],indent=2)+'\n')
parts=[];pcm=bytearray();offset=0
for i,a,b,t,r in CUTS:
 for edge,sec in [('outgoing',a),('incoming',b)]:
  start=max(0,sec-7);duration=14
  raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-ss',f'{start:.6f}','-threads','2','-i',str(SOURCE),'-t',str(duration),'-vn','-ac','1','-ar','16000','-f','s16le','-'])
  pcm+=raw;parts.append({'id':i,'edge':edge,'source_start':start,'montage_start':offset/16000,'duration':len(raw)/32000});offset+=len(raw)//2
  pcm+=b'\0'*(16000*2);offset+=16000
(H/'boundary-montage-map.json').write_text(json.dumps(parts,indent=2)+'\n')
with wave.open(str(H/'boundary-source.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000);f.writeframes(pcm)
print('Re-transcribing 24 boundary neighborhoods locally.',flush=True)
cmd=['whisper-cli','-m','/Users/je/.cache/whisper-cpp/ggml-small.en.bin','-f',str(H/'boundary-source.wav'),'-ng','-t','4','-dtw','small.en','-ojf','-of',str(H/'boundary-word-check')]
with (H/'boundary-asr.log').open('x') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
print('Local boundary word check complete.',flush=True)
