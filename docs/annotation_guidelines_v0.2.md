# TenderLens Annotation Guidelines v0.2

## 1. Purpose

These guidelines define how requirements must be manually annotated for
TenderLens evaluation datasets.

The goal is to create a consistent ground-truth dataset for evaluating:

- requirement detection
- requirement classification
- mandatory status
- evidence grounding
- requirement granularity

The annotation policy must remain independent from model predictions.

Gold annotations must not be modified merely to improve model evaluation scores.

If the annotation policy changes, create a new dataset version instead of
overwriting previous gold files.

---

## 2. Core principle

### No requirement without evidence

Every annotated requirement must be directly supported by explicit text in
the source document.

Do not infer obligations, preferences, deadlines, deliverables, or evaluation
criteria that are not explicitly supported by the document.

The `evidence_text` field must contain the smallest sufficient source passage
that supports the annotation.

---

## 3. Annotation schema

Each annotation must follow this schema:

```json
{
  "id": "REQ-001",
  "tender_id": "...",
  "document_id": "...",
  "category": "Technical",
  "sub_category": "Architecture",
  "requirement_type": "Requirement",
  "description": "...",
  "mandatory": true,
  "source_document": "...pdf",
  "pdf_page": 1,
  "page_label": "1",
  "section": "...",
  "evidence_text": "literal source evidence"
}
```

**Allowed categories:**

- Technical
- Administrative
- Legal
- Financial
- Deadline
- Deliverable
- Eligibility
- Other

**Allowed requirement types:**

- Requirement
- EvaluationCriterion
- Deadline
- Deliverable

## 4. Requirement granularity

### 4.1 Atomicity
Annotate requirements at the smallest meaningful independent obligation.
One independently actionable obligation should normally correspond to one
annotation.
Example:
The vendor must provide:
- General Liability Insurance
- Cyber Liability Insurance
- Workers' Compensation Insurance

Annotate as three independent requirements if each item represents a distinct
obligation.
Do not collapse multiple independent obligations into one annotation merely
because they appear in the same sentence or list.
### 4.2 Parent and child requirements
When a parent statement only introduces a list of requirements, annotate the
individual child requirements and do not create an additional annotation for
the parent.
Example:
Proposals must include clearly defined service levels, including:
- response times
- resolution times
- uptime expectations

Annotate:
- response times
- resolution times
- uptime expectations
Do not additionally annotate:
Proposals must include clearly defined service levels.

The parent adds no independent obligation beyond introducing the list.
### 4.3 Parent with an independent obligation
Keep the parent when it contains information that represents an additional
independent requirement.
Example:
Submit one original and five copies of the following sections:
- Cover Letter
- Company Profile
- Technical Approach

Annotate:
1. Submit one original and five copies.
2. Include Cover Letter.
3. Include Company Profile.
4. Include Technical Approach.
The number of copies is an independent obligation and must not be lost.
### 4.4 Repeated requirements
If the same requirement is explicitly repeated in different sections of the
document, annotate each occurrence only if the occurrences represent distinct
documentary obligations or materially different context.
Do not automatically merge requirements across pages or sections.
Example:
A proposal guideline may require:
Include monthly recurring costs.

A later cost section may state:
All monthly recurring service fees must be clearly itemized.

These may be annotated separately because the second requirement adds an
itemization obligation.
If two passages are semantically and operationally identical, prefer one
canonical annotation unless the evaluation dataset is explicitly intended to
measure repeated evidence.
## 5. Requirement type

### 5.1 Requirement
Use Requirement when the text defines:
- an obligation
- a condition
- a required capability
- a qualification
- a responsibility
- an explicit preference
- a contractual or administrative requirement
Examples:
The vendor must support MFA.

The proposer should have municipal experience.

The selected vendor must provide proof of insurance.

### 5.2 EvaluationCriterion
Use EvaluationCriterion when the document explicitly states that something
will be:
- evaluated
- scored
- weighted
- compared
- ranked
- used in vendor selection
Example:
Technical Approach — 30 points.

This is an evaluation criterion, even if the proposal must also contain a
Technical Approach section.
The proposal-content obligation and the scoring criterion are separate
annotations when both are explicitly present.
### 5.3 Deadline
Use Deadline only for dates or time limits that impose an actionable temporal
obligation on the proposer, vendor, or selected contractor.
Examples:
Proposals must be received by June 8, 2026.

Questions must be submitted no later than May 20.

