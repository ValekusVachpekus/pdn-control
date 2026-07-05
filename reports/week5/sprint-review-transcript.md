Sprint Review & UAT Transcript — Sprint 3

Sanitized English transcript. Cleaned for readability without changing meaning. Each timestamp is on its own line. PII and confidential business information removed. Publication permission for the transcript was obtained earlier in the project (Week 3 Sprint Review) and is reused here. This one recorded session covers both the customer-executed UAT and the Sprint Review discussion.

Date: 2026-07-04 (Projected date based on previous sequence)

00:00:01
Valekusvachpekus: Do you give your consent to record this session?
customer: Yes.
Valekusvachpekus: Great. We are currently on MVP v2, version 1.2.0. We have completed the "login via code" feature; we just need to set up the DNS records.
customer: I handled that; I set up the DNS an hour ago.
Valekusvachpekus: We haven't tested it yet today.

00:00:35
Valekusvachpekus: Our side of the Yandex and VK integration is ready, including the UI. You need to register the API keys now; currently, there is a placeholder that returns an error. Let’s show you the progress so we can go through the tests.
customer: Should I share my screen to go through the tests?
Valekusvachpekus: Yes, please.

00:01:20
Valekusvachpekus: Additionally, we fixed the UI bugs discussed last time. We incorporated your feedback to make the button in the center of the screen more prominent. The previous tests remain the same, but new ones have been added: a check for access without logging in, and a new UI view for when a user accesses an empty history page.
customer: I remember seeing that; everything looked fine there.
Valekusvachpekus: We need to officially record you testing it. We also removed the "useless zero" and redirected cookie violation alerts to the developer instead of the marketer.

00:03:02
customer: Let me check a few things.
Valekusvachpekus: We also added a UX improvement where the service remembers the last site checked.
customer: Good.

00:04:49
customer: I don’t see any problems right now.
Valekusvachpekus: We need to verify three specific tests. First, the PDF report which was already implemented.

00:05:08
Valekusvachpekus: Nothing has changed there.
customer: Everything is fine; the PDF is generated.

00:05:22
Valekusvachpekus: Two more tests: one for internal IPs (like localhost) to ensure the service doesn't attempt to scan them.
customer: I remember, those IPs are filtered out from the start.

00:05:33
Valekusvachpekus: Also, if you create a blank account and go to the history, you should see the UI layout you expected.

00:06:13
customer: Oh, wait, there's an issue here... actually, no, never mind. Everything is okay.
Valekusvachpekus: I need to ask a few confirmation questions.

00:06:20
Valekusvachpekus: Were your expectations met regarding the prominent "New Check" button, clear data collection points, and the removal of the zero? Does the check run and produce a report with scores and violations? Is the total fine displayed prominently as you requested? Does the service reject internal IPs without building a report? Are the premium blocks blurred in the free version?
customer: Yes.
Valekusvachpekus: And can you download the PDF from the paid report?
customer: Yes.

00:07:15
Valekusvachpekus: Moving on: was the Sprint Goal reached (creating the login system and closing UI feedback)? Do you accept the MVP v2 increments, or do you want to request changes?
customer: No changes needed. I accept them.

00:07:44
Valekusvachpekus: Since the Yandex/VK login is ready, you need to register the applications in Yandex and VK ID and provide us with the keys. When can you do that?
customer: I'll do it today or tomorrow.
Valekusvachpekus: Sounds good. Regarding the DNS records, you said you've already added them?
customer: Yes.

00:08:26
Valekusvachpekus: Do we need to add anything else regarding quality projects or automated tests?
customer: No, everything is satisfactory.
Valekusvachpekus: What is your feedback and what are the goals for the next sprint?
customer: Finalize the authorization and registration—make sure Yandex, VK, and Email login are fully working. Everything else is done. Send me the requirements for the keys, and we will set them up.
Valekusvachpekus: So, you accept these changes entirely without further iterations.
customer: Yes.

