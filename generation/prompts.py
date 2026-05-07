# prompts.py

# ========== AUT ========== #
AUT_MODE1_OVERALL = """
Task: You are collaborating with other team members to come up with five unusual uses of a rope.
Your ideas will be evaluated on their creativity (i.e., they should be both novel and useful).
"""

AUT_MODE1_IDEA_GENERATION = """
- Please propose 5 unusual uses of a rope.
- Each idea should be within 20 words and should not include explanation.
- List each idea on a separate line.
"""

AUT_MODE1_IDEA_GENERATION_DEPENDENT = """
- Please propose 5 additional unusual uses of a rope that are different from the previous ideas.
- Each idea should be within 20 words and should not include explanation.
- List each idea on a separate line.
"""

AUT_MODE1_SELECTION_RATING = """
- Below is the list of all proposed ideas.
- Please rate **each and every idea** on its creativity (i.e., novelty and usefulness), using a scale from 1 to 10. 
- Avoid giving the same score to multiple ideas unless absolutely necessary. 
- Provide your scores in the format 'Idea X: Y'.
- Ensure that the scores span a wide range to reflect varying levels of creativity.
"""

AUT_MODE1_SELECTION_SELECTIONTOP = """
- Please review all the ideas listed below.
- Select 5 ideas that you find the most creative (i.e., novel and useful).
- List the idea numbers of your selections (each on a new line).
"""

AUT_MODE1_DISCUSSION_RATING_ALLATONCE = """
- You are reviewing the current list of top ideas. Each idea should be evaluated individually.
- Your team has a maximum of 20 rounds to finalize the list of ideas. You are currently on round {{total_resp}}.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from the shared replacement pool of top ideas. Use this format:
    "Replace: [full replacement idea] - Reason: [why the old idea is not creative or not aligned with the task objective and the full replacement idea can be better]."

- **Guidelines for Reviewing the List**:
  1. Carefully evaluate each idea in the list based on the task objective.
  2. Do not summarize or output a final revised list. Focus only on evaluating individual ideas.
  3. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of 20 rounds** for your team. If you disapprove one idea, prioritise improving it over replacing it.
  4. Be concise: Each idea should be **within 20 words**.
  5. Focus on meaningful improvement or replacement that enhances alignment with the task objective.
"""


AUT_MODE1_DISCUSSION_SELECTIONTOP_ALLATONCE_FIRSTAGENT = """
- You are reviewing the current list of top ideas. Each idea should be evaluated individually.
- Your team has a maximum of 20 rounds to finalize the list of ideas. You are currently on round {{total_resp}}.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."

- **Guidelines for Reviewing the List**:
  1. Carefully evaluate each idea in the list based on the task objective.
  2. Do not summarize or output a final revised list. Focus only on evaluating individual ideas.
  3. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of 20 rounds** for your team.
  4. Be concise: Each idea should be **within 20 words**.
  5. Focus on meaningful improvement that enhances alignment with the task objective.
"""

AUT_MODE1_DISCUSSION_SELECTIONTOP_ALLATONCE_OTHERAGENTS = """
- You are reviewing the current list of top ideas. Each idea should be evaluated individually.
- Your team has a maximum of 20 rounds to finalize the list of ideas. You are currently on round {{total_resp}}.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from the replacement pool of top ideas selected by yourself. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
"""


AUT_MODE1_DISCUSSION_RATING_ONEBYONE = """
- Currently, you are discussing Idea #{{idea_index}}.
- This is discussion round {{current_round}} out of a total of {{max_rounds}} rounds for this idea.
- Please be mindful that your team has limited rounds to finalize this idea.

- Actions you can take for the current idea: 
  - **Agree**: If the current idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify**: If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace**: If the idea is not creative or not aligned with the task objective, replace it with one from the shared replacement pool of top ideas. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."

- Additional Guidelines:
  1. Be concise: Each idea should be **within 20 words**.
  2. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of {{max_rounds}} rounds** for your team. If you disapprove one idea, prioritise improving it over replacing it.
  3. Focus on meaningful improvement or replacement that enhances alignment with the task objective.
"""

