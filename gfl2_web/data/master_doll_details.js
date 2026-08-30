/**
 * GFL2 Doll Info
 * Source: https://docs.google.com/spreadsheets/d/1DogyU3K7ZXw2qbhP1EhRXIAw5nCyIV5G5e-QWviBZME
 * Generated: 2026-08-29
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
  "Groza": {
    "class": "Bulwark",
    "stats": {
      "hp": 1981,
      "atk": 539,
      "def": 553
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Fire Command",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects 1 target within 7 tiles, dealing Physical damage equal to 80% of attack.",
        "upgrades": [],
        "icon": "assets/Groza/Fire Command.png"
      },
      {
        "name": "Heavy Suppression",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 5,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "7",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 7 tiles, dealing Physical damage equal to 130% of attack, and applies Movement Down II to them for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If this skill causes the enemy to enter into Stability Break, the user gains 1 point of Confectance Index and recovers 4 points of stability index."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Firepower Superiority",
            "effect": "If Heavy Suppression causes the enemy target to enter Stability Break, applies Taunt to them for 1 turn."
          }
        ],
        "icon": "assets/Groza/Heavy Suppression.png"
      },
      {
        "name": "Perfect Cover",
        "traits": [
          "Active",
          "Buff",
          "Defense"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "6",
        "description": "Applies 2 stacks of Shelter and Defense Up II to all allied targets within 6 tiles for 2 turns. Gains 1 point of Confectance Index for each allied target within range. Increases the Counterattack count by 2 for the turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Restores 5 points of stability index."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Controlled Advance",
            "effect": "When using Perfect Cover, additionally applies Attack Up I for 1 turn."
          }
        ],
        "icon": "assets/Groza/Perfect Cover.png"
      },
      {
        "name": "Explosive Bombardment",
        "traits": [
          "Ultimate",
          "AoE",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "7",
        "effArea": "3x3",
        "description": "Select 1 tile within 7 tiles of the user to launch an attack, dealing AoE Physical damage equal to 90% of attack to all enemy targets within a 3x3 area and applying Movement Down II for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Damage multiplier increased by 10%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Extends the duration of Movement Down II increases by 1 turn."
          }
        ],
        "icon": "assets/Groza/Explosive Bombardment.png"
      },
      {
        "name": "Timely Maintenance",
        "traits": [
          "Passive",
          "Buff",
          "Counterattack"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "7",
        "description": "when an allied unit (excluding this unit) ends their action within 7 tiles, gains 1 point of Confectance Index and applies 1 stack of Shelter to both the allied unit and this unit. For each stack of Shelter, Groza's damage increases by 5%. \n\nIf an enemy within 6 tiles deals Targeted damage to an allied unit, Groza launches a Counterattack, dealing Physical damage equal to 80% of attack to them, as well as 4 points of Stability Damage. This can be triggered at most once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "When Groza's action ends, applies Attack Down I on the enemy with the highest attack within a 7 tile radius of self for 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "When having Shelter, reduces stability damage taken by 1 point."
          }
        ],
        "icon": "assets/Groza/Timely Maintenance.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Heavy Suppression",
        "level": "2",
        "effect": "If this skill causes the enemy to enter into Stability Break, the user gains 1 point of Confectance Index and recovers 4 points of stability index."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Perfect Cover",
        "level": "2",
        "effect": "Restores 5 points of stability index."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Explosive Bombardment",
        "level": "2",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Timely Maintenance",
        "level": "2",
        "effect": "When Groza's action ends, applies Attack Down I on the enemy with the highest ATK within a 7 tile radius of self for 1 turn."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Explosive Bombardment",
        "level": "3",
        "effect": "Extends the duration of Movement Down II increases by 1 turn."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Timely Maintenance",
        "level": "3",
        "effect": "When having Shelter, reduces stability damage taken by 1 point."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Multidimensional Assessment",
        "level": "20",
        "keyName": "Fixed Key 1 - Multidimensional Assessment",
        "description": "When the user causes the enemy to enter into Stability Break, applies Defence Down I and Attack Down I on the enemy for 1 turn.",
        "icon": "assets/Groza/Fixed Key 1 - Multidimensional Assessment.png"
      },
      {
        "node": "Fixed Key 2 - Controlled Advance",
        "level": "20",
        "keyName": "Fixed Key 2 - Controlled Advance",
        "description": "When using Perfect Cover, additionally applies Attack Up I for 1 turn.",
        "icon": "assets/Groza/Fixed Key 2 - Controlled Advance.png"
      },
      {
        "node": "Fixed Key 3 - Adaptive Strategy",
        "level": "30",
        "keyName": "Fixed Key 3 - Adaptive Strategy",
        "description": "When self HP is below 30%, increase healing received by 50%.",
        "icon": "assets/Groza/Fixed Key 3 - Adaptive Strategy.png"
      },
      {
        "node": "Fixed Key 4 - Firepower Superiority",
        "level": "30",
        "keyName": "Fixed Key 4 - Firepower Superiority",
        "description": "If Heavy Suppression causes the enemy target to enter Stability Break, applies Taunt to them for 1 turn.",
        "icon": "assets/Groza/Fixed Key 4 - Firepower Superiority.png"
      },
      {
        "node": "Fixed Key 5 - Sustainable Operations",
        "level": "40",
        "keyName": "Fixed Key 5 - Sustainable Operations",
        "description": "When the user is under the effects of Shelter, reduces AoE damage taken by 20%.",
        "icon": "assets/Groza/Fixed Key 5 - Sustainable Operations.png"
      },
      {
        "node": "Fixed Key 6 - Principles of Evasion",
        "level": "40",
        "keyName": "Fixed Key 6 - Principles of Evasion",
        "description": "When Groza enters into Stability Break, restore 20% of self max HP, 5 points of stability index, and cleanse 4 debuffs from self. Triggers only once per battle.",
        "icon": "assets/Groza/Fixed Key 6 - Principles of Evasion.png"
      },
      {
        "node": "Affinity Key - Midnight Reflection",
        "level": "-",
        "keyName": "Affinity Key - Midnight Reflection",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Groza/Affinity Key - Midnight Reflection.png"
      },
      {
        "node": "Common Key - Sustained Endurance",
        "level": "40",
        "keyName": "Common Key - Sustained Endurance",
        "description": "HP +3.0% / When Shelter is active, immune to displacement for 1 time. Has a cooldown of 1 turn.",
        "icon": "assets/Groza/Common Key - Sustained Endurance.png"
      },
      {
        "node": "Expansion Key - Absolute Defense's Essence",
        "level": "60",
        "keyName": "Expansion Key - Absolute Defense's Essence",
        "description": "When using the active skill Perfect Cover, gains Absolute Defense.",
        "icon": "assets/Groza/Expansion Key - Absolute Defense's Essence.png"
      }
    ]
  },
  "Nemesis": {
    "class": "Sentinel",
    "stats": {
      "hp": 1656,
      "atk": 703,
      "def": 463
    },
    "stabilityGauge": 9,
    "movementSpeed": 4,
    "skillAttributes": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Light Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Victory Portent",
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
        "description": "Selects 1 enemy target within 9 tiles and deals Physical damage equal to 80% attack to them.",
        "upgrades": [],
        "icon": "assets/Nemesis/Victory Portent.png"
      },
      {
        "name": "Enlightened Star",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Select 1 enemy target within 9 tiles of the user and deal Physical damage equal to 130% of attack. When attacking near Cover, increases damage dealt by 20% and gain 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If the target has Prophecy of Mourning, increase damage dealt by 10%."
          }
        ],
        "icon": "assets/Nemesis/Enlightened Star.png"
      },
      {
        "name": "Penetrating Casket",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles, applies Defense Down II for 1 turn, and deals Physical damage equal to 130% of attack to them.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Gains 1 point of Confectance Index if the target has a defense debuff."
          }
        ],
        "icon": "assets/Nemesis/Penetrating Casket.png"
      },
      {
        "name": "Constellation Pursuit",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles, dealing Corrosion damage equal to 170% of attack. For each additional 1 point of Confectance Index, this attack's damage is increased by 10%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "When Insight is active, increases the damage multiplier by 10%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For each debuff on the target, increases critical rate by 20%, up to 100%."
          }
        ],
        "icon": "assets/Nemesis/Constellation Pursuit.png"
      },
      {
        "name": "Remote Observation",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "9",
        "description": "At the start of the action, marks the 2 nearest enemy targets within range with Prophecy of Mourning for 1 turn. Action Support deals Physical damage equal to 80% of attack and 2 points of Stability Damage. This unit gains Insight for 1 turn after using a Action Support.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the duration of Prophecy of Mourning by 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "When this unit is under the effects of Insight, further increases damage dealt by 10%."
          }
        ],
        "icon": "assets/Nemesis/Remote Observation.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Remote Observation",
        "level": "2",
        "effect": "Increases the duration of Prophecy of Mourning by 1 turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Enlightened Star",
        "level": "2",
        "effect": "If the target has Prophecy of Mourning, increase damage dealt by 10%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Penetrating Casket",
        "level": "2",
        "effect": "Gains 1 point of Confectance Index if the target has a defense debuff."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Remote Observation",
        "level": "3",
        "effect": "When this unit is under the effects of Insight, further increases damage dealt by 10%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Constellation Pursuit",
        "level": "2",
        "effect": "When Insight is active, increases the damage multiplier by 10%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Constellation Pursuit",
        "level": "3",
        "effect": "For each debuff on the target, increases critical rate by 20%, up to 100%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Potent Curse",
        "level": "20",
        "keyName": "Fixed Key 1 - Potent Curse",
        "description": "If the enemy target is marked with Prophecy of Mourning, apply Defense Down II before launching an active attack.",
        "icon": "assets/Nemesis/Fixed Key 1 - Potent Curse.png"
      },
      {
        "node": "Fixed Key 2 - Changing Fortune",
        "level": "20",
        "keyName": "Fixed Key 2 - Changing Fortune",
        "description": "When this unit is under the effects of Insight, the range of the active skills Enlightened Star and Penetrating Casket are increased by 1 tile.",
        "icon": "assets/Nemesis/Fixed Key 2 - Changing Fortune.png"
      },
      {
        "node": "Fixed Key 3 - Fortune's Call",
        "level": "30",
        "keyName": "Fixed Key 3 - Fortune's Call",
        "description": "If there is Cover nearby while under the effects of Insight, reduce AoE damage taken by 20%.",
        "icon": "assets/Nemesis/Fixed Key 3 - Fortune's Call.png"
      },
      {
        "node": "Fixed Key 4 - Silent Catastrophe",
        "level": "30",
        "keyName": "Fixed Key 4 - Silent Catastrophe",
        "description": "When killing a target marked with Prophecy of Mourning, gain Attack Up I and Damage Up I for 1 turn.",
        "icon": "assets/Nemesis/Fixed Key 4 - Silent Catastrophe.png"
      },
      {
        "node": "Fixed Key 5 - Fated Calamity",
        "level": "40",
        "keyName": "Fixed Key 5 - Fated Calamity",
        "description": "When a target marked with Prophecy of Mourning is killed by this unit, gain 1 point of Confectance Index.",
        "icon": "assets/Nemesis/Fixed Key 5 - Fated Calamity.png"
      },
      {
        "node": "Fixed Key 6 - Focused Gaze",
        "level": "40",
        "keyName": "Fixed Key 6 - Focused Gaze",
        "description": "When this unit is under the effects of Insight, gain immunity to all displacement effects from enemy units.",
        "icon": "assets/Nemesis/Fixed Key 6 - Focused Gaze.png"
      },
      {
        "node": "Affinity Key - Soft Whispers",
        "level": "-",
        "keyName": "Affinity Key - Soft Whispers",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Nemesis/Affinity Key - Soft Whispers.png"
      },
      {
        "node": "Common Key - Blessing of the Morning Star",
        "level": "40",
        "keyName": "Common Key - Blessing of the Morning Star",
        "description": "ATK +3.0% / When this unit is under the effects of Insight, gains 3 tiles of Additional Movement after killing an enemy target.",
        "icon": "assets/Nemesis/Common Key - Blessing of the Morning Star.png"
      },
      {
        "node": "Expansion Key - Forecast Elegy",
        "level": "60",
        "keyName": "Expansion Key - Forecast Elegy",
        "description": "At the start of the turn, applies Prophecy of Mourning to the enemy with the highest HP within Attack Range",
        "icon": "assets/Nemesis/Expansion Key - Forecast Elegy.png"
      }
    ]
  },
  "Krolik": {
    "class": "Vanguard",
    "stats": {
      "hp": 1397,
      "atk": 618,
      "def": 463
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Melee",
      "Burn"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Instantaneous Slash",
        "traits": [
          "Basic Attack",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "Enemy",
        "description": "Selects 1 target within 1 tile, dealing melee Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Krolik/Instantaneous Slash.png"
      },
      {
        "name": "Crushing Revolution",
        "traits": [
          "Active",
          "AoE",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "3x3",
        "description": "Selects 1 enemy target within 1 tile, dealing melee AoE Physical damage equal to 120% of attack to the target and all enemy units within a 3x3 area, and gains 1 point of Confectance Index. After the attack, if there are no other allied units within 3 tiles around the user, gains 5 tiles of Additional Movement.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If the target is under the effects of Stability Break, ignore 30% of its defense."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Fierce Predator",
            "effect": "The active skill Crushing Revolution deals 30% increased damage when hitting a single target."
          }
        ],
        "icon": "assets/Krolik/Crushing Revolution.png"
      },
      {
        "name": "Quenching Slash",
        "traits": [
          "Active",
          "Targeted",
          "Melee",
          "Debuff"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "Enemy",
        "description": "Select 1 enemy target within 1 tile, apply Overburn to it for 2 turns, deal melee Burn damage equal to 150% of attack, and gain 2 points of Confectance Index. After the attack, return to the original position before the action.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Damage multiplier increased by 10%."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Proud Challenger",
            "effect": "When the active skill Quenching Slash kills an enemy target, reduces this skill's cooldown by 2 turns."
          }
        ],
        "icon": "assets/Krolik/Quenching Slash.png"
      },
      {
        "name": "Slaughter Sequence",
        "traits": [
          "Ultimate",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "1",
        "effArea": "7",
        "description": "Selects 1 direction and moves to the farthest tile within 7 tiles, dealing melee Burn damage equal to 130% of attack to the first enemy encountered. If the target is inflicted with Overburn, ignores their Cover damage reduction, and gains 5 tiles of Additional Movement.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If this kills the target, gain 2 points of Confectance Index."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "If the target is inflicted with Overburn, increases critical rate by 100%."
          }
        ],
        "icon": "assets/Krolik/Slaughter Sequence.png"
      },
      {
        "name": "Embers",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "5",
        "description": "When attacking a target with Overburn, increases damage dealt by 15%. At the end of the action, applies Overburn to the closest 2 enemy targets within 5 tiles for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Range increases by 2 tiles."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "When attacking a target with Overburn, increases critical damage by 20%."
          }
        ],
        "icon": "assets/Krolik/Embers.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Crushing Revolution",
        "level": "2",
        "effect": "If the target is under the effects of Stability Break, ignore 30% its defense."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Quenching Slash",
        "level": "2",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Slaughter Sequence",
        "level": "2",
        "effect": "If this kills the target, gain 2 points of Confectance Index."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Embers",
        "level": "2",
        "effect": "Range increases by 2 tiles."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Slaughter Sequence",
        "level": "3",
        "effect": "If the target is inflicted with Overburn, increases critical rate by 100%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Embers",
        "level": "3",
        "effect": "When attacking a target with Overburn, increases critical damage by 20%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Momentary Focus",
        "level": "20",
        "keyName": "Fixed Key 1 - Momentary Focus",
        "description": "Reduces the Confectance Index consumption of the active skill Slaughter Sequence by 1 point.",
        "icon": "assets/Krolik/Fixed Key 1 - Momentary Focus.png"
      },
      {
        "node": "Fixed Key 2 - Fierce Predator",
        "level": "20",
        "keyName": "Fixed Key 2 - Fierce Predator",
        "description": "The active skill Crushing Revolution deals 30% increased damage when hitting a single target.",
        "icon": "assets/Krolik/Fixed Key 2 - Fierce Predator.png"
      },
      {
        "node": "Fixed Key 3 - Blazing Fury",
        "level": "30",
        "keyName": "Fixed Key 3 - Blazing Fury",
        "description": "If there are no other allied units within 3 tiles of the user, increases damage dealt by 10%.",
        "icon": "assets/Krolik/Fixed Key 3 - Blazing Fury.png"
      },
      {
        "node": "Fixed Key 4 - Proud Challenger",
        "level": "30",
        "keyName": "Fixed Key 4 - Proud Challenger",
        "description": "When the active skill Quenching Slash kills an enemy target, reduces this skill's cooldown by 2 turns.",
        "icon": "assets/Krolik/Fixed Key 4 - Proud Challenger.png"
      },
      {
        "node": "Fixed Key 5 - Instinctive Pursuit",
        "level": "40",
        "keyName": "Fixed Key 5 - Instinctive Pursuit",
        "description": "At the start of action, if there are enemy units with Overburn on the field, gains Blazing Assault II for 2 turns.",
        "icon": "assets/Krolik/Fixed Key 5 - Instinctive Pursuit.png"
      },
      {
        "node": "Fixed Key 6 - Hidden Poise",
        "level": "40",
        "keyName": "Fixed Key 6 - Hidden Poise",
        "description": "Before attacking, if this unit moved more than 3 tiles, increases the user's critical rate by 10%.",
        "icon": "assets/Krolik/Fixed Key 6 - Hidden Poise.png"
      },
      {
        "node": "Affinity Key - Scorching Protection",
        "level": "-",
        "keyName": "Affinity Key - Scorching Protection",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Krolik/Affinity Key - Scorching Protection.png"
      },
      {
        "node": "Common Key - Art of Violence",
        "level": "40",
        "keyName": "Common Key - Art of Violence",
        "description": "CRIT +3.0% / If under the effects of a Burn buff, gains immunity to Frozen and Frigid, and increases damage dealt by 5%.",
        "icon": "assets/Krolik/Common Key - Art of Violence.png"
      },
      {
        "node": "Expansion Key - Aerial Bunny Assault",
        "level": "60",
        "keyName": "Expansion Key - Aerial Bunny Assault",
        "description": "Before attacking, for each tile moved, increases CRIT rate and CRIT DMG of this attack by 5%, up to 15%",
        "icon": "assets/Krolik/Expansion Key - Aerial Bunny Assault.png"
      }
    ]
  },
  "Colphne": {
    "class": "Support",
    "stats": {
      "hp": 1787,
      "atk": 515,
      "def": 503
    },
    "stabilityGauge": 10,
    "movementSpeed": 7,
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
        "name": "Quick Reaction",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Colphne/Quick Reaction.png"
      },
      {
        "name": "Crisis Aid",
        "traits": [
          "Active",
          "Healing",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 allied target within 6 tiles, restoring their HP equal to 100% of attack and applies Continuous Healing II and Continuous Stability Regen I to them for 1 turn. Gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If the target's HP is fully restored after healing, randomly grant it 1 buff for 2 turns."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Doctor's Orders",
            "effect": "The active skill Crisis Aid applies Defense Up I and Shelter to the target for 1 turn."
          }
        ],
        "icon": "assets/Colphne/Crisis Aid.png"
      },
      {
        "name": "Faint Glow of the Battlefield",
        "traits": [
          "Active",
          "Targeted",
          "Healing"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, dealing Hydro damage equal to 130% of attack. Additionally, restores HP equal to 100% of attack to the allied unit with the lowest HP.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Gains 1 extra Action Support this turn."
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Emergency Express",
            "effect": "The effects of the active skill Faint Glow of the Battlefield is enhanced. It also recovers HP to allied targets within 3 tiles."
          }
        ],
        "icon": "assets/Colphne/Faint Glow of the Battlefield.png"
      },
      {
        "name": "Emergency Treatment",
        "traits": [
          "Ultimate",
          "Healing",
          "Stability Regen",
          "Cleanse"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 allied target within 8 tiles, restoring HP equal to 140% of attack and 4 points of stability, cleansing 2 debuffs alongside removing Taunt and Fear effects.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Healing multiplier increased by 10%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increases Stability Index Recovery by 1 point."
          }
        ],
        "icon": "assets/Colphne/Emergency Treatment.png"
      },
      {
        "name": "Medical Contingency",
        "traits": [
          "Passive",
          "Support",
          "Stability Regen"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "When an enemy unit within range receives targeted damage from an allied unit, prioritizes performing 1 instance of Action Support, dealing Physical damage equal to 80% of attack and 3 points of Stability Damage to them, and applies Attack Up I to the allied unit for 2 turns. Gains 1 point of Confectance Index. This can be triggered once per turn.\n\nWhen applying an active heal to an allied unit, if the target is in Stability Break, additionally restores 2 points of Stability Index. Cooldown: 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Stability Index recovery increases by 2 points."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Cooldown reduced by 1 turn."
          }
        ],
        "icon": "assets/Colphne/Medical Contingency.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Crisis Aid",
        "level": "2",
        "effect": "If the target's HP is fully restored after healing, randomly grant it 1 buff for 2 turns."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Faint Glow of the Battlefield",
        "level": "2",
        "effect": "Gains 1 extra Action Support this turn."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Medical Contigency",
        "level": "2",
        "effect": "Stability Index recovery increases by 2 points."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Emergency Treatment",
        "level": "2",
        "effect": "Healing multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Medical Contigency",
        "level": "3",
        "effect": "Cooldown reduced by 1 turn."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Emergency Treatment",
        "level": "3",
        "effect": "Increases Stability Index Recovery by 1 point."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Doctor's Orders",
        "level": "20",
        "keyName": "Fixed Key 1 - Doctor's Orders",
        "description": "The active skill Crisis Aid applies Defense Up I and Shelter to the target for 1 turn.",
        "icon": "assets/Colphne/Fixed Key 1 - Doctor's Orders.png"
      },
      {
        "node": "Fixed Key 2 - Quick Surgery",
        "level": "20",
        "keyName": "Fixed Key 2 - Quick Surgery",
        "description": "If an allied target enters into Stability Break after being attacked, gain Movement Up II for 1 turn for self.",
        "icon": "assets/Colphne/Fixed Key 2 - Quick Surgery.png"
      },
      {
        "node": "Fixed Key 3 - Emergency Express",
        "level": "30",
        "keyName": "Fixed Key 3 - Emergency Express",
        "description": "The effects of the active skill Faint Glow of the Battlefield is enhanced. It also recovers HP to allied targets within a 3 tiles.",
        "icon": "assets/Colphne/Fixed Key 3 - Emergency Express.png"
      },
      {
        "node": "Fixed Key 4 - Combat Medic",
        "level": "30",
        "keyName": "Fixed Key 4 - Combat Medic",
        "description": "When the HP of the user is above 80%, increases their attack by 10%.",
        "icon": "assets/Colphne/Fixed Key 4 - Combat Medic.png"
      },
      {
        "node": "Fixed Key 5 - Recovery at Rest",
        "level": "40",
        "keyName": "Fixed Key 5 - Recovery at Rest",
        "description": "Randomly cleanses 1 debuff from the target after healing.",
        "icon": "assets/Colphne/Fixed Key 5 - Recovery at Rest.png"
      },
      {
        "node": "Fixed Key 6 - Fast Recovery",
        "level": "40",
        "keyName": "Fixed Key 6 - Fast Recovery",
        "description": "When using active heals on targets below 50% HP, increases healing effect by 20%.",
        "icon": "assets/Colphne/Fixed Key 6 - Fast Recovery.png"
      },
      {
        "node": "Affinity Key - Healing Treatment",
        "level": "-",
        "keyName": "Affinity Key - Healing Treatment",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Colphne/Affinity Key - Healing Treatment.png"
      },
      {
        "node": "Common Key - Fabricated Life",
        "level": "40",
        "keyName": "Common Key - Fabricated Life",
        "description": "HP +3.0% / Before using a single target active heal, cleanses 1 random debuff from the target.",
        "icon": "assets/Colphne/Common Key - Fabricated Life.png"
      },
      {
        "node": "Expansion Key - Emotional Counselling Expert",
        "level": "60",
        "keyName": "Expansion Key - Emotional Counselling Expert",
        "description": "When performing Action Support, the allied unit performing the Targeted attack recovers HP equal to 50% of ATK and 1 point of Stability.",
        "icon": "assets/Colphne/Expansion Key - Emotional Counselling Expert.png"
      }
    ]
  },
  "Sharkry": {
    "class": "Sentinel",
    "stats": {
      "hp": 1706,
      "atk": 679,
      "def": 463
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Medium Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Love Shot",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Sharkry/Love Shot.png"
      },
      {
        "name": "Boiling Soundwaves",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles, applies Overburn for 1 turns, and deals Burn damage equal to 140% of attack to them. If the user is under the effects of Zoom in, increases Stability Damage dealt by 1 point.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the duration of Overburn by 1 turn."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Target Is Your Heart",
            "effect": "When using the active skill Boiling Soundwaves, if a kill is scored, gains 1 stack of Zoom In."
          }
        ],
        "icon": "assets/Sharkry/Boiling Soundwaves.png"
      },
      {
        "name": "Perfect Rising Tone",
        "traits": [
          "Active",
          "Targeted",
          "Buff",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles, dealing Physical damage equal to 150% of attack to them. Gains Zoom In. If the target is inflicted with Overburn, applies 2 stacks of Flammable before the attack, and changes the damage type to Burn damage.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If a kill is scored, gains 1 additional stack of Zoom In."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Idol Training Day",
            "effect": "When using the active skill Perfect Rising Tone, if the target has Overburn, gains Blazing Assault II before the attack for 2 turns."
          }
        ],
        "icon": "assets/Sharkry/Perfect Rising Tone.png"
      },
      {
        "name": "Highlight Moment",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "Self",
        "effArea": "Target",
        "description": "Gains 1 stack of Zoom In and 1 instance of Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The user gains Damage Up I for 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "The effects of Zoom In are enhanced, increasing damage dealt by 5%."
          }
        ],
        "icon": "assets/Sharkry/Highlight Moment.png"
      },
      {
        "name": "Makeup Organization",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of action, gains 1 point of Confectance Index. When Overburn is applied to an enemy target, gains 1 point of Confectance Index. Critical rate increases by 20% against targets with Overburn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Critical rate is incresed by 10% against targets with Overburn. Critical damage is increased by 3% for each active buff, up to a maximum of 15%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "At the start of action, gains 1 stack of Zoom In."
          }
        ],
        "icon": "assets/Sharkry/Makeup Organization.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Boiling Soundwaves",
        "level": "2",
        "effect": "Increases the duration of Overburn by 1 turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Highlight Moment",
        "level": "2",
        "effect": "The user gains Damage Up I for 1 turn."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Perfect Rising Tone",
        "level": "2",
        "effect": "If a kill is scored, gains 1 additional stack of Zoom In."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Makeup Organisation",
        "level": "2",
        "effect": "Critical rate is incresed by 10% against targets with Overburn. Critical damage is increased by 3 % for each active buff, up to a maximum of 15%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Highlight Moment",
        "level": "3",
        "effect": "The effects of Zoom In are enhanced, increasing damage dealt by 5%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Makeup Organisation",
        "level": "3",
        "effect": "At the start of action, gains 1 stack of Zoom In."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Devilish Whisper",
        "level": "20",
        "keyName": "Fixed Key 1 - Devilish Whisper",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Sharkry/Fixed Key 1 - Devilish Whisper.png"
      },
      {
        "node": "Fixed Key 2 - Thermal Feedback",
        "level": "20",
        "keyName": "Fixed Key 2 - Thermal Feedback",
        "description": "When an enemy target within range is affected by Overburn, perform 1 instance of Wise Support, dealing Physical damage equal to 80% of attack and 2 points of Stability Damage to them. This can be triggered up to 3 times per turn.",
        "icon": "assets/Sharkry/Fixed Key 2 - Thermal Feedback.png"
      },
      {
        "node": "Fixed Key 3 - Deadly Allure",
        "level": "30",
        "keyName": "Fixed Key 3 - Deadly Allure",
        "description": "At the start of this unit's action, if there is an enemy with Overburn on the field, gains Blazing Assault II for 1 turn.",
        "icon": "assets/Sharkry/Fixed Key 3 - Deadly Allure.png"
      },
      {
        "node": "Fixed Key 4 - Idol Training Day",
        "level": "30",
        "keyName": "Fixed Key 4 - Idol Training Day",
        "description": "When using the active skill Perfect Rising Tone, if the target has Overburn, gains Blazing Assault II before attack for 2 turns.",
        "icon": "assets/Sharkry/Fixed Key 4 - Idol Training Day.png"
      },
      {
        "node": "Fixed Key 5 - Target Is Your Heart",
        "level": "40",
        "keyName": "Fixed Key 5 - Target Is Your Heart",
        "description": "When using the active skill Boiling Soundwaves, if a kill is scored, gain 1 stack of Zoom In.",
        "icon": "assets/Sharkry/Fixed Key 5 - Target Is Your Heart.png"
      },
      {
        "node": "Fixed Key 6 - Palm-Blown Kiss",
        "level": "40",
        "keyName": "Fixed Key 6 - Palm-Blown Kiss",
        "description": "When attacking a target with Overburn, restores 20% of max HP.",
        "icon": "assets/Sharkry/Fixed Key 6 - Palm-Blown Kiss.png"
      },
      {
        "node": "Affinity Key - Idol's Determination",
        "level": "-",
        "keyName": "Affinity Key - Idol's Determination",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Sharkry/Affinity Key - Idol's Determination.png"
      },
      {
        "node": "Common Key - Opening Fireworks",
        "level": "40",
        "keyName": "Common Key - Opening Fireworks",
        "description": "CRIT +3.0% / If the unit has more than 1 buff, increase damage dealt by 7%.",
        "icon": "assets/Sharkry/Common Key - Opening Fireworks.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "Damage dealt by Wise Support is changed to Burn damage.",
        "icon": "assets/Sharkry/Expansion Key.png"
      }
    ]
  },
  "Cheeta": {
    "class": "Support",
    "stats": {
      "hp": 1842,
      "atk": 591,
      "def": 494
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Welcome Gift",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal of 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Cheeta/Welcome Gift.png"
      },
      {
        "name": "Spicy Candy",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within a 6 tiles, dealing Burn damage equal to 130% of attack. If the user has Blazing Assault, this attack's damage is further increased by 20%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Damage multiplier increased by 10%."
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Goldfinger",
            "effect": "The active skill Spicy Candy gains a new effect: When the user has Blazing Assault, restores HP equal to 100% of attack to the nearest allied target (excluding the user)."
          }
        ],
        "icon": "assets/Cheeta/Spicy Candy.png"
      },
      {
        "name": "Fireworks Festival",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "2",
        "description": "Selects 1 enemy target within 6 tiles to attack, dealing AoE Physical damage equal to 80% of attack to them and all enemy targets within 2 tiles. If only 1 target is hit, applies Overheating to them for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Reduces Confectance Index consumption by 1 point."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Genius Support Plan",
            "effect": "The active skill Fireworks Festival no longer deals damage to enemy targets. Its effect is modified to restore HP equal to 90% of attack to allied targets within range and cleanses 1 debuff."
          }
        ],
        "icon": "assets/Cheeta/Fireworks Festival.png"
      },
      {
        "name": "Surprise Box",
        "traits": [
          "Ultimate",
          "Buff",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "6",
        "description": "Apply Blazing Assault II and 2 random buffs to all allied targets within 6 tiles for 2 turns. For each allied unit in range, gains 1 points of Confectance Index. Gain Support, which can be activated up to 2 times per turn for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The number of random buffs granted increases by 1."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Confectance Index gain increases by 1 point."
          }
        ],
        "icon": "assets/Cheeta/Surprise Box (row 99).png"
      },
      {
        "name": "Invention of the Century",
        "traits": [
          "Passive",
          "Healing"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "7",
        "description": "When the user is under the effects of buffs, after attacking, restores HP equal to 45% of attack to the allied target with the lowest HP within 7 tiles. Each buff increases the healing multiplier by 5%, up to a maximum of 15%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases the healing multiplier by 10% for each buff the user has, up to a maximum of 30%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the healing multiplier by 15%."
          }
        ],
        "icon": "assets/Cheeta/Invention of the Century.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Surprise Box",
        "level": "2",
        "effect": "The number of random buffs granted increases by 1."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Spicy Candy",
        "level": "2",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Fireworks Festival",
        "level": "2",
        "effect": "Reduces Confectance Index consumption by 1 point."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Invention of the Century",
        "level": "2",
        "effect": "Increases the healing multiplier by 10% for each buff the user has, up to a maximum of 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Invention of the Century",
        "level": "3",
        "effect": "Increases the healing multiplier by 15%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Surprise Box",
        "level": "3",
        "effect": "Confectance Index gain increases by 1 point."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Legitimate Research Expenses",
        "level": "20",
        "keyName": "Fixed Key 1 - Legitimate Research Expenses",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Cheeta/Fixed Key 1 - Legitimate Research Expenses.png"
      },
      {
        "node": "Fixed Key 2 - Super Useful Invention",
        "level": "20",
        "keyName": "Fixed Key 2 - Super Useful Invention",
        "description": "Increases Action Support's range by 2 tiles.",
        "icon": "assets/Cheeta/Fixed Key 2 - Super Useful Invention.png"
      },
      {
        "node": "Fixed Key 3 - Goldfinger",
        "level": "30",
        "keyName": "The active skill Spicy Candy gains a new effect",
        "description": "When the user has Blazing Assault, restores HP equal to 100% of attack to the nearest allied target (excluding the user).",
        "icon": "assets/Cheeta/The active skill Spicy Candy gains a new effect.png"
      },
      {
        "node": "Fixed Key 4 - Big Prank",
        "level": "30",
        "keyName": "Fixed Key 4 - Big Prank",
        "description": "Attack is increased by 3% for each buff the user has, up to a maximum of 15%.",
        "icon": "assets/Cheeta/Fixed Key 4 - Big Prank.png"
      },
      {
        "node": "Fixed Key 5 - Genius Support Plan",
        "level": "40",
        "keyName": "Fixed Key 5 - Genius Support Plan",
        "description": "The active skill Fireworks Festival no longer deals damage to enemy targets. Its effect is modified to restore HP equal to 90% of attack to allied targets within range and cleanses 1 debuff.",
        "icon": "assets/Cheeta/Fixed Key 5 - Genius Support Plan.png"
      },
      {
        "node": "Fixed Key 6 - Genius' Pride",
        "level": "40",
        "keyName": "Fixed Key 6 - Genius' Pride",
        "description": "If Blazing Assault is present at the end of the action, restore HP equal to 20% of attack to self.",
        "icon": "assets/Cheeta/Fixed Key 6 - Genius' Pride.png"
      },
      {
        "node": "Affinity Key - Genius' Luck",
        "level": "-",
        "keyName": "Affinity Key - Genius' Luck",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Cheeta/Affinity Key - Genius' Luck.png"
      },
      {
        "node": "Common Key - Overengineered Invention",
        "level": "40",
        "keyName": "Common Key - Overengineered Invention",
        "description": "ATK +3.0% / When using an active heal, there is a 50% chance to apply 1 random buff to the target for 1 turn.",
        "icon": "assets/Cheeta/Common Key - Overengineered Invention.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Surprise Box",
        "description": "After using an active attack, reduces cooldown of this skill by 2 turns",
        "icon": "assets/Cheeta/Surprise Box (row 186).png"
      }
    ]
  },
  "Nagant": {
    "class": "Support",
    "stats": {
      "hp": 1656,
      "atk": 609,
      "def": 512
    },
    "stabilityGauge": 10,
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
        "name": "Point Shooting",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Nagant/Point Shooting.png"
      },
      {
        "name": "Senior's Admonishment",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deal Physical damage equal to 130% of attack to it. After activating if the target is under the effects of Stability Break, apply Acid Corrosion II to the target for 1 turn.",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Bullet of Justice",
            "effect": "When using the active skill Senior's Admonishment, if it causes Stability Break on the enemy target, deal additional fixed damage equal to 50% of attack."
          }
        ],
        "icon": "assets/Nagant/Senior's Admonishment.png"
      },
      {
        "name": "Friend of Justice",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 70% of attack. If there are no enemy units within 4 tiles, performs an additional attack on the original target and applies Acid Corrosion II to them for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If the target has a defense debuff, this skill's cooldown is reduced by 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If there are no enemies within 3 tiles around self, perform an additional attack on the original target."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Legend of Guardians",
            "effect": "When using Friend of Justice, if it hits 2 times, the first hit deals Physical damage equal to 10% of attack, and the second hit deals 130% of attack."
          }
        ],
        "icon": "assets/Nagant/Friend of Justice.png"
      },
      {
        "name": "Sanction Declaration",
        "traits": [
          "Ultimate",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Corrosion damage equal to 150% of attack to them. If the target has defense debuffs, applies Vulnerable I before attacking for 2 turns. Stability Damage dealt by this attack is increased by 2 points.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If the target has defense debuffs, increases critical rate by 20%."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage multiplier increased by 10%."
          }
        ],
        "icon": "assets/Nagant/Sanction Declaration.png"
      },
      {
        "name": "Veteran's Skills",
        "traits": [
          "Passive",
          "Debuff",
          "Control"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "For each instance of damage dealt, gains 1 point of Confectance Index. If an enemy unit moves within Nagant's range, she deals Physical damage equal to 50% of attack and 2 points of Stability Damage. If the target has a defense debuff, applies Stun to the target for 1 turn. This effect can only be triggered once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage multiplier increases by 30% and deals 3 points of Stability Damage."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increase the trigger count by 1 every turn."
          }
        ],
        "icon": "assets/Nagant/Veteran's Skills.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Friend of Justice",
        "level": "2",
        "effect": "If the target has a defense debuff, this skill's cooldown is reduced by 1 turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Sanction Declaration",
        "level": "2",
        "effect": "If the target has defense debuffs, increases critical rate by 20%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Friend of Justice",
        "level": "3",
        "effect": "If there are no enemies within 3 tiles around self, perform an additional attack on the original target."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Sanction Declaration",
        "level": "3",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Veteran's Skills",
        "level": "2",
        "effect": "Damage multiplier increases by 30% and deals 3 points of Stability Damage."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Veteran's Skills",
        "level": "3",
        "effect": "Increase the trigger count by 1 every turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Heroic Strike",
        "level": "20",
        "keyName": "Fixed Key 1 - Heroic Strike",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Nagant/Fixed Key 1 - Heroic Strike.png"
      },
      {
        "node": "Fixed Key 2 - Veteran's Experience",
        "level": "20",
        "keyName": "Fixed Key 2 - Veteran's Experience",
        "description": "If attacking enemy targets with defensive debuffs, reduces the cooldown of all active skills by 1 turn.",
        "icon": "assets/Nagant/Fixed Key 2 - Veteran's Experience.png"
      },
      {
        "node": "Fixed Key 3 - Invisible Bulletproof Vest",
        "level": "30",
        "keyName": "Fixed Key 3 - Invisible Bulletproof Vest",
        "description": "If attacked by enemy targets with debuffs, reduce damage taken by 10%.",
        "icon": "assets/Nagant/Fixed Key 3 - Invisible Bulletproof Vest.png"
      },
      {
        "node": "Fixed Key 4 - Legend of Guardians",
        "level": "30",
        "keyName": "Fixed Key 4 - Legend of Guardians",
        "description": "When using Friend of Justice, if it hits 2 times, the first hit deals Physical damage equal to 10% of attack, and the second hit deals 130% of attack.",
        "icon": "assets/Nagant/Fixed Key 4 - Legend of Guardians.png"
      },
      {
        "node": "Fixed Key 5 - One Shot, One Victory",
        "level": "40",
        "keyName": "Fixed Key 5 - One Shot, One Victory",
        "description": "If the target has defense debuffs, increases critical rate and critical damage by 10%.",
        "icon": "assets/Nagant/Fixed Key 5 - One Shot, One Victory.png"
      },
      {
        "node": "Fixed Key 6 - Bullet of Justice",
        "level": "40",
        "keyName": "Fixed Key 6 - Bullet of Justice",
        "description": "When using the active skill Senior's Admonishment, if it causes Stability Break on the enemy target, deal additional fixed damage equal to 50% of attack.",
        "icon": "assets/Nagant/Fixed Key 6 - Bullet of Justice.png"
      },
      {
        "node": "Affinity Key - Hat Trick",
        "level": "-",
        "keyName": "Affinity Key - Hat Trick",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Nagant/Affinity Key - Hat Trick.png"
      },
      {
        "node": "Common Key - Veteran's Wisdom",
        "level": "40",
        "keyName": "Common Key - Veteran's Wisdom",
        "description": "ATK +3.0% / If target's Stability Index is lower than this unit's, increases damage dealt to them by 7%.",
        "icon": "assets/Nagant/Common Key - Veteran's Wisdom.png"
      },
      {
        "node": "Expansion Key - Senior's Intructions",
        "level": "40",
        "keyName": "Expansion Key - Senior's Intructions",
        "description": "After using an active attack, applies Stun on the target for 2 turns. In the current battle, if Stun is applied on the same target multiple times, Stun lasts for 1 turn instead",
        "icon": "assets/Nagant/Expansion Key - Senior's Intructions.png"
      }
    ]
  },
  "Ksenia": {
    "class": "Support",
    "stats": {
      "hp": 1842,
      "atk": 539,
      "def": 463
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Special Discount",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Ksenia/Special Discount.png"
      },
      {
        "name": "Favorable Cycle",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 2,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, deal Physical damage equal to 75% of attack to it and apply 2 stacks of Flammable, as well as Overburn for 1 turn. If under the effects of 2 or more Burn buffs, performs an additional attack on the original target, dealing Burn damage equal to 75% of attack and 2 Stability Damage.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Apply Overburn for 1 turn after the first attack."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Equivalent Exchange",
            "effect": "When using Favorable Cycle, for each kill made, increases the maximum number of Action Support uses this turn by 1"
          }
        ],
        "icon": "assets/Ksenia/Favorable Cycle.png"
      },
      {
        "name": "Comprehensive Rescue",
        "traits": [
          "Active",
          "Healing",
          "Stability Regen",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 allied target within 6 tiles, restoring HP equal to 130% of attack, 2 points of Stability Index, and applies Heat Recovery. If the target's HP is fully restored after healing, applies Blazing Assault II for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "If the target's HP is fully restored after healing and wasn't full before that, additionally restores 2 points of their Stability Index."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Mutual Benefit",
            "effect": "When using Comprehensive Rescue, the user gains the same buffs"
          }
        ],
        "icon": "assets/Ksenia/Comprehensive Rescue.png"
      },
      {
        "name": "The Secret of Making Money",
        "traits": [
          "Ultimate",
          "Targeted",
          "Buff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 5,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "The user gains Heat Recovery and Blazing Assault II for 2 turns. Select 1 enemy target within 6 tiles and deal Burn damage equal to 160% of attack to it.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If a Phase Weakness is exploited, increases damage dealt by 20%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "When attacking targets with Overburn, increase critical rate by 100%."
          }
        ],
        "icon": "assets/Ksenia/The Secret of Making Money.png"
      },
      {
        "name": "Passion for Shopping",
        "traits": [
          "Passive",
          "Support",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "When an enemy unit within range receives targeted damage from an allied unit, prioritizes performing 1 instance of Action Support, dealing Physical damage equal to 80% of attack and 3 points of Stability Damage to the enemy unit, and applies Blazing Assault II to the allied unit for 2 turns. This can be triggered up to once per turn.\n\nWhen under the effects of Heat Recovery, Stability Damage is increased by 1 point respectively. At the end of the action, gains 1 point of Confectance Index for each Burn buff.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "When under the effects of Blazing Assault, increases Stability Damage dealt by 1 point."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The maximum amount of times that Action Support can trigger increases by 1."
          }
        ],
        "icon": "assets/Ksenia/Passion for Shopping.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Favorable Cycle",
        "level": "2",
        "effect": "Apply Overburn for 1 turn after the first attack."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Passion for Shopping",
        "level": "2",
        "effect": "When under the effects of Blazing Assault, increases Stability Damage dealt by 1 point."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "The Secret of Making Money",
        "level": "2",
        "effect": "If a phase weakness is exploited, increases damage dealt by 20%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Passion for Shopping",
        "level": "3",
        "effect": "The maximum amount of times that Action Support can trigger increases by 1."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Comprehensive Rescue",
        "level": "2",
        "effect": "If the target's HP is fully restored after healing and wasn't full before that, additionally restores 2 points of their Stability Index."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "The Secret of Making Money",
        "level": "3",
        "effect": "When attacking targets with Overburn, increase critical rate by 100%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Win-Win Partnership",
        "level": "20",
        "keyName": "Fixed Key 1 - Win-Win Partnership",
        "description": "When healing an allied target other than the user, applies 1 random buff to them and the user.",
        "icon": "assets/Ksenia/Fixed Key 1 - Win-Win Partnership.png"
      },
      {
        "node": "Fixed Key 2 - Equivalent Exchange",
        "level": "20",
        "keyName": "Fixed Key 2 - Equivalent Exchange",
        "description": "When using Favorable Cycle, for each kill made, increases the maximum number of Action Support uses this turn by 1.",
        "icon": "assets/Ksenia/Fixed Key 2 - Equivalent Exchange.png"
      },
      {
        "node": "Fixed Key 3 - Steady Income",
        "level": "30",
        "keyName": "Fixed Key 3 - Steady Income",
        "description": "After dealing Burn damage, restores HP equal to 10% of damage and 1 point of Stability Index.",
        "icon": "assets/Ksenia/Fixed Key 3 - Steady Income.png"
      },
      {
        "node": "Fixed Key 4 - Mutual Benefit",
        "level": "30",
        "keyName": "Fixed Key 4 - Mutual Benefit",
        "description": "When using Comprehensive Rescue, the user gains the same buffs",
        "icon": "assets/Ksenia/Fixed Key 4 - Mutual Benefit.png"
      },
      {
        "node": "Fixed Key 5 - Friendship Gift",
        "level": "40",
        "keyName": "Fixed Key 5 - Friendship Gift",
        "description": "When applying a Burn buff, additiionally cleanses 1 debuff.",
        "icon": "assets/Ksenia/Fixed Key 5 - Friendship Gift.png"
      },
      {
        "node": "Fixed Key 6 - Discount Guide",
        "level": "40",
        "keyName": "Fixed Key 6 - Discount Guide",
        "description": "If the user possesses Heat Recovery at the end of the action, gains 1 point of Confectance Index.",
        "icon": "assets/Ksenia/Fixed Key 6 - Discount Guide.png"
      },
      {
        "node": "Affinity Key - Making Money",
        "level": "-",
        "keyName": "Affinity Key - Making Money",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Ksenia/Affinity Key - Making Money.png"
      },
      {
        "node": "Common Key - Blazing Inferno",
        "level": "40",
        "keyName": "Common Key - Blazing Inferno",
        "description": "HP +3.0% / When applying a Burn buff, there is a 50% chance to apply 1 additional buff to the target for 1 turn.",
        "icon": "assets/Ksenia/Common Key - Blazing Inferno.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "At the end of the action, restores 2 Stability for the ally with the lowest Stability",
        "icon": "assets/Ksenia/Expansion Key.png"
      }
    ]
  },
  "Littara": {
    "class": "Sentinel",
    "stats": {
      "hp": 1656,
      "atk": 670,
      "def": 487
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Heavy Ammo"
    ],
    "weaknesses": [
      "Light Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Quick Writing",
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
        "icon": "assets/Littara/Quick Writing.png"
      },
      {
        "name": "Perfect Opportunity",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "2",
        "description": "Selects 1 enemy target within 8 tiles to attack, dealing AoE Physical damage equal to 70% of attack to them and all enemy targets within a 2 tiles, applying Vulnerable I for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Damage multiplier increased by 10%."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Battle Analysis",
            "effect": "When using the active skill Perfect Opportunity, applies Attack Down I to all targets for 2 turns."
          }
        ],
        "icon": "assets/Littara/Perfect Opportunity.png"
      },
      {
        "name": "Reliable Cover",
        "traits": [
          "Active",
          "AoE",
          "Debuff",
          "Cover Destruction"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 1,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Select 1 direction  around self, deal AoE Physical damage equal to 65% of attack to all enemy targets within a 3x8 area, 2 tiles away in the selected direction and apply Defense Down II for 2 turns. Destroy all destructible Cover within that area, excluding a 3x3 area around self. For each target hit, reduce this skill's cooldown by 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The effect range increases to 3x8 tiles in front."
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Aggresive Attack",
            "effect": "Before using the active skill Reliable Cover, if no movement has been made, changes the type of damage dealt to AoE Burn damage."
          }
        ],
        "icon": "assets/Littara/Reliable Cover.png"
      },
      {
        "name": "Strategist's Plan",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "8",
        "effArea": "2",
        "description": "Selects 1 tile within 8 tiles to launch an attack, dealing AoE Physical damage equal to 85% of attack to all enemy targets within 2 tiles. If the target has a defense debuff, change the damage dealt to AoE Physical damage equal to 95% of attack and 4 points of Stability Damage. Additionally, damage dealt to targets with defense debuffs is increased by 20%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage dealt to targets with defense debuffs is increased by 20%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Confectance Index consumption is reduced by 2 points."
          }
        ],
        "icon": "assets/Littara/Strategist's Plan.png"
      },
      {
        "name": "Systematic Breakdown",
        "traits": [
          "Passive",
          "AoE"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "8",
        "description": "At the end of the action, deals AoE Physical damage equal to 30% of attack and 1 point of Stability Damage to the nearest target within range under a defense debuff, and gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increase damage multiplier by 20%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Deals damage to 2 nearest enemy targets within range with a defense debuff."
          }
        ],
        "icon": "assets/Littara/Systematic Breakdown.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Perfect Opportunity",
        "level": "2",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Reliable Cover Fire",
        "level": "2",
        "effect": "The effect range increases to 3x8 tiles in front."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Systematic Breakdown",
        "level": "2",
        "effect": "Increase damage multiplier by 20%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Strategist's Plan",
        "level": "2",
        "effect": "Damage dealt to targets with defense debuffs is increased by 20%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Strategist's Plan",
        "level": "3",
        "effect": "Confectance Index consumption is reduced by 2 points."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Systematic Breakdown",
        "level": "3",
        "effect": "Deals damage to 2 nearest enemy targets within range with a defense debuff."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Strategic Planning",
        "level": "20",
        "keyName": "Fixed Key 1 - Strategic Planning",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Littara/Fixed Key 1 - Strategic Planning.png"
      },
      {
        "node": "Fixed Key 2 - Gaining Experience",
        "level": "20",
        "keyName": "Fixed Key 2 - Gaining Experience",
        "description": "Gain 1 point of Confectance Index for every 3 instances of damage dealt.",
        "icon": "assets/Littara/Fixed Key 2 - Gaining Experience.png"
      },
      {
        "node": "Fixed Key 3 - Press the Advantage",
        "level": "30",
        "keyName": "Fixed Key 3 - Press the Advantage",
        "description": "When exploiting a Phase Weakness, randomly applies 1 debuff to the target after attacking for 2 turns.",
        "icon": "assets/Littara/Fixed Key 3 - Press the Advantage.png"
      },
      {
        "node": "Fixed Key 4 - Identifying Gaps",
        "level": "30",
        "keyName": "Fixed Key 4 - Identifying Gaps",
        "description": "If the target has defense debuffs, increases critical rate by 15%.",
        "icon": "assets/Littara/Fixed Key 4 - Identifying Gaps.png"
      },
      {
        "node": "Fixed Key 5 - Battle Analysis",
        "level": "40",
        "keyName": "Fixed Key 5 - Battle Analysis",
        "description": "When using the active skill Perfect Opportunity. applies Attack Down I to all targets for 2 turns.",
        "icon": "assets/Littara/Fixed Key 5 - Battle Analysis.png"
      },
      {
        "node": "Fixed Key 6 - Aggressive Attack",
        "level": "40",
        "keyName": "Fixed Key 6 - Aggressive Attack",
        "description": "Before using the active skill Reliable Cover, if no movement has been made, changes the type of damage dealt to AoE Burn damage.",
        "icon": "assets/Littara/Fixed Key 6 - Aggressive Attack.png"
      },
      {
        "node": "Affinity Key - Scribbled Thoughts",
        "level": "-",
        "keyName": "Affinity Key - Scribbled Thoughts",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Littara/Affinity Key - Scribbled Thoughts.png"
      },
      {
        "node": "Common Key - Vulnerability Exploit",
        "level": "40",
        "keyName": "Common Key - Vulnerability Exploit",
        "description": "CRIT +3.0% / damage dealt to targets with defense debuffs is increased by 7%.",
        "icon": "assets/Littara/Common Key - Vulnerability Exploit.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "If the target has Defense type debuffs, increases damage dealt by 10% and ignores 15% of the damage reduction from Cover",
        "icon": "assets/Littara/Expansion Key.png"
      }
    ]
  },
  "Vepley": {
    "class": "Vanguard",
    "stats": {
      "hp": 1851,
      "atk": 696,
      "def": 528
    },
    "stabilityGauge": 8,
    "movementSpeed": 8,
    "skillAttributes": [
      "Shotgun Ammo"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Live Interaction",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "5",
        "effArea": "Target",
        "description": "Select 1 enemy target within 5 tiles and deal Physical damage equal to 80% of attack to it.",
        "upgrades": [],
        "icon": "assets/Vepley/Live Interaction.png"
      },
      {
        "name": "All Out Performance",
        "traits": [
          "Active",
          "AoE",
          "Cover Destruction",
          "Displacement"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 1,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction, dealing Physical damage equal to 75% of attack to the first enemy target in each line within a 3x5 area in the selected direction, and knocks the target back by 4 tiles. Simultaneously, destroys any destructible Cover outside the 3x3 tile area around the user.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If 2 or more targets are hit, gain 3 tiles of  Additional Movement."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Contamination Zone Tour",
            "effect": "The range of All Out Performance changes to 5x3 tiles, knockback distance changes to 1 tile."
          }
        ],
        "icon": "assets/Vepley/All Out Performance.png"
      },
      {
        "name": "Exclusive Stage",
        "traits": [
          "Active",
          "Targeted",
          "Dispel"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "5",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 5 tiles and deal Physical damage equal to 150% of attack to it. If the target has movement debuffs, ignore 10% of Cover damage reduction. If the target is not protected by Cover, dispels 2 of its buffs before attacking.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If the target has movement debuffs, increase critical rate by 100%."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Dino Dash",
            "effect": "When using Exclusive Stage, ignores 10% of Cover damage reduction against targets with movement debuffs."
          }
        ],
        "icon": "assets/Vepley/Exclusive Stage.png"
      },
      {
        "name": "Infectious Enthusiasm",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "5",
        "effArea": "2",
        "description": "Selects 1 tile within 5 tiles to attack, dealing AoE Physical damage equal to 100% of attack to all enemy targets within 2 tiles. Additionally, this applies Overzealous and Vulnerable II to the targets for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Overzealous is now applied before the attack instead of after."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "If only 1 target is hit, applies Stun for 1 turn."
          }
        ],
        "icon": "assets/Vepley/Infectious Enthusiasm.png"
      },
      {
        "name": "Idol Talent",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Entire Map",
        "effArea": "Target",
        "description": "At the start of the action, gains 1 point of Confectance Index. For each instance of damage dealt, gains 1 point of Confectance Index. Damage dealt to targets with movement debuffs is increased by 20%. If this unit moved 5 or more tiles, applies Movement Down II to the target for 2 turns before attacking.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "If this unit moved 3 or more tiles, applies Movement Down II to the target before attacking."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "If the target has movement debuffs, applies Movement Denied to them for 1 turn."
          }
        ],
        "icon": "assets/Vepley/Idol Talent.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "All Out Performance",
        "level": "2",
        "effect": "If 2 or more targets are hit, gain 3 tiles of  Additional Movement."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Exclusive Stage",
        "level": "2",
        "effect": "If the target has movement debuffs, increase critical rate by 100%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Infectious Enthusiasm",
        "level": "2",
        "effect": "Overzealous is now applied before the attack instead of after."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Idol Talent",
        "level": "2",
        "effect": "If this unit moved 3 or more tiles, applies Movement Down II to the target before attacking."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Idol Talent",
        "level": "3",
        "effect": "If the target has movement debuffs, applies Movement Denied to them for 1 turn."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Infectious Enthusiasm",
        "level": "3",
        "effect": "If only 1 target is hit, applies Stun for 1 turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Safe Distance Viewing",
        "level": "20",
        "keyName": "Fixed Key 1 - Safe Distance Viewing",
        "description": "Increases Stability Damage dealt against enemy targets with movement debuffs by 2 points.",
        "icon": "assets/Vepley/Fixed Key 1 - Safe Distance Viewing.png"
      },
      {
        "node": "Fixed Key 2 - Contamination Zone Tour",
        "level": "20",
        "keyName": "Fixed Key 2 - Contamination Zone Tour",
        "description": "The range of All Out Performance changes to 5x3 tiles, knockback distance changes to 1 tile.",
        "icon": "assets/Vepley/Fixed Key 2 - Contamination Zone Tour.png"
      },
      {
        "node": "Fixed Key 3 - Fortune of an Idol",
        "level": "30",
        "keyName": "Fixed Key 3 - Fortune of an Idol",
        "description": "If there are no allied units within 6 tiles of the user, gain 1 stack of Quick Barrier at the end of the action.",
        "icon": "assets/Vepley/Fixed Key 3 - Fortune of an Idol.png"
      },
      {
        "node": "Fixed Key 4 - Dino Dash",
        "level": "30",
        "keyName": "Fixed Key 4 - Dino Dash",
        "description": "When using Exclusive Stage, ignores 10% of Cover damage reduction against targets with movement debuffs.",
        "icon": "assets/Vepley/Fixed Key 4 - Dino Dash.png"
      },
      {
        "node": "Fixed Key 5 - Stress Resistance Training",
        "level": "40",
        "keyName": "Fixed Key 5 - Stress Resistance Training",
        "description": "If there is Cover nearby, reduces AoE damage taken by 20%.",
        "icon": "assets/Vepley/Fixed Key 5 - Stress Resistance Training.png"
      },
      {
        "node": "Fixed Key 6 - Stage Commitment",
        "level": "40",
        "keyName": "Fixed Key 6 - Stage Commitment",
        "description": "When applying a movement debuff to a large target, additionally deals 1 instance of fixed damage equal to 15% of attack.",
        "icon": "assets/Vepley/Fixed Key 6 - Stage Commitment.png"
      },
      {
        "node": "Affinity Key - Grand Debut",
        "level": "-",
        "keyName": "Affinity Key - Grand Debut",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Vepley/Affinity Key - Grand Debut.png"
      },
      {
        "node": "Common Key - Heart Melting Strike",
        "level": "40",
        "keyName": "Common Key - Heart Melting Strike",
        "description": "ATK +5.0% / If the user's Mobility is greater than or equal to the target's, increases damage dealt by 7%.",
        "icon": "assets/Vepley/Common Key - Heart Melting Strike.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "Attacks ignore 15% of the target's DEF, if the target has movement debuffs, further ignores 15% DEF\n\nAll Out Performance: Applies Stun and Vulnerable II to targets for 2 turns",
        "icon": "assets/Vepley/Expansion Key.png"
      }
    ]
  },
  "Peritya": {
    "class": "Sentinel",
    "stats": {
      "hp": 1948,
      "atk": 765,
      "def": 536
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Light Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Rapid Overwrite",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to it.",
        "upgrades": [],
        "icon": "assets/Peritya/Rapid Overwrite.png"
      },
      {
        "name": "Fixed Erosion",
        "traits": [
          "Active",
          "AoE",
          "Dispel"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 1,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "3x3",
        "description": "Selects 1 enemy within 8 tiles, dealing AoE Corrosion damage equal to 85% of attack to the target and all enemies within a 3x3 area, and dispels 1 buff.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The number of buffs that can be dispelled is increased by 2."
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Friendly Contact",
            "effect": "Increases stability damage dealt to the primary target by the active skill Fixed Erosion by 4 points."
          }
        ],
        "icon": "assets/Peritya/Fixed Erosion.png"
      },
      {
        "name": "Domain Suppression",
        "traits": [
          "Active",
          "AoE",
          "Displacement"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "1",
        "description": "Select a tile within 8 tiles as the center. Deal AoE Physical damage equal to 90% of attack to all enemy targets within 1 tile of the center and pull them 1 tile towards it. For each target hit, reduce this skill's cooldown by 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Effective range is increased by 1 tile."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Lazy Resistance",
            "effect": "Increases the damage dealt by the active skill Domain Suppression to targets immune to displacement effects by 15%"
          }
        ],
        "icon": "assets/Peritya/Domain Suppression.png"
      },
      {
        "name": "Multi-Compilation",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "9x9",
        "description": "Deals AoE Corrosion damage equal to 100% of attck to all enemy targets within a 9x9 area centered on self, excluding the inner 5x5 area. For each target hit, increases damage dealt by 5%, up to 15%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "For each enemy target hit, increase additional damage by 5%, up to a 25% increase."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The excluded area is reduced to 3x3 within the 9x9 area centered on self."
          }
        ],
        "icon": "assets/Peritya/Multi-Compilation.png"
      },
      {
        "name": "Chain Reaction",
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
        "description": "When an enemy unit within range takes AoE damage from an allied unit, performs 1 instance of Action Support, dealing AoE Physical damage equal to 50% of attack and 1 point of Stability Damage, as well as gaining 1 point of Confectance Index. This effect can trigger up to 6 times per turn. \n\nBefore the attack, every 1 point of leftover mobility enhances the damage dealt by the attack by 10%, up to a maximum increase of 30%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "If no movement is made before performing an active attack, gain 2 points of Confectance Index after attacking."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Action Support can be triggered an additional 4 times per turn."
          }
        ],
        "icon": "assets/Peritya/Chain Reaction.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Fixed Erosion",
        "level": "2",
        "effect": "The number of buffs that can be dispelled is increased by 2."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Domain Suppression",
        "level": "2",
        "effect": "Effective range is increased by 1 tile."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Multi-Compilation",
        "level": "2",
        "effect": "For each enemy target hit, increase additional damage by 5%, up to a 25% increase."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Multi-Compilation",
        "level": "3",
        "effect": "The excluded area is reduced to 3x3 within the 9x9 area centered on self."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Chain Reaction",
        "level": "2",
        "effect": "If no movement is made before performing an active attack, gain 2 points of Confectance Index after attacking."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Chain Reaction",
        "level": "3",
        "effect": "Action Support can be triggered an additional 4 times per turn."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Temporary System Maintenance",
        "level": "20",
        "keyName": "Fixed Key 1 - Temporary System Maintenance",
        "description": "Gains 1 point of Confectance Index for every 10 points of stability damage dealt.",
        "icon": "assets/Peritya/Fixed Key 1 - Temporary System Maintenance.png"
      },
      {
        "node": "Fixed Key 2 - Impromptu Cat and Mouse Game",
        "level": "20",
        "keyName": "Fixed Key 2 - Impromptu Cat and Mouse Game",
        "description": "If there is remaining mobility before attacking, gains Movement Up II  at the end of the action for 1 turn.",
        "icon": "assets/Peritya/Fixed Key 2 - Impromptu Cat and Mouse Game.png"
      },
      {
        "node": "Fixed Key 3 - Automatic Repair Program",
        "level": "30",
        "keyName": "Fixed Key 3 - Automatic Repair Program",
        "description": "If no movement is made before attacking, cleanses 2 debuffs from self.",
        "icon": "assets/Peritya/Fixed Key 3 - Automatic Repair Program.png"
      },
      {
        "node": "Fixed Key 4 - Lazy Resistance",
        "level": "30",
        "keyName": "Fixed Key 4 - Lazy Resistance",
        "description": "Increases damage dealt by the active skill Domain Suppression to targets immune to displacement effects by 15%.",
        "icon": "assets/Peritya/Fixed Key 4 - Lazy Resistance.png"
      },
      {
        "node": "Fixed Key 5 - A Brief Respite",
        "level": "40",
        "keyName": "Fixed Key 5 - A Brief Respite",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Peritya/Fixed Key 5 - A Brief Respite.png"
      },
      {
        "node": "Fixed Key 6 - Friendly Contact",
        "level": "40",
        "keyName": "Fixed Key 6 - Friendly Contact",
        "description": "Increases Stability Damage dealt to the primary target by the active skill Fixed Erosion by 4 points.",
        "icon": "assets/Peritya/Fixed Key 6 - Friendly Contact.png"
      },
      {
        "node": "Affinity Key - Cat's Relaxation",
        "level": "-",
        "keyName": "Affinity Key - Cat's Relaxation",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Peritya/Affinity Key - Cat's Relaxation.png"
      },
      {
        "node": "Common Key - All Points to Damage",
        "level": "40",
        "keyName": "Common Key - All Points to Damage",
        "description": "CRIT +5.0% / If an active skill hits 2 or more enemy targets, damage dealt is increased by 7%.",
        "icon": "assets/Peritya/Common Key - All Points to Damage.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "When dealing Corrosion damage, for each debuff held by the target, increases damage dealt by 5%, up to a maximum of 25%\n\nMulti-Compilation pulls all enemies hit towards self by 2 tiles\n\nIn a single round, for every 2 instances of Action Support performed, the next Action Support deals AoE Corrosion damage equivalent to 50% ATK and 2 Stability Damage to the target and all enemies within a 3x3 radius of the target",
        "icon": "assets/Peritya/Expansion Key.png"
      }
    ]
  },
  "Sabrina": {
    "class": "Bulwark",
    "stats": {
      "hp": 2249,
      "atk": 609,
      "def": 642
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Shotgun Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "My Treat",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Sabrina/My Treat.png"
      },
      {
        "name": "Delicious Feast",
        "traits": [
          "Active",
          "AoE",
          "Debuff",
          "Stability Regen"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "2",
        "description": "Selects 1 enemy target within 6 tiles to attack, dealing AoE Hydro damage equal to 80% of attack to them and all enemy targets within 2 tiles, applying Movement Down II for 2 turns. Recovers 2 points of stability for each target hit.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If only 1 target is hit, restores 6 points of Stability Index."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Calorie Overload",
            "effect": "The effective range of Delicious Feast changes to 1 tile, the skill targets tiles instead of units and pulls all enemies 1 tile toward the center. Damage dealt increases to 100% of attack."
          }
        ],
        "icon": "assets/Sabrina/Delicious Feast.png"
      },
      {
        "name": "Meal Preparation",
        "traits": [
          "Active",
          "AoE",
          "Debuff",
          "Cover Destruction"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction and deals AoE Hydro damage equal to 70% of attack to all enemy targets within a 3x6 area in the selected direction, and applies Movement Down II for 2 turns. Destroys any destructible Cover outside a 3x3 area around self.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Damage multiplier increased by 10%."
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Weird-Tasting Health Recipe",
            "effect": "The active skill Meal Preparation is modified to affect 5 tiles around self, and no longer applies Movement Down II. It now applies Taunt to up to 2 targets for 1 turn. The cooldown is increased to 3 turns."
          }
        ],
        "icon": "assets/Sabrina/Meal Preparation.png"
      },
      {
        "name": "Gourmet Spirit",
        "traits": [
          "Ultimate",
          "Buff",
          "Defense",
          "Counter"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 5,
        "range": "Self",
        "effArea": "Entire Map",
        "description": "Apply 2 stacks of Shelter to all allied targets and gain Feeling Full for 3 turns. While having Feeling Full, if an enemy target within range deals targeted damage to an allied unit, use Counterattack against it, dealing Physical damage equal to 80% of attack and 4 points of Stability Damage. This can be triggered up to 3 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases attack of Feeling Full by 10%. Increases Stability Damage of Counterattack by 2 points."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "No longer consumes Confectance Index, gain Extra Command once."
          }
        ],
        "icon": "assets/Sabrina/Gourmet Spirit.png"
      },
      {
        "name": "Flexible Modification",
        "traits": [
          "Passive",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Before an allied unit is attacked, if they are within 7 tiles of Sabrina, applies 1 stack of Shelter to the ally. This can be triggered up to 4 times per turn. Sabrina gains 1 point of Confectance Index for each instance of damage she deals.\n\nAfter using a skill to attack, she generates Tideaway within the area. If Hydro tiles are already present in the area, a tile reaction is triggered, removing the tile and dealing fixed damage equal to 20% of attack to the enemy on the tile.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the number of times Shelter can be applied by 2."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "When Confectance is full, additionally consume 4 points of Confectance Index to increase skill damage by 30%."
          }
        ],
        "icon": "assets/Sabrina/Flexible Modification.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Flexible Modification",
        "level": "2",
        "effect": "Increases the number of times Shelter can be applied by 2."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Meal Preparation",
        "level": "2",
        "effect": "Damage multiplier increased by 10%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Delicious Feast",
        "level": "2",
        "effect": "If only 1 target is hit, restores 6 points of Stability Index."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Gourmet Spirit",
        "level": "2",
        "effect": "Increases attack of Feeling Full by 10%. Increases Stability Damage of Counterattack by 2 points."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Gourmet Spirit",
        "level": "3",
        "effect": "No longer consumes Confectance Index, gain Extra Command once."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Flexible Modification",
        "level": "3",
        "effect": "When Confectance is full, additionally consume 4 points of Confectance Index to increase skill damage by 30%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Eating is a Blessing",
        "level": "20",
        "keyName": "Fixed Key 1 - Eating is a Blessing",
        "description": "When under attack, defense is increased by 20%.",
        "icon": "assets/Sabrina/Fixed Key 1 - Eating is a Blessing.png"
      },
      {
        "node": "Fixed Key 2 - Delicious Sharing",
        "level": "20",
        "keyName": "Fixed Key 2 - Delicious Sharing",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Sabrina/Fixed Key 2 - Delicious Sharing.png"
      },
      {
        "node": "Fixed Key 3 - Let Everything Simmer",
        "level": "30",
        "keyName": "Fixed Key 3 - Let Everything Simmer",
        "description": "While on Hydro tiles, defense is increased by 30%, gaining immunity to displacement effects from enemy units and all abnormal Hydro terrain effects.",
        "icon": "assets/Sabrina/Fixed Key 3 - Let Everything Simmer.png"
      },
      {
        "node": "Fixed Key 4 - Eat Well, Sleep Well",
        "level": "30",
        "keyName": "Fixed Key 4 - Eat Well, Sleep Well",
        "description": "When Confectance Index is not full, recovers 2 points of Stability Index for each point of Confectance Index gained.",
        "icon": "assets/Sabrina/Fixed Key 4 - Eat Well, Sleep Well.png"
      },
      {
        "node": "Fixed Key 5 - Calorie Overload",
        "level": "40",
        "keyName": "Fixed Key 5 - Calorie Overload",
        "description": "The effective range of Delicious Feast changes to 1 tile, the skill targets tiles instead of units and pulls all enemies 1 tile toward the center. Damage dealt increases to 100% of attack.",
        "icon": "assets/Sabrina/Fixed Key 5 - Calorie Overload.png"
      },
      {
        "node": "Fixed Key 6 - Weird-Tasting Health Recipe",
        "level": "40",
        "keyName": "Fixed Key 6 - Weird-Tasting Health Recipe",
        "description": "The active skill Meal Preparation is modified to affect 5 tiles around self, and no longer applies Movement Down II. It now applies Taunt to up to 2 targets for 1 turn. The cooldown is increased to 3 turns.",
        "icon": "assets/Sabrina/Fixed Key 6 - Weird-Tasting Health Recipe.png"
      },
      {
        "node": "Affinity Key - Dessert Time",
        "level": "-",
        "keyName": "Affinity Key - Dessert Time",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Sabrina/Affinity Key - Dessert Time.png"
      },
      {
        "node": "Common Key -  Hot Oil Protection",
        "level": "40",
        "keyName": "Common Key -  Hot Oil Protection",
        "description": "DEF +5.0% / When dealing targeted damage, applies Movement Down II to the target for 1 turn.",
        "icon": "assets/Sabrina/Common Key -  Hot Oil Protection.png"
      },
      {
        "node": "Expansion Key - Recipe of Legend",
        "level": "60",
        "keyName": "Expansion Key - Recipe of Legend",
        "description": "Counterattack is changed to Hydro damage instead. If this triggers any Hydro type tile effect, the effects of the tile will not be removed. Every time Counterattack is performed, damage taken by Sabrina is reduced by 5%, stacking up to 30%, lasting for 2 turns.",
        "icon": "assets/Sabrina/Expansion Key - Recipe of Legend.png"
      }
    ]
  },
  "Qiongjiu": {
    "class": "Sentinel",
    "stats": {
      "hp": 1893,
      "atk": 802,
      "def": 528
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Medium Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Fuse",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Qiongjiu/Fuse.png"
      },
      {
        "name": "Common Rail",
        "traits": [
          "Active",
          "Targeted",
          "Buff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tile, dealing Burn damage equal to 150% of attack. Additionaly, this unit gains Support Boost I.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If a kill is scored, increases the damage bonus of Support Boost I to 30%."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Necessary Adjustments",
            "effect": "When a Phase Weakness is exploited using the active skill Common Rail, gains Blazing Assault II for 2 turns"
          }
        ],
        "icon": "assets/Qiongjiu/Common Rail.png"
      },
      {
        "name": "Guide to Victory",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "8",
        "description": "Selects 1 direction and deals AoE Burn damage equal to 110% of attack to the first enemy target within 8 tiles in the selected direction. Applies Overburn for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If the target is inflicted with Overburn, increases the critical rate of this attack by 100%."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Point of Vulnerability",
            "effect": "Modify the effects of the active skill Guide to Victory to deal damage to all enemy targets within 8 tiles in the selected direction. All enemy targets except the first receive 30% less damage"
          }
        ],
        "icon": "assets/Qiongjiu/Guide to Victory.png"
      },
      {
        "name": "Pressing the Momentum",
        "traits": [
          "Ultimate",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "Self",
        "effArea": "Target",
        "description": "Gains 3 stacks of Support Boost II. At max Confectance Index, gains 1 additional stack and increases the maximum number of Action Support this turn by 1.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Applies Vulnerable I to targets that are not protected by Cover for 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "When performing Action Support, applies Damage Up II to self and the allied unit for 1 turn before the aforementioned allied unit makes their attack."
          }
        ],
        "icon": "assets/Qiongjiu/Pressing the Momentum.png"
      },
      {
        "name": "Steady Plan",
        "traits": [
          "Passive",
          "Support",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Gains 1 point of Confectance Index each time after dealing damage. Increases damage dealt to targets not under the protection of Cover by 10%.\n\nWhen an enemy unit within range receives targeted damage from an ally, performs 1 instance of Action Support, dealing Physical damage equal to 90% of attack and 2 points of Stability Damage. This effect can be triggered up to 3 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "After Action Support, apply Overburn to the target for 2 turns. Action Support's damage increases by 10%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increases damage dealt by 10% against targets without Cover protection."
          }
        ],
        "icon": "assets/Qiongjiu/Steady Plan.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Common Rail",
        "level": "2",
        "effect": "If a kill is scored, increases the damage bonus of Support Boost I to 30%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Guide to Victory",
        "level": "2",
        "effect": "If the target is inflicted with Overburn, increases the critical rate of this attack by 100%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Steady Plan",
        "level": "2",
        "effect": "After Action Support, apply Overburn to the target for 2 turns. Action Support's damage increases by 10%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Pressing the Momentum",
        "level": "2",
        "effect": "Applies Vulnerable I to targets that are not protected by Cover for 1 turn."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Pressing the Momentum",
        "level": "3",
        "effect": "When performing Action Support, applies Damage Up II to self and the allied unit for 1 turn before the aforementioned allied unit makes their attack."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Steady Plan",
        "level": "3",
        "effect": "Increases damage deat by 10% against targets without Cover protection."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Concentration",
        "level": "20",
        "keyName": "Fixed Key 1 - Concentration",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Qiongjiu/Fixed Key 1 - Concentration.png"
      },
      {
        "node": "Fixed Key 2 - Efficient Planning",
        "level": "20",
        "keyName": "Fixed Key 2 - Efficient Planning",
        "description": "Before Support Action, dispels 1 buff from the target.",
        "icon": "assets/Qiongjiu/Fixed Key 2 - Efficient Planning.png"
      },
      {
        "node": "Fixed Key 3 - Targeted Training",
        "level": "30",
        "keyName": "Fixed Key 3 - Targeted Training",
        "description": "While in Support Mode, applies Defense Down II to the target for 1 turn before the allied unit's attack.",
        "icon": "assets/Qiongjiu/Fixed Key 3 - Targeted Training.png"
      },
      {
        "node": "Fixed Key 4 - Point of Vulnerability",
        "level": "30",
        "keyName": "Fixed Key 4 - Point of Vulnerability",
        "description": "Modify the effects of the active skill Guide to Victory to deal damage to all enemy targets within 8 tiles in the selected direction. All enemy targets except the first receive 30% less damage.",
        "icon": "assets/Qiongjiu/Fixed Key 4 - Point of Vulnerability.png"
      },
      {
        "node": "Fixed Key 5 - Necessary Adjustments",
        "level": "40",
        "keyName": "Fixed Key 5 - Necessary Adjustments",
        "description": "When a Phase Weakness is exploited using the active skill Common Rail, gains Blazing Assault II for 2 turns.",
        "icon": "assets/Qiongjiu/Fixed Key 5 - Necessary Adjustments.png"
      },
      {
        "node": "Fixed Key 6 - Steadiness",
        "level": "40",
        "keyName": "Fixed Key 6 - Steadiness",
        "description": "When under the effect of Support Boost, gain immunity to displacement effects applied by enemy units.",
        "icon": "assets/Qiongjiu/Fixed Key 6 - Steadiness.png"
      },
      {
        "node": "Affinity Key - Warm as Jade",
        "level": "-",
        "keyName": "Affinity Key - Warm as Jade",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Qiongjiu/Affinity Key - Warm as Jade.png"
      },
      {
        "node": "Common Key - Strategic Negotiation",
        "level": "40",
        "keyName": "Common Key - Strategic Negotiation",
        "description": "CRIT +5.0% / Increases damage dealt outside of the unit's own turn by 7%.",
        "icon": "assets/Qiongjiu/Common Key - Strategic Negotiation.png"
      },
      {
        "node": "Expansion Key - Ruined Gem",
        "level": "60",
        "keyName": "Expansion Key - Ruined Gem",
        "description": "Damage type dealt by Action Support is changed to Burn damage, and damage dealt to targets with Burn debuffs is increased by 15%.",
        "icon": "assets/Qiongjiu/Expansion Key - Ruined Gem.png"
      }
    ]
  },
  "Mosin-Nagant": {
    "class": "Sentinel",
    "stats": {
      "hp": 1859,
      "atk": 820,
      "def": 528
    },
    "stabilityGauge": 9,
    "movementSpeed": 4,
    "skillAttributes": [
      "Heavy Ammo",
      "Electric"
    ],
    "weaknesses": [
      "Light Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Patrol Time",
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
        "icon": "assets/Mosin-Nagant/Patrol Time.png"
      },
      {
        "name": "Target Victory",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles, dealing Physical damage equal to 130% of attack to them. After the attack, applies Conductivity for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If a Phase Weakness is exploited, gains 1 point of Confectance Index."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Preprepared Defenses",
            "effect": "When Target Victory deals Electric Damage, applies Paralysis for 1 turn instead of Conductivity"
          }
        ],
        "icon": "assets/Mosin-Nagant/Target Victory.png"
      },
      {
        "name": "Positive Mindset",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "Self",
        "effArea": "Target",
        "description": "Gain 1 stack of Active Engagement, and Extra Command once. Every 3 times this skill is used, gain Shock. Cannot be used more than once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increase damage dealt in Active Engagement by an additional 10%. Every 2 times this skill is used, gain Shock."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Positive Mindset",
            "effect": "When using the active skill Positive Mindset, if the user has Shock their attacks ignore 15% of Cover damage reduction"
          }
        ],
        "icon": "assets/Mosin-Nagant/Positive Mindset.png"
      },
      {
        "name": "Declaration of Victory",
        "traits": [
          "Ultimate",
          "Targeted",
          "Buff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 9 tiles, dealing Physical damage equal to 180% of attack to them. If a phase weakness is exploited, applies Paralysis to the target after the attack for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Gains 1 stack of Unshakable Confidence after each Support Action."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Gains 1 point of Confectance Index for each stack of Unshakable Confidence after using an Ultimate skill."
          }
        ],
        "icon": "assets/Mosin-Nagant/Declaration of Victory.png"
      },
      {
        "name": "Helping Others",
        "traits": [
          "Passive",
          "Support",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "When an allied unit attacks an enemy unit outside of turn but within range, if that enemy unit is in Stability Break, Mosin-Nagant performs 1 instance of Action Support, Physical damage equal to 80% of her attack and 2 points of Stability Damage. This effect can be triggered up to 2 times per turn. \n\nAfter a Support Attack, Mosin-Nagant gains 2 points of Confectance Index, and also gains Insight for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Before performing a Support Attack, gains 1 stack of Active Engagement."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "When an Electric debuff is applied to an enemy target outside of turn, gains Wise Support. The maximum number of Support Attack increases by 1."
          }
        ],
        "icon": "assets/Mosin-Nagant/Helping Others.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Target Victory",
        "level": "2",
        "effect": "If a phase weakness is exploited, gains 1 point of Confectance Index."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Declaration of Victory",
        "level": "2",
        "effect": "Gains 1 stack of Unshakable Confidence after each Support Action."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Declaration of Victory",
        "level": "3",
        "effect": "Gains 1 point of Confectance Index for each stack of Unshakable Confidence after using an Ultimate skill."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Helping Others",
        "level": "2",
        "effect": "Before performing a Support Attack, gains 1 stack of Active Engagement."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Positive Mindset",
        "level": "2",
        "effect": "Increase damage dealt in Active Engagement by an additional 10%. Every 2 times this skill is used, gain Shock."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Helping Others",
        "level": "3",
        "effect": "When an Electric debuff is applied to an enemy target outside of turn, gains Wise Support. The maximum number of Support Attack increases by 1."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Security Patrol Squad",
        "level": "20",
        "keyName": "Fixed Key 1 - Security Patrol Squad",
        "description": "If the target has Paralysis, increases Stability Damage they take by 2 points.",
        "icon": "assets/Mosin-Nagant/Fixed Key 1 - Security Patrol Squad.png"
      },
      {
        "node": "Fixed Key 2 - Preprepared Defenses",
        "level": "20",
        "keyName": "Fixed Key 2 - Preprepared Defenses",
        "description": "When Target Victory deals Electric damage, applies Paralysis for 1 turn instead of Conductivity.",
        "icon": "assets/Mosin-Nagant/Fixed Key 2 - Preprepared Defenses.png"
      },
      {
        "node": "Fixed Key 3 - Orderly Movement",
        "level": "30",
        "keyName": "Fixed Key 3 - Orderly Movement",
        "description": "If the target has Paralysis, applies 2 debuffs to them before launching an attack.",
        "icon": "assets/Mosin-Nagant/Fixed Key 3 - Orderly Movement.png"
      },
      {
        "node": "Fixed Key 4 - Positive Mindset",
        "level": "30",
        "keyName": "Fixed Key 4 - Positive Mindset",
        "description": "When using the active skill Positive Mindset, if the user has Shock, their attacks ignore 15% of Cover damage reduction.",
        "icon": "assets/Mosin-Nagant/Fixed Key 4 - Positive Mindset.png"
      },
      {
        "node": "Fixed Key 5 - Hard at Work",
        "level": "40",
        "keyName": "Fixed Key 5 - Hard at Work",
        "description": "When possessing Insight, reduce Stability Damage taken by 1 point.",
        "icon": "assets/Mosin-Nagant/Fixed Key 5 - Hard at Work.png"
      },
      {
        "node": "Fixed Key 6 - Mobile Patrol",
        "level": "40",
        "keyName": "Fixed Key 6 - Mobile Patrol",
        "description": "If an active attack applies Paralysis to the target, this unit gains 3 tiles of Additional Movement.",
        "icon": "assets/Mosin-Nagant/Fixed Key 6 - Mobile Patrol.png"
      },
      {
        "node": "Affinity Key - Heart of Gold",
        "level": "-",
        "keyName": "Affinity Key - Heart of Gold",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Mosin-Nagant/Affinity Key - Heart of Gold.png"
      },
      {
        "node": "Common Key - All Seeing Eye",
        "level": "40",
        "keyName": "Common Key - All Seeing Eye",
        "description": "ATK +5.0% / When this unit is under the effects of Insight, increases damage dealt by 7%.",
        "icon": "assets/Mosin-Nagant/Common Key - All Seeing Eye.png"
      },
      {
        "node": "Expansion Key - White Reaper",
        "level": "60",
        "keyName": "Expansion Key - White Reaper",
        "description": "When allies attempt to apply Paralysis on the target, Mosin applies Electric Sparks on the target for 1 turn. This effect can only activate once per round",
        "icon": "assets/Mosin-Nagant/Expansion Key - White Reaper.png"
      }
    ]
  },
  "Tololo": {
    "class": "Sentinel",
    "stats": {
      "hp": 1819,
      "atk": 836,
      "def": 528
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Medium Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Meteor",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Tololo/Meteor.png"
      },
      {
        "name": "Black Hole Inversion",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deal Hydro damage equal to 130% of attack to it. If Phase Weakness is exploited, gain 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If a Phase Weakness is exploited, ignores 15% of Cover damage reduction for this attack."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Principles of Observational Astronomy",
            "effect": "When using Black Hole Inversion, applies Congestion to the target for 2 turns."
          }
        ],
        "icon": "assets/Tololo/Black Hole Inversion.png"
      },
      {
        "name": "Supernova Impact",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deal Physical damage equal to 130% of attack to it. If under the effects of 2 or more buffs, increase damage dealt by 20% and gain 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If under the effects of 3 or more buffs, this attack deals Hydro damage. additionally gain 1 point of Confectance Index."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Retrograde Motion",
            "effect": "When using Supernova Impact, if an allied unit performs a Support Attack skill activation, applies Stun to the target for 1 turn."
          }
        ],
        "icon": "assets/Tololo/Supernova Impact.png"
      },
      {
        "name": "Morte Lumina",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 4,
        "cooldown": 4,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Select 1 enemy target within 8 tiles and deals Hydro damage equal to 180% of attack to it. If under the effects of 3 or more buffs, increases damage dealt by 15% and reduce this skill's cooldown by 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If under the effects of 3 or more buffs, increase damage dealt by 30% and reduce this skill's cooldown by 3 turns."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "If this kills the target, gain 1 point of Confectance Index."
          }
        ],
        "icon": "assets/Tololo/Morte Lumina.png"
      },
      {
        "name": "Aurora Curtain",
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
        "description": "Fills Confectance Index to maximum at the start of the battle. After attacking, if Confectance Index is at max, consumes all of it and gains 1 instance of an Extra Action. \n\nAt the start of each action, for every 2 points of Confectance Index, gains 1 random buff that lasts until the end of the action. Each time an allied unit delas Hydro damage, this unit gains 1 stack of Lightspike.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "During an Extra Action, this unit gains Targeted Attack Boost II, Critical Rate Boost II, Phase Boost II, and Piercing II for 2 turns."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "The effects of Lightspike are enhanced, increasing critical rate and critical damage by 2%."
          }
        ],
        "icon": "assets/Tololo/Aurora Curtain.png"
      },
      {
        "name": "Call of the Stars",
        "traits": [
          "Passive"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Map",
        "effArea": "7",
        "description": "At the end of allied turn, deals targetted Hydro damage equal to 130% of ATK to the enemy unit within 7 tile radius around the unit that has Gravitational Mark. If no unit has Gravitational Mark, targets the nearest enemy unit.",
        "upgrades": [],
        "icon": "assets/Tololo/Call of the Stars.png"
      },
      {
        "name": "Sync Standstill",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Immune to Control effects such as Stun, Taunt, and Command Prohibition.",
        "upgrades": [],
        "icon": null
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Black Hole Inversion",
        "level": "2",
        "effect": "If a Phase Weakness is exploited, ignores 15% of Cover damage reduction for this attack."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Supernova Impact",
        "level": "2",
        "effect": "If under the effects of 3 or more buffs, this attack deals Hydro damage. additionally gain 1 point of Confectance Index."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Annihilation Star",
        "level": "2",
        "effect": "If under the effects of 3 or more buffs, increase damage dealt by 30% and reduce this skill's cooldown by 3 turns."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Aurora Curtain",
        "level": "2",
        "effect": "During an Extra Action, this unit gains Targeted Attack Boost II, Critical Rate Boost II, Phase Boost II, and Piercing II for 2 turns."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Aurora Curtain",
        "level": "3",
        "effect": "The effects of Lightspike are enhanced, increasing critical rate and critical damage by 2%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Annihilation Star",
        "level": "3",
        "effect": "If this kills the target, gain 1 point of Confectance Index."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Comet Tail Transit",
        "level": "20",
        "keyName": "Fixed Key 1 - Comet Tail Transit",
        "description": "Extra Action increases mobility by 1 tile.",
        "icon": "assets/Tololo/Fixed Key 1 - Comet Tail Transit.png"
      },
      {
        "node": "Fixed Key 2 - Principles of Observational Astronomy",
        "level": "20",
        "keyName": "Fixed Key 2 - Principles of Observational Astronomy",
        "description": "When using Black Hole Inversion, applies Congestion to the target for 2 turns.",
        "icon": "assets/Tololo/Fixed Key 2 - Principles of Observational Astronomy.png"
      },
      {
        "node": "Fixed Key 3 - Invisible Light",
        "level": "30",
        "keyName": "Fixed Key 3 - Invisible Light",
        "description": "When Extra Action is triggered, gains Attack Up II and Damage Up II for 1 turn.",
        "icon": "assets/Tololo/Fixed Key 3 - Invisible Light.png"
      },
      {
        "node": "Fixed Key 4 - Retrograde Motion",
        "level": "30",
        "keyName": "Fixed Key 4 - Retrograde Motion",
        "description": "When using Supernova Impact, if an allied unit performs a Support Attack before skill activation, applies Stun to the target for 1 turn.",
        "icon": "assets/Tololo/Fixed Key 4 - Retrograde Motion.png"
      },
      {
        "node": "Fixed Key 5 - Galactic Cruise",
        "level": "40",
        "keyName": "Fixed Key 5 - Galactic Cruise",
        "description": "When exploiting a Phase Weakness, dispels 2 buffs from target before attacking.",
        "icon": "assets/Tololo/Fixed Key 5 - Galactic Cruise.png"
      },
      {
        "node": "Fixed Key 6 - Stellar Eclipse",
        "level": "40",
        "keyName": "Fixed Key 6 - Stellar Eclipse",
        "description": "When at max HP and Stability Index, ignore 10% of the target's Cover damage reduction.",
        "icon": "assets/Tololo/Fixed Key 6 - Stellar Eclipse.png"
      },
      {
        "node": "Affinity Key - Stardust's Whispers",
        "level": "-",
        "keyName": "Affinity Key - Stardust's Whispers",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Tololo/Affinity Key - Stardust's Whispers.png"
      },
      {
        "node": "Common Key - Afterglow",
        "level": "40",
        "keyName": "Common Key - Afterglow",
        "description": "ATK +5.0% / When Confectance Index is below max, increases damage dealt by 7%.",
        "icon": "assets/Tololo/Common Key - Afterglow.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "After using an active skill, Tololo gains 2 points of Confectance Index. If an allied unit (apart from Tololo) deals Hydro damage, the cooldown of the active skill Black Hole Inversion is reduced by 1 turn.",
        "icon": "assets/Tololo/Expansion Key.png"
      },
      {
        "node": "Expansion Key tier 2",
        "level": "60",
        "keyName": "Expansion Key tier 2",
        "description": "At the start of the battle, Tololo gains 3 stacks of Stellar Energy Reserve.\nAt the end of Tololo's action, she gains 1 stack of Observation Advantage for 1 round. If the number of Stationary Satellites on the field has not reached its maximum, consumes 1 stack of Stellar Energy Reserve to summon 1 Stationary Satellite by Tololo's side for 2 rounds.\nAt the start of every other round, Tololo gains 3 stacks of Stellar Energy Reserve.\nAfter Tololo performs an active attack, applies Gravitational Mark to the target. After a Stationary Satellite deals damage, applies 1 stack of Starlight Refraction to the target. Tololo then gains 1 stack of Orbital Resonance.",
        "icon": "assets/Tololo/Expansion Key tier 2.png"
      }
    ]
  },
  "Daiyan": {
    "class": "Vanguard",
    "stats": {
      "hp": 1616,
      "atk": 722,
      "def": 504
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Medium Ammo",
      "Light Ammo"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Plucking Strings",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Daiyan/Plucking Strings.png"
      },
      {
        "name": "Absolute Tuning",
        "traits": [
          "Active",
          "Targeted",
          "Dispel"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, dispels 1 buff, and deals Physical damage equal to 150% of attack to them.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If the target has no buffs to dispel when during the attack, gains 1 stack of Tuning after the attack."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Squad Broken",
            "effect": "For every 3 stacks of Tuning, dispels 1 additional buff when using the active skill Absolute Tuning."
          }
        ],
        "icon": "assets/Daiyan/Absolute Tuning.png"
      },
      {
        "name": "Qing Shang Harmony",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "Self",
        "effArea": "Target",
        "description": "Gains 3 stacks of Tuning, as well as Pitch Perfect for 1 turn. Gains 1 instance of Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increases the number of Tuning stacks gained by 3."
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Lasting Legacy",
            "effect": "After using Qing Shang Harmony, if a kill occurs in this turn, recovers 20% max HP and 2 points of Stability Index."
          }
        ],
        "icon": "assets/Daiyan/Qing Shang Harmony.png"
      },
      {
        "name": "Ethereal Resonance",
        "traits": [
          "Ultimate",
          "Targeted",
          "Buff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 6,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, dealing Physical damage equal to 190% of attack. For every 1 stack of Tuning, reduces this skill's cooldown by 1 turn.\n\nAfter attacking, consumes all stacks of Tuning and gains 1 stack of Tuning permanently, up to a maximum of 3 stacks.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases the stack limit of permanent Tuning by 3 stacks."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For every 1 enemy unit that dies on the field, gain 1 stack of Tuning permanently."
          }
        ],
        "icon": "assets/Daiyan/Ethereal Resonance.png"
      },
      {
        "name": "Swift Harmony",
        "traits": [
          "Passive",
          "Ambush"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "At the start of the action, gains 1 point of Confectance Index and 1 stack of Tuning. When performing an active attack against a target not protected by Cover, gains 1 point of Confectance Index.\n\nBefore taking targeted damage, if the number of Tuning stacks is greater than 2, launches Interception, dealing light ammo Physical damage equal to 150% of attack and 4 points of Stability Damage, and permanently gains 1 stack of Tuning. This can be triggered once per turn.\n\nIf the number of Tuning stacks is greater than 3, increases damage dealt by 20%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "If the number of Tuning stacks is greater than 5, increases damage dealt by 40% instead. Additionally Stability Damage dealt by Interception increases by 2 points, and the initial damage multiplier increases by 30%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "When the number of permanent Tuning stacks reaches max, ignores 15% of Cover damage reduction when attacking Exposed enemies."
          }
        ],
        "icon": "assets/Daiyan/Swift Harmony.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Absolute Tuning",
        "level": "2",
        "effect": "If the target has no buffs to dispel when during the attack, gains 1 stack of Tuning after the attack."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Qing Shang Harmony",
        "level": "2",
        "effect": "Increases the number of Tuning stacks gained by 3."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Ethereal Resonance",
        "level": "2",
        "effect": "Increases the stack limit of permanent Tuning by 3 stacks."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Swift Harmony",
        "level": "2",
        "effect": "If the number of Tuning stacks is greater than 5, increases damage dealt by 40% instead. Additionally Stability Damage dealt by Interception increases by 2 points, and the initial damage multiplier increases by 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Swift Harmony",
        "level": "3",
        "effect": "When the number of permanent Tuning stacks reaches max, ignores 15% of Cover damage reduction when attacking Exposed enemies."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Ethereal Resonance",
        "level": "3",
        "effect": "For every 1 enemy unit that dies on the field, gain 1 stack of Tuning permanently."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Echoing Melody",
        "level": "20",
        "keyName": "Fixed Key 1 - Echoing Melody",
        "description": "When Daiyan has Tuning, increases mobility by 1 tile.",
        "icon": "assets/Daiyan/Fixed Key 1 - Echoing Melody.png"
      },
      {
        "node": "Fixed Key 2 - Unfulfilled Dreams",
        "level": "20",
        "keyName": "Fixed Key 2 - Unfulfilled Dreams",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Daiyan/Fixed Key 2 - Unfulfilled Dreams.png"
      },
      {
        "node": "Fixed Key 3 - Hazewalker's Melody",
        "level": "30",
        "keyName": "Fixed Key 3 - Hazewalker's Melody",
        "description": "For each point of additional mobility before the attack, critical rate increases by 10%.",
        "icon": "assets/Daiyan/Fixed Key 3 - Hazewalker's Melody.png"
      },
      {
        "node": "Fixed Key 4 - Serene Serenade",
        "level": "30",
        "keyName": "Fixed Key 4 - Serene Serenade",
        "description": "If Daiyan's mobility is higher than the target's, gains 1 stack of Tuning before using an active attack.",
        "icon": "assets/Daiyan/Fixed Key 4 - Serene Serenade.png"
      },
      {
        "node": "Fixed Key 5 - Squad Broken",
        "level": "40",
        "keyName": "Fixed Key 5 - Squad Broken",
        "description": "For every 3 stacks of Tuning, dispels 1 additional buff when using the active skill Absolute Tuning.",
        "icon": "assets/Daiyan/Fixed Key 5 - Squad Broken.png"
      },
      {
        "node": "Fixed Key 6 - Lasting Legacy",
        "level": "40",
        "keyName": "Fixed Key 6 - Lasting Legacy",
        "description": "After using Qing Shang Harmony, if a kill occurs in this turn, recovers 20% max HP and 2 points of Stability Index.",
        "icon": "assets/Daiyan/Fixed Key 6 - Lasting Legacy.png"
      },
      {
        "node": "Affinity Key - Sweet Serenade",
        "level": "-",
        "keyName": "Affinity Key - Sweet Serenade",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Daiyan/Affinity Key - Sweet Serenade.png"
      },
      {
        "node": "Common Key - Shattering Stone and Silk",
        "level": "40",
        "keyName": "Common Key - Shattering Stone and Silk",
        "description": "CRIT +5.0% / At the start of the action, gains Movement Up I for 1 turn. This has a cooldown of 1 turn.",
        "icon": "assets/Daiyan/Common Key - Shattering Stone and Silk.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "For each stack of Permanent Tuning held, ignores 10% of the target's DEF when attacking. At the end of the action, gains 2 stacks of Tuning, and for each stack of Permanent Tuning held, increases Confectance Index by 1 point",
        "icon": "assets/Daiyan/Expansion Key.png"
      },
      {
        "node": "Expansion Key tier 2",
        "level": "60",
        "keyName": "Expansion Key tier 2",
        "description": "When using the Ultimate skill Ethereal Resonance and launches Interception, gain 1 stack of permanent Tuning.\r\n\r\nAt the end of a round, if no Interception was performed, gain 2 stacks of permanent Tuning and increase the next active attack's damage multiplier by 150% and Stability damage by 4 points.\r\n\r\nAfter using the Ultimate skill Ethereal Resonance, perform 1 additional attack on the target. For each stack of permanent Tuning possessed, this attack deals Physical damage equal to 100% of attack and 1 point of Stability damage.",
        "icon": "assets/Daiyan/Expansion Key tier 2.png"
      }
    ]
  },
  "Centaureissi": {
    "class": "Support",
    "stats": {
      "hp": 1893,
      "atk": 696,
      "def": 585
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Cleaning Time",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects 1 target within 7 tiles, dealing Physical damage equal to 80% of attack.",
        "upgrades": [],
        "icon": "assets/Centaureissi/Cleaning Time.png"
      },
      {
        "name": "Careful Hospitality",
        "traits": [
          "Active",
          "Targeted",
          "Healing",
          "Buff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 6,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 7 tiles and deals Burn damage equal to 130% of attack to them. After attacking, restores HP equal to 100% of attack to the nearest allied target (excluding the user) and gains Heat Recovery. If the enemy target is inflicted with Overburn, heals 1 additional allied target.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If the user has Heat Recovery, gain Thermal Cycling."
          }
        ],
        "icon": "assets/Centaureissi/Careful Hospitality.png"
      },
      {
        "name": "Zucchero's Special Drink",
        "traits": [
          "Active",
          "AoE",
          "Healing",
          "Dispel"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "3",
        "description": "Select 1 allied target within 7 tiles, restoring HP equal to 150% of attack to the target and all allied units within 3 tiles. The healing is distributed evenly among all targets. Additionally, deals AoE Physical damage equal to 50% of attack to all enemies within range. If the enemy target have Overburn, dispels 2 of their buffs.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Each allied target restores at least 75% of Centaureissi's attack as HP."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Comforting Blend",
            "effect": "Increses the healing multiplier of the active skill Zucchero's Special Drink by 75%."
          }
        ],
        "icon": "assets/Centaureissi/Zucchero's Special Drink.png"
      },
      {
        "name": "Afternoon Tea Break",
        "traits": [
          "Ultimate",
          "Healing",
          "Stability Regen",
          "Cleanse",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Entire Map",
        "effArea": "Entire Map",
        "description": "Restores HP equal to 100% of attack to all allies, cleanses 2 debuffs, removes Fear and Stun, and restores up to 7 points of Stability Index to the ally with the lowest Stability Index. After healing, applies Heat Recovery.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The number of debuffs cleansed increases by 1, and removes Taunt, Fear, Infatuated, and Stun."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Restore Stability Index for 2 allies with the lowest Stability, then further increase it by 1 point."
          }
        ],
        "icon": "assets/Centaureissi/Afternoon Tea Break.png"
      },
      {
        "name": "Maid's Duty",
        "traits": [
          "Passive",
          "Buff",
          "Debuff",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the battle, gains Heat Recovery.\n\nWhen the user is under the effects of Heat Recovery: Increases damage dealt by 20%. When healing, additionally heals 10% of the user's max HP. After active attacks applies Overburn for 2 turns.\n\nWhen an enemy unit within attack range receives targeted damage from an ally, prioritize performing 1 instance of Action Support, dealing Physical damage equal to 80% of attack and 3 points of Stability Damage to them, and applies Heat Recovery to the allied unit. Gains 1 point of Confectance Index. This can be triggered up to 2 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "When Action Support is triggered, additionally applies Blazing Assault II and Damage Up II to the allied unit for 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "When Heat Recovery is active: increases healing by 20% and damage dealt by 40%. If the healing target has Heat Recovery, the healing increase is raised to 50%; if the enemy target has Overburn, the damage dealt is increased by 50%."
          }
        ],
        "icon": "assets/Centaureissi/Maid's Duty.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Maid's Duty",
        "level": "2",
        "effect": "When Action Support is activated, additionally applies Blazing Assault II and Damage Up II to the allied unit for 1 turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Maid's Duty",
        "level": "3",
        "effect": "When Heat Recovery is active: increases healing by 20% and damage dealt by 40%. If the healing target has Heat Recovery, the healing increase is raised to 50%; if the enemy target has Overburn, the damage dealt is increased by 50%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Careful Hospitality",
        "level": "2",
        "effect": "If the user has Heat Recovery, gain Thermal Cycling."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Afternoon Tea Break",
        "level": "2",
        "effect": "The number of debuffs cleansed increases by 1, and removes  Taunt, Fear, Infatuated, and Stun."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Zucchero's Special Drink",
        "level": "2",
        "effect": "Each allied target restores at least 75% of Centaureissi's attack as HP."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Afternoon Tea Break",
        "level": "3",
        "effect": "Restores Stability Index for 2 allies with the lowest Stability, then further increases it by 1 point."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Pre-Meal Dessert",
        "level": "20",
        "keyName": "Fixed Key 1 - Pre-Meal Dessert",
        "description": "Gains 3 points of Confectance Index at the start of the battle.",
        "icon": "assets/Centaureissi/Fixed Key 1 - Pre-Meal Dessert.png"
      },
      {
        "node": "Fixed Key 2 - Maid's Resolve",
        "level": "20",
        "keyName": "Fixed Key 2 - Maid's Resolve",
        "description": "If an allied unit within 7 tiles enters Stability Break after taking damage, removes Heat Recovery from self and applies Heat Recovery to the allied unit.",
        "icon": "assets/Centaureissi/Fixed Key 2 - Maid's Resolve.png"
      },
      {
        "node": "Fixed Key 3 - Efficient Processing",
        "level": "30",
        "keyName": "Fixed Key 3 - Efficient Processing",
        "description": "When Heat Recovery is triggered, randomly dispels 1 buff from the attacker. Before Heat Recovery is triggered, cleanses 2 debuffs from allies possessing Heat Recovery.",
        "icon": "assets/Centaureissi/Fixed Key 3 - Efficient Processing.png"
      },
      {
        "node": "Fixed Key 4 - Comforting Blend",
        "level": "30",
        "keyName": "Fixed Key 4 - Comforting Blend",
        "description": "Increses the healing multiplier of the active skill Zucchero's Special Drink by 75%.",
        "icon": "assets/Centaureissi/Fixed Key 4 - Comforting Blend.png"
      },
      {
        "node": "Fixed Key 5 - Thorough Preperation",
        "level": "40",
        "keyName": "Fixed Key 5 - Thorough Preperation",
        "description": "When healing an allied target with an active skill, cleanses 1 debuff. For targets with Heat Recovery, cleanses 1 additional debuff.",
        "icon": "assets/Centaureissi/Fixed Key 5 - Thorough Preperation.png"
      },
      {
        "node": "Fixed Key 6 - Lucky Menu",
        "level": "40",
        "keyName": "Fixed Key 6 - Lucky Menu",
        "description": "When healing an allied target with an active skill, if the target has Heat Recovery, randomly applies 1 powerful buff to them for 1 turn.",
        "icon": "assets/Centaureissi/Fixed Key 6 - Lucky Menu.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Centaureissi/Affinity Key.png"
      },
      {
        "node": "Common Key - Essential Hot Beverages",
        "level": "40",
        "keyName": "Common Key - Essential Hot Beverages",
        "description": "HP +5.0% / At the end of the action, applies Heat Recovery to the closest allied unit without Heat Recovery. This effect has a 2-turn cooldown.",
        "icon": "assets/Centaureissi/Common Key - Essential Hot Beverages.png"
      },
      {
        "node": "Expansion Key - Will to Protect",
        "level": "60",
        "keyName": "Expansion Key - Will to Protect",
        "description": "At the start of the battle and after activating Afternoon Tea Break, applies Hot Sobering Tea on self for 2 rounds (Duration decreases at the end of the current round)\n\nAfter activating Zucchero's Special Drink, applies Perfect Defense for all allies for 2 turns. When allies deal Burn damage or when Centaureissi activates Action Support, increases Confectance Index by 1 point. This can be activated once per round",
        "icon": "assets/Centaureissi/Expansion Key - Will to Protect.png"
      }
    ]
  },
  "Lenna": {
    "class": "Support",
    "stats": {
      "hp": 2081,
      "atk": 689,
      "def": 550
    },
    "stabilityGauge": 10,
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
        "name": "Territory Awareness",
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
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Lenna/Territory Awareness.png"
      },
      {
        "name": "Wild Extinction",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Electric damage equivalent to 140% ATK to it. If Confectance Index has 3 points or more before skill activation, consumes 3 points and increases damage dealt by 30%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If Confectance Index has 3 points or more before skill activation, increases damage dealt by 30% → 50%. If the target has Conductivity, increases Confectance Index by 3 points"
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - SSStylish Action",
            "effect": "Wild Extinction: When this skill kills the target, increases Confectance Index by 2 points"
          }
        ],
        "icon": "assets/Lenna/Wild Extinction (row 39).png"
      },
      {
        "name": "Leaping Pursuit",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "7",
        "description": "Selects a tile within a 3 tile cross area of self and lands on the selected tile, dealing Physical damage equivalent to 30% ATK and inflicting Stability Loss II to the nearest enemy target within a 7 tile radius for 1 turn. If Confectance Index has 3 points or more before skill activation, consumes 3 points and gains Extra Command",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases effective range by 2 tiles"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - I Need More Power",
            "effect": "Leaping Pursuit: After this skill is used, applies Conductivity on the 2 nearest enemies within a 5 tile radius for 1 turn"
          }
        ],
        "icon": "assets/Lenna/Leaping Pursuit (row 69).png"
      },
      {
        "name": "Hunting Strategy",
        "traits": [
          "Ultimate",
          "AoE",
          "Debuff",
          "Buff"
        ],
        "attribute": "Electric",
        "stabilityDamage": 2,
        "cooldown": 6,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "5",
        "description": "Deals AoE Electric damage equivalent to 80% ATK to all enemies within a 5 tile radius, and inflicts Conductivity for 1 turn. Creates a Voltage tiles for 3 turns. Lenna gains Electric Arc for 3 turns. If Confectance Index has 3 points or more before skill activation, consumes 3 points and gains Concealed for 1 turn",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases effective range by 2 tiles, and inflicts 2 random debuffs on targets for 1 turn"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Electric Arc: At the end of Lenna's action, recovers Confectance Index fully. Skills no longer need to consume Confectance Index in order to be enhanced. Instead, when Confectance Index is consumed, increases damage dealt by 20%"
          }
        ],
        "icon": "assets/Lenna/Hunting Strategy (row 99).png"
      },
      {
        "name": "King's Authority",
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
        "description": "Lenna is immune from the negative effects of Electric type terrain. When an enemy gains Conductivity, increases Confectance Index by 1 point. When dealing single target damage, generates a Voltage tiles within a 1 tile radius around the target for 2 turns",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "For every 3 points of Confectance Index consumed, reduces the cooldown of all skills by 1 turn"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the duration of Concealed by 1 turn"
          }
        ],
        "icon": "assets/Lenna/King's Authority.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "King's Authority",
        "level": "2",
        "effect": "For every 3 points of Confectance Index consumed, reduces the cooldown of all skills by 1 turn"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Wild Extinction",
        "level": "2",
        "effect": "If Confectance Index has 3 points or more before skill activation, increases damage dealt by 30% → 50%. If the target has Conductivity, increases Confectance Index by 3 points"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Leaping Pursuit",
        "level": "2",
        "effect": "Increases effective range by 2 tiles"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Hunting Strategy",
        "level": "2",
        "effect": "Increases effective range by 2 tiles, and inflicts 2 random debuffs on targets for 1 turn"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "King's Authority",
        "level": "3",
        "effect": "Increases the duration of Concealed by 1 turn"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Hunting Strategy",
        "level": "3",
        "effect": "Electric Arc: At the end of Lenna's action, recovers Confectance Index fully. Skills no longer need to consume Confectance Index in order to be enhanced. Instead, when Confectance Index is consumed, increases damage dealt by 20%"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Skillful Strategem",
        "level": "20",
        "keyName": "Fixed Key 1 - Skillful Strategem",
        "description": "When attacking enemies with Conductivity and immunity to Paralysis, ignores 15% DEF",
        "icon": "assets/Lenna/Fixed Key 1 - Skillful Strategem.png"
      },
      {
        "node": "Fixed Key 2 - SSStylish Action",
        "level": "20",
        "keyName": "Wild Extinction",
        "description": "When this skill kills the target, increases Confectance Index by 2 points",
        "icon": "assets/Lenna/Wild Extinction (row 174).png"
      },
      {
        "node": "Fixed Key 3 - The Perfect Way",
        "level": "30",
        "keyName": "Fixed Key 3 - The Perfect Way",
        "description": "When applying Conductivity, changes 1 random buff on the enemy to a random debuff",
        "icon": "assets/Lenna/Fixed Key 3 - The Perfect Way.png"
      },
      {
        "node": "Fixed Key 4 - I Need More Power",
        "level": "30",
        "keyName": "Leaping Pursuit",
        "description": "After this skill is used, applies Conductivity on the 2 nearest enemies within a 5 tile radius for 1 turn",
        "icon": "assets/Lenna/Leaping Pursuit (row 176).png"
      },
      {
        "node": "Fixed Key 5 - Driving Force",
        "level": "40",
        "keyName": "Fixed Key 5 - Driving Force",
        "description": "When an enemy with Electric type debuffs is killed, increases Confectance Index by 1 point",
        "icon": "assets/Lenna/Fixed Key 5 - Driving Force.png"
      },
      {
        "node": "Fixed Key 6 - Top-Tier Intermediate Response",
        "level": "40",
        "keyName": "Fixed Key 6 - Top-Tier Intermediate Response",
        "description": "When Lenna enters into Stability Break from being attacked, inflicts Paralysis on all enemy targets within a 5 tile radius for 1 turn. This effect can be triggered once per battle",
        "icon": "assets/Lenna/Fixed Key 6 - Top-Tier Intermediate Response.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Lenna/Affinity Key.png"
      },
      {
        "node": "Common Key - Razor-Sharp Claws",
        "level": "40",
        "keyName": "Common Key - Razor-Sharp Claws",
        "description": "CRIT +5.0% / When the user deals single target damage, applies Conductivity on the target for 1 turn. This effect can be activated up to twice per turn",
        "icon": "assets/Lenna/Common Key - Razor-Sharp Claws.png"
      },
      {
        "node": "Expansion Key- Lioness' Determination",
        "level": "60",
        "keyName": "Hunting Strategy",
        "description": "After skill usage, Lenna gains Ultimate Briliance for 3 turns\n\nLeaping Pursuit: After skill usage, increases the damage multiplier of the attack executed during Extra Command by 100%\n\nFor each point of Confectance Index consumed during the round, increase Lenna's attack by 5% for the next round, up to a maximum of 30%",
        "icon": "assets/Lenna/Hunting Strategy (row 181).png"
      }
    ]
  },
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
      },
      {
        "node": "Expansion Key tier 2",
        "level": "60",
        "keyName": "Expansion Key tier 2",
        "description": "At the start of the battle, increases own ATK by 30% and ignores 30% of enemy target's DEF when attacking; additionally creates 1 high ground on the nearest empty tile. While on high ground, damage dealt increases by 80% and critical damage increases by 30%.\nWhen Ambush hits a target, summons 1 Ice Construct nearby. When Ice Construct spawns and at the end its action, if inflicts Taunt on all enemy targets within 3-tile radius (targets that are ambushed and recieve Taunt will not have it take effect immediately), lasting 2 turns.",
        "icon": "assets/Makiatto/Expansion Key tier 2.png"
      }
    ]
  },
  "Ullrid": {
    "class": "Vanguard",
    "stats": {
      "hp": 1519,
      "atk": 740,
      "def": 528
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Melee",
      "Light Ammo"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Warning Shot",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "5",
        "effArea": "Target",
        "description": "Select 1 enemy target within 5 tiles and deal Physical damage equal to 80% of attack to it.",
        "upgrades": [],
        "icon": "assets/Ullrid/Warning Shot.png"
      },
      {
        "name": "Hunter's Sight",
        "traits": [
          "Active",
          "Targeted",
          "Melee",
          "Debuff"
        ],
        "attribute": "Melee",
        "stabilityDamage": 1,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "3x3",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 1 tile, dealing melee Physical damage equal to 120% of attack and gains 6 tiles of Additional Movement. If the target is not killed, applies Mark of Prey for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "If the target is not killed, applies Movement Down II to the enemy target for 2 turns. When Ullrid is attacked by a target with Mark of Prey, reduces damage taken by 20%."
          }
        ],
        "icon": "assets/Ullrid/Hunter's Sight.png"
      },
      {
        "name": "Blade Whirlwind",
        "traits": [
          "Active",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "3x3",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 1 tile and deal melee Physical damage equal to 90% of attack to it. Gains Whirlwind after attacking.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If attacking the same target within one action, increase damage dealt by 30%. The effects of Whirlwind are enhanced: Ignores Cover damage reduction when attacking."
          }
        ],
        "icon": "assets/Ullrid/Blade Whirlwind.png"
      },
      {
        "name": "Hidden Pursuit",
        "traits": [
          "Ultimate",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "1",
        "description": "Select a tile in a cross-shaped area within 5 tiles, move to that tile and deal melee Physical damage equal to 180% of attack to the enemy target with the highest HP within 1 tile.\n\nConsumes all stacks of Hunter's Talent, for each stack consumed, increase damage dealt by this attack by 10%, up to a 30% increase. If there are 2 stacks of Hunter's Talent or more, gain 2 stacks of Camouflage for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increase range by 2 tiles. Raise the damage increase cap to 60% by consuming Hunter's Talent."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For every 2% of the enemy target's missing HP, increase self-attack by 1% for this skill. If this kills the target, increase damage dealt by the next active attack by 30%. \n\nIf there are 2 stacks of Hunter's Talent or more, gain only 1 stack of Camouflage, but Camouflage is no longer consumed after taking damage."
          }
        ],
        "icon": "assets/Ullrid/Hidden Pursuit.png"
      },
      {
        "name": "Optical Camouflage",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Gain 1 stack of Hunter's Talent and 1 point of Confectance Index after active attacks.\n\nAt the end of an enemy unit’s action, if Ullrid's HP is below 30%, gain 1 stack of Camouflage for 1 turn. Cooldown: 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "At the start of battle, for each allied target on the field (excluding self), gain 1 stack of Hunter's Talent and 1 point of Confectance Index."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Before attacking, if this unit has moved 2 tiles or more, increase attack by 20%. if Ullrid's HP is below 50%, gain Camouflage and reduce the effect's cooldown by 1 turn."
          }
        ],
        "icon": "assets/Ullrid/Optical Camouflage.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Blade Whirlwind",
        "level": "2",
        "effect": "If attacking the same target within one action, increases damage dealt by 30%. The effects of Whirlwind are enhanced: Ignores Cover damage reduction when attacking."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Optical Camouflage",
        "level": "2",
        "effect": "At the start of the battle, for each allied target on the field (excluding self), gain 1 stack of Hunter's Talent and 1 point of Confectance Index."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Hunter's Sight",
        "level": "2",
        "effect": "If target is not killed, applies Movement Down II to enemy target for 2 turns. When Ullrid is attacked by a target with Mark of Prey, reduces damage taken by 20%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Hidden Pursuit",
        "level": "2",
        "effect": "Increase range by 2 tiles. Raise the damage increase cap to 60% by consuming Hunter's Talent."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Optical Camouflage",
        "level": "3",
        "effect": "Before attacking, if this unit has moved 2 tiles or more, increase attack by 20%. if Ullrid's HP is below 50%, gain Camouflage and reduce the effect's cooldown by 1 turn."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Hidden Pursuit",
        "level": "3",
        "effect": "For every 2% of the enemy target's missing HP, increase self-attack by 1% for this skill. If this kills the target, increase damage dealt by the next active attack by 30%. \n\nIf there are 2 stacks of Hunter's Talent or more, gain only 1 stack of Camouflage, but Camouflage is no longer consumed after taking damage."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Swift Action",
        "level": "20",
        "keyName": "Fixed Key 1 - Swift Action",
        "description": "When the user possess Whirlwind, basic attacks and other active skills can be used, but it consumes an additional 2 points of Confectance Index.",
        "icon": "assets/Ullrid/Fixed Key 1 - Swift Action.png"
      },
      {
        "node": "Fixed Key 2 - Predation",
        "level": "20",
        "keyName": "Fixed Key 2 - Predation",
        "description": "Ignores 30% of the target enemy's defense when there are no other enemy units within 3 tiles of the target.",
        "icon": "assets/Ullrid/Fixed Key 2 - Predation.png"
      },
      {
        "node": "Fixed Key 3 - Appropriate Caution",
        "level": "30",
        "keyName": "Fixed Key 3 - Appropriate Caution",
        "description": "At the start of the battle, gains 3 points of Confectance Index.",
        "icon": "assets/Ullrid/Fixed Key 3 - Appropriate Caution.png"
      },
      {
        "node": "Fixed Key 4 - Ideal State",
        "level": "30",
        "keyName": "Fixed Key 4 - Ideal State",
        "description": "When there are no allied units within 3 tiles of self (excluding summoned units), increase own critical rate by 20%.",
        "icon": "assets/Ullrid/Fixed Key 4 - Ideal State.png"
      },
      {
        "node": "Fixed Key 5 - Oppression",
        "level": "40",
        "keyName": "Fixed Key 5 - Oppression",
        "description": "When at full health, damage dealt is increased by 15%.",
        "icon": "assets/Ullrid/Fixed Key 5 - Oppression.png"
      },
      {
        "node": "Fixed Key 6 - Hunter's Acuity",
        "level": "40",
        "keyName": "Fixed Key 6 - Hunter's Acuity",
        "description": "When exploiting Phase Weakness, gain Attack Up I for 2 turns.",
        "icon": "assets/Ullrid/Fixed Key 6 - Hunter's Acuity.png"
      },
      {
        "node": "Affinity Key -  Stress Ball Terminator",
        "level": "-",
        "keyName": "Affinity Key -  Stress Ball Terminator",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Ullrid/Affinity Key -  Stress Ball Terminator.png"
      },
      {
        "node": "Common Key - Mangle",
        "level": "40",
        "keyName": "Common Key - Mangle",
        "description": "CRIT +5.0% / If the enemy target's HP is not full before the attack, increase damage dealt to them by 7%.",
        "icon": "assets/Ullrid/Common Key - Mangle.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "After using Blade Whirlwind, if the target is still alive, follow up with 1 extra instance of Physical damage equal to 90% of attack and deals 1 point of Stability. The damage of this attack is increased by 30%. This effect can be triggered up to 3 times per turn.",
        "icon": "assets/Ullrid/Expansion Key.png"
      },
      {
        "node": "Expansion Key tier 2",
        "level": "60",
        "keyName": "Expansion Key tier 2",
        "description": "Inflicts Mark of Prey before each instance of using the active skill Blade Whirlwind. After using said skill, the cooldown of the Ultimate skill Hidden Pursuit is reduced by 1 turn. If Ullrid hits the same target continuously, she gains 1 point of Confectance Index. This effect can only be triggered once per round.\nBefore using the Ultimate skill Hidden Pursuit, Ullrid gains maximum stacks of Hunter's Talent.\nHunter's Talent's effect is enhanced: If Ullrid's critical rate is higher than 100%, for every 1% critical rate of overflow, her critical damage is increased by 0.3%. Increases damage dealt by all allied units that deal melee damage by 10%. For every stack of Hunter's Talent consumed, Ullrid gains 1 point of Confectance Index.\nMark of Prey apply new effect: Lacerating Wound - when taking damage, if the attacker is a blade user, for every instance of damage dealt, they deal additional damage equal to 40% of the original damage. Debuff, cannot be dispelled.",
        "icon": "assets/Ullrid/Expansion Key tier 2.png"
      }
    ]
  },
  "Lotta": {
    "class": "Sentinel",
    "stats": {
      "hp": 1599,
      "atk": 696,
      "def": 487
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Shotgun Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Heartfelt Confession",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Lotta/Heartfelt Confession.png"
      },
      {
        "name": "Cryo Rounds",
        "traits": [
          "Active",
          "AoE",
          "Debuff",
          "Cover Destruction"
        ],
        "attribute": "Shotgun Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction around self, deal AoE Freeze damage equal to 60% of attack to all enemy targets within a 3x5 area in the chosen direction. Simultaneously, destroy any destructible Cover outside a 3x3 area within range around self. Additionally, applies Cold Snap to targets for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the duration of Cold Snap by 1 turn."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Bold Shout",
            "effect": "Adds a new effect to the active skill Cryo Rounds. Knock back the target by 3 tiles."
          }
        ],
        "icon": "assets/Lotta/Cryo Rounds.png"
      },
      {
        "name": "Neural Adjustment",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Fills Confectance Index and gains Attack Up I for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Replaces Attack Up I with Attack Up II."
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Soothing Touch",
            "effect": "The active skill Neural Adjustment gains a new effect: Gains 1 stack of Quick Barrier."
          }
        ],
        "icon": "assets/Lotta/Neural Adjustment.png"
      },
      {
        "name": "Amplified Courage",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Freeze",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "6",
        "effArea": "3",
        "description": "Select 1 enemy target within 6 tiles of the user to launch an attack, dealing AoE Freeze damage equal to 100% of attack to it and all enemy targets within 3 tiles that ignores Cover damage reduction. If it hits 2 or more targets, gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "If Phase Weakness is exploited, apply Cold Snap to the target for 1 turn."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Change \"Select Enemy Target\" to \"Select Tile\""
          }
        ],
        "icon": "assets/Lotta/Amplified Courage.png"
      },
      {
        "name": "Bonds of Friendship",
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
        "description": "When an enemy target within range is affected by Cold Snap, performs 1 instance of Wise Support, dealing AoE Physical damage equal to 50% of attack and 1 point of Stability Damage to them. This can be triggered up to 2 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Increase mobility of self by 1 point."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Stability damage dealt by Wise Support increases by 1 point."
          }
        ],
        "icon": "assets/Lotta/Bonds of Friendship.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Amplified Courage",
        "level": "2",
        "effect": "If Phase Weakness is exploited, apply Cold Snap to the target for 1 turn."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Bonds of Friendship",
        "level": "2",
        "effect": "Increases mobility of self by 1 point."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Amplified Courage",
        "level": "3",
        "effect": "Change \"Select Enemy Target\" to \"Select Tile\""
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Bonds of Friendship",
        "level": "3",
        "effect": "Stability damage dealt by Wise Support increases by 1 point."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Cryo Rounds",
        "level": "2",
        "effect": "Increases the duration of Cold Snap by 1 turn."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Neural Adjustment",
        "level": "2",
        "effect": "Replaces Attack Up I with Attack Up II."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Silent Cheer",
        "level": "20",
        "keyName": "Fixed Key 1 - Silent Cheer",
        "description": "At the start of the battle, gain 3 points of Confectance Index.",
        "icon": "assets/Lotta/Fixed Key 1 - Silent Cheer.png"
      },
      {
        "node": "Fixed Key 2 - Confidence Booster",
        "level": "20",
        "keyName": "Fixed Key 2 - Confidence Booster",
        "description": "Increases damage dealt to enemy targets with Freeze type debuffs by 10%.",
        "icon": "assets/Lotta/Fixed Key 2 - Confidence Booster.png"
      },
      {
        "node": "Fixed Key 3 - Trembling Aim",
        "level": "30",
        "keyName": "Fixed Key 3 - Trembling Aim",
        "description": "If Freeze damage is dealt, applies Frozen to the target for 2 turns.",
        "icon": "assets/Lotta/Fixed Key 3 - Trembling Aim.png"
      },
      {
        "node": "Fixed Key 4 - Careful Evasion",
        "level": "30",
        "keyName": "Fixed Key 4 - Careful Evasion",
        "description": "When Hp is greater than 50%, reduces AoE damage taken by 20%.",
        "icon": "assets/Lotta/Fixed Key 4 - Careful Evasion.png"
      },
      {
        "node": "Fixed Key 5 - Bold Shout",
        "level": "40",
        "keyName": "Fixed Key 5 - Bold Shout",
        "description": "Add a new effect to the active skill Cryo Rounds. Knock back the target by 3 tiles.",
        "icon": "assets/Lotta/Fixed Key 5 - Bold Shout.png"
      },
      {
        "node": "Fixed Key 6 - Soothing Touch",
        "level": "40",
        "keyName": "The active skill Neural Adjustment gains a new effect",
        "description": "Gains 1 stack of Quick Barrier.",
        "icon": "assets/Lotta/The active skill Neural Adjustment gains a new effect.png"
      },
      {
        "node": "Affinity Key - New Sprout",
        "level": "-",
        "keyName": "Affinity Key - New Sprout",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Lotta/Affinity Key - New Sprout.png"
      },
      {
        "node": "Common Key - Hunting Trap",
        "level": "40",
        "keyName": "Common Key - Hunting Trap",
        "description": "ATK +3.0% / Increases damage dealt against enemy targets with movement debuffs by 7%.",
        "icon": "assets/Lotta/Common Key - Hunting Trap.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "Before attacking, if the target's Stability is more than 0, increases damage dealt by 10%",
        "icon": "assets/Lotta/Expansion Key.png"
      }
    ]
  },
  "Suomi": {
    "class": "Support",
    "stats": {
      "hp": 1955,
      "atk": 672,
      "def": 617
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Pelting Snowflake",
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
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Suomi/Pelting Snowflake.png"
      },
      {
        "name": "Winter's Wrath",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, dealing Freeze damage equal to 100% of attack to them. This skill's critical rate is reduced by 100%, but additionally deals fixed damage equal to 50% of defense. For each allied unit within 6 tiles, increases Stability Damage dealt by 1 point.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "If it causes Stability Break, increases fixed damage to 125% of defense."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Unyielding Momentum",
            "effect": "After using the active skill Winter's Wrath, if the target goes into / is in Stability Break, restores 2 points of Soumi's Stability."
          }
        ],
        "icon": "assets/Suomi/Winter's Wrath.png"
      },
      {
        "name": "Snow's Grace",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "6",
        "effArea": "Target",
        "description": "Select 1 allied target (excluding self) within 6 tiles and apply Frost Barrier for 2 turns. Frost Barrier absorption amount is equal to 130% of Suomi's initial attack, but cannot exceed 100% of the target's max HP. Restore 2 Stability Index. For each enemy unit within 5 tiles of the selected target, apply 1 stack of Defensive Support for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Applies Impact Response I to the target for 2 turns. For each surrounding large enemy unit, apply 1 additional stack of Defensive Support."
          },
          {
            "type": "fixedKey",
            "number": 3,
            "label": "Fixed Key 3 - Positive Feedback",
            "effect": "When using the active skill Snow's Grace, if the target's HP is below 80%, gain 1 point of Confectance Index."
          }
        ],
        "icon": "assets/Suomi/Snow's Grace.png"
      },
      {
        "name": "Snowfield's Radiance",
        "traits": [
          "Ultimate",
          "Tile"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 5,
        "range": "6",
        "effArea": "3",
        "description": "Selects 1 empty tile within 6 tiles, dealing fixed damage equal to 50% of defense to all enemy targets within 3 tiles, applying 2 stacks of Avalanche.\n\nRestores 2 points of stability, cleanses 1 debuff, and cleanses the effect of Taunt from all allied units. Additionally, applies Frost Barrier and 1 stack of Wintry Bastion for three turns. Frost Barrier absorbs damage equal to 100% of Suomi's initial attack, up to a maximum of 100% of the target's max HP.\n\nAfter this skill is used, generates Frost tiles in a snowflake-shaped area within a 3 tile radius around the selected tile for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the number of stacks of Avalanche by 1.\n\nRecovers HP equal to 30% of Suomi's maximum HP and restores Stability Index by 4 points to all allied units. All allied units (excluding self) gain an additional 1 stack of Wintery Bastion.\n\nIf an allied unit is at full HP before being healed, they gain an additional 1 stack of Shelter and Continuous Healing I for 3 turns."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Applies Defense Up II to all allied units for 3 turns. Increases the number of cleansed debuffs by 2, and also cleanses the effects of Fear, Infatuated, and Stun. Increases restored HP by 50% of Suomi's max HP. Expand the radius of Frost by 1 tile.\n\nThe effect of Shield is enhanced by 30%, up to a maximum of 150% of the target's max HP."
          }
        ],
        "icon": "assets/Suomi/Snowfield's Radiance.png"
      },
      {
        "name": "Source of Warmth",
        "traits": [
          "Passive",
          "Healing",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the action, gains 2 points of Confectance Index, restores 5% of Suomi's max HP to other allied units within 6 tiles. If the target's HP is below 50%, increases the amount restored to 10%.\n\nWhen allied units (excluding Suomi) use basic attacks or skills, Suomi applies 1 stack of Avalanche to a random enemy target within 6 tiles of herself.\n\nWhen an enemy unit within range takes targeted damage from an ally, prioritizes using Action Support once, dealing Physical damage equal to 80% of attack and 3 Stability Damage. Applies Critical Damage Up I to the allied unit for 2 turns. This can be triggered twice per turn. When HP is above 80%, gains Sleepdrift Sprint.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "If allied units have Frost Barrier, apply Warding Light to them.\n\nThe effect Speedrift Sprint is enhanced, support range is increased by 2 tiles."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Additional effect Warding Light is added: when attacked, if Frost Barrier is not broken, inflict 1 point of Stability Damage to the attacker.\n\nSupport Actions now trigger an additional 1 time per turn, and recovers 1 point of Stability Index for other allied units within 4 tiles around the user."
          }
        ],
        "icon": "assets/Suomi/Source of Warmth.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Snowfield's Radiance",
        "level": "2",
        "effect": "Increases the number of stacks of Avalanche by 1.\n\nRecovers HP equal to 30% of Suomi's maximum HP and restores Stability Index by 4 points to all allied units. All allied units (excluding self) gain an additional 1 stack of Wintery Bastion.\n\nIf an allied unit is at full HP before being healed, they gain an additional 1 stack of Shelter and Continuous Healing I for 3 turns."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Source of Warmth",
        "level": "2",
        "effect": "If allied units have Frost Barrier, apply Warding Light to them.\n\nThe effect Speedrift Sprint is enhanced, support range is increased by 2 tiles."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Snow's Grace",
        "level": "2",
        "effect": "Apply Impact Response I to the target for 2 turns. for each surrounding large enemy unit, apply 1 additional stack of Defensive Support."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Winter's Wrath",
        "level": "2",
        "effect": "If it causes Stability Break, increases fixed damage to 125% of defense."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Source of Warmth",
        "level": "3",
        "effect": "Additional effect Warding Light is added: when attacked, if Frost Barrier is not broken, inflict 1 point of Stability Damage to the attacker.\n\nSupport Actions now trigger an additional 1 time per turn, and recovers 1 point of Stability Index for other allied units within 4 tiles around the user."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Snowfield's Radiance",
        "level": "3",
        "effect": "Applies Defense Up II to all allied units for 3 turns. Increases the number of cleansed debuffs by 2, and also cleanses the effects of Fear, Infatuated, and Stun. Increases restored HP by 50% of Suomi's max HP. Expand the radius of Frost by 1 tile.\n\nThe effect of Shield is enhanced by 30%, up to a maximum of 150% of the target's max HP."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Unyielding Momentum",
        "level": "20",
        "keyName": "Fixed Key 1 - Unyielding Momentum",
        "description": "After using the active skill Winter's Wrath, if the target goes into / is in Stability Break, restores 2 points of Soumi's Stability.",
        "icon": "assets/Suomi/Fixed Key 1 - Unyielding Momentum.png"
      },
      {
        "node": "Fixed Key 2 - Little Guardian",
        "level": "20",
        "keyName": "Fixed Key 2 - Little Guardian",
        "description": "At the start of the battle, gain 3 points of Confectance Index.",
        "icon": "assets/Suomi/Fixed Key 2 - Little Guardian.png"
      },
      {
        "node": "Fixed Key 3 - Positive Feedback",
        "level": "30",
        "keyName": "Fixed Key 3 - Positive Feedback",
        "description": "When using the active skill Snow's Grace, if the target's HP is below 80%, gain 1 point of Confectance Index.",
        "icon": "assets/Suomi/Fixed Key 3 - Positive Feedback.png"
      },
      {
        "node": "Fixed Key 4 - Move Swiftly",
        "level": "30",
        "keyName": "Fixed Key 4 - Move Swiftly",
        "description": "At the start of your turn, for each allied unit (excluding self) whose HP is below 80%, increase this unit's mobility by 1 tile.",
        "icon": "assets/Suomi/Fixed Key 4 - Move Swiftly.png"
      },
      {
        "node": "Fixed Key 5 - Immovable",
        "level": "40",
        "keyName": "Fixed Key 5 - Immovable",
        "description": "When inflicted with Stun, Taunt, or Paralysis, immediately cleanse that effect and become immune to Stun, Taunt, or Paralysis for one turn. Simultaneously, gain Frost Barrier for 3 turns. Frost Barrier absorbs damage equal to 60% of base attack, up to a maximum of 100% of Suomi's max HP. This can trigger only 1 time per battle.",
        "icon": "assets/Suomi/Fixed Key 5 - Immovable.png"
      },
      {
        "node": "Fixed Key 6 - Logistics Support in Progress",
        "level": "40",
        "keyName": "Fixed Key 6 - Logistics Support in Progress",
        "description": "At the end of this unit's action, if this unit's stability is greater than 0, recovers 10% of this unit's maximum HP and 1 point of stability.",
        "icon": "assets/Suomi/Fixed Key 6 - Logistics Support in Progress.png"
      },
      {
        "node": "Affinity Key - Rock and Roll",
        "level": "-",
        "keyName": "Affinity Key - Rock and Roll",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Suomi/Affinity Key - Rock and Roll.png"
      },
      {
        "node": "Common Key - Mission's Blessing",
        "level": "40",
        "keyName": "Common Key - Mission's Blessing",
        "description": "DEF +5.0% / When HP drops below 80%, restore 15% of this unit's maximum HP and gain Defense Up III for 2 turns. Can trigger only once per battle.",
        "icon": "assets/Suomi/Common Key - Mission's Blessing.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "Action Support deals Freeze damage instead\n\nWhen allies have Frost Barrier, increases Freeze damage dealt by 15% and restores 4 Stability at the start of the round. Before allies attack, if they do not have Frost Barrier, Suomi immediately applies Frost Barrier on them for 2 turns. Frost Barrier absorbs damage equal to 60% of Suomi's initial attack, up to a maximum of 100% of the target's max HP\n\nSnowfield's Radiance: This skill applies Ice Seal for 2 turns",
        "icon": "assets/Suomi/Expansion Key.png"
      }
    ]
  },
  "Dushevnaya": {
    "class": "Support",
    "stats": {
      "hp": 1851,
      "atk": 757,
      "def": 585
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Heavy Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Light Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Daybreak",
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
        "icon": "assets/Dushevnaya/Daybreak.png"
      },
      {
        "name": "Hero's Code",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 110% of attack to them. If this kills an enemy unit with Freeze debuffs, gains 1 stack of Ice's Grace\n\n(TL Note: Ice's Grace stacks can be gained even if the enemy isn't killed with this skill)",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The number of Ice's Grace stacks gained increases by 1. When the number of stacks reaches 4, the skill's effect is enhanced, increasing the damage dealt to 140%. If the target is on an allied Freeze tile, the damage dealt increases to 160%."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Lance of Longinus",
            "effect": "Each Ice's Grace stack gained above the maximum amount increases the critical rate of Hero's Code by 5%, up to a maximum increase of 30%."
          }
        ],
        "icon": "assets/Dushevnaya/Hero's Code.png"
      },
      {
        "name": "Marzanna's Sanction",
        "traits": [
          "Active",
          "Debuff",
          "Tile"
        ],
        "attribute": "Freeze",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "6",
        "effArea": "2",
        "description": "Selects 1 tile within 6 tiles, dealing AoE Freeze damage equal to 50% of attack to all enemy targets within 2 tiles of the selected tile, and generates Frost tiles for 2 turns.\n\nThe next use of this skill will be enhanced, increasing the damage multiplier to 70%, whilst applying Frigid for 1 turn. This enhancement cannot be enhanced again if the skill has already been enhanced.\n\nIf Confectance Index is full, Marzanna's Sanction can immediately be used again.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Effective range is increased by 1 tile. The initial damage multiplier is increased to 70%. This will be further increased to 90% for the enhanced skill."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Courageous Claymore",
            "effect": "When using Marzanna's Sanction, if it causes the target to enter Stability Break, applies Defense Down II to them for 2 turns."
          }
        ],
        "icon": "assets/Dushevnaya/Marzanna's Sanction.png"
      },
      {
        "name": "Book of Prophecy",
        "traits": [
          "Ultimate",
          "Buff",
          "Support"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "7",
        "description": "Applies 1 stack of Arctic Benediction to all allied units within 7 tiles. Gains 2 points of Confectance Index, as well as Glacial Domain for 2 turns. While Glacial Domain is active, gains 2 points of Confectance Index if it is at 0 at the end of the action.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the effective range by 2 tiles and applies 1 random powerful buff and Movement Up II to all allied units within range for 2 turns. Arctic Benediction increases damage dealt by an additional 10%."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Dispels 1 buff from 4 random enemy units within range. Increases the number of Arctic Benediction stacks applied by 1. While Glacial Domain is active, ignores 30% of the target's defense, The maximum number of Support Attacks increases by 1."
          }
        ],
        "icon": "assets/Dushevnaya/Book of Prophecy.png"
      },
      {
        "name": "Blessed Artwork",
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
        "description": "Increases all allied units' damage by 10%, with an additional 10% boost specifically for Freeze damage. At the end of the action, gains 2 points of Confectance Index.\n\nWhen the user's HP is above 80%, reduces Stability Damage taken by 1 point and gains Insight. While under the effects of Insight, increases the range of active skills and Support Attacks (except Ultimates) by 1 tile.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Attacks ignore 15% of the target's Cover damage reduction. At the start of the action, generates Frost tiles within a 1 tile radius around the user for 2 turns. If the user is standing on an allied Freeze tile, their Stability Damage is increased by 1 point."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Increases the damage of active attacks by 20%, with an additional 40% boost for Freeze damage. After an active attack, dispels 1 defense buff from the target. If the user is standing on an allied Freeze tile, applies Vulnerable II to the target for 2 turns."
          }
        ],
        "icon": "assets/Dushevnaya/Blessed Artwork.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Book of Prophecy",
        "level": "2",
        "effect": "Increases the effective range by 2 tiles and applies 1 random powerful buff and Movement Up II to all allied units within range for 2 turns. Arctic Benediction increases damage dealt by an additional 10%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Blessed Artwork",
        "level": "2",
        "effect": "Attacks ignore 15% of the target's Cover damage reduction. At the start of the action, generates Frost tiles within a 1 tile radius around the user for 2 turns. If the user is standing on an allied Freeze tile, their Stability Damage is increased by 1 point."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Marzanna's Sanction",
        "level": "2",
        "effect": "Effective range is increased by 1 tile. The initial damage multiplier is increased to 70%. This will be further increased to 90% for the enhanced skill."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Hero's Code",
        "level": "2",
        "effect": "The number of Ice's Grace stacks gained increases by 1. When the number of stacks reaches 4, the skill's effect is enhanced, increasing the damage dealt to 140%. If the target is on an allied Freeze tile, the damage dealt increases to 160%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Book of Prophecy",
        "level": "3",
        "effect": "Dispels 1 buff from 4 random enemy units within range. Increases the number of Arctic Benediction stacks applied by 1. While Glacial Domain is active, ignores 30% of the target's defense, The maximum number of Support Attacks increases by 1."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Blessed Artwork",
        "level": "3",
        "effect": "Increases the damage of active attacks by 20%, with an additional 40% boost for Freeze damage. After an active attack, dispels 1 defense buff from the target. If the user is standing on an allied Freeze tile, applies Vulnerable II to the target for 2 turns."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Lance of Longinus",
        "level": "20",
        "keyName": "Fixed Key 1 - Lance of Longinus",
        "description": "Each Ice's Grace stack gained above the maximum amount increases the critical rate of Hero's Code by 5%, up to a maximum increase of 30%.",
        "icon": "assets/Dushevnaya/Fixed Key 1 - Lance of Longinus.png"
      },
      {
        "node": "Fixed Key 2 - Adventurer's Will",
        "level": "20",
        "keyName": "Fixed Key 2 - Adventurer's Will",
        "description": "When an active attack only hits 1 target, increases Freeze damage dealt by 20% and Stability Damage dealt by 2 points.",
        "icon": "assets/Dushevnaya/Fixed Key 2 - Adventurer's Will.png"
      },
      {
        "node": "Fixed Key 3 - Magical Support",
        "level": "30",
        "keyName": "Fixed Key 3 - Magical Support",
        "description": "When an active skill generates Freeze tiles, if there are Freeze tiles within range, triggers a tile reaction, removes the tiles beneath the enemy targets and dispels 1 buff from them. For each tile removed, gains 1 stack of Ice's Grace, up to 3 stacks.",
        "icon": "assets/Dushevnaya/Fixed Key 3 - Magical Support.png"
      },
      {
        "node": "Fixed Key 4 - Courageous Claymore",
        "level": "30",
        "keyName": "Fixed Key 4 - Courageous Claymore",
        "description": "When using Marzanna's Sanction, if it causes the target to enter Stability Break, applies Defense Down II to them for 2 turns.",
        "icon": "assets/Dushevnaya/Fixed Key 4 - Courageous Claymore.png"
      },
      {
        "node": "Fixed Key 5 - Heart of the Sage",
        "level": "40",
        "keyName": "Fixed Key 5 - Heart of the Sage",
        "description": "When under the effects of Glacial Domain, gains immunity to movement debuffs.",
        "icon": "assets/Dushevnaya/Fixed Key 5 - Heart of the Sage.png"
      },
      {
        "node": "Fixed Key 6 - Holy Light",
        "level": "40",
        "keyName": "Fixed Key 6 - Holy Light",
        "description": "At the start of the turn, if this unit is standing on an allied Freeze tile, 2 debuffs are cleansed.",
        "icon": "assets/Dushevnaya/Fixed Key 6 - Holy Light.png"
      },
      {
        "node": "Affinity Key - Shining Memories",
        "level": "-",
        "keyName": "Affinity Key - Shining Memories",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Dushevnaya/Affinity Key - Shining Memories.png"
      },
      {
        "node": "Common Key -  Artistic Inspiration",
        "level": "40",
        "keyName": "Common Key -  Artistic Inspiration",
        "description": "ATK +5.0% / For targets with mobility less than or equal to the user or that cannot move, increases Phase damage dealt by 10%",
        "icon": "assets/Dushevnaya/Common Key -  Artistic Inspiration.png"
      },
      {
        "node": "Expansion Key - Wintersong of the Hero",
        "level": "60",
        "keyName": "Expansion Key - Wintersong of the Hero",
        "description": "When allies deal Freeze damage, gains 1 stack of Ice's Grace, and increases Freeze damage dealt for all allies by 5%, up to 15%\n\nDushevnaya's single target attacks now deals Freeze damage, ignores 30% of the enemy's DEF, and increases Freeze damage dealt to enemies by 30%\n\nAt the start of the battle, increases damage by 10% and increases Freeze damage by 10% for the 2 highest ATK allies (excluding self)",
        "icon": "assets/Dushevnaya/Expansion Key - Wintersong of the Hero.png"
      }
    ]
  },
  "Zhaohui": {
    "class": "Vanguard",
    "stats": {
      "hp": 1975,
      "atk": 757,
      "def": 502
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Light Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Burn"
    ],
    "skills": [
      {
        "name": "Piercing Wind",
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
        "icon": "assets/Zhaohui/Piercing Wind.png"
      },
      {
        "name": "Shadow Snare",
        "traits": [
          "Active",
          "AoE",
          "Control"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "4",
        "description": "Selects a direction and deals AoE Physical damage equal to 110% of attack to all enemy targets within 4 tiles in the selected direction. If the target has any Hydro debuff, applies Stun to the target for 1 turn. Zhaohui gains 1 point of Confectance Index for each target hit, and increases critical rate of the next active attack by 10%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "When applying Stun, it no longer requires the target to have any Hydro debuff. For each target hit, Zhaohui restores 1 point of Stability Index. The critical rate of the next active attack is increased by 20%. Additionally, for each target hit, the critical rate is further increased by 5%."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - Detest Evil",
            "effect": "When the active skill Shadow Snare hits only 1 target, it deals 1 extra instance of fixed damage equal to 10% of attack and applies Damp for 2 turns."
          }
        ],
        "icon": "assets/Zhaohui/Shadow Snare.png"
      },
      {
        "name": "Wanderer's Acumen",
        "traits": [
          "Active",
          "AoE",
          "Summon",
          "Debuff"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "2",
        "description": "Selects 1 empty tile within 6 tiles and summons 1 Imperturbable Arrow, dealing AoE Hydro damage equal to 90% of attack to all enemy targets within 2 tiles of the Imperturbable Arrow, and applies Presence of Mind for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Attack range is increased by 3 tiles, and effective area is increased by 1 tile. Stability damage is increased by 2 points, and damage dealt is increased to 110% of attack."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Light of Justice",
            "effect": "When using the active skill Wanderer's Acumen, Zhaohui gains 1 stack of Quick Barrier and knocks the target back by 2 tiles."
          }
        ],
        "icon": "assets/Zhaohui/Wanderer's Acumen.png"
      },
      {
        "name": "Skybound Leap",
        "traits": [
          "Ultimate",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "9",
        "effArea": "Target",
        "description": "Selects any Imperturbable Arrow within 9 tiles, and lands on the selected tile within 2 tiles around it. Deals Hydro damage equal to 160% of attack to the nearest enemy target within 6 tiles and applies Congestion for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases Stability Damage dealt by 2 points. Applies Presence of Mind to the target for 2 turns. Relocates along with all allied units within 2 tiles of self."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "The critical damage of this attack is increased by 30%, and the damage dealt is increased to 180% of attack. After using this skill, Zhaohui's attack is increased by 10%, up to 3 stacks."
          }
        ],
        "icon": "assets/Zhaohui/Skybound Leap.png"
      },
      {
        "name": "Shadow Strike",
        "traits": [
          "Passive",
          "Support",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the action, Zhaohui may select any Imperturbable Arrow within 9 tiles and land on the selected tile within 2 tiles of the Imperturbable Arrow, gaining 1 point of Confectance Index.\n\nWhen an enemy unit within attack range takes targeted damage from an allied unit, Zhaohui launches Action Support once, dealing Hydro damage equal to 80% of attack, 2 points of Stability Damage, and applies Damp for 2 turns to the enemy unit. This effect can be triggered up to once per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "At the start of the battle, Zhaohui summons 1 Imperturbable Arrow on a surrounding tile. The maximum activation of Action Support is increased by 1. When any Imperturbable Arrow is on the field, Zhaohui's damage dealt is increased by 10%.\n\n(By default, it will be summoned on the tile to the right of Zhaohui. If that tile is invalid, it will be summoned on the tile to the left. If it is still invalid, it will be summoned on the tile behind)"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "At the end of the action, Imperturbable Arrow can now be selected from anywhere on the field. The maximum activation of Action Support is increased by 1. Before attacking, if the target has 2 or more debuffs, increases damage dealt to it by 20%."
          }
        ],
        "icon": "assets/Zhaohui/Shadow Strike.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Shadow Strike",
        "level": "2",
        "effect": "At the start of the battle, Zhaohui summons 1 Imperturbable Arrow on a surrounding tile. The maximum activation of Action Support is increased by 1. When any Imperturbable Arrow is on the field, Zhaohui's damage dealt is increased by 10%.\n\n(By default, it will be summoned on the tile to the right of Zhaohui. If that tile is invalid, it will be summoned on the tile to the left. If it is still invalid, it will be summoned on the tile behind)"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Wanderer's Acumen",
        "level": "2",
        "effect": "Attack range is increased by 3 tiles, and effective area is increased by 1 tile. Stability damage is increased by 2 points, and damage dealt is increased to 110% of attack."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Skybound Leap",
        "level": "2",
        "effect": "Increases Stability Damage dealt by 2 points. Applies Presence of Mind to the target for 2 turns. Relocates along with all allied units within 2 tiles of self."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Shadow Snare",
        "level": "2",
        "effect": "When applying Stun, it no longer requires the target to have any Hydro debuff. For each target hit, Zhaohui restores 1 point of Stability Index. The critical rate of the next active attack is increased by 20%. Additionally, for each target hit, the critical rate is further increased by 5%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Shadow Strike",
        "level": "3",
        "effect": "At the end of the action, Imperturbable Arrow can now be selected from anywhere on the field. The maximum activation of Action Support is increased by 1. Before attacking, if the target has 2 or more debuffs, increases damage dealt to it by 20%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Skybound Leap",
        "level": "3",
        "effect": "The critical damage of this attack is increased by 30%, and the damage dealt is increased to 180% of attack. After using this skill, Zhaohui's attack is increased by 10%, up to 3 stacks."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Weakness Exposed",
        "level": "20",
        "keyName": "Fixed Key 1 - Weakness Exposed",
        "description": "Increases damage dealt against targets with Hydro debuffs by 10%.",
        "icon": "assets/Zhaohui/Fixed Key 1 - Weakness Exposed.png"
      },
      {
        "node": "Fixed Key 2 - Detest Evil",
        "level": "20",
        "keyName": "Fixed Key 2 - Detest Evil",
        "description": "When the active skill Shadow Snare hits only 1 target, it deals 1 extra instance of fixed damage equal to 10% of attack and applies Damp for 2 turns.",
        "icon": "assets/Zhaohui/Fixed Key 2 - Detest Evil.png"
      },
      {
        "node": "Fixed Key 3 - Buffer Time",
        "level": "30",
        "keyName": "Fixed Key 3 - Buffer Time",
        "description": "If any Imperturbable Arrow is on the field, restores 10% of Zhaohui's HP at the end of the action.",
        "icon": "assets/Zhaohui/Fixed Key 3 - Buffer Time.png"
      },
      {
        "node": "Fixed Key 4 - Light of Justice",
        "level": "30",
        "keyName": "Fixed Key 4 - Light of Justice",
        "description": "When using the active skill Wanderer's Acumen, Zhaohui gains 1 stack of Quick Barrier and knocks the target back by 2 tiles.",
        "icon": "assets/Zhaohui/Fixed Key 4 - Light of Justice.png"
      },
      {
        "node": "Fixed Key 5 - Solidifying Rhythm",
        "level": "40",
        "keyName": "Fixed Key 5 - Solidifying Rhythm",
        "description": "If Zhaohui is within 2 tiles of any Imperturbable Arrow, reduces Stability Damage taken by 1 point and AoE damage taken by 30%.",
        "icon": "assets/Zhaohui/Fixed Key 5 - Solidifying Rhythm.png"
      },
      {
        "node": "Fixed Key 6 - Dry Humor",
        "level": "40",
        "keyName": "Fixed Key 6 - Dry Humor",
        "description": "Before using Action Support, dispels 2 buffs from the target.",
        "icon": "assets/Zhaohui/Fixed Key 6 - Dry Humor.png"
      },
      {
        "node": "Affinity Key",
        "level": "40",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Zhaohui/Affinity Key.png"
      },
      {
        "node": "Common Key - Suona's Realm",
        "level": "40",
        "keyName": "Common Key - Suona's Realm",
        "description": "CRIT +5.0% / At the start of the turn, increases the critical damage of the next active attack by 10%.",
        "icon": "assets/Zhaohui/Common Key - Suona's Realm.png"
      },
      {
        "node": "Expansion Key - Perfect Form",
        "level": "60",
        "keyName": "Expansion Key - Perfect Form",
        "description": "Increases Hydro damage dealt towards targets in Stability Break by 45%\n\nAfter executing a teleport with Shadow Strike, deals Hydro damage equal to 80% ATK and 2 Stability damage to the nearest enemy target within attack range, applies Damp for 2 turns, and increases Confectance Index by 1 point",
        "icon": "assets/Zhaohui/Expansion Key - Perfect Form.png"
      }
    ]
  },
  "Papasha": {
    "class": "Sentinel",
    "stats": {
      "hp": 1893,
      "atk": 802,
      "def": 528
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Light Ammo"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Warning Shot",
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
        "description": "Selects 1 enemy target within 6 tiles, dealing Physical damage equal to 60% of attack to them.",
        "upgrades": [],
        "icon": "assets/Papasha/Warning Shot.png"
      },
      {
        "name": "Honor Guard",
        "traits": [
          "Active",
          "AoE",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 2,
        "range": "6",
        "effArea": "1",
        "description": "Selects 1 enemy target within 6 tiles, dealing AoE Physical damage equal to 80% of attack to the target and all enemy targets within 1 tile. If the selected target's Stability Index remains greater than 0 after the attack, the City Warden gains Courage to Endure for 3 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The duration of the City Warden's Self-Repair is reduced by 1 turn. After the user is healed, the City Warden restores HP equal to 20% of its max HP.\n\nThe Stability requirement for the target has been removed. The effects of Courage to Endure is enhanced: Ignores 30% of defense when attacking Large Targets."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Glory With Us",
            "effect": "When using the active skill Honor Guard to attack a Large Target, increases damage dealt by 20%. The Stability Damage of the City Warden's active skill Counter Terrorism Support is increased by 2 points."
          }
        ],
        "icon": "assets/Papasha/Honor Guard.png"
      },
      {
        "name": "Joint Breakthrough",
        "traits": [
          "Active",
          "Targeted",
          "Cleanse"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "6",
        "effArea": "Entire Map",
        "description": "Selects 1 tile within 6 tiles, cleansing 2 debuffs from the user, as well as all control, Command Prohibition effects, and the Frigid effects from the City Warden. The City Warden moves to the selected tile and attacks the closest enemy to Papasha, dealing Physical damage equal to 150% of attack. This attack has an additional 50% damage boost against Large Targets.\n\nAfter using this skill, the City Warden will not move independently for the remainder of the turn. This skill cannot be used if City Warden is undergoing Self-Repair.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Tile casting range is expanded to the entire battlefield, and this attack is guaranteed to deal a critical hit. At the end of the turn, the City Warden launches 1 more instance of Counter Terrorism Support on the nearest enemy target."
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Final Assault",
            "effect": "When the active skill Joint Breakthrough deals damage, if there are no enemy units within 3 tiles around the City Warden, damage dealt is increased by 10%."
          }
        ],
        "icon": "assets/Papasha/Joint Breakthrough.png"
      },
      {
        "name": "Heart of Protection",
        "traits": [
          "Ultimate",
          "Targeted",
          "Buff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles, dealing Physical damage equal to 150% of attack. The City Warden gains Tenacity to Withstand for 2 turns.\n\nBefore the attack, for each buff the user has, the City Warden gains 1 random attack buff, up to a maximum of 2 buffs, lasting for 2 turns.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The effects of Tenacity to Withstand are enhanced: Increases the damage taken by the target up to 80%. The potency of the random attack buffs is amplified, and the maximum number of attack buffs gained is increased to 3 buffs. For every more than 1 stack of Power of Unity, it counts as 1 independent buff."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "The City Warden gains Tenacity to Withstand permanently at the start of the battle. Heart of Protection now applies Resolve to Defend for 2 turns."
          }
        ],
        "icon": "assets/Papasha/Heart of Protection.png"
      },
      {
        "name": "United Guards",
        "traits": [
          "Passive",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the battle, summons a City Warden near the user.\n\nAfter either the user or the City Warden attacks, the user gains 1 point of Confectance Index.\n\nWhen the user lands a critical hit, the City Warden's next attack receives a 20% critical rate boost. Similarly, when the City Warden lands a critical hit, the user's next attack gains a 20% critical rate boost.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "When the City Warden is summoned, its critical rate is increased by 30% and critical damage by 20%. At the start of the battle, the user gains 3 stacks of Power of Unity. At the end of the action, the user gains 1 stack of Power of Unity."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "The City Warden gains Security Monitoring."
          }
        ],
        "icon": "assets/Papasha/United Guards.png"
      },
      {
        "name": "Counter Terrorism Support",
        "traits": [
          "Passive",
          "Support"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Entire Map",
        "effArea": "Target",
        "description": "After Papasha attacks an enemy target, the City Warden will follow up with a Support Attack on the same target, dealing Physical damage equal to 80% of attack.",
        "upgrades": [],
        "icon": "assets/Papasha/Counter Terrorism Support.png"
      },
      {
        "name": "Explosion Prevention Measures",
        "traits": [
          "Passive",
          "Healing"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of the turn, City Warden will move independently to seek Cover.\n\nThe City Warden's healed received is reduced by 100% and it cannot receive shields. When Papasha is healed, the City Warden restores 10% of its max HP.\n\nWhen the City Warden takes fatal damage, it enters the Self-Repair state for 1 turn.",
        "upgrades": [],
        "icon": "assets/Papasha/Explosion Prevention Measures.png"
      },
      {
        "name": "Security Monitoring",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": null,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "WIP",
        "effArea": "WIP",
        "description": "At the end of this unit's action, perform Surveillance on the entire map. When an enemy unit uses a basic attack or an active attack, damage them for 40% of own attack. This effect can trigger 1 time per turn.\n\nThis passive is only unlocked after reaching Vertebrae 5",
        "upgrades": [],
        "icon": "assets/Papasha/Security Monitoring.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Honor Guard",
        "level": "2",
        "effect": "The duration of the City Warden's Self-Repair is reduced by 1 turn. After the user is healed, the City Warden restores HP equal to 20% of its max HP.\n\nThe Stability requirement for the target has been removed. The effects of Courage to Endure is enhanced: Ignores 30% of defense when attacking Large Targets."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Silent Breakthrough",
        "level": "2",
        "effect": "Tile casting range is expanded to the entire battlefield, and this attack is guaranteed to deal a critical hit. At the end of the turn, City Warden launches 1 more instance of Counter Terrorism Support on the nearest enemy target."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "United Guards",
        "level": "2",
        "effect": "When the City Warden is summoned, its critical rate is increased by 30% and critical damage by 20%. At the start of the battle, the user gains 3 stacks of Power of Unity. At the end of the action, the user gains 1 stack of Power of Unity."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Heart of Protection",
        "level": "2",
        "effect": "The effects of Tenacity to Withstand are enhanced: Increases the damage taken by the target up to 80%. The potency of the random attack buffs is amplified, and the maximum number of attack buffs gained is increased to 3 buffs. For every more than 1 stack of Power of Unity, it counts as 1 independent buff."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "United Guards",
        "level": "3",
        "effect": "The City Warden gains Security Monitoring."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Heart of Protection",
        "level": "3",
        "effect": "The City Warden gains Tenacity to Withstand permanently at the start of the battle. Heart of Protection now applies Resolve to Defend for 2 turns."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Glory With Us",
        "level": "20",
        "keyName": "Fixed Key 1 - Glory With Us",
        "description": "When using the active skill Honor Guard to attack a Large Target, increases damage dealt by 20%. The stability damage of the City Warden's active skill Counter Terrorism Support is increased by 2 points.",
        "icon": "assets/Papasha/Fixed Key 1 - Glory With Us.png"
      },
      {
        "node": "Fixed Key 2 - Vow to Defend",
        "level": "20",
        "keyName": "Fixed Key 2 - Vow to Defend",
        "description": "When the City Warden is undergoing Self-Repair, Papasha's damage dealt is increased by 20%.",
        "icon": "assets/Papasha/Fixed Key 2 - Vow to Defend.png"
      },
      {
        "node": "Fixed Key 3 - Unwavering Conviction",
        "level": "30",
        "keyName": "Fixed Key 3 - Unwavering Conviction",
        "description": "City Warden is unable to move independently, but its attack is increased by 10%.",
        "icon": "assets/Papasha/Fixed Key 3 - Unwavering Conviction.png"
      },
      {
        "node": "Fixed Key 4 - Final Assault",
        "level": "30",
        "keyName": "Fixed Key 4 - Final Assault",
        "description": "When the active skill Joint Breakthrough deals damage, if there are no enemy units within 3 tiles around the City Warden, damage dealt is increased by 10%.",
        "icon": "assets/Papasha/Fixed Key 4 - Final Assault.png"
      },
      {
        "node": "Fixed Key 5 - I'll Learn It",
        "level": "40",
        "keyName": "Fixed Key 5 - I'll Learn It",
        "description": "At the start of the turn, if Papasha has less than or equal to 1 buff that can be dispelled, she gains 1 random buff that can be dispelled for 1 turn.",
        "icon": "assets/Papasha/Fixed Key 5 - I'll Learn It.png"
      },
      {
        "node": "Fixed Key 6 - Strength in Unity",
        "level": "40",
        "keyName": "Fixed Key 6 - Strength in Unity",
        "description": "At the start of the turn, the unit with the lower attack between the user and the City Warden gains Accolade's Brilliance for 1 turn.",
        "icon": "assets/Papasha/Fixed Key 6 - Strength in Unity.png"
      },
      {
        "node": "Affinity Key - Unbreakable Faith",
        "level": "-",
        "keyName": "Affinity Key - Unbreakable Faith",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Papasha/Affinity Key - Unbreakable Faith.png"
      },
      {
        "node": "Common Key - Brilliant Medal",
        "level": "40",
        "keyName": "Common Key - Brilliant Medal",
        "description": "ATK +5.0% / Increases damage dealt by allied units' support skills (excluding self) by 10%. Can trigger at most once per turn.",
        "icon": "assets/Papasha/Common Key - Brilliant Medal.png"
      },
      {
        "node": "Expansion Key - Unfallen City",
        "level": "60",
        "keyName": "Expansion Key - Unfallen City",
        "description": "The damage dealt by the City Warden is increased by 50%. While the City Warden is present, all friendly summoned units deal 30% more damage, and at the end of their turn, they gain Damage Reduction III for 1 turn. Confectance Cost of active skill Silent Breakthrough is reduced by 3 points. When activated, the City Warden gains 2 stacks of Steel Forging.",
        "icon": "assets/Papasha/Expansion Key - Unfallen City.png"
      }
    ]
  },
  "Klukai": {
    "class": "Sentinel",
    "stats": {
      "hp": 1893,
      "atk": 827,
      "def": 504
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Swift Strike",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Klukai/Swift Strike.png"
      },
      {
        "name": "Pinpoint Detonation",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles, dealing Corrosion damage equal to 80% of attack. Performs an additional attack, deals AoE Corrosion damage equal to 60% of attack to the target and all enemy targets within 3 tiles, pulling all affected enemy targets 1 tile towards the center.\n\nIf any enemy targets are killed, reduces the cooldown of the Ultimate skill Devastating Drift by 1 turn, and gains 2 points of Confectance Index.\n\nIf no enemy targets are killed, applies 1 stack of Corrosive Infusion to the target for 2 turns.",
        "upgrades": [],
        "icon": "assets/Klukai/Pinpoint Detonation.png"
      },
      {
        "name": "Overpowering Corrosion",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 tile within a 8 tiles, dealing AoE Corrosion damage equal to 90% of attack to all enemy targets within 3 tiles, and applies Toxic Infiltration for 2 turns. Increases damage by 15% to targets already affected by Toxic Infiltration.",
        "upgrades": [],
        "icon": "assets/Klukai/Overpowering Corrosion.png"
      },
      {
        "name": "Devastating Drift",
        "traits": [
          "Ultimate",
          "AoE"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 2,
        "cooldown": 6,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within a cross-shaped area of 4 to 8 tiles, landing on the selected tile and dealing AoE Corrosion damage equal to 100% of attack to all enemy targets in a 5 tiles wide path. Gains 6 tiles of Additional Movement. If 2 or more targets are killed, this skill can be used again. up to a maximum of 1 additional time.",
        "upgrades": [
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - One Fell Swoop",
            "effect": "If the Ultimate skill Devastating Drift only hits 1 target, increases the damage dealt by 30%."
          },
          {
            "type": "fixedKey",
            "number": 5,
            "label": "Fixed Key 5 - Limit Break",
            "effect": "Reduces the width of the Ultimate skill Devastating Drift's effective area to 3 tiles. For each tile reduced, increases damage dealt by 10%."
          }
        ],
        "icon": "assets/Klukai/Devastating Drift.png"
      },
      {
        "name": "Elite's Pride",
        "traits": [
          "Passive",
          "Debuff",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Immune to all negative Control-type tile effects. When dealing damage with active attacks, applies 1 stack of Corrosive Infusion to the target for 2 turns, and gains 1 stack of Competitive Spirit after skill usage.\n\nEach time Klukai performs an active attack or other allied units deal Corrosion damage, Klukai gains 1 point of Confectance Index. For every 3 points of Confectance Index gained, reduces the cooldown of her Ultimate skill by 1 turn.",
        "upgrades": [],
        "icon": "assets/Klukai/Elite's Pride.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Overpowering Corrosion",
        "level": "2",
        "effect": "Increases damage dealt to targets that are already inflicted with Toxic Infiltration by 30%.\n\nIf the target is not killed from this damage, it can also trigger the on-death effect of Toxic Infiltration.\n\nToxic Infiltration has a new effect: At the end of the action of the unit which possesses this effect, the inflictor applies Toxic Infiltration to enemy units within 3 tiles that do not possess Toxic Infiltration for 2 turns."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Elite's Pride",
        "level": "2",
        "effect": "At the start of the battle, gains 3 stacks of Competitive Spirit. When other allied units deal Corrosion damage, Klukai can gain 1 stack of Competitive Spirit. Increases the stack limit of Competitive Spirit by 4 stacks. \n\nFor every 3 points of Confectance Index gained, applies an additional 1 stack of Corrosive Infusion to enemy units with Corrosive Infusion, and reduces the cooldown of Klukai's Ultimate skill by 1 turn.\n\nCorrosive Infusion gains a new affect: When Klukai performs an active attack or other allied units deal Corrosion damage, applies an additional 1 stack of Corrosive Infusion to targets with Corrosive Infusion. Defense is reduced by 1%, and the stack limit is increased by 5 stacks."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Devastating Drift",
        "level": "2",
        "effect": "For each enemy hit, increases damage dealt by an additional 10%, up to a maximum of 50%. If a Boss is hit, this increase will be immediately raised to the maximum value 50%. \n\nIf 2 or more targets or a Boss is hit, this skill can be used again, up to a maximum of 1 additional time. Before attacking, applies Defense Down II and Toxic Infiltration to the target for 2 turns."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Pinpoint Detonation",
        "level": "2",
        "effect": "Increases damage dealt by the first damage instance to 100% of attack. For each stack of Corrosive Infusion on the target, the damage multiplier of the additional attack is increased by 5%. If a phase weakness is exploited, the attack ignores 15% of the target's Cover damage reduction."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Overpowering Corrosion",
        "level": "3",
        "effect": "Effective range is increased by 2 tiles, damage increases to 110% of attack. Toxic Infiltration spread radius increases by 1 tile, and the damage it deals increases to 80% of attack. If the target is inflicted with a Corrosion debuffs, applies Toxic Infiltration for 2 turns before the attack.\n\nToxic Infiltration gains an additional effect: When receiving an active attack from Klukai, damage taken is increased by 30%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Devastating Drift",
        "level": "3",
        "effect": "Ignores Cover damage reduction.\n\nIncreases width by 2 tiles and applies Dismay for 2 turns.\n\nAfter the attack, triggers all enemies' effects of Corrosive Infusion and the on-death effects of Toxic Infiltration."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Deadly Entwine",
        "level": "20",
        "keyName": "Fixed Key 1 - Deadly Entwine",
        "description": "At the start of the turn, if there is only one target, applies 1 stack of Corrosive Infusion to them for 2 turns. Additionally, gains 2 points of Confectance Index.",
        "icon": "assets/Klukai/Fixed Key 1 - Deadly Entwine.png"
      },
      {
        "node": "Fixed Key 2 - One Fell Swoop",
        "level": "20",
        "keyName": "Fixed Key 2 - One Fell Swoop",
        "description": "If the Ultimate skill Devastating Drift only hits 1 target, increases the damage dealt by 30%.",
        "icon": "assets/Klukai/Fixed Key 2 - One Fell Swoop.png"
      },
      {
        "node": "Fixed Key 3 - No Mercy",
        "level": "30",
        "keyName": "Fixed Key 3 - No Mercy",
        "description": "Corrosive Infusion gains a new effect, it increases damage to targets in Stability Break by 15%.",
        "icon": "assets/Klukai/Fixed Key 3 - No Mercy.png"
      },
      {
        "node": "Fixed Key 4 - Strong Support",
        "level": "30",
        "keyName": "Fixed Key 4 - Strong Support",
        "description": "For every Support Attack performed by other allied units, gains 1 point of Confectance Index.",
        "icon": "assets/Klukai/Fixed Key 4 - Strong Support.png"
      },
      {
        "node": "Fixed Key 5 - Limit Break",
        "level": "40",
        "keyName": "Fixed Key 5 - Limit Break",
        "description": "Reduces the width of the Ultimate skill Devastating Drift's effective area to 3 tiles. For each tile reduced, increases damage dealt by 10%.",
        "icon": "assets/Klukai/Fixed Key 5 - Limit Break.png"
      },
      {
        "node": "Fixed Key 6 - Moment of Doom",
        "level": "40",
        "keyName": "Fixed Key 6 - Moment of Doom",
        "description": "After the unit(s) afflicted with Toxic Infiltration take damage from its effect and survive, they are inflicted with 1 stack of Corrosive Infusion for 2 turns.",
        "icon": "assets/Klukai/Fixed Key 6 - Moment of Doom.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Klukai/Affinity Key.png"
      },
      {
        "node": "Common Key - Murderous Return",
        "level": "40",
        "keyName": "Common Key - Murderous Return",
        "description": "ATK +5.0% / At the start of the turn, if the user's Confectance Index is full, the next instance of AoE damage inflicted by an active attack is increased by 10%.",
        "icon": "assets/Klukai/Common Key - Murderous Return.png"
      },
      {
        "node": "Expansion Key - The Pride of Elite Doll",
        "level": "60",
        "keyName": "Expansion Key - The Pride of Elite Doll",
        "description": "At the start of combat, summon Fang drone to follow Klukai. Fang is not targetable and not considered a separate summoned unit. \n\nAfter an active attack done by Klukai, Fang attacks 3 nearest enemy targets, dealing AoE Corrosion damage equal to 100% of Klukai ATK that ignores cover, and applies 1 stack of Toxic Infiltration. The damage multiplier is increased by 10% each time the Corrosive Infusion effect or the on-death effect of Toxic Infiltration is triggered.\n\nWhen Corrosive Infusion effect is triggered, the damage coefficient of Corrosive Infusion is increased for each stack of Competitive Spirit by an additional 1% .",
        "icon": "assets/Klukai/Expansion Key - The Pride of Elite Doll.png"
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
  "Vector": {
    "class": "Support",
    "stats": {
      "hp": 1819,
      "atk": 748,
      "def": 569
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Burn"
    ],
    "weaknesses": [
      "Medium Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Depressive Mentality",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Increases damage multiplier of Burn and fixed damage by 30%.\n\nThe target does not need to have Burn type debuff to deal fixed damage. Additionally applies Overheat Combustion on the target for 2 turns.\n\nVector gains 2 more points of Confectance Index."
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Hospice Care",
            "effect": "Dead End Meltdown: If this skill killed the target, generates Incineration tiles within a 3 tile radius of the target for 2 turns"
          }
        ],
        "icon": "assets/Vector/Depressive Mentality.png"
      },
      {
        "name": "Portent of Doom",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Burn damage equivalent to 100% ATK to it, and applies Smolder for 2 turns. Vector gains 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Increases damage multiplier by 30%\n\nNew effect is added for Smolder - for each Burn type debuff held, increases damage taken by 3%\n\nApplies Overheat for 1 turn. Vector gains 2 more points of Confectance Index."
          }
        ],
        "icon": "assets/Vector/Portent of Doom.png"
      },
      {
        "name": "Searing Finale",
        "traits": [
          "Ultimate",
          "AoE",
          "Tile",
          "Buff"
        ],
        "attribute": "Burn",
        "stabilityDamage": 1,
        "cooldown": 4,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "7",
        "description": "Selects a tile within a 7 tile radius, deals AoE Burn damage equivalent to 60% ATK to all enemies and generates Incineration tiles that lasts for 2 turns within a 7 tile radius of the designated tile. Applies Accelerant to all allies for 2 turns. Vector gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Enhances the effect for Accelerant - When dealing Burn damage, increases damage dealt by 20% (from 10% to 30%).\n\nApplies Blazing Assault II to all allied units for 2 turns, and cleanses 2 debuffs for all allies."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "New effect is added for Accelerant - When dealing Burn damage, increases CRIT DMG by 15%. For each Burn type buff held, increases damage dealt by 5%\n\nVector gains Apathetic Resistance for 2 turns."
          }
        ],
        "icon": "assets/Vector/Searing Finale.png"
      },
      {
        "name": "Perception Block",
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
        "description": "Vector is immune from the negative effects of Burn tiles.\n\nBefore dealing Burn damage, if the target has Overburn, applies Overheat Combustion on the target for 2 turns\n\nAt the start of the battle, increases the attack count of Support attack that deals Burn damage by 1\n\nAt the start of each turn, if Vector's Confectance Index is full, Vector consumes all points of Confectance Index, and increases ATK by 10% until the end of the round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "New effect is added for Overheat Combustion - Increases Burn damage taken by 30%, fixed damage is dealt to all enemies within a 3x3 tile radius of the target, and increases the attack count of Support attack that deals Burn damage by 2 instead."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "New effect is added for Overheat Combustion - At the end of the action, generates Incineration tiles within a 1 tile radius of self. The fixed damage multiplier is increased by 10%.\n\nAt the start of each turn, for each excess Confectance Index point above the maximum, increases ATK by 10%, up to 20%."
          }
        ],
        "icon": "assets/Vector/Perception Block.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Perception Block",
        "level": "2",
        "effect": "New effect is added for Overheat Combustion - Increases Burn damage taken by 30%, fixed damage is dealt to all enemies within a 3x3 tile radius of the target, and increases the attack count of Support attack that deals Burn damage by 2 instead."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Searing Finale",
        "level": "2",
        "effect": "Enhances the effect for Accelerant - When dealing Burn damage, increases damage dealt by 20% (from 10% to 30%).\n\nApplies Blazing Assault II to all allied units for 2 turns, and cleanses 2 debuffs for all allies."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Dead End Meltdown",
        "level": "2",
        "effect": "Increases damage multiplier of Burn and fixed damage by 30%.\n\nThe target does not need to have Burn type debuff to deal fixed damage. Additionally applies Overheat Combustion on the target for 2 turns.\n\nVector gains 2 more points of Confectance Index."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Portent of Doom",
        "level": "2",
        "effect": "Increases damage multiplier by 30%\n\nNew effect is added for Smolder - for each Burn type debuff held, increases damage taken by 3%\n\nApplies Overheat for 1 turn. Vector gains 2 more points of Confectance Index."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Perception Block",
        "level": "3",
        "effect": "New effect is added for Overheat Combustion - At the end of the action, generates Incineration tiles within a 1 tile radius of self. The fixed damage multiplier is increased by 10%.\n\nAt the start of each turn, for each excess Confectance Index point above the maximum, increases ATK by 10%, up to 20%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Searing Finale",
        "level": "3",
        "effect": "New effect is added for Accelerant - When dealing Burn damage, increases CRIT DMG by 15%. For each Burn type buff held, increases damage dealt by 5%\n\nVector gains Apathetic Resistance for 2 turns."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Hospice Care",
        "level": "20",
        "keyName": "Dead End Meltdown",
        "description": "If this skill killed the target, generates Incineration tiles within a 3 tile radius of the target for 2 turns",
        "icon": "assets/Vector/Dead End Meltdown.png"
      },
      {
        "node": "Fixed Key 2 - Splattering Pessimism",
        "level": "20",
        "keyName": "Fixed Key 2 - Splattering Pessimism",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Vector/Fixed Key 2 - Splattering Pessimism.png"
      },
      {
        "node": "Fixed Key 3 - Dispassionate Support",
        "level": "30",
        "keyName": "Fixed Key 3 - Dispassionate Support",
        "description": "Before using an active attack, dispels 2 buffs from the target",
        "icon": "assets/Vector/Fixed Key 3 - Dispassionate Support.png"
      },
      {
        "node": "Fixed Key 4 - Proliferating Despair",
        "level": "30",
        "keyName": "Fixed Key 4 - Proliferating Despair",
        "description": "When an active attack deals damage against a large target, deals an additional instance of fixed damage equivalent to 15% ATK",
        "icon": "assets/Vector/Fixed Key 4 - Proliferating Despair.png"
      },
      {
        "node": "Fixed Key 5 - Unfortunate Jinx",
        "level": "40",
        "keyName": "Fixed Key 5 - Unfortunate Jinx",
        "description": "When Vector is on a Burn type tile, decreases damage received by 20%, and recovers 2 Stability and 10% max HP at the end of the action",
        "icon": "assets/Vector/Fixed Key 5 - Unfortunate Jinx.png"
      },
      {
        "node": "Fixed Key 6 - Negative Motivation",
        "level": "40",
        "keyName": "Fixed Key 6 - Negative Motivation",
        "description": "If Overburn is applied on an enemy within attack range, undergoes an instance of Emergency Support, dealing Burn damage equivalent to 60% ATK and 1 Stability Damage. This effect can be activated once per turn",
        "icon": "assets/Vector/Fixed Key 6 - Negative Motivation.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Vector/Affinity Key.png"
      },
      {
        "node": "Common Key - Death Knell",
        "level": "40",
        "keyName": "Common Key - Death Knell",
        "description": "ATK +5.0% / At the start of the turn, if there are enemies with Burn type debuffs, increases ATK by 8%",
        "icon": "assets/Vector/Common Key - Death Knell.png"
      },
      {
        "node": "Expansion Key - Depression Empathy",
        "level": "60",
        "keyName": "Expansion Key - Depression Empathy",
        "description": "After every active attack cooldown of Searing Finale is reduced by 1 turn. \nAfter a friendly unit performs a support attack that deals Burn damage, Vector gains 1 point of Confectance Index and restores HP equal to 15% of Vector's ATK to all friendly units on the field. This can be triggered up to 4 times per round.",
        "icon": "assets/Vector/Expansion Key - Depression Empathy.png"
      }
    ]
  },
  "Belka": {
    "class": "Vanguard",
    "stats": {
      "hp": 1770,
      "atk": 757,
      "def": 528
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Medium Ammo",
      "Electric"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Nutcracker Shell",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Belka/Nutcracker Shell.png"
      },
      {
        "name": "Sylvan Vault",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Physical damage equivalent to 130% ATK to it. Increases the damage of this attack based on (3% x the number of Negative Charge) on the field, up to a maximum of 15%. If the target is a boss unit and has Negative Charge, increases damage immediately to 15% instead\n\nIf thie attack CRITs, increases Confectance Index by 1 point. After this skill is used, selects an empty tile within a 6 tile range and lands on the designated tile",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases Stability damage dealt by 2 points. Increases CRIT DMG of this attack by 30%\n\nIncreases the damage of this attack based on (6% x the number of Negative Charge) on the field, up to a maximum of 30%. If the target is a boss unit and has Negative Charge, increases damage immediately to 30% instead"
          }
        ],
        "icon": "assets/Belka/Sylvan Vault.png"
      },
      {
        "name": "Crackling Core",
        "traits": [
          "Active",
          "Targeted",
          "Buff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius and deals Electric damage equivalent to 130% ATK. For each movement point consumed, increases damage multiplier by 5%\n\nBelka gains 1 layer of Active Engagement. After this skill is used, Belka can use Sylvan Vault or Nutcracker Shell",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "For each movement point consumed, increases damage multiplier by 8% instead. Increases damage by 15% towards enemy targets with Negative Charge"
          },
          {
            "type": "fixedKey",
            "number": 4,
            "label": "Fixed Key 4 - Raised Tail",
            "effect": "Crackling Core: When using this skill to attack a target with Negative Charge, increases ATK by 10%"
          }
        ],
        "icon": "assets/Belka/Crackling Core (row 64).png"
      },
      {
        "name": "Leaping Arc",
        "traits": [
          "Ultimate",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "8",
        "effArea": "Target",
        "description": "Selects an enemy target within a 8 tile radius and deals Electric damage equivalent to 160% ATK, and applies Conductivity for 1 turn. For each movement point consumed, increases damage multiplier by 5%. Belka gains Continual Release for 2 turns",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Gains one stack of Active Engagement\n\nNew effect is added for Continual Release - If the target of this skill is the same as the target of Continual Release this turn, applies Overflowing Electrons before attacking that lasts for 2 turns"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "For each movement point consumed, increases damage multiplier by 10% instead. Increases the damage multiplier of Continual Release by 30%\n\nIf the target has 2 or more Electric type debuffs, increases CRIT DMG by 30%"
          },
          {
            "type": "fixedKey",
            "number": 6,
            "label": "Fixed Key 6 - Deciding Motive",
            "effect": "Leaping Arc: Before this skill is used, dispels 2 buffs from the target"
          }
        ],
        "icon": "assets/Belka/Leaping Arc (row 94).png"
      },
      {
        "name": "Forest's Secrets",
        "traits": [
          "Passive",
          "Debuff",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the turn, increases Confectance Index by 1 point\n\nBefore attacking, applies Negative Charge on the target and the nearest enemy for 1 turn. If the target is killed, gains Concealment\n\nFor each Negative Charge applied by allies, increases CRIT rate by 5%, up to a maximum of 30%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Before attacking, applies Conductivity on the target for 1 turn. When attacking enemy targets with Negative Charge, ignores 10% DEF\n\nWhen Belka deals single target Electric damage towards enemy targets with Negative Charge, increases the damage multiplier of fixed damage dealt by Negative Charge to 40%. For each Electric damage dealt by allies, Belka gains 1 stack of Stored Charge"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "At the start of the battle, increases movement speed and attack range by 1 tile\n\nIncreases the upper limit of Stored Charge by 4 stacks. For each instance of Electric damage dealt by self, additionally gains 1 stack of Stored Charge"
          }
        ],
        "icon": "assets/Belka/Forest's Secrets.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Crackling Core",
        "level": "2",
        "effect": "For each movement point consumed, increases damage multiplier by 8% instead. Increases damage by 15% towards enemy targets with Negative Charge"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Leaping Arc",
        "level": "2",
        "effect": "Gains one stack of Active Engagement\n\nNew effect is added for Continual Release - If the target of this skill is the same as the target of Continual Release this turn, applies Overflowing Electrons before attacking that lasts for 2 turns"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Forest's Secrets",
        "level": "2",
        "effect": "Before attacking, applies Conductivity on the target for 1 turn. When attacking enemy targets with Negative Charge, ignores 10% DEF\n\nWhen Belka deals single target Electric damage towards enemy targets with Negative Charge, increases the damage multiplier of fixed damage dealt by Negative Charge to 40%. For each Electric damage dealt by allies, Belka gains 1 stack of Stored Charge"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Forest's Secrets",
        "level": "3",
        "effect": "At the start of the battle, increases movement speed and attack range by 1 tile\n\nIncreases the upper limit of Stored Charge by 4 stacks. For each instance of Electric damage dealt by self, additionally gains 1 stack of Stored Charge"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Sylvan Vault",
        "level": "2",
        "effect": "Increases Stability damage dealt by 2 points. Increases CRIT DMG of this attack by 30%\n\nIncreases the damage of this attack based on 6% x the number of Negative Charge on the field, up to a maximum of 30%. If the target is a boss unit and has Negative Charge, increases damage immediately to 30% instead"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Leaping Arc",
        "level": "3",
        "effect": "For each movement point consumed, increases damage multiplier by 10% instead. Increases the damage multiplier of Continual Release by 30%\n\nIf the target has 2 or more Electric type debuffs, increases CRIT DMG by 30%"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Lively Energy",
        "level": "20",
        "keyName": "Fixed Key 1 - Lively Energy",
        "description": "When Concealment ends, Belka recovers HP equivalent to 30% max HP and 4 Stability",
        "icon": "assets/Belka/Fixed Key 1 - Lively Energy.png"
      },
      {
        "node": "Fixed Key 2 - Offensive of Tears",
        "level": "20",
        "keyName": "Fixed Key 2 - Offensive of Tears",
        "description": "If Belka has Continual Release, she becomes immune to movement displacement effects",
        "icon": "assets/Belka/Fixed Key 2 - Offensive of Tears.png"
      },
      {
        "node": "Fixed Key 3 - Atmosphere Booster",
        "level": "30",
        "keyName": "Fixed Key 3 - Atmosphere Booster",
        "description": "At the start of the turn, if there are enemies within a 5 tile radius of self, gains Movement Up I for 2 turns",
        "icon": "assets/Belka/Fixed Key 3 - Atmosphere Booster.png"
      },
      {
        "node": "Fixed Key 4 - Raised Tail",
        "level": "30",
        "keyName": "Crackling Core",
        "description": "When using this skill to attack a target with Negative Charge, increases ATK by 10%",
        "icon": "assets/Belka/Crackling Core (row 176).png"
      },
      {
        "node": "Fixed Key 5 - Desired Praise",
        "level": "40",
        "keyName": "Fixed Key 5 - Desired Praise",
        "description": "At the end of the action, if there are boss units with Negative Charge, gains Critical Rate Boost I and Damage Up I for 1 turn",
        "icon": "assets/Belka/Fixed Key 5 - Desired Praise.png"
      },
      {
        "node": "Fixed Key 6 - Deciding Motive",
        "level": "40",
        "keyName": "Leaping Arc",
        "description": "Before this skill is used, dispels 2 buffs from the target",
        "icon": "assets/Belka/Leaping Arc (row 178).png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Belka/Affinity Key.png"
      },
      {
        "node": "Common Key - The Will to Fight for Favor",
        "level": "40",
        "keyName": "Common Key - The Will to Fight for Favor",
        "description": "ATK +5% / If movement points are consumed, increases damage dealt by 10%",
        "icon": "assets/Belka/Common Key - The Will to Fight for Favor.png"
      },
      {
        "node": "Expansion Key - Squirrel's Resolve",
        "level": "60",
        "keyName": "Expansion Key - Squirrel's Resolve",
        "description": "Sylvan Vault deals Electric damage instead. Increases the CRIT DMG of this attack by 5% per allied unit with Positive Charge, up to a maximum of 25%\n\nWhen using Crackling Core or Leaping Arc, if Belkas has moved less than 10 times, the movement is treated as 10 tiles",
        "icon": "assets/Belka/Expansion Key - Squirrel's Resolve.png"
      }
    ]
  },
  "Andoris": {
    "class": "Bulwark",
    "stats": {
      "hp": 2288,
      "atk": 591,
      "def": 642
    },
    "stabilityGauge": 12,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Electric"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Practice Shot",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius and deals Physical damage equivalent to 80% ATK to it",
        "upgrades": [],
        "icon": "assets/Andoris/Practice Shot.png"
      },
      {
        "name": "Gentle Offensive",
        "traits": [
          "Active",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "3",
        "effArea": "Target",
        "description": "Selects an empty tile within a 3 tile radius and summons an Auto-Turret. 2 Auto-Turret may exist on the field at the same time. When the number of Auto-Turret exceeds 2, the earliest summoned Auto Turret is automatically destroyed. When Auto Turret is destroyed, increases Confectance Index by 1 point\n\nAfter skill usage, this skill can be used again",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Increases the summon range of Auto-Turret by 3 tiles. Increases the attack range of Auto-Turret by 1 tile\n\nNew effect is added for Crash Mimicry - Increases Electric damage dealt by 30% for self\n\n Added a new passive En Passant to Auto-Turret"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "3 Auto-Turret may exist on the field at the same time. Decreases the Confectance Index cost to activate this skill by 1 point. After skill usage, Andoris gains Extra Command instead of only being able to use Gentle Offensive\n\nNew effect is added - For each Auto-Turret on the field, when an ally deals Electric damage, increases ATK by 10% for that attack"
          }
        ],
        "icon": "assets/Andoris/Gentle Offensive.png"
      },
      {
        "name": "Streamlined Tactics",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "7",
        "effArea": "Target",
        "description": "Selects an enemy target within a 7 tile radius, applies Electro-Charge before attacking for 2 turns, then deals Electric damage equivalent to 110% ATK to it",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "New effect is added for Electro-Charge - when holders of Electro-Charge end their action, applies Electro-Charge to all allies without Electro-Charge within a 3 tile radius for 2 turns. When taking Electric damage, increases damage received by 15%"
          }
        ],
        "icon": "assets/Andoris/Streamlined Tactics.png"
      },
      {
        "name": "Fortification Protocol",
        "traits": [
          "Ultimate",
          "Defense",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Entire Map",
        "description": "Restores 8 Stability and gains Fortified Stance for self for 2 rounds (Duration decreases at the end of the current round). Applies 2 stacks of Shelter and 3 turns of Positive Charge for all allies",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "New effect is added - Fully restores Stability for self, restores HP equivalent to 20% of self's max HP, and cleanses all debuffs from self\n\nWhen Andoris is on the field, applies Movement Up II and Damage Up II for all allies with Positive Charge"
          }
        ],
        "icon": "assets/Andoris/Fortification Protocol.png"
      },
      {
        "name": "Delayed Response",
        "traits": [
          "Passive",
          "Shared",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the battle, gains Self-Diagnosis. This effect can be reactivated again after 3 rounds\n\nWhen allies with Positive Charge receives damage, Andoris shares 45% of the Initial Damage. When using an active attack against an enemy with Negative Charge, Andoris restores HP equivalent to 20% of self's max HP\n\nWhen receiving damage, restores HP equivalent to 5% of self's max HP, increases Confectance Index by 1 point, and applies 1 stack of Blunted Nerves for self and all Auto-Turret on the field. If Andoris is not under the protection of Cover, decreases Confectance Index by 1 point and decreases damage received by 20%",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "New effect is added - Decreases Stability damage received by 1 point. At the start of the battle, increases ATK for self and Auto-Turret by 30% of Andoris' initial DEF. Blunted Nerves is also applied when Auto-Turret receives damage\n\nNew effect is added for Blunted Nerves - Increases DEF by 20% instead, and increases the maximum number of stacks by 3"
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "At the start of the battle, increases the maximum amount of Stability by 6 points\n\nEnhances the effect of Self-Diagnosis - When receiving fatal damage, restores HP equivalent to 60% of max HP, restores Stability to full, and gains Fortified Stance for 2 rounds (Duration decreases at the end of the current round)"
          }
        ],
        "icon": "assets/Andoris/Delayed Response.png"
      },
      {
        "name": "Charged Shot",
        "traits": [
          "Basic Attack",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Electric",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within a 6 tile radius, applies Negative Charge for 2 turns, and deals Electric damage equivalent to 100% ATK to it",
        "upgrades": [],
        "icon": "assets/Andoris/Charged Shot.png"
      },
      {
        "name": "Info Relay",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "At the end of the action, applies Negative Charge on 2 targets within a 6 tile radius for 2 turns",
        "upgrades": [],
        "icon": "assets/Andoris/Info Relay.png"
      },
      {
        "name": "Crash Mimicry",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Auto-Turret cannot be healed or have a Shield applied on it, but is immune to Crowd control effects",
        "upgrades": [],
        "icon": "assets/Andoris/Crash Mimicry.png"
      },
      {
        "name": "En Passant",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "When enemies within attack range receives single target Electric damage from allies' active attacks, Auto-Turret activates Action Support against the enemy first, dealing Electric damage equivalent to 100% ATK and 1 Stability Damage to it, and applies Negative Charge for 2 turns\n\nThis passive is only unlocked after reaching Vertebrae 1",
        "upgrades": [],
        "icon": "assets/Andoris/En Passant.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Gentle Offensive",
        "level": "2",
        "effect": "Increases the summon range of Auto-Turret by 3 tiles. Increases the attack range of Auto-Turret by 1 tile\n\nNew effect is added for Crash Mimicry - Increases Electric damage dealt by 30% for self\n\n Added a new passive En Passant to Auto-Turret"
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Fortification Protocol",
        "level": "2",
        "effect": "New effect is added - Fully restores Stability for self, restores HP equivalent to 20% of self's max HP, and cleanses all debuffs from self\n\nWhen Andoris is on the field, applies Movement Up II and Damage Up II for all allies with Positive Charge"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Delayed Response",
        "level": "2",
        "effect": "New effect is added - Decreases Stability damage received by 1 point. At the start of the battle, increases ATK for self and Auto-Turret by 30% of Andoris' initial DEF. Blunted Nerves is also applied when Auto-Turret receives damage\n\nNew effect is added for Blunted Nerves - Increases DEF by 20% instead, and increases the maximum number of stacks by 3"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Delayed Response",
        "level": "3",
        "effect": "At the start of the battle, increases the maximum amount of Stability by 6 points\n\nEnhances the effect of Self-Diagnosis - When receiving fatal damage, restores HP equivalent to 60% of max HP, restores Stability to full, and gains Fortified Stance (Duration decreases at the end of the current round) for 2 rounds"
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Streamlined Tactics",
        "level": "2",
        "effect": "New effect is added for Electro-Charge - when holders of Electro-Charge end their action, applies Electro-Charge to all allies without Electro-Charge within a 3 tile radius for 2 turns. When taking Electric damage, increases damage received by 15%"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Gentle Offensive",
        "level": "3",
        "effect": "3 Auto-Turret may exist on the field at the same time. Decreases the Confectance Index cost to activate this skill by 1 point. After skill usage, Andoris gains Extra Command instead of only being able to use Gentle Offensive\n\nNew effect is added - For each Auto-Turret on the field, when an ally deals Electric damage, increases ATK by 10% for that attack"
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Careful Listening",
        "level": "20",
        "keyName": "Fixed Key 1 - Careful Listening",
        "description": "At the start of the battle, increases Confectance Index by 3 points",
        "icon": "assets/Andoris/Fixed Key 1 - Careful Listening.png"
      },
      {
        "node": "Fixed Key 2 - Sluggish Circuit",
        "level": "20",
        "keyName": "Fixed Key 2 - Sluggish Circuit",
        "description": "When dealing Electric damage, if the target is in Stability Break and has Electro-Charge, additionally deals fixed damage equivalent to 10% ATK to it",
        "icon": "assets/Andoris/Fixed Key 2 - Sluggish Circuit.png"
      },
      {
        "node": "Fixed Key 3 - Slow and Steady",
        "level": "30",
        "keyName": "Fixed Key 3 - Slow and Steady",
        "description": "When Andoris applies Positive Charge for allies, cleanses 2 debuffs from them and all Auto-Turret",
        "icon": "assets/Andoris/Fixed Key 3 - Slow and Steady.png"
      },
      {
        "node": "Fixed Key 4 - Tuned Connection",
        "level": "30",
        "keyName": "Fixed Key 4 - Tuned Connection",
        "description": "When Andoris is on the field, if an allied unit with Positive Charge ends their action within a 3 tile radius of another ally with Positive Charge, they gain 1 stack of Shelter",
        "icon": "assets/Andoris/Fixed Key 4 - Tuned Connection.png"
      },
      {
        "node": "Fixed Key 5 - Shared Intelligence",
        "level": "40",
        "keyName": "Fixed Key 5 - Shared Intelligence",
        "description": "At the start of the battle, applies Positive Charge for all allies for 3 turns",
        "icon": "assets/Andoris/Fixed Key 5 - Shared Intelligence.png"
      },
      {
        "node": "Fixed Key 6 - Advanced Scouting",
        "level": "40",
        "keyName": "Fixed Key 6 - Advanced Scouting",
        "description": "At the start of the battle, applies Electro-Charge on the enemy with the highest HP for 2 turns",
        "icon": "assets/Andoris/Fixed Key 6 - Advanced Scouting.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Andoris/Affinity Key.png"
      },
      {
        "node": "Common Key - Inductive Field",
        "level": "40",
        "keyName": "Common Key - Inductive Field",
        "description": "DEF +5% / For each Electric type debuff present on the field, increases damage dealt by 5%, up to a maximum of 10%, which lasts till the end of the round",
        "icon": "assets/Andoris/Common Key - Inductive Field.png"
      },
      {
        "node": "Expansion Key - Unfailing Vigil",
        "level": "60",
        "keyName": "Expansion Key - Unfailing Vigil",
        "description": "At the end of an Auto-Turret action, if it did not dealt any damage, increases Confectance Index for Andoris by 2 points. Before Auto-Turret attacks a target with Negative Charge, increases ATK for self by 50%\n\nWhen allies with Positive Charge receives damage, Andoris shares 65% of the Intial Damage. After Andoris receives damage for an ally, for each stack of Blunted Nerves held by all allies, Andoris restores HP equivalent to 0.5% max HP\n\nAt the end of Andoris' action, applies Positive Charge for the closest ally for 3 turns",
        "icon": "assets/Andoris/Expansion Key - Unfailing Vigil.png"
      }
    ]
  },
  "Springfield": {
    "class": "Support",
    "stats": {
      "hp": 1909,
      "atk": 696,
      "def": 585
    },
    "stabilityGauge": 10,
    "movementSpeed": 6,
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
        "name": "Gentle Approach",
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
        "description": "Selects an enemy target within a 9 tiles and deals Physical damage equal to 80% of attack to it.",
        "upgrades": [],
        "icon": "assets/Springfield/Gentle Approach.png"
      },
      {
        "name": "Intel Manipulation",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 4,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within 9 tiles and applies False Intelligence to it for 2 turns. Deals Hydro damage equal to 130% of attack to the target and applies Congestion for 1 turn. Springfield gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage dealt is increased to 150% of attack. When the enemy target enter Stability break with False Intelligence on self, Hydro damage taken is increased to 20%. Congestion is changed to Cold Snap for 1 turn."
          }
        ],
        "icon": "assets/Springfield/Intel Manipulation.png"
      },
      {
        "name": "Opportune Assistance",
        "traits": [
          "Active",
          "Healing",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an allied unit within 9 tiles. Recovers HP equal to 100% of attack and 3 points of Stability, and applies Overflowing Care for 2 rounds (Duration decreases at the end of the current round) to the selected unit. Springfield gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "HP recovery is increased to 130% of attack. The effect of Overflowing Care is increased, HP recovery is increased to 15% of attack. The maximum amount of converted enhancement to Hydro damage is increased to 70%. In addition, applies 6 stacks of Shared Telepathy to the selected unit."
          }
        ],
        "icon": "assets/Springfield/Opportune Assistance.png"
      },
      {
        "name": "Path of Protection",
        "traits": [
          "Ultimate",
          "AoE",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 3,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within 9 tiles and summons Taryz to follow it for 2 rounds (Duration decreases at the end of the current round). Applies Damp and False Intelligence to the selected enemy target and all enemy units within 3 tiles of the target for 2 turns, and deals AoE Hydro damage equal to 80% of attack.\n\nApplies Deep-Rooted Bonds and Overflowing Care to all allied units for 2 rounds (Duration decreases at the end of the current round). Recovers HP equal to 100% of attack and 2 points of Stability for all allied units, cleanses 1 debuff from them, and removes Taunt and Fear from all allied units.\n\nWhen the target that Taryz is following dies, Taryz switches to following the enemy unit with the current highest HP. Springfield gains 2 points of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Confectance Index gain increases by 1 point. HP recovery is increased to 120% of attack, Stability recovery is increased by 4 points, 1 additional debuff is cleansed. Additionally, removes Stun and Infatuated."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Increases the effect range by 1 tile. New effect is added for Buried Bonds - Decreases damage received by 15% and increases duration by 1 round\n\nIncreases the duration of Taryz by 1 round. When the target that Taryz is following dies, deals fixed damage equivalent to 40% of Springfield's ATK to all enemies within a 4 tile radius of the target"
          },
          {
            "type": "fixedKey",
            "number": 1,
            "label": "Fixed Key 1 - Coalesced Core",
            "effect": "When using the Ultimate skill Path of Protection, it pulls all targets 3 tiles toward the centre of the effect."
          }
        ],
        "icon": "assets/Springfield/Path of Protection.png"
      },
      {
        "name": "Eagle's Vigilance",
        "traits": [
          "Passive",
          "Buff",
          "Counterattack"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the end of Springfield's action, if Confectance Index is maxed out, expends all Confectance Index and gains Extra Action.\n\nAt the start of the turn, if Springfield's HP is higher than 80%, gains Insight for 2 turns. If the target that Taryz is following deals damage to an allied unit, Taryz performs Counterattack on it, dealing Hydro damage equal to 20% of Springfield's max HP and 1 point of Stability damage and healing the allied unit for 20% of Springfield's max HP. Can be triggered up to 2 times per turn.\n\nIf Taryz is on the field, Springfield recovers HP equal to 20% of max HP at the end of the action.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "New effect is added for Taryz: Increases Hydro damage received for the target which Taryz is following and all enemy units within 3 tiles of the target is increased by 10%.\n\nWhen Taryz is on the field, Hydro damage dealt by all allied units' out-of-turn attacks is increased by 40%.\n\nSupport effect added: When an allied unit performs an active attack to deal Hydro damage to the target Taryz is following, Taryz performs Action Support, dealing Hydro damage equal to 20% of Springfield's max HP and 1 point of Stability damage and healing that allied unit for 20% of Springfield's max HP. Can be triggered up to 2 times per turn."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Taryz is upgraded to Assault Taryz. all multipliers for attacks by Assault Taryz are doubled. Hydro damage multipliers are increased by 20%, Stability damage is increased by 1 point, HP recovery multiplier is increased by 20% and the effect can be triggered 2 more times per turn. Before attacking, Assault Taryz applies Vulnerability Analysis to the enemy target for 2 turns."
          }
        ],
        "icon": "assets/Springfield/Eagle's Vigilance.png"
      },
      {
        "name": "Peck",
        "traits": [
          "Passive",
          "Targeted"
        ],
        "attribute": "Hydro",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Entire Map",
        "effArea": "Target",
        "description": "After Springfield's action ends, Elsin deals Hydro damage equal to 50% of Max HP to the nearest enemy target; after an enemy unit's action ends Elsin deals the same amount of damage to it. If the target is followed by Taryz, the damage multiplier is increased by 30%. This attack is considered a basic attack.",
        "upgrades": [],
        "icon": "assets/Springfield/Peck.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Opportune Assistance",
        "level": "2",
        "effect": "HP recovery is increased to 130% of attack. The effect of Overflowing Care is increased, HP recovery is increased to 15% of attack. The maximum amount of converted enhancement to Hydro damage is increased to 70%. In addition, applies 6 stacks of Shared Telepathy to the selected unit."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Path of Protection",
        "level": "2",
        "effect": "Confectance Index gain increases by 1 point. HP recovery is increased to 120% of attack, Stability recovery is increased by 4 points, 1 additional debuff is cleansed. Additionally, removes Stun and Infatuated."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Eagle's Vigilance",
        "level": "2",
        "effect": "New effect is added for Taryz: Increases Hydro damage received for the target which Taryz is following and all enemy units within 3 tiles of the target is increased by 10%.\n\nWhen Taryz is on the field, Hydro damage dealt by all allied units' out-of-turn attacks is increased by 40%.\n\nSupport effect added: When an allied unit performs an active attack to deal Hydro damage to the target Taryz is following, Taryz performs Action Support, dealing Hydro damage equal to 20% of Springfield's max HP and 1 point of Stability damage and healing that allied unit for 20% of Springfield's max HP. Can be triggered up to 2 times per turn."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Intel Manipulation",
        "level": "2",
        "effect": "Damage dealt is increased to 150% of attack. When the enemy target enter Stability break with False Intelligence on self, Hydro damage taken is increased to 20%. Congestion is changed to Cold Snap for 1 turn."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Path of Protection",
        "level": "3",
        "effect": "Effect range increases by 1 tile. Deep-Rooted Bonds gains new effects: Damage is reduced by 15% and duration is increased by 1 round.\n\nIncreases the duration of Taryz by 1 round. When the target that Taryz is following dies, deals fixed damage equivalent to 40% of Springfield's ATK to all enemies within a 4 tile radius of the target"
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Eagle's Vigilance",
        "level": "3",
        "effect": "Taryz is upgraded to Assault Taryz. all multipliers for attacks by Assault Taryz are doubled. Hydro damage multipliers are increased by 20%, Stability damage is increased by 1 point, HP recovery multiplier is increased by 20% and the effect can be triggered 2 more times per turn. Before attacking, Assault Taryz applies Vulnerability Analysis to the enemy target for 2 turns."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Coalesced Core",
        "level": "20",
        "keyName": "Fixed Key 1 - Coalesced Core",
        "description": "When using the Ultimate skill Path of Protection, it pulls all targets 3 tiles toward the centre of the effect.",
        "icon": "assets/Springfield/Fixed Key 1 - Coalesced Core.png"
      },
      {
        "node": "Fixed Key 2 - Intel Acquisition",
        "level": "20",
        "keyName": "Fixed Key 2 - Intel Acquisition",
        "description": "Before making an active attack, Springfield dispels 1 buff from the target.",
        "icon": "assets/Springfield/Fixed Key 2 - Intel Acquisition.png"
      },
      {
        "node": "Fixed Key 3 - Airborne Link",
        "level": "30",
        "keyName": "Fixed Key 3 - Airborne Link",
        "description": "When Taryz is on the field, all allied unit's defense is increased by 10%.",
        "icon": "assets/Springfield/Fixed Key 3 - Airborne Link.png"
      },
      {
        "node": "Fixed Key 4 - Mind Reader",
        "level": "30",
        "keyName": "Fixed Key 4 - Mind Reader",
        "description": "If the target's HP is lower than 80%, healing effects are increased by 15%.",
        "icon": "assets/Springfield/Fixed Key 4 - Mind Reader.png"
      },
      {
        "node": "Fixed Key 5 - Behind Her Smile",
        "level": "40",
        "keyName": "Fixed Key 5 - Behind Her Smile",
        "description": "Before making an active attack, Springfield applies Hydro weakness for 1 turn.",
        "icon": "assets/Springfield/Fixed Key 5 - Behind Her Smile.png"
      },
      {
        "node": "Fixed Key 6 - Gentle Ministrations",
        "level": "40",
        "keyName": "Fixed Key 6 - Gentle Ministrations",
        "description": "When healing a target in Stability Break, recovers an additional 2 points of stability for the target.",
        "icon": "assets/Springfield/Fixed Key 6 - Gentle Ministrations.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, DEF +3%, HP +3%",
        "icon": "assets/Springfield/Affinity Key.png"
      },
      {
        "node": "Common Key - Meticulous Attention",
        "level": "40",
        "keyName": "Common Key - Meticulous Attention",
        "description": "HP +5.0% / At the start of the turn, if Stability is not full, gains Continuous Stability Regen II for 1 turn.",
        "icon": "assets/Springfield/Common Key - Meticulous Attention.png"
      },
      {
        "node": "Expansion Key - Vigilant Bond",
        "level": "60",
        "keyName": "Expansion Key - Vigilant Bond",
        "description": "The effect of the Opportune assistance applies to all allied units. After using the Guardian’s Path, summons Elsin around the target. If Elsin is already present, damage dealt by allied Entity Summons is increased by 50%. Each time other allied Entity Summon or Taryz deal Hydro Damage, applies 1 stack of Saturation to the target. When Elsin's Passive skill Peck is triggered, it consumes Saturation; for each stack consumed, the damage multiplier of Peck is increased by 5%.",
        "icon": "assets/Springfield/Expansion Key - Vigilant Bond.png"
      }
    ]
  },
  "Faye": {
    "class": "Vanguard",
    "stats": {
      "hp": 1609,
      "atk": 731,
      "def": 528
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Light Ammo",
      "Melee"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Practice Shot",
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
        "icon": "assets/Faye/Practice Shot.png"
      },
      {
        "name": "Ruinous Whirl",
        "traits": [
          "Active",
          "AoE",
          "Debuff"
        ],
        "attribute": "Melee",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 1,
        "range": "Self",
        "effArea": "3",
        "description": "Expends all Confectance Index. For each point of Confectance Index expended, Faye applies 1 stack of Rend to all enemy units within 3 tiles, pulls them 2 tiles towards self, and deals AoE Physical damage equal to 80% of attack, while also applying Movement Denied for 1 turn.\n\nFaye gains 8 tiles of Additional Movement and Bypass for 1 turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage multiplier is increased by 20%. Duration of Movement Denied and Bypass is increased by 1 turn.\n\nAfter this skill is used, Faye cleanses all Defense and Movement type debuffs on self."
          },
          {
            "type": "fixedKey",
            "number": 2,
            "label": "Fixed Key 2 - All-In Slash",
            "effect": "When the active skill Ruinous Whirl only hits one enemy unit, damage dealt is increased by 20%."
          }
        ],
        "icon": "assets/Faye/Ruinous Whirl.png"
      },
      {
        "name": "Fissioned Firelight",
        "traits": [
          "Active",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 4,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Faye gains 2 points of Confectance Index. Selects an enemy target within 6 tiles, applies 2 stacks of Rend to it, and deals Physical damage equal to 120% of attack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Damage multiplier is increased by 20%. If the enemy target holds 4 or more stacks of Rend after Faye uses this skill, Faye additionally applies a number of stacks of Gash equal to the number of stacks of Rend to it."
          }
        ],
        "icon": "assets/Faye/Fissioned Firelight.png"
      },
      {
        "name": "No Survivors",
        "traits": [
          "Ultimate",
          "Targeted",
          "Debuff"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects an enemy target within 6 tiles. Applies a number of stacks of Gash equal to the stacks of Rend to all enemies holding Rend within 6 tiles, and deals Physical damage equal to 160% of attack.\n\nIf the enemy target holds 6 or more stacks of Rend, expends 6 stacks of Rend from the target to increase the damage that the target takes from this attack by 120%.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "The effect of applying Gash to all enemies around Faye with Rend is changed as follow: Applies 4 stacks of Gash to all enemy units on the field. For enemy units with stacks of Rend, applies an equal number of stacks of Gash to them.\n\nAt the end of Faye's action, triggers all stacks of Gash, but does not expend the stacks of Gash."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "The effects applied when the target holds 6 or more stacks of Rend is changed as follows: Expends 6 stacks of Rend. For each stack of Rend that the enemy target holds, damage taken from this attack is increased by 20%, to a maximum increase of 160%. Each stack of Rend increases Faye's critical rate for this attack by 5% and critical damage for this attack by 2%."
          }
        ],
        "icon": "assets/Faye/No Survivors.png"
      },
      {
        "name": "Tomahawk Combo",
        "traits": [
          "Passive",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "When attacking, Faye ignores an amount of the target's defense equal to (2% x number of Rend stacks) and recovers HP equal to 10% of max HP + (2% x the number of Rend stacks).\n\nAt the end of an enemy unit's action, if it is within 6 tiles, Faye throws a tomahawk at it, gains 1 point of Confectance Index, applies 1 stack of Rend to it, and deals Physical damage equal to 80% of attack and 2 points of Stability damage. If the enemy is within 3 tiles, Faye performs an axe whirl instead; gains 1 point of Confectance Index, applies 2 stacks of Rend to all enemy units within 3 tiles, and deals AoE Physical damage equal to 60% of attack and 1 point of Stability damage. This effect can trigger up to 2 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "the amount of defense ignored by per stack of Rend is increased by 2%.\n\nAt the end of an enemy unit's action, if it holds 2 or more stacks of Rend, Faye applies 2 stacks of Rend to the nearest enemy unit."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "At the end of Faye's action, performs an axe whirl and applies Movement Denied to all enemy units within the area for 1 turn. Damage dealt by this attack is increased by 30%."
          }
        ],
        "icon": "assets/Faye/Tomahawk Combo.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Tomahawk Combo",
        "level": "2",
        "effect": "the amount of defense ignored by per stack of Rend is increased by 2%.\n\nAt the end of an enemy unit's action, if it holds 2 or more stacks of Rend, Faye applies 2 stacks of Rend to the nearest enemy unit."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Fissioned Firelight",
        "level": "2",
        "effect": "Damage multiplier is increased by 20%. If the enemy target holds 4 or more stacks of Rend after Faye uses this skill, Faye additionally applies a number of stacks of Gash equal to the number of stacks of Rend to it."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Tomahawk Combo",
        "level": "3",
        "effect": "At the end of Faye's action, performs an axe whirl and applies Movement Denied to all enemy units within the area for 1 turn. Damage dealt by this attack is increased by 30%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "No Survivors",
        "level": "2",
        "effect": "The effect of applying Gash to all enemies around Faye with Rend is changed as follow: Applies 4 stacks of Gash to all enemy units on the field. For enemy units with stacks of Rend, applies an equal number of stacks of Gash to them.\n\nAt the end of Faye's action, triggers all stacks of Gash, but does not expend the stacks of Gash."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Ruinous Whirl",
        "level": "2",
        "effect": "Damage multiplier is increased by 20%. Duration of Movement Denied and Bypass is increased by 1 turn.\n\nAfter this skill is used, Faye cleanses all Defense and Movement type debuffs on self."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "No Survivors",
        "level": "3",
        "effect": "The effects applied when the target holds 6 or more stacks of Rend is changed as follows: Expends 6 stacks of Rend. For each stack of Rend that the enemy target holds, damage taken from this attack is increased by 20%, to a maximum increase of 160%. Each stack of Rend increases Faye's critical rate for this attack by 5% and critical damage for this attack by 2%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Tracking by Scent",
        "level": "20",
        "keyName": "Fixed Key 1 - Tracking by Scent",
        "description": "For every unit on the field with Rend increases Faye's mobility by 1 tile, to a maximum increase of 3 tiles.",
        "icon": "assets/Faye/Fixed Key 1 - Tracking by Scent.png"
      },
      {
        "node": "Fixed Key 2 - All-In Slash",
        "level": "20",
        "keyName": "Fixed Key 2 - All-In Slash",
        "description": "When the active skill Ruinous Whirl only hits one enemy unit, damage dealt is increased by 20%.",
        "icon": "assets/Faye/Fixed Key 2 - All-In Slash.png"
      },
      {
        "node": "Fixed Key 3 - Rescue Response Supplies",
        "level": "30",
        "keyName": "Fixed Key 3 - Rescue Response Supplies",
        "description": "At the start of the battle, gains 3 points of Confectance Index.",
        "icon": "assets/Faye/Fixed Key 3 - Rescue Response Supplies.png"
      },
      {
        "node": "Fixed Key 4 - Emergency Plans",
        "level": "30",
        "keyName": "Fixed Key 4 - Emergency Plans",
        "description": "When Faye's HP is lower than 50%, healing effect received is increased by 30%.",
        "icon": "assets/Faye/Fixed Key 4 - Emergency Plans.png"
      },
      {
        "node": "Fixed Key 5 - Crisis Protection",
        "level": "40",
        "keyName": "Fixed Key 5 - Crisis Protection",
        "description": "At the end of Faye's action, if there are enemy units with Rend within 2 tiles, Faye gains AoE Defense I for 1 turn.",
        "icon": "assets/Faye/Fixed Key 5 - Crisis Protection.png"
      },
      {
        "node": "Fixed Key 6 - In the Fracas",
        "level": "40",
        "keyName": "Fixed Key 6 - In the Fracas",
        "description": "When an enemy unit with Gash dies, Faye's attack is increased by 4%, to a maximum increase of 20%.",
        "icon": "assets/Faye/Fixed Key 6 - In the Fracas.png"
      },
      {
        "node": "Affinity Key",
        "level": "-",
        "keyName": "Affinity Key",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Faye/Affinity Key.png"
      },
      {
        "node": "Common Key - Holmgang",
        "level": "40",
        "keyName": "Common Key - Holmgang",
        "description": "CRIT +5.0% / Physical damage taken by enemy units within 3 tiles is increased by 5%.",
        "icon": "assets/Faye/Common Key - Holmgang.png"
      },
      {
        "node": "Expansion Key",
        "level": "60",
        "keyName": "Expansion Key",
        "description": "When dealing damage towards enemies with Gash, ignores 50% of the target's DEF and increases ATK by 15%\n\nNo Survivors: After skill usage, applies 2 stacks of Rend on the target\n\nAfter using Flying Axe or Revolving Axe, applies Movement Denied for 1 turn",
        "icon": "assets/Faye/Expansion Key.png"
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
        "icon": "assets/Peri/Final Bid (row 89).png"
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
        "icon": "assets/Peri/Final Bid (row 171).png"
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
        "effArea": "Target",
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
        "icon": "assets/Yoohee/Improv (row 39).png"
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
        "icon": "assets/Yoohee/Soul of Dance (row 74).png"
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
        "icon": "assets/Yoohee/Improv (row 228).png"
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
        "icon": "assets/Yoohee/Improv (row 230).png"
      },
      {
        "node": "Fixed Key 4 - Infectious Emotions",
        "level": "30",
        "keyName": "Soul of Dance",
        "description": "After this skill applies Stun on the enemy, when Stun is removed, applies Movement Denied for 1 turn",
        "icon": "assets/Yoohee/Soul of Dance (row 231).png"
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
        "icon": "assets/Nikketa/K9 Deployment (row 39).png"
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
        "icon": "assets/Nikketa/Judgement Strike (row 74).png"
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
        "icon": "assets/Nikketa/Judgement Strike (row 232).png"
      },
      {
        "node": "Fixed Key 4 - Just Desserts",
        "level": "30",
        "keyName": "K9 Deployment",
        "description": "After skill usage, generates Tideaway in the effective area for 2 turns",
        "icon": "assets/Nikketa/K9 Deployment (row 233).png"
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
        "icon": "assets/Robella/Ultra Shot (row 19).png"
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
        "icon": "assets/Robella/Ultra Shot (row 170).png"
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
        "icon": "assets/Lainie/Simulated Partner (row 99).png"
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
        "icon": "assets/Lainie/Simulated Partner (row 328).png"
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
      },
      {
        "node": "Expansion Key tier 2",
        "level": "60",
        "keyName": "Expansion Key tier 2",
        "description": "At the end of the Simulacrum's turn, pull all enemy units on the field toward itself by 1 tile and deals 2 points of stability damage.\r\nAfter Lainie or the Simulacrum actively attacks, if the enemy target has 3 stacks of Parapluie's Penetration, applies Mirror Cache to it. If the enemy target has 6 stacks of Parapluie's Penetration, the final damage accumulated by Mirror Cache is increased to 25% and the damage dealt by Lainie or the Simulacrum's next active attack this turn is increased by 30% and critical damage increased by 30%.\r\nBefore Lainie or the Simulacrum active attacks, if the enemy target has Mirror Cache, trigger that effect, and the damage multiplier of active attacks are permanently increased by 15%, up to a maximum of 90%.",
        "icon": "assets/Lainie/Expansion Key tier 2.png"
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
        "icon": "assets/Florence/Special Care (row 39).png"
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
        "icon": "assets/Florence/Masochistic Hallucination (row 94).png"
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
        "icon": "assets/Florence/Masochistic Hallucination (row 234).png"
      },
      {
        "node": "Fixed Key 6 - Sweet Temptation",
        "level": "40",
        "keyName": "Special Care",
        "description": "This skill will no longer restore HP and cleanse debuffs, but instead deals AoE Physical damage equivalent to 30% ATK to all units (excluding self) within range",
        "icon": "assets/Florence/Special Care (row 235).png"
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
        "description": "HP +5% / Increases ATK of holder's Entity Summons by 7%",
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
        "icon": "assets/Lind/Overwhelming Burst (row 69).png"
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
        "icon": "assets/Lind/Glucose Overload (row 104).png"
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
        "icon": "assets/Lind/Assault Spray_Overwhelming Burst.png"
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
        "icon": "assets/Lind/Overwhelming Burst (row 186).png"
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
        "icon": "assets/Lind/Glucose Overload (row 188).png"
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
        "icon": "assets/Alva/Nix Requiem (row 94).png"
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
        "icon": "assets/Alva/Nix Requiem (row 172).png"
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
        "icon": "assets/Voymastina/Howl from the Firmament (row 39).png"
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
        "icon": "assets/Voymastina/Pile Bunker (row 104).png"
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
        "icon": "assets/Voymastina/Howl from the Firmament (row 183).png"
      },
      {
        "node": "Fixed Key 2",
        "level": "20",
        "keyName": "Pile Bunker",
        "description": "After triggering the passive effect of this skill, gains Movement Up II for 2 turns",
        "icon": "assets/Voymastina/Pile Bunker (row 184).png"
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
        "icon": "assets/Voymastina/Howl from the Firmament (row 186).png"
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
        "icon": "assets/Voymastina/Pile Bunker (row 188).png"
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
      },
      {
        "node": "Expansion Key - Tin Soldiers Assemble",
        "level": "60",
        "keyName": "Expansion Key - Tin Soldiers Assemble",
        "description": "After applying Tin Soldiers, if there 4 or more friendly Burn Dolls on the field, increase Rank of Tin Soldiers by 1 level.\nOnce the Rank reaches level 3, at the start of each Round, Lewis consumes all Merit from dolls with Tin Soldiers assigned to. For each 1 Merit consumed, Lewis' Burn damage dealt this Round is increased by 6% and Critical Damage is increased by 6%, up to a maximum of 48%.",
        "icon": "assets/Lewis/Expansion Key - Tin Soldiers Assemble.png"
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
        "description": "Helen is immune to the following effects: healing reduction, healing prevention or effects that convert healing into damage.\nAt the start of battle, increases Helen's defense and Max HP by 30%.\nAt the start of each turn, Helen gains 2 points of Confectance Index, restores 25% of HP, and cleanse all debuffs from self.\nFor every instance of damage taken, Helen gains 1 stack of Overedge.\nWhen Helen has Overedge, the damage multiplier of her basic attacks is increased to 180%.\nBefore Helen performs a basic attack, her attack is increased by 15% of her defence.",
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
      },
      {
        "node": "Expansion Key - Double Soul Resonance Sonata",
        "level": "60",
        "keyName": "Expansion Key - Double Soul Resonance Sonata",
        "description": "While posessing Blade Resonance, damage dealt is increased by 30%. After an active attack, deals Melee Corrosion Damage equal to 100% of ATK 1 time to the nearest enemy target withing 8 tile radius. After dealing out-of-turn damage, inflicts 3 stacks of Aichmophobia on the target for 2 rounds.",
        "icon": "assets/Phaetusa/Expansion Key - Double Soul Resonance Sonata.png"
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
      },
      {
        "node": "Expansion Key - Dance of the Fire Sakura",
        "level": "60",
        "keyName": "Expansion Key - Dance of the Fire Sakura",
        "description": "When acquiting Extra Command by using the active skill Omnidirectional Shift, can move 6 tiles.\nThe damage miltiplier of Sakura Mark is increased by 15%. For every 3 times of effect Sakura Mark is triggered (excluding triggers by the Ultimate Skill Domain of Bad Luck), gains 1 Confectance Index, up to a maximum of 4 per turn.\nEach time the effect of Thermal Conduction is triggered, damage dealt by self permanently increases by 15% and Critical Damage permanently increases by 15% up to a maximum increase of 75%.",
        "icon": "assets/Sakura/Expansion Key - Dance of the Fire Sakura.png"
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
        "cooldown": 0,
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
        "description": "After using the active skill Wide area Boost ♂Wide Muscle Boost♂ on ally holding the Alpha Process, Harpsy's critical strike rate is increased by 20% for 1 round.",
        "icon": "assets/Harpsy/Fixed Key 5 - Courage Unleashed.png"
      },
      {
        "node": "Fixed Key 6 - \r\nDistance Listen-In",
        "level": "40",
        "keyName": "Fixed Key 6 - \r\nDistance Listen-In",
        "description": "Increases the range of active skills and basic attacks by 2 tiles.",
        "icon": "assets/Harpsy/Fixed Key 6 -  Distance Listen-In.png"
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
      },
      {
        "node": "Expansion Key - Lytic Invasion",
        "level": "60",
        "keyName": "Expansion Key - Lytic Invasion",
        "description": "After using the Ultimate Skill Cyber Punch, applies Retrograde to the target for 1 turn. After an active skill attack, if the target has Retrograde, applies Movement Down III for 1 turn.\nAfter an active attack, applies 3 stacks of Antivirus Program.\nWhen self deals damage, for each friendly unit with Priority Process, self's Corrosion damage dealt increases by 5%.",
        "icon": "assets/Harpsy/Expansion Key - Lytic Invasion.png"
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
        "description": "Selects an open tile within a 6 tile radius and summons Cutie Pie on it. After skill usage, Basti can use active skills Landmine Gal, Bad Influence or her ultimate skill Sugar-Coated Trap. This skill can be used up to 2 times per turn.\n\nCutie Pie: A summoned unit that inherits Basti’s base attributes. If enemy targets are present within a 3-tile radius upon summoning, or if enemy targets spawn, end their action, or are passively displaced into the area, Cutie Pie self-destructs within the area, dealing AoE Corrosion damage equal to 100% ATK and 2 points of Stability damage, and creating a Toxic Mist tiles within the area for 2 turns. Additionally, applies Toxic Inundation and Stun to all enemy targets in the area for 2 turns, and restores HP equal to 80% ATK and 1 point of Stability Index to Basti. A maximum of 2 such summons can exist on the field at the same time.",
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
  "Liushih": {
    "class": "Sentinel",
    "stats": {
      "hp": 2028,
      "atk": 195,
      "def": 502
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Heavy Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Freeze"
    ],
    "skills": [
      {
        "name": "Line Breaker",
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
        "description": "Selects an enemy target within a 9 tile radius and deals Hydro damage equivalent to 90% ATK to it. This attack is considered a Loaded Attack.",
        "upgrades": [],
        "icon": "assets/Liushih/Line Breaker.png"
      },
      {
        "name": "All or Nothing",
        "traits": [
          "Active",
          "Targeted",
          "Buff"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius and deals Hydro damage equivalent to 90% of ATK. Consumes all points of Confectance Index. Based on the number of points consumed, Liushih and Pegasus gain number of Precision stacks. After skill usage, Liushih gains Extra Action. This attack is considered a Loaded Attack. This skill can be only used while Pegasus is in the Coordinated Combat state.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Damage multiplier increased to 120%.\nImprove the Precision effect: Increases the damage multiplier of basic attacks by 20% per stack."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Double the number of Precision stacks obtained."
          }
        ],
        "icon": "assets/Liushih/All or Nothing.png"
      },
      {
        "name": "Strategic Masterstroke",
        "traits": [
          "Active"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within a cross-shaped area of 4 to 8 tiles, landing on the selected tile and relocates Pegasus to a position near her. If Pegasus is in the Coordinated Combat or Standby state, remove that state. After skill usage, Liushih gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Creates Tideway tiles within the path for 2 turns. Pegasus no longer withdrew from the Coordinated Combat state."
          }
        ],
        "icon": "assets/Liushih/Strategic Masterstroke.png"
      },
      {
        "name": "Leading the Charge",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects an enemy target within a 9 tile radius and deals Hydro damage equivalent to 90% of ATK. Pegasus gains the Coordinated Combat state and exits Standby state. This attack is considered a Loaded Attack.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Damage multiplier increased to 120%.\nCoordinated Combat gains new effect: Liushih and Pegasus critical damage increased by 30%."
          }
        ],
        "icon": "assets/Liushih/Leading the Charge.png"
      },
      {
        "name": "We Fight as One",
        "traits": [
          "Passive",
          "Summon",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, summons Pegasus close to Liushih.\nFor every 60 points of Liushih's initial attack, increase the basic attack damage multiplier of both herself and Pegasus by 5% up to 50%.\nBefore using the active attack All or Nothing or the Ultimate Leading the Charge, inflicts Lockdown to the target for 2 turns.\nAfter Pegasus uses Point-Defense Autocannon, Liushih gains 1 point of Confectance Index.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "In the end of Liushih action Pegasus fires 1 Point-Defense Autocannon at the nearest enemy target within range."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "For every 1 point of Confectance Index obtained in the current round, Liushih and all friendly entity summons gain 1 stack of Sharpness before using the active skill All or Nothing in the next round. Lasting 1 round."
          }
        ],
        "icon": "assets/Liushih/We Fight as One.png"
      },
      {
        "name": "Point-Defense Autocannon",
        "traits": [
          "Passive",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Deals Hydro damage equivalent to 110% of ATK. This is considered a Loaded Attack and a basic attack.",
        "upgrades": [],
        "icon": "assets/Liushih/Point-Defense Autocannon.png"
      },
      {
        "name": "Safety Protocol",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Unable to move. When taking lethal damage, Pegasus goes into the Standby state. If it is in the Coordinated Combat state, it is removed.",
        "upgrades": [],
        "icon": "assets/Liushih/Safety Protocol.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "We Fight as One",
        "level": "2",
        "effect": "In the end of Liushih action Pegasus fires 1 Point-Defense Autocannon at the nearest enemy target within range."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Strategic Masterstroke",
        "level": "2",
        "effect": "Creates Tideway tiles within the path for 2 turns. Pegasus no longer withdrew from the Coordinated Combat state."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "All or Nothing",
        "level": "2",
        "effect": "Damage multiplier increased to 120%.\nImprove the Precision effect: Increases the damage multiplier of basic attacks by 20% per stack."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Leading the Charge",
        "level": "2",
        "effect": "Damage multiplier increased to 120%.\nCoordinated Combat gains new effect: Liushih and Pegasus critical damage increased by 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "We Fight as One",
        "level": "3",
        "effect": "For every 1 point of Confectance Index obtained in the current round, before using the active skill All or Nothing in the next round, you and all friendly entity summons gain 1 stack of Sharpness, lasting 1 round."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "All or Nothing",
        "level": "3",
        "effect": "Double the number of Precision stacks obtained."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Perfect Synergy",
        "level": "20",
        "keyName": "Fixed Key 1 - Perfect Synergy",
        "description": "When Pegasus is in the Coordinated Combat state damage dealt by Liushih and Pegasus is increased by 20%.",
        "icon": "assets/Liushih/Fixed Key 1 - Perfect Synergy.png"
      },
      {
        "node": "Fixed Key 2 - Deadeye",
        "level": "20",
        "keyName": "Fixed Key 2 - Deadeye",
        "description": "Each stack of Precision additionally increases Critical Rate by 5%.",
        "icon": "assets/Liushih/Fixed Key 2 - Deadeye.png"
      },
      {
        "node": "Fixed Key 3 - No Expense Spared",
        "level": "30",
        "keyName": "Fixed Key 3 - No Expense Spared",
        "description": "Before Pegasus uses Point-Defense Autocannon, dispel 1 buff from the target",
        "icon": "assets/Liushih/Fixed Key 3 - No Expense Spared.png"
      },
      {
        "node": "Fixed Key 4 - Unbreakable Will",
        "level": "30",
        "keyName": "Fixed Key 4 - Unbreakable Will",
        "description": "Pegasus is immune to control effects",
        "icon": "assets/Liushih/Fixed Key 4 - Unbreakable Will.png"
      },
      {
        "node": "Fixed Key 5 - Capital Expenditure",
        "level": "40",
        "keyName": "Fixed Key 5 - Capital Expenditure",
        "description": "After usaging Strategic Masterstroke Liushih gains Additional Movement.",
        "icon": "assets/Liushih/Fixed Key 5 - Capital Expenditure.png"
      },
      {
        "node": "Fixed Key 6 - Rallying Cry",
        "level": "40",
        "keyName": "Fixed Key 6 - Rallying Cry",
        "description": "After a friendly entity summon other than Pegasus attacks, Liushih gains 1 point of Confectance Index. Can be triggered up to 1 time per unit per round.",
        "icon": "assets/Liushih/Fixed Key 6 - Rallying Cry.png"
      },
      {
        "node": "Affinity Key - Hall of Jewels",
        "level": "-",
        "keyName": "Affinity Key - Hall of Jewels",
        "description": "CRIT +3%, HP +3%, DEF +3%",
        "icon": "assets/Liushih/Affinity Key - Hall of Jewels.png"
      },
      {
        "node": "Common Key - Financial Might",
        "level": "40",
        "keyName": "Common Key - Financial Might",
        "description": "HP +5% / Damage dealt by the holder's Entity Summons is increased by 10%",
        "icon": "assets/Liushih/Common Key - Financial Might.png"
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
            "effect": "All Electric-attribute Dolls and all Dolls that use Blades have their mobility is increased by 2 tiles (only applies once when multiple conditions (Electric or Melee) are met), and ignore enemy blocking. The Coagulation effect is enhanced; the maximum conversion of extra Critical Rate into ATK, healing, and Critical Damage is increased to 45%. The Blood Emblem effect is enhanced; for each stack of Coagulation, the damage multiplier is increased to 4%. The Scarlet Insignia effect is enhanced; Melee damage taken is increased to 10%."
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
        "effect": "All Electric-attribute Dolls and all Dolls that use Blades have their mobility is increased by 2 tiles (only applies once when multiple conditions (Electric or Melee) are met), and ignore enemy blocking. The Coagulation effect is enhanced; the maximum conversion of extra Critical Rate into ATK, healing, and Critical Damage is increased to 45%. The Blood Emblem effect is enhanced; for each stack of Coagulation, the damage multiplier is increased to 4%. The Scarlet Insignia effect is enhanced; Melee damage taken is increased to 10% ."
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
      "Resonance"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Shooting Instinct",
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
        "description": "Selects 1 target within 8 tiles, dealing Resonance damage equal to 90% of attack to them.",
        "upgrades": [],
        "icon": "assets/OTs-14/Shooting Instinct.png"
      },
      {
        "name": "Total Suppression",
        "traits": [
          "Active",
          "Aoe"
        ],
        "attribute": "Resonance",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "3x3",
        "description": "Selects 1 tile within an 8-tile radius and deals AoE Resonance Damage equal to 120% of attack to all enemy targets within a 3×3 area. If OTs-14 is under Cover Order, the damage accumulated by Command Mode is increased by 25% after skill usage. If OTs-14 is under Demolition Order, for every 15% initial Critical Damage, damage dealt is increased by 15%, and the damage multiplier is doubled.",
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
            "effect": "If the user is under Cover Order, the increase to damage accumulated by Command Mode after skill usage is raised to 33%.\nIf the user is under Demolition Order, then for every 15% initial Critical Damage, the damage multiplier is increased by 15%."
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
        "description": "Switches Command Mode between Cover Order and Demolition Order. After skill usage, gains Extra Command. This skill can be used up to 3 times per turn.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Cover Order effect enhanced: the increase to critical damage of all allied units except the user is raised to 15% of the user's initial Critical Damage.\nDemolition Order effect enhanced: the increase to the user's attack is raised to 15% of the initial attack of all allied Dolls except the user."
          }
        ],
        "icon": "assets/OTs-14/Perfect Adaptation.png"
      },
      {
        "name": "Sundering Demolition",
        "traits": [
          "Ultimate"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects 1 direction and applies Movement Down III to all enemy targets in front within a range of 3 to 10 tiles for 2 turns, then converts the damage accumulated by Command Mode into 1 point of Overload Pulse and gains Reverse Assimilation for 1 turn. This skill can be used while under Demolition Order and having Overload Pulse, or when the damage accumulated by Command Mode is greater than 0.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "Reverse Assimilation effect enhanced: the damage of Critical Blast is increased to 200%, and its effective range is increased by 2 tiles."
          },
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Reverse Assimilation effect enhanced: each time Critical Blast is used during the current turn, the damage multiplier of Critical Blast is increased by 50%, and the multiplier of the fixed damage dealt by consuming Overload Pulse is increased by 10%."
          }
        ],
        "icon": "assets/OTs-14/Sundering Demolition.png"
      },
      {
        "name": "Boojum Effect",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, performs Cellular Reconfiguration and enters Cover Order.\nAt the end of the turn, if the Ultimate skill Sundering Demolition was not used during this turn, the damage accumulated by Command Mode is converted into 1 point of Overload Pulse.\nAt the end of action, if the OTs-14 is under Demolition Order, switches to Cover Order.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Total Suppression active skill creates Phase tiles lvl 1 for 2 turns in the effective area if any Phase Reconfiguration is active. Reconfiguration · Zero does not create tiles.\nThe effects of Cellular Reconfiguration are enhanced: \nReconfiguration · Burn - Dispels 1 debuff when teammates gain Embers;\nReconfiguration · Electro - When an enemy unit's enters Stability Break, all allies regain 1 point of Stability Index;\nReconfiguration · Freeze - When an ally deals damage, increases their ATK by 10% of their shield value;\nReconfiguration · Corrosion - Active skill Total Suppression triggers all Corrosion debuffs held by enemy units within effect range;\nReconfiguration · Hydro - For each friendly unit, all Entity Summons gain 1% ATK and 1% maximum HP increase;\nReconfiguration · Zero - Demolition Order increases attack power by 50% instead of 30%, ignore 5% defense for every 15% initial Critical Damage."
          }
        ],
        "icon": "assets/OTs-14/Boojum Effect.png"
      },
      {
        "name": "Critical Blast",
        "traits": [
          "Basic Attack",
          "Active"
        ],
        "attribute": "Resonance",
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3-10",
        "effArea": "3",
        "description": "Selects 1 tile within 3-10 tile radius in front of self, deal AOE Resonance damage equal to 150% of attack to all enemy units within 3 tile radius around the selected tile. Consumes 1 Overload Pulse to deal additional fixed damage equal to 10% of accumulated damage of consumed Overload Pulse.",
        "upgrades": [],
        "icon": "assets/OTs-14/Critical Blast.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Perfect Adaptation",
        "level": "2",
        "effect": "Cover Order effect enhanced: the increase to critical damage of all allied units except the user is raised to 15% of the user's initial Critical Damage.\nDemolition Order effect enhanced: the increase to the user's attack is raised to 15% of the initial attack of all allied Dolls except the user."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Total Suppression",
        "level": "2",
        "effect": "Increases damage multiplier to 150%.\nThe effective area has been increased to 5×5 tiles.\nCooldown reduced by 1 turn."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Sundering Demolition",
        "level": "2",
        "effect": "Reverse Assimilation effect enhanced: the damage of Critical Blast is increased to 200%, and its effective range is increased by 2 tiles."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Sundering Demolition",
        "level": "3",
        "effect": "Reverse Assimilation effect enhanced: each time Critical Blast is used during the current turn, the damage multiplier of Critical Blast is increased by 50%, and the multiplier of the fixed damage dealt by consuming Overload Pulse is increased by 10%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Total Suppression",
        "level": "3",
        "effect": "If the user is under Cover Order, the increase to damage accumulated by Command Mode after skill usage is raised to 33%.\nIf the user is under Demolition Order, then for every 15% initial Critical Damage, the damage multiplier is increased by 15%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Boojum Effect",
        "level": "2",
        "effect": "Total Suppression active skill creates Phase tiles lvl 1 for 2 turns in the effective area if any Phase Reconfiguration is active. Reconfiguration · Zero does not create tiles.\nThe effects of Cellular Reconfiguration are enhanced: \nReconfiguration · Burn - Dispels 1 debuff when teammates gain Embers;\nReconfiguration · Electro - When an enemy unit's enters Stability Break, all allies regain 1 point of Stability Index;\nReconfiguration · Freeze - When an ally deals damage, increases their ATK by 10% of their shield value;\nReconfiguration · Corrosion - Active skill Total Suppression triggers all Corrosion debuffs held by enemy units within effect range;\nReconfiguration · Hydro - For each friendly unit, all Entity Summons gain 1% ATK and 1% maximum HP increase;\nReconfiguration · Zero - Demolition Order increases attack power by 50% instead of 30%, ignore 5% defense for every 15% initial Critical Damage."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Plunderer's Pace",
        "level": "20",
        "keyName": "Fixed Key 1 - Plunderer's Pace",
        "description": "After using the Active skill Total Suppression or Perfect Reaction, gains Additional Movement for 6 tiles. Can be triggered up to 1 time per turn.",
        "icon": "assets/OTs-14/Fixed Key 1 - Plunderer's Pace.png"
      },
      {
        "node": "Fixed Key 2 - Self-Recognition",
        "level": "20",
        "keyName": "Fixed Key 2 - Self-Recognition",
        "description": "When gaining Reverse Assimilation, dispels all debuffs from self.",
        "icon": "assets/OTs-14/Fixed Key 2 - Self-Recognition.png"
      },
      {
        "node": "Fixed Key 3 - Single-Minded Obsession",
        "level": "30",
        "keyName": "Fixed Key 3 - Single-Minded Obsession",
        "description": "If an active attack hits only 1 enemy target, damage dealt is increased by 20%.",
        "icon": "assets/OTs-14/Fixed Key 3 - Single-Minded Obsession.png"
      },
      {
        "node": "Fixed Key 4 - Perfect Plan",
        "level": "30",
        "keyName": "Fixed Key 4 - Perfect Plan",
        "description": "Before using the active skill Total Suppression, dispels 1 buff from the targets.",
        "icon": "assets/OTs-14/Fixed Key 4 - Perfect Plan.png"
      },
      {
        "node": "Fixed Key 5 - At All Costs",
        "level": "40",
        "keyName": "Fixed Key 5 - At All Costs",
        "description": "While OTs-14 is in the Cover Order state, damage taken is reduced by 20%.",
        "icon": "assets/OTs-14/Fixed Key 5 - At All Costs.png"
      },
      {
        "node": "Fixed Key 6 - Destructive Desire",
        "level": "40",
        "keyName": "Fixed Key 6 - Destructive Desire",
        "description": "Cellular Reconfiguration always grants Reconfiguration · Zero.",
        "icon": "assets/OTs-14/Fixed Key 6 - Destructive Desire.png"
      },
      {
        "node": "Affinity Key -  Private style",
        "level": "-",
        "keyName": "Affinity Key -  Private style",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/OTs-14/Affinity Key -  Private style.png"
      },
      {
        "node": "Common Key - Source of Pride",
        "level": "40",
        "keyName": "Common Key - Source of Pride",
        "description": "CRIT DMG +5.0% / The user's fixed damage is increased by 10%.",
        "icon": "assets/OTs-14/Common Key - Source of Pride.png"
      }
    ]
  },
  "Nemesis: Gnosis": {
    "class": "Sentinel",
    "stats": {
      "hp": 1948,
      "atk": 827,
      "def": 543
    },
    "stabilityGauge": 9,
    "movementSpeed": 5,
    "skillAttributes": [
      "Heavy Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Light Ammo",
      "Hydro"
    ],
    "skills": [
      {
        "name": "Starfall",
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
        "description": "Selects 1 enemy target within 9 tiles and deals Physical damage equal to 80% attack to them.",
        "upgrades": [],
        "icon": "assets/Nemesis_ Gnosis/Starfall.png"
      },
      {
        "name": "Calamity Resonance",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Select 1 enemy target within 9 tiles of the user and deal Corrosion damage equal to 100% of attack, then gains Doom Mark for 2 turns, Insight for 2 turns, and Extra Command. \nIf Nemesis has Fifth Prophecy: Startrack, the range of Action Support from Doom Mark is changed to the entire battlefield.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Doom Mark effect enhanced: the damage multiplier is increased to 110%, the number of Action Support triggers is increased by 1, and an additional 1 point of Confectance Index is restored."
          }
        ],
        "icon": "assets/Nemesis_ Gnosis/Calamity Resonance.png"
      },
      {
        "name": "Prismatic Refraction",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "9",
        "effArea": "Target",
        "description": "Selects 1 enemy target within a 9-tile radius and deals Corrosion Damage equal to 120% of attack.\nIf Nemesis has First Prophecy: Resonance, damage multiplier is increased by 20%, and gains 1 stack of Focus before skill usage.\nIf Nemesis has Second Prophecy: Solitude, damage dealt is increased by 20% when there are no allied units within a 4-tile radius of the user. After skill usage, restores HP equal to 15% of max HP.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "If Nemesis has First Prophecy: Resonance, the damage multiplier increase is raised from 20% to 40%.\nIf Nemesis has Second Prophecy: Solitude, and there are no allied units within a 4-tile radius of Nemesis, damage dealt is increase is raised from 20% to 40%, and the HP restored after skill usage is increased from 15% to 30%."
          }
        ],
        "icon": "assets/Nemesis_ Gnosis/Prismatic Refraction.png"
      },
      {
        "name": "Destiny Unfolding",
        "traits": [
          "Ultimate",
          "Aoe"
        ],
        "attribute": "Heavy Ammo",
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 1,
        "range": "9",
        "effArea": "1",
        "description": "Selects 1 enemy target within a 9-tile radius and deals AoE Corrosion Damage equal to 140% of attack to the target and all enemy units within a 1-tile radius around it, consuming all Confectance Index. For each 1 point of Confectance Index consumed, the damage is increased by 10%, and deals 1 point of stability damage.\nIf the user has Sixth Prophecy: Event Horizon, then for each 1 point of Confectance Index consumed, damage dealt is additionally increased by 10%, and all enemy targets within a 3-tile radius around the target additionally take AoE Corrosion Damage equal to 100% of attack and 1 point of stability damage.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Cooldown is reduced by 1 turn, and the damage multiplier is increased to 200%. If Nemesis has Fifth Prophecy: Startrack, damage dealt is increased by 50%."
          }
        ],
        "icon": "assets/Nemesis_ Gnosis/Destiny Unfolding.png"
      },
      {
        "name": "Whispers of Nirvana",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Damage dealt to Paradeus enemies is increased is increased by 20%.\nUpon the first use of the Active skill Calamity Resonance, if there are allied units within a 4-tile radius of Nemesis, gains First Prophecy: Resonance; if there are no allied units within a 4-tile radius of Nemesis, gains Second Prophecy: Solitude.\nAt the start of battle, if there are normal enemy units on the field, gains Third Prophecy: Calamity; if there are no normal enemy units on the field, gains Fourth Prophecy: Judgment. \nIf there are 2 allied Dolls using sniper rifles or 2 allied Corrosion Dolls on the field, Nemesis gains Fifth Prophecy: Startrack. If there are 4 allied Dolls using sniper rifles on the field, all allied Dolls using sniper rifles gain Sixth Prophecy: Event Horizon.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "First Prophecy: Resonance effect enhanced: Focus can stack without limit and is not removed when mobility points are consumed.\nSecond Prophecy: Solitude effect enhanced: Omen is replaced with Prophet."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Third Prophecy: Calamity effect enhanced: the damage multiplier is increased to 80%, and the effective range is expanded by 1 tile.\nFourth Prophecy: Judgment effect enhanced: the additional increase to the damage multiplier of Action Support is raised to 40%. When attacking elite or boss units, the Adjudication Privilege effect that ignores the target's defense is increased to 35%, the increase of Critical Damage is raised to 40%. Additionally, damage dealt is increased by 20%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Fifth Prophecy: Startrack effect enhanced: the range requirement for ignoring Cover when dealing targeted damage under Stellar Insight is removed. The increase to damage dealt for every 1 tile of distance from the target is increased to 10%, up to a maximum of 60%.\nSixth Prophecy: Event Horizon effect enhanced: the first Action Support triggered by Doom Mark each turn is replaced with the use of the Ultimate skill Destiny Unfolding, and it is treated as consuming all Confectance Index."
          }
        ],
        "icon": "assets/Nemesis_ Gnosis/Whispers of Nirvana.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Calamity Resonance",
        "level": "2",
        "effect": "Doom Mark effect enhanced: the damage multiplier is increased to 110%, the number of Action Support triggers is increased by 1, and an additional 1 point of Confectance Index is restored."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Destiny Unfolding",
        "level": "2",
        "effect": "Cooldown is reduced by 1 turn, and the damage multiplier is increased to 200%. If Nemesis has Fifth Prophecy: Startrack, damage dealt is increased by 50%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Whispers of Nirvana",
        "level": "2",
        "effect": "First Prophecy: Resonance effect enhanced: Focus can stack without limit and is not removed when mobility points are consumed.\nSecond Prophecy: Solitude effect enhanced: Omen is replaced with Prophet."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Prismatic Refraction",
        "level": "2",
        "effect": "If Nemesis has First Prophecy: Resonance, the damage multiplier is increase is raised from 20% to 40%.\nIf Nemesis has Second Prophecy: Solitude, and there are no allied units within a 4-tile radius of Nemesis, damage dealt is increase is raised from 20% to 40%, and the HP restored after skill usage is increased from 15% to 30%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Whispers of Nirvana",
        "level": "3",
        "effect": "Third Prophecy: Calamity effect enhanced: the damage multiplier is increased to 80%, and the effective range is expanded by 1 tile.\nFourth Prophecy: Judgment effect enhanced: the additional increase to the damage multiplier of Action Support is raised to 40%. When attacking Elite or Boss units, the Adjudication Privilege effect that ignores the target's defense is increased to 35%, the increase of Critical Damage is raised to 40%. Additionally, damage dealt is increased by 20%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Whispers of Nirvana",
        "level": "4",
        "effect": "Fifth Prophecy: Startrack effect enhanced: the range requirement for ignoring Cover when dealing targeted damage under Stellar Insight is removed. The increase to damage dealt for every 1 tile of distance from the target is increased to 10%, up to a maximum of 60%.\nSixth Prophecy: Event Horizon effect enhanced: the first Action Support triggered by Doom Mark each turn is replaced with the use of the Ultimate skill Destiny Unfolding, and it is treated as consuming all Confectance Index."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Return Anchor",
        "level": "20",
        "keyName": "Fixed Key 1 - Return Anchor",
        "description": "At the start of battle, gains 3 points of Confectance Index.",
        "icon": "assets/Nemesis_ Gnosis/Fixed Key 1 - Return Anchor.png"
      },
      {
        "node": "Fixed Key 2 - Wise Judgment",
        "level": "20",
        "keyName": "When having First Prophecy",
        "description": "Resonance, the range of Starfall, Calamity Resonance,Prismatic Refraction, and Destiny Unfolding is increased by 1 tile.",
        "icon": "assets/Nemesis_ Gnosis/When having First Prophecy (row 164).png"
      },
      {
        "node": "Fixed Key 3 -  Nomad Instinct",
        "level": "30",
        "keyName": "When having Second Prophecy",
        "description": "Solitude, if Nemesis defeats a target, gains Stealth for 1 turn.",
        "icon": "assets/Nemesis_ Gnosis/When having Second Prophecy (row 165).png"
      },
      {
        "node": "Fixed Key 4 -  Immune Bloodline",
        "level": "30",
        "keyName": "When having First Prophecy",
        "description": "Resonance, after performing Action Support, dispels 1 buff from the target.",
        "icon": "assets/Nemesis_ Gnosis/When having First Prophecy (row 166).png"
      },
      {
        "node": "Fixed Key 5 - Prophet’s Monologue",
        "level": "40",
        "keyName": "When having Second Prophecy",
        "description": "Solitude, mobility is increased by 2 tiles. After using the Prismatic Refraction, gains 4 tiles of Additional Movement.",
        "icon": "assets/Nemesis_ Gnosis/When having Second Prophecy (row 167).png"
      },
      {
        "node": "Fixed Key 6 - Blessing of Nirvana",
        "level": "40",
        "keyName": "Fixed Key 6 - Blessing of Nirvana",
        "description": "Upon every use (not only first use) of Calamity Resonance, if there are allied units within 4 tiles to Nemesis, she gains First Prophecy: Resonance; if there are no allied units within 4 tiles to Nemesis, she gains Second Prophecy: Solitude. Only 1 of either First Prophecy: Resonance or Second Prophecy: Solitude can exist at a time.",
        "icon": "assets/Nemesis_ Gnosis/Fixed Key 6 - Blessing of Nirvana.png"
      },
      {
        "node": "Affinity Key - Soft Whispers",
        "level": "-",
        "keyName": "Affinity Key - Soft Whispers",
        "description": "ATK +3%, HP +3%, CRIT DMG +3%",
        "icon": "assets/Nemesis_ Gnosis/Affinity Key - Soft Whispers.png"
      },
      {
        "node": "Common Key - Will of Vengeance",
        "level": "40",
        "keyName": "Common Key - Will of Vengeance",
        "description": "ATK +5.0% / At the start of battle, if there are 2 allied Dolls using sniper rifles or 2 allied Corrosion Dolls on the field, damage dealt is increased by 10%.",
        "icon": "assets/Nemesis_ Gnosis/Common Key - Will of Vengeance.png"
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
        "description": "Selects 1 enemy target within 8 tiles and deals Freeze damage equal to 80% of attack to them. Soppo gains Confectance Index and 2 points of Predator Mark. If Soppo is in Feral Form, this attack deals Burn damage instead.",
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
        "icon": "assets/Soppo/Fixed Key 2 - Want Another Bite_.png"
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
        "effArea": "Target",
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
        "stabilityDamage": 0,
        "cooldown": 2,
        "confectanceCost": 0,
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
        "icon": "assets/Mityl/Fixed Key 6 - Truth or Lie_.png"
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
  },
  "Faelynn": {
    "class": "Sentinel",
    "stats": {
      "hp": 1948,
      "atk": 820,
      "def": 553
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Medium Ammo",
      "Corrosion"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Cuspid Combo",
        "traits": [
          "Basic Attack",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 6 tiles and deals Physical damage equal to 80% of attack to them.",
        "upgrades": [],
        "icon": "assets/Faelynn/Cuspid Combo.png"
      },
      {
        "name": "Triple Maul",
        "traits": [
          "Active",
          "AoE",
          "Tile",
          "Debuff",
          "Control"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "3",
        "description": "Selects 1 enemy unit within 8 tiles, dealing AoE Corrosion damage equal to 60% of attack to all enemies within 3 tile of the target, cleanses 1 buff, inflicts Infatuated and Scent Mark and create Toxic Mist tiles for 2 turns. The damage multiplier of this skill is increased by 5% based on the number of Hunter's Tracking stacks held by the target. After the skill resolves, Faelynn gains 3 points of Confectance Index and 1 random buff, lasting 2 rounds.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Effective area is expanded to 5 tiles around the target, and the damage multiplier is increased by 10% for each stack of Hunter's Tracking. Scent Mark's damage multiplier is increased to 100%"
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Damage multiplier increased to 120%. If more than 3 targets or a Boss unit are hit, an additional instance of AoE corrosion damage equal to 120% of attack and 1 Stability Damage is dealt to the target. Scent Mark mark is enhanced, increasing damage taken from Faelynn by 30%."
          }
        ],
        "icon": "assets/Faelynn/Triple Maul.png"
      },
      {
        "name": "Keen-Eared Hunt",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Faelynn gains Roving Bloodlust for 3 turns and Dog-Eared Radar for 2 turns. After the skill resolves, she gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Apply Dog-Eared Radar for 1 additional turn. The effect of Roving Bloodlust is enhanced, increasing attack power by 30%."
          }
        ],
        "icon": "assets/Faelynn/Keen-Eared Hunt.png"
      },
      {
        "name": "Loyal Hunt",
        "traits": [
          "Ultimate",
          "AoE",
          "Tile"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction and deals AoE Corrosion damage equivalent to 120% ATK to all enemies within a 3x9 frontal area in the selected direction and creates Toxic Mist for 2 rounds. The damage multiplier is increased by 5% based on the number of Hunter's Tracking stacks held by the target. After the skill resolves, if Faelynn has Combo Pounce, consumes 1 stack of it to trigger the additional active skill Hunting Instinct I and gain Additional Movement.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "For each stack of Hunter's Tracking, the damage multiplier of the Ultimate Skill and of the all three extra active skill uses of Hunting Instinct increases by 10%. If Hunting Instinct II kills a target afflicted with Collar Brand, the next use of Hunting Instinct this turn will apply Collar Brand. Collar Brand's effect is enhanced: Corrosion Damage taken is increased by 30%."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Damage multiplier increased to 150%; the damage multipliers of the all three extra active skill uses of Hunting Instinct are increased to 90%, 170%, and 480% respectively. Each use of Hunting Instinct deals damage twice. If Hunting Instinct III results in a kill, gain 1 additional stack of Combo Pounce, up to a maximum of 2 stacks."
          }
        ],
        "icon": "assets/Faelynn/Loyal Hunt.png"
      },
      {
        "name": "Relentless Counterattack",
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
        "description": "At the start of battle, Faelynn gains 1 stack of Combo Pounce, stacking up to 3 times. Faelynn gains 1 stack of Combo Pounce stacks based on the number of active skills used (excluding Hunting Instinct).\nAt the start of the turn, if Faelynn is on a phase tile, she gains 1 mobility and 1 stack of Hunter's Tracking based on the tile's level, lasting 1 turn.\nIf Faelynn takes damage on a Corrosion-attribute tile, transfers 50% of the initial damage taken to the ally unit with the highest current HP (excluding Faelynn herself).\nFaelynn is immune to displacement, movement debuffs, and action prohibition effects.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "At the start of the turn, gain 4 stacks of Hunter's Tracking. The maximum stacks of Hunter's Tracking is increased to 6. Hunter's Tracking's effect is enhanced: Corrosion damage dealt is increased by 5% per stack."
          }
        ],
        "icon": "assets/Faelynn/Relentless Counterattack.png"
      },
      {
        "name": "Hunting Instinct I",
        "traits": [
          "Active",
          "AoE"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "3",
        "description": "Selects 1 enemy unit within 6 tiles, dealing AoE Corrosion damage equal to 60% of attack that ignores cover to all enemies within 3 tile of the target, and applies Collar Brand. The damage multiplier increases by 5% based on the number of Hunter’s Tracking stacks possessed. \nIf only 1 target is hit, the damage multiplier is additionally increased by 30%.\nAfter using the skill, if Combo Pounce is possessed, 1 stack of this effect is consumed to trigger the extra active skill Hunting Instinct II and Additional Movement.",
        "upgrades": [],
        "icon": "assets/Faelynn/Hunting Instinct I.png"
      },
      {
        "name": "Hunting Instinct II",
        "traits": [
          "Active",
          "AoE"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "3",
        "description": "Selects 1 enemy unit within 6 tiles, dealing AoE Corrosion damage equal to 120% of attack that ignores cover to all enemies within 3 tile of the target. Damage dealt to targets with Collar Brand is increased by 50%. The damage multiplier increases by 5% based on the number of Hunter’s Tracking stacks possessed. \nIf only 1 target is hit, the damage multiplier is additionally increased by 30%.\nAfter using the skill, if Combo Pounce is possessed, 1 stack of this effect is consumed to trigger the extra active skill Hunting Instinct III and Additional Movement.",
        "upgrades": [],
        "icon": "assets/Faelynn/Hunting Instinct II.png"
      },
      {
        "name": "Hunting Instinct III",
        "traits": [
          "Active",
          "AoE"
        ],
        "attribute": "Corrosion",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "3",
        "description": "Selects 1 enemy unit within 6 tiles, dealing AoE Corrosion damage equal to 240% of attack that ignores cover to all enemies within 3 tile of the target. Damage dealt to targets with Collar Brand is increased by 100%. Before attacking, if target on a phase tile, for each level of the tile, its DEF is reduced by 14% and Faelynn Critical Damage is increaced by 5%. The damage multiplier increases by 5% based on the number of Hunter’s Tracking stacks possessed. \nIf only 1 target is hit, the damage multiplier is additionally increased by 30%.",
        "upgrades": [],
        "icon": "assets/Faelynn/Hunting Instinct III.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Keen-Eared Hunt",
        "level": "2",
        "effect": "Apply Dog-Eared Radar for 1 additional turn. The effect of Roving Bloodlust is enhanced, increasing attack power by 30%."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Triple Maule",
        "level": "2",
        "effect": "Effective area is expanded to 5 tiles around the target, and the damage multiplier is increased by 10% for each stack of Hunter's Tracking. Scent Mark's damage multiplier is increased to 100%"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Loyal Hunt",
        "level": "2",
        "effect": "For each stack of Hunter's Tracking, the damage multiplier of the Ultimate Skill and active skill Hunting Instinct increases by 10%. If the Hunting Instinct II kills a target afflicted with Collar Brand, the next use of Hunting Instinct this turn will apply Collar Brand. Collar Brand's effect is enhanced: Corrosion Damage taken is increased by 30%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Relentless Counterattack",
        "level": "2",
        "effect": "At the start of the turn, gain 4 stacks of Hunter's Tracking. The maximum stacks of Hunter's Tracking is increased to 6. Hunter's Tracking's effect is enhanced: Corrosion damage dealt is increased by an additional 5%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Triple Maule",
        "level": "3",
        "effect": "Damage multiplier increased to 120%. If more than 3 targets or a Boss unit are hit, an additional instance of AoE Corrosion damage equal to 120% of attack and 1 Stability Damage is dealt to the target. Scent Mark mark is enhanced, increasing damage taken from Faelynn by 30%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Loyal Hunt",
        "level": "3",
        "effect": "Damage multiplier increased to 150%; the damage multipliers of the three extra active skill uses of Hunting Instinct are increased to 90%, 170%, and 480% respectively. Each use of Hunting Instinct deals damage twice. If the Hunting Instinct III results in a kill, gain 1 additional stack of Combo Pounce, up to a maximum of 2 stacks."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Dango Finisher",
        "level": "20",
        "keyName": "Fixed Key 1 - Dango Finisher",
        "description": "Increases damage dealt to enemy units that are not at full HP by 7%.",
        "icon": "assets/Faelynn/Fixed Key 1 - Dango Finisher.png"
      },
      {
        "node": "Fixed Key 2 - Piloerection",
        "level": "20",
        "keyName": "Fixed Key 2 - Piloerection",
        "description": "Before using the additional active skill Hunting Instinct, cleanses 1 buff from the target.",
        "icon": "assets/Faelynn/Fixed Key 2 - Piloerection.png"
      },
      {
        "node": "Fixed Key 3 - One Last Kon",
        "level": "30",
        "keyName": "Fixed Key 3 - One Last Kon",
        "description": "When the user dies, deals fixed damage equal to 500% of ATK and 3 points of Stability Damage to all enemy units within 6 tile radius around self, generates Toxic Mist tiles, and applies One Last Kon for 2 turns. If the enemy units are non-boss units, additional fixed damage equal to 300% of maximum HP is dealt.",
        "icon": "assets/Faelynn/Fixed Key 3 - One Last Kon.png"
      },
      {
        "node": "Fixed Key 4 - Predator's Footwork",
        "level": "30",
        "keyName": "Fixed Key 4 - Predator's Footwork",
        "description": "At the start of the turn, generate Toxic Mist tiles within 1 tile around the user lasting 2 turns",
        "icon": "assets/Faelynn/Fixed Key 4 - Predator's Footwork.png"
      },
      {
        "node": "Fixed Key 5 - Floof Armor",
        "level": "40",
        "keyName": "Fixed Key 5 - Floof Armor",
        "description": "While the user is on a Corrosion-attribute tile, damage taken is reduced by 15% and stability damage taken is reduced by 1 point.",
        "icon": "assets/Faelynn/Fixed Key 5 - Floof Armor.png"
      },
      {
        "node": "Fixed Key 6 - Scenting",
        "level": "40",
        "keyName": "Fixed Key 6 - Scenting",
        "description": "At the start of battle, applies Scent Mark to the enemy unit with the highest HP for 2 turns.",
        "icon": "assets/Faelynn/Fixed Key 6 - Scenting.png"
      },
      {
        "node": "Affinity Key - A Romantic Journey",
        "level": "40",
        "keyName": "Affinity Key - A Romantic Journey",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Faelynn/Affinity Key - A Romantic Journey.png"
      },
      {
        "node": "Common Key - Canine Intimidation",
        "level": "40",
        "keyName": "Common Key - Canine Intimidation",
        "description": "CRIT +5.0% / At the start of the turn, if the user is on a Level 3 phase tile, AoE damage dealt is increased by 10% for 1 round.",
        "icon": "assets/Faelynn/Common Key - Canine Intimidation.png"
      }
    ]
  },
  "Koleda": {
    "class": "Vanguard",
    "stats": {
      "hp": 1988,
      "atk": 767,
      "def": 494
    },
    "stabilityGauge": 8,
    "movementSpeed": 9,
    "skillAttributes": [
      "Medium Ammo",
      "Hydro"
    ],
    "weaknesses": [
      "Heavy Ammo",
      "Electric"
    ],
    "skills": [
      {
        "name": "Hunting Instinct",
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
        "description": "Selects 1 enemy target within 8 tiles and deals Hydro damage equal to 80% of attack to them. The Sinner switches to N Gear.",
        "upgrades": [],
        "icon": "assets/Koleda/Hunting Instinct.png"
      },
      {
        "name": "Eye of the Snow Wolf",
        "traits": [
          "Active",
          "Targeted"
        ],
        "attribute": "Medium Ammo",
        "stabilityDamage": 3,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "8",
        "effArea": "Target",
        "description": "Selects 1 enemy target within 8 tiles and deal Hydro damage equal to 150% of attack to it. Before the skill resolves, Koleda gains 1 stack of Upshift for 3 turns. After the skill resolves, Koleda gains 1 point of Confectance Index.\nThe Sinner switches to S+ Gear.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "The damage multiplier is increased to 180%, and for every level of Upshift, the damage multiplier is increased by 15%.\nUpshift effect is increased: Hydro damage increase is boosted to 15%. When holding 5 layers of Upshift, Critical Damage is increased by 30% and damage taken is reduced by 30%.\nBefore the skill, Koleda and The Sinner gain Turbo boost for 1 round."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Turbo boost effect is increased: attack increase is boosted to 45%.\nThe Sinner active skill Let's Go For a Spin! effect is increased: Additional attributes obtained by The Sinner are increased to 70%. When The Sinner casts active skill Speedy Speed Doll!, it applies a Phase tile corresponding to Phase attribute of the Doll selected by Let's Go For a Spin! lasting 2 rounds."
          }
        ],
        "icon": "assets/Koleda/Eye of the Snow Wolf.png"
      },
      {
        "name": "Tactical Playbook",
        "traits": [
          "Active",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 3,
        "range": "Self",
        "effArea": "Target",
        "description": "Koleda gains 2 stacks of Upshift for 3 turns. Koleda and The Sinner gain Kinetic Recovery for 3 turns.\nThe Sinner switches to S Gear.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Kinetic Recovery effect is increased: attack power, Critical Damage, and healing recieved increase is boosted to 25%.\nThe Sinner active skill KANSEI DORIFTO?! damage multiplier is increased to 120%, its effective range is increased to 7 tiles, the Pull range is increased to 7 tiles, and it applies Immobilized for 2 turns."
          }
        ],
        "icon": "assets/Koleda/Tactical Playbook.png"
      },
      {
        "name": "Hallucination",
        "traits": [
          "Ultimate",
          "Summon"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Selects one empty tile within 3 tile radius around self and summons The Sinner. Koleda gains Extra Command, and this skill is replaced with the active skill Winner!.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "Winner! effect is increased: Restores 100% Max HP and all Stability index of The Sinner, and dispels all debuffs from The Sinner.\nThe Sinner active skill Speedy Speed Doll! effect is increased: damage multiplier is increased to 120%, and the width is increased by 2 tiles.The additional damage multiplier of S Gear and S+ Gear have been increased to 90% and 120%."
          }
        ],
        "icon": "assets/Koleda/Hallucination.png"
      },
      {
        "name": "The Sinner",
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
        "description": "At the start of the turn, Koleda gains 1 point of Confectance Index. A 50% of Initial damage taken by Koleda is shared by The Sinner. Koleda is not affected by other damage-sharing effects.\n\nAt the end of The Sinner's action, Koleda gains 1 stack of Upshift for 3 turns. If The Sinner is on S+ Gear, Koleda gains an additional 1 stack of Upshift. When Koleda and The Sinner are present on the field, they gain Mobile Support. The effect is removed when either dies.\n \nAfter Koleda uses the active skill Tactical Playbook and at the end of her action, Kinetic Release is triggered 1 time.\n \n When The Sinner uses the active skill Let's Go For a Spin!, Koleda gains The Sinner's base attack and critical damage. The effect is removed when The Sinner dies",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "The number of Confectance Index obtained at the start of the turn is increased by 1 point.\nAfter using the active skill Tactical Playbook and at the end of the action, casts Kinetic Release+ 1 time instead.\nThe damage multiplier of Kinetic Release and Kinetic Release+ is increased by 30%."
          },
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "The damage shared by the The Sinner for Koleda has been increased to 80%, and the health recovered before taking damage has been increased to 25% of the max HP.\nP Gear effect increased: Target damage and AOE damage taken reduction is increased to 30%; N Gear effect increased: damage taken reduction is increased to 150%, Defense increase is boosted to 150%, and Healing recieved is increased by 150%; D gear, S gear, and S+ gear effect increased: Hydro damage increase is boosted to 30%; S gear, and S+ gear effect increased: Critical Damage increase is boosted to 30%; S+ gear effect increased: ignore of target's Defence is increased to 30%, and the damage multiplier of all damaging skills is increased by 30%."
          }
        ],
        "icon": "assets/Koleda/The Sinner.png"
      },
      {
        "name": "Winner!",
        "traits": [
          "Active",
          "Healing",
          "Stability Recovery"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 6,
        "range": "Self",
        "effArea": "Target",
        "description": "Restores The Sinner's 50% of max HP and 5 points of stability.",
        "upgrades": [],
        "icon": "assets/Koleda/Winner!.png"
      },
      {
        "name": "Let's Go For a Spin!",
        "traits": [
          "Active",
          "Summon Skill"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 99,
        "confectanceCost": 0,
        "range": "3",
        "effArea": "Target",
        "description": "Selects 1 friendly Doll (excluding Koleda) and applies Let's Go For a Spin! to them. \n \nAfter the skill resolves, The Sinner gains 9 tiles of Additional Movement and can use 1 command.",
        "upgrades": [],
        "icon": "assets/Koleda/Let's Go For a Spin!.png"
      },
      {
        "name": "KANSEI DORIFTO?!",
        "traits": [
          "Active",
          "AoE",
          "Summon Skill"
        ],
        "attribute": null,
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "5",
        "description": "Deals AoE Hydro damage equal to 90% of ATK to all enemy units within 5 tile radius around the unit and Pull them 5 tiles towards the centre of The Sinner's position. After the skill resolves, The Sinner gains 9 tiles of Additional Movement and can use the active skill Speedy Speed Doll!.",
        "upgrades": [],
        "icon": "assets/Koleda/KANSEI DORIFTO_!.png"
      },
      {
        "name": "Speedy Speed Doll!",
        "traits": [
          "Active",
          "Summon Skill"
        ],
        "attribute": null,
        "stabilityDamage": 3,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "--",
        "effArea": "Target",
        "description": "Selects 1 tile within cross-shaped area of 4 to 8 tiles, lands on it, and deals AoE Hydro damage equal to 90% of ATK to all enemy targets within 3 tile width along the path. If The Sinner is on S Gear or S+ Gear, additional AoE Hydro damage is dealt equal to 60% and 90% of ATK.",
        "upgrades": [],
        "icon": "assets/Koleda/Speedy Speed Doll!.png"
      },
      {
        "name": "Gear Shift",
        "traits": [
          "Passive",
          "Summon Skill"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of the turn, The Sinner switches to D Gear. At the end of the final action taken, removes all Gears except N Gear and switches to P Gear. Only 1 Gear can be set at a time. \n \nThe Sinner cannot be blocked by enemies, is immune to the status effects Stun, Taunt, and Incapacitation, as well as displacement and movement debuffs. In addition, damage taken by The Sinner is reduced by 35% and it recovers HP equal to 15% its Max HP when taking damage.\n\n At the end of The Sinner's action, if it is on S Gear, Kinetic Release is triggered, if it is on S+ Gear, Kinetic Release+ is triggered instead.",
        "upgrades": [],
        "icon": "assets/Koleda/Gear Shift.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Eye of the Snow Wolf",
        "level": "2",
        "effect": "The damage multiplier is increased to 180%, and for every level of Upshift, the damage multiplier is increased by 15%.\nUpshift effect is increased: Hydro damage increase is boosted to 15%. When holding 5 layers of Upshift, Critical Damage is increased by 30% and damage taken is reduced by 30%.\nBefore the skill, Koleda and The Sinner gain Turbo boost for 1 round."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "The Sinner",
        "level": "2",
        "effect": "The number of Confectance Index obtained at the start of the turn is increased by 1 point.\nAfter using the active skill Tactical Playbook and at the end of the action, casts Kinetic Release+ 1 time instead.\nThe damage multiplier of Kinetic Release and Kinetic Release+ is increased by 30%."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "The Sinner",
        "level": "3",
        "effect": "The damage shared by the The Sinner for Koleda has been increased to 80%, and the health recovered before taking damage has been increased to 25% of the max HP.\nP Gear effect increased: Target damage and AOE damage taken reduction is increased to 30%; N Gear effect increased: damage taken reduction is increased to 150%, Defense increase is boosted to 150%, and Healing recieved is increased by 150%; D gear, S gear, and S+ gear effect increased: Hydro damage increase is boosted to 30%; S gear, and S+ gear effect increased: Critical Damage increase is boosted to 30%; S+ gear effect increased: ignore of target's Defence is increased to 30%, and the damage multiplier of all damaging skills is increased by 30%."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Tactical Playbook",
        "level": "2",
        "effect": "Kinetic Recovery effect is increased: attack power, Critical Damage, and healing recieved increase is boosted to 25%.\nThe Sinner active skill KANSEI DORIFTO?! damage multiplier is increased to 120%, its effective range is increased to 7 tiles, the Pull range is increased to 7 tiles, and it applies Immobilized for 2 turns."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Hallucination",
        "level": "2",
        "effect": "Winner! effect is increased: Restores 100% Max HP and all Stability index of The Sinner, and dispels all debuffs from The Sinner.\nThe Sinner active skill Speedy Speed Doll! effect is increased: damage multiplier is increased to 120%, and the width is increased by 2 tiles.The additional damage multiplier of S Gear and S+ Gear have been increased to 90% and 120%."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Eye of the Snow Wolf",
        "level": "3",
        "effect": "Turbo boost effect is increased: attack increase is boosted to 45%.\nThe Sinner active skill Let's Go For a Spin! effect is increased: Additional attributes obtained by The Sinner are increased to 70%. When The Sinner casts active skill Speedy Speed Doll!, it applies a Phase tile corresponding to Phase attribute of the Doll selected by Let's Go For a Spin! lasting 2 rounds."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Creed",
        "level": "20",
        "keyName": "Fixed Key 1 - Creed",
        "description": "At the start of the battle, Koleda gains 2 stacks of Upshift and Kinetic Recovery for 3 turns. When The Sinner is summoned at the start of the battle, Koleda and The Sinner gain Kinetic Recovery for 3 turns",
        "icon": "assets/Koleda/Fixed Key 1 - Creed.png"
      },
      {
        "node": "Fixed Key 2 - No Time to Die",
        "level": "20",
        "keyName": "Fixed Key 2 - No Time to Die",
        "description": "When The Sinner takes lethal damage, its HP will not drop below 1 and this effect will last until the end of the round. Cooldown: 2 turns.",
        "icon": "assets/Koleda/Fixed Key 2 - No Time to Die.png"
      },
      {
        "node": "Fixed Key 3 - Dream of Ruin",
        "level": "30",
        "keyName": "Fixed Key 3 - Dream of Ruin",
        "description": "Before The Sinner uses an active skill, cleanse 1 buff from the target",
        "icon": "assets/Koleda/Fixed Key 3 - Dream of Ruin.png"
      },
      {
        "node": "Fixed Key 4 - Desperate Measures",
        "level": "30",
        "keyName": "Fixed Key 4 - Desperate Measures",
        "description": "At the start of the turn, if Koleda has 5 stacks of Upshift, movement debuffs and command-prohibition effects are cleansed",
        "icon": "assets/Koleda/Fixed Key 4 - Desperate Measures.png"
      },
      {
        "node": "Fixed Key 5 - Remember the Name",
        "level": "40",
        "keyName": "Fixed Key 5 - Remember the Name",
        "description": "Before Koleda and The Sinner uses a basic attack or active skill, applies Defense Down II to the enemy target for 2 turns.",
        "icon": "assets/Koleda/Fixed Key 5 - Remember the Name.png"
      },
      {
        "node": "Fixed Key 6 - Those Who Cling to Life, Dies",
        "level": "40",
        "keyName": "Fixed Key 6 - Those Who Cling to Life, Dies",
        "description": "When The Sinner is on S Gear or S+ Gear, for each enemy unit that dies, attack of The Sinner is increased by 4% up to 20%",
        "icon": "assets/Koleda/Fixed Key 6 - Those Who Cling to Life, Dies.png"
      },
      {
        "node": "Affinity Key - Dancing with wolves",
        "level": "-",
        "keyName": "Affinity Key - Dancing with wolves",
        "description": "ATK +3%, CRIT +3%, CRIT DMG +3%",
        "icon": "assets/Koleda/Affinity Key - Dancing with wolves.png"
      },
      {
        "node": "Common Key - A View to a Kill",
        "level": "40",
        "keyName": "Common Key - A View to a Kill",
        "description": "CRIT +5.0% / If the user or their summon has mobility greater than or equal to the target's, damage dealt is increased by 10%.",
        "icon": "assets/Koleda/Common Key - A View to a Kill.png"
      }
    ]
  },
  "Asteria": {
    "class": "Support",
    "stats": {
      "hp": 2030,
      "atk": 722,
      "def": 577
    },
    "stabilityGauge": 10,
    "movementSpeed": 8,
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
        "name": "Silent Trigger",
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
        "icon": "assets/Asteria/Silent Trigger.png"
      },
      {
        "name": "Assault Focus",
        "traits": [
          "Active",
          "Displacement",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "5",
        "effArea": "Target",
        "description": "Selects 1 tile within 5 tiles, leaps to it, and gains Steady for 1 turn.\n\nIf there is Cover nearby when landing, the effects of Steady is increased to 40% and applies Sync to the unit with Bond for 1 round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "Sync gains a new effect: When attacking, nullifies 100% of attack reduction debuff effect.\r\n\r\nWhen applying Sync, apply Damage Reduction II to all allied units for 2 turns."
          }
        ],
        "icon": "assets/Asteria/Assault Focus.png"
      },
      {
        "name": "Demolition Reckoning",
        "traits": [
          "Active",
          "AoE",
          "Debuff",
          "Buff"
        ],
        "attribute": null,
        "stabilityDamage": 2,
        "cooldown": 0,
        "confectanceCost": 4,
        "range": "--",
        "effArea": "3",
        "description": "Select one tile within a cross-shaped area of 8 tiles to launch an attack, dealing AoE Physical damage equal to 80% of attack to all enemy targets within 3 tiles and applies Movement Down II for 2 turns. If 2 or more targets or a Boss is hit, Asteria gains 6 tiles of Extra Movement and applies Sync to units holding Bond for 1 round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Applies Stun to the target for 1 turn.\r\n\r\nSync is enhanced: Units with Bond gain 30% of Asteria's initial critical damage."
          }
        ],
        "icon": "assets/Asteria/Demolition Reckoning.png"
      },
      {
        "name": "Railgun Judgement",
        "traits": [
          "Ultimate",
          "AoE",
          "Debuff"
        ],
        "attribute": null,
        "stabilityDamage": 5,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "1",
        "effArea": "--",
        "description": "Selects a direction, applies Vindicator's Mark for 2 rounds and Defense Down II for 3 turns to all enemy targets in a 3x8 area in front, and deals AoE Physical damage equal to 240% of attack that ignores Cover damage reduction. This attacks ignores 100% of the target's defense.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "Damage multiplier increased to 300%.\n\nWhen attacking, ignore 200% of the target's defense and nullifies all defense buff effects on the target.\n\nVindicator's Mark is enhanced: When taking Physical damage, takes an additional 10% of final damage as fixed damage."
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Applies Defense Down III to the target for 3 turns.\n\nWhen Asteria gains Crime and Punishment again, attack is increased by 80% this turn.\n\nFor each stack of Absolution that the target has, the damage multiplier of Asteria's Ultimate skill Railgun Judgement and Blade of Sin launched by Crime and Punishment is increased by 50%."
          }
        ],
        "icon": "assets/Asteria/Railgun Judgement.png"
      },
      {
        "name": "Bond Connextion",
        "traits": [
          "Passive"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "At the start of battle, select 1 Physical attributed Doll and apply Bond to them.\r\n\r\nWhen allied units deal non-ammo type Physical damage, apply the ammo type of the weapon they are using.\r\n\r\nAt the start of battle, gain Crime and Punishment.\r\n\r\nAt the end of the round after using the Ultimate skill Railgun Judgement, the unit with Bond gains Crime and Punishment and their stat increase is reduced by 50% for 1 round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "While under the effects of Crime and Punishment, when attacking, nullifies 150% of the target's defense buff effect.\n\nThe damage multiplier of Blade of Sin launched by Crime and Punishment increased to 100% and ignores 50% of the target's defense.\n\nBlade of Sin triggered by Physical damage has no limit on the number of triggers, but can trigger up to 1 time per unit per turn.\n\nShield of Punishment can be triggered 1 additional time."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "When Blade of Sin is launched by Crime and Punishment, applies Absolution to the target for 3 turns.\n\nAfter using an active skill (excluding Bond Connextion) or basic attack, the unit with Bond gains Crime and Punishment and resets the number of attacks from Blade of Sin until the end of this round.\n\nAsteria gains Crime and Punishment which can only trigger Shield of Punishment."
          }
        ],
        "icon": "assets/Asteria/Bond Connextion.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "Railgun Judgement",
        "level": "2",
        "effect": "Damage multiplier increased to 300%.\r\n\r\nWhen attacking, ignore 200% of the target's defense and nullifies all defense buff effects on the target.\r\n\r\nVindicator's Mark is enhanced: When taking Phsyical damage, takes an additional 10% of final damage as fixed damage."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Demolition Reckoning",
        "level": "2",
        "effect": "Applies Stun to the target for 1 turn.\r\n\r\nSync is enhanced: Units with Bond gain 30% of Asteria's initial critical damage."
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Bond Connextion",
        "level": "2",
        "effect": "While under the effects of Crime and Punishment, when attacking, nullifies 150% of the target's defense buff effect.\n\nThe damage multiplier of Blade of Sin launched by Crime and Punishment increased to 100% and ignores 50% of the target's defense.\n\nBlade of Sin triggered by Physical damage has no limit on the number of triggers, but can trigger up to 1 time per unit per turn.\n\nShield of Punishment can be triggered 1 additional time."
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Assault Focus",
        "level": "2",
        "effect": "Sync gains a new effect: When attacking, nullifies 100% of attack reduction debuff effect.\r\n\r\nWhen applying Sync, apply Damage Reduction II to all allied units for 2 turns."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "Bond Connextion",
        "level": "3",
        "effect": "When Blade of Sin is launched by Crime and Punishment, applies Absolution to the target for 3 turns.\n\nAfter using an active skill (excluding Bond Connextion) or basic attack, the unit with Bond gains Crime and Punishment and resets the number of attacks from Blade of Sin until the end of this round.\n\nAsteria gains Crime and Punishment which can only trigger Shield of Punishment."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Railgun Judgement",
        "level": "3",
        "effect": "Applies Defense Down III to the target for 3 turns.\r\n\r\nWhen Asteria gains Crime and Punishment again, attack is increased by 80% this turn.\r\n\r\nFor each stack of Absolution that the target has, the damage multiplier of Asteria's Ultimate skill Railgun Judgement and Blade of Sin launched by Crime and Punishment is increased by 50%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Invisible Guardian",
        "level": "20",
        "keyName": "Fixed Key 1 - Invisible Guardian",
        "description": "Physical damage dealt by all allied unit's out-of-turn attacks are increased by 10%.",
        "icon": "assets/Asteria/Fixed Key 1 - Invisible Guardian.png"
      },
      {
        "node": "Fixed Key 2 - Vindicator",
        "level": "20",
        "keyName": "Fixed Key 2 - Vindicator",
        "description": "When applying Sync, refresh the duration of all Vindicator's Mark on the field.",
        "icon": "assets/Asteria/Fixed Key 2 - Vindicator.png"
      },
      {
        "node": "Fixed Key 3 - Goliath Domain",
        "level": "30",
        "keyName": "Fixed Key 3 - Goliath Domain",
        "description": "Before a allied unit attacks a target with Vindicator's Mark, they gain Reversed Assault for 3 turns.",
        "icon": "assets/Asteria/Fixed Key 3 - Goliath Domain.png"
      },
      {
        "node": "Fixed Key 4 - Promise of Reunion",
        "level": "30",
        "keyName": "Fixed Key 4 - Promise of Reunion",
        "description": "When a unit with Vindicator's Mark dies, apply Vindicator's Mark to the nearest enemy unit for 2 rounds.",
        "icon": "assets/Asteria/Fixed Key 4 - Promise of Reunion.png"
      },
      {
        "node": "Fixed Key 5 - Result-Oriented",
        "level": "40",
        "keyName": "Fixed Key 5 - Result-Oriented",
        "description": "For every different enemy unit attacked by Crime and Punishment, damage dealt increased by 5%, up to a maximum of 30%.",
        "icon": "assets/Asteria/Fixed Key 5 - Result-Oriented.png"
      },
      {
        "node": "Fixed Key 6 - Path of Pursuit",
        "level": "40",
        "keyName": "Fixed Key 6 - Path of Pursuit",
        "description": "Ultimate skill Railgun Judgement is changed to deal melee damage, and damage dealt to Paradeus units is increased by 80%.",
        "icon": "assets/Asteria/Fixed Key 6 - Path of Pursuit.png"
      },
      {
        "node": "Affinity Key - Silent Bond",
        "level": "-",
        "keyName": "Affinity Key - Silent Bond",
        "description": "ATK +3%, CRIT +3%, HP +3%",
        "icon": "assets/Asteria/Affinity Key - Silent Bond.png"
      },
      {
        "node": "Common Key - One Who Looks Up to the Sky",
        "level": "40",
        "keyName": "Common Key - One Who Looks Up to the Sky",
        "description": "ATK +5% / When using an Ultimate Skill, damage dealt this turn is increased by 10%.",
        "icon": "assets/Asteria/Common Key - One Who Looks Up to the Sky.png"
      }
    ]
  },
  "Eagletta": {
    "class": "Sentinel",
    "stats": {
      "hp": 1801,
      "atk": 837,
      "def": 577
    },
    "stabilityGauge": 9,
    "movementSpeed": 6,
    "skillAttributes": [
      "Light Ammo",
      "Freeze"
    ],
    "weaknesses": [
      "Shotgun Ammo",
      "Corrosion"
    ],
    "skills": [
      {
        "name": "Rapid Pursuit",
        "traits": [
          "Basic Attack"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Depending on her Combat Stance, Eagletta uses the basic attack Swift Eagle Strike or Rending Talons.",
        "upgrades": [],
        "icon": "assets/Eagletta/Rapid Pursuit.png"
      },
      {
        "name": "Swift Eagle Strike",
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
        "description": "Consumes 2 Feathers of War to select 1 enemy target within a 6-tile radius, dealing Freeze damage equal to 100% of ATK. Damage dealt is increased by 15% and Critical Damage is increased by 5%. \nAfter the skill resolves, Eagletta gains 6 tiles of Additional Movement and can use one command. \nIf the target is killed, the skills and effects that would trigger upon its death is nullified. \nThis skill can only be used when Eagletta has 2 or more Feathers of War.",
        "upgrades": [],
        "icon": "assets/Eagletta/Swift Eagle Strike.png"
      },
      {
        "name": "Rending Talons",
        "traits": [
          "Basic Attack",
          "Targeted",
          "Melee"
        ],
        "attribute": "Melee",
        "stabilityDamage": 1,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "3x3",
        "effArea": "Target",
        "description": "Select 1 enemy target within a 3x3 area, dealing Freeze damage equal to 60% of ATK and recovers HP equal to 20% of damage dealt. \nIf the target is killed, the skills and effects that would trigger upon its death is nullified, Eagletta gains 8 tiles Additional Movement and can use one command. The range of this skill cannot be modified.",
        "upgrades": [],
        "icon": "assets/Eagletta/Rending Talons.png"
      },
      {
        "name": "Deterrence Tactics",
        "traits": [
          "Active"
        ],
        "attribute": null,
        "stabilityDamage": 0,
        "cooldown": 0,
        "confectanceCost": 0,
        "range": "Self",
        "effArea": "Target",
        "description": "Switches Combat Stance. After the skill resolves, Eagletta gains Extra Command. This skill can be used up to 1 time per round.\n\nPassive: At the start of the round, Eagletta switches to the Eagle Strike stance.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 2,
            "label": "Vertebrae Upgrade 2",
            "effect": "Passive effect added: At the end of the round, if the number of Lock on Attack for the passive skill The Wild Within has not reached the limit, gain 2 Feathers of War for each remaining use. The damage multiplier of basic attack Swift Eagle Strike is increased to 120%, damage dealt increase is raised to 25% and the critical damage increase is raised to 10%. The damage multipliers of basic attack Rending Talons and passive skill Predation are increased to 80%"
          },
          {
            "type": "vertebrae",
            "number": 6,
            "label": "Vertebrae Upgrade 6",
            "effect": "Passive effect added: When the ultimate Featherstorm Feast consumes 3 Feathers of War, the damage multiplier is additionally increased by 30%. This effect is also applies to the skill effect of Featherstorm Feast triggered by using basic attack Swift Eagle Strike while having 4 stacks of Invasive Threat. For each stack of Invasive Threat, own damage dealt is increased by 10%: when an enemy unit takes damage from an allied unit, if its on Freeze-type tile, the damage it takes is increased by 10% for each stack of Invasive Threat.\nThe ATK boost from Eagle Strike stance is increased by 20%.\nThe damage multiplier of basic attack Swift Eagle Strike is increased to 150%, the damage dealt increase is raised to 40% and critical damage increase is rased to 15%.\nThe DEF ignored by basic attack Rending Talons and passive skill Predation is increased to 10%. When Feathers of War are consumed by Heavy Talons stance, the damage multiplier increase for basic attack Rending Talons and passive skill Predation is raised to 10%."
          }
        ],
        "icon": "assets/Eagletta/Deterrence Tactics.png"
      },
      {
        "name": "Stoop Strike",
        "traits": [
          "Active",
          "Targeted",
          "Debuff",
          "Control"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 1,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Selects 1 tile within a 6-tile radius of self and lands on it, dealing Freeze damage equal to 100% of ATK to the nearest enemy target within 4-tile radius and applies Vulnerable II for 2 turns. \nAfter the skill resolves, applies Taunt and Queen of the Skies to all non-Boss enemy units within 4-tile radius around self for 2 turns. In addition, Eagletta gains Extra Command.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 3,
            "label": "Vertebrae Upgrade 3",
            "effect": "The damage multiplier increased to 120%. The range for applying Queen of the Skies is increased to within 5-tile radius around self. The effect of Queen of the Skies is enhanced: The damage reduction of the first attack against Eagletta is increased to 40%"
          }
        ],
        "icon": "assets/Eagletta/Stoop Strike.png"
      },
      {
        "name": "Featherstorm Feast",
        "traits": [
          "Ultimate",
          "Targeted"
        ],
        "attribute": "Light Ammo",
        "stabilityDamage": 2,
        "cooldown": 2,
        "confectanceCost": 0,
        "range": "6",
        "effArea": "Target",
        "description": "Select 1 enemy target within a 6-tile radius, dealing Freeze damage equal to 120% of ATK and consumes all Feathers of War. \n\nWhen 1 Feather of War is consumed, the damage dealt is increased by 20%.\nWhen 2 Feathers of War are consumed, critical damage is increased by 35% and Stability Damage dealt is increased by 4.\nWhen 3 Feathers of War are consumed, the damage multiplier is increased by 50% and attack is increased by 10%.\n\nIf the target is killed, the skills and effects that would trigger upon its death is nullified. \nAfter the skill resolves, Eagletta switches to the Heavy Talons stance.\nAt the end of the round, Eagletta gains 7 Feathers of War.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 4,
            "label": "Vertebrae Upgrade 4",
            "effect": "When 1 Feather of War is consumed, the increase of damage dealt is raised to 30%.\nWhen 2 Feathers of War are consumed, the increase of critical damage is raised to 45%.\nWhen 3 Feathers of War are consumed, the increase of damage multiplier is raised to 80% and attack increase is raised to 20%."
          }
        ],
        "icon": "assets/Eagletta/Featherstorm Feast.png"
      },
      {
        "name": "The Wild Within",
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
        "description": "Eagletta does not gain Confectance Index.\nAt the start of the battle, Eagletta gains 7 Feathers of War. \nAt the end of the allied phase, Frost tiles are generated within 3-tile radius around Eagletta, lasting for 2 rounds.\nDamage dealt is increased by 20% and critical damage is increased by 12%.\n\nIf the target is not within a 3x3 tiles around Eagletta, the damage dealt is reduced by 5% and critical damage is reduced by 3% per 1 tile of distance up to a maximum of 20% and 12% respectively.\nIf the target is inflicted with a Control effect, under effects of Frozen, Paralysis, or is a Large unit, then the damage dealt and critical damage reduction effect is nullified.\n\nWhile Eagletta is in the Heavy Talons stance, if an enemy unit is about to move, is about to attack, or ends their action within a 3x3 area around Eagletta and does not have Shock, the passive skill Predation is triggered to perform a Lock on Attack, up to 2 per round.\nFor every 7 stacks of Feathers of War consumed, Eagletta gains 1 stack of Invasive Threat. \nWhile Eagletta has 1 or more stacks of Invasive Threat, her critical rate is increased by 25% and using the basic attack Rending Talons and the passive skill Predation, Eagletta gains 1 stack of Feathers of War. \n\nWhen Eagletta has 4 or more stacks of Invasive Threat and uses the basic attack Swift Eagle Strike, consumes 2 Feathers of War to produce the skill effect of the Ultimate skill Featherstorm Feast, gaining all the effects of that skill's Feathers of War consumption.\nFeatherstorm Feast triggered by this method is treated only as a basic attack and will not trigger the transition to Heavy Talons or gaining of Feathers of War. Can be triggered up to once per round.",
        "upgrades": [
          {
            "type": "vertebrae",
            "number": 1,
            "label": "Vertebrae Upgrade 1",
            "effect": "At the start of battle, gains 1 stack of Invasive Threat. With 1 stack of Invasive Threat, using basic attack Rending Talons and passive skill Predation grants 1 extra Feather of War. With 2 stacks or more of Invasive Threat, at the end of the round, cooldown of ultimate Featherstorm Feast is reduced by 1 turn. If basic attack Swift Eagle Strike eliminates a target, gains 2 Feathers of War."
          },
          {
            "type": "vertebrae",
            "number": 5,
            "label": "Vertebrae Upgrade 5",
            "effect": "The number of Feathers of War required to obtain Invasive Threat is reduced to 3."
          }
        ],
        "icon": "assets/Eagletta/The Wild Within.png"
      }
    ],
    "vertebraeUpgrades": [
      {
        "upgrade": "Upgrade 1",
        "skill": "The Wild Within",
        "level": "2",
        "effect": "At the start of battle, gains 1 stack of Invasive Threat. With 1 stack of Invasive Threat, using basic attack Rending Talons and passive skill Predation grants 1 extra Feather of War. With 2 stacks or more of Invasive Threat, at the end of the round, cooldown of ultimate Featherstorm Feast is reduced by 1 turn. If basic attack Swift Eagle Strike eliminates a target, gains 2 Feathers of War."
      },
      {
        "upgrade": "Upgrade 2",
        "skill": "Deterrence Tactics",
        "level": "2",
        "effect": "Passive effect added: At the end of the round, if the number of Lock on Attack for the passive skill The Wild Within has not reached the limit, gain 2 Feathers of War for each remaining use. The damage multiplier of basic attack Swift Eagle Strike is increased to 120%, damage dealt increase is raised to 25% and the critical damage increase is raised to 10%. The damage multipliers of basic attack Rending Talons and passive skill Predation are increased to 80%"
      },
      {
        "upgrade": "Upgrade 3",
        "skill": "Stoop Strike",
        "level": "2",
        "effect": "The damage multiplier increased to 120%. The range for applying Queen of the Skies is increased to within 5-tile radius around self. The effect of Queen of the Skies is enhanced: The damage reduction of the first attack against Eagletta is increased to 40%"
      },
      {
        "upgrade": "Upgrade 4",
        "skill": "Featherstorm Feast",
        "level": "2",
        "effect": "When 1 Feather of War is consumed, the increase of damage dealt is raised to 30%.\nWhen 2 Feathers of War are consumed, the increase of critical damage is raised to 45%.\nWhen 3 Feathers of War are consumed, the damage multiplier increase is raised to 80% and attack increase is raised to 20%."
      },
      {
        "upgrade": "Upgrade 5",
        "skill": "The Wild Within",
        "level": "3",
        "effect": "The number of Feathers of War required to obtain Invasive Threat is reduced to 3."
      },
      {
        "upgrade": "Upgrade 6",
        "skill": "Deterrence Tactics",
        "level": "3",
        "effect": "Passive effect added: When the ultimate Featherstorm Feast consumes 3 Feathers of War, the damage multiplier is additionally increased by 30%. This effect is also applies to the skill effect of Featherstorm Feast triggered by using basic attack Swift Eagle Strike while having 4 stacks of Invasive Threat. For each stack of Invasive Threat, own damage dealt is increased by 10%: when an enemy unit takes damage from an allied unit, if its on Freeze-type tile, the damage it takes is increased by 10% for each stack of Invasive Threat.\nThe ATK boost from Eagle Strike stance is increased by 20%.\nThe damage multiplier of basic attack Swift Eagle Strike is increased to 150%, the damage dealt increase is raised to 40% and critical damage increase is rased to 15%.\nThe DEF ignored by basic attack Rending Talons and passive skill Predation is increased to 10%. When Feathers of War are consumed by Heavy Talons stance, the damage multiplier increase for basic attack Rending Talons and passive skill Predation is raised to 10%."
      }
    ],
    "neuralHelixKeys": [
      {
        "node": "Fixed Key 1 - Predator's Intimidation",
        "level": "20",
        "keyName": "Fixed Key 1 - Predator's Intimidation",
        "description": "After using the basic attack Rending Talons or the passive skill Predation on a non-Boss unit, applies Shock to it.",
        "icon": "assets/Eagletta/Fixed Key 1 - Predator's Intimidation.png"
      },
      {
        "node": "Fixed Key 2 - Lord of the Sky",
        "level": "20",
        "keyName": "Fixed Key 2 - Lord of the Sky",
        "description": "Before an active attack, cleanse 1 buff from the target.",
        "icon": "assets/Eagletta/Fixed Key 2 - Lord of the Sky.png"
      },
      {
        "node": "Fixed Key 3 - Watch from on High",
        "level": "30",
        "keyName": "Fixed Key 3 - Watch from on High",
        "description": "At the end of allied turn, Eagletta recovers 1 point of stability for each stack of Invasive Threat she has.",
        "icon": "assets/Eagletta/Fixed Key 3 - Watch from on High.png"
      },
      {
        "node": "Fixed Key 4 - Ruler of the Firmament",
        "level": "30",
        "keyName": "Fixed Key 4 - Ruler of the Firmament",
        "description": "Damage dealt to non-boss units with HP less than or equal to 50% is increased by 20%.",
        "icon": "assets/Eagletta/Fixed Key 4 - Ruler of the Firmament.png"
      },
      {
        "node": "Fixed Key 5 - Wings Against the Wind",
        "level": "40",
        "keyName": "Fixed Key 5 - Wings Against the Wind",
        "description": "Before using the basic attack Swift Eagle Strike, applies Defense Down II to the target for 2 turns.",
        "icon": "assets/Eagletta/Fixed Key 5 - Wings Against the Wind.png"
      },
      {
        "node": "Fixed Key 6 - Into Uncharted Ground",
        "level": "40",
        "keyName": "Fixed Key 6 - Into Uncharted Ground",
        "description": "The basic attack Swift Eagle Strike deals 30% more damage to mechanical non-Boss units.",
        "icon": "assets/Eagletta/Fixed Key 6 - Into Uncharted Ground.png"
      },
      {
        "node": "Affinity Key - Unadorned sincerity",
        "level": "-",
        "keyName": "Affinity Key - Unadorned sincerity",
        "description": "ATK +3%, HP +3%, CRIT +3%",
        "icon": "assets/Eagletta/Affinity Key - Unadorned sincerity.png"
      },
      {
        "node": "Common Key - An Actor's Work on Herself",
        "level": "40",
        "keyName": "Common Key - An Actor's Work on Herself",
        "description": "ATK +5.0% / If a skill does not consume Confectance Index, the damage dealt is increased by 10%.",
        "icon": "assets/Eagletta/Common Key - An Actor's Work on Herself.png"
      }
    ]
  }
};
