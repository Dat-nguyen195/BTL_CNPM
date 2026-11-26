BEGIN;

INSERT INTO public.hubs
    (hub_id, name, latitude, longitude, total_slots, available_slots, ports_total, ports_available)
VALUES
    ('HUB-001', 'Bách Khoa cơ sở Dĩ An', 10.8799, 106.8068, 12, 9, 4, 4),
    ('HUB-002', 'Ga Metro Suối Tiên', 10.8790, 106.8147, 12, 10, 4, 4),
    ('HUB-003', 'Ký túc xá khu A', 10.8780, 106.8070, 12, 11, 4, 4),
    ('HUB-004', 'Ký túc xá khu B', 10.8942, 106.8005, 12, 10, 4, 4);

INSERT INTO public.vehicles (vehicle_id, hub_id, type, battery_soc)
VALUES
    ('EV-001', 'HUB-001', 'scooter', 83),
    ('EV-002', 'HUB-001', 'bike', 46),
    ('EV-003', 'HUB-001', 'scooter', 17),
    ('EV-004', 'HUB-002', 'scooter', 75),
    ('EV-005', 'HUB-002', 'bike', 55),
    ('EV-006', 'HUB-003', 'bike', 60),
    ('EV-007', 'HUB-004', 'scooter', 69),
    ('EV-008', 'HUB-004', 'bike', 34);

COMMIT;
