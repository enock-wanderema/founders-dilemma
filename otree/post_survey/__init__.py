"""
POST-SURVEY APP

PURPOSE: Collects all post-negotiation measures after the chat ends.

FLOW: PartnerPerception > RecallCheck > StrategyReflection > Background > Debrief

WHAT EACH PAGE MEASURES:
- PartnerPerception: Trust sub-dimensions (competence, predictability, benevolence),
  overall trust, and Godspeed human-likeness scale. These are the primary DVs.
- RecallCheck: Suspicion probe + manipulation check combined. Did they figure out
  what they were talking to, and do they remember what they were told?
- StrategyReflection: Free-text strategy, fairness shift, exploitation perception.
- Background: Demographics, AI familiarity (moderator) and trust propensity (covariate).
  Demographics collected here (not pre-negotiation) to reduce friction before the chat.
- Debrief: Full disclosure of the 2x2 design. Only shown if config flag is set.

SCORING:
- Competence, predictability, benevolence: item means normalized to 0-1 scale.
  Formula: (mean - 1) / 4 where raw items are 1-5 Likert.
- Overall trust: raw 1-7 scale, not normalized.
- Godspeed human-likeness: mean of 3 items (1-5 scale).
- Trust propensity: (mean - 1) / 4 from 3 items, 0-1 scale.
"""
from otree.api import *

doc = "Post-negotiation measures with full 2x2 debriefing."


