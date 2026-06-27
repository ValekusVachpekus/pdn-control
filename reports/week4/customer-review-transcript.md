Sprint Review & UAT Transcript — Sprint 2

> Sanitized English transcript. Cleaned for readability without changing meaning.
> Each timestamp is on its own line. PII and confidential business information removed.
> Publication permission for the transcript was obtained earlier in the project (Week 3
> Sprint Review) and is reused here. This one recorded session covers both the
> customer-executed UAT and the Sprint Review discussion; exact UAT/Review timecodes are
> provided privately in the Moodle submission.

**Date:** 2026-06-27

00:00:10
ValekusVachpekus: Can we record this meeting?
customer: Yes.

00:00:30
ValekusVachpekus: Our Sprint Goal was to improve quality and deploy the service on your
infrastructure. We deployed it on your server and domain, issued a TLS certificate, and
prepared the quality requirements, quality requirement tests, CI, and Definition of Done.
We also made the checks more deterministic by removing the AI from places where it is not
needed — for example, we now detect the server IP and country with GeoIP instead of the
LLM. The website is available at the production domain. Now we need to pass UAT.
[Describes the UAT scenarios.]

customer: Okay, let's start. [Starts screen sharing and begins testing the website.]

00:04:00
customer: [Starts a check without registering.] The site did not allow the check without
registration, but the loading screen still opened.
ValekusVachpekus: That is a bug, we will fix it. To start a check you need to register on
the website.
customer: Okay. Let's note that down.

00:06:00
customer: [On the empty history screen.] There is no button to go back to the main page.
ValekusVachpekus: It is the "New check" button.
customer: Make it more intuitive. [Continues testing.]

00:11:27
customer: What does this zero mean?
ValekusVachpekus: It is a zero fine. The service could not check some information about the
personal data of the website's owners.
customer: Remove this zero, it is useless here.

00:12:30
customer: Why are these "personal data collection points" empty?
ValekusVachpekus: Are they on the main page?
customer: The site found the forms correctly, on the main page.
ValekusVachpekus: They appear empty because the forms are on the main page.
customer: Make it more intuitive — write "Main page" or something similar.

00:13:30
customer: Why is the cookie violation addressed to the Marketer?
ValekusVachpekus: I understand, we will address it to the Developer.
customer: Yes, do that.

00:15:00
ValekusVachpekus: Were you able to run a check and get a report?
customer: Yes.

00:15:30
ValekusVachpekus: We need to verify the SSRF validation scenario.
customer: [Tests it.]
ValekusVachpekus: Do you confirm that the service correctly rejects invalid and internal
addresses?
customer: Yes.

00:16:30
ValekusVachpekus: Is the difference between the free and the paid report clear, and does the
full report open after payment?
customer: Yes.
ValekusVachpekus: Was the PDF report downloaded, and does it contain all the information?
customer: Yes.

00:17:30
ValekusVachpekus: Did we reach the Sprint Goal — quality improvement and deployment on your
infrastructure?
customer: Yes.
ValekusVachpekus: Do you accept the Sprint increment?
customer: Yes.

00:18:00
ValekusVachpekus: Do you have any more feedback?
customer: No, only what we have already discussed.
ValekusVachpekus: Is your feedback captured correctly?
customer: Yes.
ValekusVachpekus: Do we need to change anything in the CI, the quality requirements, or the
quality requirement tests?
customer: No, that is enough.
ValekusVachpekus: What are the main risks or mistakes you spotted?
customer: I have not found any mistakes, only the ones we already discussed.

00:19:00
ValekusVachpekus: Is everything fine with the migration to your infrastructure and domain?
customer: Yes, everything is fine.
ValekusVachpekus: Do you accept the increment?
customer: Yes.

00:19:40
azenlrd: Can we use a third-party email provider so that we do not have to set up a local
SMTP server on your machine?
customer: Yes, you can.
azenlrd: Will you register it for us?
customer: Send me what needs to be added and I will add it.

00:20:10
ValekusVachpekus: That is all, have a good day!
customer: Goodbye, have a good day!
