/**
 * GFL2 Doll Info
 * Source: https://docs.google.com/spreadsheets/d/1DogyU3K7ZXw2qbhP1EhRXIAw5nCyIV5G5e-QWviBZME
 * Generated: 2026-06-07
 *
 * Per-doll structure:
 *   class, stats{hp,atk,def}, stabilityGauge, movementSpeed,
 *   skillAttributes[], weaknesses[],
 *   skills[{name, traits[], attribute, stabilityDamage, cooldown,
 *           confectanceCost, range, effArea, description, icon,
 *           upgrades[{type, number, label, effect}]}],
 *   vertebraeUpgrades[{upgrade, skill, level, effect}],
 *   neuralHelixKeys[{node, level, keyName, description, icon}]
 */
const DOLL_INFO = {
  "Jiangyu": {
    "class": "Support",
    "stats": {
      "hp": 2368,
      "atk": 690,
      "def": 650
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Electric"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Form-Intention Fist",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects one enemy target within a 8 tile radius and deals Physical damage equivalent to 80% attack to it",
        "upgrades": [],
        "icon": "assets/Jiangyu/Form-Intention Fist.png"
      },
      {
        "name": "Thunderclap",
        "traits": [
          "Active",
          "Melee",
          "AoE"
        ],
        "attribute": "Melee",
        "stabilityDamage": 5,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "Melee",
        "effArea": "3x3",
        "description": "Selects one enemy target within 3x3 area around self, dealing AOE Melee Electric damage equal to 90% of attack to the target and all enemy units within a 3x3 area. Creates a Voltage terrain for 3 turns. If Phase Weakness is exploited, additionally deals 5 points of Stability Damage. After the attack, gains 6 tiles of Additional Movement and Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Before attacking, gains Attack Up II for 3 turns. When dealing Stability Damage, deals an additional 5 points of fixed Stability Damage to all enemy units with Negative Charge."
          }
        ],
        "icon": "assets/Jiangyu/Thunderclap.png"
      },
      {
        "name": "Lightning Smash",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects one enemy target within a 8-tile radius and deals Electric damage equal to 110% of attack to it. Jiangyu gains 2 points of Confectance Index. If the target is in Stability Break, Jiangyu gains 1 stack of Chi before attacking.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Damage multiplier increased to 140%. \nDamage dealt to targets with Voltage Sag is increased by 30%. \nBefore dealing damage, dispels 1 Buff from the target."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the amount of dispelled buffs by 1. If\nthe target has 0 stability, perform an additional attack."
          }
        ],
        "icon": "assets/Jiangyu/Lightning Smash.png"
      },
      {
        "name": "Rolling Thunder",
        "traits": [
          "Ultimate",
          "Targeted",
          "Buff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 4,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "8",
        "description": "Selects one enemy target within a 8-tile radius. Jiangyu gains 2 stacks of Chi and deals Electric damage equal to 130% of attack that ignores Cover to it. Applies Positive Charge to all allies for 3 turns, cleanse 1 debuff, and removes Stun and Taunt. Jiangyu gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Cooldown is reduced by 1 turn, and Confectance Index gained is increased by 1. \nRestores 2 Stability Index to all allies, increases the number of cleansed debuffs by 1, and removes Fear and Infatuated."
          }
        ],
        "icon": "assets/Jiangyu/Rolling Thunder.png"
      },
      {
        "name": "Grand Aura",
        "traits": [
          "Passive",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the round, Jiangyu gains 1 point of Confectance Index. \nAt the end of the action, if the Confectance Index of Jiangyu is full, all Confectance Index is consumed to reduce the cooldown of Rolling Thunder by 1 turn. When an enemy unit repeatedly gains Negative Charge, applies 1 stack of Voltage Sag for 2 turns. When an allied unit repeatedly gains Positive Charge, applies 1 stack of Power Surge for 3 turns. \n\nWhen an enemy unit within Jiangyu's range (8) takes Targeted Damage from an ally, the user prioritizes performing 1 Support Action and gains 1 stack of Chi. \n\nSupport Action: If the target has Stability greater than 0, deals Electric damage equivalent to 45% of attack and 3 points of Stability damage. If the target is in Stability Break, deals Electric damage equivalent to 75% of attack. Can trigger up to 2 times per round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the number of Support Actions by 1. \nAt the start of battle, deals 4 fixed Stability Damage to all enemy units within a radius of 8 tiles. \nVoltage Sag gains a new effect: When gained, deals fixed damage equal to current stacks × 10% of the caster’s attack. \nPower Surge gains a new effect: Upon gaining this effect, restores HP equal to 10% of Max HP."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Fixed Stability Damage dealt at the start of battle is increased by 4 points. \nWhen Jiangyu has Chi, Electric damage dealt is increased by 15%. \nThe maximum stack limit of Voltage Sag is increased by 3. \nPower Surge effect changed: When dealing Electric damage, ignored DEF is increased to 10%, and healing received is increased to 10%."
          }
        ],
        "icon": "assets/Jiangyu/Grand Aura.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Unyielding Chi",
        "level": "2",
        "effect": "Increases the number of Support Actions by 1. \nAt the start of battle, deals 4 fixed Stability Damage to all enemy units within a radius of 8 tiles. \nVoltage Sag gains a new effect: When gained, deals fixed damage equal to current stacks × 10% of the caster’s attack. \nPower Surge gains a new effect: Upon gaining this effect, restores HP equal to 10% of Max HP."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Rolling Thunder",
        "level": "2",
        "effect": "Cooldown is reduced by 1 turn, and Confectance Index gained is increased by 1. \nRestores 2 Stability Index to all allies, increases the number of cleansed debuffs by 1, and removes Fear and Infatuated."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Lightning Smash",
        "level": "2",
        "effect": "Damage multiplier increased to 140%. \nDamage dealt to targets with Voltage Sag is increased by 30%. \nBefore dealing damage, dispels 1 Buff from the target."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Thunderclap",
        "level": "2",
        "effect": "Before attacking, gains Attack Up II for 3 turns. When dealing Stability Damage, deals an additional 5 points of fixed Stability Damage to all enemy units with Negative Charge."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Lightning Smash",
        "level": "3",
        "effect": "Increases the amount of dispelled buffs by 1. If\nthe target has 0 stability, perform an additional attack."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Grand Aura",
        "level": "3",
        "effect": "Fixed Stability Damage dealt at the start of battle is increased by 4 points. \nWhen Jiangyu has Chi, Electric damage dealt is increased by 15%. \nThe maximum stack limit of Voltage Sag is increased by 3. \nPower Surge effect changed: When dealing Electric damage, ignored DEF is increased to 10%, and healing received is increased to 10%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1",
        "level": "20",
        "keyName": "Fixed Key 1",
        "description": "At the start of battle, gains 4 stacks of Chi.",
        "icon": "assets/Jiangyu/Fixed Key 1.png"
      },
      {
        "node": "Fixed Key 2",
        "level": "20",
        "keyName": "Fixed Key 2",
        "description": "Before an enemy unit within a radius of 8 tiles performs an active attack, Jiangyu performs 1 Interception against it, dealing Electric damage equivalent to 60% of attack and 2 points of Stability Damage. Before the attack, applies Conductivity to the target for 1 turn. Can trigger up to 2 times per turn.",
        "icon": "assets/Jiangyu/Fixed Key 2.png"
      },
      {
        "node": "Fixed Key 3",
        "level": "30",
        "keyName": "Fixed Key 3",
        "description": "When inflicted with Taunt, Fear, Infatuated, or Stun, immediately cleanse the effect. Cooldown: 1 turn.",
        "icon": "assets/Jiangyu/Fixed Key 3.png"
      },
      {
        "node": "Fixed Key 4",
        "level": "30",
        "keyName": "Fixed Key 4",
        "description": "At the start of the turn, applies Positive Charge to the ally with the highest ATK for 3 turns.",
        "icon": "assets/Jiangyu/Fixed Key 4.png"
      },
      {
        "node": "Fixed Key 5",
        "level": "40",
        "keyName": "Fixed Key 5",
        "description": "Before an ally with Positive Charge (excluding self) uses an active skill, applies Defense Down II to the target for 2 turns.",
        "icon": "assets/Jiangyu/Fixed Key 5.png"
      },
      {
        "node": "Fixed Key 6",
        "level": "40",
        "keyName": "Fixed Key 6",
        "description": "All allies take 1 less point of Stability Damage.",
        "icon": "assets/Jiangyu/Fixed Key 6.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Jiangyu/Affinity Key.png"
      },
      {
        "node": "Common Key",
        "level": "40",
        "keyName": "Common Key",
        "description": "ATK +5.0% / Damage dealt to an enemy unit under Stability Break is increased by 10%.",
        "icon": "assets/Jiangyu/Common Key.png"
      },
      {
        "node": "Expansion Key - Urge to Perform",
        "level": "60",
        "keyName": "Expansion Key - Urge to Perform",
        "description": "When an enemy unit goes into Stability Break, Jiangyu deals Electric damage equal to 90% of attack (does not trigger Negative Charge effects). When allies with 3 stacks of Power Surge deal damage, for each stack of Voltage Sag on the target, the ally’s Critical Rate increases by 2% and Critical Damage increases by 3%.",
        "icon": "assets/Jiangyu/Expansion Key - Urge to Perform.png"
      }
    ]
  },
  "Makiatto": {
    "class": "Sentinel",
    "stats": {
      "hp": 1819,
      "atk": 844,
      "def": 504
    },
    "stabilityGauge": 9,
    "movementSpeed": 4,
    "skillAttributes": [
      "Heavy Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Light Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Lone Wolf Territory",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Makiatto/Lone Wolf Territory.png"
      },
      {
        "name": "Cold Precision Shot",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles and deals Freeze damage equal to 160% of attack. Increases the critical damage of this attack by 30%. Gains 1 stack of Cold Conviction for each instance of damage dealt.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Perform two attacks, critical damage will no longer increase, and the damage dealt is decreased to 100% of attack. If the first attack crits, the critical rate of the second attack is increased by 100%, and the critical damage is increased by 80%."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Additional Intelligence",
            "effect": "When the active skill Cold Precision Shot results in a kill, gains 1 point of Confectance Index."
          }
        ],
        "icon": "assets/Makiatto/Cold Precision Shot.png"
      },
      {
        "name": "Professional Tactics",
        "traits": [
          "Active",
          "Targeted",
          "Buff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles of self, deal Physical damage equal to 130% of attack, gain 4 points of Confectance Index, and gain 2 stacks of Standard Approach.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Change Standard Approach to Emergency Plan."
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Indomitable Lone Wolf",
            "effect": "After using the active skill Professional Tactics, if there are no other allied units within 3 tiles, gains 1 stack of Lone Wolf."
          }
        ],
        "icon": "assets/Makiatto/Professional Tactics.png"
      },
      {
        "name": "Absolute Mental Defense",
        "traits": [
          "Ultimate",
          "Buff",
          "Counter",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Gains Frost Barier and Alert for 2 turns. The absorption amount of Frost Barrier is equal to 65% of the initial attack, but cannot exceed 60% of max HP.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The absorption amount of Frost Barrier is increased to 80% of this unit's initial attack, and the cap is increased to 80% of max HP. The number of Interception triggered is increased by 1 time per turn."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "After using Absolute Mental Defense, gains 2 points of Confectance Index at the end of the action. This effect can be triggered 2 times.\n\nInterception can be triggered once more each turn. If the Interception deals a critical hit, gains Rapture for 1 turn."
          }
        ],
        "icon": "assets/Makiatto/Absolute Mental Defense.png"
      },
      {
        "name": "Battlefield Insight",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Increases critical rate by 40% and reduces critical damage by 10%.\n\nAt the start of the turn, if this unit's HP exceeds 80%, gains Insight and Steady Progress until the next turn. When attacking a target with Frozen, ignores 4 points of Stability Index and increases damage dealt to them by 20%. When attacking a target with Frigid, ignores 6 points of Stability Index and increases damage dealt to them by 30%. These effects cannot stack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "When dealing Freeze damage to an enemy target with Frozen, increases the Stability Index ignored to 6 points. When dealing Freeze damage to an enemy target with Frigid, increases the stability index ignored to 10 points."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "When dealing Freeze damage to an enemy target with Frozen or Frigid, increases the Stability Index ignored to 10 points and damage dealt by 30%."
          }
        ],
        "icon": "assets/Makiatto/Battlefield Insight.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Cold Precision Shot",
        "level": "2",
        "effect": "Perform two attacks, critical damage will no longer increase, and the damage dealt is decreased to 100% of attack. If the first attack crits, the critical rate of the second attack is increased by 100%, and the critical damage is increased by 80%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Absolute Mental Defence",
        "level": "2",
        "effect": "The absorption amount of Frost Barrier is increased to 80% of this unit's initial attack, and the cap is increased to 80% of max HP. The number of Interception triggered is increased by 1 time per turn."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Battlefield Insight",
        "level": "2",
        "effect": "When dealing Freeze damage to an enemy target with Frozen, increases the Stability Index ignored to 6 points. When dealing Freeze damage to an enemy target with Frigid, increases the stability index ignored to 10 points."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Professional Tactics",
        "level": "2",
        "effect": "Change Standard Approach to Emergency Plan."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Battlefield Insight",
        "level": "3",
        "effect": "When dealing Freeze damage to an enemy target with Frozen or Frigid, increases the Stability Index ignored to 10 points and damage dealt by 30%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Absolute Mental Defence",
        "level": "3",
        "effect": "After using Absolute Mental Defense, gains 2 points of Confectance Index at the end of the action. This effect can be triggered 2 times.\n\nInterception can be triggered once more each turn. If the Interception deals a critical hit, gains Rapture for 1 turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Additional Intelligence",
        "level": "20",
        "keyName": "Fixed Key 1 - Additional Intelligence",
        "description": "When the active skill Cold Precision Shot results in a kill, gains 1 point of Confectance Index.",
        "icon": "assets/Makiatto/Fixed Key 1 - Additional Intelligence.png"
      },
      {
        "node": "Fixed Key 2 - Freeze with Milk Foam",
        "level": "20",
        "keyName": "Fixed Key 2 - Freeze with Milk Foam",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Makiatto/Fixed Key 2 - Freeze with Milk Foam.png"
      },
      {
        "node": "Fixed Key 3 - Indomitable Lone Wolf",
        "level": "30",
        "keyName": "Fixed Key 3 - Indomitable Lone Wolf",
        "description": "After using the active skill Professional Tactics, if there are no other allied units within 3 tiles, gains 1 stack of Lone Wolf.",
        "icon": "assets/Makiatto/Fixed Key 3 - Indomitable Lone Wolf.png"
      },
      {
        "node": "Fixed Key 4 - Time for a Break",
        "level": "30",
        "keyName": "Fixed Key 4 - Time for a Break",
        "description": "When using Lone Wolf Territory, Cold Precision Shot, or Professional Tactics on a Freeze tile, cleanses all Freeze debuffs from self and gains 3 tiles of Additional Movement.",
        "icon": "assets/Makiatto/Fixed Key 4 - Time for a Break.png"
      },
      {
        "node": "Fixed Key 5 - Heated Caramel",
        "level": "40",
        "keyName": "Fixed Key 5 - Heated Caramel",
        "description": "At the start of the battle, applies Murderous Intent to the enemy unit with the highest HP.",
        "icon": "assets/Makiatto/Fixed Key 5 - Heated Caramel.png"
      },
      {
        "node": "Fixed Key 6 - Absolute Concentration",
        "level": "40",
        "keyName": "Fixed Key 6 - Absolute Concentration",
        "description": "Increases attack by 10% at the start of the battle. This effect lasts until HP drops below 100% for the first time.",
        "icon": "assets/Makiatto/Fixed Key 6 - Absolute Concentration.png"
      },
      {
        "node": "Affinity Key - Love So Sweet",
        "level": "-",
        "keyName": "Affinity Key - Love So Sweet",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Makiatto/Affinity Key - Love So Sweet.png"
      },
      {
        "node": "Common Key - Survival Instinct",
        "level": "40",
        "keyName": "Common Key - Survival Instinct",
        "description": "ATK +5.0% / At the start of the action, if own HP is greater than 80%, reduces Stability Damage taken from attacks by 2 points. This can trigger at most once per turn.",
        "icon": "assets/Makiatto/Common Key - Survival Instinct.png"
      },
      {
        "node": "Expansion Key - Sniper's Lock",
        "level": "60",
        "keyName": "Expansion Key - Sniper's Lock",
        "description": "Critical damage of Interceptions is increased by 30%.\n\nWhen Absolute Mental Defence is active, gains Extra Command and refunds Confectance Index consumed by the attack with said Extra Command. If the target of extra attacks is a Boss unit, before the attack, inflicts Sugar Overdose for 2 turns.",
        "icon": "assets/Makiatto/Expansion Key - Sniper's Lock.png"
      }
    ]
  },
  "Mechty": {
    "class": "Support",
    "stats": {
      "hp": 1876,
      "atk": 723,
      "def": 577
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Bedtime Warmup",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.\n\nWhen in Turbo Mode, damage type is changed to Corrosion damage, stability damage dealt is increased by 2 points, and Mechty gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Dream Fragment",
            "effect": "After using the basic attack Bedtime Warmup, gains 1 random buff for 1 turn."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Loser's Spirit",
            "effect": "When using the basic attack Bedtime Warmup, dispels 2 buffs from the target before the attack resolves."
          }
        ],
        "icon": "assets/Mechty/Bedtime Warmup.png"
      },
      {
        "name": "Dreamquake",
        "traits": [
          "Active",
          "AoE",
          "Tile"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "1",
        "description": "Selects 1 enemy unit within 8 tiles, dealing AoE Corrosion damage equal to 130% of attack to all enemies within 1 tile of the target.\n\nGains Movement Up II for 1 turn when Turbo Mode is active and generates Toxic Mist tiles for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Stability damage is increased by 2 points.\n\nWhen Turbo Mode is active, increases the damage of the next basic attack by 100%. Deals fixed damage equal to 50% of attack to all enemy units within range."
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Horror Movie Night",
            "effect": "When using the active skill Dreamquake, applies Acid Corrosion II for 2 turns before the attack resolves against large targets."
          }
        ],
        "icon": "assets/Mechty/Dreamquake.png"
      },
      {
        "name": "Dreamless Night",
        "traits": [
          "Active",
          "Buff",
          "Stability Regen"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "Self",
        "effArea": "Target",
        "description": "Recovers 6 points of stability, cleanses all debuffs on self, and applies Dream Guardian to all allied units within 8 tiles for 2 turns.\n\nWhen in Turbo Mode, the active skill Dreamquake or the basic attack Bedtime Warmup can be used after using this skill. Gains 1 stack of Sleep Aid Kit for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "The maximum stacks of Sleep Aid Kit is increased by 1. Mechty recovers HP equal to 30% of maximum HP and the allied unit with the lowest HP recovers 15% of Mechty's maximum HP and 3 points of stability.\n\nWhen in Turbo Mode, the number of Sleep Aid Kit stacks gained is increased by 1."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Quickly, So We Can Sleep",
            "effect": "When using the active skill Dreamless Night, generates Toxic Mist tiles within 2 tiles around the closest enemy for 2 turns."
          }
        ],
        "icon": "assets/Mechty/Dreamless Night.png"
      },
      {
        "name": "Dream Wonderland",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 4,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Entire Map",
        "description": "Deactivates Patch Mode and enters Turbo Mode for 3 turns. After Turbo Mode ends, returns to Patch Mode.\n\nApplies Nightmarish Shroud to all allied units and inflicts Toxic Inundation to the closest enemy target for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "No longer deactivates Patch Mode when entering Turbo Mode.\n\nNightmarish Shroud reduces the attacker's attack by 10% and increases the amount of debuffs cleansed by 1.\n\nTurbo Mode gains new effect: The critical rate of basic attacks is increased by 30%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Turbo Mode gains new effects: Mobility is increased by 2 tiles, applies Nightmarish Shroud to allied units without Nightmarish Shroud at the end of the action. Gains 1 more point of Confectance Index."
          }
        ],
        "icon": "assets/Mechty/Dream Wonderland.png"
      },
      {
        "name": "Mysterious Nap",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "",
        "effArea": "",
        "description": "At the start of battle, Mechty enters Patch Mode, and applies Nightmare Form to all allied units.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Patch Mode gains new effects: Basic attacks deal 50% more damage. At the start of the turn, cleanses 2 debuffs on self."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Patch Mode gains new effects: Corrosion damage dealt by all allied units is increased by 25%, increases critical damage dealt by Mechty's basic attack by 80%.\n\nNightmare Form gains new effects: AoE damage dealt by Support Attacks is increased to 80%, Stability damage dealt is increased by 1 point, and AoE damage dealt is increased to 20%."
          }
        ],
        "icon": "assets/Mechty/Mysterious Nap.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Dream Wonderland",
        "level": "2",
        "effect": "No longer deactivates Patch Mode when entering Turbo Mode.\n\nNightmarish Shroud reduces the attacker's attack by 10% and increases the amount of debuffs cleansed by 1.\n\nTurbo Mode gains new effect: The critical rate of basic attacks is increased by 30%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Mysterious Nap",
        "level": "2",
        "effect": "Patch Mode gains new effects: Basic attacks deal 50% more damage. At the start of the turn, cleanses 2 debuffs on self."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Dreamless Night",
        "level": "2",
        "effect": "The maximum stacks of Sleep Aid Kit is increased by 1. Mechty recovers HP equal to 30% of maximum HP and the allied unit with the lowest HP recovers 15% of Mechty's maximum HP and 3 points of stability.\n\nWhen in Turbo Mode, the number of Sleep Aid Kit stacks gained is increased by 1."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Dreamquake",
        "level": "2",
        "effect": "Stability damage is increased by 2 points.\n\nWhen Turbo Mode is active, increases the damage of the next basic attack by 100%. Deals fixed damage equal to 50% of attack to all enemy units within range."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Dream Wonderland",
        "level": "3",
        "effect": "Turbo Mode gains new effects: Mobility is increased by 2 tiles, applies Nightmarish Shroud to allied units without Nightmarish Shroud at the end of the action. Gains 1 more point of Confectance Index."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Mysterious Nap",
        "level": "3",
        "effect": "Patch Mode gains new effects: Corrosion damage dealt by all allied units is increased by 25%, increases critical damage dealt by Mechty's basic attack by 80%.\n\nNightmare Form gains new effects: AoE damage dealt by Support Attacks is increased to 80%, Stability damage dealt is increased by 1 point, and AoE damage dealt is increased to 20%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Dream Fragment",
        "level": "20",
        "keyName": "Fixed Key 1 - Dream Fragment",
        "description": "After using the basic attack Bedtime Warmup, gains 1 random buff for 1 turn.",
        "icon": "assets/Mechty/Fixed Key 1 - Dream Fragment.png"
      },
      {
        "node": "Fixed Key 2 - Rest Thee Well",
        "level": "20",
        "keyName": "Fixed Key 2 - Rest Thee Well",
        "description": "If any weakness is exploited, applies Toxic Inundation to the target after the attack resolves.",
        "icon": "assets/Mechty/Fixed Key 2 - Rest Thee Well.png"
      },
      {
        "node": "Fixed Key 3 - Horror Movie Night",
        "level": "30",
        "keyName": "Fixed Key 3 - Horror Movie Night",
        "description": "When using the active skill Dreamquake, applies Acid Corrosion II for 2 turns before the attack resolves against large targets.",
        "icon": "assets/Mechty/Fixed Key 3 - Horror Movie Night.png"
      },
      {
        "node": "Fixed Key 4 - Quickly, So We Can Sleep",
        "level": "30",
        "keyName": "Fixed Key 4 - Quickly, So We Can Sleep",
        "description": "When using the active skill Dreamless Night, generates Toxic Mist tiles within 2 tiles around the closest enemy for 2 turns.",
        "icon": "assets/Mechty/Fixed Key 4 - Quickly, So We Can Sleep.png"
      },
      {
        "node": "Fixed Key 5 - Loser's Spirit",
        "level": "40",
        "keyName": "Fixed Key 5 - Loser's Spirit",
        "description": "When using the basic attack Bedtime Warmup, dispels 2 buffs from the target before the attack resolves.",
        "icon": "assets/Mechty/Fixed Key 5 - Loser's Spirit.png"
      },
      {
        "node": "Fixed Key 6 Idler's Sofa Aura",
        "level": "40",
        "keyName": "Fixed Key 6 Idler's Sofa Aura",
        "description": "When Mechty has 2 or more buffs, targeted damage taken is reduced by 20%.",
        "icon": "assets/Mechty/Fixed Key 6 Idler's Sofa Aura.png"
      },
      {
        "node": "Affinity Key",
        "level": "40",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Mechty/Affinity Key.png"
      },
      {
        "node": "Common Key - Gaming Time",
        "level": "40",
        "keyName": "Common Key - Gaming Time",
        "description": "ATK +5.0% / Basic Attack damage is increased by 20%.",
        "icon": "assets/Mechty/Common Key - Gaming Time.png"
      },
      {
        "node": "Expansion Key - Sleepberserking Syndrome",
        "level": "60",
        "keyName": "Expansion Key - Sleepberserking Syndrome",
        "description": "At the start of the battle, enters Sleepwalking state and gains an additional skill: Awakening Command\n\nIf Mechty is in Sleepwalking at the start of the round, consumes all Confectance Index and gains maximum stacks of Sleep Aid Kit for 2 turns. For each Confectance Index consumed, cleanses 1 debuff from self, and applies 1 stack of Dreamscape Exhilaration for 1 round (Duration decreases at the end of the current round)\n\nIf Mechty is in Sleepwalking at the end of her action, for each stack of Sleep Aid Kit held by self, activates an instance of Waking Ricochet on the closest enemy, recovers HP equivalent to 10% ATK and 1 Stability for all allies",
        "icon": "assets/Mechty/Expansion Key - Sleepberserking Syndrome.png"
      }
    ]
  },
  "Peri": {
    "class": "Bulwark",
    "stats": {
      "hp": 2191,
      "atk": 696,
      "def": 560
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Passionate Gift",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Peri/Passionate Gift.png"
      },
      {
        "name": "Venture Capital",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Consumes HP equivalent to 30% of max HP, and gains 2 stacks of Hot Investment (this effect will not lower HP below 10%). Selects an enemy target within a 6 tile radius and deals Burn damage equivalent to 120% ATK to it.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Decreases HP consumed by 10%. For each stack of Hot Investment held by self, increases damage multiplier by 10%. Before attacking, dispels 1 buff from the target"
          }
        ],
        "icon": "assets/Peri/Venture Capital.png"
      },
      {
        "name": "Excess Order",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "2",
        "description": "Consumes HP equivalent to 40% of max HP, and gains 3 stacks of Hot Investment (this effect will not lower HP below 10%). Selects a tile within a 6 tile radius of tile and deals AoE Burn damage equivalent to 100% ATK to all enemies within a 2 tile radius of the specified tile, and applies Overburn for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Decreases HP consumed by 10%. Increases effect range by 1 tile. For each stack of Hot Investment held by self, increases damage multiplier by 5%"
          }
        ],
        "icon": "assets/Peri/Excess Order.png"
      },
      {
        "name": "Final Bid",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "Target",
        "description": "Gains 6 stacks of Hot Investment, gains Bargain and Capital Protection for 3 rounds (Duration decreases at the end of the current round). Capital Protection can absorb damage equivalent to 50% of Peri's max HP.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Enhanced the effect of Bargain - Increases damage dealt by 30% (From 30%→ 60%). When Bargain expires, restores Stability to maximum."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "New effect is added for Bargain - Increases CRIT DMG dealt by normal attacks by 50%.\n\nNew effect is added for Capital Protection - Before being attacked, decreases ATK for the attacker by 30%."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4",
            "effect": "Final Bid: After usage, cleanses all debuffs from self"
          }
        ],
        "icon": "assets/Peri/Final Bid.png"
      },
      {
        "name": "Profit Maximization",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the action, increases Confectance Index by 1 point. When allies (excluding self) activate Action Support that deals Burn damage, if Peri's Confectance Index is below 6 points, increases Confectance Index by 1 point. This effect can activate once per round\n\nAfter using an active skill, for every 3 stacks of Hot Investment held by self, Peri can 1 basic attack. The effects of this basic attack is changed to dealing Burn damage equivalent to 12% of Peri's initial max HP for each stack of Hot Investment held by self.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Decreases the number of Hot Investment stacks required to launch 1 basic attack by 1."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "At the start of the battle, increases Stability by 6 points. For each stack of Hot Investment held by self, increases Burn damage dealt by self by 8%"
          }
        ],
        "icon": "assets/Peri/Profit Maximization.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Profit Maximization",
        "level": "2",
        "effect": "Decreases the number of Hot Investment stacks required to launch 1 basic attack by 1."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Final Bid",
        "level": "2",
        "effect": "Enhanced the effect of Bargain - Increases damage dealt by 30% (From 30%→ 60%). When Bargain expires, restores Stability to maximum."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Profit Maximization",
        "level": "3",
        "effect": "At the start of the battle, increases Stability by 6 points. For each stack of Hot Investment held by self, increases Burn damage dealt by self by 8%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Excess Order",
        "level": "2",
        "effect": "Decreases HP consumed by 10%. Increases AoE effect range by 1 tile. For each stack of Hot Investment held by self, increases damage multiplier by 5%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Venture Capital",
        "level": "2",
        "effect": "Decreases HP consumed by 10%. For each stack of Hot Investment held by self, increases damage multiplier by 10%. Before attacking, cleanse 1 buff from the target."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Final Bid",
        "level": "3",
        "effect": "New effect is added for Bargain - Increases CRIT DMG dealt by normal attacks by 50%.\n\nNew effect is added for Capital Protection - Before being attacked, decreases ATK for the attacker by 30%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Basis of Trade",
        "level": "20",
        "keyName": "Fixed Key 1 - Basis of Trade",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Peri/Fixed Key 1 - Basis of Trade.png"
      },
      {
        "node": "Fixed Key 2 - Cool and Reliable",
        "level": "20",
        "keyName": "Fixed Key 2 - Cool and Reliable",
        "description": "For each stack of Hot Investment held, increases DEF by 5%",
        "icon": "assets/Peri/Fixed Key 2 - Cool and Reliable.png"
      },
      {
        "node": "Fixed Key 3 - Insider Information",
        "level": "30",
        "keyName": "Fixed Key 3 - Insider Information",
        "description": "At the start of the turn, if the number of stacks of Hot Investment held is more than 2, gains 2 layers of Shelter",
        "icon": "assets/Peri/Fixed Key 3 - Insider Information.png"
      },
      {
        "node": "Fixed Key 4 - Independent Woman",
        "level": "30",
        "keyName": "Final Bid",
        "description": "After usage, cleanses all debuffs from self",
        "icon": "assets/Peri/Final Bid.png"
      },
      {
        "node": "Fixed Key 5 - Mature Adult",
        "level": "40",
        "keyName": "Fixed Key 5 - Mature Adult",
        "description": "When Peri is inflicted with Stun, Taunt, or Paralysis, immediately cleanses the effect, and becomes immune to Stun, Taunt and Paralysis for 1 turn and restores HP equivalent to 20% max HP for self. This effect has a cooldown of 3 turns",
        "icon": "assets/Peri/Fixed Key 5 - Mature Adult.png"
      },
      {
        "node": "Fixed Key 6 - Social Engineering",
        "level": "40",
        "keyName": "Fixed Key 6 - Social Engineering",
        "description": "Increases damage dealt to targets with Burn type debuffs by 10%",
        "icon": "assets/Peri/Fixed Key 6 - Social Engineering.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Peri/Affinity Key.png"
      },
      {
        "node": "Common Key - Still growing",
        "level": "40",
        "keyName": "Common Key - Still growing",
        "description": "HP +5.0% / When attacking the same target multiple times, increases elemental damage dealt towards it by 10%",
        "icon": "assets/Peri/Common Key - Still growing.png"
      },
      {
        "node": "Expansion Key - Broker Scheme",
        "level": "60",
        "keyName": "Expansion Key - Broker Scheme",
        "description": "Basic attacks now attack twice.\nHot Investment now no longer reduce healing efficacy.\nFor each stack of Hot Investment, reduces damage taken by all allied units (excluding Peri herself) by 5%.\nThe passive effects of Profit Maximization is changed: When allied units (excluding Peri herself) deal Burn damage, it triggers Peri's Confectance Index gain effect.",
        "icon": "assets/Peri/Expansion Key - Broker Scheme.png"
      }
    ]
  },
  "Qiuhua": {
    "class": "Vanguard",
    "stats": {
      "hp": 1713,
      "atk": 757,
      "def": 536
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Shotgun Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Trailblaze",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Qiuhua/Trailblaze.png"
      },
      {
        "name": "Searing Sizzle",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Burn damage equivalent to 120% ATK to it. If the distance between Qiuhua and the target is less or equal to 4 tiles, increases damage dealt by 5% and Stability damage dealt by 1 point",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "After attacking, gains 6 tiles of Additional Movement\n\nIf the target has Scorch Mark, increases damage dealt by 30%\n\nIf the distance between Qiuhua and the target is less or equal to 4 tiles, increases damage dealt by 5% → 15% and Stability damage dealt by 1 → 2 points"
          }
        ],
        "icon": "assets/Qiuhua/Searing Sizzle.png"
      },
      {
        "name": "Soaring Leap",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "6",
        "description": "Selects a tile within a 6 tile radius of self and lands on the selected tile, dealing Burn damage equivalent to 30% ATK to the nearest enemy target within a 6 tile radius. After attacking, gains Extra Command. Reduces the cooldown of Ultimate by 1 turn",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier by 50%\n\nIf the target has Scorch Mark, deals an additional instance of fixed damage equivalent to 50% ATK\n\nAfter attacking, gains Phase Boost II and Stability Offensive II for 1 turn"
          }
        ],
        "icon": "assets/Qiuhua/Soaring Leap.png"
      },
      {
        "name": "Boil and Reduce",
        "traits": [
          "Ultimate",
          "AoE",
          "Debuff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Selects a tile within a 6 tile radius of self, dealing AoE Burn damage equivalent to 90% ATK and applying Scorch Mark to all enemies within a 3 tile radius of the specified tile. This skill consumes all Confectance Index, for each point of Confectance Index consumed, increases damage multiplier by 5%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Reduces cooldown by 1 turn. When dealing damage, immediately triggers the effect of Scorch Mark that are triggered at the end of the holder's action once"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "If this skill hit 1 target, increases damage dealt by 15%\n\nEnhanced the effects of Scorch Mark - increases damage dealt per stack to 10% of the caster's ATK, and increases the number of stack gained when receiving Burn damage to 2"
          },
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Emergency Support can be activated 1 → 2 times per turn\n\nIncreases Burn damage dealt by 5% → 15%. Removes the condition required to activate this effect\n\nWhen dealing damage, if CRIT rate is above 100%, each 1% additional CRIT rate is converted into 1% CRIT DMG"
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Scorch Mark no longer has a maximum stack limit\n\nNew effect is added when dealing Burn damage towards targets with Scorch Mark - if the number of stacks of Scorch Mark is more than 10, for each additional stack, increases ATK by 1%"
          }
        ],
        "icon": "assets/Qiuhua/Boil and Reduce.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Boil and Reduce",
        "level": "2",
        "effect": "Reduces cooldown by 1 turn. When dealing damage, immediately triggers the effect of Scorch Mark that are triggered at the end of the holder's action once"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Zao Jun's Rule",
        "level": "2",
        "effect": "Emergency Support can be activated 1 → 2 times per turn\n\nIncreases Burn damage dealt by 5% → 15%. Removes the condition required to activate this effect\n\nWhen dealing damage, if CRIT rate is above 100%, each 1% additional CRIT rate is converted into 1% CRIT DMG"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Zao Jun's Rule",
        "level": "3",
        "effect": "Scorch Mark no longer has a maximum stack limit\n\nNew effect is added when dealing Burn damage towards targets with Scorch Mark - if the number of stacks of Scorch Mark is more than 10, for each additional stack, increases ATK by 1%"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Soaring Leap",
        "level": "2",
        "effect": "Increases damage multiplier by 50%\n\nIf the target has Scorch Mark, deals an additional instance of fixed damage equivalent to 50% ATK\n\nAfter attacking, gains Phase Boost II and Stability Offensive II for 1 turn"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Searing Sizzle",
        "level": "2",
        "effect": "After attacking, gains 6 tiles of Additional Movement\n\nIf the target has Scorch Mark, increases damage dealt by 30%\n\nIf the distance between Qiuhua and the target is less or equal to 4 tiles, increases damage dealt by 5% → 15% and Stability damage dealt by 1 → 2 points"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Boil and Reduce",
        "level": "3",
        "effect": "If this skill hit 1 target, increases damage dealt by 15%\n\nEnhanced the effects of Scorch Mark - increases damage dealt per stack to 10% of the caster's ATK, and increases the number of stack gained when receiving Burn damage to 2"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Meal Prep",
        "level": "20",
        "keyName": "Fixed Key 1 - Meal Prep",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Qiuhua/Fixed Key 1 - Meal Prep.png"
      },
      {
        "node": "Fixed Key 2 - Roaring Stove",
        "level": "20",
        "keyName": "Fixed Key 2 - Roaring Stove",
        "description": "At the start of the turn, applies Scorch Mark to the enemy with the highest HP. This has a cooldown of 2 turns",
        "icon": "assets/Qiuhua/Fixed Key 2 - Roaring Stove.png"
      },
      {
        "node": "Fixed Key 3 - Slice and Dice",
        "level": "30",
        "keyName": "Fixed Key 3 - Slice and Dice",
        "description": "Becomes immune to all debuffs inflicted by Burn tiles and all Burn type debuffs. At the end of the action, if Qiuhua is on a Burn tile, restores 2 Stability and HP equivalent to 10% max HP",
        "icon": "assets/Qiuhua/Fixed Key 3 - Slice and Dice.png"
      },
      {
        "node": "Fixed Key 4 - Fragrant Stir-Fry",
        "level": "30",
        "keyName": "Fixed Key 4 - Fragrant Stir-Fry",
        "description": "Before using an active attack, applies Overburn on the target for 1 turn",
        "icon": "assets/Qiuhua/Fixed Key 4 - Fragrant Stir-Fry.png"
      },
      {
        "node": "Fixed Key 5 - Cooking Smoke",
        "level": "40",
        "keyName": "Fixed Key 5 - Cooking Smoke",
        "description": "After moving, gains 1 stack of Quick Barrier",
        "icon": "assets/Qiuhua/Fixed Key 5 - Cooking Smoke.png"
      },
      {
        "node": "Fixed Key 6 - Bloated Belly",
        "level": "40",
        "keyName": "Fixed Key 6 - Bloated Belly",
        "description": "Before undergoing Emergency Support, dispels 1 buff from the target",
        "icon": "assets/Qiuhua/Fixed Key 6 - Bloated Belly.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Qiuhua/Affinity Key.png"
      },
      {
        "node": "Common Key",
        "level": "40",
        "keyName": "Common Key",
        "description": "CRIT +5.0% / When Out-of-Turn attack deals Burn damage, increases damage dealt by 10%",
        "icon": "assets/Qiuhua/Common Key.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "Emergency Support damage multiplier is increased by 30% and when dealing damage, ignores 15% of target's defense; for each Emergency Support performed, gain 1 stack of Wok Aura for 2 rounds.\n\nWok Aura: Burn damage dealt increased by 7%, damage taken reduced by 7%, stacks up to 4 times. Considered a Burn buff, cannot be cleansed.\n\nWhen a unit with Scorch Mark dies, deals AoE Burn damage equal to 130% of Qiuhua's attack to all allied units within a radius of 3 tiles.\n\nWhen the active skill Soaring Leap deals damage, creates Incineration tiles within a radius of 1 tile around the target, lasting for 2 turns.",
        "icon": "assets/Qiuhua/Expansion Key.png"
      }
    ]
  },
  "Yoohee": {
    "class": "Support",
    "stats": {
      "hp": 1851,
      "atk": 757,
      "def": 585
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "-"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Rhythmic Pulse",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Yoohee/Rhythmic Pulse.png"
      },
      {
        "name": "Improv",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Physical damage equivalent to 120% ATK to it. If Yoohee has 3 or more points of Confectance Index, consumes 2 additional points of Confectance Index to ignore 30% of the target's defense on this attack",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases the damage multiplier by 60%. For each Dance Steps applied, gains 1 stack of Fantastic Conception"
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Effort and Returns",
            "effect": "Improv: When additional points of Confectance Index is consumed, increases CRIT DMG dealt by 5%"
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Tempo Resonance",
            "effect": "Improv: Before skill usage, dispels 1 random buff from the target"
          }
        ],
        "icon": "assets/Yoohee/Improv.png"
      },
      {
        "name": "Soul of Dance",
        "traits": [
          "Active",
          "AoE",
          "Buff",
          "Control"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "2",
        "description": "Selects an ally within a 8 tile radius, and applies Targeted Attack Defense I to it and all allies within a 2 tile radius of the selected ally for 2 turns.\n\nDeals AoE Physical damage equal to 80% ATK to all enemies within range, and applies Stun for 1 turn. After the attack, Yoohee gains 1 use of active skill Graceful Piroulette or Passionate Resonance.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the damage multiplier by 50%, and increases the effect range by 1 tile\n\nTargeted Attack Defense II is applied instead of Targeted Attack Defense I. Cleanses Taunt, Fear, Stun, and Infatuated for all allies"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Infectious Emotions",
            "effect": "Soul of Dance: After this skill applies Stun on the enemy, when Stun is removed, applies Movement Denied for 1 turn"
          }
        ],
        "icon": "assets/Yoohee/Soul of Dance.png"
      },
      {
        "name": "Sparkling Finale",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Entire Map",
        "description": "Yoohee gains Troupe's Core for 3 turns. Applies Stability Offensive I for all allies for 2 turns. After skill usage, gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Stability Offensive II is applied instead of Stability Offensive I. Additionally applies Attack Up II for all allied units for 2 turns\n\nAfter skill usage, if Graceful Pirouette or Passionate Resonance is used on this turn, the effects are applied to all allies"
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Yoohee gains 1 stack of Never Give Up\n\nNew effect is added for Troupe's Core - When attacking, ignores 50% of the enemy's DEF. After triggering the effects of Best Dancer, immediately activates Improv on the enemy with the highest current HP within range. This effect can only trigger once per round, and Graceful Pirouette and Passionate Resonance cannot be used after that instance of the skill \n\nFor every 2 times Best Dancer is triggered, reduces the cooldown of this skill by 1 turn"
          }
        ],
        "icon": "assets/Yoohee/Sparkling Finale.png"
      },
      {
        "name": "Main Dancer's Aura",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "When allies deal Physical damage, Yoohee gains 1 point of Confectance Index.\n\nAfter using basic attack or active skills, Graceful Pirouette or Passionate Resonance can be used (this effect cannot be triggered repeatedly).\n\nFor 3 or more Dance Steps applies, triggers an instance of Best Dancer, and gains 1 stack of Never Give Up, and refreshes the duration of all Dance Steps and Reversed Assault stacks across the entire battlefield.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The selection range of Graceful Pirouette and Passionate Resonance is expanded to the entire field\n\nNew effect is added for Graceful Pirouette- Restores HP equivalent to 15% max HP\n\nNew effect is added for Passionate Resonance - Cleanses 1 debuff from the target\n\nWhen Best Dancer is triggered, applies Defense Down II for the enemy with the highest initial DEF for 3 turns. if Yoohee has Troupe's Core, Never Give Up decreases damage taken by allies by 30%"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Doubles the effects of Dance Steps for self (Increases CRIT DMG by 20%, recovers HP equivalent to 40% ATK, gains 3 stacks of Shelter)\n\nFor each buff applies to other allies, increases ATK by 1.5% for self, up to a maximum of 45%. When triggering Best Dancer, applies Preshow Warmup for all allies for 2 turns"
          }
        ],
        "icon": "assets/Yoohee/Main Dancer's Aura.png"
      },
      {
        "name": "Graceful Pirouette",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an ally (excluding self) within a 8 tile radius, and applies Graceful Spin and Reversed Assault for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The selection range of Graceful Pirouette and Passionate Resonance is expanded to the entire field\n\nNew effect is added for Graceful Pirouette- Restores HP equivalent to 15% max HP\n\nNew effect is added for Passionate Resonance - Cleanses 1 debuff from the target\n\nWhen Best Dancer is triggered, applies Defense Down II for the enemy with the highest initial DEF for 3 turns. if Yoohee has Troupe's Core, Never Give Up decreases damage taken by allies by 30%"
          }
        ],
        "icon": "assets/Yoohee/Graceful Pirouette.png"
      },
      {
        "name": "Passionate Resonance",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an ally (excluding self) within a 8 tile radius, and applies Passionate Spin and Reversed Assault for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The selection range of Graceful Pirouette and Passionate Resonance is expanded to the entire field\n\nNew effect is added for Graceful Pirouette- Restores HP equivalent to 15% max HP\n\nNew effect is added for Passionate Resonance - Cleanses 1 debuff from the target\n\nWhen Best Dancer is triggered, applies Defense Down II for the enemy with the highest initial DEF for 3 turns. if Yoohee has Troupe's Core, Never Give Up decreases damage taken by allies by 30%"
          }
        ],
        "icon": "assets/Yoohee/Passionate Resonance.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Sparkling Finale",
        "level": "2",
        "effect": "Stability Offensive II is applied instead of Stability Offensive I. Additionally applies Attack Up II for all allied units for 2 turns\n\nAfter skill usage, if Graceful Pirouette or Passionate Resonance is used on this turn, the effects are applied to all allies"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Main Dancer's Aura",
        "level": "2",
        "effect": "The selection range of Graceful Pirouette and Passionate Resonance is expanded to the entire field\n\nNew effect is added for Graceful Pirouette- Restores HP equivalent to 15% max HP\n\nNew effect is added for Passionate Resonance - Cleanses 1 debuff from the target\n\nWhen Best Dancer is triggered, applies Defense Down II for the enemy with the highest initial DEF for 3 turns. if Yoohee has Troupe's Core, Never Give Up decreases damage taken by allies by 30%"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Sparkling Finale",
        "level": "3",
        "effect": "Yoohee gains 1 stack of Never Give Up\n\nNew effect is added for Troupe's Core - When attacking, ignores 50% of the enemy's DEF. After triggering the effects of Best Dancer, immediately activates Improv on the enemy with the highest current HP within range. This effect can only trigger once per round, and Graceful Pirouette and Passionate Resonance cannot be used after that instance of the skill \n\nFor every 2 times Best Dancer is triggered, reduces the cooldown of this skill by 1 turn"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Improv",
        "level": "2",
        "effect": "Increases the damage multiplier by 60%. For each Dance Steps applied, gains 1 stack of Fantastic Conception"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Soul of Dance",
        "level": "2",
        "effect": "Increases the damage multiplier by 50%, and increases the effect range by 1 tile\n\nTargeted Attack Defense II is applied instead of Targeted Attack Defense I. Cleanses Taunt, Fear, Stun, and Infatuated for all allies"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Main Dancer's Aura",
        "level": "3",
        "effect": "Doubles the effects of Dance Steps for self (Increases CRIT DMG by 20%, recovers HP equivalent to 40% ATK, gains 3 stacks of Shelter)\n\nFor each buff applies to other allies, increases ATK by 1.5% for self, up to a maximum of 45%. When triggering Best Dancer, applies Preshow Warmup for all allies for 2 turns"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Effort and Returns",
        "level": "20",
        "keyName": "Improv",
        "description": "When additional points of Confectance Index is consumed, increases CRIT DMG dealt by 5%",
        "icon": "assets/Yoohee/Improv.png"
      },
      {
        "node": "Fixed Key 2 - Enjoy The Limelight",
        "level": "20",
        "keyName": "Best Dancer",
        "description": "When this effect is triggered, restores HP equivalent to 20% max HP",
        "icon": "assets/Yoohee/Best Dancer.png"
      },
      {
        "node": "Fixed Key 3 - Tempo Resonance",
        "level": "30",
        "keyName": "Improv",
        "description": "Before skill usage, dispels 1 random buff from the target",
        "icon": "assets/Yoohee/Improv.png"
      },
      {
        "node": "Fixed Key 4 - Infectious Emotions",
        "level": "30",
        "keyName": "Soul of Dance",
        "description": "After this skill applies Stun on the enemy, when Stun is removed, applies Movement Denied for 1 turn",
        "icon": "assets/Yoohee/Soul of Dance.png"
      },
      {
        "node": "Fixed Key 5 - Marvellous Shift",
        "level": "40",
        "keyName": "Fixed Key 5 - Marvellous Shift",
        "description": "If Yoohee did not move on this turn, increases attack range of basic attack and skills by 3 tiles on the next turn",
        "icon": "assets/Yoohee/Fixed Key 5 - Marvellous Shift.png"
      },
      {
        "node": "Fixed Key 6 - Exquisite Choreography",
        "level": "40",
        "keyName": "Never Give Up",
        "description": "When this effect is active, increases ATK by 10%",
        "icon": "assets/Yoohee/Never Give Up.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Yoohee/Affinity Key.png"
      },
      {
        "node": "Common Key - Main Dancer's Might",
        "level": "40",
        "keyName": "Common Key - Main Dancer's Might",
        "description": "ATK +5% / When dealing Ammo-type damage, increases damage dealt by 10%",
        "icon": "assets/Yoohee/Common Key - Main Dancer's Might.png"
      },
      {
        "node": "Expansion Key - Flawless Dance Moves",
        "level": "60",
        "keyName": "Expansion Key - Flawless Dance Moves",
        "description": "After using Sparkling Finale, when using Graceful Pirouette or Passionate Resonance, the skill will also trigger on 2 allies with the highest ATK that were not selected by the skill (excluding self). These 2 skills can no longer be used on the current turn\n\nWhen dealing Physical damage from a passive skill, triggers the effects of Never Give Up. Its effects will no longer be nullified if allies dealt Phase damage\n\nIncreases healing received by allies by 50%. At the start of the battle, for each Physical attribute ally on the field, increases Physical damage dealt by allies by 3%, up to a maximum of 15%",
        "icon": "assets/Yoohee/Expansion Key - Flawless Dance Moves.png"
      }
    ]
  },
  "Nikketa": {
    "class": "Sentinel",
    "stats": {
      "hp": 1859,
      "atk": 836,
      "def": 519
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Heavy Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Light Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Active Deterrence",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Nikketa/Active Deterrence.png"
      },
      {
        "name": "K9 Deployment",
        "traits": [
          "Active",
          "AoE",
          "Summon",
          "Debuff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "2",
        "description": "Selects an empty tile within a 9 tile radius, and summons Kulich, then deals AoE Physical damage equivalent to 80% ATK to all enemies within a 2 tiles radius of the selected tile, and applies Guilt for 2 turns. If Kulich is already present, teleports Kulich to the selected tile instead. Nikketa gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases Stability damage by 2 points\n\nEnhanced the effects of Guilt - Takes 10% more Hydro damage instead, and restores Kulich HP by 30% max HP after relocation"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the range of Kulich's Loyalty by 2 tiles. Increases Kulich inherited HP to 100%\n\nKulich gains Kulich's Intimidation"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4",
            "effect": "K9 Deployment: After skill usage, generates Tideaway in the effective area for 2 turns"
          }
        ],
        "icon": "assets/Nikketa/K9 Deployment.png"
      },
      {
        "name": "Judgement Strike",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius, deals Hydro damage equivalent to 80% ATK to it, and applies Guilt for 2 turns. Nikketa gains 2 points of Confectance Index and Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Damage multiplier increased by 20%\n\nExtra Command is replaced with Extra Action"
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3",
            "effect": "Judgement Strike: This skill now deals AoE Hydro damage equivalent to 80% ATK to all enemies within a 2 tiles radius"
          }
        ],
        "icon": "assets/Nikketa/Judgement Strike.png"
      },
      {
        "name": "Righteous Verdict",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius, deals Hydro damage equivalent to 130% ATK to it. If the target has Guilt, performs an additional attack, and removes Guilt\n\nConsumes all Confectance Index, for each additional point of Confectance Index consumed, increases the damage of this skill by 5%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Damage multiplier increased by 20%. Decreases Confectance Cost by 1 point\n\nIf the target has Guilt, applies Monitoring on the target after skill activation for 1 turn"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For each additional point of Confectance Index consumed, increases damage by 10% instead. Guilt will no longer be removed"
          }
        ],
        "icon": "assets/Nikketa/Righteous Verdict.png"
      },
      {
        "name": "On-site Enforcement",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "If Kulich is present, Nikketa gains Insight. Before Nikketa and Kulich activates their skill, both gains 1 stack of Clue, if Phase Weakness is exploited, gains an additional stack of Clue\n\nKulich can only perform Counterattack once per round. After performing Counterattack, Nikketa will follow up by using her ultimate skill Righteous Verdict against the target (Righteous Verdict does not have a Confectance Cost requirement)",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Doubles the maximum stack limit for Clue to 10 stacks. Kulich can perform an additional Counterattack per turn"
          }
        ],
        "icon": "assets/Nikketa/On-site Enforcement.png"
      },
      {
        "name": "Kulich's Loyalty",
        "traits": [
          "Passive",
          "Counterattack"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Enemies will not select Kulich as the target of their attacks\n\nIf enemies within a 3 tile radius deal damage, performs Counterattack, dealing Hydro damage equivalent to 80% ATK and 2 Stability damage",
        "upgrades": [],
        "icon": "assets/Nikketa/Kulich's Loyalty.png"
      },
      {
        "name": "Kulich's Intimidation",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "5",
        "effArea": "Target",
        "description": "Decreases ATK for all enemies within a 5 tile radius by 10%\n\nThis passive is only unlocked after reaching Vertebrae 5",
        "upgrades": [],
        "icon": "assets/Nikketa/Kulich's Intimidation.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Judgement Strike",
        "level": "2",
        "effect": "Damage multiplier increased by 20%\n\nExtra Command is replaced with Extra Action"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Righteous Verdict",
        "level": "2",
        "effect": "Damage multiplier increased by 20%. Decreases Confectance Cost by 1 point\n\nIf the target has Guilt, applies Monitoring on the target after skill activation for 1 turn"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "On-site Enforcement",
        "level": "2",
        "effect": "Doubles the maximum stack limit for Clue to 10 stacks. Kulich can perform an additional Counterattack per turn"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "K9 Deployment",
        "level": "2",
        "effect": "Increases Stability damage by 2 points\n\nEnhanced the effects of Guilt - Takes 10% more Hydro damage instead, and restores Kulich HP by 30% max HP after relocation"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "K9 Deployment",
        "level": "3",
        "effect": "Increases the range of Kulich's Loyalty by 2 tiles. Increases Kulich inherited HP to 100%\n\nKulich gains Kulich's Intimidation"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Righteous Verdict",
        "level": "3",
        "effect": "For each additional point of Confectance Index consumed, increases damage by 10% instead. Guilt will no longer be removed"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Righteous Doll",
        "level": "20",
        "keyName": "Fixed Key 1 - Righteous Doll",
        "description": "After using basic attack or single target skills, increases Confectance Index by 1 point",
        "icon": "assets/Nikketa/Fixed Key 1 - Righteous Doll.png"
      },
      {
        "node": "Fixed Key 2 - Messenger of Justice",
        "level": "20",
        "keyName": "Fixed Key 2 - Messenger of Justice",
        "description": "If the target has Guilt, deals an additional 2 points of Stability damage to it",
        "icon": "assets/Nikketa/Fixed Key 2 - Messenger of Justice.png"
      },
      {
        "node": "Fixed Key 3 - Valiant Aura",
        "level": "30",
        "keyName": "Judgement Strike",
        "description": "This skill now deals AoE Hydro damage equivalent to 80% ATK to all enemies within a 2 tiles radius",
        "icon": "assets/Nikketa/Judgement Strike.png"
      },
      {
        "node": "Fixed Key 4 - Just Desserts",
        "level": "30",
        "keyName": "K9 Deployment",
        "description": "After skill usage, generates Tideaway in the effective area for 2 turns",
        "icon": "assets/Nikketa/K9 Deployment.png"
      },
      {
        "node": "Fixed Key 5 - Stern Gaze",
        "level": "40",
        "keyName": "Fixed Key 5 - Stern Gaze",
        "description": "After attacking, if the target is in Stability Break, applies Fear for 1 turn",
        "icon": "assets/Nikketa/Fixed Key 5 - Stern Gaze.png"
      },
      {
        "node": "Fixed Key 6 - Oppressive Air",
        "level": "40",
        "keyName": "Fixed Key 6 - Oppressive Air",
        "description": "When gaining Clue, gains Attack Up II for 1 turn",
        "icon": "assets/Nikketa/Fixed Key 6 - Oppressive Air.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Nikketa/Affinity Key.png"
      },
      {
        "node": "Common Key - Defender",
        "level": "40",
        "keyName": "Common Key - Defender",
        "description": "ATK +5.0% / If the holder has Hydro type buffs, increases critical rate by 10%",
        "icon": "assets/Nikketa/Common Key - Defender.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "After ending an action, gains 1 stack of Righteousness.\nEach time Kulich performs 1 Counterattack, restores 1 point of Confectance Index for Nikita. The range of Kulich's Loyalty increases by 2 tiles.\n\nRighteousness: Increases own Critical Rate by 30% and Critical Damage by 30% (this effect is fixed and does not affected by stacks). When actively using the Ultimate Skill Righteous Judgment, consumes 5 stacks of this effect to cast the Ultimate Skill an additional time. Can stack up to 5 times. Cannot be dispelled.",
        "icon": "assets/Nikketa/Expansion Key.png"
      }
    ]
  },
  "Leva": {
    "class": "Sentinel",
    "stats": {
      "hp": 1893,
      "atk": 836,
      "def": 504
    },
    "stabilityGauge": 9,
    "movementSpeed": 7,
    "skillAttributes": [
      "Light Ammo",
      "Electric"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Dangerous Smile",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Leva/Dangerous Smile.png"
      },
      {
        "name": "Rational Suppression",
        "traits": [
          "Active",
          "AoE",
          "Tile"
        ],
        "attribute": "Electric",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction, dealing AoE Electric damage equivalent to 120% ATK to all targets within a 7x3 area in the selected direction, applies Negative Charge for 2 turns, and generates Voltage tiles that lasts for 3 turns",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Applies Paralysis to all targets within range for 2 turns. Increases CRIT DMG of this skill by 25%"
          }
        ],
        "icon": "assets/Leva/Rational Suppression.png"
      },
      {
        "name": "Ordered Disruption",
        "traits": [
          "Active",
          "AoE"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 1,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "3",
        "description": "Selects a tile within a 7 tile radius and deals AoE Electric damage equivalent to 100% ATK to all targets within a 3 tile radius of the selected tile. Increases damage dealt by 30% and Stability damage dealt by 1 point against targets with Negative Charge",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases damage multiplier to 130%. At the end of the action, gains 1 stack of Superconductive Code"
          }
        ],
        "icon": "assets/Leva/Ordered Disruption.png"
      },
      {
        "name": "Quantum Calculation",
        "traits": [
          "Ultimate",
          "AoE",
          "Tile",
          "Buff"
        ],
        "attribute": "Electric",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "7",
        "description": "Deals AoE Electric damage equivalent to 60% ATK to all targets within a 7 tile radius and generates Voltage tiles that lasts for 3 turns. Leva gains Overclock Strike for 3 turns. After attacking, Superconductive Strike can be used once",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Superconductive Strike ignores 15% of the target's DEF, and gains 1 stack of Superconductive Code after skill usage. Damage multiplier and Stability damage dealt is increased as follows:\n\n1 stack - 75% ATK + 1 Stability damage\n2 stacks - 90% ATK + 2 Stability damage\n3 stacks - 120% ATK + 4 Stability damage\n4 stacks - 180% ATK + 8 Stability damage"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases damage multiplier to 90%, and cleanses all debuffs on self before attacking. Increases damage multiplier for Overclock Strike to (Additional Stability damage x 8% ATK)"
          }
        ],
        "icon": "assets/Leva/Quantum Calculation.png"
      },
      {
        "name": "Fox's Scheme",
        "traits": [
          "Passive",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the round or when triggering Tile Reaction for Voltage tiles, gains 1 stack of Superconductive Code. If Leva has Positive Charge, increases Electric damage dealt by 10%. If an enemy within Attack Range is applied with Negative Charge, performs one instance of Emergency Support, dealing melee Electric damage equivalent to 60% ATK and 1 Stability damage, and increases Confectance Index by 1 point. This effect can be triggered up to twice per round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the maximum number of instances of Emergency Support by 1. If an enemy with Negative Charge within Attack Range dies, gains 1 stack of Superconductive Code. If Leva has Positive Charge, increases Electric damage dealt by 25% instead"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "After using Rational Suppression or Ordered Disruption, Superconductive Strike can be used once\n\nAt the start of the turn, gains an additional stack of Superconductive Code. In a battle, when Leva gains 4 stacks of Superconductive Code, increases ATK by 15%"
          }
        ],
        "icon": "assets/Leva/Fox's Scheme.png"
      },
      {
        "name": "Superconductive Strike",
        "traits": [
          "Active",
          "Melee",
          "Tile"
        ],
        "attribute": "Melee",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy within a 7 tile radius, generates Voltage tiles within a 1 tile radius of the selected enemy for 3 turns, then deals melee Electric damage equivalent to 50% ATK to it\n\nConsumes all stacks of Superconductive Code. Damage multiplier and Stability damage dealt is as follows:\n\n1 stack - 60% ATK + 1 Stability damage\n2 stacks - 70% ATK + 2 Stability damage\n3 stacks - 85% ATK + 3 Stability damage\n4 stacks - 120% ATK + 6 Stability damage",
        "upgrades": [],
        "icon": "assets/Leva/Superconductive Strike.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Fox's Scheme",
        "level": "2",
        "effect": "Increases the maximum number of instances of Emergency Support by 1. If an enemy with Negative Charge within Attack Range dies, gains 1 stack of Superconductive Code. If Leva has Positive Charge, increases Electric damage dealt by 25% instead"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Ordered Disruption",
        "level": "2",
        "effect": "Increases damage multiplier to 130%. At the end of the action, gains 1 stack of Superconductive Code"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Quantum Calculation",
        "level": "2",
        "effect": "Superconductive Strike ignores 15% of the target's DEF, and gains 1 stack of Superconductive Code after skill usage. Damage multiplier and Stability damage dealt is increased as follows:\n\n1 stack - 75% ATK + 1 Stability damage\n2 stacks - 90% ATK + 2 Stability damage\n3 stacks - 120% ATK + 4 Stability damage\n4 stacks - 180% ATK + 8 Stability damage"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Rational Suppression",
        "level": "2",
        "effect": "Applies Paralysis to all targets within range for 2 turns. Increases CRIT DMG of this skill by 25%"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Quantum Calculation",
        "level": "3",
        "effect": "Increases damage multiplier to 90%, and cleanses all debuffs on self before attacking. Increases damage multiplier for Overclock Strike to (Additional Stability damage x 8% ATK)"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Fox's Scheme",
        "level": "3",
        "effect": "After using Rational Suppression or Ordered Disruption, Superconductive Strike can be used once\n\nAt the start of the turn, gains an additional stack of Superconductive Code. In a battle, when Leva gains 4 stacks of Superconductive Code, increases ATK by 15%"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Mature Aplomb",
        "level": "20",
        "keyName": "Fixed Key 1 - Mature Aplomb",
        "description": "At the start of the battle, gains 2 stacks of Superconductive Code and 1 Confectance Index",
        "icon": "assets/Leva/Fixed Key 1 - Mature Aplomb.png"
      },
      {
        "node": "Fixed Key 2 - Fox's Smile",
        "level": "20",
        "keyName": "Fixed Key 2 - Fox's Smile",
        "description": "Increases damage dealt towards enemies in Stability Break by 7%",
        "icon": "assets/Leva/Fixed Key 2 - Fox's Smile.png"
      },
      {
        "node": "Fixed Key 3 - Play It By Ear",
        "level": "30",
        "keyName": "Fixed Key 3 - Play It By Ear",
        "description": "Before performing Emergency Support, dispels 1 buff from the target",
        "icon": "assets/Leva/Fixed Key 3 - Play It By Ear.png"
      },
      {
        "node": "Fixed Key 4 - Concealment Plan",
        "level": "30",
        "keyName": "Fixed Key 4 - Concealment Plan",
        "description": "After using Superconductive Strike, gains Concealed for 1 turn",
        "icon": "assets/Leva/Fixed Key 4 - Concealment Plan.png"
      },
      {
        "node": "Fixed Key 5 - Rational Reaction",
        "level": "40",
        "keyName": "Fixed Key 5 - Rational Reaction",
        "description": "Before allies performs an active attack, applies Negative Charge to the enemy within range for 1 turn",
        "icon": "assets/Leva/Fixed Key 5 - Rational Reaction.png"
      },
      {
        "node": "Fixed Key 6 - Always Prepared",
        "level": "40",
        "keyName": "Fixed Key 6 - Always Prepared",
        "description": "At the start of the battle, gains Overclock Strike for 3 turns",
        "icon": "assets/Leva/Fixed Key 6 - Always Prepared.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Leva/Affinity Key.png"
      },
      {
        "node": "Common Key - Elite Agent",
        "level": "40",
        "keyName": "Common Key - Elite Agent",
        "description": "ATK +5.0% / Increases damage dealt towards enemies with Electric type debuffs by 7%",
        "icon": "assets/Leva/Common Key - Elite Agent.png"
      },
      {
        "node": "Expansion Key - Electric Espionage",
        "level": "60",
        "keyName": "Expansion Key - Electric Espionage",
        "description": "Support attacks and Superconductive Strike's range is increased to 9 tiles. Number of support attacks is increased by 1. Critical damage dealt is increased against enemies afflicted with Negative Charge by 7%. Critical damage dealt is further increased by 7% if target is in Stability Break. At the start of combat, with every Electric-element allies there are on the field Leva's Electric damage is increased by 2% and stability damage dealt is increased by 1.",
        "icon": "assets/Leva/Expansion Key - Electric Espionage.png"
      }
    ]
  },
  "Robella": {
    "class": "Sentinel",
    "stats": {
      "hp": 1819,
      "atk": 844,
      "def": 504
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Light Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Ultra Shot",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Extra Attention",
            "effect": "Ultra Shot: After skill usage, gains 2 stacks of Sense Weakness"
          }
        ],
        "icon": "assets/Robella/Ultra Shot.png"
      },
      {
        "name": "Light of Bond",
        "traits": [
          "Active"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an ally (excluding self) within a 8 tile radius and applies Unity on it. Only 1 Unity can exist at the same time. After skill usage, Robella gains Extra Command. This skill can only be used once per round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases ATK by 20% of the selected ally's initial ATK for self"
          }
        ],
        "icon": "assets/Robella/Light of Bond.png"
      },
      {
        "name": "Radiant Memory",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Robella gains Radiant Rise for 2 rounds (Duration decreases at the end of the current round). After skill usage, Robella gains Frost Barrier for 2 turns, Frost Barrier absorbs damage equal to 65% of Robella's initial attack, up to a maximum of 60% of the target's max HP",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Radiant Rise increases damage dealt by 50% instead\n\nEnhances the effects of Radiant Rise - when using Frigid Infiltration, applies 1 stack of Memory Shock on the target for 2 turns"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases duration of Radiant Rise by 2 rounds (Duration decreases at the end of the current round)"
          }
        ],
        "icon": "assets/Robella/Radiant Memory.png"
      },
      {
        "name": "Howling Cyclone",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Freeze",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction around self, and deals AoE Freeze damage equal to 120% of attack to all enemy targets in a 4 tile fan-shaped area",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier to 150% ATK. For each stack of Sense Weakness, increases damage multiplier by 9%"
          }
        ],
        "icon": "assets/Robella/Howling Cyclone.png"
      },
      {
        "name": "Critical Insight",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the action, increases Confectance Index by 1 point\n\nAfter using Frigid Infiltration, consumes all Inspection stacks from the target, and gains an equal number of stacks of Sense Weakness. When the number of stacks of Sense Weakness is more than 2, basic attacks deal Freeze damage instead, and increases CRIT rate by 20%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "When the number of stacks of Sense Weakness is more than 5, increases CRIT DMG by 30%, and increases damage dealt by Frigid Infiltration by 30%"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Sense Weakness no longer has a stack limit"
          }
        ],
        "icon": "assets/Robella/Critical Insight.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Light of Bond",
        "level": "2",
        "effect": "Increases ATK by 20% of the selected ally's initial ATK for self"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Radiant Memory",
        "level": "2",
        "effect": "Radiant Rise increases damage dealt by 50% instead\n\nEnhances the effects of Radiant Rise - when using Frigid Infiltration, applies 1 stack of Memory Shock on the target for 2 turns"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Critical Insight",
        "level": "2",
        "effect": "When the number of stacks of Sense Weakness is more than 5, increases CRIT DMG by 30%, and increases damage dealt by Frigid Infiltration by 30%"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Howling Cyclone",
        "level": "2",
        "effect": "Increases damage multiplier to 150% ATK. For each stack of Sense Weakness, increases damage multiplier by 9%"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Radiant Memory",
        "level": "3",
        "effect": "Increases duration of Radiant Rise by 2 rounds (Duration decreases at the end of the current round)"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Critical Insight",
        "level": "3",
        "effect": "Sense Weakness no longer has a stack limit"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Guard Vent",
        "level": "20",
        "keyName": "Fixed Key 1 - Guard Vent",
        "description": "Before allies with Unity launches an active attack or Interception, applies Defense Down II on the target for 2 turns",
        "icon": "assets/Robella/Fixed Key 1 - Guard Vent.png"
      },
      {
        "node": "Fixed Key 2 - Third-gen Neural Cloud",
        "level": "20",
        "keyName": "Fixed Key 2 - Third-gen Neural Cloud",
        "description": "At the end of the action, if Robella has Radiant Rise, gains Attack Up II for 1 turn",
        "icon": "assets/Robella/Fixed Key 2 - Third-gen Neural Cloud.png"
      },
      {
        "node": "Fixed Key 3 - Extra Attention",
        "level": "30",
        "keyName": "Ultra Shot",
        "description": "After skill usage, gains 2 stacks of Sense Weakness",
        "icon": "assets/Robella/Ultra Shot.png"
      },
      {
        "node": "Fixed Key 4 - Less Than A Dinergate",
        "level": "30",
        "keyName": "Fixed Key 4 - Less Than A Dinergate",
        "description": "If Robella or allies with Unity deals Freeze damage towards enemies with Shield, increases Shield Pierce Rate by 30% and damage by 20%",
        "icon": "assets/Robella/Fixed Key 4 - Less Than A Dinergate.png"
      },
      {
        "node": "Fixed Key 5 - Cool Protection",
        "level": "40",
        "keyName": "Fixed Key 5 - Cool Protection",
        "description": "If Robella is on an allied Frost tile, gains 5 tiles of Additional Movement after using Ultra Shot or Howling Cyclone",
        "icon": "assets/Robella/Fixed Key 5 - Cool Protection.png"
      },
      {
        "node": "Fixed Key 6 - Inner Calm",
        "level": "40",
        "keyName": "Fixed Key 6 - Inner Calm",
        "description": "Before using Frigid Infiltration, dispels 2 buffs from the target",
        "icon": "assets/Robella/Fixed Key 6 - Inner Calm.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Robella/Affinity Key.png"
      },
      {
        "node": "Common Key - Justice is My Strenght",
        "level": "40",
        "keyName": "Common Key - Justice is My Strenght",
        "description": "ATK +5% / If the holder has Shield, increases Phase damage dealt by 10%",
        "icon": "assets/Robella/Common Key - Justice is My Strenght.png"
      },
      {
        "node": "Expansion Key - Justice execution calculation",
        "level": "60",
        "keyName": "Expansion Key - Justice execution calculation",
        "description": "If posessing Radiant Rise, using basic attack Super Shot grants Extra command. Can be triggered up to 1 time per round.\nWhen using active skill Radiant Memory or when enemy unit with Inspection is eliminated by an allied unit, gains 3 stacks of Sense Weakness.\nBefore using an active attack generate Frost tiles within 2 tile radius around self for 2 turns.",
        "icon": "assets/Robella/Expansion Key - Justice execution calculation.png"
      }
    ]
  },
  "Lainie": {
    "class": "Sentinel",
    "stats": {
      "hp": 1859,
      "atk": 844,
      "def": 494
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Light Ammo"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Victory Protocol",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it\n\nIf Simulacrum is present, it will use Perplexed Reflex on the selected target after skill usage",
        "upgrades": [],
        "icon": "assets/Lainie/Victory Protocol.png"
      },
      {
        "name": "Combat Algorithm",
        "traits": [
          "Skill",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 140% ATK to it. This skill cannot be used after skill usage, lasting till the end of the next allied round\n\nIf Simulacrum is present, it will use Offense Simulation centered on itself after skill usage. If Offense Simulation did not hit any targets that were hit by Combat Algorithm, it ignores 30% of the target's DEF",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases DEF ignored to 50%, and increases CRIT DMG dealt towards enemies whose DEF is lower or equal to 0 by 10%. Before attacking, applies 1 stack of Parapluie's Penetration on the target"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases damage multiplier to 160% ATK, increases the minimum damage multiplier of Offense Simulation to 100%, and removes the restriction of being unable to use the skill after skill usage"
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5",
            "effect": "When Lainie uses Combat Algorithm or Simulacrum uses Offense Simulation, if the target's DEF is lower or equal to 0, dispels 1 random buff"
          }
        ],
        "icon": "assets/Lainie/Combat Algorithm.png"
      },
      {
        "name": "Computational Crush",
        "traits": [
          "Skill",
          "AoE"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "3",
        "description": "Selects a tile within a 7 tile radius and deals AoE Physical damage equivalent to 120% ATK to all enemies within a 3 tile radius of the selected tile. This skill cannot be used after skill usage, lasting till the end of the next allied round\n\nIf Simulacrum is present, it will use Hashrate Overclock centered on itself after skill usage, and applies Movement Down I for 2 turns",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2",
            "effect": "After Lainie uses Computational Crush or Simulacrum uses Hashrate Overclock, the other half's action knocks the target back by 2 tiles"
          }
        ],
        "icon": "assets/Lainie/Computational Crush.png"
      },
      {
        "name": "Simulated Partner",
        "traits": [
          "Ultimate",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an empty tile within a 7 tile radius and summons 1 Simulacrum. Applies Bonded Possibility on self and Simulacrum for 1 round (Duration decreases at the end of the current round)\n\nAt the end of the round, decreases Confectance Index by 3 points. If there is insufficient Confectance Index, the Simulacrum disappears. This skill cannot be used when Simulacrum is present",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Decreases cooldown by 1 turn and Confectance Index consumption by Simulacrum by 1 point\n\nIncreases the maximum stack of Parapluie's Penetration to 6. Applies 2 stacks of Parapluie's Penetration on all targets within a 3 tile radius of the selected tile, and increases Confectance Index by 3 points"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "When Lainie or Simulacrum deals damage to enemies whose DEF is lower or equal to 0, the other half gains Power of Bonds\n\nEnhances the effects of Bonded Possibility - Increases Stability damage dealt by 6 points"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4",
            "effect": "Simulated Partner: When Simulacrum disappears, resets the cooldown of this skill. This can be triggered once per battle"
          }
        ],
        "icon": "assets/Lainie/Simulated Partner.png"
      },
      {
        "name": "Precognition Foresight",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "For each 12 points of initial max HP, increases CRIT by 0.1%, up to a maximum of 30%. Applies Precognition Foresight to all enemies within a 7 tile radius\n\nBefore using an active attack, applies 1 stack of Parapluie's Penetration on the target, and increases Confectance Index by 2 points after the attack. If the target's DEF is lower or equal to 0, increases damage multiplier equivalent to 10% of initial max HP, and additionally increases Confectance Index by 1 point. After using an active attack, no active attacks can be used on the same allied round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - for each 6 points of initial max HP, increases CRIT by 0.1%, up to a maximum of 60%. When attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 20% of initial max HP\n\nPrecognition Foresight and Precognition Awareness lowers DEF by 20% instead"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - when attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 30% of initial max HP\n\nWhen Simulacrum is present, if Lainie receives fatal damage, restores HP equivalent to 100% max HP. This effect can be triggered once per battle. Simulacrum disappears after effect is triggered"
          }
        ],
        "icon": "assets/Lainie/Precognition Foresight.png"
      },
      {
        "name": "Perplexed Reflex",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it\n\nAfter skill usage, Lainie will use Victory Protocol on the selected target",
        "upgrades": [],
        "icon": "assets/Lainie/Perplexed Reflex.png"
      },
      {
        "name": "Offense Simulation",
        "traits": [
          "Skill",
          "AoE"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "3",
        "description": "Selects an enemy target within a 7 tile radius and deals AoE Physical damage equivalent to 140% ATK to all enemies within a 3 tile radius of the enemy. For each additional target hit, decreases damage multiplier by 20%, down to a minimum of 80%. This skill cannot be used after skill usage, lasting till the end of the next allied round\n\nIf this skill hits enemies whose DEF is lower or equal to 0, Combat Algorithm will ignore 30% of the target's DEF. After skill usage, Lainie will use Combat Algorithm on the selected target",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases DEF ignored to 50%, and increases CRIT DMG dealt towards enemies whose DEF is lower or equal to 0 by 10%. Before attacking, applies 1 stack of Parapluie's Penetration on the target"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases damage multiplier to 160% ATK, increases the minimum damage multiplier of Offense Simulation to 100%, and removes the restriction of being unable to use the skill after skill usage"
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5",
            "effect": "When Lainie uses Combat Algorithm or Simulacrum uses Offense Simulation, if the target's DEF is lower or equal to 0, dispels 1 random buff"
          }
        ],
        "icon": "assets/Lainie/Offense Simulation.png"
      },
      {
        "name": "Hashrate Overclock",
        "traits": [
          "Skill",
          "AoE"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "3",
        "description": "Selects an empty tile within a 7 tile radius and deals AoE Physical damage equivalent to 120% ATK to all enemies within a 3 tile radius of the selected tile. This skill cannot be used after skill usage, lasting till the end of the next allied round\n\nIf this skill hit 2 or fewer enemies, increases Stability damage dealt by Computational Crush by 5 points. After skill usage, Lainie will use Computational Crush on the selected tile",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2",
            "effect": "After Lainie uses Computational Crush or Simulacrum uses Hashrate Overclock, the other half's action knocks the target back by 2 tiles"
          }
        ],
        "icon": "assets/Lainie/Hashrate Overclock.png"
      },
      {
        "name": "Queenside Castle",
        "traits": [
          "Skill"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Entire Map",
        "description": "Swaps position with Lainie and gains Extra Command for self",
        "upgrades": [],
        "icon": "assets/Lainie/Queenside Castle.png"
      },
      {
        "name": "Precognition Awareness",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "For each 12 points of initial max HP, increases CRIT by 0.1%, up to a maximum of 30%. Applies Precognition Awareness to all enemies within a 7 tile radius\n\nBefore using an active attack, applies 1 stack of Parapluie's Penetration on the target. If the target's DEF is lower or equal to 0, increases damage multiplier equivalent to 10% of initial max HP. After using an active attack, no active attacks can be used on the same allied round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - for each 6 points of initial max HP, increases CRIT by 0.1%, up to a maximum of 60%. When attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 20% of initial max HP\n\nPrecognition Foresight and Precognition Awareness lowers DEF by 20% instead"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - when attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 30% of initial max HP\n\nWhen Simulacrum is present, if Lainie receives fatal damage, restores HP equivalent to 100% max HP. This effect can be triggered once per battle. Simulacrum disappears after effect is triggered"
          }
        ],
        "icon": "assets/Lainie/Precognition Awareness.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Simulated Partner",
        "level": "2",
        "effect": "Decreases cooldown by 1 turn and Confectance Index consumption by Simulacrum by 1 point\n\nIncreases the maximum stack of Parapluie's Penetration to 6. Applies 2 stacks of Parapluie's Penetration on all targets within a 3 tile radius of the selected tile, and increases Confectance Index by 3 points"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Combat Algorithm",
        "level": "2",
        "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases DEF ignored to 50%, and increases CRIT DMG dealt towards enemies whose DEF is lower or equal to 0 by 10%. Before attacking, applies 1 stack of Parapluie's Penetration on the target"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Precognition Foresight",
        "level": "2",
        "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - for each 6 points of initial max HP, increases CRIT by 0.1%, up to a maximum of 60%. When attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 20% of initial max HP\n\nPrecognition Foresight and Precognition Awareness lowers DEF by 20% instead"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Simulated Partner",
        "level": "3",
        "effect": "When Lainie or Simulacrum deals damage to enemies whose DEF is lower or equal to 0, the other half gains Power of Bonds\n\nEnhances the effects of Bonded Possibility - Increases Stability damage dealt by 6 points"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Precognition Foresight",
        "level": "3",
        "effect": "Enhances the effects of Precognition Foresight and Precognition Awareness - when attacking enemies whose DEF is lower or equal to 0, increases damage multiplier equivalent to 30% of initial max HP\n\nWhen Simulacrum is present, if Lainie receives fatal damage, restores HP equivalent to 100% max HP. This effect can be triggered once per battle. Simulacrum disappears after effect is triggered"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Combat Algorithm",
        "level": "3",
        "effect": "Enhances the effects of Combat Algorithm and Offense Simulation - increases damage multiplier to 160% ATK, increases the minimum damage multiplier of Offense Simulation to 100%, and removes the restriction of being unable to use the skill after skill usage"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Neural Bonds",
        "level": "20",
        "keyName": "Fixed Key 1 - Neural Bonds",
        "description": "When Lainie or Simulacrum receives healing, restores HP equivalent to 20% max HP for the other half. This effect cannot be repeatedly triggered",
        "icon": "assets/Lainie/Fixed Key 1 - Neural Bonds.png"
      },
      {
        "node": "Fixed Key 2 - Bad Things, Go Away!",
        "level": "20",
        "keyName": "Fixed Key 2 - Bad Things, Go Away!",
        "description": "After Lainie uses Computational Crush or Simulacrum uses Hashrate Overclock, the other half's action knocks the target back by 2 tiles",
        "icon": "assets/Lainie/Fixed Key 2 - Bad Things, Go Away!.png"
      },
      {
        "node": "Fixed Key 3 - Parapluie's Protection",
        "level": "30",
        "keyName": "Fixed Key 3 - Parapluie's Protection",
        "description": "At the end of the action, if the distance between Lainie and Simulacrum is larger or equal to 3 tiles, both gains AoE Defense II for 1 turn",
        "icon": "assets/Lainie/Fixed Key 3 - Parapluie's Protection.png"
      },
      {
        "node": "Fixed Key 4 - Friend's Return",
        "level": "30",
        "keyName": "Simulated Partner",
        "description": "When Simulacrum disappears, resets the cooldown of this skill. This can be triggered once per battle",
        "icon": "assets/Lainie/Simulated Partner.png"
      },
      {
        "node": "Fixed Key 5 - Sunlight's Warmth",
        "level": "40",
        "keyName": "Fixed Key 5 - Sunlight's Warmth",
        "description": "When Lainie uses Combat Algorithm or Simulacrum uses Offense Simulation, if the target's DEF is lower or equal to 0, dispels 1 random buff",
        "icon": "assets/Lainie/Fixed Key 5 - Sunlight's Warmth.png"
      },
      {
        "node": "Fixed Key 6 - OGAS' Might",
        "level": "40",
        "keyName": "Fixed Key 6 - OGAS' Might",
        "description": "Increases CRIT DMG dealt towards enemies whose DEF is lower or equal to 0 by 5%",
        "icon": "assets/Lainie/Fixed Key 6 - OGAS' Might.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Lainie/Affinity Key.png"
      },
      {
        "node": "Common Key - Complete Liberation",
        "level": "40",
        "keyName": "Common Key - Complete Liberation",
        "description": "ATK +5% / Increases damage dealt towards enemies whose DEF is lower or equal to 0 by 10%",
        "icon": "assets/Lainie/Common Key - Complete Liberation.png"
      },
      {
        "node": "Expansion Key - Algorithmic Stack",
        "level": "60",
        "keyName": "The effect of Parapluie's Penetration is improved",
        "description": "DEF reduced by an additional 6% per stack.\nWhen Lainie uses her skills Combat Algorithm, Computational Crush, or Simulated Partner, or when Lainie’s Simulacrum uses Offensive Simulation, Hashrate Overclock, or Queenside Castle, for every point of Confectance Index Lainie has the critical damage of Lainie and her Simulacrum is increased by 15%.\nWhile the Simulacrum is alive on the battlefield, Lainie and the Simulacrum have their mobility increased by two tiles of movement.",
        "icon": "assets/Lainie/The effect of Parapluie's Penetration is improved.png"
      }
    ]
  },
  "Florence": {
    "class": "Support",
    "stats": {
      "hp": 2013,
      "atk": 696,
      "def": 553
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Forced Injection",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Florence/Forced Injection.png"
      },
      {
        "name": "Special Care",
        "traits": [
          "Skill",
          "Healing"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "2",
        "description": "Selects a tile within a 6 tile radius, cleanses 2 debuffs for all allies within a 2 tile radius of the selected tile and restores HP equivalent to 120% ATK",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Sweet Temptation",
            "effect": "Special Care: This skill will no longer restore HP and cleanse debuffs, but instead deals AoE Physical damage equivalent to 30% ATK to all units (excluding self) within range"
          }
        ],
        "icon": "assets/Florence/Special Care.png"
      },
      {
        "name": "Pleasure Trigger",
        "traits": [
          "Skill",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an ally within a 6 tile radius, cleanses Fear and Taunt from it, applies Stimulant for 1 round (Duration decreases at the end of the current round) and consumes HP equivalent to 20% initial HP",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases the duration of Stimulant by 1 round (Duration decreases at the end of the current round)\n\nNew effect is added - At the end of the action, if HP is below 30%, restores HP equivalent to 100% of Florence's ATK. This effect can only activate once during the duration of Stimulant"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Additionally cleanses Infatuated and Stun. This skill is also applied to Arios"
          }
        ],
        "icon": "assets/Florence/Pleasure Trigger.png"
      },
      {
        "name": "Masochistic Hallucination",
        "traits": [
          "Ultimate",
          "AoE",
          "Summon",
          "Control"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Selects a direction, applies Chaos Compound for 2 turns and Infatuated for 1 turn for all enemies within a 3x5 area of the selected direction, and deals AoE Hydro damage equivalent to 80% ATK. After skill usage, increases Confectance Index by 6 points, and teleports Arios near self\n\nIf Arios is not on the field, summons Arios after skill usage",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Enhances the effects of Chaos Compound: Increases Hydro damage received by 15%\n\nNew effect is added - Physical damage is dealt to all units at the start of the round"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier by 20%. If Arios is present, restores HP equivalent to 100% ATK for Florence and applies Adrenaline for 1 round (Duration decreases at the end of the current round)"
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Bondage Urge",
            "effect": "Masochistic Hallucination: This skill will pull all targets towards self by 3 tiles"
          },
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Decreases Confectance Index consumption by 1 point\n\nIncreases the number of Counterattack performed by Arios by 2 times"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Arios receives 30% less damage\n\nEnhances the effects of Tremor of Despair: Increases ATK by 35%, doubles the damage multiplier of Counterattack, and restores HP equivalent to 30% of damage dealt after dealing damage"
          }
        ],
        "icon": "assets/Florence/Masochistic Hallucination.png"
      },
      {
        "name": "Precision Anesthesia",
        "traits": [
          "Skill",
          "Targeted",
          "Control",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Applies Chaos Compound on the enemy closest to Florence for 2 turns, deals Hydro damage equivalent to 80% ATK, and applies Taunt for 1 turn",
        "upgrades": [],
        "icon": "assets/Florence/Precision Anesthesia.png"
      },
      {
        "name": "No. 1 Assistant",
        "traits": [
          "Passive",
          "Counter"
        ],
        "attribute": null,
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Entire Map",
        "effArea": "Target",
        "description": "When Florence takes damage, Arios will take all damage on behalf of her\n\nIf the distance between Arios and Florence is 6 or more tiles, Arios will be teleported to near Florence\n\nWhen Arios or Florence receives damage, performs Counterattack, dealing Hydro damage equivalent to 80% ATK. This can be activated twice per round\n\nFor each damage instance received, gains 1 stack of Mark of Shame. When the number of stacks of Mark of Shame reaches 5, it is converted into Tremor of Despair",
        "upgrades": [],
        "icon": "assets/Florence/No. 1 Assistant.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Pre-Op Preparation",
        "level": "2",
        "effect": "Decreases Confectance Index consumption by 1 point\n\nIncreases the number of Counterattack through passive skill No. 1 Assistant performed by Arios by 2 times"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Masochistic Hallucination",
        "level": "2",
        "effect": "Enhances the effects of Chaos Compound: Increases Hydro damage received by 15%\n\nNew effect is added - Physical damage is dealt to all units at the start of the round"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Pleasure Trigger",
        "level": "2",
        "effect": "Increases the duration of Stimulant by 1 round (Duration decreases at the end of the current round)\n\nNew effect is added - At the end of the action, if HP is below 30%, restores HP equivalent to 100% of Florence's ATK. This effect can only activate once during the duration of Stimulant"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Masochistic Hallucination",
        "level": "3",
        "effect": "Increases damage multiplier by 20%. If Arios is present, restores HP equivalent to 100% ATK for Florence and applies Adrenaline for 1 round (Duration decreases at the end of the current round)"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Pleasure Trigger",
        "level": "3",
        "effect": "Additionally cleanses Infatuated and Stun. This skill is also applied to Arios"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Pre-Op Preparation",
        "level": "3",
        "effect": "Arios receives 30% less damage\n\nEnhances the effects of Tremor of Despair: Increases ATK by 35%, doubles the damage multiplier of Counterattack, and restores HP equivalent to 30% of damage dealt after dealing damage"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Fatal thrill",
        "level": "20",
        "keyName": "Fixed Key 1 - Fatal thrill",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Florence/Fixed Key 1 - Fatal thrill.png"
      },
      {
        "node": "Fixed Key 2 - Self-pleasure",
        "level": "20",
        "keyName": "Fixed Key 2 - Self-pleasure",
        "description": "After using active skills, restores HP equivalent to 80% ATK for self and Arios",
        "icon": "assets/Florence/Fixed Key 2 - Self-pleasure.png"
      },
      {
        "node": "Fixed Key 3 - Sensitivity Boost",
        "level": "30",
        "keyName": "Fixed Key 3 - Sensitivity Boost",
        "description": "After Florence or Arios attacks, applies Defense Down II on the enemy for 2 turns",
        "icon": "assets/Florence/Fixed Key 3 - Sensitivity Boost.png"
      },
      {
        "node": "Fixed Key 4 - Riposte's Reward",
        "level": "30",
        "keyName": "Fixed Key 4 - Riposte's Reward",
        "description": "After Arios performs a Counterattack, it gains Attack Up II for 1 turn",
        "icon": "assets/Florence/Fixed Key 4 - Riposte's Reward.png"
      },
      {
        "node": "Fixed Key 5 - Bondage Urge",
        "level": "40",
        "keyName": "Masochistic Hallucination",
        "description": "This skill will pull all targets towards self by 3 tiles",
        "icon": "assets/Florence/Masochistic Hallucination.png"
      },
      {
        "node": "Fixed Key 6 - Sweet Temptation",
        "level": "40",
        "keyName": "Special Care",
        "description": "This skill will no longer restore HP and cleanse debuffs, but instead deals AoE Physical damage equivalent to 30% ATK to all units (excluding self) within range",
        "icon": "assets/Florence/Special Care.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Florence/Affinity Key.png"
      },
      {
        "node": "Common Key - Master's Command",
        "level": "40",
        "keyName": "Common Key - Master's Command",
        "description": "HP +5% / Increases ATK by 7% dealt by the holder's Entity Summon",
        "icon": "assets/Florence/Common Key - Master's Command.png"
      },
      {
        "node": "Expansion Key - Thrill Seeker",
        "level": "60",
        "keyName": "Expansion Key - Thrill Seeker",
        "description": "After Florence uses the active skill Pleasure Trigger, applies Pleasure Trigger to all ally Entity Summons as well.\nWhen an ally unit gains Stimulant, Arios gains 1 stack of Euphoric Frenzy for 3 turn, this effect has a maximum of 6 stacks. \nAfter an ally unit with Stimulant receives healing, applies Soak I for 2 turn. \n \nEuphoric Frenzy: For every 1 stack of this effect, the damage caused by Arios' active skill Precision Anesthesia is increased by 10%; when 6 stacks of this effect are collected, owner's critical damage is increased by 20% and the ATK buffed by Tremor of Despair is increased to 2.5 times of the original effect.",
        "icon": "assets/Florence/Expansion Key - Thrill Seeker.png"
      }
    ]
  },
  "Lind": {
    "class": "Sentinel",
    "stats": {
      "hp": 1859,
      "atk": 836,
      "def": 519
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Repulsive Shot",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Applies 2 stacks of Alleviation Dependence\n\nIncreases the effect range of the skill from a small fan-shaped area to a fan-shaped area (2x6 tiles expansion to the left and right of the original area)\n\nFor each debuff held by the enemy, increases damage dealt by 10%, up to a maximum of 60%"
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Night owl's Keenness",
            "effect": "Assault Spray/Overwhelming Burst: After skill usage, gains 5 tiles of Additional Movement"
          }
        ],
        "icon": "assets/Lind/Repulsive Shot.png"
      },
      {
        "name": "Overwhelming Burst",
        "traits": [
          "Skill",
          "AoE"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "Self",
        "effArea": "6",
        "description": "Deals AoE Corrosion damage equivalent to 100% ATK to all enemies within a 6 tile radius. Before skill usage, if Confectance Index is at max, for each stack of Candyglaze, increases damage multiplier by 5%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases damage multiplier to 120% ATK and increases Stability damage dealt by 1 point\n\nBefore skill usage, if Confectance Index is at max, increases CRIT DMG by 20%, for each stack of Candyglaze, increases damage multiplier by 10%"
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Night owl's Keenness",
            "effect": "Assault Spray/Overwhelming Burst: After skill usage, gains 5 tiles of Additional Movement"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Civilized Judgement",
            "effect": "Overwhelming Burst: If this skill only hits 1 enemy, increases damage dealt by 30%"
          }
        ],
        "icon": "assets/Lind/Overwhelming Burst.png"
      },
      {
        "name": "Glucose Overload",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "8",
        "description": "Applies Ketoacidemia to all enemies within a 8 tile radius. Upon skill activation, triggers all Corrosion debuffs held by enemy units within effect range. After skill usage, Lind can use Repulsive Shot, Assault Spray, or Overwhelming Burst",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases damage dealt by the next active skill by 15%\n\nEnhances the effects of Ketoacidemia - The holder receives 12% more Corrosion damage from Lind, up to a maximum of 72%"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "After skill usage, increases Confectance Index by 3 points. If Lind has 10 stacks of Candyglaze, reduces the cooldown of this skill by 1 round"
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Withdrawal Reaction",
            "effect": "Glucose Overload: Before skill usage, gains Critical Rate Boost II for 2 turns"
          }
        ],
        "icon": "assets/Lind/Glucose Overload.png"
      },
      {
        "name": "Sweets Stockpile",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the action, increases Confectance Index by 1 point\n\nAt the start of the round, applies Honey Trap to all enemies. This has a cooldown of 1 round\n\nWhen enemies with Honey Trap dies or when allies deal Corrosion damage, Lind gains 1 stack of Candyglaze. When the number of stacks of Candyglaze held by self exceeds 5, before attacking enemies with Honey Trap, triggers the effects of Honey Trap. Afterwards, Honey Trap is consumed",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "At the start of the battle, for each ally present, Lind gains 1 stack of Candyglaze. Increases the maximum stacks of Candyglaze to 30\n\nEnhances the effect of Candyglaze - Increases Corrosion damage dealt by 2%"
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Removes the cooldown for applying Honey Trap at the start of the round\n\nWhen Honey Trap is triggered, increases the number of random powerful debuffs applied by 3, increases damage multiplier to 120% ATK, and increases CRIT DMG by 15%"
          }
        ],
        "icon": "assets/Lind/Sweets Stockpile.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Sweet Stockpile",
        "level": "2",
        "effect": "At the start of the battle, for each ally present, Lind gains 1 stack of Candyglaze. Increases the maximum stacks of Candyglaze to 30\n\nEnhances the effect of Candyglaze - Increases Corrosion damage dealt by 2%"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Glucose Overload",
        "level": "2",
        "effect": "Increases damage dealt by the next active skill by 15%\n\nEnhances the effects of Ketoacidemia - The holder receives 12% more Corrosion damage from Lind, up to a maximum of 72%"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Sweets Stockpile",
        "level": "3",
        "effect": "Removes the cooldown for applying Honey Trap at the start of the round\n\nWhen Honey Trap is triggered, increases the number of random powerful debuffs applied by 3, increases damage multiplier to 120% ATK, and increases CRIT DMG by 15%"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Assault Spray",
        "level": "2",
        "effect": "Applies 2 stacks of Alleviation Dependence\n\nIncreases the effect range of the skill from a small fan-shaped area to a fan-shaped area (2x6 tiles expansion to the left and right of the original area)\n\nFor each debuff held by the enemy, increases damage dealt by 10%, up to a maximum of 60%"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Overwhelming Burst",
        "level": "2",
        "effect": "Increases damage multiplier to 120% ATK and increases Stability damage dealt by 1 point\n\nBefore skill usage, if Confectance Index is at max, increases CRIT DMG by 20%, for each stack of Candyglaze, increases damage multiplier by 10%"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Glucose Overload",
        "level": "3",
        "effect": "After skill usage, increases Confectance Index by 3 points. If Lind has 10 stacks of Candyglaze, reduces the cooldown of this skill by 1 round"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Nociception",
        "level": "20",
        "keyName": "Fixed Key 1 - Nociception",
        "description": "At the start of the round, gains Quick Barrier",
        "icon": "assets/Lind/Fixed Key 1 - Nociception.png"
      },
      {
        "node": "Fixed Key 2 - Night owl's Keenness",
        "level": "20",
        "keyName": "Assault Spray/Overwhelming Burst",
        "description": "After skill usage, gains 5 tiles of Additional Movement",
        "icon": "assets/Lind/Assault Spray/Overwhelming Burst.png"
      },
      {
        "node": "Fixed Key 3 - Radio Invitation",
        "level": "30",
        "keyName": "Fixed Key 3 - Radio Invitation",
        "description": "Selects one ally on the field. The selected ally will be unable to move or use any skill for the entire battle, but decreases DEF for all enemies by 15%. This lasts till the selected ally dies. Lind gains 1 instance of an Extra Action",
        "icon": "assets/Lind/Fixed Key 3 - Radio Invitation.png"
      },
      {
        "node": "Fixed Key 4 - Civilized Judgement",
        "level": "30",
        "keyName": "Overwhelming Burst",
        "description": "If this skill only hits 1 enemy, increases damage dealt by 30%",
        "icon": "assets/Lind/Overwhelming Burst.png"
      },
      {
        "node": "Fixed Key 5 - Dessert Therapy",
        "level": "40",
        "keyName": "Fixed Key 5 - Dessert Therapy",
        "description": "If Lind has Candyglaze, cleanses 1 debuff from self before attacking",
        "icon": "assets/Lind/Fixed Key 5 - Dessert Therapy.png"
      },
      {
        "node": "Fixed Key 6 - Withdrawal Reaction",
        "level": "40",
        "keyName": "Glucose Overload",
        "description": "Before skill usage, gains Critical Rate Boost II for 2 turns",
        "icon": "assets/Lind/Glucose Overload.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Lind/Affinity Key.png"
      },
      {
        "node": "Common Key - Endless Night",
        "level": "40",
        "keyName": "Common Key - Endless Night",
        "description": "ATK +5% / Increases Phase damage dealt towards enemies with debuffs by 10%",
        "icon": "assets/Lind/Common Key - Endless Night.png"
      },
      {
        "node": "Expansion Key - Sugar-Coated Bullet",
        "level": "60",
        "keyName": "Expansion Key - Sugar-Coated Bullet",
        "description": "At the start of the battle, Lind gains 5 stacks of Candyglaze.\r\nWhen the Ultimate skill Glucose Overload's effect is applied to enemy units with Corrosion debuffs, damage taken by said enemy units is increased by 50%.\r\nThe damage multiplier of the active skill Overwhelming Burst is additionally increased by 65% and stability damage is additionally increased by 2 points.\r\nDamage dealt by Honey Trap is increased by 100%, stability damage dealt is increased to 3 points",
        "icon": "assets/Lind/Expansion Key - Sugar-Coated Bullet.png"
      }
    ]
  },
  "Balthilde": {
    "class": "Support",
    "stats": {
      "hp": 2006,
      "atk": 670,
      "def": 569
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Heavy Ammo"
    ],
    "weaknesses": [
      "Light Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Quenching Strike",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Balthilde/Quenching Strike.png"
      },
      {
        "name": "Reinforcement Protocol",
        "traits": [
          "Skill",
          "Summon",
          "Defense"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an empty tile within a 8 tile radius and summons Defense Construct on the selected tile. If Defense Construct is already summoned, it is moved to the selected tile\n\nIf Demolition Protocol hasn't been used on this turn, Balthilde can use Demolition Protocol once\n\nWhen Defense Construct is destroyed, this skill enters into a 3 turn cooldown",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases the range of Safety Consciousness and Focused Maintenance to 5 tiles\n\nNew effect is added for Safety Consciousness - Upon summoned, restores the durability of all Cover within a 5 tile radius\n\nNew effect is added for Focused Maintenance - Restores HP equivalent to 100% DEF and 2 Stability, and applies Defense Up I for all allies within a 5 tile radius at the end of their action"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Decreases the cooldown of this skill by 1 turn. Increases the ATK and DEF inherited by Defense Construct to 100%\n\nEnhances the effects of Safety Consciousness - Upon summoned, restores HP equivalent to 200% DEF and 4 Stability\n\nEnhances the effects of Focused Maintenance - Damage reduction is applied to all allies instead"
          }
        ],
        "icon": "assets/Balthilde/Reinforcement Protocol.png"
      },
      {
        "name": "Demolition Protocol",
        "traits": [
          "Skill",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an empty tile within a 8 tile radius and summons Offense Construct on the selected tile. If Offense Construct is already summoned, it is moved to the selected tile\n\nIf Reinforcement Protocol hasn't been used on this turn, Balthilde can use Reinforcement Protocol once\n\nWhen Offense Construct is destroyed, this skill enters into a 3 turn cooldown",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the range of Disassembly Knack to 5 tiles, and applies Stress Fracture on the target for 2 turns"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Decreases the cooldown of this skill by 1 turn. Increases the ATK and DEF inherited by Offense Construct to 100%\n\nIncreases the number of times Disassembly Knack can be used per turn by 1"
          }
        ],
        "icon": "assets/Balthilde/Demolition Protocol.png"
      },
      {
        "name": "Raging Chainblast",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals AoE Physical damage equivalent to 100% ATK to all enemies in a 6 tile fan shaped area towards the selected direction\n\nDecreases the cooldown of Reinforcement Protocol and Demolition Protocol by 1 turn",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Resets the cooldown of Reinforcement Protocol and Demolition Protocol\n\nRestores HP equivalent to 100% ATK for all allies, and applies Load-Bearing Parts for 2 turns"
          }
        ],
        "icon": "assets/Balthilde/Raging Chainblast.png"
      },
      {
        "name": "Wrench Calibration",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "After performing a basic attack, increases Confectance Index by 1 point. When allies (excluding self) deals Physical damage using an active attack, increases Confectance Index by 1 point for self. This can be triggered up to 2 times per turn.\n\nFor each point of Confectance Index gained, applies 1 stack of Performance Breakthrough to all Construct. When a Construct with 10 stacks of Performance Breakthrough is destroyed, deals Physical damage equivalent to 100% of the Construct DEF to all enemies within a 3 tile radius. This will not trigger Interceptions, Counterattacks or Action Supports",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For each point of Confectance Index held, increases the damage multiplier of Quenching Strike by 5%\n\nEnhances the effects of Performance Breakthrough - Increases ATK and DEF by 5%"
          }
        ],
        "icon": "assets/Balthilde/Wrench Calibration.png"
      },
      {
        "name": "Safety Consciousness",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Upon summoned, applies Defense Up I for 2 turns and restores HP equivalent to 100% DEF for all allies within a 3 tile radius",
        "upgrades": [],
        "icon": "assets/Balthilde/Safety Consciousness.png"
      },
      {
        "name": "Focused Maintenance",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Cover within a 3 tile radius will not lose durability. Decreases damage received by 30% for allies within range that are not benefitting from damage reduction by Cover",
        "upgrades": [],
        "icon": "assets/Balthilde/Focused Maintenance.png"
      },
      {
        "name": "Disassembly Knack",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Selects the nearest enemy target within a 3 tile radius and deals Physical damage equivalent to 100% DEF to it. This can be used twice per turn",
        "upgrades": [],
        "icon": "assets/Balthilde/Disassembly Knack.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Demolition Protocol",
        "level": "2",
        "effect": "Increases the range of Disassembly Knack to 5 tiles, and applies Stress Fracture on the target for 2 turns"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Reinforcement Protocol",
        "level": "2",
        "effect": "Increases the range of Safety Consciousness and Focused Maintenance to 5 tiles\n\nNew effect is added for Safety Consciousness - Upon summoned, restores the durability of all Cover within a 5 tile radius\n\nNew effect is added for Focused Maintenance - Restores HP equivalent to 100% DEF and 2 Stability, and applies Defense Up I for all allies within a 5 tile radius at the end of their action"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Raging Chainblast",
        "level": "2",
        "effect": "Resets the cooldown of Reinforcement Protocol and Demolition Protocol\n\nRestores HP equivalent to 100% ATK for all allies, and applies Load-Bearing Parts for 2 turns"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Demolition Protocol",
        "level": "2",
        "effect": "Decreases the cooldown of this skill by 1 turn. Increases the ATK and DEF inherited by Offense Construct to 100%\n\nIncreases the number of times Disassembly Knack can be used per turn by 1"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Reinforcement Protocol",
        "level": "3",
        "effect": "Decreases the cooldown of this skill by 1 turn. Increases the ATK and DEF inherited by Defense Construct to 100%\n\nEnhances the effects of Safety Consciousness - Upon summoned, restores HP equivalent to 200% DEF and 4 Stability\n\nEnhances the effects of Focused Maintenance - Damage reduction is applied to all allies instead"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Wrench Calibration",
        "level": "3",
        "effect": "For each point of Confectance Index held, increases the damage multiplier of Quenching Strike by 5%\n\nEnhances the effects of Performance Breakthrough - Increases ATK and DEF by 5%"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Cannot Spit It Out",
        "level": "20",
        "keyName": "Fixed Key 1 - Cannot Spit It Out",
        "description": "Before using an active attack, applies Stress Fracture on the enemy for 2 turns",
        "icon": "assets/Balthilde/Fixed Key 1 - Cannot Spit It Out.png"
      },
      {
        "node": "Fixed Key 2 - Impatient",
        "level": "20",
        "keyName": "Fixed Key 2 - Impatient",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Balthilde/Fixed Key 2 - Impatient.png"
      },
      {
        "node": "Fixed Key 3 - Misunderstood Intention",
        "level": "30",
        "keyName": "Fixed Key 3 - Misunderstood Intention",
        "description": "At the end of the action, applies Damage Reduction II for all allies not near to Cover for 1 turn",
        "icon": "assets/Balthilde/Fixed Key 3 - Misunderstood Intention.png"
      },
      {
        "node": "Fixed Key 4 - Fault Elimination Module",
        "level": "30",
        "keyName": "Fixed Key 4 - Fault Elimination Module",
        "description": "At the end of the action, restores 3 Stability for the ally with the lowest Stability",
        "icon": "assets/Balthilde/Fixed Key 4 - Fault Elimination Module.png"
      },
      {
        "node": "Fixed Key 5 - Practical Modifications",
        "level": "40",
        "keyName": "Fixed Key 5 - Practical Modifications",
        "description": "Before allies are attacked, Defense Construct restores 1 Stability for them",
        "icon": "assets/Balthilde/Fixed Key 5 - Practical Modifications.png"
      },
      {
        "node": "Fixed Key 6 - Mechanical Control",
        "level": "40",
        "keyName": "Fixed Key 6 - Mechanical Control",
        "description": "When a Construct is on the field, increases Stability damage dealt by self by 3 points",
        "icon": "assets/Balthilde/Fixed Key 6 - Mechanical Control.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Balthilde/Affinity Key.png"
      },
      {
        "node": "Common Key - Adept Smith",
        "level": "40",
        "keyName": "Common Key - Adept Smith",
        "description": "HP +5% / Increases DEF for the holder's Physical Summon by 7%",
        "icon": "assets/Balthilde/Common Key - Adept Smith.png"
      },
      {
        "node": "Expansion Key - Steel Awakening",
        "level": "60",
        "keyName": "Expansion Key - Steel Awakening",
        "description": "After using ultimate skill Raging Chainblast, if the active skill Reinforcement Protocol or Demolition Protocol is not on cooldown, Balthilde may use this skill. The Confectance Index cost of the ultimate skill Raging Chainblast is reduced to 4 points.\nConstructs gain additional effects based on the number of Performance Breakthrough stacks:\n0: Balthilde gains 4 points of Confectance Index and Constructs cleanse 1 debuff from ally units withing 5 tiles.\n2: Defense of any ally units within 5 tiles from Constructs is increased by 20%. Does not stack.\n5: When using ultimate skill Raging Chainblast and there are Constructs fwithing the area of effect, trigger the damaging death effect of the passive skill Wrench Calibration for them. Each stack of Performance Breakthrough increases the damage multiplier of the death effect by 20%.",
        "icon": "assets/Balthilde/Expansion Key - Steel Awakening.png"
      }
    ]
  },
  "Alva": {
    "class": "Support",
    "stats": {
      "hp": 1973,
      "atk": 757,
      "def": 512
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Laceration",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Alva/Laceration.png"
      },
      {
        "name": "Snow Wolf's Heart",
        "traits": [
          "Skill",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Enters into Covering Mode for 3 rounds (Duration decreases at the end of the current round). Selects an enemy target within a 8 tile radius and deals Freeze damage equivalent to 100% ATK to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases the conversion rate to Brumal Barrier dealt by Interception during Covering Mode by 30%\n\nIn Covering Mode, 20% of the damage dealt by Nix Requiem is converted into Brumal Barrier for all allies"
          }
        ],
        "icon": "assets/Alva/Snow Wolf's Heart.png"
      },
      {
        "name": "Frosted Echo",
        "traits": [
          "Skill",
          "AoE",
          "Summon"
        ],
        "attribute": "Freeze",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "8",
        "effArea": "4",
        "description": "Selects an empty tile within a 8 tile radius, consumes all Confectance Index, for each Confectance Index consumed, deals AoE Freeze damage equivalent to 15% ATK and 1 Stability Damage to all enemies within a 4 tile radius of the selected tile, and summons Liquid N2 Fang for 3 rounds (Duration decreases at the end of the current round)\n\nIf Alva has 3 stacks of Battle Prep after skill usage, consumes 3 stacks of Battle Prep and gains Extra Command",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases damage multiplier to 20% ATK. If Alva has 3 stacks of Battle Prep after skill usage, enters into Covering Mode for 3 rounds (Duration decreases at the end of the current round) and increases Confectance Index by 6 points"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Enhances the effects of Liquid N2 Fang - Increases damage multiplier to 60% of the Shield HP\n\nEnhances the effects of Hypothermia - Increases Freeze damage received by 40%"
          }
        ],
        "icon": "assets/Alva/Frosted Echo.png"
      },
      {
        "name": "Nix Requiem",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius, consumes all Confectance Index, for each Confectance Index consumed, deals Freeze damage equivalent to 30% ATK and 1 Stability Damage to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases damage multiplier to 40% ATK\n\nAfter skill usage, increases Confectance Index by 1 point for all Freeze units (excluding self)"
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Rise Anew",
            "effect": "Nix Requiem: Before skill usage, dispels 2 buffs from the target"
          }
        ],
        "icon": "assets/Alva/Nix Requiem.png"
      },
      {
        "name": "Freezing Touch",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Increases Shield amount applied by allies by 30%. When allies gain a Shield, the Shield is converted into Brumal Barrier with the same Shield HP. At the end of the action, increases Confectance Index by 3 points and gains 1 stack of Battle Prep. After launching Interception, increases Confectance Index by 1 point",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases Shield amount applied by allies by 50%\n\nNew effect is added for Brumal Barrier - When the holder deals Freeze damage, for every 1000 Shield HP held, increases CRIT DMG by 1%"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increases absorption amount of Brumal Barrier to 300% of Alva's initial attack\n\nWhen the holder deals Freeze damage, for every 1000 Shield HP held, the damage increase and CRIT DMG increase bonus are doubled"
          }
        ],
        "icon": "assets/Alva/Freezing Touch.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Frosted Echo",
        "level": "2",
        "effect": "Increases damage multiplier to 20% ATK. If Alva has 3 stacks of Battle Prep after skill usage, enters into Covering Mode for 3 rounds (Duration decreases at the end of the current round) and increases Confectance Index by 6 points"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Nix Requiem",
        "level": "2",
        "effect": "Increases damage multiplier to 40% ATK\n\nAfter skill usage, increases Confectance Index by 1 point for all Freeze units (excluding self)"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Freezing Touch",
        "level": "2",
        "effect": "Increases Shield amount applied by allies by 50%\n\nNew effect is added for Brumal Barrier - When the holder deals Freeze damage, for every 1000 Shield HP held, increases CRIT DMG by 1%"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Snow Wolf's Heart",
        "level": "2",
        "effect": "Increases the conversion rate to Brumal Barrier dealt by Interception during Covering Mode by 30%\n\nIn Covering Mode, 20% of the damage dealt by Nix Requiem is converted into Brumal Barrier for all allies"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Frosted Echo",
        "level": "3",
        "effect": "Enhances the effects of Liquid N2 Fang - Increases damage multiplier to 60% of the Shield HP\n\nEnhances the effects of Hypothermia - Increases Freeze damage received by 40%"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Freezing Touch",
        "level": "3",
        "effect": "Increases absorption amount of Brumal Barrier to 300% of Alva's initial attack\n\nWhen the holder deals Freeze damage, for every 1000 Shield HP held, the damage increase and CRIT DMG increase bonus are doubled"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Snowfield Strider",
        "level": "20",
        "keyName": "Fixed Key 1 - Snowfield Strider",
        "description": "When Hoarfrost is applied to enemies within a 4 tile radius of Liquid N2 Fang, generates Frost tiles within the area for 3 turns",
        "icon": "assets/Alva/Fixed Key 1 - Snowfield Strider.png"
      },
      {
        "node": "Fixed Key 2 - Logistics Specialist",
        "level": "20",
        "keyName": "Fixed Key 2 - Logistics Specialist",
        "description": "At the start of the battle, increases Confectance Index by 3 points and gains 3 stacks of Battle Prep",
        "icon": "assets/Alva/Fixed Key 2 - Logistics Specialist.png"
      },
      {
        "node": "Fixed Key 3 - Support Command",
        "level": "30",
        "keyName": "Fixed Key 3 - Support Command",
        "description": "Decreases Stability damage received for allies with Brumal Barrier by 1 point",
        "icon": "assets/Alva/Fixed Key 3 - Support Command.png"
      },
      {
        "node": "Fixed Key 4 - Late Bloomer",
        "level": "30",
        "keyName": "Fixed Key 4 - Late Bloomer",
        "description": "For each stack of Battle Prep consumed, increases ATK for self by 3%, up to 18%",
        "icon": "assets/Alva/Fixed Key 4 - Late Bloomer.png"
      },
      {
        "node": "Fixed Key 5 - Rise Anew",
        "level": "40",
        "keyName": "Nix Requiem",
        "description": "Before skill usage, dispels 2 buffs from the target",
        "icon": "assets/Alva/Nix Requiem.png"
      },
      {
        "node": "Fixed Key 6 - Bonechill",
        "level": "40",
        "keyName": "Fixed Key 6 - Bonechill",
        "description": "Increases Stability damage taken by enemies within a 4 tile radius of Liquid N2 Fang by 2 points",
        "icon": "assets/Alva/Fixed Key 6 - Bonechill.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Alva/Affinity Key.png"
      },
      {
        "node": "Common Key - Mind's Eye",
        "level": "40",
        "keyName": "Common Key - Mind's Eye",
        "description": "ATK +5% / Increases Phase damage towards enemies with Shield by 10%",
        "icon": "assets/Alva/Common Key - Mind's Eye.png"
      },
      {
        "node": "Expansion Key - Inheriting the name of the Alpha Wolf",
        "level": "60",
        "keyName": "Expansion Key - Inheriting the name of the Alpha Wolf",
        "description": "The effect of Shield applied by this unit is increased by 80%.\nBrumal Barrier effect enchanced: When dealing Freeze damage, the Shield value required to increase the damage dealt and critical damage is reduced to 500.\nWhen frendly unit has Brumal Barrier and deals Freeze damage, they ignore 15% of target's defence.\nLiquid N2 Fang effect enchanced: When Alva attacks, the damage multiplier based on the accumulated Shield absorbtion is doubled.",
        "icon": "assets/Alva/Expansion Key - Inheriting the name of the Alpha Wolf.png"
      }
    ]
  },
  "Voymastina": {
    "class": "Sentinel",
    "stats": {
      "hp": 1819,
      "atk": 844,
      "def": 528
    },
    "stabilityGauge": 12,
    "movementSpeed": 7,
    "skillAttributes": [
      "Melee",
      "Medium Ammo"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Dread Ultimatum",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Voymastina/Dread Ultimatum.png"
      },
      {
        "name": "Howl from the Firmament",
        "traits": [
          "Skill",
          "AoE",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "3",
        "description": "Selects an enemy target within a 8 tile radius and deals AoE Physical damage equivalent to 120% ATK to all enemies within a 3 tile radius of the target\n\nPassive: When enemies within Attack Range receives Targeted damage from allies, performs an instance of Action Support, dealing AoE Physical damage equivalent to 100% ATK and 3 Stability to all enemies within a 3 tile radius of the target. This effect can be triggered once per round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases damage multiplier to 180% ATK, increases Stability damage dealt by 2 points, increases effect area by 2 tiles\n\nPassive: Increases damage multiplier to 150% ATK, increases Stability damage dealt by 1 point, increases effect area by 2 tiles"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "New effect is added for Passive - When performing any Action Support, gains 1 stack of Coordinated Hunting"
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1",
            "effect": "Howl from the Firmament: If this skill or its passive effect hit a boss enemy or 3 or more enemies, gains Quick Barrier"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4",
            "effect": "Howl from the Firmament: If this skill or its passive effect only hits 1 enemy, increases damage dealt by 20% and Stability damage dealt by 2 points"
          }
        ],
        "icon": "assets/Voymastina/Howl from the Firmament.png"
      },
      {
        "name": "Eye of the White Mastiff",
        "traits": [
          "Skill"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "8",
        "description": "Voymastina gains Wolf Eye System for 2 rounds (Duration decreases at the end of the current round). After skill usage, gains Extra Command\n\nPassive: At the start of the battle, deals Physical damage equivalent to 100% ATK that ignores Cover and 3 Stability to the 5 nearest enemies on the entire field. Voymastina is immune to all damage and fixed damage, lasting till the effects of the Passive has been triggered",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Wolf Eye System: Increases duration by 1 round (Duration decreases at the end of the current round), increases damage multiplier to 130% ATK, and removes the maximum trigger limit per round. If an enemy is spawned within Attack Range, deals targeted damage equivalent to 130% ATK and 1 Stability to the target\n\nPassive: Increases damage multiplier to 300% ATK, increases number of targets to 10, and applies Stun for 1 turn after attack\n\nBefore triggering the active or passive effects of this skill, applies Dismay on the target for 2 rounds"
          }
        ],
        "icon": "assets/Voymastina/Eye of the White Mastiff.png"
      },
      {
        "name": "Pile Bunker",
        "traits": [
          "Ultimate",
          "AoE",
          "Displacement"
        ],
        "attribute": "Melee",
        "stabilityDamage": 5,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals AoE melee Physical damage equivalent to 200% ATK to all enemies within a 1x2 tile radius in the selected direction. After skill usage, gains Additional Movement\n\nPassive: When enemies within Attack Range receives Targeted damage from allies, performs an instance of Action Support, charging to an empty tile within a 2 tile radius of the target, and dealing targeted melee Physical damage equivalent to 150% ATK that ignores Cover and 3 Stability to the target. If there are no empty tiles, shoots at the target to deal damage instead. This effect can be triggered once per round",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Before triggering the active or passive effects of this skill, increases ATK by 10% for 1 round (Duration decreases at the end of the current round), and applies Frightened on the target for 2 round (Duration decreases at the end of the current round)"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases damage multplier to 300%. If Voymastina has Predation Protocol, increases ATK by 30%\n\nBefore triggering the active or passive effects of this skill, applies Defense Down II for 2 turns"
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2",
            "effect": "Pile Bunker: After triggering the passive effect of this skill, gains Movement Up II for 2 turns"
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6",
            "effect": "Pile Bunker: After being attacked, the next usage of this skill deals 15% more damage"
          }
        ],
        "icon": "assets/Voymastina/Pile Bunker.png"
      },
      {
        "name": "Mastiff's Vow",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Voymastina is immune to movement displacement and movement debuffs, does not receive protection from Cover, but reduces damage taken by 30%. When Stability is more than 0, reduces damage taken by 80% instead\n\nWhen dealing Physical damage, ignores 50% of the target's DEF. After using active skills or basic attack, increases Confectance Index by 2 points. If Confectance Index is at max, consumes all of it and gains Predation Protocol",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increases movement speed by 2 tiles\n\nAt the start of the battle, gains Pursuer. For each round, if Voymastina used 2 or more active skills or their passive effects, gains Pursuer or refreshes its duration. For each Action Support performed, gains 1 stack of Hunting Rhythm\n\nWhen Voymastina's ATK is increased, her DEF is increased by 50% of the corresponding ATK increase value, up to a maximum of 30% of her initial DEF. When dealing Physical damage, ignores 125% of the target's DEF"
          }
        ],
        "icon": "assets/Voymastina/Mastiff's Vow.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Howl from the Firmament",
        "level": "2",
        "effect": "Increases damage multiplier to 180% ATK, increases Stability damage dealt by 2 points, increases effect area by 2 tiles\n\nPassive: Increases damage multiplier to 150% ATK, increases Stability damage dealt by 1 point, increases effect area by 2 tiles"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Pile Bunker",
        "level": "2",
        "effect": "Before triggering the active or passive effects of this skill, increases ATK by 10% for 1 round (Duration decreases at the end of the current round), and applies Frightened on the target for 2 round (Duration decreases at the end of the current round)"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Eye of the White Mastiff",
        "level": "2",
        "effect": "Wolf Eye System: Increases duration by 1 round (Duration decreases at the end of the current round), increases damage multiplier to 130% ATK, and removes the maximum trigger limit per round. If an enemy is spawned within Attack Range, deals targeted damage equivalent to 130% ATK and 1 Stability to the target\n\nPassive: Increases damage multiplier to 300% ATK, increases number of targets to 10, and applies Stun for 1 turn after attack\n\nBefore triggering the active or passive effects of this skill, applies Dismay on the target for 2 rounds"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Howl from the Firmament",
        "level": "3",
        "effect": "New effect is added for Passive - When performing any Action Support, gains 1 stack of Coordinated Hunting"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Pile Bunker",
        "level": "3",
        "effect": "Increases damage multplier to 300%. If Voymastina has Predation Protocol, increases ATK by 30%\n\nBefore triggering the active or passive effects of this skill, applies Defense Down II for 2 turns"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Mastiff's Vow",
        "level": "2",
        "effect": "Increases movement speed by 2 tiles\n\nAt the start of the battle, gains Pursuer. For each round, if Voymastina used 2 or more active skills or their passive effects, gains Pursuer or refreshes its duration. For each Action Support performed, gains 1 stack of Hunting Rhythm\n\nWhen Voymastina's ATK is increased, her DEF is increased by 50% of the corresponding ATK increase value, up to a maximum of 30% of her initial DEF. When dealing Physical damage, ignores 125% of the target's DEF"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1",
        "level": "20",
        "keyName": "Howl from the Firmament",
        "description": "If this skill or its passive effect hit a boss enemy or 3 or more enemies, gains Quick Barrier",
        "icon": "assets/Voymastina/Howl from the Firmament.png"
      },
      {
        "node": "Fixed Key 2",
        "level": "20",
        "keyName": "Pile Bunker",
        "description": "After triggering the passive effect of this skill, gains Movement Up II for 2 turns",
        "icon": "assets/Voymastina/Pile Bunker.png"
      },
      {
        "node": "Fixed Key 3",
        "level": "30",
        "keyName": "Fixed Key 3",
        "description": "The range of all Action Support is extended to the entire field, and deals 30% more damage towards non boss enemies",
        "icon": "assets/Voymastina/Fixed Key 3.png"
      },
      {
        "node": "Fixed Key 4",
        "level": "30",
        "keyName": "Howl from the Firmament",
        "description": "If this skill or its passive effect only hits 1 enemy, increases damage dealt by 20% and Stability damage dealt by 2 points",
        "icon": "assets/Voymastina/Howl from the Firmament.png"
      },
      {
        "node": "Fixed Key 5",
        "level": "40",
        "keyName": "Fixed Key 5",
        "description": "Before attacking, gains Reversed Assault for 3 turns",
        "icon": "assets/Voymastina/Fixed Key 5.png"
      },
      {
        "node": "Fixed Key 6",
        "level": "40",
        "keyName": "Pile Bunker",
        "description": "After being attacked, the next usage of this skill deals 15% more damage",
        "icon": "assets/Voymastina/Pile Bunker.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Voymastina/Affinity Key.png"
      },
      {
        "node": "Common Key",
        "level": "40",
        "keyName": "Common Key",
        "description": "ATK +5% / When dealing melee damage, increases Physical damage dealt by 10% for 1 round (Duration decreases at the end of the current round)",
        "icon": "assets/Voymastina/Common Key.png"
      }
    ]
  },
  "Lewis": {
    "class": "Sentinel",
    "stats": {
      "hp": 1948,
      "atk": 827,
      "def": 504
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Heavy Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Light Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Playtime",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Lewis/Playtime.png"
      },
      {
        "name": "Bad Guy Cleanup",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Select 1 direction around self, deal AoE Burn damage equal to 80% of attack to all enemy targets within a 3x5 frontal area and inflicts Overburn for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage multiplier is increased to 120%. For each Burn debuff on the target, this attack deals 10% more damage, up to a maximum of 30%."
          }
        ],
        "icon": "assets/Lewis/Bad Guy Cleanup.png"
      },
      {
        "name": "Surprising FunBall",
        "traits": [
          "Active",
          "Targeted",
          "Buff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Burn damage equal to 140% of attack to it. Deals fixed damage equal to 30% of attack to the target and all enemies within a 3 tile radius of it. Lewis gains 2 stacks of Tin Soldier's Order.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Damage multiplier is increased to 160%, fixed damage multiplier is increased to 50%. \n\nTin Soldier's Order effect is modified: It no longer has stacks and no longer gets consumed by Volley Fire. Lasts for 3 rounds and increase Volley Fire damage by 50% instead."
          }
        ],
        "icon": "assets/Lewis/Surprising FunBall.png"
      },
      {
        "name": "Toy Carnival",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Burn damage equal to 180% of attack to it. For each Tin Soldier on the battlefield, increases damage dealt by 15% per Rank and critical rate by 5% per Rank of this attack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Reduces the Confectance Cost by 2 points. \nAdditional effects are added based on your highest current Rank. Higher-level effects include lower-level effects:\nRank 1: Gain Damage Up II before attacking, lasting for 2 turns.\nRank 2: This attack now ignores cover.\nRank 3: Increases the damage multiplier to 200% of your attack."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Each Tin Soldier additionally increases damage multiplier of this attack by 10% per Rank; critical damage is additionally increased by 5% per Rank."
          }
        ],
        "icon": "assets/Lewis/Toy Carnival.png"
      },
      {
        "name": "Tin Soldiers on Parade",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "All field",
        "description": "At the start of the battle, Lewis gains Thermal Conduction, and consumes all points of Confectance Index to assign Tin Soldier with Rank 1 to the 2 closest allied Burn attribute Dolls (excluding self).\n\nWhen allied units with Tin Soldier perform basic attacks or active attacks that deal Burn damage, Lewis commands the Tin Soldier to launch a Volley Fire at the target that took damage, and gains 3 points of Searing Flame and 1 Confectance Index. This effect can be triggered once per turn for each Tin Soldier.\n\nWhen the unit with Tin Soldier assigned deals Burn damage, said unit gains 1 Merit.\n\nAt the end of the round, Lewis consumes 4 Merit to increase the Rank of the Tin Soldier, maximum once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the base damage multiplier of a Volley Fire to 120% of Lewis attack.\nWhen Tin Soldier casts Volley Fire, if the enemy target has Overburn, the Overburn effect will be triggered a number of times corresponding to their Rank."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Assigned at the start of the battle Tin Soldier has Rank 2.\nRank effect enhancements:\nRank 2: Additionally increases Critical Damage by 15%.\nRank 3: At the end of assigned doll action, unleashes Volley Fire once on the nearest enemy target. This Volley Fire provides Searing Flame but does not restore Confectance Index."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Secret of Spreading Smiles",
            "effect": "Modifies the passive effect of Tin Soldiers on Parade, allowing it to apply Tin Soldiers even to non-Burn attribute Dolls. If a basic attack or active attack does not deal Burn damage, it can still trigger Volley Fire."
          }
        ],
        "icon": "assets/Lewis/Tin Soldiers on Parade.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Tin Soldiers on Parade",
        "level": "2",
        "effect": "Increases the base damage multiplier of a Volley Fire to 120% of Lewis attack.\nWhen Tin Soldier casts Volley Fire, if the enemy target has Overburn, the Overburn effect will be triggered a number of times corresponding to their Rank."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Toy Carnival",
        "level": "2",
        "effect": "Reduces the Confectance Cost by 2 points. \nAdditional effects are added based on your highest current Rank. Higher-level effects include lower-level effects:\nRank 1: Gain Damage Up II before attacking, lasting for 2 turns.\nRank 2: This attack now ignores cover.\nRank 3: Increases the damage multiplier to 200% of your attack."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Surprising FunBall",
        "level": "2",
        "effect": "Damage multiplier is increased to 160%, fixed damage multiplier is increased to 50%. \n\nTin Soldier's Order effect is modified: It no longer has stacks and no longer gets consumed by Volley Fire. Lasts for 3 rounds and increase Volley Fire damage by 50% instead."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Bad Guy Cleanup",
        "level": "2",
        "effect": "Damage multiplier is increased to 120%. For each Burn debuff on the target, this attack deals 10% more damage, up to a maximum of 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Toy Carnival",
        "level": "3",
        "effect": "Each Tin Soldier additionally increases damage multiplier of this attack by 10% per Rank; critical damage is additionally increased by 5% per Rank."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Tin Soldiers on Parade",
        "level": "3",
        "effect": "Assigned at the start of the battle Tin Soldier has Rank 2.\nRank effect enhancements:\nRank 2: Additionally increases Critical Damage by 15%.\nRank 3: At the end of assigned doll action, unleashes Volley Fire once on the nearest enemy target. This Volley Fire provides Searing Flame but does not restore Confectance Index."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Idealistic Designer",
        "level": "20",
        "keyName": "Fixed Key 1 - Idealistic Designer",
        "description": "Before using Volley Fire, inflicts Overburn to the target for 2 turns.",
        "icon": "assets/Lewis/Fixed Key 1 - Idealistic Designer.png"
      },
      {
        "node": "Fixed Key 2 - Secret of Spreading Smiles",
        "level": "20",
        "keyName": "Fixed Key 2 - Secret of Spreading Smiles",
        "description": "Modifies the passive effect of Tin Soldiers on Parade, allowing it to apply Tin Soldiers even to non-Burn attribute Dolls. If a basic attack or active attack does not deal Burn damage, it can still trigger Volley Fire.",
        "icon": "assets/Lewis/Fixed Key 2 - Secret of Spreading Smiles.png"
      },
      {
        "node": "Fixed Key 3 - Protector of Innocence",
        "level": "30",
        "keyName": "Fixed Key 3 - Protector of Innocence",
        "description": "The active skill Surprising Funball and the Toy Carnival dispels 1 buff on the target before the attack resolves.",
        "icon": "assets/Lewis/Fixed Key 3 - Protector of Innocence.png"
      },
      {
        "node": "Fixed Key 4 - Sunny Imagination",
        "level": "30",
        "keyName": "Fixed Key 4 - Sunny Imagination",
        "description": "When attacking an enemy target with Overburn, damage dealt is increased by 15% and inflicts Defense Down II.",
        "icon": "assets/Lewis/Fixed Key 4 - Sunny Imagination.png"
      },
      {
        "node": "Fixed Key 5 - Cuteness is Justice",
        "level": "40",
        "keyName": "Fixed Key 5 - Cuteness is Justice",
        "description": "At the start of the turn, if there are Tin Soldiers on the field with a Rank of 2 and higher, the range of the active skill Surprising Funball and the Ultimate skill Toy Carnival is increased by 2 for this battle.",
        "icon": "assets/Lewis/Fixed Key 5 - Cuteness is Justice.png"
      },
      {
        "node": "Fixed Key 6 - Guardian From The Cloud",
        "level": "40",
        "keyName": "Fixed Key 6 - Guardian From The Cloud",
        "description": "Units with Tin Soldiers gain 2 Merit at the end of their action.",
        "icon": "assets/Lewis/Fixed Key 6 - Guardian From The Cloud.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Lewis/Affinity Key.png"
      },
      {
        "node": "Common Key - Mighty Miracle",
        "level": "40",
        "keyName": "Common Key - Mighty Miracle",
        "description": "ATK +5% / Damage dealt by Ultimate skills is increased by 10%.",
        "icon": "assets/Lewis/Common Key - Mighty Miracle.png"
      }
    ]
  },
  "Helen": {
    "class": "Bulwark",
    "stats": {
      "hp": 2233,
      "atk": 645,
      "def": 642
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Shotgun Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Sentinel",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Freeze damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Helen/Sentinel.png"
      },
      {
        "name": "Aegis Command",
        "traits": [
          "Active",
          "Buff",
          "Damage Share"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an ally (excluding self) within a 6 tile radius and applies Aegis on it. If unit with Aegis takes damage within 6 tiles from Helen, she will share 100% of initial damage on their behalf, as well as cleansing Taunt and Fear. Aegis can be applied only to one target. After skill usage, gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Additionally removes Infatuated and Stun. If fatal damage is taken while sharing damage, Helen will not die and will recover HP equal to 150% of her defense. This effect can be triggered up to once per round. Friendly units with Aegis deal 30% more Freeze damage."
          }
        ],
        "icon": "assets/Helen/Aegis Command.png"
      },
      {
        "name": "Shield Charge",
        "traits": [
          "Active",
          "Buff",
          "Tile",
          "Defense"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within a cross-shaped area of 4 to 8 tiles and lands on the selected tile. All allied units along the path will have one debuff cleansed and gain Frost Shield that absorbs 100% of Helen's initial attack damage, up to a maximum of 100% of the target's maximum health. Generates Frost tiles along the path for 2 turns.\nFor each allied unit (excluding self) on the path, the effectiveness of this Frost Shield is increased by 30%, and restores 2 points of stability to Helen. After skill usage, Helen gains 6 tiles of Additional Movement and can use her basic attack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases width by 2 tiles, cleanse 2 additional debuffs, and applies Critical Damage Up II for 2 turns."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "For each allied unit (excluding self) on the path, an additional 2 points of stability are restored, and the corresponding number of layers of Frost Drive are gained."
          }
        ],
        "icon": "assets/Helen/Shield Charge.png"
      },
      {
        "name": "Banner Sentinel",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an ally (excluding self) within a 6 tile radius and applies Attack Up III and Defense Up III to them for 2 turns. In addition, reduces Ultimate cooldown of all Freeze-attribute Dolls (excluding self) on the field by 1 turn. After skill usage, Helen gains Additional Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Cooldown is reduced by 2 turns. Gain Attack Up III and Defense Up III for 2 turns. Gain 10 stacks of Overedge. Reduces Ultimate cooldown of Freeze-attribute Dolls by 2 turns ."
          }
        ],
        "icon": "assets/Helen/Banner Sentinel.png"
      },
      {
        "name": "Fearless Valkyrie",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Helen is immune to healing reduction effects, but cannot receive healing or effects that convert healing into damage.\nAt the start of battle, increases Helen's defense and Max HP by 30%.\nAt the start of each turn, Helen gains 2 points of Confectance Index, restores 25% of HP, and cleanse all debuffs from self.\nFor every instance of damage taken, Helen gains 1 stack of Overedge.\nWhen Helen has Overedge, the damage multiplier of her basic attacks is increased to 180%.\nBefore Helen performs a basic attack, her attack is increased by 15% of her defence.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases the Stability Gauge to 16 points, reducing damage taken by 50%. Each time\nyou take damage, you gain an additional stack of Overedge. Before performing a basic attack, increase your attack power by 30% of your defense."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Before performing a basic attack, increase Helen attack by 70% of her defense .\nWhen a friendly unit takes damage, gain 2 stacks of Overedge. While having Overedge, the damage multiplier of basic attacks is increased to 300%."
          }
        ],
        "icon": "assets/Helen/Fearless Valkyrie.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Shield Charge",
        "level": "2",
        "effect": "Increases width by 2 tiles, cleanse 2 additional debuffs, and applies Critical Damage Up II for 2 turns."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Fearless Valkyrie",
        "level": "2",
        "effect": "Increases the Stability Gauge to 16 points, reducing damage taken by 50%. Each time\nyou take damage, you gain an additional stack of Overedge. Before performing a basic attack, increase your attack power by 30% of your defense."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Banner Sentinel",
        "level": "2",
        "effect": "Cooldown is reduced by 2 turns. Gain Attack Up III and Defense Up III for 2 turns. Gain 10 stacks of Overedge. Reduces Ultimate cooldown of Freeze-attribute Dolls by 2 turns ."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Aegis Command",
        "level": "2",
        "effect": "Additionally removes Infatuated and Stun. If fatal damage is taken while sharing damage, Helen will not die and will recover HP equal to 150% of her defense. This effect can be triggered up to once per round. Friendly units with Aegis deal 30% more Freeze damage."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Shield Charge",
        "level": "3",
        "effect": "For each allied unit (excluding self) on the path, an additional 2 points of stability are restored, and the corresponding number of layers of Frost Drive are gained."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Fearless Valkyrie",
        "level": "3",
        "effect": "Before performing a basic attack, increase Helen attack by 70% of her defense .\nWhen a friendly unit takes damage, gain 2 stacks of Overedge. While having Overedge, the damage multiplier of basic attacks is increased to 300%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - The Two-Headed Spy",
        "level": "20",
        "keyName": "Fixed Key 1 - The Two-Headed Spy",
        "description": "At the start of the turn, Helen gains 3 stacks of Overedge",
        "icon": "assets/Helen/Fixed Key 1 - The Two-Headed Spy.png"
      },
      {
        "node": "Fixed Key 2 - Frostbite Bloom",
        "level": "20",
        "keyName": "Fixed Key 2 - Frostbite Bloom",
        "description": "When performing basic attacks against boss units, Freeze damage dealt is increased by 20%.",
        "icon": "assets/Helen/Fixed Key 2 - Frostbite Bloom.png"
      },
      {
        "node": "Fixed Key 3 - Buried Memories",
        "level": "30",
        "keyName": "Fixed Key 3 - Buried Memories",
        "description": "Before performing a basic attack, dispel 2 buffs from the enemy target.",
        "icon": "assets/Helen/Fixed Key 3 - Buried Memories.png"
      },
      {
        "node": "Fixed Key 4 - Guardian's Resolve",
        "level": "30",
        "keyName": "Fixed Key 4 - Guardian's Resolve",
        "description": "At the end of Helen's action, applies 2 stacks of Shelter to herself and all allied units with Aegis.",
        "icon": "assets/Helen/Fixed Key 4 - Guardian's Resolve.png"
      },
      {
        "node": "Fixed Key 5 - Glory to Mommies",
        "level": "40",
        "keyName": "Fixed Key 5 - Glory to Mommies",
        "description": "At the start of the turn, if Helen's HP is above 30%, she gains Glory to Mommies, preventing her defense from being reduced below less than 100%. Cancels when Helen's HP is below 30%.",
        "icon": "assets/Helen/Fixed Key 5 - Glory to Mommies.png"
      },
      {
        "node": "Fixed Key 6 - Enforcer of Order",
        "level": "40",
        "keyName": "Fixed Key 6 - Enforcer of Order",
        "description": "Reduces stability damage taken by 2 points, and grants immunity to Stun and Fear.",
        "icon": "assets/Helen/Fixed Key 6 - Enforcer of Order.png"
      },
      {
        "node": "Affinity Key - New Sprout",
        "level": "-",
        "keyName": "Affinity Key - New Sprout",
        "description": "ATK +3%, HP +3%, DEF +3%",
        "icon": "assets/Helen/Affinity Key - New Sprout.png"
      },
      {
        "node": "Common Key - Immovable Defense",
        "level": "40",
        "keyName": "Common Key - Immovable Defense",
        "description": "DEF +5.0% / If the user's defense is greater than or equal to the target's Defense, their damage dealt is increased by 10%.",
        "icon": "assets/Helen/Common Key - Immovable Defense.png"
      }
    ]
  },
  "Phaetusa": {
    "class": "Sentinel",
    "stats": {
      "hp": 1989,
      "atk": 802,
      "def": 528
    },
    "stabilityGauge": 9,
    "movementSpeed": 9,
    "skillAttributes": [
      "Melee",
      "Corrosion"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Dual Slash",
        "traits": [
          "Basic Attack",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "Target",
        "description": "Selects 1 target within 1 tile, dealing melee Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Phaetusa/Dual Slash.png"
      },
      {
        "name": "Descent of twin wings",
        "traits": [
          "Active",
          "Aoe",
          "Displacement"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within a cross-shaped area of 8 tiles, landing on the selected tile and dealing AoE Corrosion melee damage equal to 90% of attack to all enemy targets on the path.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases damage multiplier to 120% and width increases by 2 tiles."
          }
        ],
        "icon": "assets/Phaetusa/Descent of twin wings.png"
      },
      {
        "name": "Mirror Trap",
        "traits": [
          "Active",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "Target",
        "description": "Gain 1 stack of Blade Resonance and apply Laceration to all enemy targets on the field for 2 turns. After skill usage, Phaetusa gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Every 2 skill uses, Phaetusa will gain an additional stack of Blade Resonance, and her critical damage will be permanently increased by 15%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "After skill is used Phaetusa will gain new buff: Tempered Blood - increases damage multiplier of next active attack by 200%."
          }
        ],
        "icon": "assets/Phaetusa/Mirror Trap.png"
      },
      {
        "name": "Twin paradise",
        "traits": [
          "Ultimate",
          "Aoe",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "5",
        "description": "Deal AoE Melee Corrosion damage equal to 90% attack power to all enemies within a 5 tile radius. Consumes all stacks of Blade Resonance; for each stack consumed, increases damage multiplier of the skill by 10% and then additionally doubles on that basis.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier to 120%, and the damage multiplier bonus per stack of Blade Resonance consumed is increased to 20%."
          }
        ],
        "icon": "assets/Phaetusa/Twin paradise.png"
      },
      {
        "name": "Companionship",
        "traits": [
          "Passive",
          "Active",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Gains 1 point of Confectance Index each time Melee damage is dealt. This effect can be activated three times per round.\nWhen an enemy within range takes damage from an allied AoE attack, performs a Action support on that target, dealing AoE Melee Corrosion damage equal to 90% ATK and 1 point of Stability damage. This effect can be activated three times per round.\nAfter activation the skill Mirror Trap, active skill Companionship becomes available. Upon activation, gains the effects of True Form and Extra Command. Can be used once per battle.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases the number of times Companionship can be used per battle by 1. After gaining the effect of True Form, increases ATK by 50% for 1 round."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases Action support damage multiplier to 120%. During the current turn, each Support Action performed increases movement range by 1 tile."
          }
        ],
        "icon": "assets/Phaetusa/Companionship.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Mirror Trap",
        "level": "2",
        "effect": "Every 2 times of skill usage Phaetusa will gain an additional stack of Blade Resonance, and her critical damage will be permanently increased by 15%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Descent of twin wings",
        "level": "2",
        "effect": "Increases damage multiplier to 120% and width increases by 2 tiles."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Companionship",
        "level": "2",
        "effect": "Increases the number of times Companionship can be used per battle by 1. After gaining the effect of True Form, increases ATK by 50% for 1 round."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Twin paradise",
        "level": "2",
        "effect": "Increases damage multiplier to 120%, and the damage bonus per stack of Blade Resonance consumed is increased to 20%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Companionship",
        "level": "3",
        "effect": "Increases Support Action damage multiplier to 120%. During the current turn, each Support Action performed increases movement range by 1 tile."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Mirror Trap",
        "level": "3",
        "effect": "After using skill usage Phaetusa will gain new buff: Tempered Blood - increases multiplier of next active attack by 200%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Frosted Veins",
        "level": "20",
        "keyName": "Fixed Key 1 - Frosted Veins",
        "description": "Upon first reaching the maximum stacks of Blade Resonance, increases Critical Rate by 20%.",
        "icon": "assets/Phaetusa/Fixed Key 1 - Frosted Veins.png"
      },
      {
        "node": "Fixed Key 2 - Drifter’s Resolve",
        "level": "20",
        "keyName": "Fixed Key 2 - Drifter’s Resolve",
        "description": "At the start of the turn, applies Laceration to all enemies on the field for 1 turn. Can trigger once every 2 turns.",
        "icon": "assets/Phaetusa/Fixed Key 2 - Drifter’s Resolve.png"
      },
      {
        "node": "Fixed Key 3 - Blade of Doom",
        "level": "30",
        "keyName": "Fixed Key 3 - Blade of Doom",
        "description": "If the active attack hits only one enemy target, damage dealt to it is increased by 15%.",
        "icon": "assets/Phaetusa/Fixed Key 3 - Blade of Doom.png"
      },
      {
        "node": "Fixed Key 4 - Gift of Vitality",
        "level": "30",
        "keyName": "Fixed Key 4 - Gift of Vitality",
        "description": "For each stack of Blade Resonance consumed, restores HP equal to 10% ATK and 1 point of Stability.",
        "icon": "assets/Phaetusa/Fixed Key 4 - Gift of Vitality.png"
      },
      {
        "node": "Fixed Key 5 - Keeper of the Boundary",
        "level": "40",
        "keyName": "Fixed Key 5 - Keeper of the Boundary",
        "description": "Before performing an Support Action, dispels 1 buff from the target.",
        "icon": "assets/Phaetusa/Fixed Key 5 - Keeper of the Boundary.png"
      },
      {
        "node": "Fixed Key 6 - Hunter's Acuity",
        "level": "40",
        "keyName": "Fixed Key 6 - Hunter's Acuity",
        "description": "After activation the skill Mirror Trap, gains Additional Movement of 6 tiles.",
        "icon": "assets/Phaetusa/Fixed Key 6 - Hunter's Acuity.png"
      },
      {
        "node": "Affinity Key -  Integrated dual core",
        "level": "-",
        "keyName": "Affinity Key -  Integrated dual core",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Phaetusa/Affinity Key -  Integrated dual core.png"
      },
      {
        "node": "Common Key - Void Genesis",
        "level": "40",
        "keyName": "Common Key - Void Genesis",
        "description": "CRIT +5.0% / If the Confectance Index equals 0 during the current round, damage dealt is increased by 10%.",
        "icon": "assets/Phaetusa/Common Key - Void Genesis.png"
      }
    ]
  },
  "Sakura": {
    "class": "Vanguard",
    "stats": {
      "hp": 1754,
      "atk": 774,
      "def": 528
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Light Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Sakura Chime",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Sakura/Sakura Chime.png"
      },
      {
        "name": "Falling Blossom",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Burn",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "Full map",
        "effArea": "2",
        "description": "Selects an empty tile within a 2-tile radius of a friendly Doll or an enemy affected by Sakura Mark, then jumps to that tile, dealing AoE Burn damage equal to 60% ATK to all enemies within a 2-tile radius. Grants Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases range by 1 tile; increases effective area by 1 tile; increases damage multiplier by 15%; reduces Confectance Index consumption by 1 point."
          }
        ],
        "icon": "assets/Sakura/Falling Blossom.png"
      },
      {
        "name": "Misfortune Delivery",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Burn damage equivalent to 130% ATK to it, and applies 2 stacks of Sakura Mark.\nBefore attacking, additionally applies Bad Luck to the target for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases the number of Sakura Mark stacks applied to 3; increases the damage bonus from Bad Luck to 30%."
          }
        ],
        "icon": "assets/Sakura/Misfortune Delivery.png"
      },
      {
        "name": "Grand Isekai Adventure",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Burn",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects one direction and applies 3 stacks of Sakura Mark to all enemies within a 3×10 tile area in front, dealing AoE Burn damage equal to 90% ATK.\nAfter using this skill, triggers the effect of Sakura Mark, and gains Good Luck for 2 turns and 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the damage multiplier by 30%; expands the effective area to a 5×10 tile zone in front; stack this effect to the limit on all enemy units across the entire field affected by Sakura Mark"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Good Luck gains an additional effect:\nBefore a friendly unit performs an active attack or an out-of-turn attack (excluding the user), Sakura applies 1 stack of Sakura Mark to that target.\nCan trigger up to 3 times per turn."
          }
        ],
        "icon": "assets/Sakura/Grand Isekai Adventure.png"
      },
      {
        "name": "Ferlicitous Prayer",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, gains Thermal Conduction. When triggering the effect of Sakura Mark and if the ultimate skill Grand Isekai Adventure has not been used, gains 2 stacks of Searing Flame. At the start of each turn, gains 2 points of Confectance Index and applies 2 stacks of Sakura Mark to 3 random enemies on the field. If Sakura has Good Luck, her damage is increased by 20%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Randomly applies Sakura Mark to up to 5 enemies; the damage multiplier of Sakura Mark increases to 90%, and its effective radius increases by 1 tile.\nIf an enemy unit is standing on a Burn-type tile, damage dealt by Sakura Mark is increased by 30%."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If the user has Good Luck, increases damage dealt by 50% and Critical Damage by 25%.\nWhen an enemy gains Sakura Mark, creates Incineration tiles within a 1-tile radius around it for 3 turns; when Sakura Mark deals damage, it ignores 15% of the target’s DEF"
          }
        ],
        "icon": "assets/Sakura/Ferlicitous Prayer.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Ferlicitous Prayer",
        "level": "2",
        "effect": "Randomly applies Sakura Mark to up to 5 enemies; the damage multiplier of Sakura Mark increases to 90%, and its effective radius increases by 1 tile.\nIf an enemy unit is standing on a Burn-type tile, damage dealt by Sakura Mark is increased by 30%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Falling Blossom",
        "level": "2",
        "effect": "Increases range by 1 tile; increases effective area by 1 tile; increases damage multiplier by 15%; reduces Confectance Index consumption by 1 point."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Ferlicitous Prayer",
        "level": "2",
        "effect": "If the user has Good Luck, increases damage dealt by 50% and Critical Damage by 25%.\nWhen an enemy gains Sakura Mark, creates Incineration tiles within a 1-tile radius around it for 3 turns; when Sakura Mark deals damage, it ignores 15% of the target’s DEF"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Misfortune Delivery",
        "level": "2",
        "effect": "Increases the number of Sakura Mark stacks applied to 3; increases the damage bonus from Bad Luck to 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Grand Isekai Adventure",
        "level": "3",
        "effect": "Increases the damage multiplier by 30%; expands the effective area to a 5×10 tile zone in front; stack this effect to the limit on all enemy units across the entire field affected by Sakura Mark."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Grand Isekai Adventure",
        "level": "3",
        "effect": "Good Luck gains an additional effect:\nBefore a friendly unit performs an active attack or an out-of-turn attack (excluding the user), Sakura applies 1 stack of Sakura Mark to that target.\nCan trigger up to 3 times per turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Hard Work and Guts",
        "level": "20",
        "keyName": "Fixed Key 1 - Hard Work and Guts",
        "description": "At the start of battle, applies 1 stack of Sakura Mark to any 3 enemy units on the field.",
        "icon": "assets/Sakura/Fixed Key 1 - Hard Work and Guts.png"
      },
      {
        "node": "Fixed Key 2 - Just In Time Logistic",
        "level": "20",
        "keyName": "Fixed Key 2 - Just In Time Logistic",
        "description": "When applying Sakura Mark with a non-Ultimate skill, also applies Overburn for 1 turn.",
        "icon": "assets/Sakura/Fixed Key 2 - Just In Time Logistic.png"
      },
      {
        "node": "Fixed Key 3 - Apologize From The Heart",
        "level": "30",
        "keyName": "Fixed Key 3 - Apologize From The Heart",
        "description": "When applying Bad Luck, dispels 1 buff from the target.",
        "icon": "assets/Sakura/Fixed Key 3 - Apologize From The Heart.png"
      },
      {
        "node": "Fixed Key 4 - Jinxed by Nature",
        "level": "30",
        "keyName": "Fixed Key 4 - Jinxed by Nature",
        "description": "At the start of battle, applies Bad Luck to the enemy unit with the highest HP on the field for 3 turns.",
        "icon": "assets/Sakura/Fixed Key 4 - Jinxed by Nature.png"
      },
      {
        "node": "Fixed Key 5 - Flying Solo",
        "level": "40",
        "keyName": "Fixed Key 5 - Flying Solo",
        "description": "At the end of the action, if there are enemy units within a 3-tile radius, gains 1 stack of Quick Barrier.",
        "icon": "assets/Sakura/Fixed Key 5 - Flying Solo.png"
      },
      {
        "node": "Fixed Key 6 - Improving Everyday",
        "level": "40",
        "keyName": "Fixed Key 6 - Improving Everyday",
        "description": "When an enemy affected by Sakura Mark dies, increases self ATK by 4%, up to a maximum of 20%.",
        "icon": "assets/Sakura/Fixed Key 6 - Improving Everyday.png"
      },
      {
        "node": "Affinity Key - Mission Accomplished",
        "level": "-",
        "keyName": "Affinity Key - Mission Accomplished",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Sakura/Affinity Key - Mission Accomplished.png"
      },
      {
        "node": "Common Key - Ace Courier",
        "level": "40",
        "keyName": "Common Key - Ace Courier",
        "description": "CRIT +5.0% / Increases AOE damage dealt to enemy targets with debuffs by 10%.",
        "icon": "assets/Sakura/Common Key - Ace Courier.png"
      }
    ]
  },
  "Loreley": {
    "class": "Support",
    "stats": {
      "hp": 1948,
      "atk": 784,
      "def": 536
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Heavy Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Light Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Disciplinary Prelude",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Skill ignores 30% of the target's defense. If the target is on a Incineration tile, the damage dealt is increased by 60%."
          }
        ],
        "icon": "assets/Loreley/Disciplinary Prelude.png"
      },
      {
        "name": "Sultry Promise",
        "traits": [
          "Active",
          "AoE",
          "Tile"
        ],
        "attribute": "Burn",
        "stabilityDamage": 1,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "4",
        "effArea": "Self",
        "description": "Deals AoE Burn damage equivalent to 120% ATK to all enemies within a 4 tile radius. The total damage is evenly distributed among all targets within the area. If Loreley has Glowing Embers, the damage will not be evenly split, and Incineration tiles will be generated for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier by 30% and increases the effective range by 1 tile.\nFor each Burn buff Loreley has, the damage dealt is increased by 10%, up to a maximum of 40%."
          }
        ],
        "icon": "assets/Loreley/Sultry Promise.png"
      },
      {
        "name": "Pain's Benediction",
        "traits": [
          "AoE",
          "Buff",
          "Tile",
          "Summon"
        ],
        "attribute": "Burn",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "5",
        "effArea": "3",
        "description": "Selects an open tile within a 5 tile radius, summons Hunter - Type II on it, deals 90% ATK AoE Burn damage to all enemies within 3 tiles around it and generates Incineration tiles within 3 tiles for 2 turns. If Hunter - Type II is already present on the field, it is resummoned at the new location. CleanseTaunt from all allied units. Applies Symbiotic Dance to Loreley and the closest allied Doll, preventing death when taking lethal damage. If another ally dies while this effect is active, the protected unit will die in its place.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "New Symbiotic Dance effect: when lethal damage taken, restore 25% of your maximum health and 5 Stability Index, cleanse all debuffs and reduce the damage taken within 1 round by 60%.\nAfter using general attack or active skills, the Hunter - Type II releases an additional Pyro Pulse.\nAdditionally dispels Stun from all allied units."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Hunter - Type II generates an additional 4 Searing Flame when summoned.\nThe damage coefficient of the Pyro Pulse is doubled, and for every Pyro Pulse released, the damage caused by Loreley is increased by 10%, up to 60%; critical damage is increased by 2%, up to 12%.\nApply Flawless Blaze to all friendly units."
          }
        ],
        "icon": "assets/Loreley/Pain's Benediction.png"
      },
      {
        "name": "Queen's Endowment",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Damage dealt by all Dolls who use Sniper Rifles is increased by 10%.\nAt the start of battle, gains Thermal Conduction. When Loreley is on the field, Embers from Thermal Conduction is upgraded into Glowing Embers, which lasts for 2 global rounds.\nAt the start of the round, Loreley gains 2 points of Confectance Index. At the end of her action, if Hunter - Type II is present, Loreley also gains Additional Command. Can be triggered once per round.\nBefore an allied unit takes damage, Loreley grants them Flawless Blaze, allowing them to nullify that instance of damage. Can be triggered up to 3 times per round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The number of times Flawless Blaze can be applied is increased to 5 times.\nAdditional Command is replaced by Extra Action.\nGlowing Embers no longer increase Burn damage, but instead increase all damage caused by 45%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Searing Flame earned by all friendly units when Loreley is present are increased by an additional 1 point. For every Burn Doll on the field, Loreley ATK is increased by 6%.\nThe ATK of the Infernal Surge applied by the Hunter - Type II has been increased to 12%.\nIncreased effect of Glowing Embers: Damage reduction increased to 30%."
          }
        ],
        "icon": "assets/Loreley/Queen's Endowment.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Pain's Benediction",
        "level": "2",
        "effect": "New Symbiotic Dance effect: when lethal damage taken, restore 25% of your maximum health and 5 Stability Index, cleanse all debuffs and reduce the damage taken within 1 round by 60%.\nAfter using general attack or active skills, the Hunter - Type II releases an additional Pyro Pulse.\nAdditionally dispels Stun from all allied units."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Queen's Endowment",
        "level": "2",
        "effect": "The number of times Flawless Blaze can be applied is increased to 5 times.\nAdditional Command is replaced by Extra Action.\nGlowing Embers no longer increase Burn damage, but instead increase all damage caused by 45%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Pain's Benediction",
        "level": "3",
        "effect": "Hunter - Type II generates an additional 4 Searing Flame when summoned.\nThe damage coefficient of the Pyro Pulse is doubled, and for every Pyro Pulse released, the damage caused by Loreley is increased by 10%, up to 60%; critical damage is increased by 2%, up to 12%.\nApply Flawless Blaze to all friendly units."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Sultry Promise",
        "level": "2",
        "effect": "Increases damage multiplier by 30% and increases the effective range by 1 tile.\nFor each Burn buff Loreley has, the damage dealt is increased by 10%, up to a maximum of 40%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Burning Touch",
        "level": "2",
        "effect": "Skill ignores 30% of the target's defense. If the target is on a Incineration tile, the damage dealt is increased by 60%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Queen's Endowment",
        "level": "3",
        "effect": "Searing Flame earned by all friendly units when Loreley is present are increased by an additional 1 point. For every Burn Doll on the field, Loreley ATK is increased by 6%.\nThe ATK of the Infernal Surge applied by the Hunter - Type II has been increased to 12%.\nIncreased effect of Glowing Embers: Damage reduction increased to 30%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Hidden Passion",
        "level": "20",
        "keyName": "Fixed Key 1 - Hidden Passion",
        "description": "At the start of the battle, Loreley gains 1 Confectance Index and 10 Searing Flame",
        "icon": "assets/Loreley/Fixed Key 1 - Hidden Passion.png"
      },
      {
        "node": "Fixed Key 2 - Pain Threshold",
        "level": "20",
        "keyName": "Fixed Key 2 - Pain Threshold",
        "description": "When Hunter - Type II passive skill Pyro Pulse deals damage, applies Overburn to the target for 1 turn.",
        "icon": "assets/Loreley/Fixed Key 2 - Pain Threshold.png"
      },
      {
        "node": "Fixed Key 3 - Intertwined Dreams",
        "level": "30",
        "keyName": "Fixed Key 3 - Intertwined Dreams",
        "description": "While Hunter - Type II is on the field, all allied unit's Burn damage is increased by 7%.",
        "icon": "assets/Loreley/Fixed Key 3 - Intertwined Dreams.png"
      },
      {
        "node": "Fixed Key 4 - The Gentleness of an Angel",
        "level": "30",
        "keyName": "Fixed Key 4 - The Gentleness of an Angel",
        "description": "Before using an active attack, dispel one target's buff",
        "icon": "assets/Loreley/Fixed Key 4 - The Gentleness of an Angel.png"
      },
      {
        "node": "Fixed Key 5 - The Stride of a Devil",
        "level": "40",
        "keyName": "Fixed Key 5 - The Stride of a Devil",
        "description": "At the start of the battle, Loreley gains Movement Up III",
        "icon": "assets/Loreley/Fixed Key 5 - The Stride of a Devil.png"
      },
      {
        "node": "Fixed Key 6 - Absolute Subjugator",
        "level": "40",
        "keyName": "Fixed Key 6 - Absolute Subjugator",
        "description": "When a normal ELID enemy unit ends its action while standing within a radius of 3 tiles to Hunter - Type II, it is instantly executed. (Executions via this mechanic does not deal damage)",
        "icon": "assets/Loreley/Fixed Key 6 - Absolute Subjugator.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Loreley/Affinity Key.png"
      },
      {
        "node": "Common Key - Smoldering Breath",
        "level": "40",
        "keyName": "Common Key - Smoldering Breath",
        "description": "ATK +5.0% / When the user has a Burn-type buff, critical rate is increased by 10%",
        "icon": "assets/Loreley/Common Key - Smoldering Breath.png"
      }
    ]
  },
  "Harpsy": {
    "class": "Vanguard",
    "stats": {
      "hp": 1754,
      "atk": 757,
      "def": 545
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Light Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Targeted attack ♂Dominant Aim♂",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Harpsy/Targeted attack ♂Dominant Aim♂.png"
      },
      {
        "name": "Wide area Boost ♂Wide Muscle Boost♂",
        "traits": [
          "Active"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 ally target within 6 tiles and apply an Alpha Process to them for 2 global rounds, and extend the Alpha Process held by all ally targets by 1 global rounds. After the skill usage, Harpsy gains Extra Command. If the target already had Alpha Process, Harpsy recovers 3 points of Confectance Index. This skill can be used up to 1 time per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Reduces the cost of the Confectance Index by 1 point, and increases the number of times it can be used by 1 per turn."
          }
        ],
        "icon": "assets/Harpsy/Wide area Boost ♂Wide Muscle Boost♂.png"
      },
      {
        "name": "Beat poison with poison ♂Swallow My Virus♂",
        "traits": [
          "Active",
          "Aoe",
          "Debuff",
          "Displacement"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, deals Aoe Corrosion damage equal to 90% of attack, knocks the target back by 3 tiles and apply 2 stacks of Kill Process.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage multiplier increased to 120%.\nKill Process effect has been upgraded: after the holder dies, the number of effect stacks will be transferred to a random friendly unit"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Kill Process effect has been upgraded: consuming 70% of the stacks (rounded up) when it takes effect, and the damage multiplier of each layer is increased to 30%."
          }
        ],
        "icon": "assets/Harpsy/Beat poison with poison ♂Swallow My Virus♂.png"
      },
      {
        "name": "Online punch ゴStarForce Platinumゴ",
        "traits": [
          "Ultimate",
          "Aoe"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals AOE Corrosion damage equal to 90% of attack to them. If the number of friendly Dolls holding the Alpha Process on the field is greater than 2, the damage dealt by the Kill Process is increased by 30% for 1 global round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If Harpsy has more than 3 Confectance Index, consume all Confectance Index, and increase the damage multiplier by 20% for each additional Confectance Index consumed."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage multiplier increased to 120%.\nNew effect has been added: when there is a friendly Doll with the Alpha Process on the field, the damage multiplier of this skill is doubled."
          }
        ],
        "icon": "assets/Harpsy/Online punch ゴStarForce Platinumゴ.png"
      },
      {
        "name": "Macro virus ♂Virus Master♂",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Self",
        "description": "After an active attack Harpsy recovers 2 points of Confectance Index.\nFor every 1 Confectance Index spent with a Ultimate skill, the effect of 1 Alpha Process is triggered.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "For each trigger of the Alpha Process, increases your ATK and Critical Damage by 3%, up to a maximum of 15%."
          }
        ],
        "icon": "assets/Harpsy/Macro virus ♂Virus Master♂.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Wide area Boost ♂Wide Muscle Boost♂",
        "level": "2",
        "effect": "Reduces the cost of the Confectance Index by 1 point, and increases the number of times it can be used by 1 per turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Online punch ゴStarForce Platinumゴ",
        "level": "2",
        "effect": "If Harpsy has more than 3 Confectance Index, consume all Confectance Index, and increase the damage multiplier by 20% for each additional Confectance Index consumed."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Macro virus ♂Virus Master♂",
        "level": "2",
        "effect": "For each trigger of the Alpha Process, increases your ATK and Critical Damage by 3%, up to a maximum of 15%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Beat poison with poison ♂Swallow My Virus♂",
        "level": "2",
        "effect": "Damage multiplier increased to 120%.\nKill Process effect has been upgraded: after the holder dies, the number of effect stacks will be transferred to a random friendly unit"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Online punch ゴStarForce Platinumゴ",
        "level": "3",
        "effect": "Damage multiplier increased to 120%.\nNew effect has been added: when there is a friendly Doll with a Alpha Process on the field, the damage multiplier of this skill is doubled."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Beat poison with poison ♂Swallow My Virus♂",
        "level": "3",
        "effect": "Kill Process effect has been upgraded: consuming 70% of the stacks (rounded up) when it takes effect, and the damage multiplier of each layer is increased to 30%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Portable Relay Unit",
        "level": "20",
        "keyName": "Fixed Key 1 - Portable Relay Unit",
        "description": "After using the active skill Wide area Boost ♂Wide Muscle Boost♂, Harpsy gains 6 tiles of Additional Movement.",
        "icon": "assets/Harpsy/Fixed Key 1 - Portable Relay Unit.png"
      },
      {
        "node": "Fixed Key 2 - Brutal Overhaul",
        "level": "20",
        "keyName": "Fixed Key 2 - Brutal Overhaul",
        "description": "When the Kill Process is applied, additionally apply Retrograde for 1 turn.",
        "icon": "assets/Harpsy/Fixed Key 2 - Brutal Overhaul.png"
      },
      {
        "node": "Fixed Key 3 - Backup Strategy",
        "level": "30",
        "keyName": "Fixed Key 3 - Backup Strategy",
        "description": "After their own actions are over, allies holding Alpha Process will receive Movement Up II for 1 turn.",
        "icon": "assets/Harpsy/Fixed Key 3 - Backup Strategy.png"
      },
      {
        "node": "Fixed Key 4 - Ally’s Power",
        "level": "30",
        "keyName": "Fixed Key 4 - Ally’s Power",
        "description": "For every ally holding the Alpha Process on the field, each stack of Kill Process damage multiplier is increased by 2% when activated.",
        "icon": "assets/Harpsy/Fixed Key 4 - Ally’s Power.png"
      },
      {
        "node": "Fixed Key 5 - Courage Unleashed",
        "level": "40",
        "keyName": "Fixed Key 5 - Courage Unleashed",
        "description": "After using the active skill Wide area Boost ♂Wide Muscle Boost♂ ally holding the Alpha Process, their critical strike rate is increased by 20% for 1 large round.",
        "icon": "assets/Harpsy/Fixed Key 5 - Courage Unleashed.png"
      },
      {
        "node": "Fixed Key 6 - \r\nDistance Listen-In",
        "level": "40",
        "keyName": "Fixed Key 6 - \r\nDistance Listen-In",
        "description": "Increases the range of active skills and basic attacks by 2 tiles.",
        "icon": "assets/Harpsy/Fixed Key 6 - \r\nDistance Listen-In.png"
      },
      {
        "node": "Affinity Key - Coward's distress",
        "level": "-",
        "keyName": "Affinity Key - Coward's distress",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Harpsy/Affinity Key - Coward's distress.png"
      },
      {
        "node": "Common Key - Dependable Tech Tips",
        "level": "40",
        "keyName": "Common Key - Dependable Tech Tips",
        "description": "CRIT +5.0% / After applying a debuff, the damage dealt is increased by 10% for 1 large turn.",
        "icon": "assets/Harpsy/Common Key - Dependable Tech Tips.png"
      }
    ]
  },
  "Cheyanne": {
    "class": "Sentinel",
    "stats": {
      "hp": 1924,
      "atk": 845,
      "def": 512
    },
    "stabilityGauge": 9,
    "movementSpeed": 4,
    "skillAttributes": [
      "Heavy Ammo"
    ],
    "weaknesses": [
      "Light Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Playing to Potential",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Full map",
        "effArea": "Target",
        "description": "Selects 1 enemy target within the entire field and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Cheyanne/Playing to Potential.png"
      },
      {
        "name": "Wall of One's Self",
        "traits": [
          "Active",
          "Tile"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Cheyanne gains Sepal of Shyness and 1 instance of Extra Command.\n\nUpon receiving lethal damage while holding Sepal of Shyness, Cheyanne will not be defeated, instead deploying Smoke tiles in 1 tile radius around her position for 1 turn. When standing in these Smoke tiles, Cheyanne becomes invincible. Can be triggered once per battle.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "For every 1 round under Sepal of Shyness, Cheyanne will gain a stack of Sense of Security at the end of the round.\nThe duration of the Smoke tiles is increased to 2 turns, and the range is increased by 1 tile.\nThe cooldown time is reduced by 2 turns."
          }
        ],
        "icon": "assets/Cheyanne/Wall of One's Self.png"
      },
      {
        "name": "Steadfast Pursuit",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Full map",
        "effArea": "Target",
        "description": "Selects 1 enemy target within the entire field, apply Bullseye to them and deal Physical damage equal to 80% of attack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Bullseye effect improved: Defense reduction increased to 100%; when attacked by Cheyanne, Analytical Value is no longer consumed."
          }
        ],
        "icon": "assets/Cheyanne/Steadfast Pursuit.png"
      },
      {
        "name": "Piercing the Clouds, Into the Sun",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "Full map",
        "effArea": "Target",
        "description": "Selects 1 enemy target within the entire field, dealing Physical damage equal to 200% of attack and reset its Analytical Value. If the target holds a Bullseye, critical damage is increased by 30%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The damage multplier increased to 280%. If the target holds a Bullseye, ignore 50% of its DEF."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage multplier increased to 330%. When dealing damage, if there are 3 or fewer enemy units with Analytical Value less than 50% on the field, damage multplier increases to 380%."
          }
        ],
        "icon": "assets/Cheyanne/Piercing the Clouds, Into the Sun.png"
      },
      {
        "name": "Meticulous Planning",
        "traits": [
          "Passive",
          "Targeted"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "When an enemy unit completes its turn, Cheyanne triggers Think Before You Act, dealing Physical damage equal to 120% of attack and 2 points of Stability damage to the enemy, and increasing Confectance Index by 1. If the target’s Analytical Value  exceeds 50%, the damage multiplier of this attack is increased to 180%. Can be triggered up to 2 times per round.\n\nApply 100% of Analytical Value to all enemy units at the start of the battle.\n\nDamage to flying units increased by 20%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "For every 10% of Analytical Value held by the target when dealing damage, critical damage is increased by 5%.\nThe effect of Analytical Value is improved: The effect of ignoring the target Stability Index was increased to 10 points and 5 points respectively."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Damage multplier of Think Before You Act increased to 160%. If damage was dealt to enemy units with Analytical Value greater than or equal to 50% this turn, the damage multplier increases to 220%.\nWhen Think Before You Act deals damage, gain 1 stack of Accumulated Preheat, at most 1 time per turn."
          }
        ],
        "icon": "assets/Cheyanne/Meticulous Planning.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Meticulous Planning",
        "level": "2",
        "effect": "For every 10% of Analytical Value held by the target when dealing damage, critical damage is increased by 5%.\nThe effect of Analytical Value is improved: The effect of ignoring the target Stability Index was increased to 10 points and 5 points respectively."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Piercing the Clouds, Into the Sun",
        "level": "2",
        "effect": "The damage multplier increased to 280%. If the target holds a Bullseye, ignore 50% of its DEF."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Steadfast Pursuit",
        "level": "2",
        "effect": "Bullseye effect improved: Defense reduction increased to 100%; when attacked by Cheyanne, Analytical Value is no longer consumed."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Wall of One's Self",
        "level": "2",
        "effect": "For every 1 round under Sepal of Shyness, Cheyanne will gain a stack of Sense of Security at the end of the round.\nThe duration of the Smoke tiles is increased to 2 turns, and the range is increased by 1 tile.\nThe cooldown time is reduced by 2 turns."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Piercing the Clouds, Into the Sun",
        "level": "3",
        "effect": "Damage multplier increased to 330%. When dealing damage, if there are 3 or fewer enemy units with Analytical Value less than 50% on the field, damage multplier increases to 380%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Meticulous Planning",
        "level": "3",
        "effect": "Damage multplier of Think Before You Act increased to 160%. If damage was dealt to enemy units with Analytical Value greater than or equal to 50% this turn, the damage multplier increases to 220%.\nWhen Think Before You Act deals damage, gain 1 stack of Accumulated Preheat, at most 1 time per turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Don't Approach, I'm Shy",
        "level": "20",
        "keyName": "Fixed Key 1 - Don't Approach, I'm Shy",
        "description": "When dealing Targeted Damage, knock back the target by 2 tiles and apply Movement Down II for 2 turns.",
        "icon": "assets/Cheyanne/Fixed Key 1 - Don't Approach, I'm Shy.png"
      },
      {
        "node": "Fixed Key 2 - The Free Me",
        "level": "20",
        "keyName": "Fixed Key 2 - The Free Me",
        "description": "Cheyanne becomes immune to Taunt, Infatuated, and Fear debuffs.\nEvery 3 turns, grants immunity to AoE damage.",
        "icon": "assets/Cheyanne/Fixed Key 2 - The Free Me.png"
      },
      {
        "node": "Fixed Key 3 - A Brave Little Step",
        "level": "30",
        "keyName": "Fixed Key 3 - A Brave Little Step",
        "description": "At the start of battle, Mobility increased by 2 tiles, lasting 1 turn. Create 1 High Ground in the nearest empty tile around self.",
        "icon": "assets/Cheyanne/Fixed Key 3 - A Brave Little Step.png"
      },
      {
        "node": "Fixed Key 4 - Antisocial",
        "level": "30",
        "keyName": "Fixed Key 4 - Antisocial",
        "description": "When an enemy unit holding Bullseye dies, apply Bullseye to 1 enemy unit with the highest current HP on the field.",
        "icon": "assets/Cheyanne/Fixed Key 4 - Antisocial.png"
      },
      {
        "node": "Fixed Key 5 - Mental Resilience",
        "level": "40",
        "keyName": "Fixed Key 5 - Mental Resilience",
        "description": "Damage dealt to targets holding Bullseye is increased by 10%, and is treated as Heavy Ammo weakness.",
        "icon": "assets/Cheyanne/Fixed Key 5 - Mental Resilience.png"
      },
      {
        "node": "Fixed Key 6 - Full Attention",
        "level": "40",
        "keyName": "Fixed Key 6 - Full Attention",
        "description": "Every round, only when a target holding Bullseye ends action, release Think Before You Act once on them. Its damage multplier and Stability Damage are increased by sum of Think Before You Act casts available this turn (default is 2). Restore 2 points of Confectance Index. Max 1 trigger per turn.",
        "icon": "assets/Cheyanne/Fixed Key 6 - Full Attention.png"
      },
      {
        "node": "Affinity Key - Breathless Anticipation",
        "level": "-",
        "keyName": "Affinity Key - Breathless Anticipation",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Cheyanne/Affinity Key - Breathless Anticipation.png"
      },
      {
        "node": "Common Key - Love is a Long-Awaited Reunion",
        "level": "40",
        "keyName": "Common Key - Love is a Long-Awaited Reunion",
        "description": "ATK +5.0% / Damage dealt to targets with current HP greater than self is increased by 10%.",
        "icon": "assets/Cheyanne/Common Key - Love is a Long-Awaited Reunion.png"
      }
    ]
  },
  "Basti": {
    "class": "Support",
    "stats": {
      "hp": 1997,
      "atk": 731,
      "def": 522
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Reckless Provocation",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Basti/Reckless Provocation.png"
      },
      {
        "name": "Bad Influence",
        "traits": [
          "Active",
          "Teleport"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an ally within 6 tiles then selects 1 friendly Toxic Mist tile, teleport selected ally to that tile, restores HP equal to 100% of attack and 5 points of Stability Index for selected ally, cleanse 2 debuffs and apply Continuous Healing II for 2 turns for selected ally. Teleports Basti to an open space within 1 tile of the selected ally's location. After skill usage, Basti gains 6 tiles of Additional Movement.",
        "upgrades": [],
        "icon": "assets/Basti/Bad Influence.png"
      },
      {
        "name": "Landmine Gal",
        "traits": [
          "Active",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an open tile within a 6 tile radius and summons Cutie Pie on it. After skill usage, Basti can use active skills Landmine Gal, Bad Influence or her ultimate skill Sugar-Coated Trap. This skill can be used up to 2 times per turn.\n\nCutie Pie: A physical summoned unit that inherits Basti’s base attributes. If enemy targets are present within a 3-tile radius upon summoning, or if enemy targets spawn, end their action, or are passively displaced into the area, Cutie Pie self-destructs within the area, dealing AoE Corrosion damage equal to 100% ATK and 2 points of Stability damage, and creating a Toxic Mist tiles within the area for 2 turns. Additionally, applies Toxic Inundation and Stun to all enemy targets in the area for 2 turns, and restores HP equal to 80% ATK and 1 point of Stability Index to Basti. A maximum of 2 such summons can exist on the field at the same time.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increased range by 2 tiles. This skill can be used up to 3 times per turn.\nCutie Pie effect is enchanced: The effective range is increased to 5 tiles, maximum number of summons on the field has been increased to 3."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "After each Cutie Pie self-detonates, ATK of Basti and Cutie Pie is increased by 3%.\nCutie Pie effect is enchanced: Damage multiplier increased to 130%, and 1 random powerful debuff is applied when damage is dealt."
          }
        ],
        "icon": "assets/Basti/Landmine Gal.png"
      },
      {
        "name": "Sugar-Coated Trap",
        "traits": [
          "Ultimate",
          "AoE",
          "Tile",
          "Debuff"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "8",
        "description": "Selects 1 enemy target within 8 tiles and deals AoE Corrosion damage equal to 150% ATK to the target and all enemy targets within 8 tile radius around it, creates Toxic Mist tiles for 2 turns, and applies 1 stack of Grudge.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage multiplier increased to 200%.\nApply 2 additional layers of Alleviation Dependence.\nAfter the skill usage, restores 50% of Basti's ATK as HP of all friendly units, dispelling 2 debuffs."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Number of Grudge stacks applied is increased to 3 layers, and its damage multiplier is increased to 200%.\nFor each target hit, the damage dealt is increased by 20%, up to a maximum of 100%.\nAfter skill usage, additionally removes Infatuated and Stun from all allied units."
          }
        ],
        "icon": "assets/Basti/Sugar-Coated Trap.png"
      },
      {
        "name": "The World of Graffiti",
        "traits": [
          "Passive",
          "Tile",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "At the start of the turn, gains 1 point of Confectance Index.\nAt the start of battle, creates Toxic Mist tiles for 2 turns on the tiles where all allied Dolls are located. After moving, leaves Toxic Mist tiles within a 1-tile radius around herself for 2 turns.\nIf an enemy target is standing on an allied Toxic Mist tile, it gains Sloppy Grimace.\nWhen Cutie Pie is summoned and at the start of the turn, if allied units are on allied Toxic Mist tiles, they gain Mark of Comrades and Attack Up II for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Basti's stability damage taken is reduced by 1 point.\nAt the start of battle, creates Toxic Mist tiles for 2 turns on the tiles where all allied Dolls are located and within a 3×3 area around them. After moving, leaves Toxic Mist tiles within a 3-tile radius around herself for 2 turns.\nBefore dealing damage, the caster and Cutie Pie gain 1 stack of Energy Drink."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Energy Drink effect is enhanced: damage dealt increase per stack is increased to 24%, and healing done is increased to 6%.\nMark of Comrades effect is enhanced: damage dealt increase is increased to 30%.\nSloppy Grimace effect is enhanced: Corrosion damage taken increase is raised to 30%, and HP restored to the attacker when taking Corrosion damage is increased to 30% of the damage dealt."
          }
        ],
        "icon": "assets/Basti/The World of Graffiti.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Landmine Gal",
        "level": "2",
        "effect": "Increased range by 2 tiles. This skill can be used up to 3 times per turn.\nCutie Pie effect is enchanced: The effective range is increased to 5 tiles, maximum number of summons on the field has been increased to 3."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "The World of Graffiti",
        "level": "2",
        "effect": "Basti's stability damage taken is reduced by 1 point.\nAt the start of battle, creates Toxic Mist tiles for 2 turns on the tiles where all allied Dolls are located and within a 3×3 area around them. After moving, leaves Toxic Mist tiles within a 3-tile radius around herself for 2 turns.\nBefore dealing damage, the caster and Cutie Pie gain 1 stack of Energy Drink."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "The World of Graffiti",
        "level": "3",
        "effect": "Energy Drink effect is enhanced: damage dealt increase per stack is increased to 24%, and healing done is increased to 6%.\nMark of Comrades effect is enhanced: damage dealt increase is increased to 30%.\nSloppy Grimace effect is enhanced: Corrosion damage taken increase is raised to 30%, and HP restored to the attacker when taking Corrosion damage is increased to 30% of the damage dealt."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Sugar-Coated Trap",
        "level": "2",
        "effect": "Damage multiplier increased to 200%.\nApply 2 additional layers of Alleviation Dependence.\nAfter the skill usage, restores 50% of Basti's ATK as HP of all friendly units, dispelling 2 debuffs."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Sugar-Coated Trap",
        "level": "3",
        "effect": "Number of Grudge stacks applied is increased to 3 layers, and its damage multiplier is increased to 200%.\nFor each target hit, the damage dealt is increased by 20%, up to a maximum of 100%.\nAfter skill usage, additionally removes Infatuated and Stun from all allied units."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Landmine Gal",
        "level": "3",
        "effect": "After each Cutie Pie self-detonates, ATK of Basti and Cutie Pie is increased by 3%.\nCutie Pie effect is enchanced: Damage multiplier increased to 130%, and 1 random powerful debuff is applied when damage is dealt."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - A Moment of Inspiration",
        "level": "20",
        "keyName": "Fixed Key 1 - A Moment of Inspiration",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Basti/Fixed Key 1 - A Moment of Inspiration.png"
      },
      {
        "node": "Fixed Key 2 - Street Art",
        "level": "20",
        "keyName": "Fixed Key 2 - Street Art",
        "description": "While allied Toxic Mist tiles are present on the field, all allied units deal 7% increased Corrosion damage.",
        "icon": "assets/Basti/Fixed Key 2 - Street Art.png"
      },
      {
        "node": "Fixed Key 3 - Pain Dependency",
        "level": "30",
        "keyName": "Fixed Key 3 - Pain Dependency",
        "description": "When Fear, Taunt, Infatuated, Stun, or Immobilize is applied, the effect is immediately removed; this can trigger up to once per battle.\nAt the start of battle, gains Defense Up III for 3 turns.",
        "icon": "assets/Basti/Fixed Key 3 - Pain Dependency.png"
      },
      {
        "node": "Fixed Key 4 - Genius of Calamity",
        "level": "30",
        "keyName": "Fixed Key 4 - Genius of Calamity",
        "description": "When Cutie Pie is summoned, restores HP equal to 100% ATK and 2 points of Stability Index to the allied target with the lowest current HP on the field; this can trigger up to once per turn.",
        "icon": "assets/Basti/Fixed Key 4 - Genius of Calamity.png"
      },
      {
        "node": "Fixed Key 5 - Scary Gift",
        "level": "40",
        "keyName": "Fixed Key 5 - Scary Gift",
        "description": "Before attacking, Cutie Pie dispels 1 buff from the target.",
        "icon": "assets/Basti/Fixed Key 5 - Scary Gift.png"
      },
      {
        "node": "Fixed Key 6 - Love Smear",
        "level": "40",
        "keyName": "Fixed Key 6 - Love Smear",
        "description": "When Cutie Pie is summoned, creates a Toxic Mist tile on its current tile.",
        "icon": "assets/Basti/Fixed Key 6 - Love Smear.png"
      },
      {
        "node": "Affinity Key - Hat Trick",
        "level": "-",
        "keyName": "Affinity Key - Hat Trick",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Basti/Affinity Key - Hat Trick.png"
      },
      {
        "node": "Common Key - Deadly Possessiveness",
        "level": "40",
        "keyName": "Common Key - Deadly Possessiveness",
        "description": "CRIT +5.0% / If an enemy target is standing on a Corrosion-type tile, phase damage dealt to them is increased by 10%.",
        "icon": "assets/Basti/Common Key - Deadly Possessiveness.png"
      }
    ]
  },
  "Sextans": {
    "class": "Support",
    "stats": {
      "hp": 2014,
      "atk": 740,
      "def": 536
    },
    "stabilityGauge": 9,
    "movementSpeed": 9,
    "skillAttributes": [
      "Melee",
      "Electric"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Dreamscape Garrote",
        "traits": [
          "Basic Attack",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "Target",
        "description": "Selects 1 target within 1 tile, dealing melee Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Sextans/Dreamscape Garrote.png"
      },
      {
        "name": "Sanctuary Lauds",
        "traits": [
          "Active",
          "Aoe",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals melee AoE Electric damage equivalent to 90% ATK to all enemies within a 3x9 frontal area in the selected direction and apply Blood Kiss. The damage multiplier of this skill is increased increased by 10% based on the number of Coagulation stacks possessed by Sextans. Restores HP equalt to 90% ATK to all ally units within the area. After skill usage, Sextans gains 6 tiles of Additional Movement and can use the active skill Death Knell.",
        "upgrades": [],
        "icon": "assets/Sextans/Sanctuary Lauds.png"
      },
      {
        "name": "Death Knell",
        "traits": [
          "Active",
          "AoE",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals melee AoE Electric damage equivalent to 90% ATK to all enemies within a 3x9 frontal area in the selected direction and generates Voltage tiles for 3 turns. The damage multiplier of this skill is increased increased by 10% based on the number of Coagulation stacks possessed by Sextans. Restores HP equalt to 90% ATK to all ally units within the area amd dispels 1 debuff from them. If the enemy target is afflicted with Blood Kiss, this skill deals an additional instance of melee Electric damage with the same multiplier after this skill resolves. Sextans gains Coagulation and removes the target's Blood Kiss. Additional stacks of Coagulation is gained based on the target's rank (Normal, Elite, Boss).",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If the skill hits an enemy target, user casts Blood Emblem at it once and grants 1 point of Confectance Index. After using the skill, the user gains 2 stacks of Coagulation."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage and healing multipliers are increased by 30%; one more debuff will be dispelled; Blood Kiss is no longer removed."
          }
        ],
        "icon": "assets/Sextans/Death Knell.png"
      },
      {
        "name": "Midnight Vesper",
        "traits": [
          "Ultimate",
          "AoE",
          "Melee",
          "Tile",
          "Debuff",
          "Buff"
        ],
        "attribute": "Melee",
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within a cross-shaped area of 4-8 tiles, landing on the selected tile and dealing melee AoE Electric melee damage equal to 120% of attack to all enemy targets on the path and apply Blood Kiss to them. Generates Voltage tiles for 3 turns. The damage multiplier of this skill is increased increased by 10% based on the number of Coagulation stacks possessed by Sextans. Before the skill resolves, apply Laceration to enemy targets within the effective area, lasting 2 turns; apply Holy Blood Mark to all ally units within the area, lasting 2 turns. After the skill, gain 6 tiles of Additional Movement and can use the active skill Death Knell.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Skill area width is increased by 2 tiles. The effect of Holy Blood Mark is enhanced, with the Stability damage and the amount of Stability Index ignored are increased by 5 points; when dealing Electric or Melee damage, damage is increased by 5% for each stack of Coagulation (only applies once when multiple conditions (Electric or Melee damage) are met)."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Before using the skill, apply Electric Boost II to all friendly units for 2 turns. After using the skill, gain Concealment for 2 turns."
          }
        ],
        "icon": "assets/Sextans/Midnight Vesper.png"
      },
      {
        "name": "Requiem",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Damage dealt is increased for all Dolls that use Blades by 10%. Mobility is increased by 1 tile for all Electric-attribute Dolls and all Dolls that use Blades (only applies once when multiple conditions (Electric or Melee) are met). When an enemy unit dies or suffers Stability Break, Sextans gains 1 stack of Coagulation. Based on the enemy unit's rank, Sextans gains additional stacks of Coagulation. When ally units (excluding Sextans) attacks with a Blade, consume 1 point of Confectance Index to unleash Blood Emblem. At the start of Sextans' turn, if her Confectance Index is not full, restore it to full. Applies Scarlet Insignia to enemy units ending their action on Electric-attributed tiles.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "All Electric-attribute Dolls and all Dolls that use Blades have their mobility is increased by 2 tiles (only applies once when multiple conditions (Electric or Melee) are met), and ignore enemy cover. The Coagulation effect is enhanced; the maximum conversion of extra Critical Rate into ATK, healing, and Critical Damage is increased to 45%. The Blood Emblem effect is enhanced; for each stack of Coagulation, the damage multiplier is increased to 4%. The Scarlet Insignia effect is enhanced; Melee damage taken is increased to 10%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "At the start of combat, gain 5 stacks of Coagulation, and the Critical Rate cap for Coagulation is increased to 75%. The damage multiplier of Blood Emblem is increased to 90%, ignoring 30% of the target's DEF when dealing damage. No longer consumes Confectance Index. When at full Confectance Index, all friendly units deal 15% increased Melee damage."
          }
        ],
        "icon": "assets/Sextans/Requiem.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Death Knell",
        "level": "2",
        "effect": "If the skill hits an enemy target, user casts Blood Emblem at it once and grants 1 point of Confectance Index. After using the skill, the user gains 2 stacks of Coagulation."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Midnight Vesper",
        "level": "2",
        "effect": "Skill area width is increased by 2 tiles. The effect of Holy Blood Mark is enhanced, with the Stability damage and the amount of Stability Index ignored are increased by 5 points; when dealing Electric or Melee damage, damage is increased by 5% for each stack of Coagulation (only applies once when multiple conditions (Electric or Melee damage) are met)."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Requiem",
        "level": "2",
        "effect": "All Electric-attribute Dolls and all Dolls that use Blades have their mobility is increased by 2 tiles (only applies once when multiple conditions (Electric or Melee) are met), and ignore enemy cover. The Coagulation effect is enhanced; the maximum conversion of extra Critical Rate into ATK, healing, and Critical Damage is increased to 45%. The Blood Emblem effect is enhanced; for each stack of Coagulation, the damage multiplier is increased to 4%. The Scarlet Insignia effect is enhanced; Melee damage taken is increased to 10% ."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Midnight Vesper",
        "level": "3",
        "effect": "Before using the skill, apply Electric Boost II to all friendly units for 2 turns. After using the skill, gain Concealment for 2 turns."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Death Knell",
        "level": "3",
        "effect": "Damage and healing multipliers are increased by 30%; one more debuff will be dispelled; Blood Kiss is no longer removed."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Requiem",
        "level": "3",
        "effect": "At the start of combat, gain 5 stacks of Coagulation, and the Critical Rate cap for Coagulation is increased to 75%. The damage multiplier of Blood Emblem is increased to 90%, ignoring 30% of the target's DEF when dealing damage. No longer consumes Confectance Index. When at full Confectance Index, all friendly units deal 15% increased Melee damage."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Contractor's Bond",
        "level": "20",
        "keyName": "Fixed Key 1 - Contractor's Bond",
        "description": "At the start of battle, Sextans gains 1 stack of Coagulation based on the number of Electric-attributed Dolls or Dolls using Blades on the field (only applies once when multiple conditions (Electric or Melee) are met).",
        "icon": "assets/Sextans/Fixed Key 1 - Contractor's Bond.png"
      },
      {
        "node": "Fixed Key 2 - Silent Inscription",
        "level": "20",
        "keyName": "Fixed Key 2 - Silent Inscription",
        "description": "Before an ally unit with Holy Blood Mark uses an active attack, inflicts Defense Down II to the target for 2 turns.",
        "icon": "assets/Sextans/Fixed Key 2 - Silent Inscription.png"
      },
      {
        "node": "Fixed Key 3 - Pocket Watch Calibration",
        "level": "30",
        "keyName": "Fixed Key 3 - Pocket Watch Calibration",
        "description": "Before Blood Emblem deals damage, cleanse 1 target's buff.",
        "icon": "assets/Sextans/Fixed Key 3 - Pocket Watch Calibration.png"
      },
      {
        "node": "Fixed Key 4 - Withering Oath",
        "level": "30",
        "keyName": "Fixed Key 4 - Withering Oath",
        "description": "Enemy units under Stability Break take 7% more damage",
        "icon": "assets/Sextans/Fixed Key 4 - Withering Oath.png"
      },
      {
        "node": "Fixed Key 5 - Keeper of the Boundary",
        "level": "40",
        "keyName": "Fixed Key 5 - Keeper of the Boundary",
        "description": "After an ally unit (excluding Sextans) attacks with a Blade, generates Voltage tiles within 1 tile radius around the target.",
        "icon": "assets/Sextans/Fixed Key 5 - Keeper of the Boundary.png"
      },
      {
        "node": "Fixed Key 6 - Black Swan's Feather",
        "level": "40",
        "keyName": "Fixed Key 6 - Black Swan's Feather",
        "description": "Increase stability damage dealt by all ally units by 1.",
        "icon": "assets/Sextans/Fixed Key 6 - Black Swan's Feather.png"
      },
      {
        "node": "Affinity Key -  Silent Echo",
        "level": "-",
        "keyName": "Affinity Key -  Silent Echo",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Sextans/Affinity Key -  Silent Echo.png"
      },
      {
        "node": "Common Key - Stigmata in the Palm",
        "level": "40",
        "keyName": "Common Key - Stigmata in the Palm",
        "description": "CRIT DMG +5.0% / Melee damage dealt is increased by 10%.",
        "icon": "assets/Sextans/Common Key - Stigmata in the Palm.png"
      }
    ]
  },
  "OTs-14": {
    "class": "Sentinel",
    "stats": {
      "hp": 1981,
      "atk": 802,
      "def": 553
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Omni"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Combat Instinct",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 target within 8 tiles, dealing Omni damage equal to 90% of attack to them.",
        "upgrades": [],
        "icon": "assets/OTs-14/Combat Instinct.png"
      },
      {
        "name": "Total Suppression",
        "traits": [
          "Active",
          "Aoe"
        ],
        "attribute": "Omni",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "3x3",
        "description": "Selects 1 tile within an 8-tile radius and deals AoE Omni Damage equal to 120% of attack to all enemy targets within a 3×3 area. If OTs-14 is under Cover Command, the damage accumulated by Command Mode is increased by 25% after skill usage. If OTs-14 is under Demolition Command, for every 15% initial Critical Damage, damage dealt is increased by 15%, and the damage multiplier is doubled.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases damage multiplier to 150%.\nThe effective area has been increased to 5×5 tiles.\nCooldown reduced by 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "If the user is under Cover Command, the increase to damage accumulated by Command Mode after skill usage is raised to 33%.\nIf the user is under Demolition Command, then for every 15% initial Critical Damage, the damage multiplier is increased by 15%."
          }
        ],
        "icon": "assets/OTs-14/Total Suppression.png"
      },
      {
        "name": "Perfect Adaptation",
        "traits": [
          "Active"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Switches Command Mode between Cover Command and Demolition Command. After skill usage, gains Extra Command. This skill can be used up to 3 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Cover Command effect enhanced: the increase to critical damage of all allied units except the user is raised to 15% of the user's initial Critical Damage.\nDemolition Command effect enhanced: the increase to the user's attack is raised to 15% of the initial attack of all allied Dolls except the user."
          }
        ],
        "icon": "assets/OTs-14/Perfect Adaptation.png"
      },
      {
        "name": "Blast Judgment",
        "traits": [
          "Ultimate"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction and applies Movement Down III to all enemy targets in front within a range of 3 to 10 tiles for 2 turns, then converts the damage accumulated by Command Mode into 1 point of Overload Burst and gains Reverse Assimilation for 1 turn. This skill can be used while under Demolition Command and having Overload Burst, or when the damage accumulated by Command Mode is greater than 0.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Reverse Assimilation effect enhanced: the damage of Critical Erosion is increased to 200%, and its effective range is increased by 2 tiles."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Reverse Assimilation effect enhanced: each time Critical Erosion is used during the current turn, the damage multiplier of Critical Erosion is increased by 50%, and the multiplier of the fixed damage dealt by consuming Overload Burst is increased by 10%."
          }
        ],
        "icon": "assets/OTs-14/Blast Judgment.png"
      },
      {
        "name": "Boojum Phenomenon",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, performs Cell Reconstruction and enters Cover Command.\nAt the end of the turn, if the Ultimate skill Blast Judgment was not used during this turn, the damage accumulated by Command Mode is converted into 1 point of Overload Burst.\nAt the end of action, if the OTs-14 is under Demolition Command, switches to Cover Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Total Suppression active skill creates Phase tiles lvl 1 for 2 turns in the effective area if any Phase Reconstruction is active. Reconstruction · Zero does not create tiles.\nThe effects of Cell Reconstruction are enhanced: \nReconstruction · Burn - Dispels 1 debuff when teammates gain Embers;\nReconstruction · Electro - When an enemy unit's enters Stability Break, all allies regain 1 point of Stability Index;\nReconstruction · Freeze - When an ally deals damage, increases their ATK by 10% of their shield value;\nReconstruction · Corrosion - Active skill Total Suppression triggers all Corrosion debuffs held by enemy units within effect range;\nReconstruction · Hydro - For each friendly unit, all Entity Summons gain 1% ATK and 1% maximum HP increase;\nReconstruction · Zero - Demolition Command increases attack power by 50% instead of 30%, ignore 5% defense for every 15% initial Critical Damage."
          }
        ],
        "icon": "assets/OTs-14/Boojum Phenomenon.png"
      },
      {
        "name": "Critical Erosion",
        "traits": [
          "Basic Attack",
          "Active"
        ],
        "attribute": "Omni",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3-10",
        "effArea": "3",
        "description": "Selects 1 tile within 3-10 tile radius in front of self, deal AOE Omni damage equal to 150% of attack to all enemy units within 3 tile radius around the selected tile. Consumes 1 Overload Burst to deal additional fixed damage equal to 10% of accumulated damage of consumed Overload Burst.",
        "upgrades": [],
        "icon": "assets/OTs-14/Critical Erosion.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Perfect Adaptation",
        "level": "2",
        "effect": "Cover Command effect enhanced: the increase to critical damage of all allied units except the user is raised to 15% of the user's initial Critical Damage.\nDemolition Command effect enhanced: the increase to the user's attack is raised to 15% of the initial attack of all allied Dolls except the user."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Total Suppression",
        "level": "2",
        "effect": "Increases damage multiplier to 150%.\nThe effective area has been increased to 5×5 tiles.\nCooldown reduced by 1 turn."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Blast Judgment",
        "level": "2",
        "effect": "Reverse Assimilation effect enhanced: the damage of Critical Erosion is increased to 200%, and its effective range is increased by 2 tiles."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Blast Judgment",
        "level": "3",
        "effect": "Reverse Assimilation effect enhanced: each time Critical Erosion is used during the current turn, the damage multiplier of Critical Erosion is increased by 50%, and the multiplier of the fixed damage dealt by consuming Overload Burst is increased by 10%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Total Suppression",
        "level": "3",
        "effect": "If the user is under Cover Command, the increase to damage accumulated by Command Mode after skill usage is raised to 33%.\nIf the user is under Demolition Command, then for every 15% initial Critical Damage, the damage multiplier is increased by 15%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Boojum Phenomenon",
        "level": "2",
        "effect": "Total Suppression active skill creates Phase tiles lvl 1 for 2 turns in the effective area if any Phase Reconstruction is active. Reconstruction · Zero does not create tiles.\nThe effects of Cell Reconstruction are enhanced: \nReconstruction · Burn - Dispels 1 debuff when teammates gain Embers;\nReconstruction · Electro - When an enemy unit's enters Stability Break, all allies regain 1 point of Stability Index;\nReconstruction · Freeze - When an ally deals damage, increases their ATK by 10% of their shield value;\nReconstruction · Corrosion - Active skill Total Suppression triggers all Corrosion debuffs held by enemy units within effect range;\nReconstruction · Hydro - For each friendly unit, all Entity Summons gain 1% ATK and 1% maximum HP increase;\nReconstruction · Zero - Demolition Command increases attack power by 50% instead of 30%, ignore 5% defense for every 15% initial Critical Damage."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Predator's Stride",
        "level": "20",
        "keyName": "Fixed Key 1 - Predator's Stride",
        "description": "After using the Active skill Total Suppression or Perfect Reaction, gains Additional Movement for 6 tiles. Can be triggered up to 1 time per turn.",
        "icon": "assets/OTs-14/Fixed Key 1 - Predator's Stride.png"
      },
      {
        "node": "Fixed Key 2 - Self-Identity",
        "level": "20",
        "keyName": "Fixed Key 2 - Self-Identity",
        "description": "When gaining Reverse Assimilation, dispels all debuffs from self.",
        "icon": "assets/OTs-14/Fixed Key 2 - Self-Identity.png"
      },
      {
        "node": "Fixed Key 3 - Single-Minded Obsession",
        "level": "30",
        "keyName": "Fixed Key 3 - Single-Minded Obsession",
        "description": "If an active attack hits only 1 enemy target, damage dealt is increased by 20%.",
        "icon": "assets/OTs-14/Fixed Key 3 - Single-Minded Obsession.png"
      },
      {
        "node": "Fixed Key 4 - Perfect Battle Plan",
        "level": "30",
        "keyName": "Fixed Key 4 - Perfect Battle Plan",
        "description": "Before using the active skill Total Suppression, dispels 1 buff from the targets.",
        "icon": "assets/OTs-14/Fixed Key 4 - Perfect Battle Plan.png"
      },
      {
        "node": "Fixed Key 5 - At Any Cost",
        "level": "40",
        "keyName": "Fixed Key 5 - At Any Cost",
        "description": "While OTs-14 is in the Cover Command state, damage taken is reduced by 20%.",
        "icon": "assets/OTs-14/Fixed Key 5 - At Any Cost.png"
      },
      {
        "node": "Fixed Key 6 - Thirst for Destruction",
        "level": "40",
        "keyName": "Fixed Key 6 - Thirst for Destruction",
        "description": "Cell Reconstruction always grants Reconstruction · Zero.",
        "icon": "assets/OTs-14/Fixed Key 6 - Thirst for Destruction.png"
      },
      {
        "node": "Affinity Key -  Private style",
        "level": "-",
        "keyName": "Affinity Key -  Private style",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/OTs-14/Affinity Key -  Private style.png"
      },
      {
        "node": "Common Key - Genesis of Pride",
        "level": "40",
        "keyName": "Common Key - Genesis of Pride",
        "description": "CRIT DMG +5.0% / The user's fixed damage is increased by 10%.",
        "icon": "assets/OTs-14/Common Key - Genesis of Pride.png"
      }
    ]
  },
  "Soppo": {
    "class": "Sentinel",
    "stats": {
      "hp": 1948,
      "atk": 844,
      "def": 504
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Predator's Pursuit",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deals Freeze damage equal to 80% of attack to them. Soppo gains Confectance Index and Predator Mark. If Soppo is in Feral Form, this attack deals Burn damage instead.",
        "upgrades": [],
        "icon": "assets/Soppo/Predator's Pursuit.png"
      },
      {
        "name": "Ferocious Bite",
        "traits": [
          "Active",
          "AoE",
          "Tile"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "3",
        "description": "Selects 1 enemy target within 6 tiles, dealing AoE Freeze damage equal to 80% of attack to the target and all enemy targets within a 3-tile radius around it, and creates Frost tiles for 2 turns. After skill usage, use the basic attack Predator's Pursuit on the nearest enemy target within 8 tiles and gains Extra Command.\nIf in Feral Form, deals AoE Burn damage instead, creates Incineration tiles, and no longer gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The damage multiplier is increased to 130%. \nIf in Hunter Form, gains 2 stacks of Predator Mark after attacking, and gains Extra Action instead of Extra Command."
          }
        ],
        "icon": "assets/Soppo/Ferocious Bite.png"
      },
      {
        "name": "Midnight Howl",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "Full map",
        "effArea": "8",
        "description": "Selects any empty Freeze-type or Burn-type tile anywhere on the battlefield, moves onto that tile, and applies Slaughter Trail to all allied Dolls within an 8-tile radius around the user (excluding self) for 3 turns. After skill usage, switches to Feral Form.\n\nIf in Feral Form, deals AoE Burn damage equal to 120% of attack to all enemy targets within a 4-tile radius instead. This damage is evenly split among all targets within the area. After skill usage, Soppo use the basic attack Predator's Pursuit on the nearest enemy target within 8 tiles and gains Extra Action.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "After moving onto the target tile, if that tile is an Freeze-type or Burn-type tile, deals Freeze damage or Burn damage equal to 80% of attack to the 3 nearest enemy targets within 8 tiles.\nIf that tile is an Ashen (Freeze-Burn) tile, instead deals 1 instance of Freeze damage and 1 instance of Burn damage, each equal to 80% of attack, to the 3 nearest enemy targets within 8 tiles.\nIf in Feral Form, gains 1 stack of Predator Mark after skill usage."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "The effect of Slaughter Trail is enhanced: the range for creating Frost tiles is increased by 2 tiles; before performing an active attack, Soppo gains 1 stack of Berserk Factor.\nIf in Feral Form, the damage multiplier is increased to 150%. If the enemy target is standing on a Level 1 tile, the damage is increased by 10%; for every 1 tile level, the damage is further increased by 10%."
          }
        ],
        "icon": "assets/Soppo/Midnight Howl.png"
      },
      {
        "name": "Deadly Pounce",
        "traits": [
          "Ultimate",
          "AoE",
          "Interception"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 5,
        "cooldown": 2,
        "confectanceCost": 4,
        "range": "Self",
        "effArea": "6",
        "description": "Selects all enemy targets within a 6-tile radius, consumes all Predator Mark stacks, and deals AoE Freeze damage equal to number of Predator Mark stacks × 30% of attack. If this attack hits an enemy target standing on an phase tile, deals an additional 1 instance of Freeze damage equal to 50% of attack to that target. After skill usage, switches to Hunter Form.\n\nPassive: Before an enemy unit within 8 tiles performs an active attack, triggers Interception against it, dealing Freeze damage equal to 30% of attack and 4 points of stability damage. Can trigger at most once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "The multiplier is increased to number of Predator Mark stacks × 50% of attack. When using this skill, consumes all Confectance Index; for each additional 1 point of Confectance Index consumed, the base multiplier is increased by 5%. After skill usage, restores 2 points of Confectance Index.\nAfter triggering Interception, gains 2 stacks of Predator Mark. The damage multiplier of Interception is increased to 60%."
          }
        ],
        "icon": "assets/Soppo/Deadly Pounce.png"
      },
      {
        "name": "Mad Dog Syndrome",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, enters Hunter Form; consumes 3 points of own Confectance Index and gains Frost Barrier for 3 turns. Frost Barrier absorbs damage equal to 65% of initial attack, up to a maximum of 60% of max HP.\n\nAt the start of battle, if there are 3 or more allied Burn Dolls (excluding self), then while in Hunter Form, the damage dealt by the basic attack Predator's Pursuit and the active skill Ferocious Bite to enemy targets afflicted with Burn-type debuffs is increased by 100%; if there are 3 or more allied Freeze Dolls (excluding self), then while in Feral Form, the damage dealt by the above skills as well as the active skill Midnight Howl to enemy targets afflicted with Freeze-type debuffs is increased by 100%.\nIf neither condition is met, gains 2 stacks of Permanent Predator Mark.\n\nAfter use an active skill, gains 1 stack of Berserk Factor, up to a maximum of 10 stacks. At 4 stacks of Berserk Factor, gains Berserk Factor I; at 6 stacks of Berserk Factor, gains Berserk Factor II; at 8 or more stacks of Berserk Factor, gains Berserk Factor III.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The damage increase from team conditions against enemy targets is raised to 150% and no longer requires the target to have any debuffs. The number of Permanent Predator Mark stacks gained is increased by 2."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "At the start of battle, gains 3 stacks of Berserk Factor.\nThe maximum number of Berserk Factor stacks is increased to 20, and after performing an active attack, the number of Berserk Factor stacks gained is additionally increased by 1.\nIn addition, when Berserk Factor reaches 20 stacks, its effects are enhanced:\nBerserk Factor I — when actively attacking an enemy target standing on an phase tile, defense ignore is increased to 20%;\nBerserk Factor II — the increase to Freeze damage and Burn damage is raised to 10%;\nBerserk Factor III — when attacking an enemy target standing on an phase tile, the damage increase is raised to 30%."
          }
        ],
        "icon": "assets/Soppo/Mad Dog Syndrome.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Ferocious Bite",
        "level": "2",
        "effect": "The damage multiplier is increased to 130%. \nIf in Hunter Form, gains 2 stacks of Predator Mark after attacking, and gains Extra Action instead of Extra Command."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Midnight Howl",
        "level": "2",
        "effect": "After moving onto the target tile, if that tile is an Freeze-type or Burn-type tile, deals Freeze damage or Burn damage equal to 80% of attack to the 3 nearest enemy targets within 8 tiles.\nIf that tile is an Ashen (Freeze-Burn) tile, instead deals 1 instance of Freeze damage and 1 instance of Burn damage, each equal to 80% of attack, to the 3 nearest enemy targets within 8 tiles.\nIf in Feral Form, gains 1 stack of Predator Mark after skill usage."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Midnight Howl",
        "level": "3",
        "effect": "The effect of Slaughter Trail is enhanced: the range for creating Frost tiles is increased by 2 tiles; before performing an active attack, Soppo gains 1 stack of Berserk Factor.\nIf in Feral Form, the damage multiplier is increased to 150%. If the enemy target is standing on a Level 1 tile, the damage is increased by 10%; for every 1 tile level, the damage is further increased by 10%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Mad Dog Syndrome",
        "level": "2",
        "effect": "The damage increase from team conditions against enemy targets is raised to 150% and no longer requires the target to have any debuffs. The number of Permanent Predator Mark stacks gained is increased by 2."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Deadly Pounce",
        "level": "2",
        "effect": "The multiplier is increased to number of Predator Mark stacks × 50% of attack. When using this skill, consumes all Confectance Index; for each additional 1 point of Confectance Index consumed, the base multiplier is increased by 5%. After skill usage, restores 2 points of Confectance Index.\nAfter triggering Interception, gains 2 stacks of Predator Mark. The damage multiplier of Interception is increased to 60%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Mad Dog Syndrome",
        "level": "3",
        "effect": "At the start of battle, gains 3 stacks of Berserk Factor.\nThe maximum number of Berserk Factor stacks is increased to 20, and after performing an active attack, the number of Berserk Factor stacks gained is additionally increased by 1.\nIn addition, when Berserk Factor reaches 20 stacks, its effects are enhanced:\nBerserk Factor I — when actively attacking an enemy target standing on an phase tile, defense ignore is increased to 20%;\nBerserk Factor II — the increase to Freeze damage and Burn damage is raised to 10%;\nBerserk Factor III — when attacking an enemy target standing on an phase tile, the damage increase is raised to 30%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - This Is My Turf",
        "level": "20",
        "keyName": "Fixed Key 1 - This Is My Turf",
        "description": "At the start of battle, gains 2 stacks of Berserk Factor.",
        "icon": "assets/Soppo/Fixed Key 1 - This Is My Turf.png"
      },
      {
        "node": "Fixed Key 2 - Want Another Bite?",
        "level": "20",
        "keyName": "Fixed Key 2 - Want Another Bite?",
        "description": "After attacking an enemy target standing on an phase tile, dispels 1 buff from the target.",
        "icon": "assets/Soppo/Fixed Key 2 - Want Another Bite?.png"
      },
      {
        "node": "Fixed Key 3 - Frozen Hell",
        "level": "30",
        "keyName": "Fixed Key 3 - Frozen Hell",
        "description": "At the start of the turn, creates Frost tiles within a 4-tile radius around the user for 2 turns.",
        "icon": "assets/Soppo/Fixed Key 3 - Frozen Hell.png"
      },
      {
        "node": "Fixed Key 4 - Territorial Recovery",
        "level": "30",
        "keyName": "Fixed Key 4 - Territorial Recovery",
        "description": "When taking damage while standing on an phase tile, damage taken is reduced by 10%, and stability damage taken is reduced by 1 point.",
        "icon": "assets/Soppo/Fixed Key 4 - Territorial Recovery.png"
      },
      {
        "node": "Fixed Key 5 - Killing Frenzy",
        "level": "40",
        "keyName": "Fixed Key 5 - Killing Frenzy",
        "description": "While the Soppo has a shield, increases Burn damage and Freeze damage dealt by 10%.",
        "icon": "assets/Soppo/Fixed Key 5 - Killing Frenzy.png"
      },
      {
        "node": "Fixed Key 6 - Pack Synergy",
        "level": "40",
        "keyName": "Fixed Key 6 - Pack Synergy",
        "description": "After an allied unit (excluding Soppo) performs an out-of-turn attack, if the user does not have Blazing Assault I or Frost Assault, gains the corresponding effect for 2 turns.",
        "icon": "assets/Soppo/Fixed Key 6 - Pack Synergy.png"
      },
      {
        "node": "Affinity Key - Frolic chord",
        "level": "-",
        "keyName": "Affinity Key - Frolic chord",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Soppo/Affinity Key - Frolic chord.png"
      },
      {
        "node": "Common Key - Call of the Wild",
        "level": "40",
        "keyName": "Common Key - Call of the Wild",
        "description": "CRIT +5.0% / When attacking an enemy target standing on an Freeze-type or Burn-type tile, phase damage dealt is increased by 10%.",
        "icon": "assets/Soppo/Common Key - Call of the Wild.png"
      }
    ]
  },
  "Mityl": {
    "class": "Sentinel",
    "stats": {
      "hp": 2014,
      "atk": 809,
      "def": 494
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Assault Shot",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to it.",
        "upgrades": [],
        "icon": "assets/Mityl/Assault Shot.png"
      },
      {
        "name": "Arc Shadow of the Gray Mouse",
        "traits": [
          "Active",
          "Tile",
          "Summon",
          "Teleport"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within a 6-tile radius, excluding summons, then selects 1 empty tile within 3 tiles around that target, summons 1 Mimic Hologram of the target on that tile, and creates Tideway tiles within 5 tiles around the summoned Hologram for 2 turns. Up to 2 Holograms can exist at the same time. If the target is a Doll, Boss, or Large unit, summons 1 Personal Hologram instead.\n\nCan also select 1 Hologram within a 6-tile radius and teleport it to 1 empty tile within a 5-tile radius.\n\nAfter using the skill, gains Extra Command. Can trigger once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Each time Fitting Resonance is cast, Holograms gain 1 stack of Untouchable. The damage multiplier of Personal Hologram’s basic attack Arc Shadow Assault is increased to 120% ATK."
          }
        ],
        "icon": "assets/Mityl/Arc Shadow of the Gray Mouse.png"
      },
      {
        "name": "Aerial Dash",
        "traits": [
          "Active",
          "Targeted",
          "Displacement"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "--",
        "effArea": "6",
        "description": "Selects 1 tile within a 3- to 6-tile cross-shaped range and lands on that tile, dealing Hydro damage equal to 130% ATK to the nearest enemy target within a 6-tile radius.\n\nIf both before using this skill and when dealing damage, Mityl is on a Hydro type tile, she can use the active skill Aerial Dash 1 additional time, and its damage dealt is increased by 30%. Can trigger once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The condition for using the active skill again is changed: Mityl only needs to be on a Hydro type tile either before using the skill or when dealing damage. The damage is increased to 160% ATK. Damage dealt by the active skill used again is increased by 50%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "After the skill cast, Personal Hologram performs 1 Action Support against the target, dealing Hydro damage equal to 60% ATK and 2 points of Stability damage. Can trigger up to once per turn. Damage dealt by Mimic Hologram during this current turn is increased by 100%. This effect cannot stack."
          }
        ],
        "icon": "assets/Mityl/Aerial Dash.png"
      },
      {
        "name": "Void Fitting",
        "traits": [
          "Ultimate",
          "Tile",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "5",
        "description": "Gains Saturation Overflow for 2 turns. Creates Tideway tiles within a 5-tile radius around self for 2 turns. After using the skill, gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "The range of created Tideway tiles is expanded to a 7-tile radius. The ATK increase from Saturation Overflow is increased to 40% and also applies to Holograms. If Fitting Resonance triggers a total of 4 or more times during the current turn, Saturation Overflow does not consume its duration."
          }
        ],
        "icon": "assets/Mityl/Void Fitting.png"
      },
      {
        "name": "Stunt Montage",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Self",
        "description": "At the end of the allied turn, all Holograms cast Fitting Resonance 1 time. After Mityl or a Hologram deals Hydro damage, gains 1 point of Confectance Index. If the attacker or the attack target is on a Hydro type tile, gains 1 additional point of Confectance Index. Can gain up to 6 points of Confectance Index per turn.\n\nAt the start of battle, gains Mimic Rookie. For every 6 points of Confectance Index gained, including overflow Confectance Index, gains a higher level of Cinematic Title.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The damage of Fitting Resonance is increased to 60% ATK. When Cinematic Title is upgraded, Holograms cast Fitting Resonance 1 time. The Confectance Index required to upgrade the Title is reduced to 4 points. Fitting Resonance applies Defense Down II to the target for 2 turns."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Legendary Star gains a new effect: for every 4 points of Confectance Index gained, all Holograms cast Fitting Resonance 1 time.\n\nWhen a Hologram casts Fitting Resonance, it gains 1 stack of Fitting Amplification."
          }
        ],
        "icon": "assets/Mityl/Stunt Montage.png"
      },
      {
        "name": "Arc Shadow Assault",
        "traits": [
          "Passive",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Hydro damage equal to 100% of attack to it.",
        "upgrades": [],
        "icon": "assets/Mityl/Arc Shadow Assault.png"
      },
      {
        "name": "Data Regression",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "When casting Fitting Resonance, recovers 50% of current maximum HP and increases maximum HP by 5%, up to maximum of 20%.",
        "upgrades": [],
        "icon": "assets/Mityl/Data Regression.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Stunt Montage",
        "level": "2",
        "effect": "The damage of Fitting Resonance is increased to 60% ATK. When Cinematic Title is upgraded, Holograms cast Fitting Resonance 1 time. The Confectance Index required to upgrade the Title is reduced to 4 points. Fitting Resonance applies Defense Down II to the target for 2 turns."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Arc Shadow of the Gray Mouse",
        "level": "2",
        "effect": "Each time Fitting Resonance is cast, Holograms gain 1 stack of Untouchable. The damage multiplier of Personal Hologram’s basic attack Arc Shadow Assault is increased to 120% ATK."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Void Fitting",
        "level": "2",
        "effect": "The range of created Tideway tiles is expanded to a 7-tile radius. The ATK increase from Saturation Overflow is increased to 40% and also applies to Holograms. If Fitting Resonance triggers a total of 4 or more times during the current turn, Saturation Overflow does not consume its duration."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Aerial Dash",
        "level": "2",
        "effect": "The condition for using the active skill again is changed: Mityl only needs to be on a Hydro type tile either before using the skill or when dealing damage. The damage is increased to 160% ATK. Damage dealt by the active skill used again is increased by 50%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Aerial Dash",
        "level": "3",
        "effect": "After the skill cast, Personal Hologram performs 1 Action Support against the target, dealing Hydro damage equal to 60% ATK and 2 points of Stability damage. Can trigger up to once per turn. Damage dealt by Mimic Hologram during this current turn is increased by 100%. This effect cannot stack."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Stunt Montage",
        "level": "3",
        "effect": "Legendary Star gains a new effect: for every 4 points of Confectance Index gained, all Holograms cast Fitting Resonance 1 time.\n\nWhen a Hologram casts Fitting Resonance, it gains 1 stack of Fitting Amplification."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Cinematic Presentation",
        "level": "20",
        "keyName": "Fixed Key 1 - Cinematic Presentation",
        "description": "When the active skill Aerial Dash deals damage, cleanses 1 buff from the target.",
        "icon": "assets/Mityl/Fixed Key 1 - Cinematic Presentation.png"
      },
      {
        "node": "Fixed Key 2 - Disguised Performance",
        "level": "20",
        "keyName": "Fixed Key 2 - Disguised Performance",
        "description": "Personal Hologram can be manually controlled and can move.",
        "icon": "assets/Mityl/Fixed Key 2 - Disguised Performance.png"
      },
      {
        "node": "Fixed Key 3 - Triple somersault and interception",
        "level": "30",
        "keyName": "Fixed Key 3 - Triple somersault and interception",
        "description": "At the end of Mityl’s action, if she is on a Hydro type tile, gains Movement Up II for 2 turns.",
        "icon": "assets/Mityl/Fixed Key 3 - Triple somersault and interception.png"
      },
      {
        "node": "Fixed Key 4 - Crying Scene",
        "level": "30",
        "keyName": "Fixed Key 4 - Crying Scene",
        "description": "When Mityl and Holograms deal Hydro damage, applies Emotional Contagion to the target.",
        "icon": "assets/Mityl/Fixed Key 4 - Crying Scene.png"
      },
      {
        "node": "Fixed Key 5 - Hop on the Hype Train",
        "level": "40",
        "keyName": "Fixed Key 5 - Hop on the Hype Train",
        "description": "At the start of battle, Mityl summons 1 Hologram. Both Mityl and this Hologram are considered both a Doll and a summon. This Hologram has no skills and cannot act.",
        "icon": "assets/Mityl/Fixed Key 5 - Hop on the Hype Train.png"
      },
      {
        "node": "Fixed Key 6 - Truth or Lie?",
        "level": "40",
        "keyName": "Fixed Key 6 - Truth or Lie?",
        "description": "When Mityl or Holograms deal damage, if the attacker is on a Hydro tile, increases damage dealt by 10%. For each increase in that Hydro tile’s tile level, increases damage dealt by an additional 5%.",
        "icon": "assets/Mityl/Fixed Key 6 - Truth or Lie?.png"
      },
      {
        "node": "Affinity Key",
        "level": "40",
        "keyName": "Affinity Key",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Mityl/Affinity Key.png"
      },
      {
        "node": "Common Key - Clever Mitty",
        "level": "40",
        "keyName": "Common Key - Clever Mitty",
        "description": "CRIT +5.0% / When dealing damage, if user is on a Hydro tile, increases damage dealt by 10%.",
        "icon": "assets/Mityl/Common Key - Clever Mitty.png"
      }
    ]
  },
  "Welrod": {
    "class": "Bulwark",
    "stats": {
      "hp": 2338,
      "atk": 671,
      "def": 577
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Silent Takedown",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Welrod/Silent Takedown.png"
      },
      {
        "name": "Joint Investigation",
        "traits": [
          "Active",
          "AoE",
          "Buff",
          "Defense"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 5,
        "cooldown": 1,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Corrosion damage equal to 100% ATK to it and gains Deductive Obsession for 3 turns, you get 2 stacks of Shelter and 4 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Healing effect boost of Deductive Obsession is increased to 30%, damage taken reduction increased to 30%, and the effect is added: Corrosion damage dealt increased by 30%.\nAfter the skill usage, restores HP equal to 100% of ATK to friendly unit with the lowest HP within a radius of 5 tiles around self (excluding self) and applies 2 stacks of Shelter."
          }
        ],
        "icon": "assets/Welrod/Joint Investigation.png"
      },
      {
        "name": "Conviction and Punishment",
        "traits": [
          "Active",
          "Targeted",
          "Displacement"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "6",
        "effArea": "5",
        "description": "Selects a tile within a 6 tile radius, deal AoE Corrosion damage equal to 120% ATK to all enemies within 5 tile radius and creates Toxic Mist tiles for 2 rounds. For every 1% increase in max HP compared to initial HP, the damage multiplier is increased by 1%, up to 60%. For every enemy target hit, the accumulated damage value of Detective's Immunity is reduced by 10%. If the target is the Boss unit, it is reduced by 30%, up to maximum reduction of 50%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The damage multiplier increased to 120%.\nFor every 1% increase in max HP compared to the initial HP, the damage multiplier is increased by 1.5%, up to 150%."
          }
        ],
        "icon": "assets/Welrod/Conviction and Punishment.png"
      },
      {
        "name": "Hour of Reckoning",
        "traits": [
          "Ultimate",
          "Debuff",
          "Displacement",
          "Healing"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 5,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals AoE Corrosion damage equivalent to 120% ATK to all enemies within a 3x9 frontal area in the selected direction, pull them 3 tiles towards self and apply Crime Backlash for 1 round and Suspect for 2 rounds. Welrod recovers her HP equal to 20% of Detective's Immunity's accumulated damage value and gains V3 Protection for 1 round. After using this skill, Welrod can use basic attack Silent Takedown, active skill Joint Investigation or active skill Conviction and Punishment.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Damage multiplier increased to 120%.\nCrime Backlash effect enchanced: Damage taken is increased to the sum of 50% of Detective's Immunity's accumulated damage value and 30% of Welrod's max HP.\nCooldown of V3 Protection is reduced by 1 round."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "For every 1 instance of damage taken, damage dealt is increased by 40%, up to 80%.\nFor every enemy target hit, the damage dealt is increased by 20%, up to 100%.\nSuspect effect enchanced: The fixed damage received at the end of the round is increased to 16% of its maximum HP. If the target is the Boss unit, the damage is increased to 360% of Welrod ATK.\nCooldown is reduced by 1 round."
          }
        ],
        "icon": "assets/Welrod/Hour of Reckoning.png"
      },
      {
        "name": "Case Detective",
        "traits": [
          "Passive",
          "Control"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Welrod does not receive Cover protection and her Crit is reduced by 100%, her max HP is increased by 50% and damage taken reduced by 20%.\nGain Detective's Immunity at the start of battle. In the end of Welrod action she deals 1 instance of AOE Corrosion damage equal to 30% of Detective's Immunity's accumulated damage value to all enemy targets within 6 tiles radius, and applies Suspect for 2 rounds. When action ends, applies Taunt to all enemy targets within 6 tile radius for 1 round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "At the end of another friendly Doll action, Welrod also triggers 1 instance of AOE Corrosion damage equal to 30% of Detective's Immunity's accumulated damage value.\nDetective's Immunity effect enchanced: The upper limit of absorption value increased to the sum of 250% of own max HP and 150% of ATK at the start of the battle (no more than 800% of own initial max HP)."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "At the start of the battle, the max HP increase is boosted to 150%.\nFor every instance of damage taken (including damage caused by Detective's Immunity), own ATK is increased by 1%, up to 50%"
          }
        ],
        "icon": "assets/Welrod/Case Detective.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Joint Investigation",
        "level": "2",
        "effect": "Healing effect boost of Deductive Obsession is increased to 30%, damage taken reduction increased to 30%, and the effect is added: Corrosion damage dealt increased by 30%.\nAfter the skill usage, restores HP equal to 100% of ATK to friendly unit with the lowest HP within a radius of 5 tiles around self (excluding self) and applies 2 stacks of Shelter."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Case Detective",
        "level": "2",
        "effect": "At the end of another friendly Doll action, Welrod also triggers 1 instance of AOE Corrosion damage equal to 30% of Detective's Immunity's accumulated damage value.\nDetective's Immunity effect enchanced: The upper limit of absorption value increased to the sum of 250% of own max HP and 150% of ATK at the start of the battle (no more than 800% of own initial max HP)."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Hour of Reckoning",
        "level": "2",
        "effect": "Damage multiplier increased to 120%.\nCrime Backlash effect enchanced: Damage taken is increased to the sum of 50% of Detective's Immunity's accumulated damage value and 30% of Welrod's max HP.\nCooldown of V3 Protection is reduced by 1 round."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Conviction and Punishment",
        "level": "2",
        "effect": "The damage multiplier increased to 120%.\nFor every 1% increase in max HP compared to the initial HP, the damage multiplier is increased by 1.5%, up to 150%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Hour of Reckoning",
        "level": "3",
        "effect": "For every 1 instance of damage taken, damage dealt is increased by 40%, up to 80%.\nFor every enemy target hit, the damage dealt is increased by 20%, up to 100%.\nSuspect effect enchanced: The fixed damage received at the end of the round is increased to 16% of its maximum HP. If the target is the Boss unit, the damage is increased to 360% of Welrod ATK.\nCooldown is reduced by 1 round."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Case Detective",
        "level": "3",
        "effect": "At the start of the battle, the max HP increase is boosted to 150%.\nFor every instance of damage taken (including damage caused by Detective's Immunity), own ATK is increased by 1%, up to 50%"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Master Detective's Aura",
        "level": "20",
        "keyName": "Fixed Key 1 - Master Detective's Aura",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Welrod/Fixed Key 1 - Master Detective's Aura.png"
      },
      {
        "node": "Fixed Key 2 - Preliminary Evidence Gathering",
        "level": "20",
        "keyName": "Fixed Key 2 - Preliminary Evidence Gathering",
        "description": "Before an active attack, cleanse 1 buff from the target.",
        "icon": "assets/Welrod/Fixed Key 2 - Preliminary Evidence Gathering.png"
      },
      {
        "node": "Fixed Key 3 - Honkaku Logic",
        "level": "30",
        "keyName": "Fixed Key 3 - Honkaku Logic",
        "description": "The absorption limit of Detective's Immunity is increased to 90%.",
        "icon": "assets/Welrod/Fixed Key 3 - Honkaku Logic.png"
      },
      {
        "node": "Fixed Key 4 - Hellhound Hunt",
        "level": "30",
        "keyName": "Fixed Key 4 - Hellhound Hunt",
        "description": "When attacking a Boss unit, Corrosion damage dealt is increased by 20%.",
        "icon": "assets/Welrod/Fixed Key 4 - Hellhound Hunt.png"
      },
      {
        "node": "Fixed Key 5 - The Final Problem",
        "level": "40",
        "keyName": "Fixed Key 5 - The Final Problem",
        "description": "Gains immunity to Stun and Fear. Healing effects are increased by 30%",
        "icon": "assets/Welrod/Fixed Key 5 - The Final Problem.png"
      },
      {
        "node": "Fixed Key 6 - Two-in-One Detective",
        "level": "40",
        "keyName": "Fixed Key 6 - Two-in-One Detective",
        "description": "Detective's Immunity's fixed damage Welrod takes at the end of her action is changed to 2 times, and the fixed damage taken is reduced by 15%.",
        "icon": "assets/Welrod/Fixed Key 6 - Two-in-One Detective.png"
      },
      {
        "node": "Affinity Key - Tracking Oath",
        "level": "-",
        "keyName": "Affinity Key - Tracking Oath",
        "description": "ATK +3%, HP +3%, DEF +3%",
        "icon": "assets/Welrod/Affinity Key - Tracking Oath.png"
      },
      {
        "node": "Common Key - Van Dine's Rules",
        "level": "40",
        "keyName": "Common Key - Van Dine's Rules",
        "description": "HP +5.0% / When the user attacks, if their HP percentage is greater than or equal to the target's, the phase damage dealt is increased by 10%.",
        "icon": "assets/Welrod/Common Key - Van Dine's Rules.png"
      }
    ]
  }
};
