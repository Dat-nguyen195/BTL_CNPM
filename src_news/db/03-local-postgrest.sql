-- The local PostgREST instance has no published port and is reached by FastAPI.
BEGIN;
CREATE ROLE emobility_backend NOLOGIN;
GRANT emobility_backend TO emobility;
GRANT USAGE ON SCHEMA public TO emobility_backend;
GRANT SELECT, INSERT, UPDATE ON public.users, public.wallets, public.ledger_transactions,
    public.hubs, public.vehicles, public.bookings, public.personal_evs,
    public.personal_reservations, public.dispatches TO emobility_backend;
COMMIT;
