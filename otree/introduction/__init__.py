"""
Introduction App

Flow: Consent > ScenarioContext > PartnerReveal (with confirm + transparency check) >
      PreNegotiationBeliefs > Instructions > (EndStudy if declined)

5 pages before the negotiation starts. Demographics and trust propensity
are collected in the post-survey to reduce pre-negotiation friction.

THREE DEPLOYMENTS (switched by session.config flags is_prolific / is_volunteer):
  - Prolific (UK): the deployed study. Payment in GBP, redirects to Prolific on exit
  - Uganda (planned): via research coordinator, no in-study payment; reward set at deployment
  - Volunteer (testing/demos): no in-study payment; reward set at deployment
"""
from otree.api import *

doc = "Introduction with 2x2 manipulation: Label (Human/AI) x Transparency (Opaque/Disclosed)."


class C(BaseConstants):
    NAME_IN_URL = 'introduction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    CONDITIONS = ['HO', 'HT', 'AO', 'AT']


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    players = subsession.get_players()
    conditions = C.CONDITIONS.copy()
    for i, player in enumerate(players):
        code = conditions[i % len(conditions)]
        player.condition_code = code
        player.condition_label = 'human' if code.startswith('H') else 'ai'
        player.condition_transparency = 'opaque' if code.endswith('O') else 'transparent'
        player.participant.condition_label = player.condition_label
        player.participant.condition_transparency = player.condition_transparency
        player.participant.condition_code = player.condition_code


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Condition assignment
    condition_code = models.StringField()
    condition_label = models.StringField()
    condition_transparency = models.StringField()

    # Prolific ID capture
    prolific_pid = models.StringField(blank=True, initial='')

    # Consent
    consent = models.BooleanField(
        label="I have read the information above and agree to participate.",
        choices=[[True, 'I agree to participate'], [False, 'I do not agree']],
        widget=widgets.RadioSelect)
    declined = models.BooleanField(initial=False)

    # Transparency comprehension check (shown on PartnerReveal for transparent conditions)
    comp_transparency = models.StringField(
        label="According to the disclosure, how does Volo Technologies' representative evaluate your offers?",
        choices=[
            'Randomly',
            "By comparing against a fairness score based on each party's contribution",
            'By always accepting the first offer',
            'By consulting with a manager each round'],
        blank=True)

    # Partner confirmation (shown on PartnerReveal for all conditions)
    partner_confirm = models.StringField(
        label="Who will you be negotiating with?",
        choices=[
            'Taylor Goodenoch, a partnerships associate at Volo Technologies',
            "Volo Technologies' AI negotiation agent",
            'Another participant in this study'])

    # Pre-negotiation beliefs
    pre_fair_split = models.IntegerField(
        label="Given the contributions described, what percentage do you think would be a FAIR split for you (the developer)?",
        min=0, max=100)
    pre_fair_confidence = models.IntegerField(
        label="How confident are you in this fairness judgment?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5 - Very confident']],
        widget=widgets.RadioSelectHorizontal)
    pre_trust_competence = models.IntegerField(
        label="I expect Volo Technologies' representative to be a competent negotiator.",
        choices=[[1, 'Strongly Disagree'], [2, 'Disagree'], [3, 'Neutral'],
                 [4, 'Agree'], [5, 'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    pre_trust_fairness = models.IntegerField(
        label="I expect Volo Technologies' representative to negotiate fairly.",
        choices=[[1, 'Strongly Disagree'], [2, 'Disagree'], [3, 'Neutral'],
                 [4, 'Agree'], [5, 'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    pre_trust_overall = models.IntegerField(
        label="Overall, how much do you trust Volo Technologies' representative going into this negotiation?",
        choices=[[1, '1 - Not at all'], [2, '2'], [3, '3'], [4, '4'],
                 [5, '5'], [6, '6'], [7, '7 - Completely']],
        widget=widgets.RadioSelectHorizontal)

    # Trust propensity (covariate) — measured PRE to capture stable individual difference
    # before the manipulation acts. Three items, 5pt Likert, normalized to 0-1 scale.
    trust_1 = models.IntegerField(
        label="Most people can be counted on to do what they say they will do.",
        choices=[[1, 'Strongly Disagree'], [2, 'Disagree'], [3, 'Neutral'],
                 [4, 'Agree'], [5, 'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    trust_2 = models.IntegerField(
        label="I tend to trust people, even those I have just met.",
        choices=[[1, 'Strongly Disagree'], [2, 'Disagree'], [3, 'Neutral'],
                 [4, 'Agree'], [5, 'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    trust_3 = models.IntegerField(
        label="Most people are reliable.",
        choices=[[1, 'Strongly Disagree'], [2, 'Disagree'], [3, 'Neutral'],
                 [4, 'Agree'], [5, 'Strongly Agree']],
        widget=widgets.RadioSelectHorizontal)
    trust_propensity = models.FloatField()  # computed mean, 0-1 scale

    # Instructions comprehension
    comp_rounds = models.IntegerField(
        label="What is the maximum number of negotiation rounds?",
        choices=[1, 3, 5, 7], widget=widgets.RadioSelectHorizontal)
    comp_disagree = models.StringField(
        label="What happens if no agreement is reached after 5 rounds?",
        choices=['You get everything', 'Volo Technologies gets everything',
                 'Both parties receive only 25% each (deal falls through)',
                 'The negotiation continues indefinitely'])
    stable_internet = models.BooleanField(
        label="I have a stable internet connection for the session.",
        choices=[[True, 'Yes'], [False, 'No']],
        widget=widgets.RadioSelectHorizontal)

    # Rules acceptance / readiness
    rules_accepted = models.BooleanField(
        label="Are you ready to begin the negotiation?",
        choices=[[True, "Yes, I'm ready"], [False, 'No, I want to withdraw']],
        widget=widgets.RadioSelect)


# HELPER FUNCTIONS
def get_partner_label(player):
    if player.condition_label == 'human':
        return "Taylor Goodenoch, Volo Technologies' partnerships associate"
    return "Volo Technologies' AI negotiation agent"


def get_partner_short(player):
    if player.condition_label == 'human':
        return "Taylor"
    return "Volo Technologies' AI agent"


def is_prolific(player):
    """Helper to check deployment type from any page."""
    return player.session.config.get('is_prolific', True)


def is_volunteer(player):
    """Helper to check if this is a volunteer (unpaid) session."""
    return player.session.config.get('is_volunteer', False)


# PAGES

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        return dict(
            is_prolific=is_prolific(player),
            is_volunteer=is_volunteer(player),
            currency_symbol=config.get('currency_symbol', '£'),
            base_payment=config['base_payment'],
            max_bonus=config['max_bonus'],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not player.consent:
            player.declined = True


class EndStudy(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.declined

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        url = config.get('completion_url', '')
        return dict(
            completion_url=url,
            is_prolific=is_prolific(player),
            is_volunteer=is_volunteer(player),
        )


class ScenarioContext(Page):
    @staticmethod
    def is_displayed(player: Player):
        return not player.declined

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        return dict(
            acquisition_value=f"${config['acquisition_value']:,}",
            dev_code_pct=config['developer_code_pct'],
            volo_code_pct=config['volo_code_pct'])


# PartnerReveal now includes transparency check (for transparent conditions)
# and partner confirmation (for all conditions) on one page.
class PartnerReveal(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        """Transparent conditions get both checks. Opaque just gets partner confirm."""
        if player.condition_transparency == 'transparent':
            return ['comp_transparency', 'partner_confirm']
        return ['partner_confirm']

    @staticmethod
    def is_displayed(player: Player):
        return not player.declined

    @staticmethod
    def vars_for_template(player: Player):
        label = player.condition_label
        transparency = player.condition_transparency
        if label == 'human':
            partner_reveal = (
                "You will negotiate with <strong>Taylor Goodenoch</strong>, a partnerships "
                "associate at Volo Technologies. Taylor recently joined the team and has been "
                "assigned to handle the equity negotiation on behalf of the company.")
        else:
            partner_reveal = (
                "You will negotiate with <strong>Volo Technologies' AI negotiation agent</strong>. "
                "This system has been deployed to negotiate Volo Technologies' share of the "
                "acquisition proceeds on behalf of the company.")
        show_transparency = (transparency == 'transparent')
        if show_transparency and label == 'ai':
            transparency_text = (
                "As part of their transparency policy, Volo Technologies has disclosed how "
                "their AI negotiation agent evaluates offers:"
                "<p>The agent assesses proposals based on each party's contribution to the product. "
                "The closer your proposal is to what the agent considers a fair split, the more "
                "likely it is to be accepted. Proposals far from this benchmark are more likely "
                "to be rejected, and the counter-offer you receive will reflect how far your "
                "proposal was from the fair range.</p>")
        elif show_transparency and label == 'human':
            transparency_text = (
                "As part of their transparency policy, Volo Technologies has shared how "
                "their representative evaluates offers:"
                "<p>Taylor assesses proposals based on each party's contribution to the product. "
                "The closer your proposal is to what Taylor considers a fair split, the more "
                "likely it is to be accepted. Proposals far from this benchmark are more likely "
                "to be rejected, and the counter-offer you receive will reflect how far your "
                "proposal was from the fair range.</p>")
        else:
            transparency_text = ""
        return dict(
            partner_reveal=partner_reveal,
            partner_label=get_partner_label(player),
            show_transparency=show_transparency,
            transparency_text=transparency_text)

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        # transparency comprehension (transparent conditions only)
        if 'comp_transparency' in values:
            correct = "By comparing against a fairness score based on each party's contribution"
            if values['comp_transparency'] != correct:
                errors['comp_transparency'] = 'Incorrect. Please re-read the disclosure above.'
        # partner confirmation (all conditions)
        correct_partner = ('Taylor Goodenoch, a partnerships associate at Volo Technologies'
                           if player.condition_label == 'human'
                           else "Volo Technologies' AI negotiation agent")
        if values['partner_confirm'] != correct_partner:
            errors['partner_confirm'] = 'Incorrect. Please re-read the information about your negotiation partner.'
        return errors


class PreNegotiationBeliefs(Page):
    form_model = 'player'
    form_fields = ['trust_1', 'trust_2', 'trust_3',
                   'pre_fair_split', 'pre_fair_confidence',
                   'pre_trust_competence', 'pre_trust_fairness', 'pre_trust_overall']

    @staticmethod
    def is_displayed(player: Player):
        return not player.declined

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        return dict(
            partner_label=get_partner_label(player),
            partner_short=get_partner_short(player),
            dev_code_pct=config['developer_code_pct'],
            volo_code_pct=config['volo_code_pct'])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # trust propensity: (mean - 1) / 4 -> 0-1 scale from 3 items
        items = [player.trust_1, player.trust_2, player.trust_3]
        player.trust_propensity = round((sum(items) / len(items) - 1) / 4, 4)


class Instructions(Page):
    form_model = 'player'
    form_fields = ['comp_rounds', 'comp_disagree',
                   'stable_internet', 'rules_accepted']

    @staticmethod
    def is_displayed(player: Player):
        return not player.declined

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        return dict(
            partner_short=get_partner_short(player),
            acquisition_value=f"${config['acquisition_value']:,}",
            disagreement_pct=config['disagreement_payoff'],
            base_payment=config['base_payment'],
            max_bonus=config['max_bonus'],
            is_prolific=is_prolific(player),
            is_volunteer=is_volunteer(player),
            currency_symbol=config.get('currency_symbol', '£'),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values['comp_rounds'] != 5:
            errors['comp_rounds'] = 'Incorrect.'
        if values['comp_disagree'] != 'Both parties receive only 25% each (deal falls through)':
            errors['comp_disagree'] = 'Incorrect. Please re-read.'
        return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not player.rules_accepted:
            player.declined = True
        else:
            # initialize participant vars for the negotiation app
            player.participant.final_share = 0
            player.participant.total_bonus = 0
            player.participant.agreed = False
            player.participant.agreement_round = 0


page_sequence = [
    Consent, ScenarioContext, PartnerReveal,
    PreNegotiationBeliefs, Instructions, EndStudy,
]
