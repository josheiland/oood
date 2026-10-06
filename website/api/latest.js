// Returns every public long-form upload on the Out of Our Depth YouTube channel, newest first,
// as { video, videos }. `video` is the newest one (kept for older pages).
//
// Sources, in order:
//   1. The channel's long-form uploads feed (playlist UULF...). It leaves out Shorts and gives exact
//      publish dates, but only covers the newest 15.
//   2. The channel feed, skipping /shorts/ links.
//   3. The channel's Videos tab (leaves out Shorts, but has no exact dates).
// The homepage merges this list with the saved episodes in config.js, which a GitHub job keeps
// complete (scripts/sync-site-episodes.js). Responds { video: null, videos: [] } when nothing loads.

const CHANNEL_ID = 'UCr2sdn2AwHyhjm5SUtWUNGQ';
const LONG_FORM_PLAYLIST = 'UULF' + CHANNEL_ID.slice(2);
const HANDLE = 'OutOfOurDepthPod';
const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36';

function decode(s) {
  return s
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&');
}

function toVideo(id, title, published) {
  return {
    id,
    title,
    published: published || null,
    url: `https://www.youtube.com/watch?v=${id}`,
    thumbnail: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
  };
}

function parseFeed(xml) {
  const videos = [];
  for (const entry of xml.split('<entry>').slice(1)) {
    const link = (entry.match(/<link rel="alternate" href="([^"]+)"/) || [])[1] || '';
    if (link.includes('/shorts/')) continue;
    const id = (entry.match(/<yt:videoId>([^<]+)<\/yt:videoId>/) || [])[1];
    const title = (entry.match(/<title>([^<]*)<\/title>/) || [])[1];
    const published = (entry.match(/<published>([^<]+)<\/published>/) || [])[1];
    if (id && title) videos.push(toVideo(id, decode(title), published));
  }
  return videos;
}

async function fromFeedUrl(url) {
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!r.ok) return undefined;
  const xml = await r.text();
  if (!xml.includes('<feed')) return undefined;
  return parseFeed(xml);
}

const fromLongFormFeed = () =>
  fromFeedUrl(`https://www.youtube.com/feeds/videos.xml?playlist_id=${LONG_FORM_PLAYLIST}`);
const fromChannelFeed = () =>
  fromFeedUrl(`https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}`);

function collectVideos(node, out, seen) {
  if (!node || typeof node !== 'object') return;
  if (Array.isArray(node)) {
    for (const item of node) collectVideos(item, out, seen);
    return;
  }
  const lockup = node.lockupViewModel;
  if (lockup && lockup.contentId && lockup.contentType === 'LOCKUP_CONTENT_TYPE_VIDEO') {
    const title = lockup.metadata?.lockupMetadataViewModel?.title?.content;
    if (title && !seen.has(lockup.contentId)) {
      seen.add(lockup.contentId);
      out.push(toVideo(lockup.contentId, title));
    }
  }
  const renderer = node.videoRenderer || node.gridVideoRenderer;
  if (renderer && renderer.videoId) {
    const title = renderer.title?.runs?.[0]?.text || renderer.title?.simpleText;
    if (title && !seen.has(renderer.videoId)) {
      seen.add(renderer.videoId);
      out.push(toVideo(renderer.videoId, title));
    }
  }
  for (const value of Object.values(node)) collectVideos(value, out, seen);
}

async function fromChannelPage() {
  const r = await fetch(`https://www.youtube.com/@${HANDLE}/videos`, {
    headers: { 'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9' },
  });
  if (!r.ok) return undefined;
  const html = await r.text();
  const m = html.match(/var ytInitialData = (\{.*?\});<\/script>/s);
  if (!m) return undefined;
  const out = [];
  collectVideos(JSON.parse(m[1]), out, new Set());
  return out;
}

async function loadVideos() {
  for (const source of [fromLongFormFeed, fromChannelFeed, fromChannelPage]) {
    try {
      const videos = await source();
      if (videos && videos.length) return videos;
    } catch (err) {
      // try the next source
    }
  }
  return [];
}

module.exports = async (req, res) => {
  const videos = await loadVideos();
  // Cache at the edge for 15 minutes; serve a stale copy for up to a day if YouTube is slow.
  res.setHeader('Cache-Control', 'public, s-maxage=900, stale-while-revalidate=86400');
  res.status(200).json({ video: videos[0] || null, videos });
};

module.exports.loadVideos = loadVideos;
module.exports.parseFeed = parseFeed;
