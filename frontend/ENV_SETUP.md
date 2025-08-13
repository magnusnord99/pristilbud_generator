# Environment Variables Setup

## For Development

Create a `.env.local` file in the frontend directory with:

```bash
VITE_BACKEND_URL=http://127.0.0.1:8000
```

## For Production

Set the environment variable `VITE_BACKEND_URL` to your production backend URL.

## How it works

The application now uses a centralized config file (`src/config.ts`) that:
1. Reads `VITE_BACKEND_URL` from environment variables
2. Falls back to `http://127.0.0.1:8000` if not set
3. Provides consistent backend URL across all components

## Files updated

- `src/config.ts` - New centralized configuration
- `src/pages/LoginPage.tsx` - Now uses config.backendUrl
- `src/pages/OfferPage.tsx` - Now uses config.backendUrl

## Note

- `.env.local` is gitignored for security
- For production builds, set the environment variable in your deployment pipeline
- The fallback URL ensures the app works even without environment variables set
