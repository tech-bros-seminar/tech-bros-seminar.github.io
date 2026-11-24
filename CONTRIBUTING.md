# Publishing an improved solution

Use this workflow for a new proof of a Kourovka or Dniester problem already covered by a seminar manuscript. A shorter proof, a correction, a weaker hypothesis or a larger solved case can all justify a revision. Explain precisely which result or proof step improves and which assumptions or open cases remain.

1. **Find the predecessor.** Read the existing paper, its review record and any later versions. Record the comparison and the new argument in a fresh research run. Credit the earlier authors and any new contributors. Recheck the changed steps and all conclusions that depend on them.
2. **Prepare a separate release.** Keep the previous catalogue entry, public page and files. Add the new PDF, TeX source and review record under `content/files/<problem-slug>/` with new version-specific filenames. Recheck Lean and human review claims for this exact version. Record public prompt links supplied for this revision and the actual release authorization.
3. **Update the website in the same round.** In `content/catalog.json`, append the complete manuscript record with the existing `problem_slug`, a fresh publication slug and the next available integer version for the manuscript. Set `revises` to the immediate predecessor's **publication slug** and `revision_summary` to a brief, specific account of the change. Supply the new file paths and dates. Refresh the catalogue's `updated_at` and the problem's status if its full-solution or review status changed.

For example, an agent shortening a proof could add these fields to its new `preprints` record (illustrative values):

```json
{
  "slug": "example-proof-v2",
  "version": "2",
  "revises": "example-proof-v1",
  "revision_summary": "The new proof replaces the case split in Lemma 3 with a direct argument."
}
```

An AI-generated revision belongs in `preprints` with `status: review_pending`, even if the earlier paper received human review. Use `solutions` for a version the named human reviewers have checked. Its `based_on` field credits the AI manuscript used for the human exposition. A stronger partial result retains `scope: partial_result`. A withdrawn version stays accessible with its reason and links to subsequent revisions.

Run these checks from the website repository:

```sh
python -B -m unittest discover -s tests -v
python -B scripts/build.py
python -B scripts/check_site.py
```

Publish the catalogue and new files together. If another contributor published first, reread the catalogue and reconcile version numbers and links before retrying. Follow the Pages deployment for the published commit. Open the new paper and its downloads, follow the link back to the earlier version, and record the public URL and commit in the research repository. If publication is blocked, record the pending step so the next agent can resume.
