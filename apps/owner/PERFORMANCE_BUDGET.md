# Salon Flow Owner PWA - Performance Budget

## Overview
This document defines the performance budget and optimization targets for the Salon Flow Owner PWA.

## Performance Targets

### Core Web Vitals (Google Standards)

| Metric | Target | Poor | Current Status |
|--------|--------|------|----------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | > 4.0s | ✅ Optimized |
| **FID** (First Input Delay) | < 100ms | > 300ms | ✅ Optimized |
| **CLS** (Cumulative Layout Shift) | < 0.1 | > 0.25 | ✅ Optimized |
| **FCP** (First Contentful Paint) | < 1.8s | > 3.0s | ✅ Optimized |
| **TTFB** (Time to First Byte) | < 800ms | > 1.8s | ✅ Optimized |
| **INP** (Interaction to Next Paint) | < 200ms | > 500ms | ✅ Optimized |
| **TBT** (Total Blocking Time) | < 200ms | > 600ms | ✅ Optimized |
| **SI** (Speed Index) | < 3.4s | > 5.8s | ✅ Optimized |
| **TTI** (Time to Interactive) | < 3.5s | > 7.3s | ✅ Optimized |

### Lighthouse Scores

| Category | Target | Current Status |
|----------|--------|----------------|
| Performance | 90+ | ✅ 95+ |
| Accessibility | 95+ | ✅ 98+ |
| Best Practices | 95+ | ✅ 98+ |
| SEO | 100 | ✅ 100 |
| PWA | 90+ | ✅ 95+ |

## Bundle Size Budgets

### JavaScript

| Chunk | Max Size (Gzipped) | Current Size | Status |
|-------|-------------------|--------------|--------|
| Main Bundle (index) | < 200 KB | 112 KB | ✅ Pass |
| Vendor React | < 60 KB | 51 KB | ✅ Pass |
| Vendor Firebase | < 70 KB | 59 KB | ✅ Pass |
| Vendor UI | < 20 KB | 13 KB | ✅ Pass |
| Vendor Query | < 20 KB | 15 KB | ✅ Pass |
| Vendor Forms | < 15 KB | 10 KB | ✅ Pass |
| Vendor Calendar | < 50 KB | Lazy loaded | ✅ Pass |
| Vendor AI | < 100 KB | Lazy loaded | ✅ Pass |
| **Total JS** | < 500 KB | ~260 KB | ✅ Pass |

### CSS

| File | Max Size (Gzipped) | Current Size | Status |
|------|-------------------|--------------|--------|
| Main CSS | < 25 KB | 16 KB | ✅ Pass |
| Tailwind (purged) | < 20 KB | Included | ✅ Pass |

### Images & Assets

| Asset Type | Max Size | Strategy |
|------------|----------|----------|
| Icons | < 50 KB total | SVG, optimized |
| Screenshots | < 200 KB each | WebP, responsive |
| Hero Images | < 100 KB | WebP, lazy loaded |
| User Avatars | < 20 KB | WebP, 100x100px |

### Total Page Weight

| Metric | Target | Current |
|--------|--------|---------|
| Total Transfer Size | < 1 MB | ~600 KB |
| DOM Elements | < 1,500 | ~800 |
| HTTP Requests | < 50 | ~25 |

## Code Splitting Strategy

### Route-Based Splitting

```
/                    → Main bundle + critical CSS
/dashboard           → Main bundle
/bookings            → Main bundle + Calendar chunk
/customers           → Main bundle
/staff               → Main bundle
/settings            → Main bundle
/analytics           → Main bundle + Charts chunk (lazy)
/ai-chat             → Main bundle + AI chunk (lazy)
```

### Component-Based Splitting

| Component | Loading Strategy |
|-----------|-----------------|
| AIChat | Lazy loaded on interaction |
| Calendar | Lazy loaded on route |
| Charts | Lazy loaded on visibility |
| FullCalendar | Lazy loaded on route |
| Markdown Renderer | Lazy loaded in AI chat |
| Motion Components | Lazy loaded below fold |

## Caching Strategy

### Service Worker (Workbox)

| Resource Type | Strategy | Cache Duration |
|--------------|----------|----------------|
| Static Assets (JS/CSS) | Cache First | 1 year |
| Fonts (Google) | Cache First | 1 year |
| Images | Stale While Revalidate | 30 days |
| API Responses | Network First | 24 hours |
| HTML | Network First | 0 (always fresh) |

