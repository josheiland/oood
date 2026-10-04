from pathlib import Path
import json,csv
R=Path(__file__).resolve().parent;m=json.loads((R/'edit-manifest-v3.json').read_text());inv=json.loads((R/'source-review/inventory.json').read_text())
def tc(t):
 n=round(t);return f'{n//3600:02}:{n%3600//60:02}:{n%60:02}'
rows=[];stats=[]
for p in inv:
 duration=float(p['format']['duration']);segs=[s for s in m['segments'] if s['source']==p['path']];ranges=sorted((s['in'],s['out']) for s in segs);merged=[]
 for a,b in ranges:
  if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
  else:merged.append([a,b])
 cursor=0
 for a,b in merged:
  if a>cursor:rows.append([p['path'],tc(cursor),tc(a),round(a-cursor,3),'Omitted from this proposal; original retained'])
  cursor=b
 if cursor<duration:rows.append([p['path'],tc(cursor),tc(duration),round(duration-cursor,3),'Omitted from this proposal; original retained'])
 stats.append({'source':p['path'],'source_seconds':duration,'unique_seconds_used':sum(b-a for a,b in merged),'omitted_seconds':duration-sum(b-a for a,b in merged)})
with (R/'omitted-source-ranges-v3.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['source','source_in','source_out','seconds','status']);w.writerows(rows)
(R/'source-retention-v3.json').write_text(json.dumps(stats,indent=2))
text='''EL CRUCE | EDITORIAL REVIEW NOTES | CURRENT CUT V3

PROPOSED DIRECTION
The race supplies real stakes. The lesson is how to direct AI toward a useful result: context, constraints, a proposed plan, concrete feedback, and a stopping point. The episode keeps both hosts' judgment and their different priorities.

WHY ABOUT 23 MINUTES
Just over two hours of camera material becomes 22:58. The opening establishes why the project matters, then the concrete examples build from notes to instructions, gear choices, a flawed calendar and a working shared result. The final reflection turns the experiment into habits viewers can reuse. Cutting much more would either flatten the couple dynamic or remove the failure-to-correction chain.

WHAT WAS REMOVED
Long race-specific research and coaching questions; repeated setup; waiting for tools; production resets; model/news tangents; generic training exposition; and the claim that hosting itself fixes page spacing. The shopping example stays because choosing from your own shortlist is a transferable skill. The calendar mistake stays because it makes the need to check AI obvious.

STRUCTURAL CHANGES
The recorded reflection about specifying essentials is moved after the finished website and phone reaction. The opening intentionally previews a moment repeated in that reflection. The complete recorded signoff is used. No new speech or synthetic reactions were created.

SCREEN RECORDINGS
All three matching Desktop recordings are used. Waveform checks at the beginning, middle and end establish stable source offsets. Cropped demos keep both hosts visible alongside a short teaching takeaway. The first website reveal crop was corrected after frame review.

OPENING RECOMMENDATION
01: clearest promise of an AI lesson; used in the full proposed cut.
02: strongest emphasis on your relationship and differing goals.
03: funniest AI-specific opening.
All ten previews include their own hook, the recurring intro/sting and the same complete opening exchange. Lengths are approximately 32–38 seconds, preserving sentence endings.

TITLE RECOMMENDATION
We Asked ChatGPT to Coach Us. Then We Had to Coach It.
Thumbnail: COACHING OUR COACH
Eight alternatives/pairings are in title-and-thumbnail-options.txt. These are copy proposals, not rendered thumbnails.

PLAYBACK REVIEW STILL NEEDED
This environment reviewed full machine transcripts, selected source frames, synchronization evidence and exported frames. It cannot directly hear the audio. Check joins by ear, the original camera lip sync, dialogue/music balance and the caption wording in continuous host playback. Retained personal experiences and the exact edit also remain for host approval. Technical checks do not constitute host approval or platform acceptance.

REVERSIBILITY
edit-manifest-v3.json and edit-decision-list-v3.csv identify every kept range, source and reason. omitted-source-ranges-v3.csv lists the complementary omitted ranges. Raw source files remain intact. Earlier v1 media and incomplete v2 production files are preserved as internal working history; use v3 for the full episode and hooks-v2 for hook comparisons.
'''
(R/'editorial-review-notes.txt').write_text(text)
print('Omitted ranges',len(rows),'full seconds',m['duration'])
