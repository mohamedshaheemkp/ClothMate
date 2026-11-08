package com.clothmate.backend;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MeasurementStore {

    private final JdbcTemplate jdbc;

    public MeasurementStore(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Transactional
    public UUID save(String userRef, Map<String, Object> result) {
        UUID sessionId = jdbc.queryForObject(
            "INSERT INTO measurement_session (user_ref, garment_id, fit, method) "
                + "VALUES (?, ?, ?, ?) RETURNING id",
            UUID.class,
            userRef, text(result.get("garment_id")), text(result.get("fit")), text(result.get("method")));

        List<?> rows = (List<?>) result.get("measurements");
        for (Object item : rows) {
            Map<?, ?> row = (Map<?, ?>) item;
            jdbc.update(
                "INSERT INTO measurement "
                    + "(session_id, name, flat_cm, garment_circumference_cm, estimated_body_cm) "
                    + "VALUES (?, ?, ?, ?, ?)",
                sessionId,
                text(row.get("name")),
                number(row.get("flat_cm")),
                number(row.get("garment_circumference_cm")),
                number(row.get("estimated_body_cm")));
        }
        return sessionId;
    }

    public List<Map<String, Object>> recentSessions() {
        return jdbc.queryForList(
            "SELECT id::text AS id, created_at::text AS created_at, garment_id, fit, method "
                + "FROM measurement_session ORDER BY created_at DESC LIMIT 20");
    }

    private static String text(Object value) {
        return value == null ? null : value.toString();
    }

    private static BigDecimal number(Object value) {
        return value == null ? null : new BigDecimal(value.toString());
    }
}