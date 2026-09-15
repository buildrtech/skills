# Independent workforce planning review

Seven deterministic calculator tests pass: proposal/demand reconciliation, existing overload preservation, repeated fills, demand overfill, duplicate identities, unknown/week-mismatched references, invalid/missing hours and exact decimal arithmetic. All source skills and marketplace validate.

Fresh offline smoke comparisons used Claude Code, the same project-default model and reasoning settings per run. Two cases were tested without the skill and with the initial skill; each skill case was then repeated after clarifying unknown percentage denominators and decision authority. Raw traces are kept outside the repository in the root BB thread storage.

Coverage case: all variants calculate the central 20-hour proposal/4-hour residual. The baseline incorrectly suggests moving Cam's existing overallocated hours to the library would eliminate the overload. Skill-guided responses preserve that overload, but include overbroad narrative statements. The revised response says no one exceeds capacity despite reporting Cam's existing overload. These are qualitative observations, not a numeric quality score.

Missing-data case: the baseline mistakes assigned percentages for supply and offers an unsupported conditional gap. The first skill run still infers unused percentages and absence of overload despite unknown denominators/absences. After an explicit rule was added, the repeated response leaves all capacity/gap numbers unknown and requests the necessary data.

Evidence limitation: skill-guided responses claim calculator execution without a corresponding Bash/tool execution event in the captured BB events. This is not accepted as proof that execution occurred. Final wording now requires a written user-data ledger and observed command output; this final wording change has not received another fresh-model comparison. Deterministic tests did execute the actual calculator. The coverage task overlaps the shipped example, so it is a smoke test, not held-out evidence of generalization. No effectiveness or statistical triggering claim is made.

No external services or account integration are part of the skill. No closeout skill was added.