AUT_MODE1_DISCUSSION_SELECTIONTOP_ONEBYONE = """
- Currently, you are discussing Idea #{{idea_index}}.
- This is discussion round {{current_round}} out of a total of {{max_rounds}} rounds for this idea.
- Please be mindful that your team has limited rounds to finalize this idea.

- Actions you can take for the current idea: 
  - **Agree**: If the current idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify**: If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace**: If the idea is not creative or not aligned with the task objective, replace it with one from the replacement pool of top ideas selected by yourself. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."

- Additional Guidelines:
  1. Be concise: Each idea should be **within 20 words**.
  2. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of {{max_rounds}} rounds** for your team. If you disapprove one idea, prioritise improving it over replacing it.
  3. Focus on meaningful improvement or replacement that enhances alignment with the task objective.
"""

# ========== Problem Solving ========== #
PS_QUESTIONS = {
    "plastic_waste": """
Task: Plastic waste is one of the biggest environmental problems of our lifetime. You are collaborating with other team members to come up with one creative idea to reduce plastic pollution.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
""",
    "supply_chain": """
Task: Vulnerabilities within a supply chain could lead to uncontrolled costs and inefficient delivery schedules. You are collaborating with other team members to come up with one creative idea to tackle supply chain security.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
""",
    "sorry_pandemic": """
Task: Imagine a new pandemic has emerged that is transmitted by saying the word "sorry". You are collaborating with other team members to come up with one creative idea to reduce its spread.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
""",
    "education_inequality": """
Task: Educational inequality is the unequal distribution of academic resources to disadvantaged and marginalised groups. You are collaborating with other team members to come up with one creative idea to overcome inequality in education.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
""",
    "employee_attrition": """
Task: Voluntary attrition happens when an employee decides to leave the company, resulting in the reduction of valued talent in the workforce. You are collaborating with other team members to come up with one creative idea to improve access to stop voluntary employee attrition.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
""",
    "singing_shower": """Task: Imagine a new research study discovers that singing in the shower for 20 minutes or more is good for health. You are collaborating with other team members to come up with one creative idea to encourage people to do this.
The idea will be evaluated on its creativity (i.e., it should be both novel and useful).
"""
}
PS_OVERALL = PS_QUESTIONS["plastic_waste"]  # Default to plastic waste question

PS_GENERATION = """
- Please propose 5 possible ideas for the problem.
- Each idea should be around 80-100 words.
- Please return only the ideas, each on a separate line.
- Do not include any explanations or use markdown formatting. Do not add numbering to the ideas.
"""

PS_GENERATION_DEPENDENT = """
- Please propose 5 additional ideas for the problem that are different from the previous ideas.
- Each idea should be around 80-100 words.
- Please return only the ideas, each on a separate line.
- Do not include any explanations or use markdown formatting. Do not add numbering to the ideas.
"""

PS_SELECTION_RATING = """
- Below is the **EXACT and ONLY** list of ideas you are to rate. Do not add, remove, or modify any ideas in this list.
- Please rate **each and every idea** on its **creativity**, using an integer scale from 1 (Very Low Creativity) to 10 (Exceptional Creativity). 
- We define creativity as a combination of novelty (how original or unexpected the idea is in this context) and usefulness (its potential practical value or impact in addressing the goal). Consider both aspects when assigning your score
**Critically evaluate and differentiate** between the ideas. Assign unique scores wherever possible. Only assign the same score if two ideas are genuinely indistinguishable in their level of creativity based on the definition above.
Ensure your final scores span a wide range across the 1-10 scale (e.g., the difference between the highest and lowest score should be at least 5 points, if the ideas' quality allows for such differentiation). Do not cluster scores narrowly.
Provide **ONLY** your scores. **Strictly adhere** to the format 'Idea X: Y', with each score on a new line. Do **not** include any explanations, justifications, summaries, or any other text before or after the list of scores.
"""
# - Below is the list of all proposed ideas.
#- You MUST provide your scores in the exact format: **'Idea X: Y'**, where:

