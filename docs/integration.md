# Integration guide (Task 3)

## Architecture

```
Browser (React or Angular page)
  - user picks garment, loads the photo (stays in the browser)
  - clicks the 4 reference corners + garment points on a <canvas>
  - sends only NUMBERS (pixel positions) as JSON
        |
        v
Website backend (FastAPI  OR  Spring Boot)      <- login, roles, PostgreSQL writes
        |  adds API key, forwards JSON
        v
ClothMate measurement service (this repo, FastAPI)   <- pure maths, stateless
        |  returns measurements JSON
        v
Website backend saves to PostgreSQL, returns result -> shown in a popup/modal
```

Why this shape
- Streamlit is not needed: React/Angular draw the click screen; the service only does maths.
- Photos never leave the browser: no upload risk, no storage of private images (important for innerwear).
- One service, two frontends: React+FastAPI and Angular+Spring Boot call the same API.
- Only the website backend talks to PostgreSQL (one writer, one set of permissions).

The "iframe" quick option (embedding a Streamlit page) is not part of this design.

## API contract

`GET /v1/garments` -> list of garment types.
`GET /v1/garments/{id}` -> ordered `points` (name + on-screen instruction + required flag).

`POST /v1/measure`
```json
{
  "garment_id": "mens_tshirt",
  "fit": "regular",
  "reference": "card",
  "user_role": "customer",
  "card":   {"top_left": {"x":100,"y":100}, "top_right": {"x":400,"y":100},
             "bottom_right": {"x":400,"y":289}, "bottom_left": {"x":100,"y":289}},
  "points": {"shoulder_left": {"x":500,"y":300}, "...": {"x":0,"y":0}}
}
```
Coordinates are in ORIGINAL photo pixels (not the shrunk canvas size).
The card's "top" edge is its LONG edge. Errors come back as HTTP 422 with a readable message.
Response: `measurements[]` (flat_cm, garment_circumference_cm, ease_cm, estimated_body_cm), `warnings[]`.

## Frontend: the click screen (React sketch, untested)

```jsx
// Convert a click on the shrunk canvas into ORIGINAL photo pixels
function toImagePixels(evt, canvas, img) {
  const r = canvas.getBoundingClientRect();
  return {
    x: (evt.clientX - r.left) * (img.naturalWidth  / r.width),
    y: (evt.clientY - r.top)  * (img.naturalHeight / r.height),
  };
}
// Flow: step 0-3 = card corners (TL, TR, BR, BL), then one click per garment point
// in the order returned by GET /v1/garments/{id}; "Skip" for points with required:false.
// Then: fetch('/api/measure', {method:'POST', headers:{'Content-Type':'application/json'},
//        body: JSON.stringify({garment_id, fit, reference, card, points})})
// Show the result and warnings inside a modal (<dialog>) on the page.
```
Angular: same flow in a component; use `HttpClient.post<MeasureResponse>('/api/measure', body)`.
Call YOUR website backend (same origin, session/JWT login), never the measurement service
directly from the browser, so the API key never reaches the browser.

## Spring Boot proxy (sketch, untested)

```java
@RestController @RequestMapping("/api")
class MeasureController {
  private final WebClient client; // baseUrl = measurement service, header X-API-Key from env/secret store
  MeasureController(WebClient.Builder b, @Value("${clothmate.url}") String url,
                    @Value("${clothmate.key}") String key) {
    this.client = b.baseUrl(url).defaultHeader("X-API-Key", key).build();
  }
  @PostMapping("/measure")
  Mono<String> measure(@RequestBody String body, Authentication auth) {
    return client.post().uri("/v1/measure").contentType(MediaType.APPLICATION_JSON)
        .bodyValue(body).retrieve().bodyToMono(String.class)
        .doOnNext(json -> repository.saveSession(auth.getName(), json)); // PostgreSQL via JPA
  }
}
```
If the website backend is FastAPI instead: import `measure_garment` directly, or mount the
router, and replace `require_api_key` with the site's own JWT dependency.

## Security checklist (what is in the code vs. what you still must do)

In the code now: strict input validation (types, ranges, NaN/inf rejected, unknown fields rejected),
garment ids restricted to `[a-z0-9_]`, 100 KB body limit, API-key check with constant-time compare,
CORS closed unless configured, no internal errors leaked, security headers, no photos handled.

Still to do before production: HTTPS only, rate limiting at the gateway, real login (JWT) instead
of a shared key, secrets in a vault/env (never in git), proxy-level body limit (the header check
alone can be bypassed with chunked requests), Docker image + CI running pytest, dependency scanning,
data-retention and privacy policy, ease values signed off by a tailor.
