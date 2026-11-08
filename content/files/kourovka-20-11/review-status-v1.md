# Version 1: review and release status

**Publication type:** AI generated. **Mathematical status:** candidate solution, review pending.

The manuscript proposes affirmative answers to all four parts of Kourovka 20.11, including infinitely generated initial subgroups. It is an explicit deduction from Jaikin-Zapirain's results and standard free-group facts. It is not a claim of a new subgroup-rigidity theorem or established research priority.

## Actual review

- The authoring AI checked the original hypotheses, all four conclusions, rank zero and one, the arbitrary-intersection step, and applicability of the external results.
- A separate Codex agent, `audit_minrank`, reviewed the archived candidate on 6 November 2026 and found no mathematical gap, conditional on the cited theorems. No repair was needed.
- The manuscript is a typeset exposition of the audited argument, with the same hypotheses, proof stages, and dependencies. The authoring agent checked correspondence between this exposition and the archived argument.
- Human seminar review remains pending. No human reviewers or acceptance are claimed.
- The external subgroup-rigidity proof was not independently re-proved. Takahasi's result was checked in Jaikin-Zapirain's Proposition 2.3, not in the original 1951 article.

## Lean

No Lean executable was available (`command -v lean` found none). No Lean formalization or formal mathematical verification is supplied. The PDF build and repository tests check presentation and software, not theorem truth.

## Sources and attribution

Jaikin-Zapirain, arXiv:2403.09515v2, Corollaries 1.2 and 1.5 and Proposition 2.3, are the essential external inputs. The finitely generated initial-subgroup case is already in his work. Kourovka 19.103 also records arbitrary-intersection closure for inert subgroups. The November 2026 entry for 20.11 is unmarked, but that does not establish that the conclusion was still unknown or that this deduction has priority.

https://arxiv.org/pdf/2403.09515v2

https://kourovkanotebookorg.wordpress.com/wp-content/uploads/2026/11/21tkt.pdf

## Prompts and conversation

No public conversation link was supplied for this version. No private transcript is included.

## Separate audit record

The following is the separate review, preserved with its actual version and scope. References to the private research repository are provenance identifiers; access to that repository is not required to read the complete public manuscript.

# Separate AI audit of the Kourovka 20.11 candidate

Date: 6 November 2026. Reviewer: separate Codex agent `audit_minrank`. This is an AI audit, not human acceptance or formal verification.

## Version reviewed

- Repository: `thomasl2/math-research-lab`.
- Commit: `faaf280676b221413f125d615ef672f8cfb832c2`.
- Report: `problems/kourovka-20-11/runs/research-20261106-minrank-rdelaby-7e2c91.md`.
- Claim: `research-20261106-minrank-rdelaby-7e2c91-C1`.
- Report SHA-256: `6265b3f638f4a937ade8d235756164bcbe0b4d9f7dd14fb0d9d97c5c379629c1`.
- GitHub blob: `18823cb16a0f6e4d6c08a2cc4df71cf7fe1cacd0`.

The reviewer fetched the report at the pinned commit and verified that its text exactly equals the local report inspected.

## Verdict

**No mathematical gap was found in the stated deduction.** Assuming the cited Jaikin-Zapirain results and Takahasi finiteness theorem, the argument establishes all four assertions for the full hypotheses of Problem 20.11, including an infinitely generated initial subgroup and an ambient free group of arbitrary rank. The extra assertion that the minimum-rank overgroups form a finite sublattice also follows.

No repair is proposed or needed for the proof as written. The most important qualification concerns attribution and novelty, not mathematical scope: this is a short consequence of existing deep results and a standard arbitrary-intersection principle. This audit does not establish that the deduction is new to the literature, or that the problem was genuinely unresolved immediately before this conversation.

## Audit of the mathematical steps

1. **Exact target.** The source entry asks for a greatest overgroup, pairwise subgroup joins of the same minimum rank, a least overgroup, and pairwise intersections of the same rank. The candidate preserves each assertion and does not add finite generation of the initial subgroup. Every subgroup of the ambient free group is free, so replacing the source's phrase that both groups are free by the assumption that the ambient group is free does not weaken the hypotheses.

2. **Existence of the minimum.** The family of finite-rank overgroups is nonempty by hypothesis; its ranks form a nonempty subset of the nonnegative integers. The minimum is attained. This justifies choosing a member G0 of rank r. The case r = 0 is correctly handled separately: the only rank-zero subgroup is the trivial subgroup, forcing the initial subgroup to be trivial as well.

3. **Compression in the finite-rank join.** For rank-r overgroups A and B, the group L generated by A and B is finitely generated. Any finitely generated subgroup between A and L also contains the initial subgroup F and consequently has rank at least r. Therefore A is compressed in L. Corollary 1.2 applies without any assumption on F. Inertness bounds the rank of A intersect B by r; containment of F gives the reverse bound. Finite generation of the intersection is obtained before minimality of r is invoked. The induction to any nonempty finite intersection is valid.

4. **Right cosets.** In the Schreier graph on cosets Cw, equality Cwi = Cwj is equivalent to wi wj^(-1) belonging to C. This is exactly the difference used in the candidate. Thus each chosen witness subgroup separates the intended pair of vertices. No reversal of the coset criterion or conjugation error occurs.

