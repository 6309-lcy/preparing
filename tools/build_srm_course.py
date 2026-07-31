"""
Build Exam SRM as a complete study-ready course (after P, FM, FAM).

Syllabus midpoints (SOA-style ranges):
  Basics of statistical learning  5–10%  → 8%
  Linear models (incl. GLMs)     40–50%  → 45%
  Time series                    10–15%  → 12%
  Decision trees / ensembles     20–25%  → 22%
  PCA & clustering               ~rest   → 13%

- Full lessons, path, plan from today
- Authored SRM conceptual/quantitative drill bank
- Mark SRM ready; PA becomes next
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "data"
SRM_DIR = DATA / "courses" / "srm"
sys.path.insert(0, str(ROOT / "tools"))

import build_all_content as bac  # noqa: E402

START = date.today()
WEEKS = 14
TODAY = START.isoformat()

SRM_WEIGHTS = {
    "learning": 0.08,
    "linear_glm": 0.45,
    "time_series": 0.12,
    "trees": 0.22,
    "pca_cluster": 0.13,
}


def concept(sid, title, body):
    return {"id": sid, "type": "concept", "title": title, "body": body}


def example(sid, title, setup, solution, why):
    return {"id": sid, "type": "example", "title": title, "setup": setup, "solution": solution, "why": why}


def check(sid, title, prompt, choices, answer, explain):
    return {
        "id": sid,
        "type": "check",
        "title": title,
        "prompt": prompt,
        "choices": choices,
        "answer": answer,
        "explain": explain,
    }


def lesson(lid, title, minutes, lo, sections):
    return {
        "id": lid,
        "title": title,
        "minutes": minutes,
        "lo": lo if isinstance(lo, list) else [lo],
        "sections": sections,
    }


def srm_lessons() -> dict:
    return {
        "srm_setup": lesson(
            "srm_setup",
            "Exam SRM orientation",
            25,
            ["SRM"],
            [
                concept(
                    "s1",
                    "What SRM tests",
                    "Exam SRM (Statistics for Risk Modeling) is a 3.5-hour CBT with ~35 multiple-choice questions.\n\n"
                    "Approximate weights:\n"
                    "• Basics of statistical learning ~5–10%\n"
                    "• Linear models (regression + GLMs) ~40–50%  ← largest\n"
                    "• Time series ~10–15%\n"
                    "• Decision trees & ensembles ~20–25%\n"
                    "• PCA & clustering ~10–15%\n\n"
                    "SRM is concept-heavy: interpret models, diagnose issues, choose methods — not production ML engineering.",
                ),
                concept(
                    "s2",
                    "Study rhythm",
                    "Path: Learn → Practice → Drill → Chapter test (≥70%).\n"
                    "Spend the most time on linear models/GLMs. Last two weeks: mixed mocks only.",
                ),
                check(
                    "s3",
                    "Biggest block",
                    "Which topic usually has the largest exam weight?",
                    {
                        "A": "Only PCA",
                        "B": "Linear models / GLMs",
                        "C": "Only k-means",
                        "D": "Only AR(1) formula memorization without interpretation",
                    },
                    "B",
                    "Linear models (including GLMs) dominate the syllabus weight.",
                ),
            ],
        ),
        "srm_learn": lesson(
            "srm_learn",
            "Basics of statistical learning",
            45,
            ["SRM1"],
            [
                concept(
                    "s1",
                    "Problem types",
                    "Supervised vs unsupervised.\n"
                    "Regression (numeric Y) vs classification (categorical Y).\n"
                    "Training / validation / test splits estimate generalization.\n"
                    "Bias–variance tradeoff: flexible models can overfit; rigid models underfit.\n"
                    "Cross-validation (e.g. k-fold) for model selection when data are limited.",
                ),
                concept(
                    "s2",
                    "Workflow pitfalls",
                    "Data leakage: using future or target-derived features.\n"
                    "Imbalance: accuracy can mislead — prefer precision/recall/AUC as appropriate.\n"
                    "Feature scaling matters for distance-based methods and some regularized models.\n"
                    "Interpretability vs predictive accuracy tradeoff — exam stems often ask which matters for the business goal.",
                ),
                example(
                    "s3",
                    "Worked: overfitting signal",
                    "Train R²=0.98, test R²=0.40. What happened?",
                    "Overfitting: model memorized training noise; fails out of sample.\n"
                    "Remedies: simplify, regularize, more data, early stopping, better CV.",
                    "Always compare train vs holdout metrics.",
                ),
                check(
                    "s4",
                    "Overfitting",
                    "Overfitting typically means:",
                    {
                        "A": "Great train, weak test performance",
                        "B": "Weak train, great test",
                        "C": "No features",
                        "D": "Perfect causal identification",
                    },
                    "A",
                    "Memorizing training noise fails on new data.",
                ),
            ],
        ),
        "srm_lm": lesson(
            "srm_lm",
            "Linear regression essentials",
            50,
            ["SRM2"],
            [
                concept(
                    "s1",
                    "OLS model",
                    "Y = β0 + β1 X1 + … + βp Xp + ε.\n"
                    "Assumptions (classical): linearity in parameters, independent errors, constant variance, (for inference) normality.\n"
                    "Interpret βj as expected change in Y per unit Xj holding others fixed (ceteris paribus).\n"
                    "R² = 1 − SS_res/SS_tot; adjusted R² penalizes extra predictors.\n"
                    "Residuals diagnose curvature, heteroscedasticity, outliers.",
                ),
                concept(
                    "s2",
                    "Inference & collinearity",
                    "t-tests for coefficients; F-test for overall regression.\n"
                    "Multicollinearity: inflated SEs, unstable coefficients — check VIF/correlations.\n"
                    "Categorical predictors via dummy variables (drop one level as baseline).",
                ),
                example(
                    "s3",
                    "Worked: coefficient meaning",
                    "Model: claim_cost = 200 + 15·age − 40·safe_driver. Interpret −40.",
                    "Holding age fixed, expected claim cost is 40 lower for safe drivers than the baseline group.",
                    "Always state the holding-others-fixed condition.",
                ),
                check(
                    "s4",
                    "R²",
                    "R² measures:",
                    {
                        "A": "Causal effect size only",
                        "B": "Fraction of variance in Y explained by the model",
                        "C": "Always the best model selector alone",
                        "D": "Test-set accuracy only",
                    },
                    "B",
                    "In-sample variance explained — not automatic proof of best model.",
                ),
            ],
        ),
        "srm_glm": lesson(
            "srm_glm",
            "Generalized linear models",
            55,
            ["SRM2"],
            [
                concept(
                    "s1",
                    "GLM structure",
                    "Three parts:\n"
                    "1) Random: Y from exponential family (Normal, Poisson, Binomial, Gamma, …)\n"
                    "2) Linear predictor: η = Xβ\n"
                    "3) Link: g(μ)=η  so μ = g^{−1}(Xβ)\n\n"
                    "Common links: identity (normal), log (positive means, counts), logit (probabilities).\n"
                    "Offset: known exposure on the linear predictor (e.g. log(exposure) for rates).",
                ),
                concept(
                    "s2",
                    "Interpretation",
                    "Log link: e^{βj} multiplies the mean when Xj increases by 1 (multiplicative effect).\n"
                    "Logit link: e^{βj} is an odds ratio for a unit increase in Xj.\n"
                    "Deviance / residual diagnostics; overdispersion for Poisson (maybe NB instead).",
                ),
                example(
                    "s3",
                    "Worked: log link",
                    "Poisson GLM with log link, β_age=0.02. Effect of +1 year of age?",
                    "Mean multiplies by e^{0.02} ≈ 1.0202 (~2% increase), holding others fixed.",
                    "Never treat log-link coefficients as additive on the mean scale.",
                ),
                check(
                    "s4",
                    "Log link",
                    "With log link, coefficient β=0.2 multiplies the mean by about:",
                    {"A": "0.2", "B": "e^{0.2}", "C": "log(0.2)", "D": "1.2 exactly always without e"},
                    "B",
                    "μ ∝ e^{Xβ}; unit increase multiplies by e^β.",
                ),
            ],
        ),
        "srm_glm_select": lesson(
            "srm_glm_select",
            "Model selection & diagnostics for GLMs",
            45,
            ["SRM2"],
            [
                concept(
                    "s1",
                    "Comparing models",
                    "Nested models: likelihood ratio / deviance tests.\n"
                    "Information criteria: AIC, BIC (BIC penalizes complexity more).\n"
                    "Cross-validated predictive metrics on holdout.\n"
                    "Residual plots, leverage, influence — same spirit as linear models, adjusted for GLM variance functions.",
                ),
                concept(
                    "s2",
                    "Practical choices",
                    "Count data with variance >> mean → consider negative binomial or overdispersed Poisson.\n"
                    "Binary outcomes → logistic (binomial + logit).\n"
                    "Positive continuous skewed severity → gamma/lognormal-style GLM choices (per syllabus readings).",
                ),
                check(
                    "s3",
                    "AIC vs BIC",
                    "Compared with AIC, BIC typically:",
                    {
                        "A": "Penalizes extra parameters less",
                        "B": "Penalizes extra parameters more (for large n)",
                        "C": "Ignores likelihood",
                        "D": "Only works for trees",
                    },
                    "B",
                    "BIC's penalty grows with log(n).",
                ),
            ],
        ),
        "srm_ts": lesson(
            "srm_ts",
            "Time series models",
            50,
            ["SRM3"],
            [
                concept(
                    "s1",
                    "Components & stationarity",
                    "Trend, seasonality, cycle, irregular noise.\n"
                    "Stationarity: stable mean/variance/dependence over time (weak stationarity ideas).\n"
                    "Differencing and transformations can reduce nonstationarity.\n"
                    "ACF/PACF patterns guide AR/MA orders (conceptual recognition).",
                ),
                concept(
                    "s2",
                    "AR, MA, ARIMA, smoothing",
                    "AR(p): regress on past values.\n"
                    "MA(q): regress on past shocks.\n"
                    "ARIMA: differencing + ARMA.\n"
                    "Exponential smoothing: weighted recent observations; good for short-term forecasts.\n"
                    "Forecast uncertainty generally widens with horizon.",
                ),
                example(
                    "s3",
                    "Worked: AR(1) intuition",
                    "Y_t = 0.7 Y_{t−1} + ε_t. What does 0.7 mean?",
                    "Strong persistence: yesterday's level heavily influences today; shocks decay geometrically.",
                    "Interpretation beats memorizing only formulas.",
                ),
                check(
                    "s4",
                    "Stationarity",
                    "A weakly stationary series has roughly stable:",
                    {
                        "A": "Only the maximum value",
                        "B": "Mean/variance structure over time",
                        "C": "Sample size",
                        "D": "Software version",
                    },
                    "B",
                    "Classical stationarity targets stable moments/dependence.",
                ),
            ],
        ),
        "srm_trees": lesson(
            "srm_trees",
            "Decision trees (CART)",
            50,
            ["SRM4"],
            [
                concept(
                    "s1",
                    "How trees work",
                    "Recursive binary splits partition feature space to reduce impurity (classification) or SSE (regression).\n"
                    "Deep trees overfit; prune using cost-complexity / validation error.\n"
                    "Pros: nonlinearities, interactions, mixed feature types, interpretability of a single tree.\n"
                    "Cons: high variance, unstable splits, stepwise predictions.",
                ),
                concept(
                    "s2",
                    "Reading a tree",
                    "Follow decision rules from root to leaf.\n"
                    "Variable importance: total impurity decrease from splits on that feature.\n"
                    "Missing values and categorical splits are handled by the algorithm's rules (know conceptually).",
                ),
                example(
                    "s3",
                    "Worked: prune decision",
                    "Train error falls as tree grows; validation error U-shapes. Where to stop?",
                    "Choose size near minimum validation error (or 1-SE rule), not the deepest train-perfect tree.",
                    "Validation, not training purity, guides pruning.",
                ),
                check(
                    "s4",
                    "Overfit trees",
                    "Very deep trees without pruning tend to:",
                    {
                        "A": "Underfit always",
                        "B": "Overfit training data",
                        "C": "Have zero variance",
                        "D": "Ignore all features",
                    },
                    "B",
                    "They memorize training partitions.",
                ),
            ],
        ),
        "srm_ensembles": lesson(
            "srm_ensembles",
            "Bagging, random forests, boosting",
            50,
            ["SRM4"],
            [
                concept(
                    "s1",
                    "Bagging & random forests",
                    "Bagging: bootstrap many trees, average (regression) or vote (classification) → lower variance.\n"
                    "Random forest: bagging + random feature subset at each split → decorrelated trees.\n"
                    "OOB error approximates test error without a separate set.",
                ),
                concept(
                    "s2",
                    "Boosting",
                    "Sequentially fit weak learners to residuals / reweighted errors (AdaBoost, gradient boosting ideas).\n"
                    "Strong predictive performance; easier to overfit if too many iterations — use validation.\n"
                    "Less interpretable than a single shallow tree; still offers importance measures.",
                ),
                check(
                    "s3",
                    "RF idea",
                    "Random forests mainly improve over one tree by:",
                    {
                        "A": "Deleting all features",
                        "B": "Averaging many de-correlated trees",
                        "C": "Using only linear regression",
                        "D": "Ignoring bootstrap samples",
                    },
                    "B",
                    "Ensemble averaging + feature randomness.",
                ),
            ],
        ),
        "srm_pca": lesson(
            "srm_pca",
            "Principal components analysis",
            45,
            ["SRM5"],
            [
                concept(
                    "s1",
                    "PCA goal",
                    "Find orthogonal directions of maximum variance in feature space.\n"
                    "PC1 captures the most variance; PC2 next, subject to orthogonality.\n"
                    "Use for dimension reduction, visualization, multicollinearity relief before regression.\n"
                    "Scale features before PCA when units differ.",
                ),
                concept(
                    "s2",
                    "Interpretation",
                    "Loadings: how original variables contribute to a PC.\n"
                    "Scree plot / cumulative variance to choose number of components.\n"
                    "PCs are linear combinations — not always business-interpretable factors.",
                ),
                check(
                    "s3",
                    "PC1",
                    "The first principal component captures:",
                    {
                        "A": "Minimum variance direction",
                        "B": "Maximum variance direction",
                        "C": "Only the target Y",
                        "D": "Time index only",
                    },
                    "B",
                    "PC1 maximizes variance among unit linear combinations.",
                ),
            ],
        ),
        "srm_cluster": lesson(
            "srm_cluster",
            "Cluster analysis",
            45,
            ["SRM5"],
            [
                concept(
                    "s1",
                    "k-means & hierarchical",
                    "k-means: partition into k clusters minimizing within-cluster SS; choose k with care (elbow, silhouette concepts).\n"
                    "Hierarchical: build dendrogram (agglomerative); cut tree for clusters.\n"
                    "Distance metrics and scaling drive results.\n"
                    "Unsupervised: no Y — evaluate cohesion/separation, stability, business usefulness.",
                ),
                example(
                    "s2",
                    "Worked: when clustering helps",
                    "Insurer wants customer segments for product design without a labeled target.",
                    "Clustering on behavior/risk features can propose segments; validate with SME review and holdout stability.",
                    "Unsupervised ≠ automatic truth; it's a structure-discovery tool.",
                ),
                check(
                    "s3",
                    "Supervised?",
                    "k-means clustering is primarily:",
                    {
                        "A": "Supervised classification",
                        "B": "Unsupervised segmentation",
                        "C": "Time series forecasting",
                        "D": "A GLM link function",
                    },
                    "B",
                    "No labeled response required.",
                ),
            ],
        ),
        "srm_final": lesson(
            "srm_final",
            "SRM wrap-up",
            30,
            ["SRM"],
            [
                concept(
                    "s1",
                    "Exam-day priorities",
                    "Read the stem for the goal: prediction vs explanation, regression vs classification, supervised vs unsupervised.\n"
                    "For GLMs, translate coefficients via the link.\n"
                    "For trees/ensembles, think bias–variance and interpretability.\n"
                    "For time series, stationarity and forecast horizon.\n"
                    "Formula sheet light — concepts heavy.",
                ),
                check(
                    "s2",
                    "Priority",
                    "When a stem gives GLM coefficients with log link, first translate to:",
                    {
                        "A": "Kubernetes YAML",
                        "B": "Multiplicative effects on the mean",
                        "C": "Bond duration",
                        "D": "Life table l_x",
                    },
                    "B",
                    "Interpretation is the SRM skill.",
                ),
            ],
        ),
    }


def srm_units():
    return [
        {
            "id": "srm_u0",
            "number": 1,
            "title": "Orientation",
            "shortTitle": "Intro",
            "cluster": "intro",
            "weight": 0.02,
            "weightRange": "—",
            "color": "#0B3D3A",
            "description": "Exam map and study weights.",
            "chapters": [
                {"id": "srm_ch0", "number": 0, "title": "SRM map", "lessonId": "srm_setup", "topics": ["learning"], "levels": "short"},
            ],
        },
        {
            "id": "srm_u1",
            "number": 2,
            "title": "Statistical Learning Basics",
            "shortTitle": "Learning",
            "cluster": "learning",
            "weight": 0.08,
            "weightRange": "5–10%",
            "color": "#0F766E",
            "description": "Supervised/unsupervised, bias–variance, validation.",
            "chapters": [
                {"id": "srm_ch1", "number": 1, "title": "Learning workflow", "lessonId": "srm_learn", "topics": ["learning"]},
            ],
        },
        {
            "id": "srm_u2",
            "number": 3,
            "title": "Linear Models & GLMs",
            "shortTitle": "GLM",
            "cluster": "linear_glm",
            "weight": 0.45,
            "weightRange": "40–50%",
            "color": "#0369A1",
            "description": "Largest block: OLS + GLMs + selection.",
            "chapters": [
                {"id": "srm_ch2", "number": 2, "title": "Linear regression", "lessonId": "srm_lm", "topics": ["linear", "learning"]},
                {"id": "srm_ch3", "number": 3, "title": "GLMs", "lessonId": "srm_glm", "topics": ["glm", "linear"]},
                {"id": "srm_ch4", "number": 4, "title": "Selection & diagnostics", "lessonId": "srm_glm_select", "topics": ["glm", "learning"]},
            ],
        },
        {
            "id": "srm_u3",
            "number": 4,
            "title": "Time Series",
            "shortTitle": "TS",
            "cluster": "time_series",
            "weight": 0.12,
            "weightRange": "10–15%",
            "color": "#7C3AED",
            "description": "Stationarity, ARIMA family, smoothing.",
            "chapters": [
                {"id": "srm_ch5", "number": 5, "title": "Time series models", "lessonId": "srm_ts", "topics": ["time_series"]},
            ],
        },
        {
            "id": "srm_u4",
            "number": 5,
            "title": "Trees & Ensembles",
            "shortTitle": "Trees",
            "cluster": "trees",
            "weight": 0.22,
            "weightRange": "20–25%",
            "color": "#B45309",
            "description": "CART, bagging, RF, boosting.",
            "chapters": [
                {"id": "srm_ch6", "number": 6, "title": "Decision trees", "lessonId": "srm_trees", "topics": ["trees"]},
                {"id": "srm_ch7", "number": 7, "title": "Bagging, RF, boosting", "lessonId": "srm_ensembles", "topics": ["trees", "ensembles"]},
            ],
        },
        {
            "id": "srm_u5",
            "number": 6,
            "title": "PCA & Clustering",
            "shortTitle": "Unsup",
            "cluster": "pca_cluster",
            "weight": 0.13,
            "weightRange": "~10–15%",
            "color": "#BE185D",
            "description": "Unsupervised dimension reduction and segmentation.",
            "chapters": [
                {"id": "srm_ch8", "number": 8, "title": "PCA", "lessonId": "srm_pca", "topics": ["pca"]},
                {"id": "srm_ch9", "number": 9, "title": "Clustering", "lessonId": "srm_cluster", "topics": ["clustering"]},
            ],
        },
        {
            "id": "srm_u6",
            "number": 7,
            "title": "Wrap-up & Mocks",
            "shortTitle": "Wrap",
            "cluster": "wrap",
            "weight": 0.0,
            "weightRange": "last 2 weeks",
            "color": "#334155",
            "description": "Mixed review and full mocks.",
            "chapters": [
                {
                    "id": "srm_ch10",
                    "number": 10,
                    "title": "Mixed review — Learning & GLMs",
                    "lessonId": "srm_final",
                    "topics": ["learning", "glm", "linear"],
                    "levels": "review",
                },
                {
                    "id": "srm_ch11",
                    "number": 11,
                    "title": "Mixed review — TS, trees, PCA",
                    "lessonId": "srm_final",
                    "topics": ["time_series", "trees", "pca", "clustering"],
                    "levels": "review",
                },
                {
                    "id": "srm_ch12",
                    "number": 12,
                    "title": "Full mock 1",
                    "lessonId": "srm_final",
                    "topics": ["glm", "learning", "trees", "time_series", "pca"],
                    "levels": "full_mock",
                },
                {
                    "id": "srm_ch13",
                    "number": 13,
                    "title": "Weakness clinic",
                    "lessonId": "srm_final",
                    "topics": ["glm", "trees", "learning"],
                    "levels": "clinic",
                },
                {
                    "id": "srm_ch14",
                    "number": 14,
                    "title": "Full mock 2 + final",
                    "lessonId": "srm_final",
                    "topics": ["glm", "trees", "time_series", "pca", "clustering", "learning"],
                    "levels": "full_mock",
                },
            ],
        },
    ]


def q(num, stem, choices, answer, topics, cluster):
    return {
        "id": f"SRM-DRILL-{num}",
        "number": num,
        "exam": "SRM",
        "stem": stem,
        "stemRaw": stem,
        "choices": choices,
        "answer": answer,
        "lo": "SRM",
        "topics": topics,
        "cluster": cluster,
        "source": "SOA Grind authored SRM drill (not official SOA sample)",
        "quality": "drill",
        "qualityNotes": ["authored for course practice"],
        "images": [],
        "displayMode": "text",
    }


def build_srm_drill_bank() -> list[dict]:
    items = []
    n = 1

    def add(stem, choices, answer, topics, cluster):
        nonlocal n
        items.append(q(n, stem, choices, answer, topics, cluster))
        n += 1

    # Learning
    add(
        "Supervised learning requires:",
        {
            "A": "No labeled response variable",
            "B": "A labeled target Y for training",
            "C": "Only principal components",
            "D": "Only dendrograms",
            "E": "Only ARIMA orders",
        },
        "B",
        ["learning"],
        "learning",
    )
    add(
        "A model with excellent training performance but poor test performance is typically:",
        {
            "A": "Underfitting",
            "B": "Overfitting",
            "C": "Unbiased and efficient always",
            "D": "A perfect causal model",
            "E": "Impossible",
        },
        "B",
        ["learning"],
        "learning",
    )
    add(
        "k-fold cross-validation is mainly used to:",
        {
            "A": "Increase training R² only",
            "B": "Estimate out-of-sample performance / select models",
            "C": "Compute PCA loadings",
            "D": "Force stationarity",
            "E": "Replace all residual plots",
        },
        "B",
        ["learning"],
        "learning",
    )
    add(
        "Using a feature that is only known after the outcome occurs is an example of:",
        {
            "A": "Good practice",
            "B": "Data leakage risk",
            "C": "Bagging",
            "D": "An offset term",
            "E": "Seasonality",
        },
        "B",
        ["learning"],
        "learning",
    )

    # Linear / GLM
    add(
        "In a multiple linear regression, β_j is interpreted as:",
        {
            "A": "Correlation of Y with all X",
            "B": "Expected change in Y per unit X_j holding other predictors fixed",
            "C": "Always a causal effect",
            "D": "The R² contribution only",
            "E": "The residual variance",
        },
        "B",
        ["linear"],
        "linear_glm",
    )
    add(
        "R² measures:",
        {
            "A": "Causal identification",
            "B": "Fraction of variance in Y explained by the model (in-sample)",
            "C": "Test accuracy only",
            "D": "VIF",
            "E": "ACF at lag 1",
        },
        "B",
        ["linear"],
        "linear_glm",
    )
    add(
        "A GLM consists of a random component, a linear predictor, and a:",
        {
            "A": "Kernel density only",
            "B": "Link function",
            "C": "Dendrogram",
            "D": "Seasonal period only",
            "E": "Bootstrap forest only",
        },
        "B",
        ["glm"],
        "linear_glm",
    )
    add(
        "With a log link, a coefficient β=0.1 multiplies the mean by approximately:",
        {
            "A": "0.1",
            "B": "e^{0.1}",
            "C": "log(0.1)",
            "D": "1.1 without exponential always",
            "E": "0.9",
        },
        "B",
        ["glm"],
        "linear_glm",
    )
    add(
        "For binary outcomes, a common GLM choice is:",
        {
            "A": "Poisson with identity link only",
            "B": "Binomial with logit link (logistic regression)",
            "C": "k-means",
            "D": "PCA without Y",
            "E": "AR(1) only",
        },
        "B",
        ["glm"],
        "linear_glm",
    )
    add(
        "An offset in a count GLM is typically used to account for:",
        {
            "A": "Random forests",
            "B": "Exposure / population at risk",
            "C": "Principal component rotation",
            "D": "Seasonal dummy colors",
            "E": "Tree depth",
        },
        "B",
        ["glm"],
        "linear_glm",
    )
    add(
        "Compared with AIC, BIC generally:",
        {
            "A": "Penalizes complexity less",
            "B": "Penalizes complexity more for large n",
            "C": "Ignores the likelihood",
            "D": "Only applies to time series",
            "E": "Is identical always",
        },
        "B",
        ["glm", "learning"],
        "linear_glm",
    )
    add(
        "Multicollinearity in regression tends to:",
        {
            "A": "Reduce residual variance to zero always",
            "B": "Inflate coefficient standard errors and destabilize estimates",
            "C": "Guarantee causality",
            "D": "Remove the need for an intercept",
            "E": "Force R² negative",
        },
        "B",
        ["linear"],
        "linear_glm",
    )

    for beta in [0.05, 0.2, -0.1, 0.5]:
        # e^beta as answer concept - multiple choice approximate
        import math

        mult = math.exp(beta)
        add(
            f"Poisson GLM, log link, coefficient on rating factor = {beta}. "
            f"A one-unit increase multiplies expected count by about:",
            {
                "A": f"{mult:.4f}",
                "B": f"{beta}",
                "C": f"{1+beta:.4f}",
                "D": f"{-beta:.4f}",
                "E": f"{mult**2:.4f}",
            },
            "A",
            ["glm"],
            "linear_glm",
        )

    # Time series
    add(
        "A weakly stationary series has roughly constant:",
        {
            "A": "Only sample size",
            "B": "Mean and autocovariance structure over time",
            "C": "Forecast software version",
            "D": "Number of trees",
            "E": "PCA rank only",
        },
        "B",
        ["time_series"],
        "time_series",
    )
    add(
        "An AR(1) model expresses Y_t primarily as a function of:",
        {
            "A": "Only future values",
            "B": "Its own lagged value plus an error",
            "C": "Only a seasonal dummy without lag",
            "D": "Only PCA scores",
            "E": "Only a random forest leaf",
        },
        "B",
        ["time_series"],
        "time_series",
    )
    add(
        "Differencing in ARIMA is mainly used to:",
        {
            "A": "Increase seasonality always",
            "B": "Help achieve stationarity by removing stochastic trends",
            "C": "Compute VIF",
            "D": "Grow deeper trees",
            "E": "Replace cross-validation",
        },
        "B",
        ["time_series"],
        "time_series",
    )
    add(
        "Forecast intervals for many time series models typically:",
        {
            "A": "Shrink as the horizon increases",
            "B": "Widen as the horizon increases",
            "C": "Are always points with zero width",
            "D": "Ignore residual variance",
            "E": "Equal training R²",
        },
        "B",
        ["time_series"],
        "time_series",
    )
    add(
        "Exponential smoothing forecasts place relatively more weight on:",
        {
            "A": "The oldest observations only",
            "B": "More recent observations",
            "C": "Only PCA loadings",
            "D": "Only classification purity",
            "E": "Negative time only",
        },
        "B",
        ["time_series"],
        "time_series",
    )

    # Trees / ensembles
    add(
        "Deep unpruned decision trees tend to:",
        {
            "A": "Underfit always",
            "B": "Overfit training data",
            "C": "Have zero training error only if features are constant",
            "D": "Be identical to logistic regression",
            "E": "Ignore interactions",
        },
        "B",
        ["trees"],
        "trees",
    )
    add(
        "Pruning a tree using validation error aims to:",
        {
            "A": "Maximize training purity only",
            "B": "Balance fit vs generalization",
            "C": "Force more splits always",
            "D": "Remove the response variable",
            "E": "Compute ACF",
        },
        "B",
        ["trees"],
        "trees",
    )
    add(
        "Bagging reduces error mainly by:",
        {
            "A": "Increasing tree correlation always",
            "B": "Averaging many bootstrap trees to reduce variance",
            "C": "Deleting all features",
            "D": "Using a single unpruned tree only",
            "E": "Ignoring bootstrap samples",
        },
        "B",
        ["trees", "ensembles"],
        "trees",
    )
    add(
        "Random forests add randomness by:",
        {
            "A": "Using only one feature globally",
            "B": "Considering random feature subsets at splits (plus bagging)",
            "C": "Removing the response",
            "D": "Forcing linear splits only",
            "E": "Using test labels in training",
        },
        "B",
        ["trees", "ensembles"],
        "trees",
    )
    add(
        "Boosting builds models that:",
        {
            "A": "Ignore previous errors",
            "B": "Sequentially focus on residuals / hard examples",
            "C": "Are always unsupervised",
            "D": "Cannot overfit",
            "E": "Replace PCA",
        },
        "B",
        ["trees", "ensembles"],
        "trees",
    )
    add(
        "Out-of-bag (OOB) error in random forests approximates:",
        {
            "A": "Training purity only",
            "B": "Test / generalization error",
            "C": "ACF",
            "D": "VIF",
            "E": "Link function",
        },
        "B",
        ["trees", "ensembles"],
        "trees",
    )

    # PCA / clustering
    add(
        "The first principal component is the direction of:",
        {
            "A": "Minimum variance",
            "B": "Maximum variance",
            "C": "The response Y only",
            "D": "Time exclusively",
            "E": "Zero loadings always",
        },
        "B",
        ["pca"],
        "pca_cluster",
    )
    add(
        "Before PCA, when variables have different units, one should usually:",
        {
            "A": "Never scale",
            "B": "Standardize / scale features",
            "C": "Delete all continuous features",
            "D": "Use only the target as a feature",
            "E": "Force k=1 in k-means",
        },
        "B",
        ["pca"],
        "pca_cluster",
    )
    add(
        "k-means clustering is primarily:",
        {
            "A": "Supervised classification",
            "B": "Unsupervised segmentation",
            "C": "A GLM link",
            "D": "An ARIMA order",
            "E": "A boosting loss",
        },
        "B",
        ["clustering"],
        "pca_cluster",
    )
    add(
        "A dendrogram is associated with:",
        {
            "A": "Logistic regression coefficients only",
            "B": "Hierarchical clustering",
            "C": "Only exponential smoothing",
            "D": "Only bagging votes",
            "E": "Only R²",
        },
        "B",
        ["clustering"],
        "pca_cluster",
    )
    add(
        "PCA is often used to:",
        {
            "A": "Replace the need for any model validation",
            "B": "Reduce dimensionality / summarize correlated features",
            "C": "Forecast seasonal periods directly without data",
            "D": "Label supervised classes automatically always",
            "E": "Compute claim reserves from life tables",
        },
        "B",
        ["pca"],
        "pca_cluster",
    )

    # Mixed conceptual volume
    prompts = [
        (
            "Classification problems have a response that is primarily:",
            {
                "A": "Continuous numeric only",
                "B": "Categorical / class labels",
                "C": "A principal component score only",
                "D": "Always missing",
                "E": "A time index only",
            },
            "B",
            ["learning"],
            "learning",
        ),
        (
            "Heteroscedasticity in linear regression means:",
            {
                "A": "Constant residual variance",
                "B": "Non-constant residual variance",
                "C": "Perfect collinearity only",
                "D": "Zero R²",
                "E": "No intercept",
            },
            "B",
            ["linear"],
            "linear_glm",
        ),
        (
            "A logit link models:",
            {
                "A": "log(μ)",
                "B": "log(odds) = log(μ/(1−μ))",
                "C": "μ directly only",
                "D": "Only counts with identity",
                "E": "PCA eigenvalues",
            },
            "B",
            ["glm"],
            "linear_glm",
        ),
        (
            "Seasonality in a time series refers to:",
            {
                "A": "One-time level shifts only",
                "B": "Repeating patterns at fixed periods (e.g. monthly)",
                "C": "Only white noise",
                "D": "Only tree depth",
                "E": "Only VIF > 10",
            },
            "B",
            ["time_series"],
            "time_series",
        ),
        (
            "Variable importance in a random forest reflects:",
            {
                "A": "Alphabetical order of names",
                "B": "Contribution of features to reducing error / impurity across trees",
                "C": "Only the intercept",
                "D": "Only time order",
                "E": "Only test labels leaked in",
            },
            "B",
            ["trees", "ensembles"],
            "trees",
        ),
    ]
    for stem, ch, ans, top, cl in prompts:
        add(stem, ch, ans, top, cl)

    # more glm numeric
    for b0, b1, x in [(1.0, 0.5, 2.0), (0.0, 1.0, 0.0), (2.0, -0.5, 4.0)]:
        import math

        mu = math.exp(b0 + b1 * x)
        add(
            f"Log-link GLM: η = {b0} + {b1}·x. At x={x}, fitted mean μ equals:",
            {
                "A": f"{mu:.4f}",
                "B": f"{b0+b1*x:.4f}",
                "C": f"{b0*b1*x:.4f}",
                "D": f"{abs(b0-b1):.4f}",
                "E": f"{x:.4f}",
            },
            "A",
            ["glm"],
            "linear_glm",
        )

    return items


def update_catalog():
    cat = json.loads((DATA / "courses.json").read_text(encoding="utf-8"))
    for c in cat["courses"]:
        if c["id"] == "SRM":
            c["status"] = "ready"
            c["shortName"] = "Exam SRM"
            c["durationWeeks"] = 14
            c["examFormat"] = "35 MCQ · 3.5 hours · CBT"
            c["weights"] = SRM_WEIGHTS
            c["mix"] = {"reading": 0.40, "practice": 0.50, "mock": 0.10}
            c["description"] = (
                "COMPLETE track: learning, GLMs, time series, trees/ensembles, PCA/clustering — "
                "full path, lessons, drill bank, 14-week plan."
            )
            c["planPath"] = "data/courses/srm/plan.json"
            c["pathPath"] = "data/courses/srm/path.json"
            c["structure"] = "duo_path"
            c["syllabusNote"] = (
                "SOA SRM: Learning 5–10%, Linear/GLM 40–50%, Time series 10–15%, "
                "Trees 20–25%, PCA/clustering ~10–15%"
            )
        elif c["id"] == "PA":
            c["status"] = "next"
            c["description"] = "Next up after SRM. Not study-ready yet."
            c["planPath"] = None
            c["pathPath"] = None
            c["syllabusNote"] = "One-by-one queue — after SRM"
        elif c["id"] not in ("P", "FM", "FAM", "SRM"):
            c["status"] = "scaffold"
            c["planPath"] = None
            c["pathPath"] = None
    cat["version"] = 7
    cat["updated"] = TODAY
    cat["buildPolicy"] = "one_course_at_a_time"
    (DATA / "courses.json").write_text(json.dumps(cat, indent=2), encoding="utf-8")


def main():
    print("Building Exam SRM…")
    print("  START", START)

    lessons = json.loads((DATA / "lessons.json").read_text(encoding="utf-8"))
    lessons.update(srm_lessons())
    (DATA / "lessons.json").write_text(json.dumps(lessons, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  lessons", sum(1 for k in lessons if k.startswith("srm_")))

    all_q = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    base = [q for q in all_q if (q.get("exam") or "P") != "SRM"]
    drills = build_srm_drill_bank()
    all_q = base + drills
    (DATA / "questions.json").write_text(json.dumps(all_q, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  questions total={len(all_q)} SRM={len(drills)}")

    path = bac.build_path(
        "SRM",
        "Exam SRM — Statistics for Risk Modeling",
        srm_units(),
        SRM_WEIGHTS,
        "35 MCQ · 3.5 hours · CBT",
    )
    path["timeline"]["startDate"] = START.isoformat()
    path["timeline"]["endDate"] = (START + timedelta(weeks=WEEKS)).isoformat()
    path["timeline"]["notes"] = [
        "Heaviest time on linear models / GLMs (40–50% exam weight).",
        "Chapter tests ≥70% to unlock next chapter.",
        "Practice bank is authored SRM drills (not official SOA samples).",
    ]
    path = bac.assign_questions(path, all_q, "SRM")

    bac.START = START
    mods = bac.modules_from_path(path)
    plan = bac.build_calendar_plan(
        "SRM",
        "Exam SRM — Statistics for Risk Modeling",
        path,
        SRM_WEIGHTS,
        mods,
    )
    plan["notes"] = [
        "Primary progression is Path.",
        "Multi-level days OK.",
        "Last 2 weeks: wrap + mocks.",
        "40% reading / 50% practice / 10% mock.",
    ]
    plan = bac.assign_plan_days(plan, all_q, "SRM")

    SRM_DIR.mkdir(parents=True, exist_ok=True)
    (SRM_DIR / "path.json").write_text(json.dumps(path, indent=2, ensure_ascii=False), encoding="utf-8")
    (SRM_DIR / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    update_catalog()

    empty = 0
    for u in path["units"]:
        for ch in u["chapters"]:
            assert ch["lessonId"] in lessons, ch["lessonId"]
            for lv in ch["levels"]:
                if (lv.get("questionTarget") or 0) > 0 and not lv.get("assignedQuestionIds"):
                    empty += 1
    print(f"  path ch={path['stats']['chapters']} lv={path['stats']['levels']} empty={empty}")
    print(f"  plan days={len(plan['days'])} first={plan['days'][0]['date']}")
    print("DONE — Exam SRM ready")


if __name__ == "__main__":
    main()
