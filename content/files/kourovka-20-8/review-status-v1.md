# Version 1: review and release status

**Publication type:** AI generated. **Mathematical status:** candidate solution, review pending.

This manuscript gives a complete explicit counterexample to Kourovka 20.8. The underlying rank-three construction is due to Lei and Zhang; this exposition verifies the additional condition on every proper intermediate subgroup. Novelty and priority for this application have not been established.

## Actual review

- The authoring AI checked the full statement, both strict inclusions, all rank assertions, the universal intermediate-subgroup argument, and the second homomorphism.
- A separate Codex agent, `audit_rankdrop`, reviewed the exact archived candidate on 6 November 2026 and found no mathematical gap. No repair was needed. Its full audit follows below.
- The manuscript is a typeset exposition of that argument. The authoring agent checked correspondence with the audited report, including all graph edges and orientations. The separate audit's scope is the pinned report, not independent inspection of this typeset file.
- Human mathematical review remains pending. No human reviewer, editorial acceptance, or research priority is asserted.
- The relevant finite graphs and word identities are verified directly; the deduction does not rely on the full Lei-Zhang equalizer theorem or the project's 20.11 candidate as a black box.

## Formalization and reproducibility

No Lean executable was available (`command -v lean` found none). No Lean proof or formal mathematical verification is supplied. The exact standard-library Python verifier and its complete recorded output appear at the end of this file, so public readers can reproduce the checks without access to the private notebook. These checks validate finite data; the manuscript supplies the universal mathematical proof.

## Prompts and conversation

No public conversation link was supplied for this version. No private transcript is included.

## Separate audit

References to the private repository below identify the exact audited version. Access to that repository is not needed to read the complete manuscript, audit, or verifier.

# Separate AI audit of the Kourovka 20.8 candidate

Date: 6 November 2026. Reviewer: separate Codex agent `audit_rankdrop`.
This is an AI proof audit, not human acceptance or formal verification.

## Exact version reviewed

- Repository: `thomasl2/math-research-lab`.
- Commit: `b878477e0c534789accdf80bf29aa1bc8ca837d8`.
- Report: `problems/kourovka-20-8/runs/research-20261106-rankdrop-rdelaby-c42a6e.md`.
- Claim: `research-20261106-rankdrop-rdelaby-c42a6e-C1`.
- Report SHA-256: `f7f56caeb2e843e7d7ce61fe047918903b30603f12db73076a38b3573c73cd33`.
- GitHub report blob: `b22ee6898b4352741fc9a431a6910261adcc7dc5`.
- Checker SHA-256: `8e5903b39ae25a84bdc6ed9a3e675562ad585670e37b00fd8e7a4aba154afdab`.
- Recorded checker-output SHA-256: `2704223701b2b017efe1445cca2732a9fc21136a89036d6bd3a83b17f028f73d`.

The reviewer fetched the report at this pinned GitHub commit and compared its
complete text with the local report. They were identical. The audit concerns
that archived argument and its displayed verification code; it does not by
itself certify a subsequently edited or typeset version.

## Verdict

**No mathematical gap was found. No repair is needed for the argument as
written.** The explicit example satisfies every hypothesis of Problem 20.8
and supplies a second homomorphism fixing the specified subgroup pointwise.
The conclusion is a full negative answer, rather than a special-case result
or an unsupported search result.

The necessary graph facts and the specialized construction are proved in the
report. The deduction does not require treating the full Lei-Zhang equalizer
theorem as an unverified black box, computing the full equalizer, or using the
project's candidate solution to 20.11. The construction is nevertheless
existing work of Lei and Zhang and must retain that attribution. This audit
does not establish novelty or priority of the application to 20.8.

## Audit of the mathematical argument

### Exact hypotheses and scope

The reviewer checked the statement on printed page 157 of the November 2026
Kourovka PDF, both as extracted text and in a rendered page. It asks precisely
for finite-rank free groups K < H < F, a rank drop from K to H, the rank lower
bound for every proper intermediate subgroup of H containing K, and uniqueness
of a homomorphism H -> F fixing K. The candidate preserves both strict
inclusions and all quantifiers. The codomain is F; there is no requirement
that the alternative map take H into itself.

In the candidate,

\[
F=F(a,b),\quad u=(a^{-1}b)^2,\quad v=(a^{-2}b^2)^2,
\]
\[
H=\langle a,u,v\rangle,\qquad
K=\langle u,v,aua^{-1},a^2va^{-2}\rangle.
\]

