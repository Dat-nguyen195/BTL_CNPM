BEGIN;

CREATE TABLE public.users (
    user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    mssv text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    full_name text NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL DEFAULT 'STUDENT' CHECK (role IN ('STUDENT', 'OPERATOR', 'ADMIN'))
);

CREATE TABLE public.wallets (
    user_id uuid PRIMARY KEY REFERENCES public.users,
    balance integer NOT NULL DEFAULT 0,
    held_deposit integer NOT NULL DEFAULT 0,
    debt integer NOT NULL DEFAULT 0
);

CREATE TABLE public.ledger_transactions (
    tx_id text PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users,
    tx_type text NOT NULL,
    amount integer NOT NULL,
    balance_after integer NOT NULL,
    held_after integer NOT NULL,
    debt_after integer NOT NULL,
    booking_id text,
    note text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.hubs (
    hub_id text PRIMARY KEY,
    name text NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    total_slots integer NOT NULL,
    available_slots integer NOT NULL,
    ports_total integer NOT NULL,
    ports_available integer NOT NULL,
    destination_holds integer NOT NULL DEFAULT 0
);

CREATE TABLE public.vehicles (
    vehicle_id text PRIMARY KEY,
    hub_id text NOT NULL REFERENCES public.hubs,
    type text NOT NULL,
    battery_soc double precision NOT NULL CHECK (battery_soc BETWEEN 0 AND 100),
    status text NOT NULL DEFAULT 'AVAILABLE'
);

CREATE TABLE public.bookings (
    booking_id text PRIMARY KEY,
    student_id uuid NOT NULL REFERENCES public.users,
    hub_id text NOT NULL REFERENCES public.hubs,
    vehicle_id text NOT NULL REFERENCES public.vehicles,
    destination_hub_id text REFERENCES public.hubs,
    destination_held boolean NOT NULL DEFAULT false,
    voucher_code text,
    pin_code text NOT NULL,
    deposit_held integer NOT NULL,
    status text NOT NULL DEFAULT 'RESERVED',
    extra_free_minutes integer NOT NULL DEFAULT 0,
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    pickup_time timestamptz,
    return_time timestamptz,
    invoice jsonb
);

CREATE TABLE public.personal_evs (
    ev_id text PRIMARY KEY,
    owner_id uuid NOT NULL REFERENCES public.users,
    plate text NOT NULL UNIQUE,
    type text NOT NULL,
    brand text NOT NULL,
    battery_kwh double precision NOT NULL
);

CREATE TABLE public.personal_reservations (
    reservation_id text PRIMARY KEY,
    owner_id uuid NOT NULL REFERENCES public.users,
    ev_id text NOT NULL REFERENCES public.personal_evs,
    hub_id text NOT NULL REFERENCES public.hubs,
    request_charging boolean NOT NULL,
    charging_allocated boolean NOT NULL DEFAULT false,
    current_soc double precision NOT NULL,
    arrival_deadline timestamptz NOT NULL,
    status text NOT NULL DEFAULT 'RESERVED',
    check_in_time timestamptz,
    check_out_time timestamptz,
    invoice jsonb
);

CREATE TABLE public.dispatches (
    dispatch_id text PRIMARY KEY,
    source_hub_id text NOT NULL REFERENCES public.hubs,
    destination_hub_id text NOT NULL REFERENCES public.hubs,
    vehicle_ids text[] NOT NULL,
    reason text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    received_at timestamptz
);

-- Supabase grants public-schema access to client roles by default.
-- Only the trusted backend may use these application tables.
REVOKE ALL ON public.users, public.wallets, public.ledger_transactions,
    public.hubs, public.vehicles, public.bookings, public.personal_evs,
    public.personal_reservations, public.dispatches FROM PUBLIC;
DO $roles$
DECLARE
    client_role text;
BEGIN
    FOR client_role IN SELECT rolname FROM pg_roles
                      WHERE rolname IN ('anon', 'authenticated') LOOP
        EXECUTE format('REVOKE ALL ON public.users, public.wallets, public.ledger_transactions, public.hubs, public.vehicles, public.bookings, public.personal_evs, public.personal_reservations, public.dispatches FROM %I', client_role);
    END LOOP;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'service_role') THEN
        GRANT USAGE ON SCHEMA public TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.users, public.wallets,
            public.ledger_transactions, public.hubs, public.vehicles, public.bookings,
            public.personal_evs, public.personal_reservations, public.dispatches TO service_role;
    END IF;
END
$roles$;

COMMIT;