Do not classify internal procurement milestones as Deadline unless they impose
an explicit obligation on the proposer.
Examples that are normally NOT annotated as Deadline:
- Evaluation Period
- Notice of Award
- anticipated award date
- internal review period
A contract start date is not automatically a Deadline.
Annotate it only when the text creates an explicit temporal obligation for the
vendor.
### 5.4 Deliverable
Use Deliverable when the requirement concerns a concrete artifact or output
that must be submitted, produced, delivered, or provided.
Examples:
- report
- plan
- document
- file
- proposal section
- certificate
- architecture diagram
- implementation plan
Do not classify every vendor activity as a Deliverable.
Example:
Maintain firewall infrastructure.

This is a Requirement, not a Deliverable.
Example:
Submit a firewall migration plan.

This is a Deliverable.
## 6. Mandatory field

### 6.1 `mandatory = true`
Use true when the document clearly expresses an obligation.
Signals include:
- must
- shall
- required
- will be required
- is responsible for
- must include
- must provide
- must submit
- cannot / may not when expressing a prohibition
Example:
Proposals must include three references.

Result:
"mandatory": true

### 6.2 `mandatory = false`
Use false when the document explicitly expresses a preference or
non-mandatory characteristic.
Signals include:
- preferred
- desirable
- encouraged
- should
- preference will be given
- may include, when clearly optional
Example:
Experience with municipal clients is preferred.

Result:
"mandatory": false

Do not use false merely because a statement is an EvaluationCriterion.
### 6.3 `mandatory = null`
Use null when mandatory status cannot be determined from the source text.
Evaluation criteria will often use null because scoring something does not
necessarily mean it is mandatory.
Example:
Technical Approach — 30 points.

Result:
"mandatory": null

Use null rather than guessing.
## 7. Category rules
Category and requirement type are independent dimensions.
For example:
category = Eligibility
requirement_type = EvaluationCriterion

is valid.
### 7.1 Technical
Use for technical capabilities, architecture, systems, infrastructure,
software, cybersecurity, integration, performance, support, or implementation
requirements.
Examples:
- MFA
- VPN
- APIs
- firewall management
- backup capability
- uptime
- system integrations
- monitoring
### 7.2 Administrative
Use for proposal process, submission structure, procurement instructions,
contract administration, documentation format, procedural obligations, and
general non-technical submission requirements.
Examples:
- number of proposal copies
- required proposal sections
- formatting
- submission instructions
- acknowledgement of procurement terms
- renewal mechanics
- proposal completeness
### 7.3 Legal
Use only when the obligation primarily concerns an explicit legal, statutory,
regulatory, licensing, liability, indemnification, or legally binding
compliance requirement.
Examples:
- statutory compliance
- indemnification
- regulatory licensing
- legal liability clauses
- required legal certifications
Do not classify an item as Legal merely because it appears in a contract
section.
### 7.4 Financial
Use for pricing, fees, cost structure, financial statements, payment terms, or
cost evaluation.
Examples:
- recurring fees
- implementation costs
- separately itemized hardware
- pricing formula
- cost score
### 7.5 Deadline
Use when the primary semantic category is an actionable temporal deadline.
Examples:
- proposal due date
- question submission cutoff
This category usually pairs with:
requirement_type = Deadline

### 7.6 Deliverable
Use when the central concept is a concrete artifact or output rather than its
technical subject matter.
Examples:
- transition plan
- implementation report
- architecture document
A Deliverable may still have a domain-specific sub_category.
### 7.7 Eligibility
Use for vendor qualifications or conditions determining suitability,
experience, capacity, certifications, references, personnel qualifications, or
ability to participate.
Examples:
- years in business
- municipal experience
- references
- relevant project history
- staff qualifications
- required certifications
Vendor implementation track record or prior success should normally be
Eligibility rather than Technical.
### 7.8 Other
Use only when none of the defined categories meaningfully applies.
Other must not be used simply because classification is difficult.
## 8. Insurance annotation policy
Insurance requires an explicit annotation rule because it can reasonably be
interpreted as Legal, Administrative, or Eligibility.
TenderLens v0.2 uses the following policy:
Proof of insurance required from the vendor
Classify as:
category = Eligibility

when the requirement represents a condition the selected vendor must satisfy
or demonstrate.
Example:
The selected vendor must provide proof of Cyber Liability Insurance.

category = Eligibility
requirement_type = Requirement
mandatory = true

Proposal instructions about insurance information
Use:
category = Administrative

when the requirement primarily concerns what must be included in the proposal.
Example:
Coverage limits must be included in the proposal.

category = Administrative

Explicit legal or statutory insurance obligation
Use:
category = Legal

only when the source explicitly frames the requirement as a legal, statutory,
regulatory, or liability obligation.
## 9. Proposal contents
When a document explicitly requires a proposal section, form, attachment, or
artifact, annotate it.
Example:
Proposal must include a Technical Approach.

