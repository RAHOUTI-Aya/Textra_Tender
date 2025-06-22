**Step 2: Prompt Engineering**

Structured prompts were designed to guide the LLM in interpreting and categorizing the tenders. For example:

.. raw:: html

    <span style="color: brightblue;">Prompt Template:
    “Read the following tender description and identify the most appropriate field of activity it falls under (e.g., construction, ICT, logistics, consulting, etc.). Be precise and concise.”</span>

This prompt was tested and refined to ensure consistency in the LLM's outputs.

Example Output
--------------

For a tender like:

.. raw:: html

    <span style="color: brightblue;">“The scope includes upgrading rural water infrastructure and installing solar-powered pumps across five regions.”</span>

The LLM output would typically be:

- **Category**: Infrastructure / Renewable Energy
- **Rationale (optional)**: “This project involves construction and renewable energy technology for water access.”
