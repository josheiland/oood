from pathlib import Path
import json,csv
R=Path(__file__).resolve().parent
SRC='/Users/je/Movies/Agents episode.mp4'; repo=Path('/Users/je/oood')
# Reviewed selections in source seconds; frame-aligned below. No original is changed.
choices=[
(64.0,85.8,'Opening','Clean topic introduction; omit the abandoned opening and episode-number discussion.'),
(145.08,198.20,'Eggs: goal and approval','Use the generic shopping example without the inaccurate Fowler retelling; retain practical credit-card approval boundary.'),
(123.133333,139.766667,None,'Retain the hosts\' differing reactions to an egg purchase as a hypothetical personal exchange. Move immediately after the hypothetical shopping setup; no factual third-party claim is reconstructed.'),
(641.90,764.20,'The parts and the loop','Use the clearest components retake; preserve the love-of-your-life aside, action loop, stop criteria and quantity dilemma.'),
(794.0,834.833333,None,'Keep the common-sense versus missing-context dilemma; remove the uncertain jagged-frontier attribution.'),
(886.033333,973.366667,'Workflow or agent?','Retain the egg comparison of predefined steps versus model-selected methods; the following exchange qualifies the initial simple definitions.'),
(986.333333,1065.6,None,'Mary\'s concrete meeting-summary, follow-up and confidentiality example.'),
(1066.6,1140.033333,None,'Retain the important spectrum correction: research can already be agentic; do not equate chat interface with inability to act.'),
(1162.733333,1182.233333,'Scope and reliability','Keep the aspiration versus current personal experience; omit unsupported Gartner/Duplex claims and speculative numerical reliability rates.'),
(1198.566667,1227.866667,None,'Keep the cute-little-agents joke and the focused-task point.'),
(1237.266667,1327.033333,'Big Egg and subagents','Keep Mary\'s multi-request/ADHD comparison, manager/planner/researcher roles and Big Egg joke; omit repeated lead-in.'),
(1350.5,1409.866667,None,'Keep the corrective explanation of isolated context and sequential dependencies, police egg and coordination tradeoffs. Remove the incorrect claim that sequential workers cannot be subagents.'),
(1434.066667,1493.0,None,"Keep coordination cost and Josh's preference for one personal agent before adding complexity."),
(1504.866667,1521.0,None,'Preserve the 400 coworkers joke and the prioritization concern as host opinion.'),
(1549.233333,1628.566667,None,'Keep the real ultramarathon brain-dump example and practical chunking/feedback lesson. Remove the unrelated wealth/mental-health generalization.'),
(1741.20,1833.666667,'Project Vend and hallucinations','Keep the bored-by-Vend reaction, human-customer setup, poor pricing, hallucination definition and token explanation.'),
(1882.233333,1950.666667,None,'Retain the interpretability question, linear-algebra banter and mathematician callback; remove the speculative ten-outcomes hallucination mechanism.'),
(1952.4,1964.533333,None,'Keep the concrete operational changes; trim uncertain date wording.'),
(1972.466667,2032.233333,None,'Keep better tools, phase-two improvement, remaining autonomy question and the baby punchline. Remove unmeasured less-hallucination claim.'),
(2144.666667,2184.566667,'Trust and guardrails','Keep the question about user instructions versus bad actors and checking; remove the confusing invented-agent setup. This is a discussion of mitigations, not a guarantee.'),
(2193.666667,2209.666667,'Personal agents: a five-minute audition','Introduce the two products and Mary\'s invite experience.'),
(2212.633333,2348.866667,None,'Keep Mary\'s deliberately limited Muse trial, harsh-critic joke, Bug naming, exact reported task frustrations and her explicit qualification that she did not test deeply.'),
(2355.166667,2367.466667,None,'Keep the texting-interface contrast and teddy-bear joke; omit unverified team-size/funding and privacy-setting claims.'),
(2407.20,2474.733333,'Instinct: useful proactive work','Keep the returns example as Mary\'s account of the agent\'s reported outcome, including the approval request. No external transaction verification is asserted.'),
(2482.233333,2546.166667,None,'Keep the assignment, voice-message/emojis and TA email-draft examples; preserve the specific time adjustment and user review.'),
(2546.166667,2553.366667,'Who pays for a free assistant?','Keep the monetization question; omit the unverified Instinct advertising/cap claim.'),
(2579.366667,2703.233333,None,'Keep the hypothetical travel-agent/advertising analogy and disclosure disagreement. Remove specific unsupported monetization and tier assertions from the setup.'),
(2703.233333,2769.433333,'Dots, fit and the bike example','Retain the hosts\' experience rankings, Dottie/past context and DevDay discussion. Remove plan prices, eligibility overclaim and unannounced rollout timing.'),
(2802.233333,2908.466667,None,'Keep configuration, bike search, account verification and explicit withheld payment/final review. This is an assistance example, not a completed autonomous bike purchase.'),
(3011.433333,3024.933333,'OpenClaw and the interface','Keep the funny Big Pete/lobster naming and admission of not having used it; remove unverified legal-letter gossip and authorship inference.'),
(3029.533333,3083.766667,None,'Keep Josh\'s own early configuration experience and messaging-interface comparison; remove earliest/first-ever overclaims.'),
(3377.666667,3401.966667,'Pay for outcomes','Keep Sierra\'s customer-service use case and general pricing contrast; remove the unverified dollar rate and the long medical/legal-liability tangent.'),
(3813.833333,3883.966667,None,'Retain Mary\'s clear gym analogy: per person, per minute, per muscle gained. This is hypothetical, not a pricing claim about Planet Fitness.'),
(3907.533333,3933.333333,None,'Keep the gym efficiency/outcome payoff; remove the repeated model-economics lead-in and unnecessary Harvey detour.'),
(3933.333333,4088.833333,'What an agent actually is','Keep Mary\'s learning/callback moment and Josh\'s organized components/loop recap; preserve the future workforce question as a future discussion.'),
(4088.833333,4167.666667,'The important egg question','Keep the egg-preference callback, slow-scramble story and hard-versus-soft-boiled exchange. Cut the unsupported categorical food-safety reassurance.'),
(4178.066667,4215.166667,None,'Keep the expired-egg callback, soft-boiled naming and complete flippity-flop signoff. Omit post-recording chatter. No covered-lens gesture appears at this ending.'),
]
def segment(a,b,reason,chapter=None,kind='camera',source=SRC):
 af=round(a*30);bf=round(b*30)
 return {'source':source,'source_start_frame':af,'source_end_frame':bf,'in':af/30,'out':bf/30,'frames':bf-af,'reason':reason,'chapter':chapter,'kind':kind,'audio_stream':1 if kind=='camera' else 0}
