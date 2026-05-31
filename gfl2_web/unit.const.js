// Column indices (0-based) for the last 3 columns
const COL_AFFINITY = 12;
const COL_CLASS    = 13;
const COL_WEAPON   = 14;

// Active filter state: a Set of selected values per column
const activeFilters = {
  [COL_AFFINITY]: new Set(),
  [COL_CLASS]:    new Set(),
  [COL_WEAPON]:   new Set(),
};

// Column indices (0-based) for the V (vertebra) columns in each tier
const COL_V_GM = 3;
const COL_V_IB = 6;
const COL_V_FB = 9;

// Hide-dash filter state: when true, rows where that column = '-' are hidden
const hideDash = {
  [COL_V_GM]: false,
  [COL_V_IB]: false,
  [COL_V_FB]: false,
};

// ☕Corrosion 🦾Physical  ❄Freeze  💧Hydro    🔥Burn ⚡ Electric   
// ♜ Bulwark   ♝ Vanguard  ⛨ Support ♞Sentinel
// 🪓AR        ⚒SG        ⛯ SMG     💥LMG      🏹 SR  🗡 BLD  🔫 HG
const UNITS_DATA = `
9  Belka         S  - - -  - - -  0 7 -  ⚡  ♝  🪓
6  Andoris       S  0 4 -  0 - -  0 7 -  ⚡  ♜  🪓
6  Jiangyu       S  0 7 -  - - -  0 7 -  ⚡  ⛨  🪓
7  Lenna         S  0 7 -  - - -  - - -  ⚡  ⛨  ⛯
7  Leva          S  - - -  - - -  1 6 -  ⚡  ♞  ⛯
4  Mosin-Nagant  S  0 - 1  1 - 1  0 - -  ⚡  ♞  🏹
5  Robella       S  0 - -  - - -  - - -  ❄  ♞  ⛯
4  Makiatto      S  1 7 -  0 7 -  0 - -  ❄  ♞  🏹
5  Lotta         r  0 - -  0 - -  0 - -  ❄  ♞  ⚒
6  Helen         S  - - -  0 - -  - - -  ❄  ♜  ⚒
x  Alva          S  0 - 1  - - -  - - -  ❄  ⛨  🪓
6  Suomi         S  - - -  0 7 -  1 7 -  ❄  ⛨  ⛯
6  Dushevnaya    S  - - -  0 - -  - - -  ❄  ⛨  🏹
6  Springfield   S  1 6 1  2 6 -  2 6 -  💧  ⛨  🏹
7  Colphne       r  6 7 -  6 7 -  6 7 -  💧  ⛨  🔫
x  Florence      S  0 6 -  - - -  0 6 -  💧  ⛨  🔫
9  Zhaohui       S  0 7 1  - - -  0 7 -  💧  ♝  ⛯
5  Nikketa       S  0 6 -  1 6 -  1 6 -  💧  ♞  🏹
5  Tololo        S  5 7 2  6 7 4  4 7 1  💧  ♞  🪓
6  Sabrina       S  5 7 2  6 7 -  4 - -  💧  ♜  ⚒
6  Groza         r  6 7 -  6 7 -  6 4 -  🦾  ♜  🪓
5  Littara       r  6 7 -  6 - -  6 - -  🦾  ♞  💥
5  Papasha       S  6 2 5  6 2 6  3 - 1  🦾  ♞  ⛯
6  Yoohee        S  2 7 -  2 2 -  - - -  🦾  ⛨  🪓
x  Balthilde     S  0 - 1  0 - -  0 - -  🦾  ⛨  💥
9  Ullrid        S  - - -  0 8 1  0 8 1  🦾  ♝  🗡
9  Daiyan        S  0 8 -  - - -  1 8 -  🦾  ♝  🪓
9  Faye          S  2 2 2  3 2 -  3 - -  🦾  ♝  🔫
8  Vepley        S  3 7 1  5 7 1  4 7 2  🦾  ♝  ⚒
9  Qiuhua        S  - - -  0 - -  0 6 -  🔥  ♝  ⚒
9  Krolik        r  5 6 -  6 - -  6 - -  🔥  ♝  🗡
5  Sharkry       r  6 7 -  6 7 -  6 7 -  🔥  ♞  🪓
5  Qiongjiu      S  6 7 3  6 7 1  1 7 2  🔥  ♞  🪓
x  Lewis         S  - - -  0 - -  - - -  🔥  ♞  💥
6  Peri          S  0 - -  - - -  - - -  🔥  ♜  ⛯
9  Sakura        S  0 6 -  - - -  - - -  🔥  ♝  ⛯
6  Cheeta        r  6 6 -  6 6 -  6 6 -  🔥  ⛨  ⛯
6  Vector        S  2 7 1  1 7 -  0 7 -  🔥  ⛨  ⛯
6  Centaureissi  S  0 7 -  - - -  0 7 -  🔥  ⛨  🪓
6  Ksenia        r  6 7 -  6 - -  6 - -  🔥  ⛨  🔫
6  Nagant        r  6 - -  6 - -  6 - -  ☕  ⛨  🔫
4  Nemesis       r  6 - -  6 - -  6 - -  ☕  ♞  🏹
6  Mechty        S  0 7 -  1 7 -  0 7 -  ☕  ⛨  🪓
6  Klukai        S  1 2 -  6 6 1  0 6 -  ☕  ♞  🪓
5  Lind          S  0 6 -  0 6 -  0 6 -  ☕  ♞  ⚒
5  Peritya       S  6 4 1  6 6 2  6 6 -  ☕  ♞  💥`
