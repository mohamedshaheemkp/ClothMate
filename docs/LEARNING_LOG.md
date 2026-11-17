# Learning log — things I must be able to explain to the company
Format: concept — one-line plain explanation — where it is in the code

- Homography — maps a tilted photo plane to a flat real-world plane using 4 known points — python core/geometry
- Hartley normalization — rescales points before computing homography so the math is stable — core
- REST API — frontend asks backend using URLs + JSON — Spring controllers
- Ground Truth Validation — testing software measurements against a physical tape measure before training ML models — testing/accuracy
- Keypoint Detection — ML task predicting exact coordinates of landmark points (shoulders, collar, hem) — future CV pipeline
- TestBed — Angular testing utility that creates an isolated mock browser environment to instantiate components without a real browser — clothmate-web/src/app/app.spec.ts

## Questions I should be able to answer
1. Why does the bank card give scale? What goes wrong if the card is tilted?
2. Why Spring between Angular and Python? Why not call Python directly?
3. Why is the API key checked? Where is it stored?
4. Why can accuracy be off by 2 cm (shoulder)? What are the error sources?
5. What is a Docker volume and why does the DB need one?
