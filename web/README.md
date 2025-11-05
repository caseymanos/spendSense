# SpendSense Next.js Web

React web app (Next.js App Router) for the SpendSense user experience.

## Prereqs
- Node 18+ (Node 20 recommended)
- Running API at `http://localhost:8000` (or set `NEXT_PUBLIC_API_URL`)

## Run
```bash
# From repo root
uv run uvicorn api.main:app --reload

# In another terminal
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# → http://localhost:3000
```

## Structure
- `app/` routes: `/dashboard`, `/learn`, `/privacy`
- `components/` shared UI blocks
- `lib/` API client, hooks, and types
- `providers/` React Query provider

## Notes
- Picks the first user automatically if you select one via the header user switcher; persists in `localStorage`.
- Consent changes update dashboard and feed automatically.

