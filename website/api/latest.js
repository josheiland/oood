// Returns the newest long-form upload on the Out of Our Depth YouTube channel.
// Tries the channel RSS feed first, then the channel's Videos tab (which leaves
// out Shorts). Responds { video: null } when the channel has nothing public yet,
// and the homepage shows its "coming soon" card instead.

const CHANNEL_ID = 'UCr2sdn2AwHyhjm5SUtWUNGQ';
const HANDLE = 'OutOfOurDepthPod';
const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36';

function decode(s) {
  return s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'");
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

async function fromFeed() {
  const r = await fetch(`https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}`, {
    headers: { 'User-Agent': UA },
  });
  if (!r.ok) return undefined;
  const xml = await r.text();
  for (const entry of xml.split('<entry>').slice(1)) {
    const link = (entry.match(/<link rel="alternate" href="([^"]+)"/) || [])[1] || '';
    if (link.includes('/shorts/')) continue;
    const id = (entry.match(/<yt:videoId>([^<]+)<\/yt:videoId>/) || [])[1];
    const title = (entry.match(/<title>([^<]*)<\/title>/) || [])[1];
    const published = (entry.match(/<published>([^<]+)<\/published>/) || [])[1];
    if (id && title) return toVideo(id, decode(title), published);
  }
  return null;
}

function findFirstVideo(node) {
  if (!node || typeof node !== 'object') return null;
  if (Array.isArray(node)) {
    for (const item of node) {
      const hit = findFirstVideo(item);
      if (hit) return hit;
    }
    return null;
  }
  const lockup = node.lockupViewModel;
  if (lockup && lockup.contentId && lockup.contentType === 'LOCKUP_CONTENT_TYPE_VIDEO') {
    const title = lockup.metadata?.lockupMetadataViewModel?.title?.content;
    if (title) return toVideo(lockup.contentId, title);
  }
  const renderer = node.videoRenderer || node.gridVideoRenderer;
  if (renderer && renderer.videoId) {
    const title = renderer.title?.runs?.[0]?.text || renderer.title?.simpleText;
    if (title) return toVideo(renderer.videoId, title);
  }
  for (const value of Object.values(node)) {
    const hit = findFirstVideo(value);
    if (hit) return hit;
  }
  return null;
}

async function fromChannelPage() {
  const r = await fetch(`https://www.youtube.com/@${HANDLE}/videos`, {
    headers: { 'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9' },
  });
  if (!r.ok) return undefined;
  const html = await r.text();
  const m = html.match(/var ytInitialData = (\{.*?\});<\/script>/s);
  if (!m) return undefined;
  return findFirstVideo(JSON.parse(m[1]));
}

module.exports = async (req, res) => {
  let video;
  for (const source of [fromFeed, fromChannelPage]) {
    try {
      video = await source();
    } catch (err) {
      video = undefined;
    }
    if (video) break;
  }
  // Cache at the edge for 15 minutes; serve a stale copy for up to a day if YouTube is slow.
  res.setHeader('Cache-Control', 'public, s-maxage=900, stale-while-revalidate=86400');
  res.status(200).json({ video: video || null });
};