### Freeness and rank of H

The six-vertex, eight-edge graph in the report is connected and folded.
Checking the inverse edges introduces no duplicate outgoing signed label at
any vertex. Its four b-edges and the edge from P2 to R form a spanning tree:
they connect all six vertices and contain no cycle.

The remaining a-loop gives a. The omitted P1-to-Q1 edge gives the loop
ba^(-1)b. The omitted R-to-Q2 edge gives b^2a^(-2)b^2. Thus the stated
spanning-tree basis is correct, including the second generator's path through R.
The immersion into the two-petal rose is injective on fundamental groups,
because a reduced graph path has freely reduced label. Its image is therefore
free of rank 8-6+1=3 on a, d1=au, d2=a^2v.

Replacing d1 by a^(-1)d1 and d2 by a^(-2)d2 while fixing a is an invertible
basis change. It proves that a,u,v themselves are a free basis, not merely a
three-element generating set with an assumed absence of relations. Hence the
prescription for the later homomorphism is legitimate.

### Freeness and rank of K

In the basis a,u,v of H, the candidate's three-vertex graph has two consecutive
a-edges, u-loops at vertices 0 and 1, and v-loops at 0 and 2. It is folded,
connected, and has six topological edges. Taking the two a-edges as a tree gives
exactly the four displayed generators of K. Its label immersion proves rank
K=6-3+1=4. Rank H=3 and rank F=2 then imply K != H and H != F; the inclusions
hold by definition, so both are strict. The argument never assumes that rank
is monotone under general subgroup inclusions.

### The universal intermediate-subgroup condition

This is the central extra requirement of Problem 20.8, and the proof handles it
without replacing it by a condition on an enumerated finite list of subgroups.

For every K <= L < H, use the right-coset graph of L and set
z0=L, z1=La, z2=La^2. The three indicated loops at the base and its translates
exist for exactly the reasons stated: a u a^(-1) in L gives the u-loop at La,
and a^2 v a^(-2) in L gives the v-loop at La^2. The criterion for right cosets
is Lr=Ls if and only if r s^(-1) lies in L. Thus either adjacent equality
z0=z1 or z1=z2 forces a in L. Together with u,v in K this forces L=H, which
is excluded.

If all three cosets are distinct, the six displayed topological edges are
distinct, and their image is an embedded graph of cycle rank four. If only
z0=z2, the two v-loops coincide but the remaining edges do not: there are two
distinct a-edges, two u-loops, and one v-loop on two vertices. In particular
the a-edges are distinct topological edges, even though their endpoints are
reversed. They have the same positive label a, whereas inverse orientations
have labels a and a^(-1). This image has cycle rank 5-2+1=4.

There is no third case compatible with properness of L. Extra edges or
vertices of the full Schreier graph cannot destroy the four independent cycles
of either embedded graph. Inclusion of a subgraph injects its first homology,
since there are no two-dimensional boundaries in a graph. The fundamental
group of the full based Schreier graph is L, so rank L is at least four.
This also treats infinitely generated L: the finite subgraph still supplies
four independent cycles. It is unnecessary to invoke finite generation of L,
algebraic extension theory, or an equalizer-rank assertion.

### The second homomorphism

The free basis just proved permits the unique homomorphism phi:H -> F with
phi(a)=b and phi(u)=u, phi(v)=v. If c_i=a^(-i)b^i, then b^i=a^i c_i and
c_i commutes with c_i^2. Hence

\[
b^i c_i^2 b^{-i}=a^i c_i^2 a^{-i}\qquad(i=1,2).
\]

These identities say precisely that phi fixes a u a^(-1) and a^2 v a^(-2).
It fixes u,v by its definition, so it fixes every element of K. Since the
ambient free generators a and b are different, phi(a) != a. This is a second
homomorphism satisfying the exact requirement of the question. Injectivity
of phi is not needed; the report correctly makes no dependency on it.

## Computations checked

The reviewer read the standard-library verifier, including inverse-word
formation, free reduction, substitution, deterministic folding, membership
testing, and enumeration of set partitions. The script was then rerun with
Python 3.12.14. Its complete output was byte-for-byte identical to the archived
`check-output.json`.

The rerun confirmed ranks 3,4,4 for H in F, K in the abstract group on a,u,v,
and K directly in F, respectively. It confirmed agreement of the two maps on
all four K generators, disagreement on a, and b not belonging to H. The last
fact is supplementary and is not necessary for the counterexample.

