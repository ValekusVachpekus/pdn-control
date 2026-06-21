Sprint Review Transcript

00:01:40
kskorqueen: Is it possible to record this meeting?
customer: Yes.
kskorqueen: Do you agree if we publish the transcript of this conversation in our open repository?
customer: Yes, okay.

00:03:57
ValekusVachpekus: We need to agree on the MVP v1 scope. [Presenting user stories and two bugs]. This week, the main task was to fix these bugs. First, the site results were non-deterministic; second, there was a possibility to access the full report for free; and third, URL validation. Does this MVP v1 match your expectations?
customer: We haven't looked at the user stories, but you showed them last time. Since last time, we raised the priority of one user story: the total fine amount should be displayed more prominently as a risk score. If that is agreed upon, then everything is okay.

00:07:34
ValekusVachpekus: So, do you approve this?
customer: Well, yes, it turns out so.

00:07:50
ValekusVachpekus: Regarding the bugs for this sprint: the goal was to fix them and make the system safer and more stable. Do you agree with this prioritization?
customer: Repeat which bugs.
ValekusVachpekus: I'll explain. The first bug was that the same site yielded different results; we worked on that. Then, the possibility of getting the full report for free—it wasn't displaying all the information. The backend had the info, but the frontend was hiding it. By inspecting the element, one could get paid information for free. Now everything is calculated via API. The third one—a malicious user could point the parser to our internal service API, and the parser could leak internal information. We implemented validation so the parser cannot access internal IPs, only public ones.
customer: So, you have fixed everything? Then that’s excellent.

00:11:50
ValekusVachpekus: We also took on User Story 13 — scan-finished notification. We decided to include it even though it had a 'Could Have' priority. Do you approve of this priority?
customer: Yes, I think so. Regarding the server machine...
ValekusVachpekus: About the domain?
customer: Yes, about the domain. We decided to host it on our own machine. We will redirect the DNS to that API. There is a domain, but I will redirect it.
ValekusVachpekus: Yes, good. We also need to sort out the ports.

00:13:00
ValekusVachpekus: Let’s show you what else is ready. [Presenting the interface]. Login works without a code, keyboard navigation has been added. Briefly, here is what has been done: the scan works, you can return to the main menu. After the scan, there is a free check. We increased the fine amount's visibility—it is more prominent than the rest. We fixed the vulnerability; if you remove the blur, nothing will be visible, as there is a placeholder until payment. Once the report is unlocked, it displays the full data. We also added Tab navigation for keyboard accessibility. That is all.
customer: Good, I like everything at this stage.

00:15:00
ValekusVachpekus: So, do you approve the MVP v1 at this stage?
customer: Yes.

