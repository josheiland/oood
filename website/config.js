// Everything you are likely to change lives here.
window.OOOD = {
  youtube: 'https://www.youtube.com/@OutOfOurDepthPod',

  spotify: 'https://open.spotify.com/show/5uqWe60E7Vi3MfQtJki7b1',

  email: 'hi@outofourdepth.com',

  // Shown as icons in the top right, in this order, followed by the email icon.
  // icon: 'instagram' | 'x' | 'linkedin' | 'facebook' | 'tiktok' | 'youtube' | 'spotify'
  // Josh trimmed these to Instagram, X and email on 2026-10-03. The other accounts are live; add them back here if wanted:
  // { label: 'TikTok', icon: 'tiktok', url: 'https://www.tiktok.com/@outofourdepthpod' },
  // { label: 'LinkedIn', icon: 'linkedin', url: 'https://www.linkedin.com/company/outofourdepth' },
  // { label: 'Facebook', icon: 'facebook', url: 'https://www.facebook.com/outofourdepthpod' },
  socials: [
    { label: 'Instagram', icon: 'instagram', url: 'https://www.instagram.com/outofourdepthpod/' },
    { label: 'X', icon: 'x', url: 'https://x.com/OutOfOurDepthX' },
  ],

  // Verified public uploads, newest first. Numbering follows the public order (renumbered 2026-10-03:
  // the AI-basics episode was re-uploaded without pop-ups, so it is now 002).
  // Keep these as a fallback when YouTube is unavailable.
  episodes: [
    {
      id: 'cp4P_2t5rRQ', number: '002', title: "Who's Who in AI (Explained With a Toyota Prius)",
      blurb: 'We untangle AI companies, models and apps, with a little help from a Toyota Prius.',
      published: '2026-10-03T19:37:28+00:00',
      url: 'https://www.youtube.com/watch?v=cp4P_2t5rRQ',
      thumbnail: 'https://i.ytimg.com/vi/cp4P_2t5rRQ/maxresdefault.jpg'
    },
    {
      id: 'd-ykZl4WHjo', number: '001', title: "Projects, Connectors & Skills… Take Your AI From Fresh Intern to Full-Time Hire",
      blurb: 'We try projects, connectors and skills to give AI context and put it to work.',
      published: '2026-09-30T23:00:52+00:00',
      url: 'https://www.youtube.com/watch?v=d-ykZl4WHjo',
      thumbnail: 'https://i.ytimg.com/vi/d-ykZl4WHjo/maxresdefault.jpg'
    },
    {
      id: 'y0NH_zvAdEo', number: '000', title: "We Can’t Keep Up With AI Either (So We Started a Podcast!)",
      blurb: 'Meet Josh and Mary, and why we decided to learn AI out loud together.',
      published: '2026-09-30T21:31:01+00:00',
      url: 'https://www.youtube.com/watch?v=y0NH_zvAdEo',
      thumbnail: 'https://i.ytimg.com/vi/y0NH_zvAdEo/maxresdefault.jpg'
    }
  ],

  // The latest-episode card fills itself from YouTube via /api/latest.
  // To pin a specific episode instead, fill this in, e.g.
  // { title: 'Why we are here', url: 'https://www.youtube.com/watch?v=...', thumbnail: '' }
  pinnedEpisode: null,
};