5. **Finite subgraph embedding.** Only finitely many vertex pairs occur in a finite subgraph Q. Intersecting G0 with the finitely many witness overgroups produces a member B of rank r. The canonical map from the C-Schreier graph to the B-Schreier graph is injective on Q's vertices by construction. It is also injective on positively oriented labelled edges, because each vertex of a Schreier graph has a unique outgoing edge with each basis label. This handles loops and parallel edges; forgetting labels too early would have been unsafe, but the candidate retains them.

6. **Rank bound for the full intersection.** The inclusion of a subgraph in a graph injects its first homology, because graphs have no two-dimensional boundaries. The first Betti number of any finite connected Q is therefore at most r. An infinite connected graph has more than r independent cycles only if some finite connected subgraph already has more than r independent cycles. The candidate's spanning-tree explanation establishes this fact. Hence the subgroup C represented by the full Schreier graph has free rank at most r, so it is finitely generated. Because it contains F, it has rank at least r. This argument does not assume that the family of overgroups is finite or countable: only finitely many witnesses are selected for each Q.

7. **Least member and reduction.** The intersection C is contained in every rank-r overgroup, and it itself has rank r. It is therefore the least member, not just a member minimal under inclusion. The equality between the rank-r overgroups of F and those of C is correct in both directions. The minimum overgroup rank of C remains r.

8. **Application of Corollary 1.5.** The candidate applies the corollary to C, which has now been proved finitely generated, inside the finite-rank join L = <A,B>. The minimum rank in this smaller ambient group is still r: A gives an overgroup of rank r, and a smaller one would contain F. Thus A and B lie in the corollary's critical family, and their ordinary subgroup join has rank r. The dependency is not circular and does not silently apply the corollary to the original possibly infinitely generated F.

9. **Algebraic overgroups.** A proper free factor of a finite-rank free group G has smaller rank than G. If such a factor contained C, it would also contain F, contradicting the minimum r. Consequently each rank-r overgroup is an algebraic extension of C. Takahasi finiteness applies. The optional reduction of the ambient group to finite rank is correct: choose a finite-rank free factor P containing C; the free-product subgroup theorem makes G intersect P a free factor of G, so algebraicity forces G to lie in P.

10. **Greatest member and finite lattice.** After finiteness has been proved, a repeated binary join produces a rank-r member containing every member of the family. This is a greatest member. Binary intersections and joins coincide with those in the ambient subgroup lattice. The claim is about a sublattice with binary operations; it does not claim that the empty join or empty meet agrees with those of the entire subgroup lattice.

The cyclic case r = 1 introduces no exceptional failure. Its Schreier graphs obey the same argument, and proper free factors of a rank-one group are trivial. Infinite rank of the ambient H is isolated from the applications requiring finite-rank groups.

## Sources checked and limits

The reviewer inspected the local November 2026 Kourovka text at Problem 20.11 and the local arXiv:2403.09515v2 text at Corollaries 1.2 and 1.5, Proposition 2.3, and Section 3.7. The statements match the uses in the candidate. The source PDF hashes are:

- Kourovka: `45420f88b0246f2558b581bf813184275972de2fd0a7c87cf4942f777c9d833d`.
- Jaikin-Zapirain: `256810e24a25e4fd1403358a7ecac8c4cc39f1d281acbd90da2067ee14215ce1`.

The full proof of Jaikin-Zapirain's deep subgroup-rigidity theorem was not independently re-proved. The original Takahasi article was not inspected; its theorem was checked in the cited Proposition 2.3. No Lean proof checker or other formal proof system was run. No finite computation can certify the universal conclusion here, and none was treated as doing so.

Primary source links:

- https://kourovkanotebookorg.wordpress.com/wp-content/uploads/2026/11/21tkt.pdf
- https://arxiv.org/pdf/2403.09515v2

## Attribution, novelty, and recommended public wording

For a finitely generated initial subgroup, the key intersection and join result is explicitly Jaikin-Zapirain's Corollary 1.5. The least and greatest members then follow from finiteness of algebraic extensions. The arbitrary-intersection argument in this candidate is an explicit proof of a standard rank-compactness principle. Indeed, Kourovka Problem 19.103 already records that arbitrary intersections of inert subgroups are known to be inert. Combining that fact with Corollary 1.2 also gives the finitely generated least overgroup C directly.

The November 2026 entry for Problem 20.11 is unmarked and contains no solution comment. A targeted web search for the identifier and minimum-rank overgroups did not locate a separately labelled resolution of all four parts. This is limited negative-search evidence and does not establish priority. The conclusion may already be regarded as an implicit consequence of the existing theorem. The user-facing description should therefore be an **explicit deduction of all four assertions of an unmarked Kourovka problem from existing results**, with the full dependence on Jaikin-Zapirain and the absence of a novelty claim stated prominently.

Recommended next step: human mathematical review of the exact deduction and its attribution. The project should retain provisional candidate status. This AI audit supplies a separate check of the displayed proof; it is neither human acceptance nor editorial confirmation that Problem 20.11 is solved.
