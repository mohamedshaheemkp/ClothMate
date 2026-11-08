package com.clothmate.backend;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

@RestController
@RequestMapping("/api")
public class MeasureController {

    private static final ParameterizedTypeReference<Map<String, Object>> JSON_MAP =
        new ParameterizedTypeReference<>() {};
    private static final String DEMO_USER = "demo-user"; // TODO: use the logged-in user

    private final RestClient python;
    private final MeasurementStore store;

    public MeasureController(@Value("${clothmate.measure-url}") String url,
                             @Value("${clothmate.api-key:}") String apiKey,
                             MeasurementStore store) {
        RestClient.Builder builder = RestClient.builder().baseUrl(url);
        if (!apiKey.isBlank()) {
            builder.defaultHeader("X-API-Key", apiKey);
        }
        this.python = builder.build();
        this.store = store;
    }

    @GetMapping("/garments")
    public ResponseEntity<Object> garments() {
        return forwardGet("/v1/garments");
    }

    @GetMapping("/garments/{id}")
    public ResponseEntity<Object> garment(@PathVariable String id) {
        if (!id.matches("[a-z0-9_]{1,60}")) {
            return error(HttpStatus.BAD_REQUEST, "Bad garment id");
        }
        return forwardGet("/v1/garments/" + id);
    }

    @PostMapping("/measure")
    public ResponseEntity<Object> measure(@RequestBody Map<String, Object> body) {
        try {
            Map<String, Object> result = python.post().uri("/v1/measure")
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                .body(JSON_MAP);
            if (result == null) {
                return error(HttpStatus.BAD_GATEWAY, "Empty reply from the measurement service");
            }
            UUID sessionId = store.save(DEMO_USER, result);
            Map<String, Object> out = new LinkedHashMap<>(result);
            out.put("session_id", sessionId.toString());
            return ResponseEntity.ok(out);
        } catch (RestClientResponseException ex) {
            return relay(ex);
        } catch (RestClientException ex) {
            return error(HttpStatus.BAD_GATEWAY, "Measurement service is not reachable");
        }
    }

    @GetMapping("/sessions")
    public List<Map<String, Object>> sessions() {
        return store.recentSessions();
    }

    private ResponseEntity<Object> forwardGet(String path) {
        try {
            String json = python.get().uri(path).retrieve().body(String.class);
            return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(json);
        } catch (RestClientResponseException ex) {
            return relay(ex);
        } catch (RestClientException ex) {
            return error(HttpStatus.BAD_GATEWAY, "Measurement service is not reachable");
        }
    }

    /** Pass the Python service's own error message on (e.g. "Missing points"). */
    private ResponseEntity<Object> relay(RestClientResponseException ex) {
        int code = ex.getStatusCode().value();
        if (code == 401 || code == 403 || code == 503) {
            return error(HttpStatus.BAD_GATEWAY, "Measurement service is misconfigured");
        }
        return ResponseEntity.status(ex.getStatusCode())
            .contentType(MediaType.APPLICATION_JSON)
            .body(ex.getResponseBodyAsString());
    }

    private ResponseEntity<Object> error(HttpStatus status, String message) {
        return ResponseEntity.status(status).body(Map.of("detail", message));
    }
}