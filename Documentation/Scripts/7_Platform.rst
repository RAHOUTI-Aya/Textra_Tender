Final Platform
===============

1. Overview
------------

Textra Tender is an intelligent digital platform designed to simplify and support the participation of suppliers in public and private tenders. The platform offers two separate user spaces: one for suppliers and one for clients, with the supplier space being the core focus of the system.

Textra Tender enables suppliers to:

- Describe the kind of tenders they’re looking for,
- Receive AI-scored recommendations with explanations,
- Interact with tender documents,
- Refine results through feedback,
- Generate submission documents based on company information,
- Track opportunities via a dashboard,
- Access learning content related to tender procedures.

2. User Access & Structure
---------------------------

**Authentication**

- **Registration & Login**: All users must register or log in to access their space.

**Two Workspaces**:

- **Supplier Space**
- **Client Space** (future or restricted use; not the focus of current implementation)

3. Supplier Space: Features and Workflow
-----------------------------------------

**Step 1: Tender Search Preferences Input**

The user specifies the profile of the tenders they are interested in by filling out a form that includes:

- *Secteur d'activité* (Field/Sector)
- *Date limite* (Deadline)
- *Localisation* (Geographic area)
- *Type d’entreprise* (SME, large company, etc.)
- *Forme juridique* (Legal structure)
- *Zone d'activité principale* (Main operational field)

**Step 2: AI-Based Tender Recommendations**

After form submission:

- The platform uses an LLM (Large Language Model) to select and score the 5 most relevant tenders based on the user's inputs.
- Each suggested tender includes:
    - A numerical score
    - A justification (why this tender is a good match)
    - A scrollable preview of the PDF document for full review

This makes it easier for suppliers to quickly assess which opportunities are worth pursuing.

**Step 3: User Feedback Loop**

The user can provide feedback on the relevance or suitability of the suggested tenders (e.g., “not aligned,” “too complex,” etc.).

- The platform reprocesses the tenders using the updated feedback to refine scores and deliver better-matching results.
- This creates an adaptive loop where the platform learns from user reactions.

**Step 4: Candidature Generation**

If a user chooses to apply for a tender:

- They proceed to a form where they fill in the company’s key information (name, size, certifications, references, etc.).
- Based on that input, the system automatically generates the documents required for submission (e.g., declaration forms, administrative letters, etc.), tailored to the specific tender requirements.

4. Dashboard & Analytics
-------------------------

The platform includes a user-specific dashboard that provides:

**Tender Statistics**:

- Most demanded sectors
- Active regions
- Common deadlines (*périodes de marché*)
- History of viewed and submitted tenders

**Insights** to help users better understand market trends.

5. Microlearning & Chatbot
---------------------------

To support supplier success:

- The platform includes a microlearning module offering short guides or videos on:
    - How to respond to tenders
    - Understanding qualification criteria
    - Document formatting and compliance norms
- A built-in chatbot assistant is available to answer common questions or clarify tender-related terminology and processes.

6. Summary of Key Features
---------------------------

.. list-table::
    :header-rows: 1

    * - Feature 
      - Description
    * - Login/Register 
      - Required to access personalized features
    * - Tender Request Form
      - User inputs preferred tender characteristics
    * - AI Recommendations
      - System shows top 5 matching tenders with scores and justifications
    * - Tender Document Preview
      - Users can scroll through the tender PDF before deciding
    * - User Feedback & Rescoring
      - Users give feedback, and the system adjusts tender relevance
    * - Candidature Submission
      - Generates personalized submission documents based on company info
    * - Dashboard
      - Displays market insights and user statistics
    * - Microlearning + Chatbot
      - Learning center and conversational assistant for guidance

7. Target Users
----------------

- Small and medium enterprises (SMEs)
- Freelancers or consulting firms
- Large suppliers seeking filtered tender opportunities
- New market entrants unfamiliar with formal tender procedures

