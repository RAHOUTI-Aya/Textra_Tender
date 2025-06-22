Modular Categorization
======
The primary objective of this component of the Textra Tender Project was to automatically categorize tenders based on their field activity zones using a scalable, context-aware approach. Rather than building and maintaining static lists of categories or keywords, a Large Language Model (LLM) was leveraged to dynamically infer and assign categories based on semantic content.

Methodology Overview
--------------------

Why an LLM-Based Approach?
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Traditional classification models often rely on fixed taxonomies, keyword matching, or supervised learning with structured labels. However, tenders often contain nuanced, domain-specific language that varies widely. Using an LLM allowed for:

- Contextual understanding of tender descriptions
- Generalization across industries without hardcoding sector definitions
- Scalability, as new tender formats or zones emerged

Workflow Breakdown
~~~~~~~~~~~~~~~~~~

**Step 1: Data Ingestion and Cleaning**

- Collected tender content from APIs, web scraping, or manual uploads.
- Preprocessing included basic cleaning (e.g., removing noise and formatting issues), but no stopword filtering or lemmatization, allowing the LLM to work with natural language inputs.

**Step 2: Prompt Engineering**

Structured prompts were designed to guide the LLM in interpreting and categorizing the tenders. For example:

.. code-block:: text
    :class: bright-blue

    Prompt Template:
    “Read the following tender description and identify the most appropriate field of activity it falls under (e.g., construction, ICT, logistics, consulting, etc.). Be precise and concise.”


This prompt was tested and refined to ensure consistency in the LLM's outputs.

**Step 3: LLM Inference**

- Tender descriptions were passed into the prompt templates.
- Responses were parsed to extract the predicted activity zone.
- OpenAI's GPT-4 API or a similar model was used for generation.

**Step 4: Confidence Scoring & Filtering**

- Optional: Added a second pass where the LLM justified the categorization. This was used for internal auditing or to flag uncertain results.
- Where confidence was low or output ambiguous, fallback prompts were issued or human review was triggered.

Modular Design of the Categorization System
-------------------------------------------

The entire system was built in modular blocks:

- **Inference Module**: Handles prompt construction and LLM interaction
- **Categorization Engine**: Parses LLM output into structured labels
- **Storage Module**: Stores categorized tenders in a database with metadata
- **Audit Module**: Allows logging, review, and correction of edge cases

This modularity allowed easy experimentation and upgrading (e.g., switching from GPT-4 to another model or improving prompts without refactoring core logic).

Example Output
--------------

For a tender like:

.. code-block:: text
    :class: bright-blue

    “The scope includes upgrading rural water infrastructure and installing solar-powered pumps across five regions.”


The LLM output would typically be:

- **Category**: ``Infrastructure / Renewable Energy``
- **Rationale (optional)**: ``This project involves construction and renewable energy technology for water access.``

Benefits of the LLM Approach
----------------------------

- **Reduced maintenance**: No need to update keyword lists or manually label data.
- **Flexible taxonomy**: Model could infer new or overlapping zones (e.g., “Green Infrastructure”).
- **Higher semantic accuracy**: Better at picking up context than traditional rule-based classifiers.

Challenges & Mitigations
-------------------------

+------------------------------------------+---------------------------------------------+
| **Challenge**                            | **Mitigation**                              |
+------------------------------------------+---------------------------------------------+
| Occasional vague or multi-category       | Improved prompt clarity and added           |
| outputs                                  | “single-best category” constraints          |
+------------------------------------------+---------------------------------------------+
| Latency of LLM inference at scale        | Batched processing and asynchronous calls   |
+------------------------------------------+---------------------------------------------+
| Cost of API usage                        | Used caching and tiered models for frequent |
|                                          | categories                                  |
+------------------------------------------+---------------------------------------------+
