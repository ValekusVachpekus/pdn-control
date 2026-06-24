## Customer Feedback Response

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| The "Total Fine" amount should be more prominent as a risk score. | #78 | Done | Increased UI contrast, font size, and visual weight of the fine amount in the MVP v1 report view. |
| Audit results were non-deterministic (different data for the same site). | #34 | Done | Fixed the backend parsing logic to ensure consistent results across multiple scans of the same URL. |
| Security flaw: Full report data was accessible for free via browser "Inspect Element" (Blur bypass). | #54 | Done | Moved the data-gating logic to the API. Sensitive data is no longer sent to the frontend until payment is confirmed. |
| Security risk: Parser could be pointed to internal APIs (SSRF vulnerability). | #57 | Done | Implemented strict server-side URL validation to prevent the scanner from accessing internal or private IP ranges. |
| Request for scan completion notifications (US-13). | #13 | Done | Implemented automated notifications once the audit is finished, despite its initial low priority. |
| Requirement to host the service on the customer's infrastructure and redirect DNS. | #110 | To Do | Added a new task to prepare deployment configurations and assist the customer with DNS migration to their own server. |
