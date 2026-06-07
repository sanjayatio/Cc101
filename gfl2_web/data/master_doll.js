/**
 * Affinity lookup
 * @type {[string, string]}
 * Index 0: Key
 * Index 1: Value
 */
const AFFINITY = [
  ["☕", "Corrosion"],
  ["🦾", "Physical"],
  ["❄", "Freeze"],
  ["💧", "Hydro"],
  ["🔥", "Burn"],
  ["⚡", "Electric"],
];

/**
 * Class lookup
 * @type {[string, string]}
 * Index 0: Key
 * Index 1: Value
 */
const CLASS = [
  ["♜", "Bulwark"],
  ["♝", "Vanguard"],
  ["⛨", "Support"],
  ["♞", "Sentinel"],
];

/**
 * Weapon lookup
 * @type {[string, string, string]}
 * Index 0: Key
 * Index 1: Value
 * Index 1: Name
 */
const WEAPON = [
  ["🪓", "AR",  "Assault Riffle"],
  ["⚒", "SG",  "Shotgun"],
  ["⛈", "SMG", "Small Machine Gun"],
  ["💥", "LMG", "Machine Gun"],
  ["🏹", "SR",  "Sniper Riffle"],
  ["🗡", "BLD", "Sword"],
  ["🔫", "HG",  "Handgun"],
];


/**
 * Doll master data
 * @type {[number, string, string, string, string, string]}
 * Index 0: Movement range
 * Index 1: Doll rarity
 * Index 2: Affinity key
 * Index 3: Class key
 * Index 4: Weapon key
 * Index 5: Doll name
 */
const DOLL_MASTER = [
  [9,"S","⚡","♝","🪓","Belka"],       [7,"S","⚡","⛨","⛈","Lenna"],
  [6,"S","⚡","♜","🪓","Andoris"],     [7,"S","⚡","♞","⛈","Leva"],
  [6,"S","⚡","⛨","🪓","Jiangyu"],     [4,"S","⚡","♞","🏹","Mosin-Nagant"],
  [5,"S","❄","♞","⛈","Robella"],     [6,"S","❄","⛨","🪓","Alva"],
  [4,"S","❄","♞","🏹","Makiatto"],    [6,"S","❄","⛨","⛈","Suomi"],
  [5,"r","❄","♞","⚒","Lotta"],       [6,"S","❄","⛨","🏹","Dushevnaya"],
  [6,"S","❄","♜","⚒","Helen"],
  [6,"S","💧","⛨","🏹","Springfield"], [5,"S","💧","♞","🏹","Nikketa"],
  [7,"r","💧","⛨","🔫","Colphne"],     [5,"S","💧","♞","🪓","Tololo"],
  [6,"S","💧","⛨","🔫","Florence"],    [6,"S","💧","♜","⚒","Sabrina"],
  [9,"S","💧","♝","⛈","Zhaohui"],
  [5,"r","🦾","♞","💥","Littara"],     [9,"S","🦾","♝","🗡","Ullrid"],
  [5,"S","🦾","♞","⛈","Papasha"],     [9,"S","🦾","♝","🔫","Faye"],
  [7,"S","🦾","♞","🪓","Voymastina"],  [8,"S","🦾","♝","⚒","Vepley"],
  [6,"S","🦾","⛨","🪓","Yoohee"],      [9,"S","🦾","♝","🪓","Daiyan"],
  [6,"S","🦾","⛨","💥","Balthilde"],   [6,"r","🦾","♜","🪓","Groza"],
  [9,"S","🔥","♝","⚒","Qiuhua"],      [9,"S","🔥","♝","⛈","Sakura"],
  [9,"r","🔥","♝","🗡","Krolik"],      [6,"r","🔥","⛨","⛈","Cheeta"],
  [5,"r","🔥","♞","🪓","Sharkry"],     [6,"S","🔥","⛨","⛈","Vector"],
  [5,"S","🔥","♞","🪓","Qiongjiu"],    [6,"S","🔥","⛨","🪓","Centaureissi"],
  [5,"S","🔥","♞","💥","Lewis"],       [6,"r","🔥","⛨","🔫","Ksenia"],
  [6,"S","🔥","♜","⛈","Peri"],
  [6,"r","☕","⛨","🔫","Nagant"],      [6,"S","☕","♞","🪓","Klukai"],
  [4,"r","☕","♞","🏹","Nemesis"],     [5,"S","☕","♞","⚒","Lind"],
  [6,"S","☕","⛨","🪓","Mechty"],      [5,"S","☕","♞","💥","Peritya"],
];
esis"],     [5,"S","☕","♞","⚒","Lind"],
  [6,"S","☕","⛨","🪓","Mechty"],      [5,"S","☕","♞","💥","Peritya"],
];