hooks=[
('01-big-egg','Big Egg and the egg police',[(1291.533333,1301.166667),(1382.70,1397.80)],'Recommended: immediate absurd egg-team premise, both hosts, a clean too-many-eggs payoff.'),
('02-five-minute-audition','What if I die tomorrow trying to get Muse to work?',[(2222.166667,2246.90)],'Recommended: strong personal stakes joke, the harsh-critic response and a real qualification.'),
('03-i-just-want-a-baby','I do not know where we are going with the baby',[(2004.10,2032.233333)],'Recommended: an explanation turns into an unexpected personal punchline.'),
('04-four-hundred-coworkers','Me and my 400 coworkers',[(1440.90,1449.50),(1504.866667,1521.00)],'Contrast a practical single agent with the entertaining AI-team/startup boast.'),
('05-mathematicians','Bring back the mathematicians',[(1907.266667,1921.966667),(1940.70,1950.666667)],'Linear-algebra banter and the extinct-mathematicians callback; clearly a joke.'),
('06-agent-gender','She is doing so well she has to be a she',[(2407.20,2412.833333),(2427.60,2445.166667)],'Instinct setup, spontaneous gender joke and an actual approval question.'),
('07-runny-boil','You are having a runny boil?',[(4137.733333,4157.60),(4162.466667,4167.666667)],'Egg-preference disagreement and an odd phrase; food-safety reassurance excluded.'),
('08-eggs-and-credit-cards','That would piss you off. I would kind of love it.',[(145.066667,159.10),(190.60,198.20),(123.133333,133.90)],'Price versus convenience disagreement; only hypothetical shopping, no inaccurate Fowler setup.'),
]
# Last hook exceeds 30 seconds: use the concise personal reaction with the approval question.
hooks[-1]=('08-eggs-and-credit-cards',hooks[-1][1],[(190.60,198.20),(123.133333,139.766667)],hooks[-1][3])
intro_source=str(repo/'03_ASSETS/music/oood-sting-5s.wav');intro_still=str(repo/'03_ASSETS/codex-mono-mirrored-3digit/intro-card.png')
outro_source=str(repo/'03_ASSETS/music/oood-outro-11s.wav');outro_still=str(repo/'03_ASSETS/codex-mono-mirrored-3digit/outro-card.png')
H=[]
for id,title,ranges,why in hooks:
 segs=[segment(a,b,'Authentic hook excerpt; preserved setup/reaction.',kind='camera') for a,b in ranges]
 remain=900-sum(s['frames'] for s in segs)
 assert remain>0,(id,remain)
 card=segment(0,remain/30,'Recurring card/sting; preview ends here, without full episode opening.',kind='card',source=intro_source);card['still']=intro_still;card['gain_db']=-5
 segs.append(card);t=0
 for s in segs:s['timeline_in']=t/30;t+=s['frames'];s['timeline_out']=t/30
 H.append({'id':id,'title':title,'file':'hooks/'+id+'.mp4','reason':why,'segments':segs,'frames':t,'duration':t/30})
