// Everything you are likely to change lives here.
window.OOOD = {
  youtube: 'https://www.youtube.com/@OutOfOurDepthPod',

  // Paste the show link from Spotify for Creators once the show is live,
  // e.g. 'https://open.spotify.com/show/XXXXXXXX'. While this is empty the
  // Spotify button says "coming soon" and does not link anywhere.
  spotify: '',

  email: 'hi@outofourdepth.com',

  socials: [
    { label: 'Instagram', url: 'https://www.instagram.com/outofourdepthpod/' },
    { label: 'TikTok', url: 'https://www.tiktok.com/@outofourdepthpod' },
    { label: 'X', url: 'https://x.com/OutOfOurDepthX' },
  ],

  // The latest-episode card fills itself from YouTube via /api/latest.
  // To pin a specific episode instead, fill this in, e.g.
  // { title: 'Why we are here', url: 'https://www.youtube.com/watch?v=...', thumbnail: '' }
  pinnedEpisode: null,
};