All five set partitions of the three graph vertices were checked. The
identity partition and the identification 0=2 have folded rank four. Each
partition identifying consecutive vertices folds to the three-petal rose of
rank three, representing H. These outcomes agree with the written case split.

As an additional independent check, the reviewer entered the three graphs
directly, without importing the candidate's verifier, checked the outgoing
signed labels for foldedness, and computed the ranks of their incidence
matrices over F2 by Gaussian elimination. The cycle-space dimensions were:

| Graph | Vertices | Topological edges | Cycle rank |
| --- | ---: | ---: | ---: |
| Graph for H in F(a,b) | 6 | 8 | 3 |
| Graph for K in H | 3 | 6 | 4 |
| The 0=2 quotient | 2 | 5 | 4 |

The computation is a check of finite data, not a formal proof of the universal
statement. The preceding Schreier-graph reasoning supplies that statement.
`command -v lean` returned no executable. No Lean formalization or other formal
mathematical proof checker was run.

## Sources, attribution, and limits

The source PDF hashes inspected in this audit are:

- Kourovka Notebook, November 2026 update:
  `45420f88b0246f2558b581bf813184275972de2fd0a7c87cf4942f777c9d833d`.
- Lei-Zhang, arXiv:2604.24502v2:
  `f1d96297adc895bad8e8b62100fb5c789e08ccace5c2cccd7d3ea593169fc223`.

The reviewer inspected Lei-Zhang's Lemma 3.2, Proposition 3.3, Construction 4.1,
and the related graph computations. The candidate is the n=3 specialization
of their construction, together with the explicit intermediate-overgroup
argument needed for the different Kourovka question. The mathematical
construction itself must not be presented as an original discovery of this
project.

The unmarked entry in the inspected Notebook confirms only its editorial
appearance on that date. This audit did not conduct a comprehensive literature
or priority search and does not endorse a claim that nobody had previously
observed the application. The absence of a solution marker is not evidence
sufficient to establish worldwide openness or novelty.

Primary sources:

- https://kourovkanotebookorg.wordpress.com/wp-content/uploads/2026/11/21tkt.pdf
- https://arxiv.org/pdf/2604.24502v2

The recommended project status remains **candidate solution — review pending**.
The manuscript may accurately say that a separate AI audit found no gap in the
complete explicit counterexample, while keeping human acceptance, editorial
acceptance, novelty, and formal verification separate. This review does not
authorize website deployment before the user confirms that access is ready.


## Reproducibility appendix: complete verifier

Save this code as `check_rank_drop.py` and run `python3 check_rank_drop.py`. No third-party packages are required. The Python version field may differ on another machine.