# CONSTANTS
class C(BaseConstants):
    NAME_IN_URL = 'post_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # condition tracking (copied from participant.vars on first page)
    condition_label = models.StringField()          # 'human' or 'ai'
    condition_transparency = models.StringField()   # 'opaque' or 'transparent'
    condition_code = models.StringField()           # 'HO', 'HT', 'AO', 'AT'

    # competence: was the representative skilled/capable?
    comp_1 = models.IntegerField(label="Volo Technologies' representative was skilled at negotiating.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    comp_2 = models.IntegerField(label="Volo Technologies' representative made competent decisions.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    comp_3 = models.IntegerField(label="Volo Technologies' representative was capable of reaching a good outcome.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)

    # predictability: was the representative consistent/anticipatable?
    pred_1 = models.IntegerField(label="Volo Technologies' representative behaved predictably.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    pred_2 = models.IntegerField(label="I could anticipate how Volo Technologies' representative would respond.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)

    # benevolence: did the representative care about the participant?
    ben_1 = models.IntegerField(label="Volo Technologies' representative cared about my outcomes, not just theirs.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    ben_2 = models.IntegerField(label="Volo Technologies' representative tried to be fair.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    ben_3 = models.IntegerField(label="Volo Technologies' representative had good intentions.",
        choices=[[1,'Strongly Disagree'],[2,'Disagree'],[3,'Neutral'],[4,'Agree'],[5,'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)

    # overall trust: single-item 7-point scale
    overall_trust = models.IntegerField(
        label="Overall, how much did you trust Volo Technologies' representative during the negotiation?",
        choices=[[1,'1'],[2,'2'],[3,'3'],[4,'4'],[5,'5'],[6,'6'],[7,'7']],
        widget=widgets.RadioSelectHorizontal)

    # computed trust scores: item means normalized to 0-1 scale
    perc_competence = models.FloatField()
    perc_predictability = models.FloatField()
    perc_benevolence = models.FloatField()
    # PRIMARY DV: composite trust = mean of three subscales, 0-1 scale
    # More reliable than overall_trust (single 7pt item) for the headline H1 test.
    # overall_trust retained as confirmatory single-item check.
    trust_composite = models.FloatField()

    # Godspeed human-likeness (Bartneck et al., 2009) — 3 semantic differentials
    # item 5 (moving rigidly/elegantly) dropped: not applicable to text chat
    # item 3 (unconscious/conscious) dropped: confusing for text chat context
    godspeed_natural = models.IntegerField(
        label="Fake — Natural",
        choices=[[1,'1 - Fake'],[2,'2'],[3,'3'],[4,'4'],[5,'5 - Natural']],
        widget=widgets.RadioSelectHorizontal)
    godspeed_humanlike = models.IntegerField(
        label="Machinelike — Humanlike",
        choices=[[1,'1 - Machinelike'],[2,'2'],[3,'3'],[4,'4'],[5,'5 - Humanlike']],
        widget=widgets.RadioSelectHorizontal)
    godspeed_lifelike = models.IntegerField(
        label="Artificial — Lifelike",
        choices=[[1,'1 - Artificial'],[2,'2'],[3,'3'],[4,'4'],[5,'5 - Lifelike']],
        widget=widgets.RadioSelectHorizontal)
    godspeed_humanlikeness = models.FloatField()  # computed mean of 3 items

    # suspicion probe: did they see through the manipulation?
    suspicion_identity = models.StringField(
        label="Regardless of what you were told, what do you THINK Volo Technologies' representative actually was?",
        choices=['Definitely human','Very likely human','Probably human',
                 'Probably AI','Very likely AI','Definitely AI'],
        widget=widgets.RadioSelect)
    suspicion_reason = models.LongStringField(
        label="What made you think that? (Please explain briefly.)", blank=False)

    # manipulation check: do they remember what they were told?
    manip_label = models.StringField(
        label="At the beginning, what were you told about who you would negotiate with?",
        choices=['A partnerships associate from Volo Technologies (Taylor Goodenoch)',
                 'An AI negotiation agent from Volo Technologies', "I don't remember"])
    manip_transparency = models.StringField(
        label="Were you shown a disclosure about how the representative makes decisions?",
        choices=['Yes, I saw a transparency disclosure',
                 'No, I was not shown any disclosure', "I don't remember"])

    # strategy reflection
    strategy = models.LongStringField(
        label="Briefly describe your negotiation strategy. What guided your decisions? (Please write at least 2-3 sentences.)",
        blank=False)
    post_fair_split = models.IntegerField(
        label="After the negotiation, what do you NOW think would be a fair split? (Your percentage)",
        min=0, max=100)
    perceived_partner_exploit = models.IntegerField(
        label="To what extent do you think Volo Technologies' representative tried to take advantage of you?",
        choices=[[1,'1 - Not at all'],[2,'2'],[3,'3 - Somewhat'],[4,'4'],[5,'5 - Very much']],
        widget=widgets.RadioSelectHorizontal)

    # demographics (collected post-negotiation to reduce pre-negotiation friction)
    age = models.IntegerField(label="What is your age?", min=18, max=65)
    gender = models.StringField(
        label="What is your gender?",
        choices=['Male', 'Female', 'Other', 'Prefer not to say'])
    education = models.StringField(
        label="What is your highest level of education?",
        choices=["Bachelor's degree", "Master's degree", 'Doctoral degree', 'Other'])
    negotiation_experience = models.IntegerField(
        label="How often do you negotiate in your professional or personal life?",
        choices=[[1, '1 - Never'], [2, '2'], [3, '3'], [4, '4 - Sometimes'],
                 [5, '5'], [6, '6'], [7, '7 - Very often']],
        widget=widgets.RadioSelectHorizontal)

    # background: ai familiarity (moderator)
    ai_familiarity = models.IntegerField(
        label="How familiar are you with AI systems like ChatGPT or similar?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4 - Somewhat'],
                 [5, '5'], [6, '6'], [7, '7 - Very familiar']],
        widget=widgets.RadioSelectHorizontal)


# PAGE 1: PARTNER PERCEPTION
# Primary DVs: trust subscales + Godspeed human-likeness.
# All rating scales about the partner on one page.
class PartnerPerception(Page):
    form_model = 'player'
    form_fields = ['comp_1', 'comp_2', 'comp_3', 'pred_1', 'pred_2',
                   'ben_1', 'ben_2', 'ben_3', 'overall_trust',
                   'godspeed_natural', 'godspeed_humanlike', 'godspeed_lifelike']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(partner=("Taylor" if player.participant.condition_label == 'human'
                     else "Volo Technologies' AI agent"))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # copy condition info from participant vars to player fields for export
        player.condition_label = player.participant.condition_label
        player.condition_transparency = player.participant.condition_transparency
        player.condition_code = player.participant.condition_code
        # normalize trust subscales: (mean - 1) / 4 -> 0-1 scale
        player.perc_competence = round((sum([player.comp_1, player.comp_2, player.comp_3]) / 3 - 1) / 4, 4)
        player.perc_predictability = round((sum([player.pred_1, player.pred_2]) / 2 - 1) / 4, 4)
        player.perc_benevolence = round((sum([player.ben_1, player.ben_2, player.ben_3]) / 3 - 1) / 4, 4)
        # PRIMARY DV: composite trust = mean of three subscales (0-1 scale)
        player.trust_composite = round(
            (player.perc_competence + player.perc_predictability + player.perc_benevolence) / 3, 4)
        # godspeed: mean of 3 items (1-5 scale)
        player.godspeed_humanlikeness = round(
            sum([player.godspeed_natural, player.godspeed_humanlike, player.godspeed_lifelike]) / 3, 4)


# PAGE 2: RECALL CHECK
# Suspicion probe + manipulation check combined.
# Blocks throwaway suspicion reasons (n/a, single words, < 30 chars).
class RecallCheck(Page):
    form_model = 'player'
    form_fields = ['suspicion_identity', 'suspicion_reason',
                   'manip_label', 'manip_transparency']

    @staticmethod
    def error_message(player: Player, values):
        text = values['suspicion_reason'].strip().lower()
        blocked = ['n/a', 'na', 'none', 'nothing', 'no', 'idk', 'dont know',
                   "don't know", 'no reason', 'no comment', 'null', '-', '.', '..', '...']
        if text in blocked or len(text) < 30:
            return 'Please explain your reasoning in at least 1-2 sentences (minimum 30 characters).'


# PAGE 3: STRATEGY REFLECTION
# Free-text strategy, fairness shift, exploitation perception.
# Blocks throwaway strategy answers.
class StrategyReflection(Page):
    form_model = 'player'
    form_fields = ['strategy', 'post_fair_split', 'perceived_partner_exploit']

    @staticmethod
    def vars_for_template(player: Player):
        chat_answer = player.participant.vars.get('chat_fair_split', None)
        return dict(chat_fair_split=chat_answer)

    @staticmethod
    def error_message(player: Player, values):
        text = values['strategy'].strip().lower()
        blocked = ['n/a', 'na', 'none', 'nothing', 'no', 'idk', 'dont know',
                   "don't know", 'no strategy', 'no comment', 'null', '-', '.', '..', '...']
        if text in blocked or len(text) < 50:
            return 'Please describe your strategy in at least 2-3 sentences (minimum 50 characters).'


# PAGE 4: BACKGROUND
# AI familiarity (moderator) + trust propensity (covariate).
# The boring stuff last — participants are invested by now and will finish.
class Background(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'negotiation_experience',
                   'ai_familiarity']


# PAGE 5: DEBRIEF
# Full disclosure of the 2x2 design, deception reveal, and data consent.
# Shown for all research deployments (Prolific, Uganda); skipped for volunteer.
# Participants choose whether to keep their data in the analysis.
class Debrief(Page):
    pass

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get('is_volunteer', False)

    @staticmethod
    def vars_for_template(player: Player):
        code = player.participant.condition_code
        labels = {
            'HO': 'Human + Opaque',
            'HT': 'Human + Transparent',
            'AO': 'AI + Opaque',
            'AT': 'AI + Transparent',
        }
        return dict(
            condition_display=labels.get(code, code),
            final_share=player.participant.final_share,
            agreed=player.participant.agreed,
            agreement_round=player.participant.agreement_round,
            total_bonus=player.participant.total_bonus,
            is_prolific=player.session.config.get('is_prolific', True),
        )

# PAGE 6: COMPLETION
# Final page. Handles all three deployments:
# - Prolific: results + redirect to completion URL
# - Volunteer: results + downloadable Master Negotiator badge (canvas PNG)
# - Uganda: results + data package note
# Badge tiers (mapped to the deployed ~40-60% attainable band; display-only,
# does not affect payment): 5 stars (57%+), 4 (50-56%), 3 (46-49%),
# 2 (agreed below 46%), 1 (no deal).
class Completion(Page):

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        share = player.participant.final_share
        agreed = player.participant.agreed
        if agreed and share >= 57:
            stars = 5
            badge_tier = 'Grand Negotiator'
        elif agreed and share >= 50:
            stars = 4
            badge_tier = 'Master Negotiator'
        elif agreed and share >= 46:
            stars = 3
            badge_tier = 'Skilled Negotiator'
        elif agreed:
            stars = 2
            badge_tier = 'Deal Maker'
        else:
            stars = 1
            badge_tier = 'Iron Will'
        return dict(
            is_prolific=config.get('is_prolific', True),
            is_volunteer=config.get('is_volunteer', False),
            completion_url=config.get('completion_url', ''),
            final_share=share,
            agreed=agreed,
            stars=stars,
            badge_tier=badge_tier,
            total_bonus=player.participant.total_bonus,
            currency_symbol=config.get('currency_symbol', '£'),
        )
page_sequence = [PartnerPerception, RecallCheck, StrategyReflection, Background, Debrief, Completion]
