/* Topic guides used to lengthen today's lesson and align it with quiz topics */
window.SOA_TOPIC_GUIDES = {
  sets_venn: {
    label: "Sets & Venn / unions",
    techniques: [
      "Draw the Venn (or list regions) before writing equations.",
      "Convert “none / neither / at least one” into complements of unions.",
      "Use inclusion–exclusion; do not double-count pairwise intersections.",
      "For three sets, include the triple intersection with the correct sign.",
    ],
    formulas: [
      "P(A∪B)=P(A)+P(B)−P(A∩B)",
      "P(Aᶜ)=1−P(A)",
      "P(A∪B∪C)=ΣP − ΣP(∩) + P(A∩B∩C)",
      "P(none of A,B,C)=1−P(A∪B∪C)",
    ],
    examMoves: [
      "If given P(neither), you often have P(union) via complement.",
      "Policyholder classification tables are almost always multi-set counting.",
    ],
  },
  combinatorics: {
    label: "Counting (permutations & combinations)",
    techniques: [
      "Ask: does order matter? Roles → permutations; committees/hands → combinations.",
      "Use the fundamental counting rule for sequential choices.",
      "With replacement vs without replacement changes the model.",
      "When outcomes are equally likely: P = favorable / total.",
    ],
    formulas: [
      "P(n,k)=n!/(n−k)!",
      "C(n,k)=n!/(k!(n−k)!)",
      "Multinomial: n!/(n1! n2! …)",
    ],
    examMoves: [
      "Urn problems: write the denominator sizes carefully each draw.",
      "“Same color / different color” → mutually exclusive cases, then add.",
    ],
  },
  conditional_bayes: {
    label: "Conditional probability & Bayes",
    techniques: [
      "Write the definition: P(A|B)=P(A∩B)/P(B).",
      "Build a probability tree for multi-stage experiments.",
      "Total probability: partition the sample space, then average.",
      "Bayes: reverse conditioning — posterior ∝ likelihood × prior.",
    ],
    formulas: [
      "P(A∩B)=P(A)P(B|A)=P(B)P(A|B)",
      "P(A)=Σ P(A|Bi)P(Bi)",
      "P(Bi|A)=P(A|Bi)P(Bi)/Σ P(A|Bj)P(Bj)",
    ],
    examMoves: [
      "Insurance risk classes + “given a claim” → Bayes, not raw prior.",
      "Restrict the denominator to the conditioning event only.",
    ],
  },
  total_prob: {
    label: "Law of total probability",
    techniques: [
      "Identify a partition (risk class, machine type, prior state).",
      "Weight each branch by its prior probability.",
      "Then apply Bayes if the question reverses the conditioning.",
    ],
    formulas: ["P(A)=Σ_i P(A|Bi)P(Bi)  for a partition {Bi}"],
    examMoves: ["If the stem gives rates within groups and group sizes, total probability is the bridge."],
  },
  independence: {
    label: "Independence vs mutually exclusive",
    techniques: [
      "Independent: P(A∩B)=P(A)P(B) or P(A|B)=P(A).",
      "Mutually exclusive: A∩B=∅ so P(A∩B)=0.",
      "Nontrivial events cannot be both independent and mutually exclusive.",
    ],
    formulas: ["Independence ⇒ P(A∪B)=P(A)+P(B)−P(A)P(B)"],
    examMoves: ["Check the stem for the word “independent” before using a product."],
  },
  discrete_rv: {
    label: "Discrete random variables",
    techniques: [
      "State the support (possible values) before writing the PMF.",
      "Match story → family: fixed n trials (binomial), rare counts (Poisson), without replacement (hypergeometric), trials until r successes (NB).",
      "Compute E[X] and Var(X) with the correct formulas for that family.",
    ],
    formulas: [
      "Binomial(n,p): E=np, Var=np(1−p)",
      "Poisson(λ): E=Var=λ",
      "Var(X)=E[X²]−(E[X])²",
    ],
    examMoves: ["Clarify whether geometric counts trials or failures — wording matters."],
  },
  continuous_rv: {
    label: "Continuous random variables",
    techniques: [
      "Probabilities are areas: integrate the PDF over an interval.",
      "P(X=exact point)=0 for continuous X.",
      "Percentile π_p solves F(π_p)=p.",
      "Survival S(x)=P(X>x) is often faster for insurance tails.",
    ],
    formulas: [
      "F(x)=∫_{−∞}^x f",
      "E[X]=∫ x f(x) dx",
      "For X≥0, E[X]=∫_0^∞ S(x) dx (when applicable)",
    ],
    examMoves: ["Always check support endpoints before integrating."],
  },
  normal: {
    label: "Normal distribution",
    techniques: [
      "Standardize: Z=(X−μ)/σ ~ N(0,1).",
      "Use the exam normal table for Φ(z).",
      "Symmetry: Φ(−z)=1−Φ(z).",
    ],
    formulas: ["P(X≤x)=Φ((x−μ)/σ)"],
    examMoves: ["Do not integrate the normal PDF by hand — standardize and table."],
  },
  expectation_var: {
    label: "Expectation & variance",
    techniques: [
      "Linearity always works: E[aX+b]=aE[X]+b even without independence.",
      "Var(aX+b)=a²Var(X).",
      "For E[g(X)], use LOTUS — do not require the distribution of g(X) first unless asked.",
    ],
    formulas: [
      "Var(X)=E[X²]−(E[X])²",
      "Independent ⇒ Var(X+Y)=VarX+VarY",
    ],
    examMoves: ["Compute E[X²] carefully for discrete tables."],
  },
  insurance: {
    label: "Insurance payment variables",
    techniques: [
      "Define ground-up loss X vs insurer payment Y.",
      "Ordinary deductible d: Y=(X−d)+.",
      "Policy limit u: Y=min(X,u).",
      "Coinsurance α multiplies the payment after other modifications — read order carefully.",
      "Per loss includes zeros; per payment conditions on payment > 0.",
    ],
    formulas: [
      "E[(X−d)+]=∫_d^∞ S(x) dx  (X≥0 continuous, common case)",
      "Exponential mean θ: E[(X−d)+]=θ e^{−d/θ}",
    ],
    examMoves: ["Underline deductible / limit / coinsurance / inflation order before integrating."],
  },
  joint: {
    label: "Joint / marginal / conditional",
    techniques: [
      "Marginal: sum (or integrate) out the other variable.",
      "Conditional: joint / marginal.",
      "Independence: joint factors into product of marginals.",
    ],
    formulas: [
      "p_X(x)=Σ_y p(x,y)",
      "p(y|x)=p(x,y)/p_X(x)",
      "Cov(X,Y)=E[XY]−E[X]E[Y]",
    ],
    examMoves: ["Build the joint table first; most errors are wrong margins."],
  },
  order_stats: {
    label: "Order statistics",
    techniques: [
      "For i.i.d. continuous sample: CDF of max is [F(x)]^n.",
      "CDF of min uses 1−[1−F(x)]^n.",
    ],
    formulas: [
      "P(X_{(n)}≤x)=[F(x)]^n",
      "P(X_{(1)}>x)=[1−F(x)]^n",
    ],
    examMoves: ["“Largest claim / first failure” language → order stats."],
  },
  clt: {
    label: "Central Limit Theorem",
    techniques: [
      "Sums and means of i.i.d. finite-variance RVs become approximately normal.",
      "Standardize with the correct SE: σ/√n for the mean, σ√n for the sum.",
    ],
    formulas: [
      "X̄ ≈ N(μ, σ²/n)",
      "S_n ≈ N(nμ, nσ²)",
    ],
    examMoves: ["Identify n, μ, σ before writing Z."],
  },
  general_misc: {
    label: "General probability tools",
    techniques: [
      "Translate words → events before computing.",
      "Choose complement when “at least / none” appears.",
      "Keep a consistent definition of the random variable X.",
    ],
    formulas: [],
    examMoves: ["If stuck, redefine X in one sentence, then write the target probability in symbols."],
  },
};
