Scoring Approach
================

Objective
---------

The tender scoring module was designed to evaluate and prioritize tenders based on their relevance, strategic fit, and feasibility. The key goal was to assist internal teams in quickly identifying high-potential opportunities and filtering out tenders that were misaligned with business priorities. To achieve nuanced and adaptive scoring, a Large Language Model (LLM) was used rather than a rigid scoring matrix.

1. Why Use an LLM for Tender Scoring?
-------------------------------------

Scoring tenders requires analyzing unstructured, variable-length descriptions, often involving complex jargon and implicit signals. Traditional rule-based or weighted systems often:

- Struggle with context,
- Fail to adapt to different domains,
- Require heavy manual tuning.

By using an LLM, the scoring system benefits from:

- Contextual understanding of tender content,
- Semantic reasoning, including feasibility and competitiveness,
- Scalability without constant retraining.

2. Scoring Criteria
-------------------

Each tender was evaluated on multiple dimensions, inferred directly through natural language understanding:

.. list-table::
    :header-rows: 1

    * - Criterion
      - Description
    * - Relevance
      - How closely the tender aligns with Textra’s service offerings or strategic domains
    * - Complexity
      - Technical or logistical difficulty of execution
    * - Eligibility
      - Whether the requirements match Textra’s qualifications
    * - Estimated Value
      - Apparent commercial opportunity (explicit or inferred)
    * - Geographic Fit
      - Whether the region is within Textra’s operational scope
    * - Timeline Feasibility
      - Whether deadlines are achievable

3. LLM-Based Scoring Workflow
-----------------------------

**Step 1: Prompt Engineering**

The system uses structured prompts to request a breakdown of tender scoring. Example:

.. code-block:: text

    "You are an expert tender analyst. Read the following tender description and score it on the following criteria from 0 (poor) to 10 (excellent), with short justifications: relevance, complexity, eligibility, commercial opportunity, geographic fit, timeline feasibility."

This prompt produces both numerical scores and rationales for each dimension.

**Step 2: LLM Inference and Response Parsing**

Tender text is embedded into the prompt dynamically.

The LLM generates a structured response, for example:

.. code-block:: json

    {
      "relevance": 9,
      "relevance_reason": "The tender involves digital infrastructure, one of Textra’s core services.",
      "complexity": 6,
      "complexity_reason": "The project requires coordination across three government agencies.",
      "eligibility": 8,
      "eligibility_reason": "Textra meets the experience and certification requirements.",
      "commercial_opportunity": 7,
      "commercial_opportunity_reason": "Value not stated, but scope suggests a mid-size contract.",
      "geographic_fit": 9,
      "geographic_fit_reason": "Located in a region Textra is already active in.",
      "timeline_feasibility": 6,
      "timeline_feasibility_reason": "Tight deadlines, but achievable with a dedicated team."
    }

**Step 3: Aggregated Score Calculation**

A weighted average score is calculated (weights can be adjusted by project type):

.. math::

    \text{Final Score} = \sum_{i=1}^{n} w_i \times \text{Score}_i

Example weight scheme:

- Relevance (30%)
- Eligibility (20%)
- Commercial Value (15%)
- Geographic Fit (15%)
- Complexity (10%)
- Timeline (10%)

Result: Final Tender Score: 7.8/10

4. Modular Integration
-----------------------

Each component was modularized:

- **Scoring Engine**: Interacts with the LLM
- **Response Parser**: Extracts numerical values and reasons
- **Scoring Aggregator**: Computes final score and flags tenders
- **Reviewer Interface**: Displays LLM output for human review (optional)
- **Data Store**: Saves scores for analysis and dashboards

5. Benefits of the LLM Approach
-------------------------------

- **Interpretability**: Human-readable rationales improve trust and transparency
- **Adaptability**: Works across diverse sectors without retraining
- **Speed**: Tenders are scored in near real-time
- **Scalability**: Handles both structured and ambiguous tenders
