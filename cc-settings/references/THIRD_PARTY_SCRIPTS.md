# Third-Party Script Identification Database

Use this reference to identify scripts and determine the appropriate confidence level for recommendations.

---

## Analytics & Tag Managers

**Confidence Level: KNOWN TRADE-OFF**
Deferring analytics may result in lost pageview data for users who bounce before scripts load.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `gtm.js`, `googletagmanager.com` | Google Tag Manager | Container for other tags |
| `gtag/js`, `www.googletagmanager.com/gtag` | Google Analytics 4 | GA4 tracking |
| `analytics.js`, `google-analytics.com/analytics.js` | Universal Analytics | Legacy GA (deprecated) |
| `G-XXXXXXXX` in URL | GA4 Property | Each property loads separately |
| `clarity.js`, `clarity.ms` | Microsoft Clarity | Session recording, heatmaps |
| `lux.js`, `cdn.speedcurve.com` | SpeedCurve LUX | RUM performance monitoring |
| `rum.js`, various RUM providers | Real User Monitoring | Performance analytics |
| `hotjar.com`, `static.hotjar.com` | Hotjar | Heatmaps, recordings |
| `fullstory.com` | FullStory | Session replay |
| `heap.io`, `heapanalytics.com` | Heap | Product analytics |
| `mixpanel.com` | Mixpanel | Product analytics |
| `segment.com`, `cdn.segment.com` | Segment | Customer data platform |
| `amplitude.com` | Amplitude | Product analytics |
| `plausible.io` | Plausible | Privacy-focused analytics |
| `fathom.com`, `usefathom.com` | Fathom | Privacy-focused analytics |
| `matomo.js`, `piwik.js` | Matomo/Piwik | Self-hosted analytics |

---

## Consent Management Platforms

**Confidence Level: CANNOT DEFER**
These are legally required for GDPR/CCPA compliance. Deferring or removing breaks compliance.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `usercentrics.eu`, `WebSdk.lib.js` | UserCentrics | CMP - must load early |
| `cookiebot.com`, `consent.cookiebot.com` | Cookiebot | CMP |
| `onetrust.com`, `cdn.cookielaw.org` | OneTrust | Enterprise CMP |
| `didomi.io` | Didomi | CMP |
| `trustarc.com`, `consent.trustarc.com` | TrustArc | CMP |
| `quantcast.com/cmp` | Quantcast Choice | CMP |
| `iubenda.com` | iubenda | CMP + privacy policy |
| `termly.io` | Termly | CMP |
| `osano.com` | Osano | CMP |
| `consentmanager.net` | ConsentManager | CMP |

---

## Advertising & Marketing

**Confidence Level: REQUIRES VERIFICATION**
These often impact revenue. Verify with business stakeholders before modifying.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `googlesyndication.com` | Google AdSense | Display ads |
| `doubleclick.net`, `googleads.g.doubleclick.net` | Google Ad Manager | Programmatic ads |
| `pagead2.googlesyndication.com` | Google Publisher Tag | Ad serving |
| `connect.facebook.net`, `fbevents.js` | Meta Pixel | Conversion tracking |
| `facebook.net/tr/` | Meta Pixel (tracking) | Event tracking |
| `snap.licdn.com`, `insight.min.js` | LinkedIn Insight Tag | B2B tracking |
| `bat.bing.com`, `bat.js` | Microsoft Ads (Bing) | UET tag |
| `ads-twitter.com`, `static.ads-twitter.com` | X (Twitter) Ads | Conversion tracking |
| `tiktok.com/i18n/pixel` | TikTok Pixel | Conversion tracking |
| `pinterest.com/ct.js` | Pinterest Tag | Conversion tracking |
| `criteo.com`, `static.criteo.net` | Criteo | Retargeting |
| `taboola.com` | Taboola | Native ads |
| `outbrain.com` | Outbrain | Native ads |
| `amazon-adsystem.com` | Amazon Ads | Display ads |

---

## A/B Testing & Personalization

**Confidence Level: KNOWN TRADE-OFF**
These often need to load early to prevent flicker. Deferring may break tests or cause flicker.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `optimizely.com`, `cdn.optimizely.com` | Optimizely | A/B testing |
| `vwo.com`, `dev.visualwebsiteoptimizer.com` | VWO | A/B testing |
| `googleoptimize.com` | Google Optimize | A/B testing (deprecated) |
| `abtasty.com` | AB Tasty | A/B testing |
| `kameleoon.com` | Kameleoon | A/B testing |
| `dynamic-yield.com` | Dynamic Yield | Personalization |
| `monetate.net` | Monetate | Personalization |
| `evergage.com` | Salesforce Interaction Studio | Personalization |

---

## Chat & Support Widgets

