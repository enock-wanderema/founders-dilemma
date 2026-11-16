"""Payment summary (paid participants) and badge (volunteers)."""
from otree.api import *

doc = "Payment summary and completion."

class C(BaseConstants):
    NAME_IN_URL = 'payment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    final_share = models.IntegerField()
    final_dollar = models.IntegerField()
    base_payment = models.FloatField()
    bonus = models.FloatField()
    total_payment = models.FloatField()

class PaymentSummary(Page):
    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        is_volunteer = config.get('is_volunteer', False)      # volunteer = no payment, badge instead
        is_prolific = config.get('is_prolific', False)
        currency = config.get('currency_symbol', '')
        base = config['base_payment']
        bonus = player.participant.total_bonus or 0
        share = player.participant.final_share or 0
        agreed = player.participant.agreed
        acq = config['acquisition_value']
        agreement_round = player.participant.agreement_round or 0

        # save to player fields for data export
        player.final_share = share
        player.final_dollar = round(acq * share / 100)
        player.base_payment = base
        player.bonus = bonus
        player.total_payment = round(base + bonus, 2)

        # agreement info for the badge
        if agreed:
            agreement_info = f"Deal in round {agreement_round} of 5"
        else:
            agreement_info = "No agreement reached"

        # format payment strings based on deployment
        if is_prolific:
            base_str = f"£{base:.2f}"
            bonus_str = f"£{bonus:.2f}"
            total_str = f"£{player.total_payment:.2f}"
        elif not is_volunteer:
            base_str = f"{currency}{base}"
            bonus_str = f"{currency}{bonus}"
            total_str = f"{currency}{player.total_payment}"
        else:
            base_str = ""      # volunteers see no payment
            bonus_str = ""
            total_str = ""

        return dict(
            final_share=share,
            final_dollar=f"${player.final_dollar:,}",
            base_payment=base_str,
            bonus=bonus_str,
            total_payment=total_str,
            agreed=agreed,
            agreement_info=agreement_info,
            is_volunteer=is_volunteer,
            is_prolific=is_prolific,
            completion_url=config.get('completion_url', ''),
        )

page_sequence = [PaymentSummary]
