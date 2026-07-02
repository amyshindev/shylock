"""Per-scene logical flaws in Portia's arguments — guides Tubal evidence search."""

from shylock_trial.app.constants.tubal_prompt import TUBAL_SEARCH_FAILURE_COMMENT

PORTIA_LOGICAL_FLAWS: dict[str, str] = {
    "portia_opens": (
        "Portia frames mercy as Shylock's moral obligation, "
        "but ignores that Antonio's party has shown no mercy to Shylock either. "
        "The argument is asymmetric — mercy is demanded of Shylock alone."
    ),
    "bassanio_plea": (
        "Bassanio offers ten times the bond and appeals to mercy, "
        "but treats Shylock's lawful contract as something money can simply replace. "
        "He ignores that Shylock was denied dignity long before this trial began."
    ),
    "crowd_jeers": (
        "The crowd dehumanizes Shylock based on ethnicity, not conduct. "
        "This is prejudice masquerading as moral judgment."
    ),
    "jessica_attack": (
        "Jessica's elopement is a private family matter irrelevant to contract law. "
        "Portia introduces it to emotionally undermine Shylock, not to make a legal argument."
    ),
    "hath_not_moment": (
        "Portia questions whether Shylock has human feeling, "
        "yet the court has systematically denied him the human dignity she demands he show. "
        "The argument is self-contradicting."
    ),
    "blood_reveal": (
        "Portia applies extreme literalism to void the bond — "
        "interpreting 'flesh' as excluding 'blood' defies the contextual meaning of the contract. "
        "No contract can be executed under such impossible conditions by design."
    ),
    "alien_law_reveal": (
        "The alien law is applied retroactively to punish Shylock "
        "for attempting to enforce a contract the court itself initially recognized as valid. "
        "This is double jeopardy — first voiding the bond, then criminalizing the attempt."
    ),
}

__all__ = ["PORTIA_LOGICAL_FLAWS", "TUBAL_SEARCH_FAILURE_COMMENT"]
