# Token Level Event Coreference Resolution

## Task Description
Event  coreference  task  is  similar  to  the  entity  coreference  task.   However,compared to entity coreference resolution,  which is to link nouns and pro-nouns that point to the same entity, ECR is less studied but arguably more challenging. Event coreference resolution is the task of identifying piecesof text that refer to unique events and grouping them, resulting in one groupper unique event.

Example:
- Donald Trump <b><u>left</u></b><sub><b>ev1</b></sub> the White House on Thursday for the debate with Joe Biden.
- He <b><u>departed</u></b><sub><b>ev2</b></sub> the White House in a black armoured SUV.

**ev1** and **ev2** are coreferent.

We are trying to build a **token-level** | **non-end-to-end** | **within-document** event coreference resolution pipeline with **ACE2005 English** dataset.


## ACE2005 Event Coreference Parser (ACE05_Parser)

ACE05_Parser is basic parser where you can have each document and their events with mention groups. Please check parsing.ipynb for details.

## Baselines
#### Dumb Baselines
There are two dumb baselines. Their details and scores are available on dumbBaselines.ipynb file.