```python
#!/usr/bin/env python3
"""Exact free-word and finite Stallings-fold checks; Python standard library only.

This is a reproducible check of the objects used in the written proof, not a
formal proof checker or a finite search over all intermediate subgroups.
"""
import json
import platform


def reduce_word(word):
    out = []
    for letter in word:
        if out and out[-1] == -letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def inv(word):
    return tuple(-x for x in reversed(word))


def substitute(word, images):
    out = []
    for x in word:
        out.extend(images[x] if x > 0 else inv(images[-x]))
    return reduce_word(out)


def fold(vertex_count, edges, partition=None):
    parent = list(range(vertex_count))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        x, y = find(x), find(y)
        if x == y:
            return False
        parent[max(x, y)] = min(x, y)
        return True

    if partition:
        for block in partition:
            for v in block[1:]:
                union(block[0], v)
    arcs = edges + [(v, -x, u) for u, x, v in edges]
    changed = True
    while changed:
        changed = False
        transitions = {}
        for u, x, v in arcs:
            key = (find(u), x)
            if key in transitions:
                changed |= union(v, transitions[key])
            else:
                transitions[key] = find(v)
    classes = sorted({find(v) for v in range(vertex_count)})
    renumber = {v: i for i, v in enumerate(classes)}
    positive = sorted({(renumber[find(u)], x, renumber[find(v)])
                       for u, x, v in arcs if x > 0})
    groups = [[v for v in range(vertex_count) if find(v) == c] for c in classes]
    return {'vertices': len(classes), 'edges': len(positive),
            'rank': len(positive) - len(classes) + 1,
            'positive_edges': positive, 'vertex_classes': groups}


def from_words(words):
    edges = []
    count = 1
    for word in words:
        current = 0
        for i, x in enumerate(word):
            target = 0 if i == len(word) - 1 else count
            if target:
                count += 1
            edges.append((current, x, target))
            current = target
    return fold(count, edges)


def contains(graph, word):
    trans = {}
    for u, x, v in graph['positive_edges']:
        trans[u, x] = v
        trans[v, -x] = u
    vertex = 0
    for x in word:
        if (vertex, x) not in trans:
            return False
        vertex = trans[vertex, x]
    return vertex == 0


def partitions(items):
    if not items:
        yield []
        return
    first, *rest = items
    for blocks in partitions(rest):
        yield [[first]] + blocks
        for i in range(len(blocks)):
            yield blocks[:i] + [[first] + blocks[i]] + blocks[i + 1:]


def main():
    # Ambient F(a,b): a=1, b=2. Abstract H: t=1, x=2, y=3.
    a, b = (1,), (2,)
    u, v = (-1, 2, -1, 2), (-1, -1, 2, 2, -1, -1, 2, 2)
    g = {1: a, 2: u, 3: v}
    h = {1: b, 2: u, 3: v}
    generators = [(2,), (3,), (1, 2, -1), (1, 1, 3, -1, -1)]
    agreement = [substitute(w, g) == substitute(w, h) for w in generators]
    assert all(agreement)
    assert g[1] != h[1]
    H = from_words([a, u, v])
    K_abstract = from_words(generators)
    K_ambient = from_words([substitute(w, g) for w in generators])
    assert H['rank'] == 3
    assert K_abstract['rank'] == K_ambient['rank'] == 4
    assert not contains(H, b)
    # Independently specified three-vertex graph from the proof.
    edges = [(0, 1, 1), (1, 1, 2), (0, 2, 0), (1, 2, 1),
             (0, 3, 0), (2, 3, 2)]
    graph = fold(3, edges)
    assert graph['rank'] == 4
    assert all(contains(graph, w) for w in generators)
    quotients = []
    for partition in partitions([0, 1, 2]):
        q = fold(3, edges, partition)
        assert q['rank'] == 4 or (q['rank'] == 3 and q['vertices'] == 1)
        if q['rank'] == 3:
            assert q['positive_edges'] == [(0, 1, 0), (0, 2, 0), (0, 3, 0)]
        quotients.append({'initial_partition': partition, **q})
    assert len(quotients) == 5
    print(json.dumps({
        'python_version': platform.python_version(),
        'word_convention': 'Signed integers; inverse reverses order and changes signs.',
        'H_in_F2': H,
        'K_in_abstract_H': K_abstract,
        'K_in_F2': K_ambient,
        'agreement_on_four_K_generators': agreement,
        'maps_differ_on_t': g[1] != h[1],
        'b_belongs_to_H': contains(H, b),
        'all_five_vertex_partitions': quotients,
        'result': 'All exact finite checks passed.',
        'scope': 'The manuscript supplies the universal Schreier-graph argument; this script checks its finite data.'
    }, indent=2))


if __name__ == '__main__':
    main()
```

## Reproducibility appendix: recorded output