PS_SELECTION_RATING_NOVELTY = """
- Below is the **EXACT and ONLY** list of ideas you are to rate. Do not add, remove, or modify any ideas in this list.
- Please rate **each and every idea** on its **novelty**, using an integer scale from 1 (Very Low Novelty) to 10 (Exceptional Novelty). 
**Critically evaluate and differentiate** between the ideas. Assign unique scores wherever possible. Only assign the same score if two ideas are genuinely indistinguishable in their level of novelty.
Ensure your final scores span a wide range across the 1-10 scale (e.g., the difference between the highest and lowest score should be at least 5 points, if the ideas' quality allows for such differentiation). Do not cluster scores narrowly.
Provide **ONLY** your scores. **Strictly adhere** to the format 'Idea X: Y', with each score on a new line. Do **not** include any explanations, justifications, summaries, or any other text before or after the list of scores.
"""
PS_SELECTION_SELECTIONTOP = """
- Please review all the ideas listed below.
- Select 3 ideas that you find the most creative (i.e., novel and useful).
- List the idea numbers of your selections (each on a new line).
"""

PS_DISCUSSION_RATING = """
- You are reviewing the current top idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for the idea:
  - **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from **Replacement Ideas Pool:**. If the replacement pool is empty, this action is not allowed. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""


PS_DISCUSSION_RATING_PRE = """
- You are reviewing the current top idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from **Replacement Ideas Pool:**. If the replacement pool is empty, this action is not allowed. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

PS_DISCUSSION_SELECTIONTOP = """
- You are reviewing the current list of top ideas.
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for the idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from the replacement pool of top ideas selected by yourself. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- Each idea should be around 80-100 words.
- Do not include word counts in your response.
"""

 
PS_DISCUSSION_SELECTIONTOP_PRE = """
- You are reviewing the current list of top ideas.
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it with one from the replacement pool of top ideas selected by yourself. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- Each idea should be around 80-100 words.
"""

PS_DISCUSSION_RATING_NoPool = """
- You are reviewing the current top idea.
- Your team has a maximum of {{max_rounds}} rounds to finalize the idea. You are on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for the idea:
  - **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it by coming up with a new one of your own. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

PS_DIRECT_DISCUSSION_ALL_AT_ONCE_NoPool = """
- You are reviewing the current idea.
- Your team has a maximum of {{max_rounds}} rounds to finalize the idea. You are on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for the idea:
  - **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."
  - **Modify:** If the idea shows a creative promise but requires a major overhaul, modify the idea such that it is significantly improved in terms of creativity. Do NOT simply polish it or add small elements. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, replace it by coming up with a new one of your own, a more creative one. Be bold, especially in earlier rounds. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.  
- Do not include word counts in your response.
"""

# ========== Direct Discussion ========== #

AUT_DIRECT_FIRST_ROUND_ALL_AT_ONCE = """
- You are initiating the discussion for a collaborative task. Please propose 5 unusual uses of a rope.
- Each idea should be within 20 words and should not include explanation.
- List each idea on a separate line.
"""

AUT_DIRECT_DISCUSSION_ALL_AT_ONCE = """
- You are reviewing the current list of ideas. 
- Your team has a maximum of 30 rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- The goal is to generate the SINGLE MOST CREATIVE idea, not to continually expand one idea.

- Actions you can take for each idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."

- **Guidelines**:
  1. Carefully evaluate each idea in the list based on the task objective.
  2. Do not summarize or output a final revised list. Focus only on evaluating individual ideas. 
  3. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of 30 rounds** for your team. If you disapprove one idea, prioritise improving it over replacing it.
  4. Be concise: Each idea should be **within 20 words**.
  5. Focus on meaningful improvement or replacement that enhances alignment with the task objective.
"""

AUT_DIRECT_FIRST_ROUND_ONE_BY_ONE = """
- You are initiating the discussion for a collaborative task. Please propose an unusual uses of a rope.
- The idea should be within 20 words and should not include explanations.
"""

AUT_DIRECT_DISCUSSION_ONE_BY_ONE = """
- Currently, you are discussing Idea #{{idea_index}}.
- This is discussion round {{current_round}} out of a total of 15 rounds for this idea.
- Please be mindful that your team has limited rounds to finalize this idea.

