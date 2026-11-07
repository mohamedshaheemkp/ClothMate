CREATE TABLE measurement_session (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at   timestamptz NOT NULL DEFAULT now(),
    user_ref     text NOT NULL,
    user_role    text CHECK (user_role IN ('customer', 'tailor', 'staff')),
    garment_id   text NOT NULL,
    fit          text NOT NULL CHECK (fit IN ('slim', 'regular', 'loose')),
    method       text NOT NULL CHECK (method IN ('scale', 'homography'))
);

CREATE TABLE measurement (
    id                        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id                uuid NOT NULL REFERENCES measurement_session(id) ON DELETE CASCADE,
    name                      text NOT NULL,
    flat_cm                   numeric(6,1) NOT NULL,
    garment_circumference_cm  numeric(6,1),
    ease_cm                   numeric(5,1),
    estimated_body_cm         numeric(6,1),
    UNIQUE (session_id, name)
);

CREATE INDEX idx_session_user ON measurement_session (user_ref, created_at DESC);
CREATE INDEX idx_measurement_session ON measurement (session_id);