```json
{
  "python_version": "3.12.14",
  "word_convention": "Signed integers; inverse reverses order and changes signs.",
  "H_in_F2": {
    "vertices": 6,
    "edges": 8,
    "rank": 3,
    "positive_edges": [
      [
        0,
        1,
        0
      ],
      [
        0,
        2,
        1
      ],
      [
        1,
        2,
        3
      ],
      [
        2,
        1,
        1
      ],
      [
        2,
        2,
        0
      ],
      [
        4,
        1,
        3
      ],
      [
        5,
        1,
        4
      ],
      [
        5,
        2,
        2
      ]
    ],
    "vertex_classes": [
      [
        0,
        1,
        4,
        5
      ],
      [
        2,
        6
      ],
      [
        3,
        10
      ],
      [
        7
      ],
      [
        8
      ],
      [
        9
      ]
    ]
  },
  "K_in_abstract_H": {
    "vertices": 3,
    "edges": 6,
    "rank": 4,
    "positive_edges": [
      [
        0,
        1,
        1
      ],
      [
        0,
        2,
        0
      ],
      [
        0,
        3,
        0
      ],
      [
        1,
        1,
        2
      ],
      [
        1,
        2,
        1
      ],
      [
        2,
        3,
        2
      ]
    ],
    "vertex_classes": [
      [
        0
      ],
      [
        1,
        2,
        3,
        6
      ],
      [
        4,
        5
      ]
    ]
  },
  "K_in_F2": {
    "vertices": 17,
    "edges": 20,
    "rank": 4,
    "positive_edges": [
      [
        0,
        1,
        11
      ],
      [
        0,
        2,
        9
      ],
      [
        1,
        1,
        0
      ],
      [
        1,
        2,
        2
      ],
      [
        3,
        1,
        2
      ],
      [
        3,
        2,
        0
      ],
      [
        4,
        1,
        1
      ],
      [
        4,
        2,
        5
      ],
      [
        5,
        2,
        6
      ],
      [
        7,
        1,
        6
      ],
      [
        8,
        1,
        7
      ],
      [
        8,
        2,
        3
      ],
      [
        9,
        2,
        12
      ],
      [
        10,
        1,
        9
      ],
      [
        10,
        2,
        11
      ],
      [
        11,
        1,
        16
      ],
      [
        13,
        1,
        12
      ],
      [
        14,
        1,
        13
      ],
      [
        14,
        2,
        15
      ],
      [
        15,
        2,
        16
      ]
    ],
    "vertex_classes": [
      [
        0
      ],
      [
        1,
        4
      ],
      [
        2
      ],
      [
        3,
        10
      ],
      [
        5
      ],
      [
        6
      ],
      [
        7
      ],
      [
        8
      ],
      [
        9
      ],
      [
        11,
        14
      ],
      [
        12
      ],
      [
        13,
        20
      ],
      [
        15
      ],
      [
        16
      ],
      [
        17
      ],
      [
        18
      ],
      [
        19
      ]
    ]
  },
  "agreement_on_four_K_generators": [
    true,
    true,
    true,
    true
  ],
  "maps_differ_on_t": true,
  "b_belongs_to_H": false,
  "all_five_vertex_partitions": [
    {
      "initial_partition": [
        [
          0
        ],
        [
          1
        ],
        [
          2
        ]
      ],
      "vertices": 3,
      "edges": 6,
      "rank": 4,
      "positive_edges": [
        [
          0,
          1,
          1
        ],
        [
          0,
          2,
          0
        ],
        [
          0,
          3,
          0
        ],
        [
          1,
          1,
          2
        ],
        [
          1,
          2,
          1
        ],
        [
          2,
          3,
          2
        ]
      ],
      "vertex_classes": [
        [
          0
        ],
        [
          1
        ],
        [
          2
        ]
      ]
    },
    {
      "initial_partition": [
        [
          0,
          1
        ],
        [
          2
        ]
      ],
      "vertices": 1,
      "edges": 3,
      "rank": 3,
      "positive_edges": [
        [
          0,
          1,
          0
        ],
        [
          0,
          2,
          0
        ],
        [
          0,
          3,
          0
        ]
      ],
      "vertex_classes": [
        [
          0,
          1,
          2
        ]
      ]
    },
    {
      "initial_partition": [
        [
          1
        ],
        [
          0,
          2
        ]
      ],
      "vertices": 2,
      "edges": 5,
      "rank": 4,
      "positive_edges": [
        [
          0,
          1,
          1
        ],
        [
          0,
          2,
          0
        ],
        [
          0,
          3,
          0
        ],
        [
          1,
          1,
          0
        ],
        [
          1,
          2,
          1
        ]
      ],
      "vertex_classes": [
        [
          0,
          2
        ],
        [
          1
        ]
      ]
    },
    {
      "initial_partition": [
        [
          0
        ],
        [
          1,
          2
        ]
      ],
      "vertices": 1,
      "edges": 3,
      "rank": 3,
      "positive_edges": [
        [
          0,
          1,
          0
        ],
        [
          0,
          2,
          0
        ],
        [
          0,
          3,
          0
        ]
      ],
      "vertex_classes": [
        [
          0,
          1,
          2
        ]
      ]
    },
    {
      "initial_partition": [
        [
          0,
          1,
          2
        ]
      ],
      "vertices": 1,
      "edges": 3,
      "rank": 3,
      "positive_edges": [
        [
          0,
          1,
          0
        ],
        [
          0,
          2,
          0
        ],
        [
          0,
          3,
          0
        ]
      ],
      "vertex_classes": [
        [
          0,
          1,
          2
        ]
      ]
    }
  ],
  "result": "All exact finite checks passed.",
  "scope": "The manuscript supplies the universal Schreier-graph argument; this script checks its finite data."
}
```
