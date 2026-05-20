export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, first_name } = req.body;

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }

  const pubId  = process.env.BEEHIIV_PUB_ID;
  const apiKey = process.env.BEEHIIV_API_KEY;

  if (!pubId || !apiKey) {
    return res.status(500).json({ error: 'Server configuration error' });
  }

  try {
    const response = await fetch(
      `https://api.beehiiv.com/v2/publications/${pubId}/subscriptions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          email,
          first_name: first_name || '',
          reactivate_existing: false,
          send_welcome_email: true,
          utm_source: 'gfto-website'
        })
      }
    );

    if (response.ok) {
      return res.status(200).json({ success: true });
    }

    const err = await response.json();
    console.error('Beehiiv error:', err);
    return res.status(502).json({ error: 'Subscription failed' });

  } catch (e) {
    console.error('Subscribe handler error:', e);
    return res.status(500).json({ error: 'Internal error' });
  }
}
