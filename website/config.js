// Everything you are likely to change lives here.
window.OOOD = {
  youtube: 'https://www.youtube.com/@OutOfOurDepthPod',

  spotify: 'https://open.spotify.com/show/5uqWe60E7Vi3MfQtJki7b1',

  email: 'hi@outofourdepth.com',

  // Shown as icons in the top right, in this order, followed by the email icon.
  // icon: 'instagram' | 'x' | 'linkedin' | 'facebook' | 'tiktok' | 'youtube' | 'spotify'
  socials: [
    { label: 'Instagram', icon: 'instagram', url: 'https://www.instagram.com/outofourdepthpod/' },
    // TikTok hidden 2026-09-28 while @outofourdepthpod is suspended. Restore after the appeal:
    // { label: 'TikTok', icon: 'tiktok', url: 'https://www.tiktok.com/@outofourdepthpod' },
    { label: 'X', icon: 'x', url: 'https://x.com/OutOfOurDepthX' },
    { label: 'LinkedIn', icon: 'linkedin', url: 'https://www.linkedin.com/company/outofourdepth' },
    { label: 'Facebook', icon: 'facebook', url: 'https://www.facebook.com/outofourdepthpod' },
  ],

  // The latest-episode card fills itself from YouTube via /api/latest.
  // To pin a specific episode instead, fill this in, e.g.
  // { title: 'Why we are here', url: 'https://www.youtube.com/watch?v=...', thumbnail: '' }
  pinnedEpisode: null,
};
