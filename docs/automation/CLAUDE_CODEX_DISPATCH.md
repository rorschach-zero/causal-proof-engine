# Claude ↔ Codex review dispatch

Status: **proposed, disabled until merged and configured**. No trading or model execution is enabled by this change.

## What it does

When Codex submits a review on a `claude/*` pull request in this repository, the workflow sends a **single notification** to an existing Claude Code Routine via Anthropic's official `/fire` endpoint. The payload carries only the PR number, review ID and commit SHA. It does not include GitHub comment text or run PR code.

The Claude routine must already be configured to fetch PR reviews, deduplicate reviewed IDs, obey a three-round issue limit, and stop without committing when no new actionable finding exists. Keep the routine's daily scheduled trigger as an independent fallback.

GitHub's native routine trigger covers pull-request and release events, **not PR review comments**. This bridge uses the `pull_request_review.submitted` event, which groups multiple inline comments into one review and avoids firing once for every finding.

## Set up (owner only)

1. Edit **CPE — Autonomous Scientific Review** at https://claude.ai/code/routines.
2. In *Select a trigger*, keep the daily schedule and choose **Add another trigger → API**. Generate a trigger token and copy the exact `/fire` URL. **Never paste the token into chat, comments, commits or workflow files.**
3. In the repository's GitHub Actions secrets at https://github.com/rorschach-zero/causal-proof-engine/settings/secrets/actions create:
   - `CPE_CLAUDE_ROUTINE_URL` — complete Anthropic-generated HTTPS routine `/fire` URL.
   - `CPE_CLAUDE_ROUTINE_TOKEN` — generated bearer token.
4. Review and merge this workflow PR only after its security review. A workflow must exist on the default branch for review webhooks to invoke it.
5. Test on a **documentation-only Claude branch PR**. Request Codex review and check the GitHub Actions run plus the Claude Routine run history. Verify that no branch is merged and no duplicate review ID is processed.
6. Rotate/delete the Anthropic token or disable this GitHub Actions workflow to stop dispatch immediately.

## Boundaries

- Allows only Codex reviews for Claude-authored branch names, never PR code execution.
- Uses minimal GitHub permissions; does not expose the Anthropic token in logs.
- Uses only the official Claude Code Routine API and the user's existing routine entitlement. Each triggered run counts against its usage limits; extra usage may incur charges if enabled.
- This is a coordination mechanism, **not** a scientific guarantee. Codex automatic code review does not replace an independent high-effort scientific audit.
- A daily fallback still handles comments not included in a submitted review and any webhook delivery loss.
- No automatic merges, broker access, trading orders or risk-rule modifications.

## Operational checks

Monitor https://github.com/rorschach-zero/causal-proof-engine/actions and https://claude.ai/code/routines. If repeated runs, unexpected costs or permission errors appear, disable the workflow and investigate before resuming.