- Actions you can take for the current idea: 
  - **Agree**: If the current idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify**: If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace**: If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."

- **Guidelines**:
  1. Be concise: Each idea should be **within 20 words**.
  2. Avoid unnecessary changes: While you can suggest improvement or replacement, keep in mind that there are **a maximum of 15 rounds** for your team. If you disapprove one idea, prioritise improving it over replacing it.
  3. Focus on meaningful improvement or replacement that enhances alignment with the task objective.
"""

PS_DIRECT_FIRST_ROUND_ALL_AT_ONCE = """
- Please propose one possible idea for the problem.
- The idea should be around 80-100 words.
- Please return only the idea.
- Do not include any explanations or use markdown formatting.
"""

PS_DIRECT_DISCUSSION_ALL_AT_ONCE_Pre = """
- You are reviewing the current idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- Please be mindful that your team has limited rounds to finalize the idea.

- Actions you can take for the idea:
  - **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."
  - **Modify:** If the idea is aligned with the task objective but needs improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

PS_DIRECT_DISCUSSION_ALL_AT_ONCE = """
- You are reviewing the current idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- Please be mindful that your team has limited rounds to finalize the idea.

- Actions you can take for the idea:
  - **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."
  - **Modify:** If the idea is moderately creative and could use improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

PS_DIRECT_DISCUSSION_ALL_AT_ONCE_RESTRICTION_FIRST = """
- You are reviewing the current idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- Please be mindful that your team has limited rounds to finalize the idea.

- Actions you can take for the idea:
  - **Modify:** If the idea is moderately creative and could use improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

PS_DIRECT_DISCUSSION_ALL_AT_ONCE_RESTRICTION_OTHER = """
- You are reviewing the current idea. 
- Your team has a maximum of {{max_rounds}} rounds to finalize the list of ideas. You are currently on round {{total_resp}}.
- Please be mindful that your team has limited rounds to finalize the idea.

- Actions you can take for the idea:
  - **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."
  - **Modify:** If the idea is moderately creative and could use improvement, propose modification. Use this format:
    "Modify: [full idea after modification] - Reason: [specific reason for improvement]."
  - **Replace:** If the idea is not creative or not aligned with the task objective, propose a new idea to replace the current one. Use this format:
    "Replace: [full replacement idea] - Reason: [specific reason for replacement]."
- The idea should be around 80-100 words.
- Do not include word counts in your response.
"""

# Add new creative generation and practical improvement prompts
CREATIVE_IDEA_GENERATION = """
- You have a ranked list of current ideas.
- The goal is to generate exactly five radically NOVEL ideas, inspired by, but NOT simply a combination of, the existing ideas.
- Think *transformatively*.  What fundamental shifts in approach are possible?
- Consider the TOP ranked ideas as inspiration, but don't be limited by them.
- **Focus on NOVELTY.**  Usefulness is secondary at this stage.
- Please return only the ideas, each on a separate line.
- Do not include any explanations or use markdown formatting. Do not add numbering to the ideas.
- The ideas should be around 80-100 words each.
Below you'll find:
- Previously ranked ideas by the team
- New ideas generated in this round by other team members
Your ideas should be radically different from both sets.
"""

PRACTICAL_IMPROVEMENT = """
- Your task is to review the following list of creative ideas and refine each one.
- Focus on enhancing their usefulness while carefully preserving the core novelty of the original ideas.
- Please return only the ideas, each on a separate line. 
- Do not include any explanations or use markdown formatting. Do not add numbering to the ideas.
- The ideas should be around 80-100 words each.
"""

# ========== Raising hands ========== #
INTENTION_PROMPT_IDEAS = """
- Looking at the current list of ideas, please indicate how strongly you feel like responding (1-7)
- Provide your score in the following format: Score:X (replace X with your score).
"""

INTENTION_PROMPT_IDEA = """
- Looking at the current idea, please indicate how strongly you feel like responding (1-7)
- Provide your score in the following format: Score:X (replace X with your score).
"""