**Confidence Level: SAFE TO LAZY-LOAD**
These can typically be loaded on user interaction without impacting functionality.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `intercom.com`, `widget.intercom.io` | Intercom | Chat + support |
| `zendesk.com`, `static.zdassets.com` | Zendesk | Support widget |
| `drift.com`, `js.driftt.com` | Drift | Chat |
| `crisp.chat`, `client.crisp.chat` | Crisp | Chat |
| `tawk.to`, `embed.tawk.to` | Tawk.to | Free chat |
| `livechatinc.com`, `cdn.livechatinc.com` | LiveChat | Chat |
| `freshdesk.com`, `freshchat.com` | Freshworks | Support |
| `hubspot.com` (chat widget) | HubSpot Chat | Chat |
| `olark.com` | Olark | Chat |
| `tidio.co` | Tidio | Chat + bots |

---

## Social & Embeds

**Confidence Level: SAFE TO LAZY-LOAD (Facade Pattern)**
Heavy embeds. Use facade pattern (show thumbnail, load on click).

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `youtube.com/iframe_api`, `www-player.css` | YouTube | ~700KB player JS |
| `platform.twitter.com/widgets.js` | X (Twitter) Embeds | Tweet embeds |
| `instagram.com/embed.js` | Instagram Embeds | Post embeds |
| `pinterest.com/pinit.js` | Pinterest | Pin buttons |
| `addthis.com` | AddThis | Social sharing |
| `sharethis.com` | ShareThis | Social sharing |
| `addtoany.com` | AddToAny | Social sharing |
| `facebook.com/plugins` | Facebook Plugins | Like buttons, embeds |
| `vimeo.com/player` | Vimeo | Video player |

---

## Maps & Location

**Confidence Level: SAFE TO LAZY-LOAD**
Load only when map container is in viewport.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `maps.googleapis.com` | Google Maps | Maps API |
| `api.mapbox.com` | Mapbox | Maps |
| `leaflet.js`, `unpkg.com/leaflet` | Leaflet | Open-source maps |
| `openstreetmap.org` | OpenStreetMap | Open-source maps |

---

## E-commerce & Payments

**Confidence Level: REQUIRES VERIFICATION**
Payment-related scripts are business-critical.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `js.stripe.com` | Stripe | Payment processing |
| `paypal.com/sdk` | PayPal | Payment processing |
| `klarna.com`, `x.klarnacdn.net` | Klarna | Buy now, pay later |
| `afterpay.com` | Afterpay | Buy now, pay later |
| `affirm.com` | Affirm | Buy now, pay later |
| `shopify.com` (various) | Shopify | E-commerce platform |
| `yotpo.com` | Yotpo | Reviews |
| `bazaarvoice.com` | Bazaarvoice | Reviews |
| `trustpilot.com` | Trustpilot | Reviews |
| `recharge.com` | Recharge | Subscriptions |

---

## CDN & Performance

**Confidence Level: SAFE TO OPTIMIZE**
These serve assets and can often be consolidated or preconnected.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `cloudflare.com`, `cdnjs.cloudflare.com` | Cloudflare | CDN |
| `cdn.jsdelivr.net` | jsDelivr | Open source CDN |
| `unpkg.com` | UNPKG | npm CDN |
| `ajax.googleapis.com` | Google Hosted Libraries | jQuery, etc. |
| `fonts.googleapis.com`, `fonts.gstatic.com` | Google Fonts | Web fonts |
| `use.typekit.net` | Adobe Fonts | Web fonts |
| `use.fontawesome.com` | Font Awesome | Icon fonts |

---

## Security & Bot Detection

**Confidence Level: REQUIRES VERIFICATION**
Security tools may be critical for fraud prevention.

| Script Pattern | Service | Notes |
|----------------|---------|-------|
| `google.com/recaptcha` | reCAPTCHA | Bot detection |
| `hcaptcha.com` | hCaptcha | Bot detection |
| `cloudflare.com/cdn-cgi/challenge-platform` | Cloudflare Bot Management | Bot detection |
| `fingerprintjs.com` | FingerprintJS | Device fingerprinting |
| `sift.com` | Sift | Fraud detection |
| `datadome.co` | DataDome | Bot protection |

---

## Unknown Scripts

If a script doesn't match any pattern above:

1. **Check the domain** - Is it the client's own domain? → Likely first-party
2. **Check the filename** - Does it suggest purpose? (`tracking.js`, `analytics.js`)
3. **Check DevTools Network tab** - What does it request/send?

**Always mark as REQUIRES VERIFICATION** with specific questions:
> "Development team should confirm the purpose of `xyz-widget.min.js` (loaded from thirdparty.com) before modifying its loading behavior."
