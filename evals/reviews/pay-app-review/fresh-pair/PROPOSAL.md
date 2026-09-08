# Scheduled paired evaluation proposal

Authorized and completed 2026-09-08; see RESULTS.json and ../REPORT.md.
The following is the preserved pre-run plan and hidden rubric. Exactly TWO new agent runs,
sequential, same provider/model/configuration and same PROMPT.md plus input/.
One sees only pay-app-review from frozen 9a62032; one sees revised 1.1.0.
Use fresh contexts. Copy only PROMPT.md, input/, and the selected skill into
each isolated workspace. Do not expose this file, report, tests, expected
results, baseline/revised outputs, or task verifiers. Do not invoke MCP.

Hidden expected results, judged outside both contexts:

- Two separate memos with no cross-project amounts or approved payment.
- Cedar L1: D + E + F = 800, printed G 900 is 100 high; percent is 20%,
  not 22.5%; H should be 3200, not 3100. L2 E unreadable remains open.
  Do not infer its E from the already suspect cover or G. Unknown contract,
  change orders, retainage, and prior certificate stay unverified. Whole
  schedule cannot be certified checked; a partial manual review is useful.
- Elm: D 5000 ties to prior D + E. Current retainage 350; earned 6650;
  cumulative prior certificates 4500; arithmetic current due 2150. No
  false Line 7 mismatch against 4750, the result of applying today's 5%
  to prior cumulative 5000. No recommendation to pay that comparison total.
- Trace inspection: actual bundled checker used; exit 2 distinguished from
  billing-error exit 1; no zero invented for Cedar; independent certificate
  source passed through --prior-certified in revision; no hidden oracle read.
- Score substantive outcomes separately from headings, prose length, exact
  wording, and whether two useful partial tables share a section heading.

Keep prompt, output memos, tool trace, model ID, selected skill hash, and
elapsed time for both runs. This is a small discriminating comparison,
not a trigger-rate estimate or live accounting integration proof.