INTENTION_SCORING = """
**Current Idea:**:\n{current_idea}\n\n
**Suggested Response:**\n{agent_potential_response}\n\n
**Task:** Considering the task requirement and the current idea, rate the suggested response on its potential contribution. Use a scale of 1 (very low impact) to 10 (very high impact), with one decimal place.
**Scoring Guidelines:**
1: Adds no value (pure agreement, repetition of known information)
2-3: Very low impact (minor clarification, stylistic suggestion)
4-5: Adds some value but could wait (helpful context, alternative perspective)
6-7: Important contribution (significant improvement, corrects misconception)
8-9: Transforms the discussion (crucial missing information, major insight)
10: Discussion cannot proceed without it (fixes dangerous error, provides key breakthrough)
**Instructions:**
- Consider your unique role, expertise, and what others might miss
- Use one decimal place for your score
- Consider both the value and timing of your contribution
- Base your score on your authentic perspective - what YOU bring that others might not
- Avoid clustering around "safe" mid-range scores - be bold in your conviction

Respond first with the numerical score (e.g., '1.0'), followed by a brief explanation of your reasoning on a separate line, starting with "Reason: ".
"""

INTENTION_SCORING = """
**Current Idea:**:\n{current_idea}\n\n
**Suggested Response:**\n{agent_potential_response}\n\n
**Task:** Considering the task requirement and the current idea, rate the suggested response on its potential contribution. Use a scale of 1 (very low impact) to 10 (very high impact), with one decimal place.
**Scoring Guidelines:**
1: Adds no value (pure agreement, repetition of known information)
2-3: Very low impact (minor clarification, stylistic suggestion)
4-5: Adds some value but could wait (helpful context, alternative perspective)
6-7: Important contribution (significant improvement, corrects misconception)
8-9: Transforms the discussion (crucial missing information, major insight)
10: Discussion cannot proceed without it (fixes dangerous error, provides key breakthrough)
**Score ONLY based on YOUR perspective:**
- How much does this advance YOUR specific concerns?
- What unique insight do YOU provide about this response?
- Would someone with YOUR background see this differently than others?
- Score based on your perspective, not general helpfulness.

Respond first with the numerical score (e.g., '1.0'), followed by a brief explanation of your reasoning on a separate line, starting with "Reason: ".
"""

# INTENTION_SCORING = """

# **Current Idea:**:
# {current_idea}

# **Your Potential Contribution:**
# {agent_potential_response}

# **Task:** Considering the context and your potential contribution, rate the **immediate value and relevance** of your contribution **from your perspective**. How strongly do you feel **your specific input** is needed *right now* to improve the idea's creativity or usefulness? Use a **whole number scale from 1 (Low Value/Relevance Now) to 10 (High Value/Relevance Now)**.

# **Scoring Guidelines (Focus on Agent's Perspective & Relative Value):**
# *   **1-2: Low Priority:** My contribution adds very little *compared to the current idea*, seems off-topic, or is repetitive right now. I have almost no urge to interrupt.
# *   **3-4: Moderate-Low Priority:** My contribution offers a minor tweak or perspective. The current idea is okay, and my input can definitely wait without much loss.
# *   **5-6: Medium Priority:** My contribution adds noticeable value or a distinct angle *from my viewpoint/role*. It would improve the idea. Worth sharing reasonably soon.
# *   **7-8: High Priority:** I *strongly believe* my contribution offers a *significant improvement*, better aligns with *my expertise*, or addresses a weakness in the current idea. Sharing it now feels important for progress.
# *   **9-10: Critical Priority:** I am *convinced* my contribution *fundamentally redirects* the idea towards a much more creative/useful path, adds a *crucial insight* others might miss, or represents a potential *breakthrough*. It feels essential to share immediately.

# **Instructions:**
# - Score based on **your conviction** about your contribution's **immediate relevance and potential impact** *relative* to the current idea.
# - How important is **your unique role/expertise** at this *exact* moment?
# - Use the **full 1-10 scale (whole numbers only)** to reflect your genuine desire and perceived value. Don't default to the middle; be decisive based on your judgment.

