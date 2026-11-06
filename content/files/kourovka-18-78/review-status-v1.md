# Review and publication status

**Status: Proposed solution — review pending.**

**Manuscript:** *Simple twisted group algebras over arbitrary fields*  
**Problem:** Kourovka Notebook 18.78  
**Manuscript date:** 26 October 2026  
**This record:** 6 November 2026  
**Release:** Version 1; original LaTeX source and a 10-page compiled PDF.

## What is being claimed

The manuscript proposes an affirmative answer to Problem 18.78: if a finite group admits a simple twisted group algebra over an arbitrary field, then the group is soluble. The conclusion in `thm:main` concerns simplicity as a ring; it does not assume that the algebra is central simple over the specified field.

Its principal character-theoretic assertion, `thm:ordinary`, allows group automorphisms and cyclotomic Galois automorphisms to act together on irreducible characters above a faithful central character. The proposed argument combines an affine classification, a simultaneous ordinary/Brauer minimal-counterexample proof, and reductions covering fields of both zero and positive characteristic.

This entry records a proposed complete argument. It does not record an accepted resolution of the problem.

## Audits completed for this release

Two separate AI agents conducted bounded independent audits of complementary parts of this exact manuscript. Both reported **no decisive flaw identified within the scope examined**. That finding describes the outcome of these checks; it is not a guarantee of correctness.

**Character-theoretic core.** The first audit examined `lemma:affine-radical`, `thm:affine`, `lemma:character-cover`, and the joint proof in `sec:character-transitivity`. It checked the affine fixed-point counts and normalizer argument, the universal-central-extension construction and its paired-action equivariance, the lexicographic minimality reductions, the soluble inertia-group step, prime support, layer elimination, and the final passage to a smaller Brauer configuration. The classification and Schur-multiplier inputs were compared with the cited sources. No decisive defect was found in these steps.

**Galois stability and field reductions.** The second audit examined the class of groups whose soluble-radical quotient is a product of copies of `GL_3(2)`, the canonical-lift and central-extension reasoning in `thm:galois-stability`, and the explicit class-function argument in `lemma:restriction-transitivity`. It also checked the characteristic-zero descent and positive-characteristic reduction in `sec:fields`, including the cited normal-complement and Hall-subalgebra hypotheses, the perfect-closure step, and the Witt-vector lifting argument. No decisive flaw was identified in that bounded review.

The first audit also checked the canonical-lift references and basic modular Clifford and Gallagher statements. This overlap provides an additional check of those dependencies, while the two audits remain AI assessments.

## Selected sources checked

The source checks included the following primary mathematical publications or author-maintained reference data:

- [Bastos–Schneider, Lemma 6 and Corollary 7](https://arxiv.org/html/2006.16414v2): simple groups with soluble subgroups of prime-power index, including the relevant stabilizer types.
- [Navarro–Rizo, Theorems A and 3.4](https://www.degruyterbrill.com/document/doi/10.1515/jgth-2016-0052/html): the automorphism-only predecessor and the prime absent from a simple group's Schur multiplier.
- [Vallejo, Theorems 1.25, 4.6–4.8 and 4.30](https://www.uv.es/cavaro3/download/Thesis.pdf): canonical lifts, Galois invariance, modular Clifford theory, and Gallagher correspondence.
- [GAP Character Table Library subgroup data](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/L3(2).html) and [the characteristic-two decomposition matrix](https://www.math.rwth-aachen.de/~moc/decomposition/tex/L3(2)/L3(2)mod2.pdf): the specific `L_3(2)` facts used in the argument.
- [Gorenstein, “On a theorem of Philip Hall”](https://msp.org/pjm/1966/19-1/pjm-v19-n1-p08-p.pdf): the characteristic critical-subgroup properties.
- [Passman, “Character theory and group rings”](https://people.math.wisc.edu/~passman/charprob.pdf), especially Lemmas 2.6(ii) and 2.7: the positive-characteristic reduction.

These checks do not amount to independently reconstructing the classification of finite simple groups or verifying every foundational reference page by page.

## Human review and remaining checks

Human review of this version has **not been recorded**. These audits did not establish novelty, run a formal proof checker, or provide a formal correctness certificate. Successful PDF compilation concerns document production, not the validity of the mathematics.

Independent expert review should examine the complete dependency chain, particularly the paired-action character-cover correspondence, the modular Galois-stability argument, and their interaction in the simultaneous minimal-counterexample proof. These are priorities for further verification, not findings that those steps are false or incomplete.

Public release was explicitly authorized. That permission authorizes distribution; it does not supply mathematical acceptance. The supplied manuscript gives no author names, and none have been inferred.

## Integrity and corrections

The original LaTeX source is unchanged. Its first-page warning that the proposed proof requires independent verification is preserved in the compiled PDF. Future corrections should identify the affected statement and proof version and retain a traceable record of the change.

**Original TeX SHA-256**

```text
c70ae48f9007a4512ebdff1b112378e0dc9936d8c53bfceb2fd5e590ac07ff22
```

**Compiled PDF SHA-256**

```text
5eea469e39bfd933cf7c92fc2e8af6127444fabc05b607bfcdec8c808b745e30
```
