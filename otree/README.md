# oTree experiment

The oTree project behind The AI Label Paradox. Built on oTree 6.0.10.

## Apps

The live session runs introduction, then negotiation, then post_survey,
set by app_sequence in settings.py. A payment app is included for the
operator-facing payment summary.

The negotiation app holds the dual-layer confederate: a deterministic
Python algorithm sets every numerical move, and the OpenAI API generates
the conversational text (gpt-4o-mini for text, gpt-4o for intent
inference).

## Session configs

Three configs ship in settings.py: founders_dilemma_prolific,
founders_dilemma_uganda and founders_dilemma_volunteer.

## Run locally

The secrets are read from the environment and are never stored in the
code.

    pip install -r requirements.txt
    export OPENAI_API_KEY=...
    export OTREE_SECRET_KEY=...
    export OTREE_ADMIN_PASSWORD=...
    otree devserver

## Deploy

A Procfile is included for Heroku. Set OPENAI_API_KEY, OTREE_SECRET_KEY
and OTREE_ADMIN_PASSWORD as config vars on the host.

## Licence

Code in this folder is released under the MIT Licence (LICENSE). Data and
written materials in the repository are CC-BY-4.0.
