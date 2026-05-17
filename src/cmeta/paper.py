#!/usr/bin/env python3
"""Full-text of the Epistemic Closure paper (arXiv:2603.09756).

This file contains the original arXiv abstract and key excerpts.
For the complete paper, see https://arxiv.org/abs/2603.09756
"""
# ============================================================
# Title: Epistemic Closure: Autonomous Mechanism Completion
#        for Physically Consistent Simulation
# Authors: Yue Wu, Tianhao Su, Rui Hu, Mingchuan Zhao,
#          Shunbo Hu, Deng Pan, Jizhong Huang
# arXiv: 2603.09756v1 [cs.DB] 10 Mar 2026
# ============================================================

ABSTRACT = """
The integration of Large Language Models (LLMs) into scientific discovery is
currently hindered by the "Implicit Context" problem, where governing equations
extracted from literature contain invisible thermodynamic assumptions (e.g.,
undrained conditions) that standard generative models fail to recognize. This
leads to "Physical Hallucination": the generation of syntactically correct
solvers that faithfully execute physically invalid laws. Here, we introduce a
Neuro-Symbolic Generative Agent that functions as a cognitive supervisor atop
traditional numerical engines. By encapsulating physical laws into modular
"Constitutive Skills" and leveraging latent intrinsic priors, the Agent employs
a Chain-of-Thought reasoning workflow to autonomously validate, prune, and
complete physical mechanisms. We demonstrate this capability on the challenge
of thermal pressurization in low-permeability sandstone. While a standard
literature-retrieval baseline erroneously predicts catastrophic material failure
by blindly adopting a rigid "undrained" simplification, our Agent autonomously
identifies the system as operating in a drained regime (Deborah number De << 1)
via dimensionless scaling analysis. Consequently, it inductively completes the
missing dissipation mechanism (Darcy flow) required to satisfy boundary
constraints, predicting a stable stress path consistent with experimental
reality. This work establishes a paradigm where AI agents transcend the role of
coding assistants to act as epistemic partners, capable of reasoning about—and
correcting—the theoretical assumptions embedded in scientific data.
"""

KEYWORDS = ["Neuro-Symbolic AI", "Physical Hallucination",
            "Autonomous Mechanism Completion"]

KEY_CONTRIBUTIONS = [
    (
        "Context-Aware Reasoning: Agent identifies when "
        "literature assumptions (e.g., undrained) contradict "
        "the system's actual operating regime"
    ),
    (
        "Emergent Validity: Fully autonomous coupled simulation "
        "predicts safe stress path (p' ~ 8.9 MPa), avoiding "
        "false-positive failure prediction"
    ),
    (
        "Methodological Robustness: Cell-by-cell validation + "
        "regime detection ensures AI creativity is bounded "
        "by physical laws"
    ),
]

# The paper's three core mechanism components:
# 1. Semantic Encapsulation: raw equations -> Constitutive Skills (C_meta)
# 2. Physics-Informed Cognitive Reasoning
#    - Deductive Pruning (constraint compatibility check)
#    - Inductive Completion (dimensionless analysis + intrinsic priors)
# 3. Automated Variational Synthesis (C_meta -> FEM weak form -> solver)