body=[segment(a,b,why,chapter) for a,b,chapter,why in choices]
# Provisional hook is an editorial recommendation, not a host selection.
segs=[dict(s) for s in H[0]['segments']]+body
outro=segment(0,323/30,'Recurring Episode 000 three-prompt outro/music.',kind='card',source=outro_source);outro.update(still=outro_still,gain_db=-5);segs.append(outro)
t=0;chapters=[{'time':0,'title':'Big Egg: cold open (provisional)'}]
for k,s in enumerate(segs):
 s['id']=f's{k:03}';s['timeline_in']=t/30;t+=s['frames'];s['timeline_out']=t/30
 if s.get('chapter'):chapters.append({'time':s['timeline_in'],'title':s['chapter']})
# Collapse close introductory markers to meet shared chapter spacing.
chapters=[c for i,c in enumerate(chapters) if i==0 or c['time']-chapters[i-1]['time']>=30]
assert all(b['time']-a['time']>=30 for a,b in zip(chapters,chapters[1:]));assert t/30-chapters[-1]['time']>=30
m={'title':'AI agents: what would we actually trust them to do?','status':'Proposed host-review cut; not approved or published','source':SRC,'source_sha256':json.loads((R/'source-review/inventory.json').read_text())['source_sha256'],'fps':30,'width':1920,'height':1080,'output_file':'agents-proposed-cut-v1.mp4','total_frames':t,'duration':t/30,'provisional_hook':H[0]['id'],'segments':segs,'body':body,'hooks':H,'chapters':chapters,'audio_strategy':'Use one verified AAC mix; center its two independent channels at equal weights; restrained 60 Hz rumble reduction and two-pass loudness normalization. No claim of continuous auditory review.'}
(R/'edit-manifest-v1.json').write_text(json.dumps(m,indent=2)+'\n')
with (R/'edit-decision-list.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['id','source','source_start','source_end','output_start','output_end','reason'])
 for s in segs:w.writerow([s['id'],s['source'],s['in'],s['out'],s['timeline_in'],s['timeline_out'],s['reason']])
print('Duration',t/30, 'minutes',t/1800,'body',sum(s['frames'] for s in body)/1800,'segments',len(segs),'chapters',len(chapters))