Possible annotation:
category = Deliverable
requirement_type = Deliverable
mandatory = true

Requirements describing what that section must contain should be annotated
separately.
Example:
Technical Approach must describe cybersecurity controls.

category = Technical
requirement_type = Requirement
mandatory = true

## 10. Qualifications and experience
Use Eligibility when a requirement evaluates or requires characteristics of
the vendor itself.
Examples:
- years in business
- staff qualifications
- references
- previous municipal projects
- successful similar implementations
- certifications
If such a characteristic is explicitly scored:
category = Eligibility
requirement_type = EvaluationCriterion

## 11. Responsibilities
Explicit vendor or proposer responsibilities must be annotated even when they
do not use the word "must".
Example:
It is each Proposer's responsibility to carefully review all requirements.

This is an explicit obligation.
requirement_type = Requirement
mandatory = true

Similarly:
It is the proposer's responsibility to request clarification if the RFP is
ambiguous.

must be annotated.
Do not discard these statements merely because they appear in narrative prose.
## 12. Conditional requirements
A requirement remains a requirement even when its activation depends on a
condition.
Example:
The Town may require the selected proposer to participate in negotiations.

Annotate the obligation.
The condition belongs in the normalized description.
Example:
If requested by the Town, the selected proposer must participate in
negotiations and submit resulting revisions.

Mandatory status should reflect the obligation once the stated condition is
triggered.
Use:
mandatory = true

when the conditional statement clearly creates an obligation after the
condition occurs.
## 13. Evidence text
evidence_text must:
- be copied from the source
- remain verbatim
- preserve enough context to support the annotation
- be as short as reasonably possible
- not contain invented or normalized wording
Do not use the normalized description as evidence.
Bad:
The vendor must implement secure authentication.

when those exact words do not appear in the source.
Good:
Multi-Factor Authentication (MFA) enforcement

when that is the source text supporting the requirement.
## 14. Description
description should normalize the source into a clear, standalone statement.
It may:
- expand implied subjects from surrounding context
- make list items understandable independently
- normalize grammar
- state conditional context
It must not:
- add unsupported requirements
- infer missing technical details
- convert preferences into mandatory obligations
- introduce technologies absent from the source
## 15. PDF page
pdf_page refers to the physical PDF page number used by the extraction
pipeline.
The first page in the PDF is:
pdf_page = 1

even when the printed page number differs.
## 16. Page label
page_label stores the printed/document page identifier when available.
Example:
pdf_page = 4
page_label = "3"

If no meaningful printed label exists:
"page_label": null

## 17. Section
Use the nearest meaningful source heading.
Example:
6. PROPOSAL EVALUATION CRITERIA

Do not invent a section name if none exists.
Use:
"section": null

when necessary.
## 18. Evaluation criteria and proposal requirements may coexist
Do not collapse these two concepts.
Example:
Proposal must include a Technical Approach.

and:
Technical Approach — 30 points.

These produce two annotations:
1. Required proposal component.
2. Evaluation criterion.
They represent different facts.
## 19. Annotation uncertainty
When unsure:
1. Prefer explicit documentary evidence over interpretation.
2. Do not infer an obligation.
3. Use mandatory = null when obligation status is genuinely unclear.
4. Avoid Other unless other categories clearly fail.
5. Record ambiguous annotation cases for later guideline review.
Do not silently change annotation policy case-by-case.
## 20. Dataset versioning
Gold datasets are immutable once frozen.
Existing datasets:
v0.1

must not be modified to conform to v0.2 rules.
New annotations created under these guidelines must use:
v0.2

or a later version.
Example:
snoqualmie_page_2_v0.2.json

Do not overwrite:
snoqualmie_page_2_v0.1.json

## 21. Development and test separation
Datasets used to modify prompts or extraction logic are development datasets.
Current policy:
Snoqualmie → DEV

Kingsbury v0.1 has already been inspected extensively and should be retained as
a historical benchmark rather than treated as a clean future test set.
A new unseen RFP should be annotated according to v0.2 and reserved as the next
TEST dataset.
Do not modify the extraction prompt based on errors observed in that test set.
## 22. Annotation checklist
Before accepting an annotation, verify:
- Is the requirement explicitly supported?
- Is evidence_text verbatim?
- Is the requirement atomic?
- Did I avoid unnecessary parent + child duplication?
- Is the type correct?
- Is the category correct according to these guidelines?
- Is mandatory status supported by the wording?
- Is the physical PDF page correct?
- Is the section correct?
- Did I avoid adding knowledge not present in the document?
Before freezing a dataset, review all annotations for consistency using the
same policy.