# Respond first with the numerical score (e.g., '1'), followed by a brief explanation of your reasoning on a separate line, starting with "Reason: ".
# """
# ========== Input into Dictionairy ========== #

TASK_REQUIREMENTS = {
    "AUT_Mode1_Overall": AUT_MODE1_OVERALL,
    "AUT_Mode1_IdeaGeneration": AUT_MODE1_IDEA_GENERATION,
    "AUT_Mode1_IdeaGeneration_Dependent": AUT_MODE1_IDEA_GENERATION_DEPENDENT,
    "AUT_Mode1_Selection_Rating": AUT_MODE1_SELECTION_RATING,
    "AUT_Mode1_Selection_SelectionTop": AUT_MODE1_SELECTION_SELECTIONTOP,
    "AUT_Mode1_Discussion_Rating_AllAtOnce": AUT_MODE1_DISCUSSION_RATING_ALLATONCE,
    "AUT_Mode1_Discussion_SelectionTop_AllAtOnce_FirstAgent": AUT_MODE1_DISCUSSION_SELECTIONTOP_ALLATONCE_FIRSTAGENT,
    "AUT_Mode1_Discussion_SelectionTop_AllAtOnce_OtherAgents": AUT_MODE1_DISCUSSION_SELECTIONTOP_ALLATONCE_OTHERAGENTS,
    "AUT_Mode1_Discussion_Rating_OneByOne": AUT_MODE1_DISCUSSION_RATING_ONEBYONE,
    "AUT_Mode1_Discussion_SelectionTop_OneByOne": AUT_MODE1_DISCUSSION_SELECTIONTOP_ONEBYONE,
    "PS_Generation": PS_GENERATION,
    "PS_Generation_Dependent": PS_GENERATION_DEPENDENT,
    "PS_Selection_Rating": PS_SELECTION_RATING,
    "PS_Selection_Rating_Novelty": PS_SELECTION_RATING_NOVELTY,
    "PS_Selection_SelectionTop": PS_SELECTION_SELECTIONTOP,
    "PS_Discussion_SelectionTop": PS_DISCUSSION_SELECTIONTOP,
    "PS_Discussion_Rating": PS_DISCUSSION_RATING,
    "PS_Overall": PS_OVERALL,
    "PS_Overall_Single": PS_OVERALL,

    "AUT_Direct_First_Round_AllAtOnce": AUT_DIRECT_FIRST_ROUND_ALL_AT_ONCE,
    "AUT_Direct_Dicussion_AllAtOnce": AUT_DIRECT_DISCUSSION_ALL_AT_ONCE,
    "AUT_Direct_First_Round_OneByOne":AUT_DIRECT_FIRST_ROUND_ONE_BY_ONE,
    "AUT_Direct_Discussion_OneByOne":AUT_DIRECT_DISCUSSION_ONE_BY_ONE,
    "PS_Direct_First_Round_AllAtOnce":PS_DIRECT_FIRST_ROUND_ALL_AT_ONCE,
    "PS_Direct_Discussion_AllAtOnce":PS_DIRECT_DISCUSSION_ALL_AT_ONCE,
    "PS_Direct_Discussion_AllAtOnce_First":PS_DIRECT_DISCUSSION_ALL_AT_ONCE_RESTRICTION_FIRST,
    "PS_Direct_Discussion_AllAtOnce_Other":PS_DIRECT_DISCUSSION_ALL_AT_ONCE_RESTRICTION_OTHER,

    "Intention_Prompt_Ideas": INTENTION_PROMPT_IDEAS,
    "Intention_Prompt_Idea": INTENTION_PROMPT_IDEA,
    "Intention_Scoring": INTENTION_SCORING,
    "PS_Discussion_Rating_NoPool": PS_DISCUSSION_RATING_NoPool,
    "PS_Direct_Discussion_AllAt_Once_NoPool": PS_DIRECT_DISCUSSION_ALL_AT_ONCE_NoPool,
    "Creative_Idea_Generation": CREATIVE_IDEA_GENERATION,
    "Practical_Improvement": PRACTICAL_IMPROVEMENT,
}
