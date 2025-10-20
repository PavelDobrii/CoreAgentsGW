INSERT INTO route_drafts (id, user_id, city, language, duration_min, transport_mode, status, payload_json)
VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'Vilnius', 'en', 180, 'walking', 'draft', '{}'::jsonb)
ON CONFLICT DO NOTHING;
