// Everything you are likely to change lives here.
window.OOOD = {
  youtube: 'https://www.youtube.com/@OutOfOurDepthPod',

  spotify: 'https://open.spotify.com/show/5uqWe60E7Vi3MfQtJki7b1',

  applePodcasts: 'https://podcasts.apple.com/us/podcast/out-of-our-depth/id6819080935',

  email: 'hi@outofourdepth.com',

  // Shown as icons in the top right, in this order, followed by the email icon.
  // icon: 'instagram' | 'x' | 'linkedin' | 'facebook' | 'tiktok' | 'youtube' | 'spotify'
  // Josh trimmed these to Instagram, X and email on 2026-10-03, then added LinkedIn back on 2026-10-04. The others are live; add them back here if wanted:
  // { label: 'TikTok', icon: 'tiktok', url: 'https://www.tiktok.com/@outofourdepthpod' },
  // { label: 'Facebook', icon: 'facebook', url: 'https://www.facebook.com/outofourdepthpod' },
  socials: [
    { label: 'Instagram', icon: 'instagram', url: 'https://www.instagram.com/outofourdepthpod/' },
    { label: 'X', icon: 'x', url: 'https://x.com/OutOfOurDepthX' },
    { label: 'LinkedIn', icon: 'linkedin', url: 'https://www.linkedin.com/company/outofourdepth' },
  ],

  // Saved public uploads, newest first. Episodes are numbered in public order from 000.
  // You don't need to edit this list: a GitHub job (scripts/sync-site-episodes.js) adds new
  // long-form uploads, updates renamed titles and drops deleted videos every few hours, and the
  // homepage also picks up anything newer straight from YouTube. Manual edits between the markers
  // get overwritten, except extra fields such as `blurb`, which are kept.
  episodes: [
    // episodes:start
    {
      id: 'yhVYY1N7hDg', number: '009', title: '[BONUS EPISODE] The Art of Personalization: Teaching AI YOUR voice & style',
      published: '2026-10-26T19:40:45+00:00',
      url: 'https://www.youtube.com/watch?v=yhVYY1N7hDg',
      thumbnail: 'https://i.ytimg.com/vi/yhVYY1N7hDg/maxresdefault.jpg'
    },
    {
      id: 'lGp5szF6HI4', number: '008', title: 'Will AI Take Our Jobs? What AGI Actually Means',
      published: '2026-10-21T22:49:52+00:00',
      url: 'https://www.youtube.com/watch?v=lGp5szF6HI4',
      thumbnail: 'https://i.ytimg.com/vi/lGp5szF6HI4/maxresdefault.jpg'
    },
    {
      id: '82qlgC3QcEw', number: '007', title: 'How to Learn AI Without Feeling Behind',
      published: '2026-10-17T15:43:55+00:00',
      url: 'https://www.youtube.com/watch?v=82qlgC3QcEw',
      thumbnail: 'https://i.ytimg.com/vi/82qlgC3QcEw/maxresdefault.jpg'
    },
    {
      id: 'NiEnSBPe158', number: '006', title: 'AI Planned Our Wedding',
      published: '2026-10-11T22:31:34+00:00',
      url: 'https://www.youtube.com/watch?v=NiEnSBPe158',
      thumbnail: 'https://i.ytimg.com/vi/NiEnSBPe158/maxresdefault.jpg'
    },
    {
      id: '_d-hzc6Lt5c', number: '005', title: 'How to Make AI Actually Sound Like You',
      published: '2026-10-09T22:11:34+00:00',
      url: 'https://www.youtube.com/watch?v=_d-hzc6Lt5c',
      thumbnail: 'https://i.ytimg.com/vi/_d-hzc6Lt5c/maxresdefault.jpg'
    },
    {
      id: 'Fby7CJC9i-Q', number: '004', title: 'ChatGPT as Our Running Coach: What We Had to Fix',
      published: '2026-10-06T14:54:38+00:00',
      url: 'https://www.youtube.com/watch?v=Fby7CJC9i-Q',
      thumbnail: 'https://i.ytimg.com/vi/Fby7CJC9i-Q/maxresdefault.jpg'
    },
    {
      id: 'rxethT04zMY', number: '003', title: 'What the Heck is an AI Agent?',
      published: '2026-10-04T19:13:36+00:00',
      url: 'https://www.youtube.com/watch?v=rxethT04zMY',
      thumbnail: 'https://i.ytimg.com/vi/rxethT04zMY/maxresdefault.jpg'
    },
    {
      id: 'cp4P_2t5rRQ', number: '002', title: "ChatGPT vs Claude vs Gemini: What's the Difference?",
      blurb: 'We untangle AI companies, models and apps, with a little help from a Toyota Prius.',
      published: '2026-10-03T19:37:28+00:00',
      url: 'https://www.youtube.com/watch?v=cp4P_2t5rRQ',
      thumbnail: 'https://i.ytimg.com/vi/cp4P_2t5rRQ/maxresdefault.jpg'
    },
    {
      id: 'd-ykZl4WHjo', number: '001', title: 'Claude/ChatGPT Skills, Projects & Connectors, Explained Simply',
      blurb: 'We try projects, connectors and skills to give AI context and put it to work.',
      published: '2026-09-30T23:00:52+00:00',
      url: 'https://www.youtube.com/watch?v=d-ykZl4WHjo',
      thumbnail: 'https://i.ytimg.com/vi/d-ykZl4WHjo/maxresdefault.jpg'
    },
    {
      id: 'y0NH_zvAdEo', number: '000', title: 'We Can’t Keep Up with AI Either (So We Started a Podcast!)',
      blurb: 'Meet Josh and Mary, and why we decided to learn AI out loud together.',
      published: '2026-09-30T21:31:01+00:00',
      url: 'https://www.youtube.com/watch?v=y0NH_zvAdEo',
      thumbnail: 'https://i.ytimg.com/vi/y0NH_zvAdEo/maxresdefault.jpg'
    }
    // episodes:end
  ],

  // Titles the site shows in place of YouTube's, by video ID. YouTube keeps its own title; the sync
  // job leaves these alone and uses them on the no-JS cards too.
  siteTitles: {
    'Fby7CJC9i-Q': 'Build With Us: Turn ChatGPT Into Your Coach', // Josh 2026-10-11
    // No ellipses on the site (Josh 2026-10-11). The E001/E002 overrides that stripped them were
    // dropped 2026-10-14, when the YouTube titles changed to ones without ellipses.
  },

  // YouTube video IDs to leave off the site, e.g. a trailer or clip uploaded as a long-form video.
  // Hidden videos also don't count toward episode numbers.
  hiddenVideos: [],

  // The latest-episode card fills itself from YouTube via /api/latest.
  // To pin a specific episode instead, fill this in, e.g.
  // { title: 'Why we are here', url: 'https://www.youtube.com/watch?v=...', thumbnail: '' }
  pinnedEpisode: null,
};
