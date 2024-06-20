from .base import Rule


"""
rule config schema 

{
    rule_name: {
        "fields: [],
        "config": {}, 
        ...
    }
}
"""


class RuleBook:

    def __init__(
        self,
        rules: dict[str, Rule] | list[Rule] = None,
        ruleorder: list[str] = None,
        rule_config: dict[str, dict] = None,
    ):
        self.rules = rules
        self.ruleorder = ruleorder
        self.rule_config = rule_config or {k: {} for k in self.ruleorder}

    @property
    def _all_applied_log(self):
        """return all applied logs from all rules in the rulebook"""
        _out = []
        for i in self.rules.values():
            _out.extend([j for j in i.applied_log if j is not None])
        return _out

    @property
    def _all_invoked_log(self):
        """return all invoked logs from all rules in the rulebook"""
        _out = []
        for i in self.rules.values():
            _out.extend([j for j in i.invoked_log if j is not None])
        return _out

    def __getitem__(self, key: str) -> Rule:
        return self.rules[key]

    # def add_rule(self, rule_name: str, rule: Rule, config: dict = None):
    #     if rule_name in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' already exists.")
    #     self.rules[rule_name] = rule
    #     self.ruleorder.append(rule_name)
    #     self.rule_config[rule_name] = config or {}

    # def remove_rule(self, rule_name: str):
    #     if rule_name not in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' does not exist.")
    #     del self.rules[rule_name]
    #     self.ruleorder.remove(rule_name)
    #     del self.rule_config[rule_name]

    # def update_rule_config(self, rule_name: str, config: dict):
    #     if rule_name not in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' does not exist.")
    #     self.rule_config[rule_name] = config

    # def list_rules(self) -> list[str]:
    #     return self.ruleorder

    # def get_rule_details(self, rule_name: str) -> dict:
    #     if rule_name not in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' does not exist.")
    #     return {
    #         "rule": self.rules[rule_name],
    #         "config": self.rule_config[rule_name]
    #     }

    # async def validate_data(self, data: Any) -> bool:
    #     for rule in self.rules.values():
    #         if not await rule.validate(data):
    #             return False
    #     return True

    # def export_rulebook(self, filepath: str):
    #     import json
    #     with open(filepath, 'w') as f:
    #         json.dump({
    #             "rules": list(self.rules.keys()),
    #             "ruleorder": self.ruleorder,
    #             "rule_config": self.rule_config
    #         }, f)

    # @classmethod
    # def import_rulebook(cls, filepath: str) -> 'RuleBook':
    #     import json
    #     with open(filepath, 'r') as f:
    #         config = json.load(f)
    #     rules = {name: Rule() for name in config["rules"]}
    #     return cls(rules=rules, ruleorder=config["ruleorder"], rule_config=config["rule_config"])

    # def enable_rule(self, rule_name: str, enable: bool = True):
    #     if rule_name not in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' does not exist.")
    #     self.rules[rule_name].enabled = enable

    # def log_rule_application(self, rule_name: str, data: Any):
    #     if rule_name not in self.rules:
    #         raise ValueError(f"Rule '{rule_name}' does not exist.")
    #     log_entry = {
    #         "rule": rule_name,
    #         "data": data,
    #         "timestamp": SysUtil.get_timestamp()
    #     }
    #     # Append log_entry to a log file or a logging system
