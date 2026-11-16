"""
SETTINGS — Three deployments of the same experiment.

PROLIFIC (UK): Base payment via Prolific + up to £1.00 bonus.
UGANDA: reward via research coordinator (set at deployment). No in-study payment.
VOLUNTEER: No payment. Badge reward. For pilot testing.

Only payment display differs. Algorithm is identical across all deployments.
"""
from os import environ

SESSION_CONFIGS = [
    # PROLIFIC DEPLOYMENT (UK, paid through Prolific)
    dict(
        name='founders_dilemma_prolific',
        display_name="AI Label Paradox (Prolific)",
        app_sequence=['introduction', 'negotiation', 'post_survey'],
        num_demo_participants=4,

        # Payment (GBP)
        base_payment=2.00,
        max_bonus=1.00,
        currency_symbol='£',

        # Algorithm parameters
        acceptance_threshold=45,        # Logistic midpoint (see bot_evaluate)
        logistic_k=0.25,                # Logistic steepness (see bot_evaluate)
        acquisition_value=1000000,      # Fictional acquisition price ($1M)
        developer_code_pct=70,          # Participant wrote 70% of code
        volo_code_pct=30,               # Volo contributed 30%
        volo_equity_claim=58,           # Volo claims 58% so opening offer = 42%
        disagreement_payoff=25,         # Both get 25% if no deal
        counter_reference=80,           # demands below this earn better counters
        counter_scaling=2,              # every 2 points closer to fair = 1 point better counter

        # Deployment flags
        is_prolific=True,
        is_volunteer=False, # not a volunteer session
        completion_url='https://app.prolific.com/submissions/complete?cc=CI4A27FG',

        # LLM (gpt-4o-mini for text generation, gpt-4o for intent inference)
        openai_api_key=environ.get('OPENAI_API_KEY', ''),
    ),

    # UGANDA DEPLOYMENT (Reward package via research coordinator)
    dict(
        name='founders_dilemma_uganda',
        display_name="AI Label Paradox (Uganda)",
        app_sequence=['introduction', 'negotiation', 'post_survey'],
        num_demo_participants=4,

        # No in-study payment — coordinator handles data package offline
        base_payment=0,
        max_bonus=0,
        currency_symbol='',

        # Algorithm parameters (identical to Prolific)
        acceptance_threshold=45,
        logistic_k=0.25,
        acquisition_value=1000000,
        developer_code_pct=70,
        volo_code_pct=30,
        volo_equity_claim=58,
        disagreement_payoff=25,
        counter_reference=80,
        counter_scaling=2,

        # Deployment flags
        is_prolific=False,
        is_volunteer=False,
        completion_url='',

        # LLM (gpt-4o-mini for text generation, gpt-4o for intent inference)
        openai_api_key=environ.get('OPENAI_API_KEY', ''),
    ),

    # VOLUNTEER DEPLOYMENT (friends/pilot, no payment, badge reward)
    dict(
        name='founders_dilemma_volunteer',
        display_name="AI Label Paradox (Volunteer)",
        app_sequence=['introduction', 'negotiation', 'post_survey'],
        num_demo_participants=4,

        # No payment — volunteers get a downloadable badge instead
        base_payment=0,
        max_bonus=0,
        currency_symbol='',

        # Algorithm parameters (identical to Prolific)
        acceptance_threshold=45,
        logistic_k=0.25,
        acquisition_value=1000000,
        developer_code_pct=70,          # Participant wrote 70% of code
        volo_code_pct=30,               # Volo contributed 30%
        volo_equity_claim=58,           # Volo claims 58% so opening offer = 42%
        disagreement_payoff=25,
        counter_reference=80,
        counter_scaling=2,

        # Deployment flags
        is_prolific=False,
        is_volunteer=True, # templates check this to hide payment info
        completion_url='',

        # LLM (gpt-4o-mini for text generation, gpt-4o for intent inference)
        openai_api_key=environ.get('OPENAI_API_KEY', ''),
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=0,
    doc="",
)

PARTICIPANT_FIELDS = [
    'condition_label', 'condition_transparency', 'condition_code',
    'final_share', 'total_bonus', 'agreed', 'agreement_round',
    'chat_fair_split',
]

SESSION_FIELDS = []
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False

ROOMS = [
    dict(name='prolific', display_name='Prolific Participants'),
    dict(name='uganda', display_name='Uganda Participants'),
    dict(name='volunteer', display_name='Volunteer Participants'),
]

ADMIN_USERNAME = environ.get('OTREE_ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', '')
DEMO_PAGE_INTRO_HTML = "<h3>The AI Label Paradox</h3>"
SECRET_KEY = environ.get('OTREE_SECRET_KEY', '')
DEBUG = False