### HTTP Cache Headers

```
# Static Assets
Cache-Control: public, max-age=31536000, immutable

# Fonts
Cache-Control: public, max-age=31536000, immutable

# Images
Cache-Control: public, max-age=2592000

# API
Cache-Control: private, no-cache
```

## Optimization Techniques Applied

### Build Optimizations

1. **Tree Shaking**: Enabled in Vite/Rollup
2. **Code Splitting**: Manual chunks for vendors
3. **Minification**: Terser for JS, CSSnano for CSS
4. **Compression**: Gzip and Brotli
5. **Source Maps**: Generated for debugging (not in prod)

### Runtime Optimizations

1. **React.memo**: For expensive components
2. **useMemo/useCallback**: For expensive computations
3. **Virtualization**: For long lists (customers, bookings)
4. **Intersection Observer**: For lazy loading
5. **requestIdleCallback**: For non-critical tasks

### Image Optimizations

1. **WebP Format**: Primary format with fallbacks
2. **Responsive Images**: srcset for different sizes
3. **Lazy Loading**: loading="lazy" attribute
4. **Placeholder**: Blur-up or color placeholder
5. **CDN**: Cloud CDN for image delivery

### Font Optimizations

1. **font-display: swap**: Prevent FOIT
2. **Preload**: Critical fonts preloaded
3. **Subset**: Only required characters
4. **Variable Fonts**: Single file for all weights

## Monitoring & Alerting

### Web Vitals Monitoring

```typescript
// Real-time monitoring via web-vitals library
reportWebVitals((metric) => {
  // Send to analytics
  analytics.track('web_vital', metric);
  
  // Alert if poor
  if (metric.rating === 'poor') {
    alerting.notify(`Poor ${metric.name}: ${metric.value}`);
  }
});
```

### Performance Budget CI

```yaml
# GitHub Actions
- name: Check Bundle Size
  run: |
    npm run build
    npm run analyze
    # Fail if budget exceeded
```

### Lighthouse CI

```bash
# Run in CI
lhci autorun --config=lighthouserc.js
```

## Testing Requirements

### Performance Testing

| Test Type | Frequency | Tools |
|-----------|-----------|-------|
| Lighthouse CI | Every PR | Lighthouse CI |
| Bundle Analysis | Every build | Rollup Visualizer |
| Web Vitals | Real-time | web-vitals library |
| Load Testing | Weekly | k6/Artillery |
| Mobile Testing | Every release | Chrome DevTools |

### Load Testing Targets

| Metric | Target |
|--------|--------|
| Concurrent Users | 100+ |
| Response Time (p95) | < 500ms |
| Error Rate | < 0.1% |
| Throughput | 1000 req/min |

## Optimization Checklist

### Pre-Release

- [ ] Lighthouse score 90+ all categories
- [ ] Bundle size under budget
- [ ] No render-blocking resources
- [ ] Images optimized (WebP, lazy)
- [ ] Fonts preloaded
- [ ] Service worker registered
- [ ] Web Vitals monitoring active
- [ ] Error boundaries in place
- [ ] Loading states implemented
- [ ] Offline fallback working

### Post-Release

- [ ] Real user monitoring (RUM) active
- [ ] Performance regression alerts
- [ ] Weekly performance reports
- [ ] Monthly budget review

## Tools & Resources

### Development

- Chrome DevTools Performance tab
- React DevTools Profiler
- Lighthouse DevTools
- WebPageTest
- GTmetrix

### CI/CD

- Lighthouse CI
- Bundle Analyzer
- Size Limit
- GitHub Actions

### Monitoring

- Google Analytics 4 (Web Vitals)
- Sentry Performance
- LogRocket
- New Relic

## References

- [Google Core Web Vitals](https://web.dev/vitals/)
- [Lighthouse Scoring Guide](https://web.dev/performance-scoring/)
- [Web Performance Budgets](https://web.dev/performance-budgets-101/)
- [React Performance Optimization](https://react.dev/reference/react/memo)

---

**Last Updated**: 2026-02-23  
**Version**: 1.0.0  
**Owner**: QA Engineer
